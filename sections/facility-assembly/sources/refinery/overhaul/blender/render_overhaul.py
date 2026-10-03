"""Fixed-camera CPU review; compatible existing views survive targeted rerenders."""
import bpy
import sys
import json
import hashlib
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['slice']
required_names = ['CAM_ENTRY', 'CAM_MAIN_ROUTE', 'CAM_PROCESS', 'CAM_REVERSE',
                  'CAM_PINCH', 'CAM_MATERIAL', 'CAM_ASSEMBLY', 'CAM_DISPATCH',
                  'CAM_MINE_TO_CRUSHER', 'CAM_WORK_NOOK', 'CAM_HERO_DETAIL']
revision = args[0]
names = args[1:] or required_names
assert len(set(names)) == len(names) and set(names).issubset(required_names), names
out = root / 'production/renders' / revision
out.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
source = Path(bpy.data.filepath)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = sha(source)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.seed = 73
scene.cycles.max_bounces = 8
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
settings = dict(engine='CYCLES', device='CPU', samples=24,
                resolution=[960, 540], seed=73, world_strength=0)
manifest_path = out / 'manifest.json'
views = {}
if manifest_path.exists():
    previous = json.loads(manifest_path.read_text())
    if (previous['source_sha256'] != before or previous['settings'] != settings
            or previous['blender'] != bpy.app.version_string
            or not previous.get('source_unchanged')):
        raise RuntimeError('Existing batch source or settings differ; choose a new revision directory.')
    for view in previous['views']:
        name = view['camera']
        assert name in required_names and name not in views, name
        camera = scene.objects[name]
        image_path = out / (name + '.png')
        if (image_path.is_file() and sha(image_path) == view['sha256']
                and view['matrix'] == [list(row) for row in camera.matrix_world]
                and view['lens'] == camera.data.lens):
            views[name] = dict(view, path=str(image_path))
manifest = dict(source=str(source), source_sha256=before,
                blender=bpy.app.version_string, settings=settings,
                required_cameras=required_names, views=[], complete=False)

def save_manifest():
    manifest['views'] = list(views.values())
    manifest['source_unchanged'] = sha(source) == before
    assert manifest['source_unchanged']
    manifest['complete'] = set(required_names).issubset(views)
    temporary = manifest_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(manifest, indent=2))
    temporary.replace(manifest_path)

for name in names:
    scene.camera = scene.objects[name]
    scene.render.filepath = str(out / (name + '.png'))
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    views[name] = dict(camera=name, matrix=[list(row) for row in scene.camera.matrix_world],
                       lens=scene.camera.data.lens, path=scene.render.filepath,
                       sha256=sha(Path(scene.render.filepath)), seconds=time.monotonic() - start)
    save_manifest()
    print('RENDERED', name, flush=True)
