"""Deterministic, conservative static geometry evidence for the full OCRU room.

Call ``validate_geometry(scene)`` inside Blender after dependency-graph update.
No scene mutation, dependency on an open UI, physics simulation, or quality score.
All collision bounds come from evaluated mesh vertices, including modifiers and
curve/font conversion. See production/technical-method.md for proof boundaries.
"""

from collections import deque
import hashlib
import json
import math
from pathlib import Path
import struct

import bpy
from mathutils import Vector


GRID = 0.10
HUMAN_WIDTH = 0.60
HUMAN_HEIGHT = 1.80
FLOOR_STEP = 0.035
DIM_TOL = 0.002
EPS = 1e-7
GEOMETRY_TYPES = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}
TARGETS = {
    'loading': (0.55, 4.0),
    'controls': (-1.65, 5.8),
    'rear_service': (0.6, 8.35),
    'recovery': (4.3, 6.5),
    'battery': (-2.95, 8.0),
}


def _rounded(value):
    return round(float(value), 6)


def _ray(scene, depsgraph, origin, direction, distance):
    ok, point, normal, face, obj, matrix = scene.ray_cast(
        depsgraph, Vector(origin), Vector(direction), distance=distance)
    return {
        'hit': bool(ok),
        'point_m': [_rounded(x) for x in point] if ok else None,
        'normal': [_rounded(x) for x in normal] if ok else None,
        'object': obj.name if ok and obj else None,
        'distance_m': _rounded((point - Vector(origin)).length) if ok else None,
    }


def _evaluated_bounds(scene, depsgraph):
    """Bounds include all geometric objects; hidden objects are not exempted."""
    bounds, errors = [], []
    for obj in scene.objects:
        if obj.type not in GEOMETRY_TYPES:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = None
        try:
            mesh = evaluated.to_mesh()
            if not mesh or not mesh.vertices:
                errors.append({'object': obj.name, 'reason': 'no evaluated vertices'})
                continue
            points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            if not all(math.isfinite(v) for p in points for v in p):
                errors.append({'object': obj.name, 'reason': 'non-finite evaluated vertices'})
                continue
            digest = hashlib.sha256()
            for point in points:
                digest.update(struct.pack('<3f', *point))
            for polygon in mesh.polygons:
                indices = tuple(polygon.vertices)
                digest.update(struct.pack('<I', len(indices)))
                digest.update(struct.pack('<' + 'I' * len(indices), *indices))
            bounds.append({
                'object': obj.name,
                'min': [min(p[i] for p in points) for i in range(3)],
                'max': [max(p[i] for p in points) for i in range(3)],
                'geometry_role': obj.get('geometry_role', ''),
                'hidden_render': bool(obj.hide_render),
                'surface_signature': digest.hexdigest(),
            })
        except Exception as exc:
            errors.append({'object': obj.name, 'reason': str(exc)})
        finally:
            if mesh is not None:
                evaluated.to_mesh_clear()
    covered_names = {b['object'] for b in bounds}
    for instance in depsgraph.object_instances:
        if instance.is_instance:
            original = instance.object.original
            # Blender 5.2 exposes evaluated curve/font meshes as instances of
            # their own source at the same transform; to_mesh above covers them.
            already_covered = (original.name in covered_names
                               and max(abs(instance.matrix_world[r][c] - original.matrix_world[r][c])
                                       for r in range(4) for c in range(4)) < 1e-7)
            if already_covered:
                continue
            errors.append({'object': instance.object.name,
                           'reason': 'unrealized dependency-graph instance; explicit instance-transform collision support is not implemented'})
    return bounds, errors


def _public_bound(bound):
    return {key: [_rounded(x) for x in value] if key in {'min', 'max'} else value
            for key, value in bound.items()}


