"""Render labelled corners, walls and significant assets from the isolated room.

Blender --background --factory-startup --disable-autoexec --python render_review.py
Optional: -- --only CORNER_SW (comma-separated IDs). Does not save scene changes.
"""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revamp-review/room-survey'
preview = '--preview' in sys.argv
if preview:
    OUT = ROOT / 'revamp-review/framing-preview'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'module_overhaul_R1.blend'
before = hashlib.sha256(source.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(source), link=False) as (library, loaded):
    loaded.scenes = ['REANIMATION_EDIT_LOCAL']
scene = bpy.data.scenes['REANIMATION_EDIT_LOCAL']
bpy.context.window.scene = scene
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 32
scene.eevee.use_raytracing = False
scene.eevee.shadow_pool_size = '1024'
if preview:
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
shots = []
def shot(id, label, group, position=None, target=None, lens=24, inherited=None):
    shots.append(dict(id=id, label=label, group=group, position=position,
                      target=target, lens=lens, inherited=inherited))
shot('CORNER_SW', '01 | FRONT LEFT / CUTAWAY', 'corners', (-7,-3.5,8.5), (0,4.9,1.1), 21)
shot('CORNER_SE', '02 | FRONT RIGHT / CUTAWAY', 'corners', (7,-3.5,8.5), (0,4.9,1.1), 21)
shot('CORNER_NW', '03 | REAR LEFT / CUTAWAY', 'corners', (-7,12.5,8.5), (0,4.9,1.1), 21)
shot('CORNER_NE', '04 | REAR RIGHT / CUTAWAY', 'corners', (7,12.5,8.5), (0,4.9,1.1), 21)
shot('WALL_SOUTH', '05 | ENTRY WALL', 'walls', (0,7.4,1.9), (0,0,1.8), 22)
shot('WALL_WEST', '06 | OCRU WALL', 'walls', (2.3,4.5,1.9), (-4,4.5,1.8), 19)
shot('WALL_NORTH', '07 | RESTART / DECON WALL', 'walls', (0,1.5,1.9), (0,9,1.8), 22)
shot('WALL_EAST', '08 | RECOVERY / SUPPLIES WALL', 'walls', (-1.1,4.5,1.9), (4,4.5,1.8), 16)
shot('HERO_OCRU', '09 | OCRU REANIMATION UNIT', 'assets', inherited='CAM_HERO')
shot('HERO_RESTART', '10 | RESTART CONSOLE', 'assets', (.1,6.2,1.65), (-.4,8.55,1.05), 24)
shot('HERO_CARTRIDGES', '11 | MEDICAL CARTRIDGE BANK', 'assets', (.9,5.8,1.55), (1,8.6,1.3), 22)
shot('HERO_RESERVE', '12 | RESERVE POWER', 'assets', (-.65,7.3,1.5), (-2.15,8.7,.85), 26)
shot('HERO_DECON', '13 | DECONTAMINATION ALCOVE', 'assets', (1.95,7.3,1.65), (2.33,10.7,1.3), 24)
shot('HERO_RECOVERY', '14 | RECOVERY BERTH', 'assets', (.7,2.8,1.8), (3.3,4.7,.85), 28)
shot('HERO_CART', '15 | TRANSFER CART', 'assets', (-1.6,.9,1.65), (-3.1,1.3,.7), 18)
shot('HERO_SUPPLIES', '16 | SUPPLY WORKBENCH', 'assets', (1,3.4,1.65), (3.55,1.5,.9), 28)
shot('HERO_WASH', '17 | HANDWASH STATION', 'assets', (1.8,3,1.6), (3.7,3,1.15), 38)
shot('HERO_CABINET', '18 | MEDICAL SUPPLIES CABINET', 'assets', (1.2,6.3,1.7), (3.6,7.4,1.65), 25)

overlay = bpy.data.collections.new('TEMP_REVIEW_LABELS')
scene.collection.children.link(overlay)
def emission(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs[0].default_value = (*color,1)
    mat.node_tree.links.new(emit.outputs[0], output.inputs['Surface'])
    return mat
white = emission('Review label white', (.85,.85,.85))
dark = emission('Review label charcoal', (.008,.012,.016))
font = bpy.data.curves.new('Review label', 'FONT')
font.font = bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
font_obj = bpy.data.objects.new('Review label', font)
overlay.objects.link(font_obj)
font.materials.append(white)
mesh = bpy.data.meshes.new('Review label backing')
mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)], [], [(0,1,2,3)])
badge = bpy.data.objects.new('Review label backing', mesh)
overlay.objects.link(badge)
mesh.materials.append(dark)
only = None
if '--' in sys.argv:
    args = sys.argv[sys.argv.index('--')+1:]
    if '--only' in args: only = args[args.index('--only')+1].split(',')
