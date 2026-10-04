"""Fixed-camera CPU review; compatible existing views survive targeted rerenders."""
import bpy
import sys
import json
import hashlib
import time
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = root.parents[4]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['baseline']
required_names = ['C01_Entry', 'C02_Casks', 'C03_Reverse', 'C04_Route', 'C05_Transfer', 'C06_Dry', 'C07_Quarantine', 'C08_Extraction', 'C09_Inventory', 'C10_Workbench', 'W01_Personnel', 'W02_ReceivingReturn', 'W03_Dispatch', 'W04_CellService', 'W05_ReceivingExterior', 'W06_PersonnelExterior', 'W07_DispatchExterior', 'W08_BoothDoor', 'W09_DrySouth', 'W10_ResidueService', 'D01_SealRepair']
revision = args[0]
if not re.fullmatch(r'(?:baseline|R\d+[a-z]?(?:_cold)?)', revision):
    raise ValueError('Render revision must be a safe revision basename')
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
                resolution=[960, 540], seed=73, denoising=True, max_bounces=8, use_light_tree=scene.cycles.use_light_tree, threads=8, exposure=scene.view_settings.exposure, look=scene.view_settings.look, world_strength=scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value)
manifest_path = out / 'manifest.json'
views = {}
if manifest_path.exists():
    previous = json.loads(manifest_path.read_text())
    previous_settings = dict(previous['settings'])
    # Historical builders used the original module's enabled default.
    previous_settings.setdefault('use_light_tree', True)
    if (previous['source_sha256'] != before or previous_settings != settings
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
            views[name] = dict(view, path=image_path.relative_to(repo).as_posix())
manifest = dict(source=source.resolve().relative_to(repo).as_posix(), source_sha256=before,
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
    # Resume a full batch from hash/pose/settings-verified compatible records.
    # An explicit selection still requests a fresh targeted render.
    if not args[1:] and name in views:
        print('REUSED_VERIFIED', name, flush=True)
        continue
    scene.camera = scene.objects[name]
    scene.render.filepath = str(out / (name + '.png'))
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    views[name] = dict(camera=name, matrix=[list(row) for row in scene.camera.matrix_world],
                       lens=scene.camera.data.lens, path=Path(scene.render.filepath).relative_to(repo).as_posix(),
                       sha256=sha(Path(scene.render.filepath)), seconds=time.monotonic() - start)
    save_manifest()
    print('RENDERED', name, flush=True)

save_manifest()
