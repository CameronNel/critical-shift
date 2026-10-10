"""Render ten focused reactor review views without changing the source asset.

Blender 5.2.2 LTS: blender --background --disable-autoexec -noaudio SOURCE.blend
  --python-exit-code 1 --python render_detail_views.py -- --output OUTPUT
Add --preview for framing checks or --views 01 02 to select view numbers.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

VIEWS = [
    ('01_machinery_turbine_grid', 'Machinery · turbine and switchgear', (5.9,-7,2.5), (9.2,-2.4,1.5), 20),
    ('02_machinery_coolant_eccs', 'Machinery · coolant pump and emergency cooling', (6,-5.4,2.4), (0,-9.5,2.25), 18),
    ('03_floor_access_lane', 'Floor · access lane, tiles and safety markings', (-6.3,-3,1.4), (-7.8,-.4,.02), 28),
    ('04_floor_pool_circulation', 'Floor · pool circulation and service routes', (0,9.4,7.5), (.3,3.2,.1), 20),
    ('05_control_rods_upper', 'Control rods · bank housings and drives', (0,-7.5,11.5), (0,0,11.5), 28),
    ('06_control_rods_pool', 'Control rods · twin shafts and pool interfaces', (3.7,6.7,5.2), (0,0,3.9), 18),
    ('07_roof_crane', 'Roof · bridge crane and structural supports', (0,-7.5,15.6), (-3,4.6,15.8), 20),
    ('08_roof_girders_services', 'Roof · girders, cable trays and lighting', (6.5,1.4,15.3), (-3,6,16.8), 18),
    ('09_walls_north_fuel', 'Walls · north panels and fuel doorway', (-5.6,4.4,3.6), (0,10.4,4.3), 18),
    ('10_walls_west_access', 'Walls · west panels and main access', (-3.7,2.7,3.2), (-10.8,.8,4.4), 18),
]

INSPECTION_VIEWS = [
    ('11_pool_control_face','Inspection · SCRAM, acknowledge and bypass',(0,-7.2,2.0),(0,-3.75,1.15),32),
    ('12_ec_local_controls','Inspection · emergency cooling controls',(2.55,-6.9,1.6),(2.55,-8.43,.91),40),
    ('13_switchgear_face','Inspection · circuits and cabinet construction',(6.8,-1.2,1.45),(9.47,-1.2,1.15),24),
    ('14_turbine_base','Inspection · turbine frame and service guard',(7.2,-6.3,2.5),(9.95,-4.6,.65),24),
    ('15_roof_running_gear','Inspection · wheels, bearings and bridge',(-9.35,2.7,15.35),(-10,4.6,14.65),22),
    ('16_gantry_access','Inspection · fixed gantry ladder and gate',(4.8,3.0,15.3),(7.04,1.07,14.15),24),
    ('17_board_direct','Inspection · stability board and clear lettering',(8.2,-1.4,7.2),(10.30,0,7.07),24),
    ('18_north_signs','Inspection · fuel doorway and header',(-1,7.4,4.2),(0,10.4,5.66),20),
    ('19_bank_service_face','Inspection · bank identification and service access',(-1.4,-4.1,11.2),(-1.4,-1.22,11.1),28),
    ('20_bank_suspension','Inspection · fixed housing load path and cable terminations',(-4,-3.2,13.7),(-1.4,0,13.0),24),
    ('21_pool_depth','Inspection · water interface and lining depth marks',(0,-3.0,2.2),(0,3.3,-2.5),20),
    ('22_main_trolley','Inspection · travelling hoist drum, motor and running gear',(-6.35,3.1,16.0),(-6.35,4.8,15.84),28),
    ('23_gantry_ladder','Inspection · ladder feet and lower rungs',(5.25,1.05,1.1),(7.17,1.05,1.1),14),
    ('24_gantry_middle','Inspection · ladder middle rungs and fall-arrest guide',(4.5,1.05,7.5),(7.17,1.05,7.5),24),
    ('25_gantry_overview','Inspection · complete ladder route in context',(-4.5,3.1,7.4),(7.17,1.05,7.4),16),
    ('26_main_hook','Inspection · hook socket, block and forged throat',(-5.2,2.6,10.6),(-6.4,4.6,10.50),45),
    ('27_main_hoist_upper','Inspection · drum rope entry from service walkway',(-6.35,4.12,16.075),(-6.50,4.68,16.015),22),
    ('31_props_drum_group','Inspection · steel drum hoops, bungs and inventory',(4.9,-5.2,1.4),(6.7,-3.3,.65),35),
    ('32_cone_close','Inspection · weighted cone base and reflective seams',(3.8,-5.0,1.15),(5.07,-4.0,.35),40),
    ('33_floor_wet_drain','Inspection · water films, drainage and slab relief',(-6.3,-3,1.4),(-7.8,-.4,.02),40),
    ('34_floor_annulus','Inspection · annular drainage recess and coping bearing',(-4.6,-5.7,1.2),(-2.4,-3.8,-.15),28),
    ('35_vessel_instruments','Inspection · vessel EC1 instruments and service ports',(3.3,-8.0,2.1),(3.3,-9.2,2.1),50),
    ('36_floor_crack','Inspection · shallow shrinkage crack and branch',(-7.75,-.4,.85),(-7.30,.4,0),40),
    ('37_generator_plaque','Inspection · standby generator identification',(-8.55,-4.60,4.64),(-10.683,-4.60,4.64),35),
    ('38_reserve_plaque','Inspection · reserve power A identification',(-8.65,4.50,4.14),(-10.683,4.50,4.14),40),
    ('39_watch_instruction','Inspection · operating instruction',(4.30,8.75,5.041),(4.30,10.683,5.041),35),
    ('40_exit_north','Inspection · north exit sign',(-2.2,8.69,5.21),(-2.2,10.39,5.21),60),
    ('41_exit_west','Inspection · west exit sign',(-8.69,-2.2,5.21),(-10.39,-2.2,5.21),60),
    ('42_exit_diagonal','Inspection · diagonal exit sign',(8.53,-5.42,5.21),(9.66,-6.55,5.21),60),
    ('44_wall_clock','Inspection · wall clock face and mount',(4.2,-8.6,5.45),(4.2,-10.734,5.45),60),
    ('43_stool','Inspection · stool legs and foot ring',(8.2,4.2,1.15),(7,3.07,.32),40),
    ('29_roof_original_crane','Comparison · original low crane framing',(-8,-4.5,9.2),(0,4.6,14),18),
    ('30_roof_original_services','Comparison · original low services framing',(7,-7,10.5),(-3,6,14.2),22),
    ('28_main_rope_path','Inspection · complete hoist rope load path',(-5.9,3.3,13.15),(-6.5,4.6,13.15),27),
    ('45_roof_utilities','Inspection · ceiling utility types and diameter hierarchy',(.3,7.7,16.0),(1.25,9.6,16.75),20),
    ('46_perimeter_cable_tray','Inspection · utility tray, cables and conduit entries',(4,8.4,12.2),(4,9.85,11.65),28),
    ('48_rod_guide_housing_entry','Inspection · bored housings and fixed guide seats',(0,-4.0,9.05),(0,0,9.70),28),
    ('47_stability_floor_approach','Inspection · stability board from floor approach',(5,3,1.7),(10.3,0,7.07),24),
]

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--preview', action='store_true')
parser.add_argument('--views', nargs='*', choices=[f'{i:02}' for i in range(1, 49)])
parser.add_argument('--inspection', action='store_true', help='Additional functional faces; output separately from the ten fixed views')
parser.add_argument('--save-review-scene', action='store_true')
parser.add_argument('--state', type=float, default=1.0, help='Stability input; separate output directory per state')
parser.add_argument('--samples', type=int, default=96, help='Diagnostic override; final quality remains 96')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
args.output.mkdir(parents=True, exist_ok=True)
source = Path(bpy.data.filepath)
scene = bpy.context.scene
scene.frame_set(1)
bpy.data.objects['REACTOR_STATE']['stability'] = args.state
bpy.data.objects['REACTOR_STATE'].update_tag()
bpy.context.view_layer.update()
assert not bpy.data.libraries, 'Unexpected external scene library dependency'
assert all(i.packed_file or i.source != 'FILE' for i in bpy.data.images), 'Missing unpacked image dependency'

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.render.threads_mode = 'FIXED'
scene.render.threads = len(os.sched_getaffinity(0))
scene.cycles.samples = 16 if args.preview else args.samples
scene.cycles.use_adaptive_sampling = not args.preview
scene.cycles.adaptive_threshold = .015
scene.cycles.adaptive_min_samples = min(32, scene.cycles.samples)
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
scene.cycles.denoising_prefilter = 'ACCURATE'
scene.cycles.max_bounces = 12
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 8
scene.cycles.volume_bounces = 1
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.cycles.use_guiding = not args.preview
scene.cycles.use_surface_guiding = True
scene.cycles.use_volume_guiding = True
scene.cycles.guiding_training_samples = 64
scene.render.use_persistent_data = True
scene.render.resolution_x = 480 if args.preview else 1280
scene.render.resolution_y = 270 if args.preview else 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '16'
scene.render.image_settings.compression = 15
scene.render.film_transparent = False
scene.render.use_border = False
scene.render.use_compositing = True
scene.render.use_sequencer = False

manifest = {
    'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender': bpy.app.version_string, 'frame': scene.frame_current, 'stability': args.state,
    'resolution': [scene.render.resolution_x, scene.render.resolution_y],
    'engine': scene.render.engine, 'device': scene.cycles.device, 'threads': scene.render.threads,
    'samples_max': scene.cycles.samples, 'adaptive_threshold': scene.cycles.adaptive_threshold,
    'adaptive_min_samples': scene.cycles.adaptive_min_samples, 'denoiser': scene.cycles.denoiser,
    'max_bounces': scene.cycles.max_bounces, 'volume_bounces': scene.cycles.volume_bounces,
    'reflective_caustics': scene.cycles.caustics_reflective,
    'refractive_caustics': scene.cycles.caustics_refractive,
    'path_guiding': scene.cycles.use_guiding,
    'guiding_training_samples': scene.cycles.guiding_training_samples,
    'color_depth': scene.render.image_settings.color_depth,
    'color_management': {'transform': scene.view_settings.view_transform,
                         'look': scene.view_settings.look, 'exposure': scene.view_settings.exposure},
    'preview': args.preview, 'views': []}
manifest_path = args.output/'render_manifest.json'
if args.views and manifest_path.exists():
    previous = json.loads(manifest_path.read_text())
    assert {k: v for k, v in previous.items() if k != 'views'} == {
        k: v for k, v in manifest.items() if k != 'views'
    }, 'Cannot resume images with different source or render settings'
    for record in previous['views']:
        if record['name'][:2] not in args.views:
            path = args.output/record['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
            manifest['views'].append(record)
cameras = []
for name, title, location, target, lens in (INSPECTION_VIEWS if args.inspection else VIEWS):
    if name in ('17_board_direct','47_stability_floor_approach'):
        label = bpy.data.objects['RH refine REACTOR STABILITY']
        point = label.matrix_world.translation
        target = (point.x, point.y, point.z-.24)
        if name == '17_board_direct':
            normal = (label.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
            location = tuple(Vector(target)+normal*2.6+Vector((0,0,.13)))
    # Plaques can move within their bays to clear real machinery. Their direct
    # proof cameras follow the final saved lettering, rather than an old guess.
    plaque = {'37_generator_plaque':'RH refine STANDBY GENERATOR',
              '38_reserve_plaque':'RH refine RESERVE POWER A',
              '39_watch_instruction':'RH refine pool instruction'}.get(name)
    if plaque:
        label=bpy.data.objects.get(plaque)
        assert label is not None, 'Missing inspection plaque '+plaque
        distance=(Vector(location)-Vector(target)).length
        point=label.matrix_world.translation
        normal=(label.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        target=tuple(point); location=tuple(point+normal*distance)
    data = bpy.data.cameras.new('DETAIL_' + name)
    data.lens = lens
    data.sensor_width = 36
    if name=='28_main_rope_path':
        data.type='ORTHO';data.ortho_scale=12.8
    data.clip_start = .05
    data.clip_end = 200
    data.dof.use_dof = False
    camera = bpy.data.objects.new('DETAIL_' + name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-Vector(location)).to_track_quat('-Z','Y').to_euler()
    cameras.append((camera, name, title, location, target, lens))

if args.save_review_scene:
    scene.camera = cameras[0][0]
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'reactor_detail_review.blend'))

for camera, name, title, location, target, lens in cameras:
    if args.views and name[:2] not in args.views:
        continue
    scene.camera = camera
    scene.cycles.seed = int(name[:2]) * 101
    destination = args.output/(name+'.png')
    scene.render.filepath = str(destination)
    started = time.monotonic()
    print('VIEW_STARTED', name, flush=True)
    bpy.ops.render.render(write_still=True)
    assert destination.is_file() and destination.stat().st_size > 1000
    record = {'name': name, 'title': title, 'location': location, 'target': target,
              'lens_mm': lens, 'projection': camera.data.type,
              'ortho_scale': camera.data.ortho_scale if camera.data.type=='ORTHO' else None,
              'file': destination.name,
              'elapsed_seconds': round(time.monotonic()-started, 2),
              'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}
    manifest['views'].append(record)
    manifest['views'].sort(key=lambda view: view['name'])
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    print('VIEW_COMPLETED', json.dumps(record), flush=True)

print('BATCH_COMPLETED', len(manifest['views']), flush=True)
# Avoid headless audio shutdown hanging in this read-only cloud runtime.
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