def _shell_probes(scene, depsgraph, slice_mode=False):
    """Measure distributed finished shell faces, independently of scene labels."""
    specs = []
    for y in (2.7, 4.4, 6.2):
        specs.append(('main_west', (-3.98, y, 2.75), (-1, 0, 0), 0, -4.0))
    for y in (1.8, 3.8, 8.7):
        specs.append(('main_east', (3.98, y, 2.75), (1, 0, 0), 0, 4.0))
    for x in (-3.0, -2.0, 2.0, 3.0):
        specs.append(('main_front', (x, .02, 2.7), (0, -1, 0), 1, 0.0))
    for x in (-1.8, 0.0, 2.7):
        specs.append(('main_rear', (x, 8.98, 2.7), (0, 1, 0), 1, 9.0))
    for y in (5.0, 6.5, 8.0):
        specs.append(('recovery_east', (6.18, y, 2.7), (1, 0, 0), 0, 6.2))
    for x in (4.5, 5.5, 6.0):
        specs.extend([
            ('recovery_front', (x, 4.62, 2.7), (0, -1, 0), 1, 4.6),
            ('recovery_rear', (x, 8.38, 2.7), (0, 1, 0), 1, 8.4),
        ])
    for x, y in ((-2.8, 2.0), (-2.8, 4.4), (2.8, 6.5), (2.8, 8.5)):
        specs.append(('main_ceiling', (x, y, 3.58), (0, 0, 1), 2, 3.6))
    for x, y in ((4.6, 5.0), (5.4, 6.5), (5.8, 8.0)):
        specs.append(('recovery_ceiling', (x, y, 3.13), (0, 0, 1), 2, 3.15))
    for x, y in ((3.2, .8), (2.8, 4.0), (2.8, 8.4)):
        specs.append(('main_floor', (x, y, FLOOR_STEP), (0, 0, -1), 2, 0.0))
    for x, y in ((4.3, 5.2), (4.3, 7.8), (5.9, 8.1)):
        specs.append(('recovery_floor', (x, y, FLOOR_STEP), (0, 0, -1), 2, 0.0))
    if slice_mode:
        specs = []
        for y in (.5, 1.6, 2.7):
            specs.extend([
                ('slice_west', (-3.98, y, 2.75), (-1, 0, 0), 0, -4.0),
                ('slice_floor', (2.8, y, FLOOR_STEP), (0, 0, -1), 2, 0.0),
                ('slice_ceiling', (2.8, y, 3.58), (0, 0, 1), 2, 3.6),
            ])
    records = []
    for label, origin, direction, axis, expected in specs:
        hit = _ray(scene, depsgraph, origin, direction, .35)
        actual = hit['point_m'][axis] if hit['hit'] else None
        normal_dot = (sum(hit['normal'][i] * -direction[i] for i in range(3))
                      if hit['hit'] else None)
        passed = (actual is not None and abs(actual - expected) <= DIM_TOL
                  and normal_dot >= math.cos(math.radians(12)))
        records.append({'surface': label, 'origin_m': list(origin),
                        'expected_coordinate_m': expected, 'measured_coordinate_m': actual,
                        'normal_toward_interior_dot': normal_dot,
                        **hit, 'pass': passed})
    groups = {}
    for record in records:
        if record['hit']:
            groups.setdefault(record['surface'], []).append(record['measured_coordinate_m'])
    def difference(first, second):
        if first not in groups or second not in groups:
            return None
        return _rounded(min(groups[first]) - max(groups[second]))
    return {
        'method': 'distributed evaluated scene ray casts at expected interior faces',
        'scope': 'slice floor, ceiling and west wall only' if slice_mode else 'main room and recovery alcove',
        'tolerance_m': DIM_TOL,
        'measured_main_m': {
            'width': difference('main_east', 'main_west'),
            'length': difference('main_rear', 'main_front'),
            'height': difference('main_ceiling', 'main_floor'),
        },
        'measured_recovery_m': {
            # The alcove begins at the open east face of the main room.
            'width': difference('recovery_east', 'main_east'),
            'length': difference('recovery_rear', 'recovery_front'),
            'height': difference('recovery_ceiling', 'recovery_floor'),
        },
        'pass': all(r['pass'] for r in records), 'probes': records,
    }


