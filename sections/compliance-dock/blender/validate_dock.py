"""Read-only, CPU-only validation of a loaded Compliance Dock .blend.

blender --background --factory-startup scene.blend --python-exit-code 1 \
  --python validate_dock.py -- --output report.json [--interface interface.json]

No operators, scene writes, render calls, live-Blender connections or GPU work.
The report is written before a failing run raises RuntimeError. Use Blender's
--python-exit-code 1: Blender otherwise need not return failure for a script error.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}
EPS = 1e-6
CONTACT_PROBE_M = .25
CLEARANCE_SKIN_M = .001
# A sill up to 20 mm is kept separate from the requested usable headroom.
FLOOR_CONTACT_SKIN_M = .020


def vec(value):
    return [round(float(x), 8) for x in value]


def finite(value):
    return all(math.isfinite(float(x)) for x in value)


def json_safe(value):
    """Keep a diagnostic report writable even when the scene contains NaNs."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def ancestors(obj):
    seen = set()
    while obj is not None and obj.name not in seen:
        seen.add(obj.name)
        yield obj
        obj = obj.parent


def assembly_of(obj):
    return next((p for p in ancestors(obj.parent)
                 if p.get('support_class') == 'supported_assembly'), None)


def bounds(points):
    if not points:
        return None
    return ([min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)])


def overlaps(a, b, skin=0):
    return all(a[0][i] <= b[1][i] + skin and b[0][i] <= a[1][i] + skin
               for i in range(3))


def ray_bounds(origin, direction, box, distance):
    low, high = 0., distance
    for i in range(3):
        if abs(direction[i]) < 1e-12:
            if origin[i] < box[0][i] - EPS or origin[i] > box[1][i] + EPS:
                return False
        else:
            a = (box[0][i] - origin[i]) / direction[i]
            b = (box[1][i] - origin[i]) / direction[i]
            low, high = max(low, min(a, b)), min(high, max(a, b))
            if low > high + EPS:
                return False
    return True


def open_delta(obj):
    """Author-declared static open transform; do not invent an opening pose."""
    for node in ancestors(obj):
        if 'clearance_open_translation' in node:
            value = list(node['clearance_open_translation'])
            if len(value) != 3 or not finite(value):
                raise ValueError(f'{node.name}: invalid clearance_open_translation')
            return Matrix.Translation(Vector(value)), node.name
        if 'clearance_open_angle_deg' in node:
            if 'hinge_world' not in node:
                raise ValueError(f'{node.name}: open angle has no hinge_world')
            hinge = Vector(node['hinge_world'])
            axis = str(node.get('hinge_axis', 'Z'))
            angle = float(node['clearance_open_angle_deg'])
            if len(hinge) != 3 or not finite(hinge) or not math.isfinite(angle) or axis not in {'X', 'Y', 'Z'}:
                raise ValueError(f'{node.name}: invalid open hinge transform')
            return (Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(angle), 4, axis)
                    @ Matrix.Translation(-hinge)), node.name
    return None, None


class Shape:
    def __init__(self, obj, depsgraph, delta=None):
        self.obj = obj
        self.name = obj.name
        self.owner = assembly_of(obj)
        self.solid = bool(obj.get('circulation_solid', False))
        self.architectural = obj.get('support_class') == 'architectural'
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            matrix = obj.matrix_world.copy()
            if delta is not None:
                matrix = delta @ matrix
            normal_matrix = matrix.to_3x3().inverted().transposed()
            self.local_vertices = [v.co.copy() for v in mesh.vertices]
            self.vertices = [matrix @ v for v in self.local_vertices]
            self.triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
            self.normals = [(normal_matrix @ t.normal).normalized() for t in mesh.loop_triangles]
            self.polygons = len(mesh.polygons)
            self.edges = len(mesh.edges)
            self.bounds = bounds(self.vertices)
            self.local_bounds = bounds(self.local_vertices)
            self.matrix = matrix
            self.closed = all(len(link) == 2 for link in self._edge_faces().values()) if self.triangles else False
        finally:
            evaluated.to_mesh_clear()
        if not all(finite(v) for v in self.vertices):
            raise ValueError(f'{obj.name}: nonfinite evaluated vertex')
        self.bvh = BVHTree.FromPolygons(self.vertices, self.triangles, all_triangles=True, epsilon=1e-7) if self.triangles else None

    def _edge_faces(self):
        edges = defaultdict(list)
        for i, tri in enumerate(self.triangles):
            for a, b in zip(tri, tri[1:] + tri[:1]):
                edges[tuple(sorted((a, b)))].append(i)
        return edges

    def ray(self, origin, direction, distance):
        if not self.bvh or not ray_bounds(origin, direction, self.bounds, distance):
            return None
        point, normal, face, length = self.bvh.ray_cast(origin, direction, distance)
        if point is None:
            return None
        return {'point': point, 'normal': self.normals[face], 'face': face,
                'distance': float(length), 'shape': self}

    def contains(self, point):
        # Ray parity on a closed evaluated mesh; two irrational directions reduce
        # shared-edge/tangent ambiguity. Open surfaces cannot establish containment.
        if not self.closed or not all(self.bounds[0][i] < point[i] < self.bounds[1][i] for i in range(3)):
            return False
        votes = []
        for value in ((1., .3713907, .529173), (.219471, 1., .681703)):
            direction = Vector(value).normalized()
            origin = point.copy()
            count = 0
            for _ in range(len(self.triangles) + 1):
                hit = self.ray(origin, direction, 1000.)
                if hit is None:
                    break
                count += 1
                origin = hit['point'] + direction * 1e-5
            votes.append(count % 2 == 1)
        return all(votes)


