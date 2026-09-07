"""Measure the saved Electrical Room; never builds, renders, or alters the .blend.

blender --background electrical_slice.blend --python-exit-code 2 \
  --python validate_scene.py -- --out ../production/checkpoints/S01/validation.json

--out is a JSON file (a directory is also accepted). Nonzero exit on failure.
All geometry tests use modifier-evaluated world-space vertices and BVH surfaces.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import traceback

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
GAP = .005
PENETRATION = .002
ANGLE = 12.0
EPS = .00001
GEOMETRY_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}
FULL_CAMERAS = ['C01_Entry', 'C02_Hero', 'C03_Reverse', 'C04_Route',
                'C05_Drawout_Clearance', 'C06_Transformer', 'C07_Reserve_Bay',
                'C08_Material_Detail', 'C09_Workbench', 'C10_Transfer']
SLICE_CAMERAS = ['S01_Validation', 'S02_Construction']
# Only construction is exempt from an individual support declaration. Merely
# assigning "fixed-architecture" to a loose prop does not exempt it.
STRUCTURAL_NAMES = {
    'Floor', 'Ceiling', 'West wall', 'East wall', 'East structural wall',
    'Portal wall return', 'Portal wall head', 'Wall pilaster',
    'Damp-proof concrete curb', 'Precast horizontal reveal',
    'Precast vertical reveal', 'Transverse slab joint', 'Longitudinal slab joint',
    'I beam flange', 'I beam web', 'Beam end plate', 'Route edge guide',
    'Connection vestibule floor', 'Connection vestibule side',
    'Connection vestibule ceiling', 'Connection privacy return',
    'Reserve bay opening head', 'Reserve opening south return',
    'Reserve opening north return', 'Reserve floor', 'Reserve ceiling',
    'Reserve east wall', 'Reserve south wall', 'Reserve north wall',
    'Reserve bay floor', 'Reserve bay ceiling', 'Reserve bay east wall',
    'Reserve bay south wall', 'Reserve bay north wall',
}
# Finite, reviewable construction joints. Exact duplicates are tested before
# this table is consulted. No blanket door/utility/architecture exemption.
KNOWN_JOIN_PAIRS = {
    frozenset(('Floor', 'Flush portal threshold')): 'flush threshold inlay',
    frozenset(('Connection vestibule floor', 'Flush portal threshold')): 'flush threshold inlay',
    frozenset(('Portal wall return', 'Deep steel portal jamb')): 'frame seated in structural opening',
    frozenset(('Portal wall return', 'Portal header')): 'header seated in structural opening',
    frozenset(('Portal wall head', 'Portal header')): 'header seated in structural opening',
    frozenset(('Crown rain lip', 'Tap-off riser')): 'bus termination through cabinet crown',
    frozenset(('Cable termination boot', 'Tap-off riser')): 'telescoping electrical termination',
    frozenset(('Bolted termination flange', 'Tap-off riser')): 'flanged electrical termination',
    frozenset(('Bolted termination flange', 'Tapered tap-off transition')): 'flanged electrical transition',
    frozenset(('Cable termination boot', 'Tapered tap-off transition')): 'telescoping electrical transition',
    frozenset(('Wall permit board', 'Precast horizontal reveal')): 'board seated over shallow wall reveal',
}


def base_name(name):
    return re.sub(r'\.\d{3}$', '', name)


def vec(value):
    return [round(float(x), 8) for x in value]


def prop_json(obj, key, default=None):
    value = obj.get(key, default)
    return json.loads(value) if isinstance(value, str) else value


def finite(values):
    return all(math.isfinite(float(x)) for x in values)


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def support_hit(record, point, direction):
    hit = record['bvh'].ray_cast(point-direction*.052, direction, 2.052)
    if hit[0] is not None:
        return hit, 'ray'
    # Rotating a doorway by pi puts an on-edge anchor ~0.1 micrometres
    # outside its floor triangle. Accept only a closest point on the same
    # support line to 10 micrometres; the ordinary gap and angle gates remain.
    near = record['bvh'].find_nearest(point)
    if near[0] is not None:
        delta = near[0]-point
        tangent_error = (delta-direction*delta.dot(direction)).length
        if tangent_error <= EPS and -.052 <= delta.dot(direction) <= 2:
            if math.degrees(near[1].angle(-direction)) <= ANGLE:
                return near, 'closest_point_within_10_micrometre_ray_edge_tolerance'
            # At a convex mesh edge the closest triangle can be the vertical
            # slab side. Sub-micron rounding must not turn its normal into a
            # false 90 degree support failure. Probe only within the same 10 um
            # lateral budget, requiring a real ray hit with the correct normal.
            axis = Vector((1, 0, 0)) if abs(direction.x) < .9 else Vector((0, 1, 0))
            u = direction.cross(axis).normalized()
            v = direction.cross(u).normalized()
            for du, dv in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                ray = record['bvh'].ray_cast(point+(u*du+v*dv)*EPS*.5-direction*.052,
                                             direction, 2.052)
                if ray[0] is not None and math.degrees(ray[1].angle(-direction)) <= ANGLE:
                    return ray, 'ray_within_10_micrometre_edge_tolerance'
    return hit, 'no_hit'


class Audit:
    def __init__(self, options):
        self.options = options
        self.scene = bpy.context.scene
        self.stage = options.stage if options.stage != 'auto' else self.scene.get('stage')
        self.checks = []
        self.records = {}
        self.roots = {o.name: o for o in self.scene.objects if o.get('assembly_root')}
        self.result = {
            'schema': 'critical-shift.geometry-validation.v1',
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'blend': bpy.data.filepath, 'blender_version': bpy.app.version_string,
            'section': self.scene.get('section'), 'revision': self.scene.get('revision'),
            'stage': self.stage, 'checks': self.checks,
            'tolerances': {'gap_m': GAP, 'penetration_m': PENETRATION,
                           'support_angle_degrees': ANGLE, 'dimension_m': .005},
            'limitations': [
                'A slice result applies only to its 7.2 m partial hall; it cannot accept the full room.',
                'Route checks are conservative world AABB exclusion tests, not a navigation or carried-body sweep.',
                'Support proves registered anchors and their actual contact faces; arbitrary internal parts require their own support roots.',
                'Intersection tests report triangle-surface crossings; fully contained solids can evade crossing detection.',
                'Construction joins and same-assembly intersections are classified, not asserted collision-free.',
                'Visual quality, electrical safety, runtime behavior and neighboring module alignment are not evaluated.',
            ],
        }

    def check(self, name, passed, measured=None, severity='error'):
        self.checks.append({'id': name, 'status': 'PASS' if passed else
                            ('WARN' if severity == 'warning' else 'FAIL'),
                            'measurements': measured})

    def record_geometry(self):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        errors, material_errors, registration_errors = [], [], []
        degenerates, open_meshes = [], []
        for obj in self.scene.objects:
            if obj.type not in GEOMETRY_TYPES:
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                if not mesh or not mesh.vertices or not mesh.polygons:
                    errors.append({'object': obj.name, 'reason': 'no evaluated polygon geometry'})
                    continue
                vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
                if not all(finite(v) for v in vertices):
                    errors.append({'object': obj.name, 'reason': 'nonfinite evaluated coordinates'})
                    continue
                faces = [tuple(p.vertices) for p in mesh.polygons]
                low = Vector(tuple(min(v[i] for v in vertices) for i in range(3)))
                high = Vector(tuple(max(v[i] for v in vertices) for i in range(3)))
                bvh = BVHTree.FromPolygons(vertices, faces, all_triangles=False, epsilon=0)
                collection_names = {c.name for c in obj.users_collection}
                owner = obj.get('assembly_member')
                structural = (owner == 'fixed-architecture' and 'Architecture' in collection_names
                              and base_name(obj.name) in STRUCTURAL_NAMES and obj.parent is None)
                parent_roots = []
                ancestor = obj.parent
                while ancestor:
                    if ancestor.get('assembly_root'):
                        parent_roots.append(ancestor.name)
                    ancestor = ancestor.parent
                if not structural and (owner not in self.roots or not parent_roots
                                       or owner != parent_roots[0]):
                    registration_errors.append({'object': obj.name, 'assembly_member': owner,
                                                'ancestor_roots': parent_roots})
                if not mesh.materials or any(m is None for m in mesh.materials):
                    material_errors.append({'object': obj.name, 'reason': 'missing material slot'})
                if any(p.material_index >= len(mesh.materials) for p in mesh.polygons):
                    material_errors.append({'object': obj.name, 'reason': 'invalid face material index'})
                bad_faces = sum(p.area < 1e-12 or p.normal.length < .5 for p in mesh.polygons)
                if bad_faces:
                    degenerates.append({'object': obj.name, 'count': bad_faces})
                edge_use = Counter(tuple(sorted((f[i], f[(i+1) % len(f)])))
                                   for f in faces for i in range(len(f)))
                boundary_edges = sum(n == 1 for n in edge_use.values())
                nonmanifold_edges = sum(n > 2 for n in edge_use.values())
                if boundary_edges or nonmanifold_edges:
                    open_meshes.append({'object': obj.name, 'boundary_edges': boundary_edges,
                                        'nonmanifold_edges': nonmanifold_edges})
                if nonmanifold_edges:
                    errors.append({'object': obj.name, 'reason': 'edges used by more than two faces',
                                   'count': nonmanifold_edges})
                if not boundary_edges and not nonmanifold_edges:
                    mesh.calc_loop_triangles()
                    centre = (low+high)*.5
                    volume = sum((vertices[t.vertices[0]]-centre).dot(
                        (vertices[t.vertices[1]]-centre).cross(vertices[t.vertices[2]]-centre))
                        for t in mesh.loop_triangles)/6
                    if volume <= 0:
                        errors.append({'object': obj.name, 'reason': 'closed mesh has nonpositive signed volume',
                                       'signed_volume_m3': volume})
                # Coordinate multiset is independent of vertex ordering and names.
                signature = hashlib.sha256(json.dumps(sorted(tuple(round(c, 7) for c in v)
                                                               for v in vertices)).encode()).hexdigest()
                self.records[obj.name] = {
                    'object': obj, 'bvh': bvh, 'low': low, 'high': high,
                    'vertices': vertices, 'faces': faces, 'structural': structural,
                    'owner': owner, 'ancestors': parent_roots, 'signature': signature,
                    'boundary_edges': boundary_edges, 'nonmanifold_edges': nonmanifold_edges,
                }
                if obj.hide_render or obj.hide_get() or obj.hide_viewport:
                    errors.append({'object': obj.name, 'reason': 'hidden renderable geometry'})
                if any(abs(v-1) > 1e-5 for v in obj.scale):
                    errors.append({'object': obj.name, 'reason': 'unapplied object scale',
                                   'scale': vec(obj.scale)})
                if obj.matrix_world.determinant() <= 0:
                    errors.append({'object': obj.name, 'reason': 'singular or mirrored transform'})
                if obj.type == 'MESH':
                    mismatches = [m.name for m in obj.modifiers if m.show_viewport != m.show_render]
                    if mismatches:
                        errors.append({'object': obj.name, 'reason': 'viewport/render modifier mismatch',
                                       'modifiers': mismatches})
            finally:
                evaluated.to_mesh_clear()
        self.check('geometry_integrity', not errors, errors)
        self.check('material_assignment', not material_errors, material_errors)
        self.check('support_registration', not registration_errors, registration_errors)
        self.check('degenerate_faces', not degenerates, degenerates)
        # Open engraved text/chips and solidified cloth may be intentional.
        self.check('open_mesh_inventory', not open_meshes, open_meshes, 'warning')
        self.result['counts'] = {'scene_objects': len(self.scene.objects),
                                  'evaluated_geometry_objects': len(self.records),
                                  'support_roots': len(self.roots)}

    def scene_integrity(self):
        s = self.scene
        self.check('scene_identity', s.get('section') == 'electrical-room'
                   and self.stage in {'slice', 'full'}, {'section': s.get('section'), 'stage': self.stage})
        self.check('metric_units', s.unit_settings.system == 'METRIC'
                   and abs(s.unit_settings.scale_length-1) < 1e-8,
                   {'system': s.unit_settings.system, 'scale_length': s.unit_settings.scale_length})
        self.check('saved_blend', bool(bpy.data.filepath) and Path(bpy.data.filepath).is_file(),
                   {'path': bpy.data.filepath})
        source = ROOT / 'blender' / 'build_room.py'
        actual = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
        revision = str(s.get('revision', ''))
        checkpoint = ROOT / 'production' / 'checkpoints' / revision / 'build_room.py'
        historical = (hashlib.sha256(checkpoint.read_bytes()).hexdigest()
                      if re.fullmatch(r'[A-Za-z0-9_-]+', revision) and checkpoint.is_file() else None)
        saved = s.get('source_sha256')
        current_matches = actual is not None and actual == saved
        historical_matches = historical is not None and historical == saved
        require_current = getattr(self.options, 'require_current_source', False)
        self.check('source_fingerprint', current_matches or (historical_matches and not require_current),
                   {'saved_sha256': saved, 'current_source_sha256': actual,
                    'checkpoint_source_sha256': historical, 'checkpoint_source': str(checkpoint),
                    'require_current_source': require_current,
                    'verified_source': 'current' if current_matches else
                    ('checkpoint' if historical_matches and not require_current else None)})
        if not current_matches:
            self.check('current_source_differs_from_saved_build', False,
                       {'historical_source_verified': historical_matches,
                        'note': 'This report cannot establish that the current build script reproduces this file.'}, 'warning')
        self.check('render_dimensions', s.render.resolution_x >= 1280 and s.render.resolution_y >= 800
                   and s.render.resolution_percentage == 100,
                   {'width': s.render.resolution_x, 'height': s.render.resolution_y,
                    'percentage': s.render.resolution_percentage})
        dependencies = []
        for library in bpy.data.libraries:
            path = Path(bpy.path.abspath(library.filepath))
            dependencies.append({'kind': 'library', 'name': library.name, 'path': str(path),
                                 'exists': path.is_file()})
        for img in bpy.data.images:
            if img.source in {'GENERATED', 'VIEWER'}:
                continue
            packed = bool(img.packed_file or len(img.packed_files))
            path = Path(bpy.path.abspath(img.filepath, library=img.library))
            exists = packed or path.is_file()
            if img.source == 'TILED' and not packed:
                exists = all(Path(str(path).replace('<UDIM>', str(tile.number))).is_file()
                             for tile in img.tiles)
            dependencies.append({'kind': 'image', 'name': img.name, 'path': str(path),
                                 'packed': packed, 'exists': exists})
        for font in bpy.data.fonts:
            if font.filepath in {'', '<builtin>'}:
                continue
            path = Path(bpy.path.abspath(font.filepath, library=font.library))
            dependencies.append({'kind': 'font', 'name': font.name, 'path': str(path),
                                 'exists': bool(font.packed_file) or path.is_file()})
        self.check('external_dependencies', all(d['exists'] for d in dependencies), dependencies)
        invalid_materials = [m.name for m in bpy.data.materials if m.users
                             and (not m.use_nodes or not any(n.type == 'OUTPUT_MATERIAL'
                                                           for n in m.node_tree.nodes))]
        self.check('material_nodes', not invalid_materials, invalid_materials)

    def dimensions_and_routes(self):
        contract = json.loads((ROOT / 'interface.json').read_text(encoding='utf-8-sig'))
        end = 7.2 if self.stage == 'slice' else contract['envelopes']['main_clear']['max'][1]
        measured = []
        expectations = {
            'Floor': ([-5.5, 0, None], [5.5, end, 0]),
            'Ceiling': ([-5.5, 0, 4.8], [5.5, end, None]),
            'West wall': ([-5.75, 0, 0], [-5.5, end, 4.8]),
        }
        if self.stage == 'slice':
            expectations['East wall'] = ([5.5, 0, 0], [5.75, end, 4.8])
        for name, (expected_low, expected_high) in expectations.items():
            rec = self.records.get(name)
            passed = bool(rec)
            if rec:
                passed = all(e is None or abs(a-e) <= .005
                             for actual, expected in [(rec['low'], expected_low), (rec['high'], expected_high)]
                             for a, e in zip(actual, expected))
            measured.append({'object': name, 'pass': passed,
                             'actual_min': vec(rec['low']) if rec else None,
                             'actual_max': vec(rec['high']) if rec else None,
                             'expected_min': expected_low, 'expected_max': expected_high})
        self.check('architectural_dimensions', all(m['pass'] for m in measured), measured)
        routes = {'MAIN_KEEP_CLEAR': ([-1.2, 0, .025], [1.2, end, 2.7]),
                  'D01_CLEAR_APERTURE': ([-1.2, -.175, .025], [1.2, .175, 2.7])}
        if self.stage == 'full':
            branch = contract['circulation']['reserve_branch_design']
            routes.update({'D02_CLEAR_APERTURE': ([-1.2, end-.175, .025], [1.2, end+.175, 2.7]),
                           'RESERVE_BRANCH_KEEP_CLEAR': ([*branch['xy_min'], .025], [*branch['xy_max'], 2.7]),
                           'P03_CLEAR_APERTURE': ([5.5, 12, .025], [5.75, 14.4, 2.7])})
        measurements = []
        for name, (low, high) in routes.items():
            obstructions = []
            for obj_name, rec in self.records.items():
                overlap = [min(high[i], rec['high'][i])-max(low[i], rec['low'][i]) for i in range(3)]
                if all(v > EPS for v in overlap):
                    obstructions.append({'object': obj_name, 'owner': rec['owner'],
                                         'overlap_m': vec(overlap), 'object_min': vec(rec['low']),
                                         'object_max': vec(rec['high'])})
            measurements.append({'route': name, 'min': low, 'max': high,
                                 'obstructions': obstructions})
        self.check('named_route_aabb_clearance', not any(m['obstructions'] for m in measurements), measurements)
        overhead = []
        for name, rec in self.records.items():
            if 'Utilities' not in {c.name for c in rec['object'].users_collection}:
                continue
            if rec['low'].x < 1.2 and rec['high'].x > -1.2 and rec['high'].y > 0 and rec['low'].y < end:
                overhead.append({'object': name, 'underside_z_m': rec['low'].z,
                                 'pass': rec['low'].z >= 3.5-EPS})
        self.check('overhead_route_crossing', all(m['pass'] for m in overhead), overhead)
        if self.stage == 'full':
            self.full_envelope_and_markers(contract)

    def full_envelope_and_markers(self, contract):
        measurements = []
        structural = [r for r in self.records.values() if r['structural']]
        # Probe actual boundary surfaces, avoiding pilaster/reveal positions.
        probes = [('east_wall', (0, y, 2.4), (1, 0, 0), 5.5) for y in [.5, 8.0, 16.0]]
        probes += [('reserve_floor', (x, y, 1), (0, 0, -1), 1)
                   for x, y in [(6, 11.6), (8, 11.6), (6, 15), (8, 15)]]
        probes += [('reserve_ceiling', (6.5, 13.2, 1), (0, 0, 1), 2.6),
                   ('reserve_east_wall', (6.5, 13.2, 2), (1, 0, 0), 1.8),
                   ('reserve_south_wall', (6.5, 13.2, 2), (0, -1, 0), 2.2),
                   ('reserve_north_wall', (6.5, 13.2, 2), (0, 1, 0), 2.2)]
        for name, origin, direction, expected in probes:
            hits = [(hit[3], rec['object'].name) for rec in structural
                    if (hit := rec['bvh'].ray_cast(Vector(origin), Vector(direction), 20))[0] is not None]
            hit = min(hits) if hits else None
            measurements.append({'probe': name, 'origin': origin, 'direction': direction,
                                 'expected_distance_m': expected, 'hit': hit,
                                 'pass': bool(hit) and abs(hit[0]-expected) <= .005})
        self.check('full_boundary_surface_probes', all(m['pass'] for m in measurements), measurements)
        markers = []
        for definition in contract['portals'] + contract['utilities']:
            obj = self.scene.objects.get(definition['marker'])
            actual = obj.matrix_world.translation if obj else None
            error = (actual-Vector(definition['centre'])).length if obj else None
            markers.append({'marker': definition['marker'], 'expected': definition['centre'],
                            'actual': vec(actual) if obj else None, 'error_m': error,
                            'pass': obj is not None and error <= .005})
        self.check('interface_marker_positions', all(m['pass'] for m in markers), markers)

    def supports(self):
        measurements = []
        for name, root in sorted(self.roots.items()):
            result = {'root': name, 'target': root.get('support_target'), 'anchors': [], 'errors': []}
            measurements.append(result)
            target = self.records.get(root.get('support_target'))
            if not target:
                result['errors'].append('Missing evaluated support target')
                continue
            try:
                anchors = prop_json(root, 'support_anchors')
                if not anchors or not all(len(a) == 3 and finite(a) for a in anchors):
                    raise ValueError('Expected a nonempty JSON list of finite local xyz anchors')
                direction = prop_json(root, 'support_direction')
                if direction is None:
                    direction = {'Floor': [0, 0, -1], 'Ceiling': [0, 0, 1]}.get(root.get('support_target'))
                if direction is None or len(direction) != 3 or not finite(direction):
                    raise ValueError('Non-floor/ceiling targets require local support_direction')
                direction = root.matrix_world.to_3x3() @ Vector(direction)
                if direction.length < 1e-8:
                    raise ValueError('support_direction is zero')
                direction.normalize()
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                result['errors'].append(str(exc))
                continue
            members = [r for r in self.records.values() if r['owner'] == name
                       and r['object'].type != 'FONT']
            if not members:
                result['errors'].append('No directly registered physical component geometry')
                continue
            result['direction_world'] = vec(direction)
            for local in anchors:
                point = root.matrix_world @ Vector(local)
                item = {'local': vec(local), 'world': vec(point), 'errors': []}
                result['anchors'].append(item)
                # Begin outside the tolerable penetration, so a small penetration
                # still hits the intended front surface rather than the far side.
                target_hit, method = support_hit(target, point, direction)
                hit, normal, _, _ = target_hit
                item['target_query_method'] = method
                nearest = target['bvh'].find_nearest(point)
                item['target_nearest_distance_m'] = nearest[3] if nearest[0] is not None else None
                if hit is None:
                    item['errors'].append('No target surface in support direction within 2 m')
                else:
                    signed_gap = (hit-point).dot(direction)
                    angle = math.degrees(normal.angle(-direction))
                    item.update({'target_hit': vec(hit), 'signed_gap_m': signed_gap,
                                 'target_normal': vec(normal), 'target_angle_degrees': angle})
                    if signed_gap > GAP+EPS or signed_gap < -PENETRATION-EPS:
                        item['errors'].append('Anchor gap/penetration exceeds tolerance')
                    if angle > ANGLE:
                        item['errors'].append('Target contact normal is not opposed to support direction')
                candidates = []
                for rec in members:
                    near = rec['bvh'].find_nearest(point)
                    if near[0] is not None:
                        candidates.append((near[3], rec['object'].name, near))
                distance, member_name, member_hit = min(candidates, key=lambda x: x[0])
                member_point, member_normal = member_hit[:2]
                member_angle = math.degrees(member_normal.angle(direction))
                member_rec = self.records[member_name]
                two_sided_sheet = (member_rec['boundary_edges'] > 0 and
                                   min(member_rec['high']-member_rec['low']) <= EPS)
                if two_sided_sheet:
                    member_angle = min(member_angle, 180-member_angle)
                item.update({'physical_member': member_name, 'member_nearest_point': vec(member_point),
                             'anchor_to_member_m': distance, 'member_angle_degrees': member_angle,
                             'zero_thickness_sheet': two_sided_sheet})
                if distance > GAP+EPS:
                    item['errors'].append('No real assembly surface reaches anchor (dummy/floating anchor)')
                if member_angle > ANGLE:
                    item['errors'].append('Assembly surface at anchor does not face support')
                # Check the actual component contact, not only the declared point.
                actual_hit, method = support_hit(target, member_point, direction)
                real_hit, real_normal, _, _ = actual_hit
                item['physical_query_method'] = method
                if real_hit is None:
                    item['errors'].append('Actual member has no support surface in expected direction')
                else:
                    physical_gap = (real_hit-member_point).dot(direction)
                    item['physical_gap_m'] = physical_gap
                    if physical_gap > GAP+EPS or physical_gap < -PENETRATION-EPS:
                        item['errors'].append('Actual component gap/penetration exceeds tolerance')
            # A set of separate planar scuffs/patches cannot hide a floating
            # sheet behind one correctly positioned assembly-level anchor.
            sheet_samples = []
            for rec in members:
                if not rec['boundary_edges'] or min(rec['high']-rec['low']) > EPS:
                    continue
                thin_axis = min(range(3), key=lambda k: rec['high'][k]-rec['low'][k])
                if abs(direction[thin_axis]) < math.cos(math.radians(ANGLE)):
                    # Cabinet-facing chips belong to the cabinet, not its floor.
                    continue
                failures = []
                gaps = []
                for point in rec['vertices']:
                    surface, _ = support_hit(target, point, direction)
                    if surface[0] is None:
                        failures.append('missing target')
                        continue
                    gap = (surface[0]-point).dot(direction)
                    gaps.append(gap)
                    if gap > GAP+EPS or gap < -PENETRATION-EPS or math.degrees(surface[1].angle(-direction)) > ANGLE:
                        failures.append('gap, penetration, or target normal')
                sheet_samples.append({'object': rec['object'].name, 'sampled_vertices': len(rec['vertices']),
                                      'signed_gap_range_m': [min(gaps), max(gaps)] if gaps else None,
                                      'failed_vertices': len(failures)})
            result['planar_sheet_support_samples'] = sheet_samples
            if any(s['failed_vertices'] for s in sheet_samples):
                result['errors'].append('One or more planar member vertices are unsupported')
            result['pass'] = not result['errors'] and not any(a['errors'] for a in result['anchors'])
        self.check('support_contact', bool(measurements) and all(m.get('pass') for m in measurements), measurements)

    def cameras(self):
        cameras = {o.name: o for o in self.scene.objects if o.type == 'CAMERA'}
        required = SLICE_CAMERAS if self.stage == 'slice' else FULL_CAMERAS
        invalid, measured = [], []
        for name, obj in sorted(cameras.items()):
            d = obj.data
            matrix = [float(v) for row in obj.matrix_world for v in row]
            item = {'name': name, 'world_matrix': matrix, 'location': vec(obj.matrix_world.translation),
                    'rotation_euler': vec(obj.rotation_euler), 'lens_mm': d.lens,
                    'sensor_width_mm': d.sensor_width, 'clip_m': [d.clip_start, d.clip_end]}
            measured.append(item)
            if not finite(matrix+[d.lens, d.clip_start, d.clip_end]) or d.lens <= 0 or d.clip_end <= d.clip_start:
                invalid.append(name)
        signatures = Counter(tuple(round(x, 6) for x in m['world_matrix']+[m['lens_mm']]) for m in measured)
        missing = sorted(set(required)-set(cameras))
        active = self.scene.camera.name if self.scene.camera else None
        self.check('fixed_camera_integrity', not missing and not invalid and active in cameras
                   and all(n == 1 for n in signatures.values()),
                   {'required': required, 'missing': missing, 'invalid': invalid,
                    'duplicate_view_count': sum(n-1 for n in signatures.values()),
                    'active_camera': active, 'cameras': measured})
        if self.options.camera_baseline:
            baseline = json.loads(Path(self.options.camera_baseline).read_text(encoding='utf-8-sig'))
            rows = baseline.get('cameras', baseline.get('renders', []))
            failures = []
            for old in rows:
                name = old.get('name', old.get('camera'))
                obj = cameras.get(name)
                if obj is None or abs(obj.data.lens-old['lens_mm']) > 1e-5:
                    failures.append({'camera': name, 'reason': 'missing or changed lens'})
                    continue
                for attr in ['location', 'rotation_euler']:
                    if any(abs(a-b) > 1e-5 for a, b in zip(getattr(obj, attr), old[attr])):
                        failures.append({'camera': name, 'reason': 'changed '+attr})
            self.check('camera_baseline', bool(rows) and not failures,
                       {'file': self.options.camera_baseline, 'failures': failures})

    def intersections(self):
        by_signature = defaultdict(list)
        for name, rec in self.records.items():
            by_signature[rec['signature']].append(name)
        duplicates = [names for names in by_signature.values() if len(names) > 1]
        self.check('exact_duplicate_geometry', not duplicates, duplicates)
        counts = Counter()
        unresolved = []
        reviewed_joins = []
        records = sorted(self.records.values(), key=lambda r: r['low'].x)
        for i, a in enumerate(records):
            for b in records[i+1:]:
                if b['low'].x >= a['high'].x-PENETRATION:
                    break
                overlap = [min(a['high'][k], b['high'][k])-max(a['low'][k], b['low'][k]) for k in range(3)]
                if not all(v > PENETRATION+EPS for v in overlap):
                    continue
                if a['signature'] == b['signature']:
                    counts['exact_duplicate'] += 1
                    continue
                if a['structural'] and b['structural']:
                    counts['known_structural_join'] += 1
                    continue
                if a['owner'] == b['owner']:
                    counts['same_assembly_construction'] += 1
                    continue
                pair = frozenset((base_name(a['object'].name), base_name(b['object'].name)))
                if pair in KNOWN_JOIN_PAIRS:
                    counts['known_named_construction_join'] += 1
                    reviewed_joins.append({'objects': [a['object'].name, b['object'].name],
                                           'reason': KNOWN_JOIN_PAIRS[pair],
                                           'aabb_overlap_m': vec(overlap)})
                    continue
                # A caller can list exact object names for an engineered join.
                # Every such exemption is exposed in the report, never hidden.
                allowed_a = prop_json(a['object'], 'allowed_intersections', [])
                allowed_b = prop_json(b['object'], 'allowed_intersections', [])
                if b['object'].name in allowed_a or a['object'].name in allowed_b:
                    counts['explicit_engineered_join'] += 1
                    reviewed_joins.append({'objects': [a['object'].name, b['object'].name],
                                           'reason': 'object allowed_intersections declaration',
                                           'aabb_overlap_m': vec(overlap)})
                    continue
                if set(a['ancestors']) & set(b['ancestors']):
                    counts['nested_assembly_construction'] += 1
                    continue
                crossings = a['bvh'].overlap(b['bvh'])
                if crossings:
                    unresolved.append({'objects': [a['object'].name, b['object'].name],
                                       'owners': [a['owner'], b['owner']],
                                       'aabb_overlap_m': vec(overlap), 'crossing_triangle_pairs': len(crossings)})
        self.check('cross_assembly_surface_intersections', not unresolved,
                   {'classified_candidate_counts': dict(counts), 'reviewed_joins': reviewed_joins,
                    'unresolved': unresolved})

    def run(self):
        for method in [self.scene_integrity, self.record_geometry, self.dimensions_and_routes,
                       self.supports, self.cameras, self.intersections]:
            try:
                method()
            except Exception as exc:
                self.check('validator_exception.'+method.__name__, False,
                           {'error': str(exc), 'traceback': traceback.format_exc()})
        failures = [c['id'] for c in self.checks if c['status'] == 'FAIL']
        self.result.update({'pass': not failures, 'status': 'PASS' if not failures else 'FAIL',
                            'failure_ids': failures,
                            'warning_ids': [c['id'] for c in self.checks if c['status'] == 'WARN'],
                            'scope': 'partial_style_slice' if self.stage == 'slice' else 'full_room_geometry',
                            'visual_acceptance_evaluated': False, 'runtime_acceptance_evaluated': False})
        return self.result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='JSON output file or directory')
    parser.add_argument('--stage', choices=['auto', 'slice', 'full'], default='auto')
    parser.add_argument('--camera-baseline', help='Earlier build/render manifest with fixed camera transforms')
    parser.add_argument('--require-current-source', action='store_true',
                        help='Final acceptance: require the current build script to match the saved source hash')
    options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    result = Audit(options).run()
    path = Path(options.out)
    if path.suffix.lower() != '.json':
        path = path / 'validation.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(result), indent=2, allow_nan=False), encoding='utf-8')
    print('VALIDATION_'+result['status'], str(path), 'FAILURES', ','.join(result['failure_ids']), flush=True)
    if not result['pass']:
        raise RuntimeError('Electrical Room validation failed; see '+str(path))


if __name__ == '__main__':
    main()
