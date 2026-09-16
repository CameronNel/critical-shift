"""Five exterior captures of the canonical full map; never saves source assets."""
import bpy
import hashlib
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(os.environ.get('GITHUB_WORKSPACE', Path.cwd())).resolve()
OUT = ROOT / 'capture-output'
OUT.mkdir(exist_ok=True)
for directory in ('renders', 'screenshots'):
    (OUT / directory).mkdir(exist_ok=True)
manifest = json.loads((ROOT / 'MAP.json').read_text(encoding='utf-8'))
source = ROOT / manifest['inspection_scene']

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

with source.open('rb') as stream:
    if stream.read(64).startswith(b'version https://git-lfs'):
        raise RuntimeError('The full-map scene is still an unhydrated LFS pointer.')
source_hash = digest(source)
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.use_raytracing = False
if hasattr(s.eevee, 'taa_render_samples'):
    s.eevee.taa_render_samples = 32
s.render.resolution_x = 1600
s.render.resolution_y = 900
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.film_transparent = False
s.render.use_file_extension = True
try:
    bpy.context.preferences.view.render_display_type = 'NONE'
except (AttributeError, TypeError):
    pass
preview = bpy.data.collections.get('27_MATERIAL_PREVIEW')
if preview is None:
    raise RuntimeError('Canonical material-preview collection not found.')
preview.hide_viewport = False
preview.hide_render = False
for obj in preview.all_objects:
    obj.hide_set(False)
    obj.hide_render = False
# No geometry isolation: every full-map preview group remains present.
preview_sources = sorted({str(o.get('preview_source', '')) for o in preview.all_objects})
if not any('mine' in value.lower() for value in preview_sources):
    raise RuntimeError('Mine is absent from the full-map preview.')
missing_libraries = []
for lib in bpy.data.libraries:
    resolved = Path(bpy.path.abspath(lib.filepath))
    if not resolved.exists():
        missing_libraries.append({'library': lib.filepath, 'resolved': str(resolved)})
if missing_libraries:
    (OUT / 'missing_libraries.json').write_text(json.dumps(missing_libraries, indent=2))
    raise RuntimeError('Linked full-map libraries missing; refusing incomplete captures.')

# Portable-path recovery is allowed only for an existing exact/suffix-matched image.
image_paths = None
missing_images = []
repaired_images = []
for image in bpy.data.images:
    if image.source != 'FILE' or image.packed_file or not image.filepath:
        continue
    resolved = Path(bpy.path.abspath(image.filepath, library=image.library))
    if resolved.exists():
        continue
    if image_paths is None:
        image_paths = {}
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tif', '.tiff', '.webp'}:
                image_paths.setdefault(path.name.lower(), []).append(path)
    normalized = image.filepath.replace('\\', '/')
    candidates = image_paths.get(normalized.rsplit('/', 1)[-1].lower(), [])
    if len(candidates) == 1:
        candidate = candidates[0]
        with candidate.open('rb') as stream:
            if stream.read(64).startswith(b'version https://git-lfs'):
                missing_images.append({'name': image.name, 'path': image.filepath, 'reason': 'LFS pointer'})
                continue
        try:
            old = image.filepath
            image.filepath = str(candidate)
            image.reload()
            repaired_images.append({'image': image.name, 'old': old, 'resolved': str(candidate.relative_to(ROOT))})
            continue
        except Exception as error:
            print('IMAGE_PATH_REPAIR_FAILED', image.name, repr(error), flush=True)
    missing_images.append({'name': image.name, 'path': image.filepath, 'reason': 'not uniquely resolvable'})
if missing_images:
    (OUT / 'missing_images.json').write_text(json.dumps(missing_images, indent=2))
    print('WARNING_MISSING_IMAGES', json.dumps(missing_images), flush=True)

layout = json.loads((ROOT / manifest['layout']).read_text(encoding='utf-8-sig'))
placement = layout['placements']['mine']
angle = math.radians(placement['rotation_z_degrees'])
rotation = Matrix.Rotation(angle, 4, 'Z')
translation = Vector(placement['translation'])
scale = Vector(placement['scale'])
def world(point):
    local = Vector(tuple(point[i] * scale[i] for i in range(3)))
    return rotation @ local + translation

