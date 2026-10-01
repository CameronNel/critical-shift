"""Fixed 600p evidence; extends the labelled medical renderer's review recipe.

Labels, cutaways and diagnostic changes are process-only. Never saves the input.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--baseline',action='store_true')
p.add_argument('--spawn',action='store_true')
p.add_argument('--cold',action='store_true')
p.add_argument('--out',required=True)
p.add_argument('--only',default='')
p.add_argument('--samples',type=int,default=24)
p.add_argument('--diagnostic',choices=['clay','uv','neutral'])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT.parent/'spawn-room/module.blend' if a.spawn else ROOT/('module.blend' if a.baseline else 'module_overhaul_R1.blend')
out=ROOT/'revamp/production/renders'/a.out
out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
source_sha=sha(source)
if any(out.glob('*.png')):
    raise RuntimeError('Use a fresh evidence directory; existing images are not silently reused.')
if a.baseline or a.spawn or a.cold:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'] if not (a.baseline or a.spawn) else bpy.context.scene
else:
    with bpy.data.libraries.load(str(source),link=False) as (lib,loaded):
        loaded.scenes=['COMPLIANCE_EDIT_LOCAL']
    scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL']
bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples
scene.cycles.seed=8217;scene.cycles.use_animated_seed=False;scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.06;scene.cycles.adaptive_min_samples=4
scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=6
scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False
scene.render.resolution_x=1067;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.use_persistent_data=True
shots=[]
def shot(id,label,group='mandatory',inherited=None,position=None,target=None,lens=24):
    shots.append(dict(id=id,label=label,group=group,inherited=inherited,position=position,target=target,lens=lens))
if a.spawn:
    for name in ['REFERENCE_HALL','REFERENCE_BRIEFING','REFERENCE_LOCKER','DETAIL_FourLockers']:
        shot(name,'SPAWN REFERENCE / '+name.replace('_',' '),inherited=name)
else:
    inherited=[('C01_ENTRY','01 | FACILITY ENTRY'),('C02_HERO_DOCK','02 | INSPECTION / WIDE'),
               ('C03_CHECKIN_COUNTER','03 | CHECK-IN HATCH'),('C04_SCANNER_APPROACH','04 | WORKER INSPECTION'),
               ('C05_CONVEYOR_LEAD_TUNNEL','05 | CARGO INSPECTION'),('C06_CART_GATE_G1','06 | CART BYPASS'),
               ('C07_OFFICE_INTERIOR','07 | STAFF OFFICE'),('C08_CONCEALED_SUPPORT_H1','08 | CONCEALED SUPPORT'),
               ('C09_ARRIVAL_GATE_P2','09 | SEALED ARRIVAL'),('C10_ROOF_SERVICES','10 | ROOF SERVICES')]
    # R04 C05/C10 are inside solid geometry; C06 crops the opening and C09 faces
    # the entry rather than arrival. Rebase these before the formal comparison.
    rebased={
        'C05_CONVEYOR_LEAD_TUNNEL':((2.95,4.15,1.65),(4.65,7.4,1.08),25),
        'C06_CART_GATE_G1':((2.3,4.2,1.65),(1.95,7,1.15),24),
        'C09_ARRIVAL_GATE_P2':((1.4,11.4,1.65),(0,15.8,1.85),24),
        'C10_ROOF_SERVICES':((1.4,9.7,2.1),(1.6,6.5,3.65),20)}
    for name,label in inherited:
        if name in rebased:
            pos,target,lens=rebased[name];shot(name,label,position=pos,target=target,lens=lens)
        else:shot(name,label,inherited=name)
    for i,(id,pos) in enumerate([('CORNER_SW',(-11,-4,12)),('CORNER_SE',(11,-4,12)),('CORNER_NW',(-11,20,12)),('CORNER_NE',(11,20,12))]):
        shot(id,f'{11+i:02} | '+id.replace('_',' ')+' / CUTAWAY','corners',position=pos,target=(0,7.9,1.2),lens=26)
    shot('WALL_SOUTH','15 | ENTRY WALL / FRONT OFFICE','walls',position=(0,10.8,2.1),target=(0,0,1.8),lens=18)
    shot('WALL_NORTH','16 | ARRIVAL WALL','walls',position=(0,5,2.1),target=(0,15.8,1.9),lens=18)
    shot('WALL_EAST','17 | SERVICE / CARGO WALL','walls',position=(-1.8,7.9,1.85),target=(6.8,7.9,1.9),lens=18)
    shot('WALL_WEST','18 | OFFICE / STORAGE WALL / CUTAWAY','wall-cutaway',position=(1.2,7.9,2.1),target=(-6.8,7.9,1.8),lens=16)
    shot('HERO_SCANNER','19 | WORKER INSPECTION ARCH','assets',position=(-2.5,3.4,1.85),target=(0,7,1.3),lens=28)
    shot('HERO_CARGO','20 | CARGO EXAMINATION MACHINE','assets',position=(3.2,3.7,1.85),target=(4.65,7.4,1.05),lens=25)
    shot('HERO_EVIDENCE','21 | EVIDENCE STORAGE','assets',position=(-4.5,13,1.65),target=(-5.6,15.25,.9),lens=26)
    shot('HERO_TROLLEY','22 | COVERED TRANSFER TROLLEY','assets',position=(-3.4,10.6,1.65),target=(-5.8,13.2,.85),lens=25)
    shot('HERO_UTILITIES','23 | ELECTRICAL / DATA SERVICES','assets',position=(3.4,11,1.65),target=(6.4,13.3,1.65),lens=25)
    shot('DETAIL_CHECKIN','24 | CHECK-IN WORK / DETAIL','details',position=(-4.6,2.3,1.65),target=(-3.55,3.75,1.0),lens=35)
    shot('PLAYER_REVERSE','25 | REVERSE / PLAYER HEIGHT','mandatory',position=(1.95,11.5,1.65),target=(0,2.5,1.4),lens=25)
    shot('PLAYER_PINCH','26 | NORTH RETURN / PLAYER HEIGHT','mandatory',position=(-3.5,14.8,1.65),target=(-.5,14.8,1.4),lens=25)
    shot('SLICE_ENTRY','SLICE | CHECK-IN / PLAYER HEIGHT','slice',position=(-4.2,.45,1.65),target=(-4.1,3.6,1.56),lens=22)
    shot('SLICE_MATERIAL','SLICE | COUNTER / MATERIALS','slice',position=(-2.8,1.9,1.65),target=(-3.55,3.65,1.1),lens=32)
    shot('SLICE_DOOR','SLICE | STAFF DOOR / CONSTRUCTION','slice',position=(-3.85,1.7,1.65),target=(-5.4,3.6,1.15),lens=30)
if a.only:
    requested=set(a.only.split(','));shots=[s for s in shots if s['id'] in requested]
    if {s['id'] for s in shots}!=requested:raise ValueError('Unknown requested camera')
elif not a.spawn:
    shots=[s for s in shots if s['group']!='slice']
if a.diagnostic:
    for o in scene.objects:
        if o.type=='LIGHT':o.data.energy=0
    scene.world=scene.world.copy()
    bg=scene.world.node_tree.nodes.get('Background')
    if bg:bg.inputs[0].default_value=(.55,.55,.55,1);bg.inputs[1].default_value=.65
    d=bpy.data.lights.new('TEMP neutral practical','AREA');d.energy=800;d.size=5
    light=bpy.data.objects.new(d.name,d);scene.collection.objects.link(light)
    light.location=(-3.5,3,3);light.rotation_euler=(0,0,0)
    if a.diagnostic!='neutral':
        m=bpy.data.materials.new('TEMP diagnostic');m.use_nodes=True
        bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.35,.35,1);bs.inputs['Roughness'].default_value=.8
        if a.diagnostic=='uv':
            tex=m.node_tree.nodes.new('ShaderNodeTexChecker');tex.inputs['Scale'].default_value=10
            tex.inputs['Color1'].default_value=(.08,.18,.28,1);tex.inputs['Color2'].default_value=(.75,.72,.61,1)
            uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='CD_Physical_1m'
            m.node_tree.links.new(uv.outputs[0],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs[0],bs.inputs['Base Color'])
        for o in scene.objects:
            if o.type=='MESH' and (a.diagnostic=='clay' or o.get('overhaul_surface')):
                for slot in o.material_slots:slot.material=m
labels=bpy.data.collections.new('TEMP_REVIEW_LABELS');scene.collection.children.link(labels)
def emission(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear()
    e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1)
    o=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
white=emission('TEMP label white',(.85,.85,.85));dark=emission('TEMP label backing',(.008,.012,.016))
font=bpy.data.curves.new('TEMP label','FONT');font.materials.append(white)
fp=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
if fp.exists():font.font=bpy.data.fonts.load(str(fp))
fobj=bpy.data.objects.new('TEMP label',font);labels.objects.link(fobj)
me=bpy.data.meshes.new('TEMP label backing');me.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);me.materials.append(dark)
badge=bpy.data.objects.new('TEMP label backing',me);labels.objects.link(badge)
manifest={'source_sha256':source_sha,'renderer_sha256':sha(__file__),'resolution':[1067,600],
          'samples':a.samples,'engine':'CYCLES','device':'CPU','seed':8217,'cold_open':a.cold,
          'adaptive_threshold':.06,'adaptive_min_samples':4,'max_bounces':6,'diffuse_bounces':3,'glossy_bounces':3,'transmission_bounces':6,
          'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,
          'exposure':scene.view_settings.exposure,'diagnostic':a.diagnostic,'source_saved':False,
          'label_method':'Temporary camera-attached emission geometry','complete':False,'shots':[]}
for item in shots:
    hidden=[]
    if item['group'] in {'corners','wall-cutaway'}:
        for o in scene.objects:
            if o.type!='MESH' or o.name.startswith('TEMP '):continue
            v=[o.matrix_world @ Vector(c) for c in o.bound_box]
            lo=[min(p[k] for p in v) for k in range(3)];hi=[max(p[k] for p in v) for k in range(3)]
            roof='ceiling slab' in o.name.lower() or 'roof deck' in o.name.lower()
            side=False
            if item['group']=='corners':
                pos=item['position'];side=(hi[0]<-6.70 if pos[0]<0 else lo[0]>6.70)
                side=side or (hi[1]<.10 if pos[1]<0 else lo[1]>15.68)
            else:
                side=('office' in o.name.lower() and -2.52<((lo[0]+hi[0])/2)<-2.28) or 'support screen' in o.name.lower() or 'Observation glass' in o.name
            if roof or side:hidden.append((o,o.hide_render));o.hide_render=True
    if item['inherited']:
        cam=scene.objects[item['inherited']]
    else:
        data=bpy.data.cameras.new('REVIEW_'+item['id']);cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
        cam.location=item['position'];cam.rotation_euler=(Vector(item['target'])-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=item['lens'];data.sensor_width=36
        if item['group']=='corners':
            inv=cam.rotation_euler.to_quaternion().inverted();required=0
            for o in scene.objects:
                if o.hide_render or o.type not in {'MESH','CURVE','FONT'} or o.name.startswith('TEMP '):continue
                for p in o.bound_box:
                    q=inv @ (o.matrix_world @ Vector(p)-cam.location)
                    required=max(required,abs(q.x)*2,abs(q.y)*2*1067/600)
            data.type='ORTHO';data.ortho_scale=required/.90
    scene.camera=cam;cam.data.clip_start=.01;bpy.context.view_layer.update()
    frame=cam.data.view_frame(scene=scene);distance=.1
    frame=[Vector((v.x,v.y,-distance)) if cam.data.type=='ORTHO' else v*(distance/abs(v.z)) for v in frame]
    left=min(v.x for v in frame);right=max(v.x for v in frame);bottom=min(v.y for v in frame);px=(right-left)/1067
    font.body=item['label'];font.size=13*px;fobj.parent=cam;fobj.location=(left+20*px,bottom+20*px,-.1);fobj.rotation_euler=(0,0,0)
    badge.parent=cam;badge.location=((left+13*px)*1.01,(bottom+12*px)*1.01,-.101);badge.rotation_euler=(0,0,0);badge.scale=((len(item['label'])*8+16)*px*1.01,26*px*1.01,1)
    dest=out/(item['id']+'.png');scene.render.filepath=str(dest)
    print('RENDER_SHOT',item['id'],flush=True)
    result=bpy.ops.render.render(write_still=True)
    if 'FINISHED' not in result or not dest.is_file():raise RuntimeError('Missing completed render: '+item['id'])
    h=dest.read_bytes()[:24]
    if h[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',h[16:24])!=(1067,600):raise RuntimeError('Incorrect render size')
    item.update(camera_matrix_world=[list(r) for r in cam.matrix_world],actual_lens_mm=cam.data.lens,projection=cam.data.type,image_sha256=sha(dest),temporary_hidden_geometry=[o.name for o,state in hidden])
    if cam.data.type=='ORTHO':item['ortho_scale_m']=cam.data.ortho_scale
    for o,state in hidden:o.hide_render=state
    manifest['shots'].append(item)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if sha(source)!=source_sha:raise RuntimeError('Source changed during rendering')
manifest['complete']=True;manifest['requested_view_count']=len(shots)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('RENDER_BATCH_COMPLETE',len(shots),flush=True)
