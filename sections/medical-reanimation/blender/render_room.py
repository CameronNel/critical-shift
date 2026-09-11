"""Fresh-process camera renderer. Invoke Blender through facility-run/gpu_gate.py."""
import bpy, sys, argparse, json, hashlib, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--cameras',default='all');p.add_argument('--samples',type=int,default=48);p.add_argument('--width',type=int,default=1440);p.add_argument('--height',type=int,default=900);p.add_argument('--device',default='HIP')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.seed=17
s.render.resolution_x=a.width;s.render.resolution_y=a.height;s.render.resolution_percentage=100
prefs=bpy.context.preferences.addons['cycles'].preferences
if a.device=='CPU':s.cycles.device='CPU'
else:
    prefs.compute_device_type=a.device;prefs.get_devices()
    for d in prefs.devices:d.use=(d.type==a.device)
    if not any(d.use for d in prefs.devices):raise RuntimeError('Requested GPU unavailable')
    s.cycles.device='GPU'
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
cams=sorted([o for o in bpy.data.objects if o.type=='CAMERA'],key=lambda o:o.name)
if a.cameras!='all':
    requested=a.cameras.split(',');cams=[bpy.data.objects[n] for n in requested]
evidence={'blend':Path(bpy.data.filepath).name,'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'revision':s.get('revision'),'source_sha256':s.get('source_sha256'),'settings':{'engine':'CYCLES','device':a.device,'samples':a.samples,'resolution':[a.width,a.height],'seed':17},'renders':[]}
for c in cams:
    t=time.time();s.camera=c;s.render.filepath=str(out/(c.name+'.png'));bpy.ops.render.render(write_still=True)
    evidence['renders'].append({'camera':c.name,'seconds':round(time.time()-t,2),'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens_mm':c.data.lens})
    (out/'render_manifest.json').write_text(json.dumps(evidence,indent=2))
    print('RENDER_COMPLETE',c.name,flush=True)
print('BATCH_COMPLETE',len(cams),flush=True)
