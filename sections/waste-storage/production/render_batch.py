"""Render saved Waste Storage cameras. Invoke ONLY through the shared GPU gate.

No source mutation, no camera repositioning, no live Blender dependency.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import bpy


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


args_parser = argparse.ArgumentParser()
args_parser.add_argument('--output', required=True)
args_parser.add_argument('--cameras', default='all')
args_parser.add_argument('--width', type=int, default=1280)
args_parser.add_argument('--height', type=int, default=800)
args_parser.add_argument('--samples', type=int, default=64)
args_parser.add_argument('--revision', required=True)
args_parser.add_argument('--cpu', action='store_true')
args = args_parser.parse_args(sys.argv[sys.argv.index('--') + 1:])

scene = bpy.context.scene
if not bpy.data.filepath:
    raise RuntimeError('Open a saved authoritative section file before rendering')
source = Path(bpy.data.filepath).resolve()
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
all_cameras = sorted(obj.name for obj in scene.objects if obj.type == 'CAMERA' and obj.name.startswith('C'))
chosen = all_cameras if args.cameras == 'all' else args.cameras.split(',')
if args.cameras == 'all' and len(chosen) != 10:
    raise RuntimeError(f'Expected exactly 10 fixed cameras, got {chosen}')
for name in chosen:
    if name not in all_cameras:
        raise RuntimeError(f'Unknown fixed camera {name}')

scene.render.engine = 'CYCLES'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.seed = 4217
scene.cycles.use_animated_seed = False
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 6
scene.cycles.transparent_max_bounces = 8
scene.render.resolution_x = args.width
scene.render.resolution_y = args.height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = False
scene.render.use_file_extension = True
device_names = []
if not args.cpu:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    available_types = [item.identifier for item in prefs.bl_rna.properties['compute_device_type'].enum_items]
    # Dynamic backend properties can omit HIP from the static RNA enum list.
    for backend in ('HIP', 'OPTIX', 'CUDA', 'ONEAPI'):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            devices = [dev for dev in prefs.devices if dev.type != 'CPU']
            if not devices:
                continue
            for dev in prefs.devices:
                dev.use = dev.type != 'CPU'
            device_names = [f'{dev.type}: {dev.name}' for dev in devices]
            scene.cycles.device = 'GPU'
            break
        except (TypeError, RuntimeError):
            continue
if not device_names:
    scene.cycles.device = 'CPU'
    device_names = ['CPU']
print('WASTE_RENDER_DEVICES ' + json.dumps(device_names), flush=True)

manifest = {
    'revision': args.revision,
    'blender': bpy.app.version_string,
    'source_file': source.name,
    'source_sha256': sha256(source),
    'render_script_sha256': sha256(__file__),
    'engine': scene.render.engine,
    'devices': device_names,
    'settings': {'width': args.width, 'height': args.height, 'samples': args.samples,
                 'seed': scene.cycles.seed, 'denoising': True,
                 'view_transform': scene.view_settings.view_transform,
                 'look': scene.view_settings.look, 'exposure': scene.view_settings.exposure,
                 'gamma': scene.view_settings.gamma, 'max_bounces': 8},
    'cameras': [],
    'completed': False
}
manifest_path = out / 'manifest.json'
for name in chosen:
    camera = scene.objects[name]
    scene.camera = camera
    scene.render.filepath = str(out / (name + '.png'))
    start = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    entry = {'name': name, 'image': name + '.png', 'location': list(camera.location),
             'rotation_euler': list(camera.rotation_euler), 'lens_mm': camera.data.lens,
             'sensor_width_mm': camera.data.sensor_width, 'clip_start': camera.data.clip_start,
             'clip_end': camera.data.clip_end, 'matrix_world': [list(row) for row in camera.matrix_world],
             'sha256': sha256(scene.render.filepath),
             'seconds': round(time.perf_counter() - start, 3)}
    manifest['cameras'].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('WASTE_RENDER_COMPLETE ' + json.dumps(entry), flush=True)
manifest['completed'] = True
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('WASTE_BATCH_COMPLETE ' + str(manifest_path), flush=True)