def _entry_probes(scene, depsgraph, portal):
    widths, heights = [], []
    for y in (-.08, 0.0, .08):
        for z in (.10, .60, 1.2, 1.8, 2.30, 2.48):
            origin = (0.0, y, z)
            left = _ray(scene, depsgraph, origin, (-1, 0, 0), 2.0)
            right = _ray(scene, depsgraph, origin, (1, 0, 0), 2.0)
            width = (_rounded(right['point_m'][0] - left['point_m'][0])
                     if left['hit'] and right['hit'] else None)
            widths.append({'origin_m': list(origin), 'width_m': width,
                           'left': left, 'right': right})
        for x in (-.9, -.45, 0.0, .45, .9):
            hit = _ray(scene, depsgraph, (x, y, FLOOR_STEP), (0, 0, 1), 3.5)
            heights.append({'xy_m': [x, y], 'height_m': hit['point_m'][2] if hit['hit'] else None,
                            'ceiling': hit})
    measured_width = min((p['width_m'] for p in widths if p['width_m'] is not None), default=None)
    measured_height = min((p['height_m'] for p in heights if p['height_m'] is not None), default=None)
    return {
        'method': 'minimum over 18 horizontal and 15 upward scene ray casts through door depth',
        'required_width_m': portal['clear_width_m'],
        'required_height_m': portal['clear_height_m'],
        'minimum_sampled_width_m': measured_width,
        'minimum_sampled_height_m': measured_height,
        'width_pass': (all(p['width_m'] is not None for p in widths)
                       and measured_width >= portal['clear_width_m'] - DIM_TOL),
        'height_pass': (all(p['height_m'] is not None for p in heights)
                        and measured_height >= portal['clear_height_m'] - DIM_TOL),
        'width_probes': widths, 'height_probes': heights,
        'limitation': 'Distributed samples can miss local protrusions between probe heights; human routes use all evaluated object bounds.',
    }


def _equipment(bounds, contract):
    berth = contract['equipment']['ocru']['berth']
    candidates = [b for b in bounds if b['geometry_role'] == 'ocru_patient_support']
    if not candidates:
        candidates = [b for b in bounds if 'patient support' in b['object'].lower()
                      or 'patient berth' in b['object'].lower()]
    if len(candidates) != 1:
        return {'berth': {'pass': False, 'reason': 'need exactly one actual patient support object',
                          'candidate_objects': [b['object'] for b in candidates]},
                'pass': False}
    bound = candidates[0]
    measured = {'width_m': _rounded(bound['max'][0] - bound['min'][0]),
                'length_m': _rounded(bound['max'][1] - bound['min'][1]),
                'surface_z': _rounded(bound['max'][2]),
                'centre_xy': [_rounded((bound['min'][i] + bound['max'][i]) / 2) for i in (0, 1)]}
    checks = {key: abs(measured[key] - berth[key]) <= DIM_TOL
              for key in ('width_m', 'length_m', 'surface_z')}
    checks['centre_xy'] = all(abs(measured['centre_xy'][i] - berth['centre_xy'][i]) <= DIM_TOL for i in (0, 1))
    result = {'object': bound['object'], 'evaluated_bounds': _public_bound(bound),
              'required': berth, 'measured': measured, 'checks': checks, 'pass': all(checks.values()),
              'limitation': 'Overall support extents do not establish usable mattress area, ingress clearance, patient fit or loading motion.'}
    return {'berth': result, 'pass': result['pass']}


def _rect_overlap(a, b):
    # Equality is clear contact at the chosen conservative envelope, not penetration.
    return (a[0] < b[2] - EPS and a[2] > b[0] + EPS
            and a[1] < b[3] - EPS and a[3] > b[1] + EPS)


