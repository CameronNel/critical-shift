"""Create an editable baseline copy with a read-only linked map scene.

Run with Blender 5.2 LTS --background --factory-startup --disable-autoexec
--python prepare_revamp.py. Existing output is never overwritten.
"""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
ASSEMBLY = ROOT.parents[1]
OUTPUT = ROOT / 'module_overhaul_R1.blend'
MAP = ASSEMBLY / 'blender/facility_environment.blend'
PRODUCTION = ROOT / 'revamp-review'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if OUTPUT.exists():
    raise RuntimeError('Working checkpoint already exists; refusing to overwrite edits.')
PRODUCTION.mkdir(exist_ok=True)
protected = {str(p.relative_to(ASSEMBLY)): sha(p) for p in (MAP, ROOT / 'module.blend')}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'module.blend'), load_ui=False)
room = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
records = []
triangles = 0
for obj in room.objects:
    record = {'name': obj.name, 'type': obj.type,
              'matrix_world': [list(row) for row in obj.matrix_world],
              'dimensions': list(obj.dimensions)}
    if obj.type == 'MESH':
        mesh = obj.evaluated_get(deps).to_mesh()
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        obj.evaluated_get(deps).to_mesh_clear()
    records.append(record)
report = {'protected_sha256': protected, 'objects': records,
          'evaluated_triangles': triangles,
          'material_count': len(bpy.data.materials),
          'draw_calls': 'Engine measurement required; Blender object count is not draw calls.'}
(PRODUCTION / 'baseline.json').write_text(json.dumps(report, indent=2))
# Save fixed-camera baseline evidence without changing the inherited presentation.
old = (room.render.resolution_x, room.render.resolution_y, room.render.resolution_percentage,
       room.render.engine, room.camera)
room.render.engine = 'BLENDER_WORKBENCH'
room.display.shading.light = 'STUDIO'
room.display.shading.color_type = 'MATERIAL'
room.render.resolution_x = 960
room.render.resolution_y = 540
room.render.resolution_percentage = 100
for name in ('CAM_ENTRY', 'CAM_HERO', 'CAM_REVERSE'):
    room.camera = bpy.data.objects[name]
    room.render.filepath = str(PRODUCTION / (name + '.png'))
    bpy.ops.render.render(write_still=True)
room.render.resolution_x, room.render.resolution_y, room.render.resolution_percentage, room.render.engine, room.camera = old
room.name = 'REANIMATION_EDIT_LOCAL'
room['revamp_status'] = 'Untouched baseline prepared for owner-directed revamp'
room['map_placement_m'] = [-18.0, 31.0, 0.0]
room['map_context'] = 'Switch scenes to the linked facility scene for read-only reference. The map still uses module.blend.'
with bpy.data.libraries.load(str(MAP), link=True) as (source, target):
    target.scenes = list(source.scenes)
linked_names = [scene.name for scene in target.scenes]
for lib in bpy.data.libraries:
    if lib.parent is None:
        lib.filepath = bpy.path.relpath(bpy.path.abspath(lib.filepath), start=str(ROOT))
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), compress=True)
assert all(sha(ASSEMBLY / p) == expected for p, expected in protected.items())
report['linked_map_scenes'] = linked_names
report['working_checkpoint'] = OUTPUT.name
(PRODUCTION / 'baseline.json').write_text(json.dumps(report, indent=2))
print('REVAMP_READY', OUTPUT, linked_names, len(records), triangles, flush=True)