def nearest_ray(shapes, origin, direction, distance, exclude=()):
    found = None
    skip = set(exclude)
    for shape in shapes:
        if shape.name in skip:
            continue
        hit = shape.ray(origin, direction, distance if found is None else found['distance'] + EPS)
        if hit and (found is None or hit['distance'] < found['distance']):
            found = hit
    return found


class Prism:
    def __init__(self, start, end, width, height, floor=0.):
        start, end = Vector((start[0], start[1], 0)), Vector((end[0], end[1], 0))
        along = end - start
        length = along.length
        if length <= EPS or width <= 0 or height <= 0:
            raise ValueError('Clearance prism dimensions must be positive')
        self.axes = [Vector((-along.y, along.x, 0)).normalized(), along.normalized(), Vector((0, 0, 1))]
        self.centre = (start + end) * .5 + Vector((0, 0, floor + (height + FLOOR_CONTACT_SKIN_M) * .5))
        self.half = Vector((width * .5 - CLEARANCE_SKIN_M, length * .5,
                            (height - FLOOR_CONTACT_SKIN_M) * .5 - CLEARANCE_SKIN_M))
        self.bounds = bounds([self.centre + sum((self.axes[i] * self.half[i] * sign[i] for i in range(3)), Vector())
                              for sign in ((x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))])

    def local(self, point):
        return Vector(tuple((point - self.centre).dot(axis) for axis in self.axes))

    def triangle_intersects(self, points):
        vertices = [self.local(point) for point in points]
        edges = [vertices[(i + 1) % 3] - vertices[i] for i in range(3)]
        unit = (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
        axes = [*unit, edges[0].cross(edges[1])]
        axes.extend(edge.cross(axis) for edge in edges for axis in unit)
        for axis in axes:
            if axis.length_squared < 1e-18:
                continue
            projection = [axis.dot(v) for v in vertices]
            radius = sum(abs(axis[i]) * self.half[i] for i in range(3))
            if min(projection) > radius + 1e-8 or max(projection) < -radius - 1e-8:
                return False
        return True

    def collision(self, shape):
        if not shape.bounds or not overlaps(self.bounds, shape.bounds):
            return None
        for index, tri in enumerate(shape.triangles):
            points = [shape.vertices[i] for i in tri]
            if overlaps(self.bounds, bounds(points)) and self.triangle_intersects(points):
                return {'object': shape.name, 'method': 'triangle_vs_oriented_box_SAT', 'triangle': index,
                        'world_triangle': [vec(p) for p in points]}
        if shape.contains(self.centre):
            return {'object': shape.name, 'method': 'closed_mesh_ray_parity_contains_prism_centre'}
        return None


class Validator:
    def __init__(self, args):
        self.args = args
        self.scene = bpy.context.scene
        self.depsgraph = bpy.context.evaluated_depsgraph_get()
        self.shapes = []
        self.by_name = {}
        self.report = {
            'schema_version': 1,
            'validator': {'file': str(Path(__file__).resolve()),
                          'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'generated_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'read-only static evaluated Blender geometry; CPU calculations; no renders',
            'checks': [], 'errors': [], 'warnings': [], 'support_table': [],
            'geometry': [], 'clearance': {},
            'unverified': [
                'Engine collision meshes, navigation, playtesting and runtime interaction are not exercised.',
                'Cart/body curved turning, ragdoll extents, moving-door swept collisions and handler space are not simulated.',
                'Assembly ancestry and contact anchors do not establish structural load capacity or every internal component load path.',
                'Absence of external libraries does not independently prove original authorship or a factory-empty build.',
            ],
            'tolerances': {'contact_probe_m': CONTACT_PROBE_M, 'numerical_epsilon_m': EPS,
                           'clearance_boundary_skin_m': CLEARANCE_SKIN_M,
                           'floor_sill_allowance_m': FLOOR_CONTACT_SKIN_M},
        }

    def fail(self, code, message, **context):
        self.report['errors'].append({'code': code, 'message': message, **context})

    def check(self, name, start, **details):
        self.report['checks'].append({'name': name, 'status': 'fail' if len(self.report['errors']) > start else 'pass', **details})

    def inventory(self):
        start = len(self.report['errors'])
        path = Path(bpy.data.filepath) if bpy.data.filepath else None
        if not path or not path.is_file():
            self.fail('unsaved_scene', 'A saved .blend must be loaded before validation.')
        self.report['scene'] = {
            'file': str(path) if path else None, 'name': self.scene.name,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else None,
            'bytes': path.stat().st_size if path and path.is_file() else None,
            'blender_runtime_version': bpy.app.version_string,
            'blend_file_version': list(bpy.data.version),
            'stage': self.scene.get('stage'), 'revision': self.scene.get('revision'),
            'object_count': len(self.scene.objects), 'material_count': len(bpy.data.materials),
            'unit_system': self.scene.unit_settings.system,
            'metres_per_unit': self.scene.unit_settings.scale_length,
        }
        if self.scene.unit_settings.system != 'METRIC' or abs(self.scene.unit_settings.scale_length - 1) > EPS:
            self.fail('units', 'Validation contract requires metric units at one metre per scene unit.')
        if self.scene.get('stage') not in ('slice', 'full'):
            self.fail('stage', 'Scene stage must be slice or full.')
        if self.args.expected_stage and self.args.expected_stage != self.scene.get('stage'):
            self.fail('unexpected_stage', f'Expected {self.args.expected_stage} scene.')
        for obj in self.scene.objects:
            values = [x for row in obj.matrix_world for x in row]
            if not finite(values) or not finite(obj.location) or not finite(obj.scale):
                self.fail('nonfinite_transform', 'Nonfinite object transform.', object=obj.name)
                continue
            if obj.type not in GEOMETRY_TYPES:
                continue
            if abs(obj.matrix_world.to_3x3().determinant()) < 1e-12:
                self.fail('singular_transform', 'Geometry has a noninvertible world matrix.', object=obj.name)
                continue
            if not obj.data.materials or any(m is None for m in obj.data.materials):
                self.fail('missing_material', 'Geometry has no material or an empty material slot.', object=obj.name)
            if obj.type == 'MESH':
                if any(p.material_index >= len(obj.data.materials) for p in obj.data.polygons):
                    self.fail('invalid_material_index', 'Polygon refers to a nonexistent material slot.', object=obj.name)
            try:
                shape = Shape(obj, self.depsgraph)
                self.shapes.append(shape)
                self.by_name[obj.name] = shape
                self.report['geometry'].append({
                    'object': obj.name, 'type': obj.type,
                    'assembly': shape.owner.name if shape.owner else None,
                    'support_class': obj.get('support_class'), 'circulation_solid': shape.solid,
                    'world_bounds': [vec(p) for p in shape.bounds] if shape.bounds else None,
                    'source_polygons': len(obj.data.polygons) if obj.type == 'MESH' else None,
                    'evaluated_polygons': shape.polygons, 'evaluated_triangles': len(shape.triangles),
                    'evaluated_vertices': len(shape.vertices), 'closed_triangle_manifold': shape.closed,
                    'materials': [m.name if m else None for m in obj.data.materials],
                })
                if not shape.triangles:
                    self.fail('empty_geometry', 'Geometry evaluates to no triangles.', object=obj.name)
            except Exception as exc:
                self.fail('evaluation_failed', str(exc), object=obj.name)
        points = [Vector(p) for shape in self.shapes if shape.bounds for p in shape.bounds]
        self.report['scene']['geometry_world_bounds'] = [vec(p) for p in bounds(points)] if points else None
        self.report['scene']['evaluated_polygons'] = sum(s.polygons for s in self.shapes)
        self.report['scene']['evaluated_triangles'] = sum(len(s.triangles) for s in self.shapes)
        self.report['scene']['source_polygons'] = sum(len(o.data.polygons) for o in self.scene.objects if o.type == 'MESH')
        self.report['scene']['geometry_object_count'] = len(self.shapes)
        self.check('scene_inventory_transforms_material_assignment', start)

    def resources(self):
        start = len(self.report['errors'])
        resources = {'libraries': [], 'images': []}
        for library in bpy.data.libraries:
            path = Path(bpy.path.abspath(library.filepath))
            resources['libraries'].append({'name': library.name, 'path': str(path), 'exists': path.is_file()})
            self.fail('external_library', 'Original self-contained geometry contract does not permit linked libraries.', library=library.name)
        for image in bpy.data.images:
            packed = bool(image.packed_file) or bool(getattr(image, 'packed_files', ()))
            entry = {'name': image.name, 'source': image.source, 'packed': packed, 'size': list(image.size)}
            if image.source in {'FILE', 'SEQUENCE', 'MOVIE', 'TILED'} and not packed:
                raw = bpy.path.abspath(image.filepath, library=image.library)
                paths = [Path(raw.replace('<UDIM>', str(tile.number))) for tile in image.tiles] if image.source == 'TILED' else [Path(raw)]
                entry['paths'] = [str(p) for p in paths]
                entry['exists'] = all(p.is_file() for p in paths)
                if not raw or not entry['exists']:
                    self.fail('missing_image', 'Image resource cannot be resolved.', image=image.name, paths=entry['paths'])
            resources['images'].append(entry)
        for material in bpy.data.materials:
            if material.use_nodes and material.node_tree:
                for node in material.node_tree.nodes:
                    if node.type in {'TEX_IMAGE', 'TEX_ENVIRONMENT'} and node.image is None:
                        self.fail('unassigned_image_node', 'An image texture node has no image.', material=material.name, node=node.name)
        for obj in self.scene.objects:
            if obj.library or (obj.data and obj.data.library):
                self.fail('linked_object_data', 'Scene geometry/object uses linked external data.', object=obj.name)
        self.report['resources'] = resources
        self.check('external_resource_integrity', start)

    def support(self):
        start = len(self.report['errors'])
        roots = {o.name: o for o in self.scene.objects if o.get('support_class') == 'supported_assembly' or 'support_target' in o}
        raw = self.scene.get('contact_assemblies')
        try:
            registry = json.loads(raw) if isinstance(raw, str) else list(raw)
            if not isinstance(registry, list) or not all(isinstance(x, str) for x in registry):
                raise ValueError('Registry must be a list of object names')
        except Exception as exc:
            self.fail('invalid_contact_registry', str(exc))
            registry = []
        if len(registry) != len(set(registry)):
            self.fail('duplicate_registry_entry', 'An assembly is registered more than once.')
        for name in set(roots) - set(registry):
            self.fail('unregistered_assembly', 'Supported assembly is absent from scene contact_assemblies.', assembly=name)
        for name in set(registry) - set(roots):
            self.fail('invalid_registered_assembly', 'Registry name does not resolve to a supported assembly in this scene.', assembly=name)
        for shape in self.shapes:
            obj, owner = shape.obj, shape.owner
            category = obj.get('support_class')
            if category == 'assembly_component':
                if owner is None or owner.name not in registry or obj.get('assembly') != owner.name:
                    self.fail('invalid_assembly_ancestry', 'Component needs actual supported-assembly ancestry, matching assembly property and registry entry.', object=obj.name, claimed_assembly=obj.get('assembly'))
            elif category == 'architectural':
                if owner is not None:
                    self.fail('architecture_under_assembly', 'Architectural classification conceals component ancestry.', object=obj.name)
            else:
                self.fail('unclassified_geometry', 'Geometry must be architectural or a registered assembly component.', object=obj.name)
        for anchor in (o for o in self.scene.objects if o.get('contact_anchor')):
            owner = assembly_of(anchor)
            if owner is None or owner.name not in registry:
                self.fail('orphan_contact_anchor', 'Anchor is not a child of a registered assembly.', anchor=anchor.name)
        for name, root in roots.items():
            if root.type != 'EMPTY' or root.get('support_class') != 'supported_assembly':
                self.fail('invalid_assembly_root', 'Supported assembly root must be a classified empty.', assembly=name)
            target_name = root.get('support_target')
            target = self.by_name.get(target_name)
            components = [s for s in self.shapes if s.owner == root]
            anchors = [o for o in self.scene.objects if o.get('contact_anchor') and assembly_of(o) == root]
            if not components:
                self.fail('empty_assembly', 'Registered assembly has no component geometry.', assembly=name)
            if not anchors:
                self.fail('assembly_without_anchors', 'Registered assembly has no physical contact anchors.', assembly=name)
            if target is None or target in components:
                self.fail('invalid_support_target', 'Support target is missing, not evaluated geometry, or belongs to its own assembly.', assembly=name, target=target_name)
                continue
            try:
                local_direction = Vector(root['support_direction'])
                direction = root.matrix_world.to_3x3() @ local_direction
                gap = float(root['max_gap_m'])
                penetration = float(root['max_penetration_m'])
                angle = float(root['angle_tolerance_deg'])
                if len(direction) != 3 or not finite(direction) or direction.length < EPS:
                    raise ValueError('Support direction must be finite and nonzero')
                if not finite((gap, penetration, angle)) or not (0 <= gap <= .005 and 0 <= penetration <= .002 and 0 <= angle <= 12):
                    raise ValueError('Contact limits may not exceed .005m gap, .002m penetration, 12 degrees')
                direction.normalize()
            except Exception as exc:
                self.fail('invalid_support_metadata', str(exc), assembly=name)
                continue
            for anchor in anchors:
                before = len(self.report['errors'])
                point = anchor.matrix_world.translation.copy()
                row = {'assembly': name, 'anchor': anchor.name, 'target': target_name,
                       'anchor_world': vec(point), 'support_direction_world': vec(direction),
                       'limits': {'gap_m': gap, 'penetration_m': penetration, 'angle_deg': angle}}
                origin = point - direction * CONTACT_PROBE_M
                hit = target.ray(origin, direction, 2 * CONTACT_PROBE_M)
                if hit is None:
                    row['target_ray_hit'] = None
                    self.fail('support_ray_miss', 'Anchor support ray misses its declared target within the probe range.', assembly=name, anchor=anchor.name, target=target_name)
                else:
                    signed_gap = (hit['point'] - point).dot(direction)
                    normal_angle = math.degrees(math.acos(max(-1., min(1., hit['normal'].dot(-direction)))))
                    row.update({'target_ray_hit': vec(hit['point']), 'target_normal_world': vec(hit['normal']),
                                'target_triangle': hit['face'], 'signed_gap_m': signed_gap,
                                'gap_m': max(0., signed_gap), 'penetration_m': max(0., -signed_gap),
                                'normal_error_deg': normal_angle})
                    if signed_gap > gap + EPS:
                        self.fail('support_gap', 'Anchor is detached from declared support.', assembly=name, anchor=anchor.name, measured_m=signed_gap)
                    if signed_gap < -penetration - EPS:
                        self.fail('support_penetration', 'Anchor penetrates declared support beyond tolerance.', assembly=name, anchor=anchor.name, measured_m=-signed_gap)
                    if normal_angle > angle + .001:
                        self.fail('support_angle', 'Declared direction is not opposed to actual target surface normal.', assembly=name, anchor=anchor.name, measured_deg=normal_angle)
                    # Ignore this assembly when asking which external surface is
                    # immediately behind its anchor, but never ignore another prop.
                    short_origin = point - direction * .025
                    nearest = nearest_ray(self.shapes, short_origin, direction, .050 + max(0, signed_gap),
                                          exclude=[s.name for s in components])
                    row['first_external_surface'] = nearest['shape'].name if nearest else None
                    if nearest and nearest['shape'] != target:
                        difference = (hit['point'] - nearest['point']).dot(direction)
                        row['external_surface_lead_m'] = difference
                        if difference > penetration + EPS:
                            self.fail('wrong_support_surface', 'A different object intercepts contact before the declared support.', assembly=name, anchor=anchor.name, actual_target=nearest['shape'].name, lead_m=difference)
                nearest_component = None
                for component in components:
                    if not component.bvh:
                        continue
                    location, _, face, distance = component.bvh.find_nearest(point)
                    if location is not None and (nearest_component is None or distance < nearest_component[0]):
                        nearest_component = (distance, component, location, face)
                if nearest_component:
                    distance, component, location, face = nearest_component
                    row.update({'nearest_component': component.name, 'component_surface_world': vec(location),
                                'component_distance_m': float(distance), 'component_triangle': face})
                    if distance > gap + EPS:
                        self.fail('anchor_detached_from_assembly', 'Anchor touches no actual assembly component within the contact tolerance.', assembly=name, anchor=anchor.name, nearest_component=component.name, measured_m=float(distance))
                else:
                    self.fail('anchor_without_component_geometry', 'No evaluated component can substantiate this anchor.', assembly=name, anchor=anchor.name)
                row['status'] = 'fail' if len(self.report['errors']) > before else 'pass'
                self.report['support_table'].append(row)
        self.report['support_registry'] = registry
        self.check('contact_registry_ancestry_and_measured_support', start, assemblies=len(roots), anchors=len(self.report['support_table']))

    def duplicates(self):
        start = len(self.report['errors'])
        candidates = defaultdict(list)
        for shape in self.shapes:
            if not shape.bounds:
                continue
            key = tuple(round(float(x), 7) for row in shape.matrix for x in row)
            key += tuple(round(float(x), 7) for point in shape.local_bounds for x in point)
            candidates[key].append(shape)
        groups = []
        for shapes in candidates.values():
            if len(shapes) < 2:
                continue
            fingerprints = defaultdict(list)
            for shape in shapes:
                payload = ([[round(float(x), 7) for x in v] for v in shape.local_vertices], shape.triangles)
                fingerprints[hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()].append(shape)
            for exact in fingerprints.values():
                if len(exact) < 2:
                    continue
                documented = all(s.obj.get('allow_stacked_overlap') is True and str(s.obj.get('duplicate_reason', '')).strip() for s in exact)
                entry = {'objects': [s.name for s in exact], 'allowed': documented,
                         'reasons': [s.obj.get('duplicate_reason') for s in exact]}
                groups.append(entry)
                if not documented:
                    self.fail('exact_duplicate_geometry', 'Coincident transform, bounds and evaluated topology without documented stacked-part exceptions.', objects=entry['objects'])
        self.report['duplicate_groups'] = groups
        self.check('exact_duplicate_geometry', start, comparison='world matrix + evaluated local bounds + vertices/topology, rounded to 1e-7 m')

    def cameras(self):
        start = len(self.report['errors'])
        cameras = [o for o in self.scene.objects if o.type == 'CAMERA']
        names = {o.name for o in cameras}
        slice_names = {'S01_style', 'S02_material'}
        if not slice_names.issubset(names):
            self.fail('missing_slice_cameras', 'Both fixed slice cameras are required.', missing=sorted(slice_names - names))
        full = [o for o in cameras if o.name not in slice_names]
        if self.scene.get('stage') == 'full' and len(full) != 10:
            self.fail('full_camera_count', 'Full stage needs exactly ten review cameras in addition to its two slice cameras.', actual_full_cameras=len(full))
        for obj in cameras:
            if not finite((obj.data.lens, obj.data.clip_start, obj.data.clip_end)) or obj.data.lens <= 0 or not (0 < obj.data.clip_start < obj.data.clip_end):
                self.fail('invalid_camera', 'Camera lens/clipping values are invalid.', camera=obj.name)
        if self.scene.camera not in cameras:
            self.fail('missing_active_camera', 'Active scene camera must belong to this scene.')
        self.report['cameras'] = [{'name': o.name, 'location_world': vec(o.matrix_world.translation), 'lens_mm': o.data.lens} for o in cameras]
        self.check('fixed_camera_inventory', start, total=len(cameras), full_cameras=len(full))

    def collisions(self, prisms, shapes):
        hits = []
        for index, prism in enumerate(prisms):
            for shape in shapes:
                collision = prism.collision(shape)
                if collision:
                    hits.append({'segment': index, **collision})
        return hits

    def floor_samples(self, path, floor):
        samples, failures = [], []
        architecture = [s for s in self.shapes if s.architectural]
        for a, b in zip(path, path[1:]):
            steps = max(1, math.ceil(math.dist(a, b) / .5))
            for i in range(steps + 1):
                t = i / steps
                point = Vector((a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t, floor + .1))
                hit = nearest_ray(architecture, point, Vector((0, 0, -1)), .2)
                row = {'xy': vec(point)[:2], 'surface_z': float(hit['point'].z) if hit else None, 'object': hit['shape'].name if hit else None}
                samples.append(row)
                if hit is None or abs(hit['point'].z - floor) > FLOOR_CONTACT_SKIN_M + EPS:
                    failures.append(row)
        return {'sample_spacing_max_m': .5, 'samples': samples, 'failed_samples': failures}

    def clearances(self):
        start = len(self.report['errors'])
        path = Path(self.args.interface)
        if not path.is_file():
            self.fail('missing_interface', 'Dimensional contract interface.json is missing.', path=str(path))
            self.check('clearance_contract', start)
            return
        contract = json.loads(path.read_text(encoding='utf-8-sig'))
        self.report['clearance']['contract_file'] = str(path.resolve())
        self.report['clearance']['contract_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if self.scene.get('stage') != 'full':
            self.report['checks'].append({'name': 'full_interior_portal_and_route_clearance', 'status': 'not_applicable', 'reason': 'Slice does not contain the full interior or all route obstacles.'})
            self.report['unverified'].append('Full interior, complete routes, all portals and ten full review cameras are outside a slice validation.')
            return
        if contract.get('units') != 'metres':
            self.fail('contract_units', 'Interface contract units must be metres.')
        interior = contract['interior']
        floor = float(interior['floor_z'])
        solids = [s for s in self.shapes if s.solid]
        inferred_architecture = []
        for shape in self.shapes:
            if shape.solid or not shape.architectural or not shape.bounds:
                continue
            dimensions = [shape.local_bounds[1][i] - shape.local_bounds[0][i] for i in range(3)]
            if min(dimensions) >= .05 - EPS and math.prod(dimensions) >= .015 and shape.bounds[1][2] > floor + FLOOR_CONTACT_SKIN_M:
                # A missing collision label must not erase a substantial ceiling,
                # wall or curb from the dimensional test. Include it conservatively
                # and disclose the inference instead of silently certifying space.
                inferred_architecture.append(shape.name)
                solids.append(shape)
        if inferred_architecture:
            self.report['warnings'].append({'code': 'unlabelled_substantial_architecture',
                'message': 'Substantial architectural geometry was conservatively included despite its false/missing circulation_solid label.',
                'objects': inferred_architecture})
        posed, pose_changes = [], []
        for shape in solids:
            try:
                delta, source = open_delta(shape.obj)
                if delta is not None:
                    posed.append(Shape(shape.obj, self.depsgraph, delta=delta))
                    pose_changes.append({'object': shape.name, 'metadata_owner': source, 'delta_world_matrix': [vec(row) for row in delta]})
                else:
                    posed.append(shape)
            except Exception as exc:
                self.fail('invalid_open_pose', str(exc), object=shape.name)
                posed.append(shape)
        self.report['clearance'].update({'obstacle_objects': [s.name for s in solids],
            'obstacle_selection': 'Author-labelled circulation_solid objects plus conservatively included substantial architectural geometry. Decorative non-solids are not runtime collision meshes.',
            'inferred_architectural_obstacles': inferred_architecture,
            'architecture_inference_rule': 'Architectural geometry above the 20mm floor skin with local bounding-box minimum thickness >=50mm and volume >=0.015 cubic metres.',
            'broad_phase': 'evaluated world bounding boxes',
            'narrow_phase': 'triangle vs oriented box separating-axis test; closed-mesh containment parity',
            'declared_open_pose_changes': pose_changes})
        self.report['unverified'].append('circulation_solid labels select bulky static obstacles; completeness of game collision assignments is unverified.')
        routes = contract.get('reserved_routes', [])
        if not routes:
            self.fail('missing_routes', 'Full validation requires declarative route centrelines.')
        route_results = []
        for route in routes:
            points = route.get('centreline_xy', [])
            width = next((route[k] for k in ('nominal_clear_width_m', 'swept_width_allowance_m', 'limiting_door_clear_width_m') if k in route), None)
            height = route.get('headroom_min_m')
            if len(points) < 2 or width is None or height is None:
                self.fail('invalid_route', 'Route requires centreline, width and height.', route=route.get('id'))
                continue
            prisms = [Prism(a, b, float(width), float(height), floor) for a, b in zip(points, points[1:])]
            # Segment rectangles are joined with width-square boxes, so changing
            # direction does not leave untested gaps between rectangles.
            radius = float(width) * .5
            prisms += [Prism((p[0], p[1] - radius), (p[0], p[1] + radius), float(width), float(height), floor) for p in points[1:-1]]
            actual = self.collisions(prisms, solids)
            opened = self.collisions(prisms, posed)
            ground = self.floor_samples(points, floor)
            row = {'id': route['id'], 'required_width_m': width, 'required_height_m': height,
                   'contract_route_state': route.get('route_state_for_clearance_check'),
                   'tested_prism_count': len(prisms), 'saved_pose_collisions': actual,
                   'declared_open_pose_collisions': opened, 'floor_support': ground,
                   'status': 'fail' if opened or ground['failed_samples'] else 'pass',
                   'interpretation': 'Static straight-segment and junction clearance; declared open poses are applied in memory only.'}
            if opened:
                self.fail('route_obstructed', 'Actual evaluated obstacles intersect the declared route even with authored open poses.', route=route['id'], objects=sorted({h['object'] for h in opened}))
            if ground['failed_samples']:
                self.fail('route_floor', 'Route floor is missing or outside the sill-height allowance at sampled points.', route=route['id'], samples=ground['failed_samples'])
            if actual and not opened:
                row['saved_pose_status'] = 'blocked_by_authored_openable_geometry'
            route_results.append(row)
        self.report['clearance']['routes'] = route_results
        portals = list(contract.get('portals', []))
        scanner = contract.get('equipment', {}).get('human_scanner')
        if scanner:
            portals.append({'id': 'human_scanner', 'threshold': scanner['centre'], 'width_axis': '+X',
                            'clear_width_m': scanner['clear_width_m'], 'clear_height_m': scanner['clear_height_m'], 'wall_depth_m': .9})
        portal_results = []
        required = {'facility_entry', 'staff_front', 'staff_rear', 'cart_gate', 'human_scanner'}
        if required - {p['id'] for p in portals}:
            self.fail('missing_portal_contract', 'Required aperture is absent from dimensional contract.', missing=sorted(required - {p['id'] for p in portals}))
        for portal in portals:
            if portal['id'] == 'sealed_external_access':
                portal_results.append({'id': portal['id'], 'status': 'unverified', 'reason': 'Authored sealed boundary; no open geometric proof requested for external access.'})
                continue
            centre = Vector(portal['threshold'])
            width, height = float(portal['clear_width_m']), float(portal['clear_height_m'])
            width_axis = Vector((0, 1, 0)) if str(portal.get('width_axis', '+X')).endswith('Y') else Vector((1, 0, 0))
            along = Vector((-width_axis.y, width_axis.x, 0))
            depth = float(portal.get('aperture_depth_m', portal.get('wall_depth_m', portal.get('wall_thickness_m', .28 if portal['id'] == 'facility_entry' else .16))))
            depth = max(.16, depth)
            prism = Prism(centre - along * depth * .5, centre + along * depth * .5, width, height, centre.z)
            actual, opened = self.collisions([prism], solids), self.collisions([prism], posed)
            samples = []
            for z in (.15, height * .5, height - .03):
                for longitudinal in (-depth * .4, 0, depth * .4):
                    origin = centre + along * longitudinal + Vector((0, 0, z))
                    left = nearest_ray(posed, origin, -width_axis, width * 2)
                    right = nearest_ray(posed, origin, width_axis, width * 2)
                    samples.append({'sample_world': vec(origin), 'left_object': left['shape'].name if left else None,
                                    'right_object': right['shape'].name if right else None,
                                    'measured_width_m': left['distance'] + right['distance'] if left and right else None})
            row = {'id': portal['id'], 'status': 'fail' if opened else 'pass', 'required_width_m': width,
                   'required_height_m': height, 'tested_depth_m': depth,
                   'saved_pose_collisions': actual, 'declared_open_pose_collisions': opened,
                   'transverse_ray_measurements': samples}
            finite_widths = [s['measured_width_m'] for s in samples if s['measured_width_m'] is not None]
            row['minimum_sampled_width_m'] = min(finite_widths) if finite_widths else None
            if opened:
                self.fail('portal_obstructed', 'Evaluated geometry intrudes into required aperture in its declared open pose.', portal=portal['id'], objects=sorted({h['object'] for h in opened}))
            if actual and not opened:
                row['saved_pose_status'] = 'blocked_by_authored_openable_geometry'
            portal_results.append(row)
        self.report['clearance']['portals'] = portal_results
        self.interior_faces(interior)
        self.check('full_interior_portal_and_route_clearance', start, routes=len(route_results), portals=len(portal_results))

    def interior_faces(self, interior):
        xmin, ymin, xmax, ymax = map(float, interior['bounds_xy'])
        walls = [s for s in self.shapes if s.architectural and s.solid]
        samples = []
        for axis, lo, hi, other_lo, other_hi in ((0, xmin, xmax, ymin, ymax), (1, ymin, ymax, xmin, xmax)):
            # The middle of either Y boundary is an authored entry/arrival cut.
            # Sample four side piers there, not the centre of either opening.
            fractions = (.09, .5, .91) if axis == 0 else (.09, .24, .76, .91)
            for fraction in fractions:
                other = other_lo + (other_hi - other_lo) * fraction
                pair = []
                for face, sign in ((lo, -1), (hi, 1)):
                    point = Vector((0, 0, 1.5))
                    point[axis], point[1 - axis] = face - sign * .1, other
                    direction = Vector((0, 0, 0))
                    direction[axis] = sign
                    hit = nearest_ray(walls, point, direction, .65)
                    measured = float(hit['point'][axis]) if hit else None
                    row = {'axis': 'XY'[axis], 'expected_face': face, 'sample_other_coordinate': other,
                           'measured_face': measured, 'object': hit['shape'].name if hit else None}
                    samples.append(row)
                    pair.append(measured)
                    if hit is None or abs(measured - face) > .005 + EPS:
                        self.fail('interior_face_mismatch', 'Perimeter face is missing or differs from declared interior bounds at a non-portal sample.', **row)
                if all(v is not None for v in pair):
                    samples[-1]['measured_opposite_face_span_m'] = pair[1] - pair[0]
        self.report['clearance']['interior_face_measurements'] = samples

    def run(self):
        self.inventory()
        self.resources()
        self.support()
        self.duplicates()
        self.cameras()
        self.clearances()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--interface', default=str(ROOT / 'interface.json'))
    parser.add_argument('--expected-stage', choices=('slice', 'full'))
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    validator = Validator(args)
    try:
        validator.run()
    except Exception as exc:
        validator.fail('validator_internal_error', str(exc), traceback=traceback.format_exc())
    report = validator.report
    report['passed'] = not report['errors']
    report['summary'] = {'failures': len(report['errors']), 'warnings': len(report['warnings']),
                         'unverified_checks': len(report['unverified']),
                         'passed_checks': sum(c['status'] == 'pass' for c in report['checks']),
                         'failed_checks': sum(c['status'] == 'fail' for c in report['checks'])}
    destination = Path(args.output).resolve()
    if destination.suffix.lower() == '.blend' or destination == Path(bpy.data.filepath).resolve():
        raise RuntimeError('Report output must not overwrite a .blend file')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(json_safe(report), indent=2, allow_nan=False), encoding='utf-8')
    print('VALIDATION_REPORT', destination)
    print('VALIDATION_SUMMARY', json.dumps(report['summary']))
    if report['errors']:
        for error in report['errors'][:25]:
            print('VALIDATION_FAILURE', json.dumps(error))
        raise RuntimeError(f"Compliance Dock validation failed with {len(report['errors'])} error(s); see {destination}")
    print('VALIDATION_PASS: static scene checks only; see explicit unverified checks in report.')


if __name__ == '__main__':
    main()