def _domain_contains(rect):
    """Exact containment of a rectangle in the authored L-shaped floor outline."""
    x0, y0, x1, y1 = rect
    if x0 < -4 - EPS or x1 > 6.2 + EPS or y0 < -EPS or y1 > 9 + EPS:
        return False
    if x1 > 4 + EPS and (y0 < 4.6 - EPS or y1 > 8.4 + EPS):
        return False
    return True


class _Navigator:
    def __init__(self, obstacles, domain_max_y=None):
        self.obstacles = obstacles
        self.domain_max_y = domain_max_y
        self.bins = {}
        # Coarse spatial buckets are only an acceleration of exact rectangle tests.
        for index, obstacle in enumerate(obstacles):
            x0, y0, x1, y1 = obstacle['rect']
            for ix in range(math.floor(x0), math.floor(x1) + 1):
                for iy in range(math.floor(y0), math.floor(y1) + 1):
                    self.bins.setdefault((ix, iy), []).append(index)

    def collisions(self, rect):
        indices = set()
        for ix in range(math.floor(rect[0]), math.floor(rect[2]) + 1):
            for iy in range(math.floor(rect[1]), math.floor(rect[3]) + 1):
                indices.update(self.bins.get((ix, iy), ()))
        return [self.obstacles[i]['object'] for i in sorted(indices)
                if _rect_overlap(rect, self.obstacles[i]['rect'])]

    def swept_rect(self, a, b):
        r = HUMAN_WIDTH / 2
        return (min(a[0], b[0]) - r, min(a[1], b[1]) - r,
                max(a[0], b[0]) + r, max(a[1], b[1]) + r)

    def clear(self, a, b=None):
        rect = self.swept_rect(a, a if b is None else b)
        domain_ok = _domain_contains(rect)
        if self.domain_max_y is not None:
            domain_ok = domain_ok and rect[3] <= self.domain_max_y + EPS and rect[2] <= 4 + EPS
        return domain_ok and not self.collisions(rect)


def _compact_path(path):
    if len(path) <= 2:
        return path
    result = [path[0]]
    for i in range(1, len(path) - 1):
        a, b, c = path[i - 1:i + 2]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > EPS:
            result.append(b)
    result.append(path[-1])
    return result


def _floor_support(scene, depsgraph, xy):
    hit = _ray(scene, depsgraph, (*xy, FLOOR_STEP), (0, 0, -1), .10)
    flat_normal = math.cos(math.radians(12))
    if (hit['hit'] and DIM_TOL < hit['point_m'][2] <= FLOOR_STEP
            and 0 < hit['normal'][2] < flat_normal):
        # A floor-mat bevel is an allowed low step, not the supporting plane.
        # Keep the original edge hit and seek a real flat sample within 20 mm.
        for dx, dy in ((.02, 0), (-.02, 0), (0, .02), (0, -.02)):
            support = _ray(scene, depsgraph, (xy[0] + dx, xy[1] + dy, FLOOR_STEP), (0, 0, -1), .10)
            if (support['hit'] and -.005 <= support['point_m'][2] <= FLOOR_STEP
                    and support['normal'][2] >= flat_normal):
                return {**support, 'nominal_xy_m': list(xy),
                        'support_sample_offset_xy_m': [dx, dy], 'step_edge_probe': hit}
    return hit


