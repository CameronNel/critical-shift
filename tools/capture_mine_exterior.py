"""Five exterior captures of the canonical full map; never saves source assets."""
import bpy
import hashlib
import json
import math
import os
import sys
import time
import traceback
import subprocess
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
    s.eevee.taa_render_samples = 8
s.eevee.taa_samples = 8
s.eevee.use_shadow_jitter_viewport = False
s.eevee.shadow_resolution_scale = 0.5
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
    'render_resolution_setting': [1600,900], 'full_map_groups': preview_sources,
    'missing_images': missing_images, 'image_path_repairs': repaired_images,
    'source_assets_edited': False, 'visible_geometry_changed': False,
    'note': 'Direct rendered-viewport screenshots of the canonical full map. Existing materials, sun/world lighting and geometry retained. The 28m preview-light culling matches facility_material_preview.py. The renders folder holds lossless viewport crops, not offline renders. Source scene never saved.',
    'shots': []
}

# Unload only hidden authoring/solid-cache duplicates already represented by
# the complete material preview; do not remove any visible map geometry.
preview_object_names = {o.name for o in preview.all_objects}
unloaded = []
duplicate_collections = [
    '01_LINKED_ROOMS', '06_LINKED_EXTERIORS', 'CONNECTION_C01_RESCUE_COURTYARD',
    '09_FINISHED_HORIZONTAL_CONNECTIONS', '13_FINISHED_ACCESS_SCENERY',
    '15_FINISHED_NETWORK_SCENERY', '17_REACTOR_EXTERIOR_FINISH',
    '20_ROOF_SERVICE_GEOMETRY', '22_EXTERIOR_FINISH_GEOMETRY',
    '29_SPAWN_APPROVED_EXTERIOR', '30_RETAINED_INTERIOR_LIGHTING',
    '07_FAST_WALKTHROUGH_PROXIES', '10_NETWORK_VIEWPORT_CACHE',
    '14_ACCESS_FINISH_VIEWPORT_CACHE', '16_NETWORK_FINISH_VIEWPORT_CACHE',
    '18_REACTOR_FINISH_VIEWPORT_CACHE', '21_ROOF_SERVICE_VIEWPORT_CACHE',
    '23_EXTERIOR_FINISH_VIEWPORT_CACHE'
]
for name in duplicate_collections:
    collection = bpy.data.collections.get(name)
    if collection and collection.hide_render and collection.hide_viewport:
        bpy.data.collections.remove(collection)
        unloaded.append(name)
if hasattr(bpy.data, 'orphans_purge'):
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
assert preview_object_names == {o.name for o in preview.all_objects}
report['hidden_authoring_duplicates_unloaded_in_memory'] = unloaded
report['visible_full_map_preview_objects_preserved'] = len(preview_object_names)
state = {'index': 0, 'phase': 'view', 'maximized': False}
report['method'] = 'Blender rendered 3D viewport screenshot'
report['viewport_samples'] = 8
report['viewport_shadow_resolution_scale'] = 0.5
report['light_culling_m'] = 28

def write_report():
    (OUT / 'capture_manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

def area_context():
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return window, area, region

def advance():
    try:
        index = state['index']
        if index >= len(shots):
            report['source_sha256_after'] = digest(source)
            assert report['source_sha256_after'] == source_hash, 'Source scene changed!'
            report['completed'] = True
            write_report()
            print('CAPTURE_COMPLETE', json.dumps(report), flush=True)
            sys.stdout.flush()
            os._exit(0)
        slug, title, eye_local, target_local, lens = shots[index]
        window, area, region = area_context()
        if state['phase'] == 'view':
            area.type = 'VIEW_3D'
            if not state['maximized']:
                with bpy.context.temp_override(window=window, area=area, region=region):
                    bpy.ops.screen.screen_full_area(use_hide_panels=True)
                state['maximized'] = True
                window, area, region = area_context()
            space = area.spaces.active
            eye, target = world(eye_local), world(target_local)
            quat = (target - eye).to_track_quat('-Z', 'Y')
            space.lens = lens
            space.clip_start = 0.05
            space.clip_end = 1000
            space.show_gizmo = False
            space.overlay.show_overlays = False
            space.show_region_ui = False
            space.show_region_toolbar = False
            space.shading.type = 'RENDERED'
            for setting in ('use_scene_world_render', 'use_scene_lights_render'):
                if hasattr(space.shading, setting):
                    setattr(space.shading, setting, True)
            space.region_3d.view_perspective = 'PERSP'
            space.region_3d.view_rotation = quat
            space.region_3d.view_distance = 1
            space.region_3d.view_location = eye + quat @ Vector((0, 0, -1))
            # Preserve all map geometry. Use the repository's standard preview
            # radius for local artificial lights; sun/world illumination stays.
            lights = bpy.data.collections.get('28_MATERIAL_PREVIEW_LIGHTS')
            if lights:
                for obj in lights.all_objects:
                    if obj.type == 'LIGHT' and obj.data.type != 'SUN':
                        obj.hide_set((obj.matrix_world.translation - eye).length > 28)
            bpy.context.view_layer.update()
            report['shots'].append({'name': title, 'slug': slug, 'camera_world': list(eye), 'target_world': list(target), 'lens_mm': lens})
            state['phase'] = 'settle'
            state['began'] = time.time()
            write_report()
            area.tag_redraw()
            print('VIEWPORT_SHOT_BEGIN', slug, tuple(eye), tuple(target), flush=True)
            return 30.0 if index == 0 else 12.0
        if state['phase'] == 'settle':
            # A second UI cycle allows deferred shader compilation and TAA.
            area.tag_redraw()
            state['phase'] = 'capture'
            return 20.0 if index == 0 else 8.0
        path = OUT / 'screenshots' / (slug + '.png')
        with bpy.context.temp_override(window=window, area=area, region=region):
            bpy.ops.screen.screenshot(filepath=str(path))
        crop = OUT / 'renders' / (slug + '.png')
        left, top = region.x, window.height - (region.y + region.height)
        box = [left, top, left + region.width, top + region.height]
        code = 'from PIL import Image; import sys,json; im=Image.open(sys.argv[1]); im.crop(tuple(json.loads(sys.argv[3]))).save(sys.argv[2])'
        subprocess.run(['/usr/bin/python3', '-c', code, str(path), str(crop), json.dumps(box)], check=True)
        report['shots'][-1].update({'screenshot': str(path.relative_to(OUT)), 'render': str(crop.relative_to(OUT)), 'viewport_crop_box': box, 'capture_seconds': round(time.time()-state['began'], 2)})
        write_report()
        print('VIEWPORT_SCREENSHOT_SAVED', path.name, flush=True)
        state['index'] += 1
        state['phase'] = 'view'
        return 0.5
    except Exception:
        report['error'] = traceback.format_exc()
        write_report()
        print(report['error'], flush=True)
        sys.stdout.flush()
        os._exit(1)

write_report()
bpy.app.timers.register(advance, first_interval=2.0)
