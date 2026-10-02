"""Render the authored freight leaves in a diagnostic CLOSED pose, without saving.

blender -b --disable-autoexec --python-exit-code 1 --python render_closed_gate.py -- scene out
This shows leaf fabrication. It does not certify a runtime controller or sweep.
"""
from pathlib import Path
import sys, json, hashlib, datetime, os
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
args = sys.argv[sys.argv.index('--') + 1:]
src, out = Path(args[0]).resolve(), Path(args[1]).resolve()
before = hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src), load_ui=False)
pose = []
for name in ['FREIGHT_GATE_LEFT_CARRIAGE', 'FREIGHT_GATE_RIGHT_CARRIAGE']:
    ob = bpy.data.objects[name]
    assert ob['current_pose'] == 'OPEN'
    start = ob.matrix_world.copy()
    movement = -Vector(ob['closed_to_open_translation_m'])
    ob.matrix_world.translation += movement
    ob['current_pose'] = 'CLOSED_DIAGNOSTIC'
    pose.append({'object': name, 'translation_m': list(movement),
                 'open_matrix': [list(r) for r in start],
                 'diagnostic_matrix': [list(r) for r in ob.matrix_world]})
bpy.context.view_layer.update()
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SAMPLES', '32'))
sc.cycles.use_denoising = True; sc.cycles.seed = 7
sc.render.resolution_x, sc.render.resolution_y = map(int, os.environ.get('RES', '1280x853').split('x'))
sc.render.resolution_percentage = 100; sc.render.image_settings.file_format = 'PNG'
out.mkdir(parents=True, exist_ok=True)
views = []
for name in ['E03_FREIGHT_LEAF']:
    cam = bpy.data.objects[name]; png = out / (name + '.png')
    sc.camera = cam; sc.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    views.append({'name': name, 'image': png.name,
                  'matrix_world': [list(r) for r in cam.matrix_world],
                  'lens': cam.data.lens, 'sha256': hashlib.sha256(png.read_bytes()).hexdigest()})
assert hashlib.sha256(src.read_bytes()).hexdigest() == before, 'Source modified'
report = {'schema': 'fuel-closed-gate-diagnostic/1',
          'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scene': str(src.relative_to(ROOT)), 'scene_sha256': before,
          'blender': bpy.app.version_string, 'resolution': [sc.render.resolution_x, sc.render.resolution_y],
          'samples': sc.cycles.samples, 'seed': sc.cycles.seed, 'denoise': True,
          'look': sc.view_settings.look, 'exposure': sc.view_settings.exposure,
          'pose_changes': pose, 'cameras': views,
          'scope': 'Rigid authored-leaf diagnostic; native remains OPEN. Runtime controller and continuous sweep unverified.'}
(out / 'RENDER_MANIFEST.json').write_text(json.dumps(report, indent=2) + '\n')
print('CLOSED_GATE_DIAGNOSTIC', before, flush=True)