def _navigation(scene, depsgraph, obstacles, scenario, targets=None, domain_max_y=None):
    nav = _Navigator(obstacles, domain_max_y)
    targets = TARGETS if targets is None else targets
    start = (0.0, .4)
    grid_points = {(ix, iy): (round(ix * GRID, 6), round(iy * GRID, 6))
                   for ix in range(-37, 60) for iy in range(3, 88)}
    clear_nodes = {key for key, point in grid_points.items() if nav.clear(point)}
    source = (0, 4)
    previous = {source: None} if source in clear_nodes else {}
    queue = deque(previous)
    while queue:
        node = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            other = (node[0] + dx, node[1] + dy)
            if other in previous or other not in clear_nodes:
                continue
            if not nav.clear(grid_points[node], grid_points[other]):
                continue
            previous[other] = node
            queue.append(other)
    routes = {}
    floor_cache, headroom_cache = {}, {}
    for name, target in targets.items():
        nearby = sorted((key for key in previous
                         if math.dist(grid_points[key], target) <= GRID * 1.5
                         and nav.clear(grid_points[key], target)),
                        key=lambda key: math.dist(grid_points[key], target))
        blockers = nav.collisions(nav.swept_rect(target, target))
        if not nearby:
            routes[name] = {'target_xy_m': list(target), 'pass': False, 'path_xy_m': [],
                            'target_blockers': blockers,
                            'reason': 'no conservative clear route from inside entry'}
            continue
        key, path = nearby[0], []
        while key is not None:
            path.append(grid_points[key])
            key = previous[key]
        path.reverse()
        if math.dist(path[-1], target) > EPS:
            path.append(target)
        # Floor and ceiling evidence are taken on every path node and midpoint.
        samples = list(path)
        samples.extend(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(path, path[1:]))
        bad_floor, step_edges, headrooms = [], [], []
        for xy in samples:
            cache_key = tuple(round(x, 6) for x in xy)
            if cache_key not in floor_cache:
                floor_cache[cache_key] = _floor_support(scene, depsgraph, xy)
                headroom_cache[cache_key] = _ray(scene, depsgraph, (*xy, FLOOR_STEP), (0, 0, 1), 6.0)
            floor = floor_cache[cache_key]
            above = headroom_cache[cache_key]
            if (not floor['hit'] or floor['point_m'][2] < -.005
                    or floor['normal'][2] < math.cos(math.radians(12))):
                bad_floor.append({'xy_m': list(xy), **floor})
            if 'step_edge_probe' in floor:
                step_edges.append(floor)
            if above['hit'] and floor['hit']:
                headrooms.append(above['point_m'][2] - floor['point_m'][2])
        swept_ok = all(nav.clear(a, b) for a, b in zip(path, path[1:]))
        minimum_headroom = min(headrooms, default=None)
        passed = (swept_ok and not bad_floor and minimum_headroom is not None
                  and minimum_headroom >= HUMAN_HEIGHT - DIM_TOL)
        routes[name] = {'target_xy_m': list(target), 'pass': passed,
                        'path_xy_m': [list(p) for p in _compact_path(path)],
                        'path_length_m': _rounded(sum(math.dist(a, b) for a, b in zip(path, path[1:]))),
                        'swept_square_clear': swept_ok,
                        'sampled_floor_pass': not bad_floor,
                        'failed_floor_probes': bad_floor,
                        'floor_step_edge_probes': step_edges,
                        'floor_probe_count': len(samples),
                        'minimum_sampled_headroom_m': _rounded(minimum_headroom) if minimum_headroom is not None else None,
                        'target_blockers': blockers}
    return {'scenario': scenario, 'start_xy_m': list(start),
            'reachable_grid_nodes': len(previous), 'clear_grid_nodes': len(clear_nodes),
            'routes': routes, 'pass': all(r['pass'] for r in routes.values())}


