"""Render fixed, labelled evidence from the additive overhaul. Never saves changes.

Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python render_overhaul.py
Optional: -- --only CORNER_SW (comma-separated IDs). Does not save scene changes.
"""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output_name = args[args.index('--out')+1] if '--out' in args else 'cycle-1'
OUT = ROOT / 'revamp-review/production/renders' / output_name
preview = '--preview' in sys.argv
diagnostic = args[args.index('--diagnostic')+1] if '--diagnostic' in args else None
if diagnostic and diagnostic not in {'clay','uv','neutral'}:
    raise ValueError('Diagnostic must be clay, uv or neutral')
if preview:
    OUT = ROOT / 'revamp-review/framing-preview'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'module_overhaul_R2.blend'
before = hashlib.sha256(source.read_bytes()).hexdigest()
renderer_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
prior_manifest=None
if (OUT/'manifest.json').exists():
    prior_manifest=json.loads((OUT/'manifest.json').read_text())
    if prior_manifest.get('source_sha256')!=before:
        if '--only' in args or '--skip-existing' in args:
            raise RuntimeError('Partial or cached rendering requires an output manifest for this exact source SHA; use a new directory')
        prior_manifest=None
if '--skip-existing' in args and any(OUT.glob('*.png')) and prior_manifest is None:
    raise RuntimeError('Existing PNGs have no matching provenance; use a new output directory')
if ('--skip-existing' in args or '--only' in args) and prior_manifest:
    if prior_manifest.get('renderer_sha256')!=renderer_sha or bool(prior_manifest.get('cold_open',False))!=('--cold' in sys.argv):
        raise RuntimeError('Cached images do not match the current renderer recipe and cold-open mode; use a new directory')
if '--cold' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
else:
    with bpy.data.libraries.load(str(source), link=False) as (library, loaded):
        loaded.scenes = ['REANIMATION_EDIT_LOCAL']
scene = bpy.data.scenes['REANIMATION_EDIT_LOCAL']
bpy.context.window.scene = scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
if preview:
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x = 1067
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
if diagnostic:
    # Disposable inspection only. Neither material replacement nor temporary
    # lighting is saved into the authored source or treated as its art evidence.
    for obj in scene.objects:
        if obj.type=='LIGHT':obj.data.energy=0
    nodes=scene.world.node_tree.nodes;nodes.clear()
    bg=nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.55,.55,.55,1);bg.inputs[1].default_value=.6
    out=nodes.new('ShaderNodeOutputWorld');scene.world.node_tree.links.new(bg.outputs[0],out.inputs[0])
    data=bpy.data.lights.new('TEMP | Neutral inspection','AREA');data.energy=650;data.shape='DISK';data.size=5
    light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light)
    light.location=(0,4.5,3.3);light.rotation_euler=(0,0,0)
    if diagnostic in {'clay','uv'}:
        mat=bpy.data.materials.new('TEMP | '+diagnostic);mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.34,.34,.34,1);p.inputs['Roughness'].default_value=.8
        if diagnostic=='uv':
            checker=mat.node_tree.nodes.new('ShaderNodeTexChecker');checker.inputs['Scale'].default_value=20
            checker.inputs['Color1'].default_value=(.08,.18,.28,1);checker.inputs['Color2'].default_value=(.75,.72,.61,1)
            coord=mat.node_tree.nodes.new('ShaderNodeUVMap');coord.uv_map='MED_Physical_1m';mat.node_tree.links.new(coord.outputs[0],checker.inputs['Vector']);mat.node_tree.links.new(checker.outputs[0],p.inputs['Base Color'])
        for obj in scene.objects:
            if obj.type=='MESH' and (diagnostic=='clay' or obj.name.startswith('MED_R2 |') or obj.data.name.startswith('MED | Skill revised')):
                for slot in obj.material_slots:slot.material=mat
shots = []
def shot(id, label, group, position=None, target=None, lens=24, inherited=None):
    shots.append(dict(id=id, label=label, group=group, position=position,
                      target=target, lens=lens, inherited=inherited))
shot('ENTRY', '19 | ENTRY / PLAYER HEIGHT', 'mandatory', inherited='CAM_ENTRY')
shot('REVERSE', '20 | REVERSE / PLAYER HEIGHT', 'mandatory', inherited='CAM_REVERSE')
shot('PINCH', '21 | RESCUE ROUTE / PLAYER HEIGHT', 'mandatory', inherited='MED_ROUTE')
shot('DETAIL_OCRU', '22 | OCRU CARRIAGE / DETAIL', 'details', inherited='MED_DETAIL_OCRU')
shot('DETAIL_SUPPLIES', '23 | CLINICAL WORK / DETAIL', 'details', inherited='MED_DETAIL_SUPPLIES')
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
shot('HIDDEN_BAG', '24 | BAG / INSPECTION FILL', 'inspection', (-1.35,4.63,.72), (-2.10,4.63,.492), 35)

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
font_path=ROOT/'revamp-review/production/fonts/DejaVuSans.ttf'
if not font_path.exists():font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
if font_path.exists():font.font = bpy.data.fonts.load(str(font_path))
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
if '--skip-existing' in args:
    known={item['id']:item for item in (prior_manifest or {}).get('shots',[]) if 'camera_matrix_world' in item}
    for item in shots:
        if (not only or item['id'] in only) and (OUT/(item['id']+'.png')).exists() and item['id'] not in known:
            raise RuntimeError('Cached image lacks completed camera evidence: '+item['id'])
