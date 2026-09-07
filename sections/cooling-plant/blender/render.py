"""Run only through shared facility gpu_gate.py. Opens authored blend first."""
import bpy,sys,json,argparse,time,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--cameras',default='all');ap.add_argument('--out',required=True);ap.add_argument('--samples',type=int,default=48);ap.add_argument('--width',type=int,default=1440)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);sc=bpy.context.scene;out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
prefs=bpy.context.preferences.addons['cycles'].preferences
backend='CPU'
for kind in ('HIP','OPTIX','CUDA'):
    try:
        prefs.compute_device_type=kind;prefs.get_devices()
        devices=[d for d in prefs.devices if d.type==kind]
        if devices:
            for d in prefs.devices:d.use=d.type==kind
            backend=kind;break
    except Exception:pass
sc.cycles.device='GPU' if backend!='CPU' else 'CPU';sc.cycles.samples=a.samples
sc.render.resolution_x=a.width;sc.render.resolution_y=round(a.width*2/3);sc.render.resolution_percentage=100
names=sorted(o.name for o in sc.objects if o.type=='CAMERA') if a.cameras=='all' else a.cameras.split(',')
log=dict(revision=sc.get('revision'),blend=bpy.data.filepath,source_sha256=sc.get('source_sha256'),backend=backend,samples=a.samples,resolution=[sc.render.resolution_x,sc.render.resolution_y],cameras=[])
print('COOLING_RENDER_BACKEND',backend,flush=True)
for name in names:
    sc.camera=sc.objects[name];sc.render.filepath=str(out/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True)
    log['cameras'].append(dict(camera=name,seconds=round(time.time()-start,2),sha256=hashlib.sha256(Path(sc.render.filepath).read_bytes()).hexdigest(),location=list(sc.camera.location),rotation=list(sc.camera.rotation_euler),lens=sc.camera.data.lens))
    (out/'render_manifest.json').write_text(json.dumps(log,indent=2));print('COOLING_CAMERA_DONE',name,flush=True)
print('COOLING_RENDER_OK',flush=True)