for item in shots:
    if only and item['id'] not in only: continue
    review_light = None
    if item['id'] == 'HERO_CART':
        light = bpy.data.lights.new('Temporary cart inspection fill', 'AREA')
        light.energy = 140
        light.shape = 'DISK'
        light.size = 2
        review_light = bpy.data.objects.new(light.name, light)
        scene.collection.objects.link(review_light)
        review_light.location = (-1.6,1.3,2.7)
        review_light.rotation_euler = (Vector((-3.1,1.3,.6)) - review_light.location).to_track_quat('-Z','Y').to_euler()
        item['temporary_review_light'] = {'purpose':'Reveal cart mechanism in dark parking bay', 'type':'AREA', 'energy_w':140, 'size_m':2}
    cutaway = item['group'] == 'corners'
    hidden = []
    if cutaway:
        for obj in scene.objects:
            if obj.type != 'MESH': continue
            corners_world = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
            lo = [min(v[i] for v in corners_world) for i in range(3)]
            hi = [max(v[i] for v in corners_world) for i in range(3)]
            near_side = (hi[0] < -3.84 if item['position'][0] < 0 else lo[0] > 3.84)
            near_end = (hi[1] < .20 if item['position'][1] < 0 else lo[1] > 8.88 and hi[1] < 9.20)
            if 'ceiling' in obj.name.lower() or near_side or near_end:
                hidden.append((obj, obj.hide_render))
                obj.hide_render = True
    item['temporary_hidden_geometry'] = [obj.name for obj,state in hidden]
    if item['inherited']:
        cam = scene.objects[item['inherited']]
    else:
        data = bpy.data.cameras.new(item['id'])
        cam = bpy.data.objects.new(item['id'], data)
        scene.collection.objects.link(cam)
        cam.location = item['position']
        cam.rotation_euler = (Vector(item['target']) - cam.location).to_track_quat('-Z','Y').to_euler()
        data.lens = item['lens']
        data.sensor_width = 36
        if cutaway:
            # Fit the full visible module, including the projecting decon alcove.
            inverse = cam.rotation_euler.to_quaternion().inverted()
            required = 0.0
            for obj in scene.objects:
                if obj.hide_render or obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Review label'):
                    continue
                for point in obj.bound_box:
                    local = inverse @ (obj.matrix_world @ Vector(point) - cam.location)
                    if local.z < -.1:
                        required = max(required, abs(local.x)/-local.z,
                                       abs(local.y)/-local.z*1600/900)
            data.lens = min(data.lens, 36*.90/(2*required))
    cam.data.clip_start = .01
    scene.camera = cam
    # Render the small label as camera-attached emission geometry. No retouching.
    frame = cam.data.view_frame(scene=scene)
    distance = .1
    corners = [v * (distance / abs(v.z)) for v in frame]
    left, right = min(v.x for v in corners), max(v.x for v in corners)
    bottom = min(v.y for v in corners)
    px = (right-left)/1600
    font.body = item['label']
    font.size = 19*px
    font_obj.parent = cam
    font_obj.location = (left+30*px, bottom+30*px, -.1)
    font_obj.rotation_euler = (0,0,0)
    badge.parent = cam
    badge.location = ((left+20*px)*1.01, (bottom+18*px)*1.01, -.101)
    badge.rotation_euler = (0,0,0)
    badge.scale = ((len(item['label'])*12+24)*px*1.01, 39*px*1.01, 1)
    scene.render.filepath = str(OUT/(item['id']+'.png'))
    print('RENDER_SHOT', item['id'], flush=True)
    if '--skip-existing' not in sys.argv or not Path(scene.render.filepath).exists():
        bpy.ops.render.render(write_still=True)
    for obj,state in hidden:
        obj.hide_render = state
    if review_light:
        bpy.data.objects.remove(review_light, do_unlink=True)
    item['camera_matrix_world'] = [list(row) for row in cam.matrix_world]
    item['actual_lens_mm'] = cam.data.lens
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
manifest = {'source_sha256': before, 'engine': scene.render.engine,
            'resolution':[1600,900], 'samples':32, 'lighting':'Inherited room practical lights and world; temporary soft inspection fill for cart hero only',
            'label_method':'Camera-attached emission text; source scene never saved',
            'shots':shots}
if only and (OUT/'manifest.json').exists():
    prior = json.loads((OUT/'manifest.json').read_text())
    prior_shots = {item['id']:item for item in prior['shots']}
    manifest['shots'] = [item if item['id'] in only else prior_shots.get(item['id'],item) for item in shots]
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('REVIEW_RENDER_COMPLETE', flush=True)