checkpoint={item['id']:item for item in (prior_manifest or {}).get('shots',[]) if 'camera_matrix_world' in item}
for item in shots:
    if only and item['id'] not in only: continue
    review_light = None
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
                    required = max(required,abs(local.x)*2,abs(local.y)*2*1067/600)
            data.type='ORTHO'
            data.ortho_scale=required/.90
    cam.data.clip_start = .01
    scene.camera = cam
    # Cached images do not invoke render's dependency-graph update. Resolve the
    # new camera transform before recording provenance even when skipping pixels.
    bpy.context.view_layer.update()
    if item['group']=='inspection':
        # Owner-only inspection evidence of the concealed prop. This fill is
        # explicitly labelled, temporary, and never saved in the authored scene.
        d=bpy.data.lights.new('TEMP | Concealed bag inspection fill','AREA');d.energy=2;d.color=(.92,.92,.88);d.size=.25
        review_light=bpy.data.objects.new(d.name,d);scene.collection.objects.link(review_light)
        review_light.location=(-1.68,4.63,.64)
        review_light.rotation_euler=(Vector((-2.1,4.63,.50))-review_light.location).to_track_quat('-Z','Y').to_euler()
        item['temporary_inspection_fill_watts']=2
    # Render the small label as camera-attached emission geometry. No retouching.
    frame = cam.data.view_frame(scene=scene)
    distance = .1
    corners = [Vector((v.x,v.y,-distance)) for v in frame] if cam.data.type=='ORTHO' else [v * (distance / abs(v.z)) for v in frame]
    left, right = min(v.x for v in corners), max(v.x for v in corners)
    bottom = min(v.y for v in corners)
    px = (right-left)/1067
    font.body = item['label']
    font.size = 13*px
    font_obj.parent = cam
    font_obj.location = (left+20*px, bottom+20*px, -.1)
    font_obj.rotation_euler = (0,0,0)
    badge.parent = cam
    badge.location = ((left+13*px)*1.01, (bottom+12*px)*1.01, -.101)
    badge.rotation_euler = (0,0,0)
    badge.scale = ((len(item['label'])*8+16)*px*1.01, 26*px*1.01, 1)
    scene.render.filepath = str(OUT/(item['id']+'.png'))
    print('RENDER_SHOT', item['id'], flush=True)
    if '--skip-existing' not in sys.argv or not Path(scene.render.filepath).exists():
        result=bpy.ops.render.render(write_still=True)
        if 'FINISHED' not in result:
            raise RuntimeError('Render cancelled or failed: '+item['id'])
    # Blender can return from an interrupted render without writing a frame.
    # A camera checkpoint and complete manifest require the actual 600p PNG.
    output=Path(scene.render.filepath)
    if not output.is_file():
        raise RuntimeError('Render did not write its PNG: '+item['id'])
    import struct
    with output.open('rb') as handle:header=handle.read(24)
    if header[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',header[16:24])!=(1067,600):
        raise RuntimeError('Render is not the required 1067 x 600 PNG: '+item['id'])
    for obj,state in hidden:
        obj.hide_render = state
    if review_light:
        bpy.data.objects.remove(review_light, do_unlink=True)
    item['camera_matrix_world'] = [list(row) for row in cam.matrix_world]
    item['actual_lens_mm'] = cam.data.lens
    item['projection'] = cam.data.type
    if cam.data.type=='ORTHO':item['ortho_scale_m']=cam.data.ortho_scale
    checkpoint[item['id']]=item.copy()
    progress={'source_sha256':before,'renderer_sha256':renderer_sha,'engine':scene.render.engine,'resolution':[1067,600],'samples':24,'cold_open':'--cold' in sys.argv,'diagnostic':diagnostic,'complete':False,'shots':list(checkpoint.values())}
    temporary=OUT/'manifest.tmp.json';temporary.write_text(json.dumps(progress,indent=2));temporary.replace(OUT/'manifest.json')
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
if not only and not diagnostic and (len(checkpoint)!=24 or any(not (OUT/(item['id']+'.png')).is_file() for item in shots)):
    raise RuntimeError('Full render batch is incomplete')
manifest = {'source_sha256': before,'renderer_sha256':renderer_sha, 'engine': scene.render.engine,'complete':not only and not diagnostic,'diagnostic':diagnostic,
            'resolution':[1067,600], 'samples':24,'cold_open':'--cold' in sys.argv, 'lighting':'Authored overhaul lights and physical Cycles bounce; only the explicitly labelled concealed-bag inspection uses a temporary 2 W fill',
            'label_method':'Camera-attached emission text; source scene never saved',
            'shots':shots}
if only:
    prior_shots={item['id']:item for item in (prior_manifest or {}).get('shots',[]) if 'camera_matrix_world' in item and (OUT/(item['id']+'.png')).exists()}
    completed={item['id']:item for item in shots if 'camera_matrix_world' in item}
    prior_shots.update(completed)
    manifest['shots']=[prior_shots[item['id']] for item in shots if item['id'] in prior_shots]
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('REVIEW_RENDER_COMPLETE', flush=True)
