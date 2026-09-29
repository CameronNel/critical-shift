"""Render saved spawn-yard cameras; GPU jobs must run through shared gpu_gate.py."""
import bpy,json,hashlib,ctypes,sys
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/spawn-finish';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
if '--cold' in sys.argv:
 import runpy
 runpy.run_path(str(Path(__file__).with_name('verify_spawn_finish.py')),run_name='__main__')
s=bpy.context.scene;s.frame_set(1);s.render.engine='CYCLES'
nearby=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if hi[2]>6 and hi[0]>-25 and lo[0]<10 and hi[1]>28 and lo[1]<55:
  nearby.append(dict(name=o.name_full,lo=lo,hi=hi,materials=[m.name if m else None for m in o.data.materials]))
(out/'nearby-tall.json').write_text(json.dumps(nearby,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='HIP';prefs.get_devices()
gpus=[d for d in prefs.devices if d.type=='HIP'];assert gpus,'No HIP device found'
for d in prefs.devices:d.use=d in gpus
s.cycles.device='GPU';s.cycles.samples=16;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
views=[('01-front-yard',(-17,27,1.7),(-28,11,2.1),24),('02-east-side',(-10,8,1.7),(-28,9,2.0),24),('03-yard-reverse',(-27,16,1.7),(-18,29,1.5),24)]
if '--slice' in sys.argv:views=views[:1]
if '--cold' in sys.argv:views=views[:1]
m=dict(source=str(src),source_sha256=before,settings=dict(device='GPU',backend='HIP',devices=[d.name for d in gpus],samples=16,seed=73,resolution=[1280,720]),views=[],complete=False)
for name,pos,target,lens in views:
 cam=bpy.data.objects.get('SY CAMERA | '+name)
 assert cam is not None,'Saved camera missing'
 assert (cam.location-Vector(pos)).length<.001
 s.camera=cam;s.render.filepath=str(out/(('cold-' if '--cold' in sys.argv else '')+name+'.png'));bpy.ops.render.render(write_still=True)
 m['views'].append(dict(name=name,path=s.render.filepath,position=pos,target=target,lens=lens,saved_camera=True,sha256=sha(s.render.filepath)))
 (out/('cold-render.json' if '--cold' in sys.argv else 'manifest.json')).write_text(json.dumps(m,indent=2));print('SPAWN_FINISH_RENDERED',name,flush=True)
m.update(complete=True,source_unchanged=sha(src)==before)
(out/('cold-render.json' if '--cold' in sys.argv else 'manifest.json')).write_text(json.dumps(m,indent=2));print('SPAWN_FINISH_COMPLETE',flush=True)
