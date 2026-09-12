"""Read-only CPU ray/projection inspection of the frozen style12 scene. No render/save."""
from pathlib import Path
import bpy, hashlib, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
SECTION = HERE.parents[1]
SAVED = SECTION / 'production/checkpoints/style12/Fuel_Corridor.blend'
EXPECTED = '58511635e4394538d6c1f8c25ddd2454574431ecbde5a1686757809f40ee339a'
assert hashlib.sha256(SAVED.read_bytes()).hexdigest() == EXPECTED
assert not bpy.data.filepath, 'Run in a fresh factory process'
bpy.ops.wm.open_mainfile(filepath=str(SAVED), load_ui=False)
scene = bpy.context.scene
camera = bpy.data.objects['D01_CARRIER_OPERATION']
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
width, height = 1440, 960
frame = camera.data.view_frame(scene=scene)
left, right = min(v.x for v in frame), max(v.x for v in frame)
bottom, top = min(v.y for v in frame), max(v.y for v in frame)
origin = camera.matrix_world.translation

def ray(px, py):
    local = Vector((left + (px + .5) / width * (right-left),
                    top - (py + .5) / height * (top-bottom), frame[0].z))
    direction = camera.matrix_world.to_quaternion() @ local.normalized()
    hit, location, normal, face, obj, matrix = scene.ray_cast(deps, origin, direction)
    return {'pixel_top_left': [px, py], 'hit': hit, 'object': obj.name if hit else None,
            'location': list(location) if hit else None,
            'normal': list(normal) if hit else None, 'face_index': face}

def inspect(obj):
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    projected = [world_to_camera_view(scene, camera, point) for point in points]
    info = {'name': obj.name, 'parent': obj.parent.name if obj.parent else None,
            'hide_render': obj.hide_render,
            'world_bounds': [[min(p[a] for p in points) for a in range(3)],
                             [max(p[a] for p in points) for a in range(3)]],
            'projected_pixel_bounds_top_left':
               [min(p.x*width for p in projected), min((1-p.y)*height for p in projected),
                max(p.x*width for p in projected), max((1-p.y)*height for p in projected)],
            'world_vertices': [list(p) for p in points],
            'polygon_normals_world': [list(evaluated.matrix_world.to_3x3().inverted().transposed() @ p.normal) for p in mesh.polygons]}
    evaluated.to_mesh_clear()
    return info

samples = [(1098, 889), (1100, 869), (1091, 911), (1094, 929),
           (870, 945), (873, 933), (860, 955), (1080, 884), (1125, 897)]
report = {'blend': str(SAVED), 'blend_sha256': EXPECTED, 'scene_revision': scene.get('revision'),
          'blender_version': bpy.app.version_string, 'camera': camera.name,
          'image_size': [width, height], 'saved_resolution': [scene.render.resolution_x, scene.render.resolution_y],
          'rays': [ray(x,y) for x,y in samples],
          'wheel_rubs': [inspect(o) for o in scene.objects if o.name.startswith('Parked_wheel_rub')],
          'no_render_or_save': True}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest() == EXPECTED
(HERE / 'astra-style12-floor-probe.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
