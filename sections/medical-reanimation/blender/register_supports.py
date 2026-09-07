"""Account for support of every geometric object using evaluated surface evidence.

register_supports(scene) returns an audit and writes explicit per-object support
metadata. Unknown objects, detached islands, excessive sampled penetration and
floating contact chains fail. Geometry is never moved and tolerances never grow
to fit an observed error. Architectural boundary roots are explicit premises,
not simulated building engineering. Designed mechanical insertion requires an
explicit, reviewed per-object tolerance; the default is 2 mm penetration.
"""

import hashlib
import json
import math
import re
import struct

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

GEOMETRY_TYPES = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}
GAP = .005
PENETRATION = .002
ANGLE = 12.0
COS_ANGLE = math.cos(math.radians(ANGLE))

# Exact authored architectural boundaries are the static support graph roots.
# Fixtures, skirtings, channels, trim, shelves and equipment are not roots.
BOUNDARY_ROOTS = {
    'Finished seamless resin slab': 'main structural floor boundary',
    'West reinforced plaster wall': 'west load-bearing building boundary',
    'Entry solid pier': 'front load-bearing building boundary',
    'Door lintel': 'front structural opening boundary',
    'Ceiling soffit': 'main structural overhead boundary',
}

# Each rule records intentional support hosts, rather than permission to ignore
# a component. Names are resolved only after evaluating all scene geometry.
# All candidate links must satisfy the same measured contact tests below.
RULES = {
    'Ceiling steel channel': ('wall-mounted structural channel', ['West reinforced plaster wall'], None),
    'West coved skirting': ('wall-applied trim', ['West reinforced plaster wall'], (-1, 0, 0)),
    'West cart buffer': ('wall-mounted impact rail', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Front coved skirting': ('wall-applied trim', ['Entry solid pier'], (0, -1, 0)),
    'Wash zone expansion strip': ('floor-inlaid strip', ['Finished seamless resin slab'], (0, 0, -1)),
    'Sparse wheel scuff': ('applied floor marking', ['Finished seamless resin slab', 'Flush perforated wash grate'], (0, 0, -1)),
    'Door steel jamb': ('floor-supported door frame', ['Finished seamless resin slab'], (0, 0, -1)),
    'Door rubber seal': ('attached door seal', ['Door steel jamb'], None),
    'Door track hood': ('mounted sliding-door track', ['Door lintel', 'Door steel jamb'], None),
    'Parked sliding leaf': ('floor-supported sliding leaf', ['Finished seamless resin slab', 'Door track hood'], None),
    'Door kick plate': ('attached protection plate', ['Parked sliding leaf'], (0, -1, 0)),
    'Recessed observation rim': ('attached observation frame', ['Parked sliding leaf'], (0, -1, 0)),
    'Observation glass': ('seated window pane', ['Recessed observation rim'], (0, -1, 0)),
    'Pull recess': ('attached handle mounting', ['Parked sliding leaf'], (0, -1, 0)),
    'Recessed door pull': ('handle attached at returns', ['Pull recess'], (0, -1, 0)),
    'Door panel folded seam': ('attached panel return', ['Parked sliding leaf'], (0, -1, 0)),
    'Door removable panel screw': ('panel fastener', ['Parked sliding leaf'], (0, -1, 0)),
    'Localized pull wear': ('applied wear marking', ['Parked sliding leaf', 'Pull recess'], (0, -1, 0)),
    'Sliding leaf number': ('applied ink', ['Parked sliding leaf'], (0, -1, 0)),
    'Flush crossing threshold': ('floor-supported threshold', ['Finished seamless resin slab'], (0, 0, -1)),
    'Entry department title': ('applied architectural ink', ['Door lintel'], (0, -1, 0)),
    'Pressed stainless wash basin': ('bracket-supported basin', ['Triangular wall bracket', 'Pressed triangular basin gusset'], (0, 0, -1)),
    'Basin drain': ('seated drain fitting', ['Pressed stainless wash basin'], (0, 0, -1)),
    'Triangular wall bracket': ('wall-mounted basin bracket', ['Basin bracket wall plate'], (-1, 0, 0)),
    'Basin bracket wall plate': ('wall-mounted bracket plate', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Trapped basin drain': ('connected plumbing', ['Pressed stainless wash basin', 'West reinforced plaster wall', 'Basin drain'], None),
    'Wastepipe compression nut': ('plumbing compression fitting', ['Trapped basin drain'], None),
    'Basin bracket anchor': ('wall-bracket fastener', ['Basin bracket wall plate'], (-1, 0, 0)),
    'Swan neck tap': ('basin-mounted tap', ['Pressed stainless wash basin'], (0, 0, -1)),
    'Ceramic isolation tap': ('basin-mounted isolation tap', ['Pressed stainless wash basin'], (0, 0, -1)),
    'Tap lever': ('attached tap lever', ['Ceramic isolation tap'], (0, 0, -1)),
    'Formed enamel decon backsplash': ('wall-mounted backsplash', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Backsplash folded perimeter': ('attached backsplash return', ['Formed enamel decon backsplash'], (-1, 0, 0)),
    'Backsplash captive screw': ('backsplash fastener', ['Formed enamel decon backsplash'], (-1, 0, 0)),
    'Pressed triangular basin gusset': ('attached basin gusset', ['Basin bracket wall plate', 'Triangular wall bracket'], None),
    'Hose utility riser': ('wall-mounted utility housing', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Coiled rinse hose': ('connected flexible hose', ['Hose utility riser', 'Spray grip'], None),
    'Spray grip': ('hose-connected handpiece', ['Coiled rinse hose', 'Wall hose cradle', 'Spray barrel'], None),
    'Spray barrel': ('attached spray barrel', ['Spray grip'], None),
    'Spray nozzle ferrule': ('attached spray fitting', ['Spray barrel'], (-1, 0, 0)),
    'Spray perforated face': ('attached nozzle face', ['Spray nozzle ferrule'], (-1, 0, 0)),
    'Spray thumb trigger': ('attached handpiece trigger', ['Spray grip', 'Spray barrel'], None),
    'Spray trigger body': ('cradled spray handpiece', ['Wall hose cradle', 'Coiled rinse hose'], None),
    'Wall hose cradle': ('wall-mounted hose cradle', ['West reinforced plaster wall', 'Hose utility riser'], (-1, 0, 0)),
    'Rinse supply pipe': ('wall-supported service pipe', ['Rinse pipe saddle', 'Hose utility riser', 'West reinforced plaster wall'], None),
    'Rinse pipe saddle': ('wall-mounted pipe saddle', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Rinse isolator stem': ('pipe-mounted valve stem', ['Rinse supply pipe'], (-1, 0, 0)),
    'Rinse isolation handwheel': ('spoke-supported handwheel', ['Handwheel spoke'], None),
    'Handwheel spoke': ('valve stem connection', ['Rinse isolator stem'], None),
    'Decon mat edge': ('floor-supported mat border', ['Finished seamless resin slab'], (0, 0, -1)),
    'Flush perforated wash grate': ('floor-supported wash mat', ['Finished seamless resin slab'], (0, 0, -1)),
    'Grate tread': ('attached wash-mat tread', ['Flush perforated wash grate'], (0, 0, -1)),
    'Drain rim': ('floor-supported drain surround', ['Finished seamless resin slab'], (0, 0, -1)),
    'Drain slot': ('applied drain insert', ['Drain rim'], (0, 0, -1)),
    'Suspended steel luminaire': ('suspended fixture housing', ['Fixture drop'], (0, 0, 1)),
    'Prismatic diffuser': ('seated luminaire diffuser', ['Suspended steel luminaire'], (0, 0, 1)),
    'Fixture drop': ('ceiling-attached suspension', ['Ceiling soffit'], (0, 0, 1)),
    'Localized wall repair': ('applied wall repair', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Towel shelf folded sheet': ('wall-mounted shelf', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Shelf front return': ('attached shelf return', ['Towel shelf folded sheet'], (-1, 0, 0)),
    'Folded work towel lower': ('shelf-resting linen', ['Towel shelf folded sheet'], (0, 0, -1)),
    'Folded work towel upper': ('stacked linen', ['Folded work towel lower'], (0, 0, -1)),
    'Folded linen towel': ('shelf-resting linen', ['Towel shelf folded sheet'], (0, 0, -1)),
    'Folded towel sewn edge': ('attached sewn edge', ['Folded linen towel', 'Folded work towel lower'], None),
    'Rinse bottle': ('basin-rim-resting bottle', ['Pressed stainless wash basin'], (0, 0, -1)),
    'Bottle pump collar': ('attached bottle collar', ['Rinse bottle'], (0, 0, -1)),
    'Bottle spout': ('attached bottle spout', ['Bottle pump collar'], None),
    'Cleaning brush': ('basin-rim-resting brush', ['Pressed stainless wash basin'], (0, 0, -1)),
    'Brush bristles': ('attached brush bristles', ['Cleaning brush'], (0, 0, -1)),
    'Decon procedure clipboard': ('wall-mounted clipboard', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Revised paper form': ('clipboard-supported paper', ['Decon procedure clipboard'], (-1, 0, 0)),
    'Decon form': ('applied paper ink', ['Revised paper form'], (-1, 0, 0)),
    'Towel rail': ('wall-mounted towel rail', ['West reinforced plaster wall'], (-1, 0, 0)),
    'Hanging linen towel': ('rail-supported hanging fabric', ['Towel rail'], (-1, 0, 0)),
    'Towel sewn hem': ('attached sewn hem', ['Hanging linen towel'], None),
    'Clipboard metal spring clip': ('attached clipboard clip', ['Decon procedure clipboard', 'Revised paper form'], (-1, 0, 0)),
    'Linen bin rubber plinth': ('floor-supported bin base', ['Finished seamless resin slab'], (0, 0, -1)),
    'Pressed metal linen drum': ('base-supported bin shell', ['Linen bin rubber plinth'], (0, 0, -1)),
    'Bin rolled bead': ('attached rolled drum rim', ['Pressed metal linen drum'], None),
    'Hinged linen-bin lid': ('drum-supported bin lid', ['Pressed metal linen drum', 'Lid hinge'], (0, 0, -1)),
    'Lid hinge': ('attached lid hinge', ['Pressed metal linen drum'], None),
    'Foot pedal': ('attached bin pedal', ['Linen bin rubber plinth'], (-1, 0, 0)),
    'Pedal linkage': ('attached bin linkage', ['Pressed metal linen drum', 'Linen bin rubber plinth'], None),
    'Bin lid grip': ('attached bin handle', ['Hinged linen-bin lid'], (0, 0, -1)),
    'Discarded cleaning glove palm': ('lid-resting glove', ['Hinged linen-bin lid'], (0, 0, -1)),
    'Glove finger': ('connected glove finger', ['Discarded cleaning glove palm', 'Hinged linen-bin lid'], None),
    'Glove thumb': ('connected glove thumb', ['Discarded cleaning glove palm', 'Hinged linen-bin lid'], None),
    'Bin modest inventory mark': ('applied bin marking', ['Pressed metal linen drum'], (-1, 0, 0)),
    'Localized pedal scuff': ('applied pedal wear', ['Foot pedal'], (0, 0, -1)),
}


def _base(name):
    return re.sub(r'\.\d{3}$', '', name)


def _v(vector):
    return [round(float(x), 7) for x in vector]


def _geometry(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None or not mesh.vertices:
        if mesh is not None:
            evaluated.to_mesh_clear()
        raise ValueError('no evaluated surface geometry')
    try:
        vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        polygons = [tuple(p.vertices) for p in mesh.polygons]
        digest = hashlib.sha256()
        for p in vertices:
            digest.update(struct.pack('<3f', *p))
        for polygon in polygons:
            digest.update(struct.pack('<I', len(polygon)))
            digest.update(struct.pack('<' + 'I' * len(polygon), *polygon))
        mesh.calc_loop_triangles()
        triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
        parents = list(range(len(vertices)))
        def root(i):
            while parents[i] != i:
                parents[i] = parents[parents[i]]
                i = parents[i]
            return i
        for triangle in triangles:
            first = root(triangle[0])
            for index in triangle[1:]:
                parents[root(index)] = first
        components = {}
        for triangle in triangles:
            components.setdefault(root(triangle[0]), []).append(triangle)
        samples = []
        for component, faces in components.items():
            component_samples = []
            stride = max(1, len(faces) // 600)
            selected = list(faces[::stride])
            indices = {index for triangle in faces for index in triangle}
            extremes = {min(indices, key=lambda i: vertices[i][axis]) for axis in range(3)}
            extremes.update(max(indices, key=lambda i: vertices[i][axis]) for axis in range(3))
            selected.extend(t for t in faces if any(i in extremes for i in t))
            for face in selected:
                a, b, c = (vertices[i] for i in face)
                normal = (b - a).cross(c - a)
                if normal.length < 1e-12:
                    continue
                normal.normalize()
                component_samples.append(((a + b + c) / 3, normal))
                component_samples.extend((vertices[i], normal) for i in face)
            samples.append(component_samples)
        return {'name': obj.name, 'object': obj,
                'bvh': BVHTree.FromPolygons(vertices, triangles, all_triangles=True),
                'min': Vector(tuple(min(v[i] for v in vertices) for i in range(3))),
                'max': Vector(tuple(max(v[i] for v in vertices) for i in range(3))),
                'samples': samples, 'component_count': len(samples),
                'surface_signature': digest.hexdigest()}
    finally:
        evaluated.to_mesh_clear()


def _contact(source, target, expected_direction, gap_tolerance, penetration_tolerance):
    fixed = Vector(expected_direction).normalized() if expected_direction is not None else None
    maximum_penetration = 0.0
    penetration_evidence = None
    islands = []
    for index, samples in enumerate(source['samples']):
        best, closest = None, None
        for point, source_normal in samples:
            nearest, normal, face, distance = target['bvh'].find_nearest(point, .25)
            if nearest is None:
                continue
            signed = (point - nearest).dot(normal)
            if signed < -maximum_penetration:
                maximum_penetration = -signed
                penetration_evidence = {'source_surface_m': _v(point), 'target_surface_m': _v(nearest),
                                        'target_normal': _v(normal), 'signed_distance_m': round(signed, 7)}
            if closest is None or distance < closest['surface_distance_m']:
                closest = {'source_surface_m': _v(point), 'target_surface_m': _v(nearest),
                           'surface_distance_m': round(distance, 7), 'signed_distance_m': round(signed, 7)}
            direction = fixed if fixed is not None else source_normal
            if source_normal.dot(direction) < COS_ANGLE:
                continue
            # Probe from the real source surface, backed away from its host.
            hit, hit_normal, hit_face, ray_distance = target['bvh'].ray_cast(point - direction * .10, direction, .35)
            if hit is None:
                continue
            signed_gap = (hit - point).dot(direction)
            angle = math.degrees(math.acos(max(-1.0, min(1.0, hit_normal.dot(-direction)))))
            passed = (-penetration_tolerance - 1e-6 <= signed_gap <= gap_tolerance + 1e-6
                      and angle <= ANGLE + 1e-6)
            anchor = {'anchor_on_source_m': _v(point), 'direction_to_support': _v(direction),
                      'target_surface_m': _v(hit), 'signed_gap_m': round(signed_gap, 7),
                      'normal_angle_deg': round(angle, 5), 'pass': passed}
            rank = (not passed, abs(signed_gap), angle)
            if best is None or rank < best[0]:
                best = (rank, anchor)
        islands.append({'component_index': index, 'sample_count': len(samples),
                        'contact': best[1] if best else None, 'nearest_surface': closest,
                        'pass': bool(best and best[1]['pass'])})
    penetration_pass = maximum_penetration <= penetration_tolerance + 1e-6
    return {'target': target['name'], 'components': islands,
            'maximum_sampled_penetration_m': round(maximum_penetration, 7),
            'penetration_evidence': penetration_evidence,
            'sampled_penetration_pass': penetration_pass,
            'pass': bool(islands) and all(i['pass'] for i in islands) and penetration_pass}


def register_supports(scene):
    """Register intended connections and return current evaluated contact audit."""
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    geometries, errors = {}, []
    for obj in scene.objects:
        if obj.type not in GEOMETRY_TYPES:
            continue
        try:
            geometries[obj.name] = _geometry(obj, depsgraph)
        except Exception as exc:
            errors.append({'object': obj.name, 'reason': str(exc)})
    records, roots = {}, set()
    for name, geometry in geometries.items():
        obj, base = geometry['object'], _base(name)
        if base in BOUNDARY_ROOTS:
            records[name] = {'object': name, 'classification': 'authored structural boundary',
                             'basis': BOUNDARY_ROOTS[base], 'root': True,
                             'evaluated_bounds_m': [_v(geometry['min']), _v(geometry['max'])],
                             'component_count': geometry['component_count'], 'pass': True}
            roots.add(name)
            obj['support_classification'] = 'authored structural boundary'
            obj['support_required'] = False
            continue
        if 'support_target' in obj and not obj.get('support_derived_registration', False):
            obj['support_authored_target'] = obj['support_target']
            obj['support_authored_direction'] = list(obj.get('support_direction', (0, 0, -1)))
        if 'support_authored_target' in obj:
            classification = 'explicit authored support connection'
            hosts = [obj['support_authored_target']]
            expected = obj['support_authored_direction']
            candidates = [geometries[h] for h in hosts if h in geometries]
        elif base in RULES:
            classification, hosts, expected = RULES[base]
            candidates = [g for n, g in geometries.items() if _base(n) in hosts and n != name]
        else:
            classification, hosts, expected, candidates = 'unclassified support-dependent geometry', [], None, []
        gap_tolerance = float(obj.get('support_gap_tolerance', GAP))
        penetration_tolerance = float(obj.get('support_penetration_tolerance', PENETRATION))
        contacts = [_contact(geometry, host, expected, gap_tolerance, penetration_tolerance) for host in candidates]
        contacts.sort(key=lambda c: (not c['pass'], c['maximum_sampled_penetration_m'],
                                    min((i['nearest_surface']['surface_distance_m'] for i in c['components']
                                         if i['nearest_surface']), default=math.inf)))
        record = {'object': name, 'classification': classification, 'root': False,
                  'component_count': geometry['component_count'], 'intended_host_names': hosts,
                  'expected_direction': list(expected) if expected is not None else 'outward normal of evaluated source face',
                  'maximum_gap_m': gap_tolerance, 'maximum_penetration_m': penetration_tolerance,
                  'maximum_normal_angle_deg': ANGLE, 'candidate_contacts': contacts,
                  'selected_target': None, 'support_chain': [], 'pass': False}
        if not candidates:
            record['failure'] = 'No explicit support classification/host or intended host absent.'
        records[name] = record
        obj['support_classification'] = classification
        obj['support_required'] = True
    supported = set(roots)
    changed = True
    while changed:
        changed = False
        for name, record in records.items():
            if name in supported:
                continue
            viable = next((c for c in record['candidate_contacts'] if c['pass'] and c['target'] in supported), None)
            if viable:
                record['selected_target'] = viable['target']
                record['support_chain'] = [viable['target']] + records[viable['target']].get('support_chain', [])
                record['pass'] = True
                supported.add(name)
                changed = True
    for name, record in records.items():
        if record['root']:
            continue
        obj = geometries[name]['object']
        contact = next((c for c in record['candidate_contacts'] if c['target'] == record['selected_target']), None)
        if contact is None and record['candidate_contacts']:
            contact = record['candidate_contacts'][0]
        if contact:
            anchor = next((island['contact'] for island in contact['components'] if island['contact']), None)
            if anchor:
                obj['support_target'] = contact['target']
                obj['support_anchor'] = anchor['anchor_on_source_m']
                obj['support_direction'] = anchor['direction_to_support']
                obj['support_gap_tolerance'] = record['maximum_gap_m']
                obj['support_penetration_tolerance'] = record['maximum_penetration_m']
                obj['support_derived_registration'] = True
        if not record['pass'] and 'failure' not in record:
            record['failure'] = ('Local contact passes but its support chain does not reach a structural boundary.'
                                 if any(c['pass'] for c in record['candidate_contacts']) else
                                 'No candidate satisfies every disconnected component contact plus sampled penetration tolerances.')
    signatures = {n: g['surface_signature'] for n, g in sorted(geometries.items())}
    report = {
        'schema_version': 1, 'method': 'evaluated world BVHs, real source-surface anchors, per-component rays and directed support graph',
        'geometry_count': len(geometries), 'evaluation_errors': errors,
        'classified_object_count': sum(r['classification'] != 'unclassified support-dependent geometry' for r in records.values()),
        'structural_boundary_roots': sorted(roots), 'supported_object_count': len(supported),
        'all_geometry_accounted_for': not errors and len(records) == len(geometries),
        'all_support_chains_pass': len(supported) == len(geometries) and not errors,
        'surface_signatures': signatures,
        'objects': list(records.values()),
        'pass': bool(geometries) and len(supported) == len(geometries) and not errors,
        'limitations': [
            'Named structural floor, wall, lintel and soffit boundaries are authored static premises. Structural continuation and building engineering outside this module are not simulated.',
            'Each disconnected evaluated mesh component requires a contact. Anchors are sampled triangle/vertex surfaces, including extrema; this is finite geometric evidence, not a continuous contact or load-stability proof.',
            'Maximum penetration is sampled nearest-surface signed distance; open meshes, incorrect winding and highly concave geometry can yield conservative false failures requiring inspection.',
            'Inferred attachment directions use actual outward source-face normals, restricted by explicit intended host rules. The rules do not waive gap, angle, penetration or grounded-chain requirements.',
            'All defaults are 5 mm gap, 2 mm penetration and 12 degrees. No tolerance is increased to accommodate an observed failure.',
            'This audit does not establish fastener strength, friction, flexural support, cloth stability, rigid-body physics or runtime attachment constraints.',
        ],
    }
    scene['support_validation_json'] = json.dumps(report, separators=(',', ':'))
    scene['support_registry_count'] = sum('support_target' in g['object'] for g in geometries.values())
    return report
