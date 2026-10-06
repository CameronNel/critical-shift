"""Actual full-map capture. Does not save or modify source Blender files."""
import bpy, json, math, hashlib, argparse, sys
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path.cwd();OUT=ROOT/'mine-camera-output';OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--survey-only',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
meta=json.loads((ROOT/'MAP.json').read_text())
source=ROOT/meta['inspection_scene'];original=hashlib.sha256(source.read_bytes()).hexdigest()
assert original=='4d5d160d5c9d25b0a447fda933974790260cdde7aced2db1da1c908afdcdc937'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
scene=bpy.context.scene;bpy.context.view_layer.update()
libraries=[{'name':x.name,'path':x.filepath,'missing':bool(x.is_missing)} for x in bpy.data.libraries]
assert len(libraries)==24 and not any(x['missing'] for x in libraries),libraries
images=[{'name':im.name_full,'path':im.filepath,'packed':bool(im.packed_file) or bool(im.packed_files)} for im in bpy.data.images]
existing=[]
for ob in bpy.data.objects:
    if ob.type=='CAMERA':existing.append({'name':ob.name_full,'matrix_world':[list(r) for r in ob.matrix_world],'lens':ob.data.lens,'hide_render':ob.hide_render,'library':ob.library.filepath if ob.library else None})
nearby=[]
for ob in bpy.data.objects:
    if ob.library or ob.type not in {'MESH','EMPTY','LIGHT','FONT'}:continue
    p=ob.matrix_world.translation
    if (-55<p.x<8 and -48<p.y<-13) or any(s in ob.name.lower() for s in ['mine','s01 exterior']):
        nearby.append({'name':ob.name_full,'type':ob.type,'location':list(p),'dimensions':list(ob.dimensions),'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,'collections':[c.name for c in ob.users_collection],'data':ob.data.name if ob.data else None,'materials':[m.name if m else None for m in getattr(ob.data,'materials',[])]})
report={'source':meta['inspection_scene'],'source_sha256':original,'blender_version':bpy.app.version_string,'objects':len(bpy.data.objects),'libraries':libraries,'images':images,'existing_cameras':existing,'collections':[{'name':c.name_full,'objects':len(c.objects),'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.data.collections],'nearby_objects':nearby,'source_engine':scene.render.engine}
(OUT/'SCENE_SURVEY.json').write_text(json.dumps(report,indent=2))
print('FULL_MAP_OPENED',len(bpy.data.objects),len(libraries),len(images),flush=True)
layout=json.loads((ROOT/'sections/facility-assembly/production/LAYOUT_A12.json').read_text());pose=layout['placements']['mine']
matrix=Matrix.Translation(Vector(pose['translation']))@Matrix.Rotation(math.radians(pose['rotation_z_degrees']),4,'Z')
specs=[('MINE_APPROACH',(0,-34,1.72),(0,-20.4,2.15),32),('MINE_OBLIQUE',(-9,-31,2.0),(0,-19.5,2.2),30),('MINE_CONTEXT',(-11,-38,7.0),(0,-15,2.5),35)]
fixed=[]
for name,loc,target,lens in specs:
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
    ob.location=matrix@Vector(loc);aim=matrix@Vector(target)
    ob.rotation_euler=(aim-ob.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.sensor_width=36;data.sensor_fit='HORIZONTAL';data.clip_start=.05;data.clip_end=500;data.dof.use_dof=False
    bpy.context.view_layer.update()
    rec={'id':name,'origin':'actual assembled R17, mine placement transform','local_position':loc,'local_target':target,'world_position':list(ob.location),'world_target':list(aim),'matrix_world':[list(r) for r in ob.matrix_world],'lens_mm':data.lens,'sensor_width_mm':data.sensor_width,'sensor_fit':data.sensor_fit,'clip_start':data.clip_start,'clip_end':data.clip_end,'resolution':[1280,720],'pixel_aspect':[1,1],'dof':False,'shift_x':data.shift_x,'shift_y':data.shift_y}
    rec['camera_sha256']=hashlib.sha256(json.dumps(rec,sort_keys=True).encode()).hexdigest();fixed.append(rec)
(OUT/'CAMERAS.json').write_text(json.dumps(fixed,indent=2))
if args.survey_only:
    print('SURVEY_DONE',flush=True)
else:
    # Offline CPU capture only. The authored scene stays EEVEE and is never saved.
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
    scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.06
    scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE'
    if hasattr(scene.cycles,'denoising_use_gpu'):scene.cycles.denoising_use_gpu=False
    scene.cycles.time_limit=90;scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=2
    scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.film_transparent=False;scene.render.use_compositing=False;scene.render.use_persistent_data=True
    for rec in fixed:
        scene.camera=bpy.data.objects[rec['id']];scene.render.filepath=str(OUT/(rec['id']+'.png'))
        print('RENDER_START',rec['id'],flush=True);bpy.ops.render.render(write_still=True)
        rec['image_sha256']=hashlib.sha256((OUT/(rec['id']+'.png')).read_bytes()).hexdigest()
        (OUT/'CAMERAS.json').write_text(json.dumps(fixed,indent=2))
        print('RENDER_DONE',rec['id'],flush=True)
    (OUT/'RESULT.json').write_text(json.dumps({'actual_full_map_opened':True,'source_unchanged':True,'capture_engine':'Cycles CPU, offline capture only','source_engine':report['source_engine'],'source':meta['inspection_scene'],'source_sha256':original,'views':fixed,'status':'CAMERA_SELECTION_NOT_ART_ACCEPTANCE'},indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==original,'Source changed'