# First four are the repository's exterior_mine.py shots in world placement.
shots = [
    ('01_front_approach', 'Front approach', (0,-45,7), (0,-17,3), 35),
    ('02_oblique_exterior', 'Oblique exterior', (-23,-38,14), (0,-13,3), 35),
    ('03_reverse_exterior', 'Reverse exterior', (25,-5,13), (0,-18,3), 35),
    ('04_handoff_detail', 'Mine handoff facade detail', (9,-25,1.8), (6.8,-20.4,1.65), 45),
    ('05_elevated_context', 'Elevated mine and facility context', (45,-55,46), (0,2,1), 32),
]
camera_data = bpy.data.cameras.new('CAPTURE_ONLY_mine_exterior')
camera = bpy.data.objects.new('CAPTURE_ONLY_mine_exterior', camera_data)
s.collection.objects.link(camera)
s.camera = camera
camera_data.clip_start = 0.05
camera_data.clip_end = 1000
camera_data.dof.use_dof = False
report = {
    'source_scene': manifest['inspection_scene'], 'source_sha256_before': source_hash,
    'source_commit': os.environ.get('SOURCE_COMMIT'), 'capture_commit': os.environ.get('GITHUB_SHA'),
    'blender_version': bpy.app.version_string, 'engine': s.render.engine, 'raytracing': False,
    'resolution': [1600,900], 'full_map_groups': preview_sources,
    'missing_images': missing_images, 'image_path_repairs': repaired_images,
    'geometry_materials_and_lighting_edited': False,
    'note': 'Canonical full-map material preview. Render settings/camera only; source scene never saved. Screenshots show the Blender window displaying each rendered camera image.',
    'shots': []
}
state = {'index': 0, 'phase': 'render'}

def write_report():
    (OUT / 'capture_manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

def image_area():
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    return window, area

def advance():
    try:
        index = state['index']
        if index >= len(shots):
            report['source_sha256_after'] = digest(source)
            assert report['source_sha256_after'] == source_hash, 'Source scene changed!'
            report['completed'] = True
            write_report()
            print('CAPTURE_COMPLETE', json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None
        slug, title, eye_local, target_local, lens = shots[index]
        if state['phase'] == 'render':
            eye, target = world(eye_local), world(target_local)
            camera.location = eye
            camera.rotation_euler = (target - eye).to_track_quat('-Z', 'Y').to_euler()
            camera_data.lens = lens
            bpy.context.view_layer.update()
            path = OUT / 'renders' / (slug + '.png')
            s.render.filepath = str(path)
            print('CAPTURE_RENDER_BEGIN', slug, tuple(eye), tuple(target), flush=True)
            began = time.time()
            bpy.ops.render.render(write_still=True)
            report['shots'].append({'name': title, 'slug': slug, 'camera_world': list(eye), 'target_world': list(target), 'lens_mm': lens, 'render_seconds': round(time.time()-began, 2), 'render': str(path.relative_to(OUT))})
            window, area = image_area()
            area.type = 'IMAGE_EDITOR'
            area.spaces.active.image = bpy.data.images.load(str(path), check_existing=True)
            area.spaces.active.show_region_ui = False
            area.spaces.active.show_region_toolbar = False
            if index == 0:
                region = next(r for r in area.regions if r.type == 'WINDOW')
                with bpy.context.temp_override(window=window, area=area, region=region):
                    bpy.ops.screen.screen_full_area(use_hide_panels=True)
            state['phase'] = 'fit'
            write_report()
            return 1.5
        if state['phase'] == 'fit':
            window, area = image_area()
            region = next(r for r in area.regions if r.type == 'WINDOW')
            with bpy.context.temp_override(window=window, area=area, region=region):
                bpy.ops.image.view_all(fit_view=True)
            state['phase'] = 'screenshot'
            return 1.5
        path = OUT / 'screenshots' / (slug + '.png')
        bpy.ops.screen.screenshot(filepath=str(path))
        report['shots'][-1]['screenshot'] = str(path.relative_to(OUT))
        write_report()
        print('CAPTURE_SCREENSHOT_SAVED', path.name, flush=True)
        state['index'] += 1
        state['phase'] = 'render'
        return 0.5
    except Exception:
        report['error'] = traceback.format_exc()
        write_report()
        print(report['error'], flush=True)
        sys.stdout.flush()
        os._exit(1)

write_report()
bpy.app.timers.register(advance, first_interval=2.0)
