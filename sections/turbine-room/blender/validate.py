"""Read-only CPU validation of a freshly opened turbine-room blend.

Blender --background turbine-room.blend --python-exit-code 1 --python validate.py
The validator never saves the scene or renders. Exit 2 is an evidence FAIL.
"""
import argparse
import bpy
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[1]
SCENE = bpy.context.scene
EPS = 1e-5
RESULTS = []
CACHE = {}


def add(check, status, evidence, **details):
    RESULTS.append(dict(check=check, status=status, evidence=evidence, **details))


def finite(values):
    return all(math.isfinite(float(v)) for v in values)


def geometry(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        return None
    mesh.calc_loop_triangles()
    verts = [obj.matrix_world @ v.co for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    badnorm = sum(not finite(p.normal) or p.normal.length < .99 for p in mesh.polygons if p.area > 1e-12)
    degenerate = sum(p.area <= 1e-12 for p in mesh.polygons)
    edges = collections.Counter(tuple(sorted((a, b))) for p in mesh.polygons for a, b in zip(p.vertices, list(p.vertices[1:]) + [p.vertices[0]]))
    nonmanifold = sum(n != 2 for n in edges.values())
    evaluated.to_mesh_clear()
    if not verts or not tris:
        return None
    bounds = ([min(v[i] for v in verts) for i in range(3)], [max(v[i] for v in verts) for i in range(3)])
    return dict(verts=verts, tris=tris, bounds=bounds,
                edges=list({tuple(sorted((t[i], t[(i + 1) % 3]))) for t in tris for i in range(3)}),
                bvh=BVHTree.FromPolygons(verts, tris, all_triangles=True),
                badnorm=badnorm, degenerate=degenerate, nonmanifold=nonmanifold)


def prefix(name):
    return [o for o in SCENE.objects if o.name == name or re.fullmatch(re.escape(name) + r"\.\d+", o.name)]


def closest_named(name, point):
    objects = prefix(name)
    return min(objects, key=lambda o: (o.matrix_world.translation - point).length) if objects else None


def inferred_prop(row, anchor):
    """Diagnosis compatibility only. The registry still fails until prop is explicit."""
    name = row['anchor'].removeprefix('SUPPORT_')
    names = {'vise': 'Vise bolt base', 'bearing cradle': 'Bearing inspection cradle',
             'mug': 'Enamel shift mug', 'rag': 'Used folded cotton rag',
             'clipboard': 'Clipboard', 'tool rail': 'Tool rail back',
             'task lamp': 'Task lamp wall foot', 'lubrication chart': 'Lubrication chart',
             'oil stand': 'Oil stand feet'}
    if name.startswith('bench foot'):
        return closest_named('Bench foot', anchor.matrix_world.translation)
    if name.startswith('conduit saddle'):
        return closest_named('Conduit saddle', anchor.matrix_world.translation)
    if name.endswith(' sign'):
        return SCENE.objects.get(name)
    return SCENE.objects.get(names.get(name, ''))


def ray_contact(point, direction, target, max_gap, max_penetration, angle):
    # Ray starts in front of the proposed contact: negative signed distance
    # then measures penetration, rather than missing the near face from inside.
    backoff = max(.025, max_penetration + .01)
    loc, normal, face, distance = target['bvh'].ray_cast(point - direction * backoff, direction, 4.0 + backoff)
    if loc is None:
        return dict(status='FAIL', reason='no target surface along support direction')
    gap = distance - backoff
    deviation = math.degrees(math.acos(max(-1, min(1, normal.normalized().dot(-direction)))))
    good = -max_penetration - EPS <= gap <= max_gap + EPS and deviation <= angle + 1e-3
    return dict(status='PASS' if good else 'FAIL', gap_m=round(gap, 6),
                angle_deg=round(deviation, 3), point=list(point), hit=list(loc))


def segment_distance_squared(p, q, r, s):
    # Closest points on two finite segments, including parallel/degenerate
    # segments. Together with vertex-to-triangle distances this completes
    # triangle-to-triangle proximity, including coplanar overlapping faces.
    d1 = q - p; d2 = s - r; delta = p - r
    aa = d1.dot(d1); ee = d2.dot(d2); ff = d2.dot(delta)
    clamp = lambda x: max(0.0, min(1.0, x))
    if aa <= 1e-16 and ee <= 1e-16:
        return delta.length_squared
    if aa <= 1e-16:
        ss = 0.0; tt = clamp(ff / ee)
    else:
        cc = d1.dot(delta)
        if ee <= 1e-16:
            tt = 0.0; ss = clamp(-cc / aa)
        else:
            bb = d1.dot(d2); denom = aa * ee - bb * bb
            ss = clamp((bb * ff - cc * ee) / denom) if denom > 1e-16 else 0.0
            tt = (bb * ss + ff) / ee
            if tt < 0:
                tt = 0.0; ss = clamp(-cc / aa)
            elif tt > 1:
                tt = 1.0; ss = clamp((bb - cc) / aa)
    return (delta + d1 * ss - d2 * tt).length_squared


def candidate_segments(geo, low, high):
    segments = []
    for ia, ib in geo['edges']:
        a, b = geo['verts'][ia], geo['verts'][ib]
        lo = [min(a[i], b[i]) for i in range(3)]; hi = [max(a[i], b[i]) for i in range(3)]
        if all(hi[i] >= low[i] and lo[i] <= high[i] for i in range(3)):
            segments.append((a, b, lo, hi))
    return segments


def surface_contact(a, b, tolerance=.005):
    """Check physical connection for an explicitly declared small assembly."""
    alo, ahi = a['bounds']; blo, bhi = b['bounds']
    if any(ahi[i] + tolerance < blo[i] or bhi[i] + tolerance < alo[i] for i in range(3)):
        return False
    if a['bvh'].overlap(b['bvh']):
        return True
    for source, target in sorted(((a, b), (b, a)), key=lambda pair: len(pair[0]['verts'])):
        if any((hit := target['bvh'].find_nearest(v, tolerance))[0] is not None for v in source['verts']):
            return True
    low = [max(alo[i], blo[i]) - tolerance for i in range(3)]
    high = [min(ahi[i], bhi[i]) + tolerance for i in range(3)]
    a_edges = candidate_segments(a, low, high); b_edges = candidate_segments(b, low, high)
    for p, q, plow, phigh in a_edges:
        for r, s, rlow, rhigh in b_edges:
            if all(phigh[i] + tolerance >= rlow[i] and rhigh[i] + tolerance >= plow[i] for i in range(3)):
                if segment_distance_squared(p, q, r, s) <= (tolerance + EPS) ** 2:
                    return True
    return False


def connected_members(root, members, tolerance):
    pending = set(members) - {root}
    connected = {root}
    while pending:
        added = {n for n in pending if n in CACHE and any(surface_contact(CACHE[n], CACHE[p], tolerance) for p in connected)}
        if not added:
            break
        pending -= added; connected |= added
    return connected, pending


def check_support():
    try:
        rows = json.loads(SCENE.get('support_registry', '[]'))
    except Exception as exc:
        add('support.registry', 'FAIL', str(exc)); return
    if not rows:
        add('support.registry', 'FAIL', 'No support registry'); return
    associated = set()
    for row in rows:
        label = 'support.' + row.get('anchor', '?')
        anchor = SCENE.objects.get(row.get('anchor', ''))
        target = CACHE.get(row.get('target', ''))
        if anchor is None or target is None:
            add(label, 'FAIL', 'Missing anchor or evaluated target geometry', registry=row); continue
        direction = Vector(row.get('direction', (0, 0, -1)))
        if direction.length < EPS or not finite(direction):
            add(label, 'FAIL', 'Invalid support direction', registry=row); continue
        direction.normalize()
        prop_name = row.get('prop')
        prop = SCENE.objects.get(prop_name) if prop_name else anchor.parent
        explicit = prop is not None
        if not prop:
            prop = inferred_prop(row, anchor)
        if prop:
            associated.add(prop.name)
        options = (float(row.get('max_gap', .005)), float(row.get('max_penetration', .002)), float(row.get('angle_deg', 12)))
        anchor_result = ray_contact(anchor.matrix_world.translation, direction, target, *options)
        problems = []
        if not explicit:
            problems.append('No explicit visible prop association in registry or anchor parent')
        if prop is None or prop.name not in CACHE:
            problems.append('No visible prop resolved')
            prop_result = None
        elif prop.name == row['target']:
            problems.append('False registry: visible prop targets itself')
            prop_result = None
        else:
            pg = CACHE[prop.name]
            # Highest projection points form the actual extremal supporting
            # surface, evaluated after bevel/solidify/curve conversion.
            projection = max(v.dot(direction) for v in pg['verts'])
            contact_verts = [v for v in pg['verts'] if projection - v.dot(direction) <= EPS]
            nearest = pg['bvh'].find_nearest(anchor.matrix_world.translation)
            # Interior supports (a tabletop resting on inset rails) need not
            # lie below a mesh vertex. Query the real prop surface at the
            # anchor and verify that its outward normal faces the support.
            if nearest[0] is not None and nearest[1].dot(direction) >= math.cos(math.radians(options[2])):
                contact_verts.append(nearest[0])
            results = [ray_contact(v, direction, target, *options) for v in contact_verts]
            successful = [r for r in results if 'gap_m' in r]
            prop_result = dict(prop=prop.name, explicit_association=explicit,
                               extremal_vertex_count=len(contact_verts),
                               contact_pass_count=sum(r['status'] == 'PASS' for r in results),
                               min_gap_m=min((r['gap_m'] for r in successful), default=None),
                               max_gap_m=max((r['gap_m'] for r in successful), default=None),
                               anchor_to_prop_surface_m=round(nearest[3], 6) if nearest[3] is not None else None,
                               failed_samples=[r for r in results if r['status'] != 'PASS'][:5])
            if not any(r['status'] == 'PASS' for r in results):
                problems.append('Visible prop has no verified supporting contact')
            if any(r.get('gap_m', 0) < -options[1] - EPS for r in results):
                problems.append('Evaluated supporting surface penetrates target beyond tolerance')
            if nearest[3] is None or nearest[3] > options[0] + options[1] + EPS:
                problems.append('Anchor is detached from associated visible prop')
            members, disconnected = connected_members(prop.name, row.get('members', []), options[0])
            associated.update(members)
            prop_result['verified_connected_members'] = sorted(members - {prop.name})
            if disconnected:
                prop_result['disconnected_members'] = sorted(disconnected)
                problems.append('Declared assembly members have no geometric contact chain to support prop')
        if anchor_result['status'] != 'PASS':
            problems.append('Anchor contact exceeds gap, penetration, or angle tolerance')
        add(label, 'FAIL' if problems else 'PASS', '; '.join(problems) or 'Anchor and evaluated visible contact verified',
            registry=row, anchor_result=anchor_result, visible_prop=prop_result)
    # Explicitly enumerate root mounting parts authored by this builder.
    # Subparts bolted/welded to these roots are assessed via assembly checks,
    # not silently counted as independent floor/wall-supported props.
    roots = ['Bench foot', 'Bench top', 'Vise bolt base', 'Bearing inspection cradle',
             'Enamel shift mug', 'Used folded cotton rag', 'Clipboard',
             'Maintenance spanner shank', 'Forged spanner shank', 'Grease pencil',
             'Tool rail back', 'Task lamp wall foot',
             'Conduit saddle', 'Replacement junction box', 'Lubrication chart',
             'Oil stand feet', 'Fixture hanger', 'Suspended luminaire back',
             'Bearing toolcase body', 'Door downlight body',
             'D01 reactor sign', 'D02 electrical sign']
    missing = sorted(o.name for p in roots for o in prefix(p) if o.name not in associated)
    # Any builder-marked root is mandatory even if not in compatibility list.
    missing += sorted(o.name for o in SCENE.objects if o.get('support_required') and o.name not in associated and o.name not in missing)
    add('support.coverage', 'FAIL' if missing else 'PASS',
        'All enumerated support roots require explicit records; general arbitrary assembly support is not automatically inferred',
        registry_count=len(rows), associated_count=len(associated), unregistered=missing)


def check_contact_islands():
    """Catch unregistered floating pieces across the entire visible scene.

    This only establishes a geometric contact path to the architecture. It is
    independent of registry intent and does not certify strength, fastening,
    load path, penetration allowance or pose. The separate registry checks
    verify intended targets, direction and tolerances.
    """
    tolerance = .005
    names = sorted(n for n in CACHE if not SCENE.objects[n].hide_render)
    parents = {n: n for n in names}

    def root(n):
        while parents[n] != n:
            parents[n] = parents[parents[n]]; n = parents[n]
        return n

    cells = collections.defaultdict(list)
    pairs = set()
    for name in names:
        lo, hi = CACHE[name]['bounds']
        ranges = [range(math.floor((lo[i] - tolerance) / 1.5), math.floor((hi[i] + tolerance) / 1.5) + 1) for i in range(3)]
        nearby = set()
        for x in ranges[0]:
            for y in ranges[1]:
                for z in ranges[2]:
                    nearby.update(cells[x, y, z]); cells[x, y, z].append(name)
        for other in nearby:
            olo, ohi = CACHE[other]['bounds']
            if all(hi[i] + tolerance >= olo[i] and ohi[i] + tolerance >= lo[i] for i in range(3)):
                pairs.add((other, name))
    checked = 0
    for a, b in sorted(pairs):
        ar, br = root(a), root(b)
        if ar != br:
            checked += 1
            if surface_contact(CACHE[a], CACHE[b], tolerance):
                parents[br] = ar
    structural_names = {o.name for p in ['Structural floor', 'West wall', 'East wall', 'End wall', 'Roof deck'] for o in prefix(p)}
    grounded = {root(n) for n in structural_names if n in parents}
    islands = collections.defaultdict(list)
    for n in names:
        if root(n) not in grounded:
            islands[root(n)].append(n)
    nearest_evidence = []
    for component in islands.values():
        distances = []
        for a in component:
            alo, ahi = CACHE[a]['bounds']
            for b in names:
                if b in component:
                    continue
                blo, bhi = CACHE[b]['bounds']
                lower = math.sqrt(sum(max(0, blo[i] - ahi[i], alo[i] - bhi[i]) ** 2 for i in range(3)))
                if lower < .15:
                    distances.append((lower, a, b))
        measured = []
        for lower, a, b in sorted(distances)[:24]:
            best = math.inf
            for source, target in ((CACHE[a], CACHE[b]), (CACHE[b], CACHE[a])):
                for v in source['verts']:
                    nearest = target['bvh'].find_nearest(v, min(.15, best))
                    if nearest[0] is not None:
                        best = min(best, nearest[3])
            if best < math.inf:
                measured.append(dict(object=a, nearest_object=b, sampled_surface_gap_m=round(best, 6)))
        nearest_evidence.append(dict(island=component, nearby=sorted(measured, key=lambda item: item['sampled_surface_gap_m'])[:3]))
    add('support.visible_contact_islands', 'FAIL' if islands else 'PASS',
        'Every evaluated render-visible surface checked for a contact chain to structural floor/walls/roof within 5 mm; unsupported islands require review or correction',
        tested_objects=len(names), candidate_pairs=len(pairs), actual_pair_queries=checked,
        disconnected_islands=list(islands.values()),
        nearest_evidence=nearest_evidence,
        caveat='Vertex/surface and segment/segment distance plus triangle intersections; connection is not mechanical stability or a substitute for an explicit intended-support registry')


def clip_triangle(triangle, low, high):
    polygon = list(triangle)
    for axis in range(3):
        for limit, sign in ((low[axis], 1), (high[axis], -1)):
            out = []
            for a, b in zip(polygon, polygon[1:] + polygon[:1]):
                da = sign * (a[axis] - limit); db = sign * (b[axis] - limit)
                if da >= 0:
                    out.append(a)
                if (da >= 0) != (db >= 0):
                    out.append(a + (b - a) * (da / (da - db)))
            polygon = out
            if not polygon:
                return False
    return True


def inside_mesh(point, geo):
    # Odd/even intersections in a non-axis direction. Only used for a
    # clearance box fully swallowed by a solid, after triangle clipping.
    direction = Vector((1, .37639, .18271)).normalized()
    origin = point.copy(); count = 0
    for unused in range(100):
        hit = geo['bvh'].ray_cast(origin, direction, 1000)
        if hit[0] is None:
            break
        count += 1; origin = hit[0] + direction * 1e-4
    return bool(count % 2)


def overlaps(geo, low, high):
    lo, hi = geo['bounds']
    if any(hi[i] <= low[i] or lo[i] >= high[i] for i in range(3)):
        return False
    for tri in geo['tris']:
        points = [geo['verts'][i] for i in tri]
        if any(max(p[i] for p in points) <= low[i] or min(p[i] for p in points) >= high[i] for i in range(3)):
            continue
        if clip_triangle(points, low, high):
            return True
    return inside_mesh(Vector([(a + b) / 2 for a, b in zip(low, high)]), geo)


def clear_volume(label, low, high):
    # A 10-micrometre face inset avoids counting shared mathematical boundaries.
    low = [v + EPS for v in low]; high = [v - EPS for v in high]
    offenders = []
    for name, geo in CACHE.items():
        obj = SCENE.objects[name]
        if obj.hide_render:
            continue
        if overlaps(geo, low, high):
            offenders.append(dict(object=name, bounds=geo['bounds']))
    add(label, 'FAIL' if offenders else 'PASS',
        'Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback',
        tested_min=low, tested_max=high, intrusions=offenders)


def check_clearance(interface):
    circulation = interface['circulation']
    volume = circulation['main_keep_clear']
    low, high = list(volume['min']), list(volume['max'])
    low[2] = .02  # flush paint/joint/threshold allowance; documented explicitly
    is_slice = SCENE.get('build_phase') == 'slice'
    if is_slice:
        low[1] = max(low[1], 17)
    clear_volume('clearance.main_route', low, high)
    for key in ('east_service_aisle', 'north_crossover', 'south_crossover', 'west_equipment_apron'):
        area = circulation.get(key)
        if not area:
            continue
        lo = [*area['xy_min'], .02]; hi = [*area['xy_max'], area.get('minimum_clear_height_m', 2.7)]
        if is_slice:
            lo[1] = max(lo[1], 17)
        if lo[1] >= hi[1]:
            add('clearance.' + key, 'NOT_APPLICABLE', 'Outside built slice'); continue
        clear_volume('clearance.' + key, lo, hi)
    for portal in interface['portals']:
        p = portal['centre']; width = portal['clear_width_m']; height = portal['clear_height_m']
        if is_slice and p[1] < 17:
            add('clearance.portal.' + portal['id'], 'NOT_APPLICABLE', 'Outside built slice'); continue
        axis = {'X': 0, 'Y': 1}[portal['width_axis']]
        low = [p[0] - .38, p[1] - .38, p[2] + .02]
        high = [p[0] + .38, p[1] + .38, p[2] + height]
        low[axis] = p[axis] - width / 2; high[axis] = p[axis] + width / 2
        clear_volume('clearance.portal.' + portal['id'], low, high)


def check_dimensions(interface):
    low = interface['envelopes']['main_clear']['min']
    high = interface['envelopes']['main_clear']['max']
    expected = dict(west_x=low[0], east_x=high[0], finished_floor_z=low[2], clear_roof_z=high[2],
                    wall_start_y=17 if SCENE.get('build_phase') == 'slice' else low[1], wall_end_y=high[1])
    required = ['West wall', 'East wall', 'Structural floor', 'Roof deck']
    if any(n not in CACHE for n in required):
        add('architecture.dimensions', 'FAIL', 'Missing named architecture surfaces', missing=[n for n in required if n not in CACHE]); return
    actual = dict(west_x=CACHE['West wall']['bounds'][1][0], east_x=CACHE['East wall']['bounds'][0][0],
                  finished_floor_z=CACHE['Structural floor']['bounds'][1][2], clear_roof_z=CACHE['Roof deck']['bounds'][0][2],
                  wall_start_y=CACHE['West wall']['bounds'][0][1], wall_end_y=CACHE['West wall']['bounds'][1][1])
    errors = {key: round(actual[key] - value, 6) for key, value in expected.items() if abs(actual[key] - value) > .001}
    add('architecture.dimensions', 'FAIL' if errors else 'PASS', 'Evaluated interior wall, floor and roof planes compared to interface design', expected=expected, actual=actual, errors_m=errors)
    if SCENE.get('build_phase') != 'slice':
        missing = []; mismatches = []
        for entry in interface['portals'] + interface['utilities']:
            name = entry['marker']; obj = SCENE.objects.get(name)
            if not obj:
                missing.append(name); continue
            delta = (obj.matrix_world.translation - Vector(entry['centre'])).length
            if delta > .001:
                mismatches.append(dict(marker=name, position_error_m=delta))
        add('architecture.interface_markers', 'FAIL' if missing or mismatches else 'PASS',
            'Local portal and utility marker positions only; neighboring alignment is not bound', missing=missing, mismatches=mismatches)


def reflected_distance(source, target, axis_point, mirror_normal):
    tree = KDTree(len(target['verts']))
    for index, point in enumerate(target['verts']):
        tree.insert(point, index)
    tree.balance()
    errors = []
    for point in source['verts']:
        reflected = point - 2 * (point - axis_point).dot(mirror_normal) * mirror_normal
        errors.append(tree.find(reflected)[2])
    return max(errors, default=0)


def check_machine(interface):
    if SCENE.get('build_phase') == 'slice':
        add('machine.shaft_alignment', 'NOT_APPLICABLE', 'No turbine in slice')
        return
    raw = SCENE.get('machine_contract')
    if not raw:
        add('machine.contract', 'FAIL', 'Full train requires explicit measurable shaft and symmetry contract')
        return
    contract = json.loads(raw)
    point = Vector(contract['axis_point']); direction = Vector(contract['axis_direction']).normalized()
    mirror = Vector(contract.get('mirror_normal', [1, 0, 0])).normalized()
    shafts = contract.get('shaft_objects', [])
    centred = contract.get('centered_objects', [])
    pairs = contract.get('mirror_pairs', [])
    errors = []
    for zone in interface['equipment_zones']:
        if zone['id'] in {'TURBINE', 'COUPLING', 'GENERATOR'}:
            for endpoint in ['axis_start', 'axis_end']:
                if endpoint in zone:
                    delta = Vector(zone[endpoint]) - point
                    offset = (delta - delta.dot(direction) * direction).length
                    if offset > .005:
                        errors.append(dict(zone=zone['id'], endpoint=endpoint, axis_offset_m=offset))
    add('machine.interface_axis', 'FAIL' if errors else 'PASS', 'Train axis compared to all three interface equipment axes', errors=errors)
    if not shafts or not centred:
        add('machine.coverage', 'FAIL', 'At least one shaft and a centered casing/generator symmetry set are required')
    else:
        add('machine.coverage', 'PASS', 'Named shaft and centered machine sets exist', shaft_count=len(shafts), centered_count=len(centred), mirror_pairs=len(pairs))
    for spec in shafts:
        if isinstance(spec, str):
            spec = dict(name=spec, local_axis='Z')
        obj = SCENE.objects.get(spec['name']); geo = CACHE.get(spec['name'])
        if not obj or not geo:
            add('machine.shaft.' + spec['name'], 'FAIL', 'Missing shaft geometry'); continue
        local = {'X': Vector((1, 0, 0)), 'Y': Vector((0, 1, 0)), 'Z': Vector((0, 0, 1))}[spec.get('local_axis', 'Z')]
        actual_axis = (obj.matrix_world.to_3x3() @ local).normalized()
        angle = math.degrees(math.acos(min(1, abs(actual_axis.dot(direction)))))
        # A cylinder/shaft's extrema midpoint establishes its geometric centre
        # independently of its object origin. Circumferential symmetry is also
        # verified below when it is included in centered_objects.
        center = Vector([(lo + hi) / 2 for lo, hi in zip(*geo['bounds'])])
        delta = center - point; offset = (delta - delta.dot(direction) * direction).length
        good = offset <= spec.get('center_tolerance_m', .002) and angle <= spec.get('angle_tolerance_deg', .1)
        add('machine.shaft.' + spec['name'], 'PASS' if good else 'FAIL', 'Evaluated bounds centre and transformed authored shaft axis',
            measured_center=list(center), axis_offset_m=offset, direction_error_deg=angle,
            actual_axis=list(actual_axis), local_axis=spec.get('local_axis', 'Z'))
    tolerance = contract.get('symmetry_tolerance_m', .002)
    for name in centred:
        geo = CACHE.get(name)
        if not geo:
            add('machine.symmetry.' + name, 'FAIL', 'Missing centered geometry'); continue
        deviation = reflected_distance(geo, geo, point, mirror)
        add('machine.symmetry.' + name, 'PASS' if deviation <= tolerance else 'FAIL',
            'Evaluated vertex set compared to its reflection across the declared train median plane',
            max_reflection_error_m=deviation, tolerance_m=tolerance)
    for pair in pairs:
        left, right = pair['left'], pair['right']
        if left not in CACHE or right not in CACHE:
            add('machine.pair.' + left, 'FAIL', 'Missing named mirror-pair geometry', pair=pair); continue
        deviation = max(reflected_distance(CACHE[left], CACHE[right], point, mirror), reflected_distance(CACHE[right], CACHE[left], point, mirror))
        add('machine.pair.' + left, 'PASS' if deviation <= tolerance else 'FAIL',
            'Bidirectional evaluated vertex reflection check', pair=pair, max_reflection_error_m=deviation, tolerance_m=tolerance)


def check_configuration():
    camera_contract = json.loads(SCENE.get('camera_contract', '[]'))
    disk_contract = json.loads((ROOT / 'production/cameras.json').read_text())
    camera_errors = []
    for name, position, target, lens in disk_contract:
        obj = SCENE.objects.get(name)
        if not obj or obj.type != 'CAMERA':
            camera_errors.append(name + ': missing'); continue
        delta = (obj.matrix_world.translation - Vector(position)).length
        desired = (Vector(target) - Vector(position)).normalized()
        actual = obj.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        angle = math.degrees(desired.angle(actual))
        if delta > 1e-4 or angle > .02 or abs(obj.data.lens - lens) > 1e-4:
            camera_errors.append(dict(camera=name, position_error_m=delta, direction_error_deg=angle, lens=obj.data.lens))
    if camera_contract != disk_contract:
        camera_errors.append('Scene camera_contract differs from production/cameras.json')
    baseline_path = ROOT / 'production/renders/review/slice-01/build_manifest.json'
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text()).get('cameras')
        if baseline != disk_contract:
            camera_errors.append('Camera contract differs from the first review baseline; a documented invalid-camera rebaseline requires explicit review')
    count = sum(o.type == 'CAMERA' for o in SCENE.objects)
    if len(disk_contract) != 10 or count != 10:
        camera_errors.append('Exactly ten evidence cameras required')
    add('configuration.cameras', 'FAIL' if camera_errors else 'PASS', 'Ten camera transforms and lenses compared with external contract', errors=camera_errors, count=count)
    settings = dict(engine=SCENE.render.engine, resolution=[SCENE.render.resolution_x, SCENE.render.resolution_y, SCENE.render.resolution_percentage],
                    units=SCENE.unit_settings.system, unit_scale=SCENE.unit_settings.scale_length,
                    view_transform=SCENE.view_settings.view_transform, transparent=SCENE.render.film_transparent,
                    active_camera=SCENE.camera.name if SCENE.camera else None)
    ok = settings['engine'] == 'CYCLES' and settings['resolution'] == [1280, 800, 100] and settings['units'] == 'METRIC' and settings['unit_scale'] == 1 and settings['active_camera']
    add('configuration.render', 'PASS' if ok else 'FAIL', 'Saved render/metric configuration; no render performed', settings=settings)
    expected = ROOT / 'blender/turbine-room.blend'
    add('configuration.file', 'PASS' if Path(bpy.data.filepath).resolve() == expected.resolve() else 'FAIL', bpy.data.filepath)
    private = Path(os.environ.get('BLENDER_USER_RESOURCES', '')).resolve()
    add('configuration.private_resources', 'PASS' if private == (ROOT / '.blender-user').resolve() else 'FAIL', str(private))
    dependencies = []
    for image in bpy.data.images:
        if image.source in {'FILE', 'TILED', 'SEQUENCE'} and not image.packed_file:
            path = Path(bpy.path.abspath(image.filepath))
            dependencies.append(dict(kind='image', name=image.name, path=str(path), exists=path.exists()))
    for library in bpy.data.libraries:
        path = Path(bpy.path.abspath(library.filepath))
        dependencies.append(dict(kind='library', name=library.name, path=str(path), exists=path.exists()))
    for font in bpy.data.fonts:
        if font.filepath not in {'', '<builtin>'} and not font.packed_file:
            path = Path(bpy.path.abspath(font.filepath)); dependencies.append(dict(kind='font', name=font.name, path=str(path), exists=path.exists()))
    add('dependencies', 'FAIL' if any(not d['exists'] for d in dependencies) else 'PASS', 'File-backed images, libraries and fonts checked', dependencies=dependencies)
    missing = [o.name for o in SCENE.objects if o.type in {'MESH', 'CURVE', 'FONT'} and not o.hide_render and (not o.data.materials or any(m is None for m in o.data.materials))]
    materials = []
    for mat in bpy.data.materials:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.use_nodes else None
        materials.append(dict(name=mat.name, users=mat.users, roughness=bsdf.inputs['Roughness'].default_value if bsdf else None,
                              metallic=bsdf.inputs['Metallic'].default_value if bsdf else None))
    add('materials.assignment', 'FAIL' if missing else 'PASS', 'Every render-visible mesh/curve/font has non-null materials; shader statistics are not visual acceptance', missing=missing, materials=materials)


def check_meshes():
    invalid = []; normals = []; degenerates = []; topology = []; hidden = []
    duplicates = collections.defaultdict(list)
    for obj in SCENE.objects:
        if not finite(v for row in obj.matrix_world for v in row) or abs(obj.matrix_world.determinant()) < 1e-12:
            invalid.append(obj.name)
        if obj.hide_render and obj.type in {'MESH', 'CURVE', 'FONT'}:
            hidden.append(obj.name)
        geo = CACHE.get(obj.name)
        if not geo:
            continue
        if not all(finite(v) for v in geo['verts']):
            invalid.append(obj.name + ': nonfinite vertex')
        if geo['badnorm']:
            normals.append(dict(object=obj.name, bad_face_normals=geo['badnorm']))
        if geo['degenerate']:
            degenerates.append(dict(object=obj.name, degenerate_polygons=geo['degenerate']))
        if geo['nonmanifold']:
            topology.append(dict(object=obj.name, boundary_or_nonmanifold_edges=geo['nonmanifold']))
        # Exact evaluated surface match is a strong duplicate signal. Ignore
        # shared mesh datablocks in different transforms; those are intentional.
        points = sorted(tuple(round(v[i], 6) for i in range(3)) for v in geo['verts'])
        digest = hashlib.sha256(repr(points).encode()).hexdigest()
        geo['fingerprint'] = digest
        duplicates[(len(geo['tris']), digest)].append(obj.name)
    duplicate_groups = [names for names in duplicates.values() if len(names) > 1]
    add('geometry.finite', 'FAIL' if invalid else 'PASS', 'All object matrices and evaluated world vertices finite, transforms nonsingular', invalid=invalid)
    add('geometry.normals', 'FAIL' if normals else 'PASS', 'Nondegenerate evaluated face normals finite and unit-length; outward winding is not generally proven', problems=normals)
    add('geometry.degenerates', 'FAIL' if degenerates else 'PASS', 'Zero-area evaluated polygons', problems=degenerates)
    add('geometry.topology', 'REVIEW' if topology else 'PASS', 'Boundary/nonmanifold edges reported; intended open cloth/text surfaces need interpretation', problems=topology)
    add('geometry.exact_duplicates', 'FAIL' if duplicate_groups else 'PASS', 'Coincident evaluated point sets and triangle counts', groups=duplicate_groups)
    add('geometry.hidden', 'REVIEW' if hidden else 'PASS', 'Hidden render geometry requires explicit intent review', objects=hidden)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output'); ap.add_argument('--expect-revision'); ap.add_argument('--compare-report'); ap.add_argument('--no-fail-exit', action='store_true')
    args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    start = time.monotonic()
    blend_path = Path(bpy.data.filepath)
    initial_stat = blend_path.stat()
    blend_sha256 = hashlib.sha256(blend_path.read_bytes()).hexdigest()
    revision = SCENE.get('source_revision', 'unknown')
    if args.expect_revision:
        add('configuration.revision', 'PASS' if revision == args.expect_revision else 'FAIL', revision, expected=args.expect_revision)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in SCENE.objects:
        if obj.type in {'MESH', 'CURVE', 'FONT'}:
            geo = geometry(obj, depsgraph)
            if geo:
                CACHE[obj.name] = geo
    check_configuration(); check_meshes(); check_support(); check_contact_islands()
    interface = json.loads((ROOT / 'interface.json').read_text())
    check_dimensions(interface); check_clearance(interface)
    check_machine(interface)
    manifest_path = ROOT / 'production/renders/review' / revision / 'build_manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        mismatch = manifest.get('objects') != len(SCENE.objects) or manifest.get('phase') != SCENE.get('build_phase')
        add('configuration.build_manifest', 'FAIL' if mismatch else 'PASS', 'Saved scene count and phase compared with the revision build manifest',
            expected_objects=manifest.get('objects'), actual_objects=len(SCENE.objects), expected_phase=manifest.get('phase'))
    else:
        add('configuration.build_manifest', 'FAIL', 'No manifest for saved source revision')
    final_stat = blend_path.stat()
    changed = (initial_stat.st_mtime_ns, initial_stat.st_size) != (final_stat.st_mtime_ns, final_stat.st_size)
    add('configuration.snapshot_stability', 'FAIL' if changed else 'PASS', 'Saved blend file timestamp and size stayed stable throughout validation')
    geometry_sha256 = hashlib.sha256(json.dumps([(name, geo['fingerprint'], len(geo['tris'])) for name, geo in sorted(CACHE.items())]).encode()).hexdigest()
    if args.compare_report:
        reference = json.loads(Path(args.compare_report).read_text())
        match = reference.get('geometry_sha256') == geometry_sha256
        add('cold_reopen.geometry_comparison', 'PASS' if match else 'FAIL',
            'Current evaluated named geometry fingerprint compared to a prior report; material and pixel equivalence are separate checks',
            reference_report=args.compare_report, reference_geometry_sha256=reference.get('geometry_sha256'), current_geometry_sha256=geometry_sha256)
    fail = any(r['status'] == 'FAIL' for r in RESULTS)
    unresolved = any(r['status'] == 'NOT_PROVEN' for r in RESULTS)
    report = dict(schema='critical-shift.geometry-validation.v1', revision=revision,
                  phase=SCENE.get('build_phase'), status='FAIL' if fail else ('INCOMPLETE' if unresolved else 'PASS'),
                  blender_version=bpy.app.version_string, blend_file=bpy.data.filepath,
                  blend_sha256=blend_sha256, geometry_sha256=geometry_sha256,
                  validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  source_counts=dict(objects=len(SCENE.objects), meshes=len(CACHE), materials=len(bpy.data.materials),
                                     triangles=sum(len(g['tris']) for g in CACHE.values())),
                  method='Fresh-process saved-blend CPU inspection; no mutation and no rendering',
                  limitations=['No visual score or full cold-start render acceptance', 'No engine collision/navmesh/physics proof',
                               'General arbitrary inter-object collision and assembly strength are not proven',
                               'Neighbor alignment remains unbound; tested local geometry only',
                               'Support extrema check establishes contact at sampled authored support points, not mechanical stability'],
                  seconds=round(time.monotonic() - start, 2), checks=RESULTS)
    output = Path(args.output) if args.output else ROOT / 'production/validation' / revision / 'technical.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    summary = ['# Turbine room technical validation', '', f"Revision: {revision}. Phase: {report['phase']}. Result: **{report['status']}**.", '',
               report['method'] + '.', '', f"Blender {bpy.app.version_string}; {len(SCENE.objects)} objects; {len(CACHE)} evaluated surfaces.", '',
               'This is objective geometry evidence, not an art score or a full cold-start render PASS.', '', '| Check | Result | Evidence |', '|---|---|---|']
    summary += [f"| {r['check']} | {r['status']} | {r['evidence']} |" for r in RESULTS]
    summary += ['', 'Detailed measured contacts and intrusions are in the adjacent technical.json.', '', 'Limitations:'] + ['- ' + x for x in report['limitations']]
    output.with_suffix('.md').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    print('VALIDATION_REPORT=' + str(output))
    print(json.dumps(dict(status=report['status'], revision=revision, counts=report['source_counts'],
                          failed=[r['check'] for r in RESULTS if r['status'] == 'FAIL']), indent=2))
    if (fail or unresolved) and not args.no_fail_exit:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