def _support_registration_audit(scene, bounds):
    """Report coverage without inventing exhaustive support-dependent taxonomy."""
    geometry = [o for o in scene.objects if o.type in GEOMETRY_TYPES]
    registered = [o.name for o in geometry if 'support_target' in o]
    # An explicit support_required flag makes missing registrations a real failure.
    missing = [o.name for o in geometry if o.get('support_required', False) and 'support_target' not in o]
    unclassified = [o.name for o in geometry
                    if (('support_target' not in o and 'support_required' not in o
                         and 'support_classification' not in o)
                        or o.get('support_classification') == 'unclassified support-dependent geometry')]
    evidence = None
    evidence_error = None
    if 'support_validation_json' in scene:
        try:
            evidence = json.loads(scene['support_validation_json'])
        except (TypeError, ValueError) as exc:
            evidence_error = str(exc)
    signatures = {bound['object']: bound['surface_signature'] for bound in bounds}
    current = bool(evidence and evidence.get('surface_signatures') == signatures)
    verified = bool(current and evidence.get('pass') and evidence.get('all_support_chains_pass')
                    and evidence.get('classified_object_count') == len(bounds)
                    and not missing and not unclassified)
    return {
        'registered_object_count': len(registered),
        'registered_objects': registered,
        'explicit_required_but_unregistered': missing,
        'unclassified_geometry_count': len(unclassified),
        'unclassified_geometry': unclassified,
        'explicit_registration_pass': not missing,
        'support_evidence_present': evidence is not None,
        'support_evidence_parse_error': evidence_error,
        'support_evidence_matches_current_evaluated_geometry': current,
        'support_chain_audit_pass': evidence.get('pass') if evidence else None,
        'exhaustive_support_taxonomy_verified': verified,
        'limitation': 'Coverage requires register_supports.py evidence for every object/component and a passing grounded contact chain, with signatures matching current evaluated vertices/topology. Generic construction labels and old single-anchor registrations are insufficient. Finite contact sampling is not a continuous intersection or physical load-stability proof.',
    }


