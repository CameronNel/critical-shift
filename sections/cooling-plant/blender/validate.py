"""Measured Cooling Plant validation; run on a saved blend in a private CPU process.

Example (PowerShell; no render and no live-instance access):
  $env:BLENDER_USER_RESOURCES='<section>/.blender-user-validation'
  & '<Blender>/blender.exe' --background --factory-startup --threads 4 '<section>/blender/cooling_plant.blend' --python '<section>/blender/validate.py' -- --revision S01

No geometry or blend file is written. A PASS here is objective-check evidence only,
never a visual score or final-production acceptance. See production/technical/README.md.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
SECTION = HERE.parent
EPS = 0.00001
DEFAULT_ANGLE = 12.0
GEOMETRY_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}
FULL_ROOTS = ['Floor', 'WestWall', 'EastWall', 'RearWall', 'Ceiling',
              'P-01', 'P-02', 'HX-01 exchanger', 'maintenance workbench',
              'service cart', 'reserve restart socket', 'D02 swinging leaf']
SLICE_ROOTS = ['Floor', 'WestWall', 'RearWall', 'Ceiling', 'P-02',
               'maintenance workbench', 'service cart', 'D02 swinging leaf']
EQUIPMENT_NAMES = {'CP-PUMP-A': 'P-01', 'CP-PUMP-B': 'P-02',
                   'CP-HX-01': 'HX-01 exchanger', 'CP-RESTART': 'reserve restart socket',
                   'CP-WORKBENCH': 'maintenance workbench', 'CP-TOOL-CART': 'service cart'}
STRUCTURE_EXACT = {'Floor', 'WestWall', 'EastWall', 'RearWall', 'Ceiling',
                   'Alcove wall west', 'Alcove wall east', 'Alcove side',
                   'Alcove lintel', 'Alcove ceiling', 'front facade', 'portal head'}
STRUCTURE_PREFIX = ('lower wall impact paint', 'steel column', 'column base shoe',
                    'wall control joint', 'panel horizontal reveal', 'roof girder ',
                    'beam end gusset', 'D02 metal jamb', 'D02 header',
                    'D01 reveal', 'D01 inner guide', 'D01 head track',
                    'D01 raised folded shutter', 'workshop glazing')
FLUSH_PREFIX = ('floor saw cut', 'patched concrete', 'drain channel',
                'drain flush grate', 'route worn edge', 'tube pull bay marking',
                'tube withdrawal floor label', 'D01 threshold', 'pump bay edge', 'route floor identity', 'route arrow')


def base_name(name):
    return re.sub(r'\.\d{3}$', '', name)


def serial(value):
    if isinstance(value, Vector):
        return [round(float(x), 7) for x in value]
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def prop_json(owner, key, default):
    raw = owner.get(key)
    if raw is None:
        return default
    return json.loads(raw) if isinstance(raw, str) else raw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def overlap(a, b, eps=EPS):
    return all(min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) > eps for i in range(3))


def bounds_json(bb):
    return {'min': serial(bb[0]), 'max': serial(bb[1])}


def outside(bb, reserve):
    return [max(0.0, reserve[0][i]-bb[0][i], bb[1][i]-reserve[1][i]) for i in range(3)]


def descendants(root):
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def clip_triangle(tri, lo, hi):
    """Clip an actual world triangle against the slightly inset open AABB."""
    poly = list(tri)
    for axis in range(3):
        for edge, keep_above in ((lo[axis], True), (hi[axis], False)):
            old, poly = poly, []
            if not old:
                return []
            a = old[-1]
            da = a[axis]-edge if keep_above else edge-a[axis]
            for b in old:
                db = b[axis]-edge if keep_above else edge-b[axis]
                if (da >= 0) != (db >= 0):
                    poly.append(a+(b-a)*(da/(da-db)))
                if db >= 0:
                    poly.append(b)
                a, da = b, db
    return poly


class MeasuredMesh:
    def __init__(self, obj, depsgraph):
        self.obj = obj
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            self.vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            self.triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
            self.polygons = len(mesh.polygons)
            self.degenerate = sum(1 for t in mesh.loop_triangles if t.area < 1e-12)
            self.material_indices = set(p.material_index for p in mesh.polygons)
            self.materials = [m.name if m else None for m in mesh.materials]
        finally:
            evaluated.to_mesh_clear()
        if not self.vertices or not self.triangles:
            raise ValueError('evaluated geometry has no renderable faces')
        self.bounds = (Vector(tuple(min(v[i] for v in self.vertices) for i in range(3))),
                       Vector(tuple(max(v[i] for v in self.vertices) for i in range(3))))
        self.tree = BVHTree.FromPolygons(self.vertices, self.triangles, all_triangles=True, epsilon=0.0)

    def point_inside(self, point):
        # A containment fallback for closed solids completely enclosing a keep-clear box.
        direction = Vector((0.93217, 0.27183, 0.23719)).normalized()
        origin = point.copy()
        hits = 0
        for _ in range(128):
            hit, normal, index, distance = self.tree.ray_cast(origin, direction, 200)
            if hit is None:
                return bool(hits % 2)
            hits += 1
            origin = hit + direction * 0.000003
        return False

    def volume_intersection(self, bb):
        if not overlap(self.bounds, bb):
            return None
        lo, hi = bb[0]+Vector((EPS, EPS, EPS)), bb[1]-Vector((EPS, EPS, EPS))
        for ids in self.triangles:
            tri = [self.vertices[i] for i in ids]
            if any(max(v[i] for v in tri) < lo[i] or min(v[i] for v in tri) > hi[i] for i in range(3)):
                continue
            polygon = clip_triangle(tri, lo, hi)
            if len(polygon) >= 3:
                area = sum((polygon[i]-polygon[0]).cross(polygon[i+1]-polygon[0]).length/2 for i in range(1, len(polygon)-1))
                if area > 1e-11:
                    return {'method': 'evaluated_triangle_clipped_to_open_volume',
                            'witness_m': serial(sum(polygon, Vector())/len(polygon))}
        centre = (lo+hi)/2
        if self.point_inside(centre):
            return {'method': 'box_centre_inside_evaluated_solid', 'witness_m': serial(centre)}
        return None


class Validator:
    def __init__(self, args):
        self.args = args
        self.scene = bpy.context.scene
        self.stage = self.scene.get('stage', 'unknown')
        self.revision = self.scene.get('revision', 'unknown')
        self.interface_path = SECTION/'interface.json'
        self.contract = json.loads(self.interface_path.read_text(encoding='utf-8'))
        self.initial_contract_hash = sha(self.interface_path)
        self.issues = []
        self.checks = {}
        self.meshes = {}
        self.exemptions = []
        self.unregistered = []

    def issue(self, category, code, severity='FAIL', **evidence):
        self.issues.append(dict(category=category, code=code, severity=severity, **serial(evidence)))

    def members(self, root):
        return [self.meshes[o.name] for o in descendants(root) if o.name in self.meshes]

    def evaluated_geometry(self):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for obj in self.scene.objects:
            if obj.type not in GEOMETRY_TYPES:
                continue
            if obj.hide_render:
                self.issue('geometry', 'hidden_render_geometry', 'REVIEW', object=obj.name)
            try:
                self.meshes[obj.name] = MeasuredMesh(obj, depsgraph)
            except Exception as exc:
                self.issue('geometry', 'evaluation_failed', object=obj.name, error=str(exc))
        if not self.meshes:
            self.issue('geometry', 'empty_scene')
        self.checks['evaluated_geometry'] = {'objects': len(self.meshes),
            'triangles': sum(len(m.triangles) for m in self.meshes.values()),
            'method': 'depsgraph evaluated meshes including modifiers, curves and text; world coordinates'}

    def scope_and_source(self):
        resources = os.environ.get('BLENDER_USER_RESOURCES')
        if not bpy.app.background:
            self.issue('execution', 'validator_requires_private_headless_process')
        if not resources or not Path(resources).resolve().is_relative_to(SECTION.resolve()):
            self.issue('execution', 'private_section_user_resources_required', configured=resources)
        if self.stage not in ('slice', 'full'):
            self.issue('scope', 'missing_or_unknown_stage', stage=self.stage)
        required = FULL_ROOTS if self.stage == 'full' else SLICE_ROOTS
        missing = [n for n in required if n not in self.scene.objects]
        for name in missing:
            self.issue('scope', 'missing_required_scene_object', object=name)
        if self.stage == 'slice':
            self.issue('scope', 'slice_is_not_full_section', 'INCOMPLETE',
                       omitted_full_scene_objects=[n for n in FULL_ROOTS if n not in self.scene.objects])
        source_digest = hashlib.sha256((HERE/'build_scene.py').read_bytes()+(HERE/'kit.py').read_bytes()+(HERE/'develop_room.py').read_bytes()).hexdigest()
        stored_digest = self.scene.get('source_sha256')
        if stored_digest != source_digest:
            self.issue('reproducibility', 'saved_scene_source_differs_from_current_files',
                       saved_sha256=stored_digest, current_sha256=source_digest)
        if self.args.revision and self.args.revision != self.revision:
            self.issue('reproducibility', 'requested_revision_differs_from_saved_scene',
                       requested=self.args.revision, saved=self.revision)
        if not bpy.data.filepath or not Path(bpy.data.filepath).is_file():
            self.issue('reproducibility', 'scene_not_opened_from_saved_file')
        if self.scene.unit_settings.system != 'METRIC' or abs(self.scene.unit_settings.scale_length-1)>EPS:
            self.issue('scale', 'non_metric_or_non_metre_scale',
                       system=self.scene.unit_settings.system, scale_length=self.scene.unit_settings.scale_length)
        self.checks['source'] = {'saved_source_sha256': stored_digest, 'current_source_sha256': source_digest,
                                 'blend_sha256': sha(Path(bpy.data.filepath)),
                                 'validator_sha256': sha(Path(__file__)),
                                 'interface_sha256': self.initial_contract_hash}

    def is_flush(self, mesh):
        name = base_name(mesh.obj.name)
        floor = float(self.contract['shell'].get('floor_elevation', 0))
        return (name == 'Floor' and mesh.bounds[1].z <= floor+.002 or
                name.startswith(FLUSH_PREFIX) and mesh.bounds[1].z <= floor+.010)

    def door_exempt(self, obj, volume_id):
        if volume_id != 'KC-ALCOVE-DOOR':
            return False
        while obj:
            if obj.name == 'D02 swinging leaf' or obj.get('door_swing_volume') == volume_id:
                return True
            obj = obj.parent
        return False

    def clearances(self):
        volumes = [(v['id'], v['bounds']) for v in self.contract['keep_clear_volumes']]
        volumes += [('PORTAL-'+v['id'], v['clear_bounds']) for v in self.contract['portals']]
        measured = []
        volume_specs = {v['id']: v for v in self.contract['keep_clear_volumes']}
        for volume_id, raw in volumes:
            bb = (Vector(raw['min']), Vector(raw['max']))
            hits = []
            for mesh in self.meshes.values():
                if not overlap(mesh.bounds, bb):
                    continue
                reason = ('expected_floor_or_flush_mark_under_10mm' if self.is_flush(mesh)
                          else 'intentional_leaf_inside_own_swing_reserve' if self.door_exempt(mesh.obj, volume_id) else None)
                permitted = volume_specs.get(volume_id, {}).get('permitted_object_names', [])
                owner = mesh.obj
                while owner and not reason:
                    if owner.name in permitted:
                        reason = 'explicit_contract_permitted_mechanism_or_support:'+owner.name
                    owner = owner.parent
                if reason:
                    self.exemptions.append({'object': mesh.obj.name, 'volume': volume_id, 'reason': reason})
                    continue
                witness = mesh.volume_intersection(bb)
                if witness:
                    penetration = [min(mesh.bounds[1][i], bb[1][i])-max(mesh.bounds[0][i], bb[0][i]) for i in range(3)]
                    hit = dict(object=mesh.obj.name, evaluated_bounds=bounds_json(mesh.bounds),
                               aabb_overlap_extent_m=penetration, **witness)
                    hits.append(hit)
                    self.issue('clearance', 'geometry_intersects_keep_clear', volume=volume_id, **hit)
            measured.append({'id': volume_id, 'bounds': raw, 'geometry_clash_count': len(hits)})
        outer = self.contract['shell']['outer_bounds']
        bb = (Vector(outer['min']), Vector(outer['max']))
        for mesh in self.meshes.values():
            excess = outside(mesh.bounds, bb)
            if max(excess) > .002:
                self.issue('envelope', 'outside_section_outer_bounds', object=mesh.obj.name,
                           excess_xyz_m=excess, evaluated_bounds=bounds_json(mesh.bounds))
        self.checks['keep_clear'] = {'volumes': measured, 'exemptions': self.exemptions,
            'tolerance_m': EPS, 'method': 'AABB broad phase then world triangle clipping and solid containment fallback'}
        main = next((v for v in self.contract['keep_clear_volumes'] if v['id']=='KC-MAIN'),None)
        crossing_height = self.contract.get('utilities',{}).get('minimum_overhead_crossing_underside')
        if main and crossing_height:
            crossing = (Vector(main['bounds']['min']),Vector(main['bounds']['max']))
            crossing[0].z = main['bounds']['max'][2]
            crossing[1].z = crossing_height
            if crossing[1].z > crossing[0].z:
                for mesh in self.meshes.values():
                    if mesh.obj.type != 'CURVE' or 'start_m' not in mesh.obj:
                        continue
                    witness = mesh.volume_intersection(crossing)
                    if witness:
                        self.issue('clearance','utility_crossing_below_required_underside', object=mesh.obj.name,
                            minimum_underside_m=crossing_height, forbidden_crossing_volume=bounds_json(crossing),**witness)
        equipment = []
        for item in self.contract.get('equipment_envelopes', []):
            name = item.get('object_name', EQUIPMENT_NAMES.get(item['id']))
            root = self.scene.objects.get(name) if name else None
            if not root:
                if self.stage == 'full':
                    self.issue('envelope', 'equipment_contract_object_missing', equipment=item['id'], object=name)
                continue
            members = self.members(root)
            excluded = []
            utility_names = item.get('utility_object_names', [])
            body_members = []
            for member in members:
                owner = member.obj
                is_service = owner.name in utility_names
                while owner:
                    is_service = is_service or owner.get('envelope_role') == 'utility'
                    owner = owner.parent
                if is_service:
                    excluded.append(member.obj.name)
                else:
                    body_members.append(member)
            members = body_members
            if not members:
                continue
            actual = (Vector([min(m.bounds[0][i] for m in members) for i in range(3)]),
                      Vector([max(m.bounds[1][i] for m in members) for i in range(3)]))
            bounds = item['bounds']
            excess = outside(actual, (Vector(bounds['min']), Vector(bounds['max'])))
            equipment.append({'id': item['id'], 'object': name, 'actual_bounds': bounds_json(actual),
                              'contract_bounds': bounds, 'excess_xyz_m': excess,
                              'utility_members_excluded_from_equipment_bounds_only': excluded})
            if max(excess) > .005:
                self.issue('envelope', 'equipment_exceeds_declared_envelope', equipment=item['id'], object=name,
                           excess_xyz_m=excess, actual_bounds=bounds_json(actual), contract_bounds=bounds)
        self.checks['equipment_envelopes'] = equipment

    def geometry_dependencies_cameras(self):
        fingerprints = defaultdict(list)
        for name, mesh in self.meshes.items():
            if not mesh.materials or any(i >= len(mesh.materials) or mesh.materials[i] is None for i in mesh.material_indices):
                self.issue('materials', 'missing_assigned_material', object=name, slots=mesh.materials)
            if any(not math.isfinite(c) for v in mesh.vertices for c in v):
                self.issue('geometry', 'nonfinite_world_vertex', object=name)
            if mesh.degenerate:
                self.issue('geometry', 'degenerate_evaluated_triangles', 'INFO', object=name, count=mesh.degenerate,
                           note='Zero-area evaluated tessellation is inventoried, not by itself proof of a visible or structural defect.')
            # Independent of vertex order, material or datablock sharing; 10-micron quantization.
            coords = sorted(tuple(round(c, 5) for c in v) for v in mesh.vertices)
            digest = hashlib.sha256(repr(coords).encode()).hexdigest()
            fingerprints[(len(mesh.vertices), len(mesh.triangles), digest)].append(name)
        duplicates = [v for v in fingerprints.values() if len(v)>1]
        for names in duplicates:
            self.issue('geometry', 'coincident_duplicate_evaluated_mesh', objects=names)
        images = []
        for img in bpy.data.images:
            if img.source in {'VIEWER', 'GENERATED'} or img.packed_file:
                continue
            resolved = Path(bpy.path.abspath(img.filepath, library=img.library))
            images.append({'image': img.name, 'resolved': str(resolved), 'exists': resolved.is_file()})
            if not resolved.is_file():
                self.issue('dependencies', 'missing_external_image', image=img.name, resolved=str(resolved))
        for library in bpy.data.libraries:
            path = Path(bpy.path.abspath(library.filepath))
            if not path.is_file():
                self.issue('dependencies', 'missing_linked_library', library=library.name, resolved=str(path))
        specs = json.loads((SECTION/'production'/'cameras.json').read_text(encoding='utf-8'))
        if len(specs) != 10 or len({c['id'] for c in specs}) != 10:
            self.issue('cameras', 'fixed_camera_manifest_must_have_ten_unique_cameras', count=len(specs))
        for spec in specs:
            cam = self.scene.objects.get(spec['id'])
            if cam is None or cam.type != 'CAMERA':
                self.issue('cameras', 'missing_fixed_camera', camera=spec['id'])
                continue
            position_error = (cam.matrix_world.translation-Vector(spec['position_m'])).length
            expected = (Vector(spec['target_m'])-Vector(spec['position_m'])).normalized()
            actual = (cam.matrix_world.to_3x3() @ Vector((0,0,-1))).normalized()
            angle = math.degrees(actual.angle(expected))
            if position_error > .0001 or angle > .03 or abs(cam.data.lens-spec['lens_mm']) > .001:
                self.issue('cameras', 'fixed_camera_changed', camera=cam.name,
                           position_error_m=position_error, angle_error_degrees=angle,
                           actual_lens_mm=cam.data.lens, expected_lens_mm=spec['lens_mm'])
            for mesh in self.meshes.values():
                p = cam.matrix_world.translation
                if all(mesh.bounds[0][i]+EPS < p[i] < mesh.bounds[1][i]-EPS for i in range(3)) and mesh.point_inside(p):
                    self.issue('cameras', 'camera_inside_evaluated_geometry', camera=cam.name, object=mesh.obj.name)
        if not self.scene.camera or self.scene.camera.type != 'CAMERA':
            self.issue('cameras', 'missing_active_render_camera')
        self.checks['dependencies_and_cameras'] = {'external_images': images, 'fixed_camera_count': len(specs),
            'coincident_duplicate_groups': duplicates,
            'render_resolution': [self.scene.render.resolution_x, self.scene.render.resolution_y, self.scene.render.resolution_percentage]}

    def support_contacts(self):
        tested = []
        coverage = defaultdict(list)
        architecture_claims = []
        registered = [o for o in self.scene.objects if o.get('support_target')]
        roots = [o for o in self.scene.objects if o.get('assembly')]
        for obj in roots:
            if not obj.get('support_target') and obj.get('validation_role') != 'architecture':
                self.issue('support_registration', 'assembly_missing_support_registration', object=obj.name)
        for obj in self.scene.objects:
            if obj.type not in GEOMETRY_TYPES:
                continue
            name = base_name(obj.name)
            if name in STRUCTURE_EXACT or name.startswith(STRUCTURE_PREFIX) or obj.get('validation_role') == 'architecture':
                if obj.get('validation_role') == 'architecture':
                    architecture_claims.append(obj.name)
                continue
            if obj.name in self.meshes and self.is_flush(self.meshes[obj.name]):
                continue
            owner = obj
            covered = False
            top = obj
            while owner:
                top = owner
                if owner.get('support_target') or owner.get('validation_role') == 'architecture':
                    covered = True
                    break
                owner = owner.parent
            if not covered:
                coverage[top.name].append(obj.name)
        self.unregistered = sorted(coverage)
        if self.unregistered:
            self.issue('support_registration', 'unregistered_standalone_geometry_clusters',
                       objects=self.unregistered,
                       note='Explicit coverage required; this is a hierarchy-based inventory, not a claim to infer all semantic props by name.')
        for obj in registered:
            target = self.scene.objects.get(obj['support_target'])
            required = ['support_anchors', 'support_direction', 'max_gap_m', 'max_penetration_m', 'support_angle_tolerance_deg']
            absent = [k for k in required if k not in obj]
            if absent:
                self.issue('support_registration', 'incomplete_support_registration', object=obj.name, missing=absent)
            if target is None:
                self.issue('support', 'support_target_missing', object=obj.name, target=obj['support_target'])
                continue
            props, targets = self.members(obj), self.members(target)
            shared = set(m.obj.name for m in props).intersection(m.obj.name for m in targets)
            if shared:
                self.issue('support', 'support_target_contains_prop_itself', object=obj.name, target=target.name, members=sorted(shared))
                targets = [m for m in targets if m.obj.name not in shared]
            if not props or not targets:
                self.issue('support', 'support_or_prop_has_no_evaluated_faces', object=obj.name, target=target.name)
                continue
            fallback = [0,0,1] if 'ceiling' in target.name.lower() else [0,0,-1]
            direction = Vector(obj.get('support_direction', fallback))
            if direction.length < .1:
                self.issue('support_registration', 'invalid_support_direction', object=obj.name)
                continue
            direction.normalize()
            anchors = prop_json(obj, 'support_anchors', [])
            if not anchors:
                self.issue('support_registration', 'missing_support_anchors', object=obj.name)
            max_gap = float(obj.get('max_gap_m', .005))
            max_pen = float(obj.get('max_penetration_m', .002))
            max_angle = float(obj.get('support_angle_tolerance_deg', DEFAULT_ANGLE))
            if max_gap>.005+EPS or max_pen>.002+EPS or max_angle>DEFAULT_ANGLE+EPS:
                self.issue('support_registration', 'support_tolerance_exceeds_protocol', object=obj.name,
                           max_gap_m=max_gap, max_penetration_m=max_pen, angle_tolerance_degrees=max_angle)
            for index, anchor in enumerate(anchors):
                anchor = Vector(anchor)
                origin = anchor+direction*.08
                candidates = []
                for mesh in props:
                    p,n,face,d = mesh.tree.ray_cast(origin, -direction, .25)
                    if p is not None:
                        candidates.append((d, mesh.obj.name, p, n))
                if not candidates:
                    self.issue('support', 'anchor_has_no_actual_prop_surface', object=obj.name,
                               target=target.name, anchor_index=index, anchor_m=anchor)
                    continue
                _, member, point, prop_normal = min(candidates, key=lambda x:x[0])
                support_origin = point-direction*.1
                candidates = []
                for mesh in targets:
                    p,n,face,d = mesh.tree.ray_cast(support_origin, direction, .35)
                    if p is not None:
                        candidates.append((d, mesh.obj.name, p, n))
                if not candidates:
                    self.issue('support', 'no_support_surface_in_expected_direction', object=obj.name,
                               target=target.name, anchor_index=index, measured_prop_surface_m=point)
                    continue
                _, support_member, surface, normal = min(candidates, key=lambda x:x[0])
                gap = (surface-point).dot(direction)
                angle = math.degrees(normal.angle(-direction))
                entry = dict(object=obj.name, target=target.name, anchor_index=index, anchor_m=anchor,
                    actual_prop_member=member, actual_support_member=support_member,
                    actual_prop_contact_m=point, actual_support_contact_m=surface,
                    signed_gap_m=gap, support_angle_degrees=angle,
                    max_gap_m=max_gap, max_penetration_m=max_pen, angle_tolerance_degrees=max_angle)
                tested.append(serial(entry))
                if gap>max_gap+EPS:
                    self.issue('support', 'floating_support_contact', **entry)
                elif gap < -max_pen-EPS:
                    self.issue('support', 'support_penetration_exceeds_tolerance', **entry)
                if angle > max_angle+.01:
                    self.issue('support', 'implausible_support_surface_angle', **entry)
        self.checks['support_contacts'] = {'registered_roots': len(registered), 'tested_anchors': tested,
            'unregistered_standalone_objects_or_root_clusters': dict(coverage),
            'explicit_architecture_claims_for_human_audit': architecture_claims,
            'method': 'evaluated prop surface ray then intended evaluated support ray, signed gap and normal; anchors alone never count as contact'}

    def pipe_connections(self):
        pipes = {}
        for obj in self.scene.objects:
            if obj.type != 'CURVE' or 'start_m' not in obj:
                continue
            splines = obj.data.splines
            if not splines:
                self.issue('pipes', 'pipe_has_no_source_spline', object=obj.name)
                continue
            spline = splines[0]
            local_points = [Vector(p.co[:3]) for p in spline.points]
            points = [obj.matrix_world @ p for p in local_points]
            if not points:
                self.issue('pipes', 'unsupported_pipe_spline_type', object=obj.name)
                continue
            pipes[obj.name] = points
            for endpoint, actual, actual_local in [('start', points[0], local_points[0]), ('end', points[-1], local_points[-1])]:
                recorded = Vector(obj[endpoint+'_m'])
                # kit.pipe records its native spline points before parent/object placement.
                # Compare metadata in that same local frame; use world points for joins.
                error = (actual_local-recorded).length
                if error > .0001:
                    self.issue('pipes', 'stored_endpoint_differs_from_actual_curve', object=obj.name,
                               endpoint=endpoint, error_m=error, actual_world_m=actual,
                               actual_local_m=actual_local, recorded_local_m=recorded)

        def endpoint(name, which):
            if name in pipes:
                return pipes[name][0 if which=='start' else -1]
            return None

        rules = [
            ('pump return branch 7.6','start','PRIMARY RETURN header','centreline'),
            ('pump return branch 7.6','end','P-02 suction union cast flange','solid'),
            ('pump discharge riser 7.6','start','P-02 discharge neck','end'),
            ('pump discharge riser 7.6','end','pumped hot header','centreline'),
            ('P01 return branch','start','PRIMARY RETURN header','centreline'),
            ('P01 return branch','end','P-01 suction union cast flange','solid'),
            ('P01 discharge branch','start','P-01 discharge neck','end'),
            ('P01 discharge branch','end','pumped hot header','centreline'),
            ('hot crossfeed to HX','start','pumped hot header','start'),
            ('hot crossfeed to HX','end','HX primary inlet neck','end'),
            ('HX cooled outlet neck','end','cooled SUPPLY return to reactor','start'),
        ]
        custom = prop_json(self.scene, 'pipe_connections_json', [])
        rules += [(r['object'],r['endpoint'],r['target'],r.get('target_endpoint','surface')) for r in custom]
        connections = []
        for name, which, target, target_end in rules:
            point = endpoint(name, which)
            if point is None:
                if self.stage == 'full' or name.startswith(('pump return branch','pump discharge riser')):
                    self.issue('pipes', 'required_pipe_source_missing', object=name, target=target)
                continue
            distance, witness = None, None
            if target_end in ('start','end'):
                witness = endpoint(target, target_end)
                if witness is not None:
                    distance = (point-witness).length
            elif target_end == 'centreline' and target in pipes:
                for a,b in zip(pipes[target],pipes[target][1:]):
                    ab=b-a
                    if ab.length_squared==0:
                        continue
                    q=a+ab*max(0,min(1,(point-a).dot(ab)/ab.length_squared))
                    d=(point-q).length
                    if distance is None or d<distance:
                        distance,witness=d,q
            elif target in self.meshes:
                q,n,i,d = self.meshes[target].tree.find_nearest(point)
                distance,witness=d,q
                if target_end == 'solid' and self.meshes[target].point_inside(point):
                    distance,witness=0.0,point
            record = dict(object=name, endpoint=which, actual_endpoint_m=point, target=target,
                          target_kind=target_end, connection_distance_m=distance, target_witness_m=witness)
            connections.append(serial(record))
            if distance is None:
                self.issue('pipes', 'pipe_connection_target_missing', **record)
            elif distance > .008:
                self.issue('pipes', 'pipe_connection_gap', **record)
        socket_defaults = {'CP-COOL-RETURN':('PRIMARY RETURN header','start'),
                           'CP-COOL-SUPPLY':('cooled SUPPLY return to reactor','end'),
                           'CP-RESERVE-POWER':('reserve cable upfeed','end'),
                           'CP-MINE-WATER':('mine water blank cap','centre'),
                           'CP-PORTABLE-BATTERY':('reserve cap','centre'),
                           'CP-DRAIN-OUT':('HX drain','end')}
        sockets = []
        for spec in self.contract.get('utilities',{}).get('sockets',[]):
            if spec.get('installed') is False:
                sockets.append({'socket':spec['id'],'measurement_status':'NOT_INSTALLED_PROPOSED',
                                'contract_m':spec['position'],
                                'note':'This explicitly proposed external interface is not claimed to exist in scene geometry.'})
                continue
            fallback = socket_defaults.get(spec['id'])
            name=spec.get('source_object',fallback[0] if fallback else None)
            which=spec.get('source_endpoint',fallback[1] if fallback else 'start')
            point=endpoint(name,which)
            if which in ('centre', 'center') and name in self.meshes:
                point=sum(self.meshes[name].bounds,Vector())/2
            if point is None:
                if self.stage=='full':
                    self.issue('pipes', 'utility_socket_has_no_measured_source_endpoint', socket=spec['id'], object=name)
                continue
            distance=(point-Vector(spec['position'])).length
            sockets.append(dict(socket=spec['id'],object=name,endpoint=which,actual_m=serial(point),
                                contract_m=spec['position'],error_m=distance))
            if distance>.008:
                self.issue('pipes','utility_socket_endpoint_disagrees_with_interface',**sockets[-1])
        self.checks['pipes']={'source_curves':len(pipes),'connections':connections,'socket_tests':sockets,
                              'limitation':'Geometric connectivity only; no hydraulic or engine behavior is asserted.'}

    def execute(self):
        # Runtime-only settings: this validator never renders or saves the blend.
        self.scene.render.threads_mode='FIXED'
        self.scene.render.threads=4
        if self.scene.render.engine=='CYCLES':
            self.scene.cycles.device='CPU'
        self.scope_and_source()
        self.evaluated_geometry()
        self.clearances()
        self.geometry_dependencies_cameras()
        self.support_contacts()
        self.pipe_connections()
        if sha(self.interface_path)!=self.initial_contract_hash:
            self.issue('reproducibility','interface_changed_during_validation')
        final_source_digest = hashlib.sha256((HERE/'build_scene.py').read_bytes()+(HERE/'kit.py').read_bytes()+(HERE/'develop_room.py').read_bytes()).hexdigest()
        if final_source_digest != self.checks['source']['current_source_sha256']:
            self.issue('reproducibility','source_files_changed_during_validation')
        failures=sum(i['severity']=='FAIL' for i in self.issues)
        reviews=sum(i['severity']=='REVIEW' for i in self.issues)
        status='FAIL' if failures else 'REVIEW_REQUIRED' if reviews else 'PASS'
        report={'schema':'critical-shift.cooling-plant.technical-validation.v1',
            'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'revision':self.revision,
            'stage':self.stage,'objective_status':status,'failure_count':failures,'review_count':reviews,
            'production_acceptance':'Objective audit only: independent >=90 per-category visual evidence, ten final cameras and cold-start render comparison are separate acceptance evidence',
            'fresh_process_open':bool(bpy.app.background and bpy.data.filepath),
            'cold_start_render_validated':False,
            'scene_path':bpy.data.filepath,'blender_version':bpy.app.version_string,
            'runtime':{'background':bpy.app.background,'threads':4,'render_device':'CPU','render_performed':False,
                       'private_user_resources':os.environ.get('BLENDER_USER_RESOURCES')},
            'limitations':['No visual scores are assigned.',
                'Clearances use actual evaluated surfaces; intended floor/flush marks and own door swing exclusions are enumerated.',
                'Support coverage is audited by root registration and standalone geometry inventory, not perfect semantic inference.',
                'Duplicate detection covers exactly coincident evaluated vertices to 10 microns; arbitrary self-intersections and all nonmanifold geometry are not certified.',
                'Fresh-process open/check is not a cold-start render comparison or runtime engine acceptance.'],
            'checks':self.checks,'issues':self.issues}
        out=Path(self.args.out) if self.args.out else SECTION/'production'/'technical'/f'{self.revision}-validation.json'
        out=out.resolve()
        allowed=(SECTION/'production'/'technical').resolve()
        if not out.is_relative_to(allowed):
            raise ValueError('Validation reports must stay in production/technical')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(serial(report),indent=2),encoding='utf-8')
        counts=Counter(i['category'] for i in self.issues if i['severity']=='FAIL')
        text=[f'# Cooling Plant {self.revision}: objective validation', '',
              f'Status: **{status}**. Scope: **{self.stage}**. {failures} failures; {reviews} review items.', '',
              'This report does not assign a visual score or certify final production acceptance.', '',
              f'Measured {len(self.meshes)} evaluated geometry objects from a fresh headless reopen. No render or geometry changes were performed.', '',
              'Failure categories: '+', '.join(f'{k}: {v}' for k,v in counts.items()), '',
              'Full measured evidence is in the accompanying JSON. Highest-priority failures:', '']
        for issue in [i for i in self.issues if i['severity']=='FAIL'][:30]:
            text.append('- '+issue['code']+': '+json.dumps({k:v for k,v in issue.items() if k not in ('category','code','severity')},ensure_ascii=False))
        text += ['', 'Integration-readiness acceptance also requires independent scores of at least 90 in every required category, ten fixed-camera final renders, and a fresh-process render comparison. This objective audit does not substitute for pixel review.']
        out.with_suffix('.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
        print('COOLING_TECHNICAL_RESULT '+json.dumps({'report':str(out),'revision':self.revision,
            'stage':self.stage,'status':status,'failures':failures,'review_items':reviews,'categories':dict(counts)}))
        return 1 if failures or reviews else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision')
    parser.add_argument('--out')
    parser.add_argument('--strict-exit',action='store_true',help='Exit nonzero for objective failures or required review items.')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    # Refuse accidentally targeting an interactive Blender process.
    if not bpy.app.background:
        raise RuntimeError('Run this validator in a new headless Blender process, never a live UI instance.')
    validator=Validator(args)
    code=validator.execute()
    if args.strict_exit and code:
        raise SystemExit(code)
