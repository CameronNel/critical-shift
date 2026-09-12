"""Cold-process, CPU-only geometric audit; does not mutate or save the scene.

blender -b Fuel_Corridor.blend --python validate.py -- --output audit.json

The frozen camera table is independent of build.py and scene custom properties.
Clearance uses evaluated triangle surfaces, not declared cell/bounding-box widths.
Sampling is an engineering approximation, not engine collision certification.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(os.environ.get('FUEL_CORRIDOR_ROOT',str(Path(__file__).resolve().parents[1])))
CAMERAS = [
    ('C01_ENTRY', (0, 1.4, 1.70), (.25, 9.9, 1.65), 25),
    ('C02_PRIMARY_ROUTE', (3, 9, 1.70), (13, 10.4, 1.70), 27),
    ('C03_HERO', (-1.45, 6.0, 1.70), (1.1, 11.5, 1.8), 22),
    ('C04_REVERSE', (1, 10.5, 1.70), (-.15, 1, 1.60), 26),
    ('C05_EAST_TURN', (11.15, 8.45, 1.70), (14.2, 17, 1.65), 25),
    ('C06_REACTOR_THRESHOLD', (13.5, 19.4, 1.70), (14.3, 24, 2.10), 26),
    ('C07_BYPASS', (.45, 14, 1.70), (-.2, 19.7, 1.65), 25),
    ('C08_SERVICE_JUNCTION', (1.7, 19.85, 1.70), (7.6, 20, 1.6), 25),
    ('C09_MATERIALS', (3.7, 9.9, 1.60), (2.65, 12.32, .85), 42),
    ('C10_PLANT_HEADER', (-.7, 17.2, 1.70), (-5.4, 17.4, 1.45), 25),
]
CAP_ROOTS = {'REFINERY_BOUNDARY', 'REACTOR_BOUNDARY'}
CAP_SUFFIXES = ('_sliding_leaf', '_leaf_stiffener', '_folded_return', '_kick_plate')
SUPPORTED_ROLES = {'floor', 'wall', 'ceiling', 'fixture', 'supported', 'prop'}
GEOMETRY_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE'}
MAX_GAP = .005
MAX_PENETRATION = .002
MAX_ANGLE = 12.0
CONTACT_EPS = .00005


def rounded(value):
    return [round(float(v), 6) for v in value]


def decode(value, default=None):
    if value is None:
        return default
    return json.loads(value) if isinstance(value, str) and value[:1] in '[{' else value


def descendants(obj):
    result = []
    for child in obj.children:
        result.append(child)
        result.extend(descendants(child))
    return result


def lineage(obj):
    result = []
    while obj:
        result.append(obj)
        obj = obj.parent
    return result


def assembly(obj):
    return next((o for o in lineage(obj) if 'assembly_role' in o), None)


def cap_member(obj):
    owner = assembly(obj)
    if owner is None or owner.name not in CAP_ROOTS:
        return False
    # Restrict exclusion to the two named external caps, never a generic flag.
    return bool(obj.get('external_presentation_cap', False)) or any(
        obj.name.startswith(owner.name + suffix) for suffix in CAP_SUFFIXES)


class Geometry:
    def __init__(self, obj, depsgraph):
        self.obj = obj
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            self.vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            self.polygons = [tuple(p.vertices) for p in mesh.polygons]
            self.finite = all(math.isfinite(c) for v in self.vertices for c in v)
            self.bvh = (BVHTree.FromPolygons(self.vertices, self.polygons)
                        if self.finite and self.polygons else None)
            self.bounds = ([min(v[i] for v in self.vertices) for i in range(3)],
                           [max(v[i] for v in self.vertices) for i in range(3)]) if self.vertices else None
            self.materials = [m.name if m else None for m in mesh.materials]
            self.invalid_material_faces = sum(
                p.material_index >= len(mesh.materials) or not mesh.materials[p.material_index]
                for p in mesh.polygons)
            self.zero_area_faces = sum(p.area < 1e-12 for p in mesh.polygons)
            edges = collections.Counter()
            for poly in mesh.polygons:
                for edge in poly.edge_keys:
                    edges[tuple(sorted(edge))] += 1
            self.boundary_edges = sum(n == 1 for n in edges.values())
            self.nonmanifold_edges = sum(n > 2 for n in edges.values())
        finally:
            evaluated.to_mesh_clear()

    def fingerprint(self):
        # Coordinate and face topology comparison independent of vertex numbering.
        coords = [tuple(round(float(c), 6) for c in v) for v in self.vertices]
        faces = sorted(tuple(sorted(coords[i] for i in p)) for p in self.polygons)
        return hashlib.sha256(repr(faces).encode()).hexdigest()


class SurfaceSet:
    def __init__(self, geometries):
        vertices, polygons, self.owners = [], [], []
        for geom in geometries:
            if not geom.bvh:
                continue
            offset = len(vertices)
            vertices.extend(geom.vertices)
            polygons.extend(tuple(i + offset for i in p) for p in geom.polygons)
            self.owners.extend([geom.obj.name] * len(geom.polygons))
        self.bvh = BVHTree.FromPolygons(vertices, polygons) if polygons else None

    def ray(self, origin, direction, distance):
        if self.bvh is None:
            return None
        point, normal, index, length = self.bvh.ray_cast(Vector(origin), Vector(direction), distance)
        if point is None:
            return None
        return {'object': self.owners[index], 'point': rounded(point),
                'normal': rounded(normal), 'distance_m': float(length)}


def camera_audit(scene, expected_samples):
    issues, results = [], []
    actual = sorted(o.name for o in scene.objects if o.type == 'CAMERA')
    expected = sorted(c[0] for c in CAMERAS)
    if actual != expected:
        issues.append({'camera_inventory': {'expected': expected, 'actual': actual}})
    for name, loc, target, lens in CAMERAS:
        obj = scene.objects.get(name)
        if obj is None or obj.type != 'CAMERA':
            continue
        expected_q = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y')
        rotation_error = math.degrees(obj.matrix_world.to_quaternion().rotation_difference(expected_q).angle)
        errors = {}
        for key, actual_v, expected_v, tolerance in [
            ('location_error_m', (obj.matrix_world.translation - Vector(loc)).length, 0, 1e-5),
            ('rotation_error_degrees', rotation_error, 0, .001),
            ('lens_mm', obj.data.lens, lens, 1e-5),
            ('clip_start_m', obj.data.clip_start, .04, 1e-6),
            ('clip_end_m', obj.data.clip_end, 150, 1e-5),
            ('shift_x', obj.data.shift_x, 0, 1e-8), ('shift_y', obj.data.shift_y, 0, 1e-8),
            ('sensor_width_mm', obj.data.sensor_width, 36, 1e-6),
        ]:
            if abs(actual_v - expected_v) > tolerance:
                errors[key] = {'actual': actual_v, 'expected': expected_v}
        if obj.data.type != 'PERSP' or obj.data.dof.use_dof:
            errors['projection_or_dof'] = 'Expected perspective without depth of field'
        results.append({'camera': name, 'status': 'FAIL' if errors else 'PASS', 'errors': errors})
        if errors:
            issues.append({name: errors})
    settings = {
        'engine': (scene.render.engine, 'CYCLES'),
        'resolution': ([scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage], [1440, 960, 100]),
        'samples': (scene.cycles.samples, expected_samples),
        'seed': (scene.cycles.seed, 71),
        'denoising': (scene.cycles.use_denoising, True),
        'max_bounces': (scene.cycles.max_bounces, 8),
        'format': (scene.render.image_settings.file_format, 'PNG'),
        'color_mode': (scene.render.image_settings.color_mode, 'RGB'),
        'view_transform': (scene.view_settings.view_transform, 'AgX'),
        'look': (scene.view_settings.look, 'AgX - Medium High Contrast'),
        'exposure': (round(scene.view_settings.exposure, 5), .10),
        'gamma': (scene.view_settings.gamma, 1.0),
        'pixel_aspect': ([scene.render.pixel_aspect_x, scene.render.pixel_aspect_y], [1.0, 1.0]),
        'border': (scene.render.use_border, False),
        'units': ([scene.unit_settings.system, scene.unit_settings.scale_length], ['METRIC', 1.0]),
    }
    for key, (actual_v, expected_v) in settings.items():
        if actual_v != expected_v:
            issues.append({key: {'actual': actual_v, 'expected': expected_v}})
    return {'status': 'FAIL' if issues else 'PASS', 'cameras': results,
            'settings': {k: a for k, (a, _) in settings.items()}, 'issues': issues}


def geometry_audit(geometries, errors):
    issues, warnings, fingerprints = [], [], collections.defaultdict(list)
    for geom in geometries.values():
        obj = geom.obj
        if not geom.finite:
            issues.append({'object': obj.name, 'issue': 'Non-finite evaluated coordinates'})
        elif geom.polygons:
            fingerprints[geom.fingerprint()].append(obj)
        if not geom.polygons:
            issues.append({'object': obj.name, 'issue': 'Empty evaluated render geometry'})
        if geom.invalid_material_faces:
            issues.append({'object': obj.name, 'issue': 'Missing material', 'faces': geom.invalid_material_faces})
        if geom.zero_area_faces or geom.nonmanifold_edges:
            issues.append({'object': obj.name, 'issue': 'Degenerate or non-manifold evaluated geometry',
                           'zero_area_faces': geom.zero_area_faces, 'edges_with_over_two_faces': geom.nonmanifold_edges})
        if geom.boundary_edges:
            warnings.append({'object': obj.name, 'boundary_edges': geom.boundary_edges,
                             'note': 'Open surface: may be intentional paper/decal/fabric; not automatically a solid collision hull'})
    duplicates = []
    for group in fingerprints.values():
        if len(group) < 2:
            continue
        reasons = [str(o.get('intentional_duplicate_reason', '')).strip() for o in group]
        documented = all(reasons)
        result = {'objects': [o.name for o in group], 'documented': documented, 'reasons': reasons}
        duplicates.append(result)
        if not documented:
            issues.append({'issue': 'Exact coincident evaluated geometry without documented exception', **result})
    for error in errors:
        issues.append(error)
    return {'status': 'FAIL' if issues else 'PASS', 'mesh_objects': len(geometries),
            'evaluated_polygons': sum(len(g.polygons) for g in geometries.values()),
            'issues': issues, 'open_surface_notes': warnings, 'exact_duplicates': duplicates,
            'duplicate_method': 'World-space evaluated polygon topology quantized to 1 micrometre; vertex-order independent. Intersections among different assembly members are not exact duplicates.'}


def dependency_audit():
    issues, resources = [], []
    for kind, items in [('image', bpy.data.images), ('library', bpy.data.libraries),
                        ('font', bpy.data.fonts), ('sound', bpy.data.sounds), ('movieclip', bpy.data.movieclips)]:
        for item in items:
            path = getattr(item, 'filepath', '')
            if not path or path == '<builtin>' or (kind == 'image' and item.source in {'GENERATED', 'VIEWER'}):
                continue
            packed = bool(getattr(item, 'packed_file', None)) or bool(getattr(item, 'packed_files', []))
            absolute = Path(bpy.path.abspath(path, library=getattr(item, 'library', None)))
            exists = absolute.exists()
            resources.append({'type': kind, 'name': item.name, 'path': path, 'packed': packed, 'exists': exists})
            if not packed and not exists:
                issues.append({'name': item.name, 'issue': 'Unresolved external dependency', 'path': str(absolute)})
            elif not packed and not path.startswith('//'):
                issues.append({'name': item.name, 'issue': 'Unpacked absolute dependency is not portable', 'path': path})
    return {'status': 'FAIL' if issues else 'PASS', 'resources': resources, 'issues': issues}


def close_geometry(first, second, tolerance=MAX_GAP):
    """Actual triangle intersection or sampled surface separation, AABB broad-phase only."""
    if not first.bvh or not second.bvh:
        return False
    amin, amax = first.bounds
    bmin, bmax = second.bounds
    if any(amax[i] + tolerance < bmin[i] or bmax[i] + tolerance < amin[i] for i in range(3)):
        return False
    if first.bvh.overlap(second.bvh):
        return True
    for src, dest in [(first, second), (second, first)]:
        # All vertices, plus polygon centres, prevent coarse broad-face misses.
        points = list(src.vertices)
        points.extend(sum((src.vertices[i] for i in p), Vector()) / len(p) for p in src.polygons)
        for point in points:
            _, _, _, distance = dest.bvh.find_nearest(point, tolerance + CONTACT_EPS)
            if distance is not None and distance <= tolerance + CONTACT_EPS:
                return True
    return False


def disconnected_diagnostics(graph, connected, geometries):
    remaining, result = set(graph) - connected, []
    while remaining:
        component = {remaining.pop()}
        pending = list(component)
        while pending:
            current = pending.pop()
            found = graph[current] & remaining
            remaining.difference_update(found)
            component.update(found)
            pending.extend(found)
        nearest = None
        # Nearest sampled distance to the grounded component, for repair evidence.
        target = SurfaceSet([geometries[n] for n in connected])
        if target.bvh:
            for name in component:
                geom = geometries[name]
                points = list(geom.vertices)
                points.extend(sum((geom.vertices[i] for i in p), Vector()) / len(p) for p in geom.polygons)
                for point in points:
                    hit, _, index, distance = target.bvh.find_nearest(point)
                    if distance is not None and (nearest is None or distance < nearest['sampled_separation_m']):
                        nearest = {'member': name, 'grounded_member': target.owners[index],
                                   'member_point': rounded(point), 'grounded_point': rounded(hit),
                                   'sampled_separation_m': float(distance)}
        if nearest:
            nearest['sampled_separation_m'] = round(nearest['sampled_separation_m'], 6)
        result.append({'members': sorted(component), 'nearest_grounded_contact': nearest})
    return sorted(result, key=lambda c: -len(c['members']))


def needs_support(obj):
    if obj.get('support_required', False) or obj.get('assembly_role') in SUPPORTED_ROLES:
        return True
    # Independent functional inventory prevents default 'architecture' from exempting props.
    if obj.name in {'Bay_steelwork', 'Longitudinal_tray', 'Service_pipework', 'Long_cask_carrier',
                    'Slice_utility_header', 'Dispatch_paperwork_station', 'Vacuum_flask_shelf'}:
        return True
    if 'assembly_role' in obj:
        collections_used = {c.name for c in obj.users_collection}
        if '05_Practical_lighting' in collections_used:
            return True
        if '04_Freight_and_dressing' in collections_used and obj.name != 'Bay_floor_finish':
            return True
    return False


def support_audit(scene, geometries):
    results, issues, uncovered = [], [], []
    support_links, direct_architecture = collections.defaultdict(set), set()
    registrations = [o for o in scene.objects if needs_support(o) or 'support_anchors' in o]
    registered = set(registrations)
    for obj in scene.objects:
        if obj.type not in GEOMETRY_TYPES:
            continue
        owner = assembly(obj)
        sensitive = any(c.name in {'02_Structure_and_services', '04_Freight_and_dressing', '05_Practical_lighting'} for c in obj.users_collection)
        if sensitive and (owner is None or owner.name != 'Bay_floor_finish') and not any(p in registered for p in lineage(obj)):
            uncovered.append(obj.name)
    if uncovered:
        issues.append({'issue': 'Unregistered support-dependent geometry', 'objects': uncovered})
    all_support = SurfaceSet([g for g in geometries.values() if g.obj.get('support_surface', False)])
    for obj in sorted(registrations, key=lambda o: o.name):
        result = {'assembly': obj.name, 'role': obj.get('assembly_role', 'unclassified'), 'issues': [], 'anchors': []}
        anchors = decode(obj.get('support_anchors'), [])
        direction_raw = decode(obj.get('support_direction'), None)
        directions = decode(obj.get('support_directions'), None)
        targets = decode(obj.get('support_targets'), None)
        common_target = decode(obj.get('support_target'), None)
        if not anchors or (direction_raw is None and not directions) or (not targets and not common_target):
            result['issues'].append('Registration requires explicit anchors, direction, and intended support_target or per-anchor support_targets')
        try:
            direction = Vector(direction_raw if direction_raw is not None else directions[0]).normalized()
            if direction.length < .99:
                result['issues'].append('Invalid support direction')
        except Exception:
            direction = Vector((0, 0, 0))
            result['issues'].append('Invalid support direction')
        declared = {'max_gap_m': float(obj.get('support_max_gap', MAX_GAP)),
                    'max_penetration_m': float(obj.get('support_max_penetration', MAX_PENETRATION)),
                    'max_angle_degrees': float(obj.get('support_angle_tolerance', MAX_ANGLE))}
        if declared['max_gap_m'] > MAX_GAP or declared['max_penetration_m'] > MAX_PENETRATION or declared['max_angle_degrees'] > MAX_ANGLE:
            result['issues'].append('Declared support tolerance exceeds mandatory 5 mm / 2 mm / 12 degree limits')
        result['tolerances'] = declared
        members = [geometries[o.name] for o in [obj] + descendants(obj) if o.name in geometries]
        own_surfaces = SurfaceSet(members)
        anchor_members = set()
        if targets and len(targets) != len(anchors):
            result['issues'].append('support_targets count differs from anchors')
        if directions and len(directions) != len(anchors):
            result['issues'].append('support_directions count differs from anchors')
        for index, anchor_value in enumerate(anchors):
            sample = {'index': index, 'issues': []}
            try:
                anchor = Vector(anchor_value)
                if len(anchor) != 3 or not all(math.isfinite(v) for v in anchor):
                    raise ValueError('Anchor must be a finite world-space XYZ point')
                sample['world_point'] = rounded(anchor)
                if directions and index < len(directions):
                    direction = Vector(directions[index]).normalized()
                sample['toward_support'] = rounded(direction)
                target_spec = targets[index] if targets and index < len(targets) else common_target
                names = [target_spec] if isinstance(target_spec, str) else list(target_spec or [])
                sample['intended_targets'] = names
                selected = []
                for name in names:
                    target_obj = scene.objects.get(name)
                    if target_obj is None:
                        sample['issues'].append('Intended target missing: ' + str(name))
                        continue
                    selected.extend(geometries[o.name] for o in [target_obj] + descendants(target_obj)
                                    if o.name in geometries and o not in [obj] + descendants(obj))
                for geom in selected:
                    if geom.obj.get('support_surface', False):
                        direct_architecture.add(obj.name)
                    target_owner = next((p for p in lineage(geom.obj) if p in registered), None)
                    if target_owner:
                        support_links[obj.name].add(target_owner.name)
                if not selected:
                    sample['issues'].append('No valid intended support geometry')
                if own_surfaces.bvh:
                    _, _, face_index, distance = own_surfaces.bvh.find_nearest(anchor)
                    sample['distance_to_assembly_surface_m'] = round(distance, 6)
                    sample['anchor_member'] = own_surfaces.owners[face_index]
                    if distance > MAX_GAP + CONTACT_EPS:
                        sample['issues'].append('Declared anchor does not touch own assembly geometry within 5 mm')
                    else:
                        anchor_members.add(own_surfaces.owners[face_index])
                else:
                    sample['issues'].append('Assembly has no evaluated surface geometry')
                if selected and direction.length > .99:
                    surfaces = SurfaceSet(selected)
                    # Start on the prop side, preserving signed penetration at the declared anchor.
                    origin = anchor - direction * .10
                    hit = surfaces.ray(origin, direction, 2.10)
                    sample['target_hit'] = hit
                    if hit is None:
                        sample['issues'].append('No intended support surface in expected direction within 2 m')
                    else:
                        signed_gap = hit['distance_m'] - .10
                        alignment = max(-1, min(1, -Vector(hit['normal']).dot(direction)))
                        angle = math.degrees(math.acos(alignment))
                        sample['signed_gap_m'] = round(signed_gap, 6)
                        sample['support_angle_degrees'] = round(angle, 4)
                        if signed_gap > min(MAX_GAP, declared['max_gap_m']) + CONTACT_EPS:
                            sample['issues'].append('Support gap exceeds 5 mm maximum')
                        if signed_gap < -min(MAX_PENETRATION, declared['max_penetration_m']) - CONTACT_EPS:
                            sample['issues'].append('Support penetration exceeds 2 mm maximum')
                        if angle > min(MAX_ANGLE, declared['max_angle_degrees']) + .01:
                            sample['issues'].append('Support normal exceeds 12 degree orientation tolerance')
                        nearer = all_support.ray(origin, direction, max(.0001, hit['distance_m'] - MAX_PENETRATION))
                        if nearer and nearer['object'] not in {g.obj.name for g in selected}:
                            sample['issues'].append('Another architectural support surface lies in front of declared target')
                            sample['intervening_surface'] = nearer
            except Exception as exc:
                sample['issues'].append(str(exc))
            sample['status'] = 'FAIL' if sample['issues'] else 'PASS'
            result['anchors'].append(sample)
        # A supported root does not excuse disconnected loose tools, cloth, signs or fixtures.
        graph = {g.obj.name: set() for g in members}
        for i, first in enumerate(members):
            for second in members[i + 1:]:
                if close_geometry(first, second):
                    graph[first.obj.name].add(second.obj.name)
                    graph[second.obj.name].add(first.obj.name)
        connected = set(anchor_members)
        pending = list(anchor_members)
        while pending:
            current = pending.pop()
            for neighbor in graph[current] - connected:
                connected.add(neighbor)
                pending.append(neighbor)
        disconnected = sorted(set(graph) - connected)
        result['assembly_member_count'] = len(members)
        result['anchor_connected_members'] = len(connected)
        result['disconnected_members'] = disconnected
        result['disconnected_components'] = disconnected_diagnostics(graph, connected, geometries)
        if disconnected:
            result['issues'].append('Members have no measured contact chain to a support anchor')
        result['status'] = 'FAIL' if result['issues'] or any(a['issues'] for a in result['anchors']) else 'PASS'
        results.append(result)
        if result['status'] == 'FAIL':
            issues.append({'assembly': obj.name, 'issue': 'Failed registration, physical contact, or assembly connectivity'})
    resolved_roots = set(direct_architecture)
    while True:
        found = {name for name, targets in support_links.items() if targets & resolved_roots}
        if found <= resolved_roots:
            break
        resolved_roots.update(found)
    unresolved_roots = sorted(o.name for o in registrations if o.name not in resolved_roots)
    if unresolved_roots:
        issues.append({'issue': 'Support dependency does not reach a registered architectural support surface (possibly missing target or cyclic prop support)', 'assemblies': unresolved_roots})
    return {'status': 'FAIL' if issues else 'PASS', 'assemblies': results, 'issues': issues,
            'support_dependency_edges': {name: sorted(targets) for name, targets in support_links.items()},
            'architecture_rooted_assemblies': sorted(resolved_roots),
            'method': 'Explicit world-space anchors raycast toward named evaluated support targets. Signed gap from 100 mm prop-side offset; normal must oppose direction. Own-anchor proximity plus a triangle-intersection / <=5 mm sampled surface contact graph checks members reach an anchored member.',
            'limitations': 'Contact graph proves geometric attachment approximatively, not mechanical stress, fastening adequacy, or correct support of every hidden interior component. Intentional different-part assembly intersections are accepted; exact duplicates remain separately checked.'}


def inclusive_steps(low, high, maximum_step):
    count = max(1, math.ceil((high - low) / maximum_step))
    return [low + (high - low) * i / count for i in range(count + 1)]


def clearance_ray(surfaces, start, end, findings, stats, label):
    vec = Vector(end) - Vector(start)
    if vec.length < 1e-7:
        return
    stats['rays'] += 1
    hit = surfaces.ray(start, vec.normalized(), vec.length)
    if hit:
        stats['blocked_rays'] += 1
        stats['blocking_objects'].add(hit['object'])
        if len(findings) < 60:
            findings.append({'label': label, 'start': rounded(start), 'end': rounded(end), 'hit': hit})


def straight_route(surfaces, centerline, width, height, name):
    findings, stats = [], {'rays': 0, 'blocked_rays': 0, 'blocking_objects': set()}
    cross_positions, measured = [], []
    z0 = .0051  # Surface finishes <= 5 mm are permitted threshold upstands.
    for index, (start_xy, end_xy) in enumerate(zip(centerline, centerline[1:])):
        start, end = Vector((*start_xy, 0)), Vector((*end_xy, 0))
        axis = (end - start).normalized()
        side = Vector((-axis.y, axis.x, 0))
        length = (end - start).length
        for cross in inclusive_steps(-width / 2 + .0001, width / 2 - .0001, .075):
            for z in inclusive_steps(z0, height, .10):
                offset = side * cross + Vector((0, 0, z))
                clearance_ray(surfaces, start + offset, end + offset, findings, stats, 'longitudinal_%d' % index)
        for along in inclusive_steps(.001, length - .001, .125):
            point = start + axis * along
            cross_positions.append(point)
            for z in [z0, .12, .57, 1.0, 1.7, height]:
                origin = point + Vector((0, 0, z))
                clearance_ray(surfaces, origin - side * (width / 2 - .0001), origin + side * (width / 2 - .0001), findings, stats, 'transverse_%d' % index)
                left, right = surfaces.ray(origin, -side, 12), surfaces.ray(origin, side, 12)
                available = (left['distance_m'] if left else 12) + (right['distance_m'] if right else 12)
                measured.append({'point': rounded(origin), 'width_m': round(available, 5),
                                 'left': left['object'] if left else 'beyond_12m',
                                 'right': right['object'] if right else 'beyond_12m'})
    headroom, floor_issues = [], []
    for point in cross_positions:
        floor = surfaces.ray(point + Vector((0, 0, .05)), (0, 0, -1), .35)
        if not floor or abs(floor['point'][2]) > .00505:
            if len(floor_issues) < 60:
                floor_issues.append({'point': rounded(point), 'hit': floor})
        hit = surfaces.ray(point + Vector((0, 0, z0)), (0, 0, 1), 8)
        if hit:
            headroom.append({'point': rounded(point), 'height_m': round(hit['point'][2], 5), 'object': hit['object']})
    stats['blocking_objects'] = sorted(stats['blocking_objects'])
    return {'name': name, 'status': 'FAIL' if stats['blocked_rays'] or floor_issues else 'PASS',
            'required_width_m': width, 'required_height_m': height, 'centerline': centerline,
            **stats, 'minimum_measured_width': min(measured, key=lambda m: m['width_m']) if measured else None,
            'minimum_centerline_headroom': min(headroom, key=lambda m: m['height_m']) if headroom else None,
            'floor_continuity_issues': floor_issues, 'first_obstructions': findings,
            'measurement_scope': 'Three-dimensional crosshatched ray volume, transverse pitch <=75 mm, vertical pitch <=100 mm, longitudinal cross-sections <=125 mm. Side width sampled at six heights; headroom and floor datum sampled along centerline. Edges inset 0.1 mm for numeric contact; ground starts 5.1 mm above Z0.'}


def turn_volume(surfaces, center, diameter, height, name):
    radius = diameter / 2
    findings, stats = [], {'rays': 0, 'blocked_rays': 0, 'blocking_objects': set()}
    for z in inclusive_steps(.0051, height, .10):
        for cross in inclusive_steps(-radius + .001, radius - .001, .075):
            half = math.sqrt(max(0, radius * radius - cross * cross)) - .0001
            for rotate in [False, True]:
                points = [(center[0] - half, center[1] + cross, z), (center[0] + half, center[1] + cross, z)]
                if rotate:
                    points = [(center[0] + cross, center[1] - half, z), (center[0] + cross, center[1] + half, z)]
                clearance_ray(surfaces, *points, findings, stats, name)
    stats['blocking_objects'] = sorted(stats['blocking_objects'])
    return {'name': name, 'status': 'FAIL' if stats['blocked_rays'] else 'PASS',
            'center': center, 'operating_diameter_m': diameter, 'height_m': height,
            **stats, 'first_obstructions': findings,
            'scope': 'Sampled orthogonal chords through a 3D operating cylinder, a conservative centered spin envelope for the 2.2 x 0.9 m cart. Not steerable-wheel dynamics, operator-body simulation, or turning trajectory proof.'}


def stretcher_turn(surfaces):
    findings, stats = [], {'rays': 0, 'blocked_rays': 0, 'blocking_objects': set()}
    center = Vector((0, 19.8, 0))
    for degrees in range(0, 91, 5):
        angle = math.radians(degrees)
        axis, side = Vector((math.cos(angle), math.sin(angle), 0)), Vector((-math.sin(angle), math.cos(angle), 0))
        for z in inclusive_steps(.0051, 1.1, .10):
            for cross in inclusive_steps(-.375, .375, .075):
                mid = center + side * cross + Vector((0, 0, z))
                clearance_ray(surfaces, mid - axis * 1.1, mid + axis * 1.1, findings, stats, 'stretcher_yaw_%d' % degrees)
    stats['blocking_objects'] = sorted(stats['blocking_objects'])
    return {'name': 'nominal_stretcher_bypass_corner', 'status': 'FAIL' if stats['blocked_rays'] else 'PASS',
            'envelope_m': [2.2, .75, 1.1], 'center': rounded(center), **stats,
            'first_obstructions': findings,
            'scope': 'Nominal stretcher only, centered yaw 0..90 degrees at 5 degree steps; no attendant envelope, steering or engine collision claim.'}


def routes_audit(scene, geometries, interface):
    cap_objects = sorted(n for n, g in geometries.items() if cap_member(g.obj))
    if scene.get('stage') != 'full':
        return {'status': 'NOT_RUN', 'reason': 'Style slice does not contain full-route geometry; final acceptance requires --stage full', 'excluded_cap_leaf_members': cap_objects}
    surfaces = SurfaceSet([g for g in geometries.values() if not cap_member(g.obj)])
    freight = interface['route_centerlines']['freight']
    bypass = interface['route_centerlines']['service_bypass']
    checks = [straight_route(surfaces, freight, 2.4, 2.2, 'freight_sampled_straight_clearance'),
              straight_route(surfaces, bypass, 2.0, 2.2, 'dressed_service_bypass'),
              straight_route(surfaces, bypass, .75, 1.1, 'nominal_stretcher_straight_clearance'),
              turn_volume(surfaces, [0, 10], 3.0, 2.2, 'west_freight_operating_turn'),
              turn_volume(surfaces, [14.2, 10], 3.0, 2.2, 'east_freight_operating_turn'),
              stretcher_turn(surfaces)]
    return {'status': 'FAIL' if any(c['status'] != 'PASS' for c in checks) else 'PASS',
            'excluded_cap_leaf_members': cap_objects, 'checks': checks,
            'caveats': ['External boundary frames, jambs, sills and all internal door geometry remain included.',
                        'A 2.4 m measured straight freight proof does not establish the 2.6 m nominal lane design everywhere; reported actual minimum remains authoritative.',
                        'Finite sampling can miss features smaller than grid spacing. This is not a full swept-mesh or runtime controller test.',
                        'No adjacent scene imported: neighboring passage, global fit and cross-section travel remain unverified.']}


def caps_audit(scene, geometries):
    surfaces = SurfaceSet([g for g in geometries.values() if cap_member(g.obj)])
    checks = []
    for name, center, axis in [('REFINERY_BOUNDARY', (0, 0, 1.1), (0, 1, 0)),
                               ('REACTOR_BOUNDARY', (14.2, 24, 1.1), (0, 1, 0))]:
        obj = scene.objects.get(name)
        if not obj:
            checks.append({'boundary': name, 'state': 'ABSENT'})
            continue
        leaves = [o for o in descendants(obj) if '_sliding_leaf' in o.name]
        hits = []
        # Two off-seam rays avoid the narrow centre join between paired leaves.
        for dx in [-.25, .25]:
            origin = Vector(center) + Vector((dx, 0, 0)) - Vector(axis)
            hit = surfaces.ray(origin, axis, 2)
            if hit:
                hits.append(hit)
        checks.append({'boundary': name, 'state': 'CLOSED' if hits else 'NO_SAMPLED_LEAF_BLOCK',
                       'leaf_count': len(leaves), 'authored_closed_states': [bool(o.get('closed_state', False)) for o in leaves],
                       'actual_mesh_hits': hits, 'removable_section_owned_presentation_cap': True})
    return {'state': 'CLOSED_SECTION_PRESENTATION_CAPS' if any(c['state'] == 'CLOSED' for c in checks) else 'NO_CLOSED_CAP_HIT',
            'through_passage': 'BLOCKED_BY_SECTION_CAPS' if any(c['state'] == 'CLOSED' for c in checks) else 'NOT_CERTIFIED',
            'checks': checks,
            'neighbor_state': 'Neighbor files were neither imported nor modified. Existing reactor-owned doors are independently documented closed in interface.json. Removing these connector caps does not open or certify neighboring paths.'}


def run_self_tests(output):
    """Synthetic negative controls in a disposable factory process, never a production scene."""
    if bpy.data.filepath:
        raise RuntimeError('--self-test requires --factory-startup with no loaded .blend')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    material = bpy.data.materials.new('Audit_fixture_material')
    def cube(name, location, dimensions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        obj = bpy.context.object
        obj.name = name
        obj.dimensions = dimensions
        obj.data.materials.append(material)
        return obj
    floor = cube('Audit_floor', (0, 0, -.1), (10, 10, .2))
    floor['support_surface'] = True
    root = bpy.data.objects.new('Audit_supported_fixture', None)
    scene.collection.objects.link(root)
    root['assembly_role'] = 'floor'
    root['support_direction'] = [0, 0, -1]
    root['support_target'] = floor.name
    member = cube('Audit_contact_member', (0, 0, .1), (.2, .2, .2))
    member.parent = root
    def geometry():
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        return {o.name: Geometry(o, graph) for o in scene.objects if o.type in GEOMETRY_TYPES}
    tests = []
    def support_case(name, base, anchor, expected):
        member.location.z = base + .1
        root['support_anchors'] = json.dumps([anchor])
        result = support_audit(scene, geometry())
        tests.append({'name': name, 'expected': expected, 'actual': result['status'],
                      'pass': result['status'] == expected,
                      'anchor_issues': result['assemblies'][0]['anchors'][0]['issues']})
    support_case('exact_floor_contact', 0, [0, 0, 0], 'PASS')
    support_case('4mm_gap_within_limit', .004, [0, 0, .004], 'PASS')
    support_case('20mm_floating_prop', .020, [0, 0, .020], 'FAIL')
    support_case('1mm_penetration_within_limit', -.001, [0, 0, -.001], 'PASS')
    support_case('5mm_penetration_rejected', -.005, [0, 0, -.005], 'FAIL')
    support_case('fabricated_anchor_on_floor_away_from_prop', 0, [.7, 0, 0], 'FAIL')
    support_case('fabricated_floor_anchor_under_floating_prop', .020, [0, 0, 0], 'FAIL')
    root['support_anchors'] = json.dumps([[0, 0, 0]])
    member.location.z = .1
    del root['support_target']
    result = support_audit(scene, geometry())
    tests.append({'name': 'unregistered_target_rejected', 'expected': 'FAIL', 'actual': result['status'], 'pass': result['status'] == 'FAIL'})
    root['support_target'] = floor.name
    loose = cube('Audit_floating_tool', (.5, 0, .2), (.1, .1, .1))
    loose.parent = root
    result = support_audit(scene, geometry())
    tests.append({'name': 'unsupported_assembly_member_rejected', 'expected': 'FAIL', 'actual': result['status'], 'pass': result['status'] == 'FAIL'})
    bpy.data.objects.remove(loose, do_unlink=True)
    bpy.data.objects.remove(member, do_unlink=True)
    bpy.data.objects.remove(root, do_unlink=True)
    surfaces = SurfaceSet(list(geometry().values()))
    result = straight_route(surfaces, [[0, -2], [0, 2]], 2.4, 2.2, 'fixture_clear')
    tests.append({'name': 'clear_route_passes', 'expected': 'PASS', 'actual': result['status'], 'pass': result['status'] == 'PASS'})
    blocker = cube('Audit_route_barrier', (0, 0, 1), (2.6, .01, 2))
    surfaces = SurfaceSet(list(geometry().values()))
    result = straight_route(surfaces, [[0, -2], [0, 2]], 2.4, 2.2, 'fixture_blocked')
    tests.append({'name': '10mm_transverse_barrier_rejected', 'expected': 'FAIL', 'actual': result['status'], 'pass': result['status'] == 'FAIL', 'blocked_rays': result['blocked_rays']})
    blocker['external_presentation_cap'] = True
    tests.append({'name': 'generic_cap_flag_cannot_exclude_barrier', 'expected': False, 'actual': cap_member(blocker), 'pass': not cap_member(blocker)})
    duplicate = cube('Audit_exact_duplicate', (0, 0, 1), (2.6, .01, 2))
    result = geometry_audit(geometry(), [])
    tests.append({'name': 'exact_duplicate_rejected', 'expected': 'FAIL', 'actual': result['status'], 'pass': result['status'] == 'FAIL' and bool(result['exact_duplicates'])})
    report = {'status': 'PASS' if all(t['pass'] for t in tests) else 'FAIL', 'tests': tests,
              'scope': 'Disposable factory-startup CPU validation controls; no production file loaded or saved.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('FUEL_VALIDATOR_SELF_TEST', report['status'], len(tests), str(output), flush=True)
    if report['status'] != 'PASS':
        raise RuntimeError('Technical validator self-test failed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'production/technical_validation.json')
    parser.add_argument('--expected-samples', type=int, default=32)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--source-dir', type=Path, default=ROOT/'blender')
    parser.add_argument('--interface', type=Path, default=ROOT/'interface.json')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if args.self_test:
        run_self_tests(args.output)
        return
    start = time.monotonic()
    scene, depsgraph = bpy.context.scene, bpy.context.evaluated_depsgraph_get()
    interface = json.loads(args.interface.read_text(encoding='utf-8'))
    geometries, errors = {}, []
    for obj in scene.objects:
        if obj.type in GEOMETRY_TYPES:
            try:
                geometries[obj.name] = Geometry(obj, depsgraph)
            except Exception as exc:
                errors.append({'object': obj.name, 'issue': 'Failed evaluated geometry extraction', 'error': str(exc)})
    report = {
        'schema': 'fuel-corridor-technical-audit/1',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'blend': bpy.data.filepath, 'blender_version': bpy.app.version_string,
        'fresh_background_process': bool(bpy.app.background),
        'render_performed': False, 'scene_modified': False, 'validation_device': 'CPU BVH / no Cycles render',
        'revision': scene.get('revision'), 'stage': scene.get('stage'),
        'saved_source_sha256': scene.get('source_sha256'),
        'current_source_sha256': hashlib.sha256((args.source_dir / 'build.py').read_bytes()).hexdigest(),
        'saved_detail_source_sha256': scene.get('detail_source_sha256'),
        'current_detail_source_sha256': hashlib.sha256((args.source_dir / 'valorant_details.py').read_bytes()).hexdigest(),
        'saved_interface_sha256': scene.get('interface_sha256'),
        'current_interface_sha256': hashlib.sha256(args.interface.read_bytes()).hexdigest(),
        'validator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'camera_and_render_settings': camera_audit(scene, args.expected_samples),
        'geometry': geometry_audit(geometries, errors),
        'dependencies': dependency_audit(),
    }
    print('AUDIT_PHASE support', flush=True)
    report['support_contact'] = support_audit(scene, geometries)
    print('AUDIT_PHASE routes', flush=True)
    report['internal_routes'] = routes_audit(scene, geometries, interface)
    report['external_presentation_caps'] = caps_audit(scene, geometries)
    carrier = scene.objects.get('Long_cask_carrier')
    report['carrier_actual_envelope']={'status':'FAIL','issue':'Required carrier absent or has no evaluated members'}
    if carrier:
        members = [geometries[o.name] for o in descendants(carrier) if o.name in geometries]
        if members:
            low = [min(g.bounds[0][i] for g in members) for i in range(3)]
            high = [max(g.bounds[1][i] for g in members) for i in range(3)]
            report['carrier_actual_envelope'] = {'bounds_min': rounded(low), 'bounds_max': rounded(high),
                                                  'dimensions_xyz_m': rounded(Vector(high) - Vector(low)),
                                                  'declared_envelope_lwh_m': interface['handling']['fuel_caddy_parked_envelope']}
            over = [i for i, limit in enumerate(interface['handling']['fuel_caddy_parked_envelope']) if high[i] - low[i] > limit + .002]
            report['carrier_actual_envelope']['status'] = 'FAIL' if over else 'PASS'
            report['carrier_actual_envelope']['exceeded_axes'] = over
            report['carrier_actual_envelope']['tolerance_m'] = .002
    core=[g for n,g in geometries.items() if n.startswith(('Current_reactor_cartridge','Current_cask_end_closure'))]
    payload=interface['handling']['cartridge_envelope']
    report['current_cartridge_core']={'status':'FAIL','issue':'Expected single body and paired closures missing'}
    if len(core)==3:
        low=Vector([min(g.bounds[0][i] for g in core) for i in range(3)])
        high=Vector([max(g.bounds[1][i] for g in core) for i in range(3)])
        dimensions=high-low;expected=[payload['length'],payload['maximum_diameter'],payload['maximum_diameter']]
        report['current_cartridge_core']={'status':'PASS' if all(abs(dimensions[i]-expected[i])<.002 for i in range(3)) else 'FAIL','dimensions_xyz_m':rounded(dimensions),'expected_m':expected,'scope':'Bare current compatible body and closures. Transport straps, lifting eyes, latch hardware belong to the original carrier restraint assembly, not the bare cartridge envelope.'}
    report['source_matches_saved_scene'] = (report['saved_source_sha256'] == report['current_source_sha256'] and report['saved_detail_source_sha256'] == report['current_detail_source_sha256'] and report['saved_interface_sha256'] == report['current_interface_sha256'])
    gates = ['camera_and_render_settings', 'geometry', 'dependencies', 'support_contact', 'internal_routes','current_cartridge_core']
    if 'carrier_actual_envelope' in report:
        gates.append('carrier_actual_envelope')
    report['failed_gates'] = [gate for gate in gates if report[gate]['status'] != 'PASS']
    if not report['source_matches_saved_scene']:
        report['failed_gates'].append('source_matches_saved_scene')
    if not bpy.app.background or not bpy.data.filepath:
        report['failed_gates'].append('cold_reopen_context')
    report['status'] = 'FAIL' if report['failed_gates'] else 'PASS'
    report['elapsed_seconds'] = round(time.monotonic() - start, 2)
    report['acceptance_scope'] = 'Technical geometry gates only; closed external caps remain explicit integration blockers. Pixel quality, repeated review cycles and final cold render comparison are separate mandatory acceptance gates.'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('FUEL_TECHNICAL_AUDIT', report['status'], report['failed_gates'], str(args.output), flush=True)
    if report['status'] != 'PASS':
        # Blender should be invoked with --python-exit-code 1 to propagate this failure.
        raise RuntimeError('Fuel Corridor technical validation failed; see ' + str(args.output))


if __name__ == '__main__':
    main()