def validate_geometry(scene):
    """Return factual geometry checks; caller decides its overall acceptance gate."""
    contract_path = Path(__file__).resolve().parents[1] / 'scenery' / 'interface.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8-sig'))
    slice_mode = scene.get('phase') == 'slice'
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bounds, evaluation_errors = _evaluated_bounds(scene, depsgraph)
    obstacles = [{'object': b['object'],
                  'rect': [b['min'][0], b['min'][1], b['max'][0], b['max'][1]],
                  'z_range_m': [b['min'][2], b['max'][2]]}
                 for b in bounds
                 if b['max'][2] > FLOOR_STEP + EPS and b['min'][2] < FLOOR_STEP + HUMAN_HEIGHT - EPS]
    shell = _shell_probes(scene, depsgraph, slice_mode)
    portal = next(p for p in contract['portals'] if p['id'] == 'main_entry')
    entry = _entry_probes(scene, depsgraph, portal)
    equipment = (_equipment(bounds, contract) if not slice_mode else
                 {'status': 'not_applicable_to_slice', 'reason': 'OCRU and recovery have not been built'})
    scenarios = [_navigation(scene, depsgraph, obstacles, 'slice_entry_and_wash',
                             {'arrival_pad': (0.0, 2.65), 'wash_approach': (-2.55, 1.65)},
                             domain_max_y=3.2)] if slice_mode else [_navigation(scene, depsgraph, obstacles, 'unobstructed')]
    proxies = []
    for spec in ([] if slice_mode else contract['obstruction_tests']):
        proxy = {'object': 'TEST_ONLY:' + spec['id'], 'rect': spec['bounds_xy'],
                 'z_range_m': [0, .35 if 'body' in spec['id'] else .95]}
        proxies.append(proxy)
        scenarios.append(_navigation(scene, depsgraph, obstacles + [proxy], spec['id']))
    if len(proxies) > 1:
        scenarios.append(_navigation(scene, depsgraph, obstacles + proxies, 'body_and_cart_together'))
    actual_width = entry['minimum_sampled_width_m']
    residual = (actual_width - 2.0) / 2 if actual_width is not None else None
    support_audit = _support_registration_audit(scene, bounds)
    checks = {
        'one_blender_unit_is_one_metre': (scene.unit_settings.system == 'METRIC'
                                        and abs(scene.unit_settings.scale_length - 1.0) < 1e-9),
        'all_geometry_evaluated': not evaluation_errors,
        'entry_width': entry['width_pass'], 'entry_height': entry['height_pass'],
        'explicit_support_registrations': support_audit['explicit_registration_pass'],
        'exhaustive_support_contacts': support_audit['exhaustive_support_taxonomy_verified'],
    }
    if slice_mode:
        checks.update({'slice_floor_ceiling_wall_probes': shell['pass'],
                       'slice_entry_arrival_and_wash_routes': scenarios[0]['pass']})
    else:
        checks.update({'main_and_recovery_dimensions': shell['pass'],
                       'patient_berth_dimensions': equipment['pass'],
                       'unobstructed_personnel_routes': scenarios[0]['pass'],
                       'internal_obstruction_personnel_routes': all(s['pass'] for s in scenarios[1:])})
    return {
        'schema_version': 1, 'units': 'metres',
        'phase': 'slice' if slice_mode else 'full',
        'scope': 'static evaluated Blender geometry; no runtime physics or aesthetic scoring',
        'contract': str(contract_path), 'contract_revision': contract.get('revision'),
        'checks': checks, 'pass': all(checks.values()),
        'evaluated_geometry_count': len(bounds), 'evaluation_errors': evaluation_errors,
        'collision_obstacle_count': len(obstacles),
        'human_model': {'width_m': HUMAN_WIDTH, 'height_m': HUMAN_HEIGHT,
                        'footprint': 'axis-aligned square (conservative for diameter 0.6 m cylinder)',
                        'standing_collision_z_m': [FLOOR_STEP, FLOOR_STEP + HUMAN_HEIGHT],
                        'maximum_floor_step_allowance_m': FLOOR_STEP, 'grid_spacing_m': GRID,
                        'validated_domain': 'main room x=-4…4, y=0…3.2 only' if slice_mode else 'full L-shaped room interior',
                        'collision_method': 'continuous swept square against evaluated world AABBs, cardinal grid search',
                        'geometry_exemptions': 'only geometry wholly below the floor step allowance or wholly above standing height; no object-name exemptions'},
        'shell': shell, 'entry': entry, 'equipment': equipment,
        'navigation_scenarios': scenarios,
        'obstruction_proxies': proxies,
        'doorway_blockage': {
            'transverse_cart_width_m': 2.0, 'transverse_cart_depth_m': .75,
            'centred_cart_side_gap_m': _rounded(residual) if residual is not None else None,
            'human_width_m': HUMAN_WIDTH,
            'personnel_can_pass_beside_centred_cart': residual >= HUMAN_WIDTH if residual is not None else None,
            'result': 'Single exterior doorway can be blocked. Manual clearing/dragging is required; exterior access robustness is not passed.',
            'runtime_clearing_verified': False,
        },
        'support_registration_audit': support_audit,
        'limitations': [
            'Navigation uses conservative evaluated object AABBs. Curves, hollow shapes and rotated objects can create false blockages; a failed route needs geometric investigation, never an automatic exemption.',
            'Passed swept routes prove absence of the evaluated object bounds within the standing envelope; 0.10 m path search may fail to discover another valid route.',
            'Floor contact and ceiling are sampled along routes, not a proof of a watertight walkable surface everywhere.',
            'Small floor features up to 35 mm are treated as step-over surfaces; the engine must determine actual step, snag and collision behaviour.',
            'Clearance starts at the inside entry approach; exterior facility approach, full cart turning/loading and ragdoll motion remain unverified.',
            'Obstruction passes apply only to the listed chosen arrival placements. An obstruction occupying the loading approach or doorway requires physical clearing and cannot be claimed passable.',
            'Shell dimensions and door clearance use explicit distributed ray probes; they do not establish a continuously watertight shell or full portal swept volume.',
            'Support audit fails until every support-dependent assembly/component has classified contact evidence and a grounded chain matching the current evaluated geometry.',
            'No Blender static test proves interaction reach, physics, door trapping, grabbing, dragging, network ownership or runtime navigation.',
        ],
    }
