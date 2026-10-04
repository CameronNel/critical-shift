"""Render fixed supplemental process details without replacing the 21 required views."""
import bpy
import sys
import json
import hashlib
import time
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = root.parents[4]
args = sys.argv[sys.argv.index('--') + 1:]
revision = args[0]
if not re.fullmatch(r'R\d+[a-z]?(?:_cold)?', revision):
    raise ValueError('Detail revision must be a safe revision basename')
source = Path(bpy.data.filepath)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = sha(source)
scene = bpy.context.scene
required = ['D02_CaptureService', 'D03_ExtractionRun']
assert all(name in scene.objects and scene.objects[name].type == 'CAMERA' for name in required), 'Both fixed detail cameras are mandatory'
names = args[1:] or required
assert len(names) == len(set(names)) and set(names).issubset(required)
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
settings = dict(engine='CYCLES', device='CPU', samples=24, resolution=[960, 540],
                seed=73, denoising=True, max_bounces=8, use_light_tree=scene.cycles.use_light_tree, threads=8,
                exposure=scene.view_settings.exposure, look=scene.view_settings.look,
                world_strength=scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value)
out = root / 'production/details' / revision
out.mkdir(parents=True, exist_ok=True)
manifest_path = out / 'manifest.json'
views = {}
if manifest_path.exists():
    previous = json.loads(manifest_path.read_text())
    previous_settings = dict(previous['settings'])
    previous_settings.setdefault('use_light_tree', True)
    assert previous['source_sha256'] == before and previous_settings == settings
    assert previous['blender'] == bpy.app.version_string and previous['source_unchanged']
    for view in previous['views']:
        name = view['camera']
        assert name in required and name not in views
        camera = scene.objects[name]
        path = out / (name + '.png')
        if (path.is_file() and sha(path) == view['sha256']
                and view['matrix'] == [list(row) for row in camera.matrix_world]
                and view['lens'] == camera.data.lens):
            views[name] = dict(view, path=path.relative_to(repo).as_posix())

for name in names:
    scene.camera = scene.objects[name]
    scene.render.filepath = str(out / (name + '.png'))
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    assert sha(source) == before
    views[name] = dict(camera=name, matrix=[list(row) for row in scene.camera.matrix_world],
                       lens=scene.camera.data.lens,
                       path=Path(scene.render.filepath).relative_to(repo).as_posix(),
                       sha256=sha(Path(scene.render.filepath)), seconds=time.monotonic() - start)
    report = dict(source=source.resolve().relative_to(repo).as_posix(), source_sha256=before,
                  blender=bpy.app.version_string, settings=settings, required_cameras=required,
                  views=list(views.values()), complete=set(views) == set(required), source_unchanged=True,
                  scope='Supplemental process details; the mandatory 21 fixed views remain independent.')
    temporary = manifest_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(manifest_path)
    print('DETAIL_RENDERED', revision, name, flush=True)
