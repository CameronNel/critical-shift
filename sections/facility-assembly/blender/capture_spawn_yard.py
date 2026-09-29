"""Read-only exterior views of the current spawn and neighbouring yard."""
import bpy,json,hashlib,ctypes,sys
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/spawn-yard';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
if '--inspect' in sys.argv:
 records=[]
 for o in s.objects:
  if o.type=='MESH' and ('spawn' in o.name.lower() or 'spawn' in ' '.join(c.name.lower() for c in o.users_collection)):
   pts=[o.matrix_world@Vector(v) for v in o.bound_box];records.append(dict(name=o.name_full,hidden=o.hide_render,bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],collections=[c.name for c in o.users_collection]))
 (out/'inspection.json').write_text(json.dumps(dict(source=str(src),sha256=before,objects=records),indent=2));print('SPAWN_INSPECTED',len(records),flush=True)
else:
 data=bpy.data.cameras.new('TEMP | Spawn yard inspection');cam=bpy.data.objects.new(data.name,data);s.collection.objects.link(cam);s.camera=cam;data.clip_start=.08;data.clip_end=300
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
 views=[('01-front-yard',(-17,27,1.7),(-28,11,2.1),24),('02-east-side',(-10,8,1.7),(-28,9,2.0),24),('03-yard-reverse',(-27,16,1.7),(-18,29,1.5),24)]
 m=dict(source=str(src),source_sha256=before,scene_saved=False,settings=dict(device='CPU',threads=1,samples=4,resolution=[1280,720],seed=73),views=[],complete=False)
 if '--yard-only' in sys.argv:
  m=json.loads((out/'manifest.json').read_text());assert m['source_sha256']==before;m['views']=[v for v in m['views'] if v['name']!='03-yard-reverse'];m['complete']=False;views=views[-1:]
 for name,pos,target,lens in views:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
  m['views'].append(dict(name=name,path=s.render.filepath,position=pos,target=target,lens=lens,sha256=sha(s.render.filepath)));assert sha(src)==before;(out/'manifest.json').write_text(json.dumps(m,indent=2));print('SPAWN_RENDERED',name,flush=True)
 m.update(complete=True,source_unchanged=True);(out/'manifest.json').write_text(json.dumps(m,indent=2));print('SPAWN_COMPLETE',flush=True)
