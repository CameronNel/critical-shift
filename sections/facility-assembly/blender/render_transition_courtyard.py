"""Remaining fixed-camera 720p CPU evidence; does not save scene changes."""
import bpy,json,hashlib,ctypes
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/courtyard';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'build-verification.json').read_text());SRC=Path(bpy.data.filepath);assert sha(SRC)==report['saved_sha256']
manifest=json.loads((OUT/'manifest.json').read_text());assert manifest['source_sha256']==report['saved_sha256']
for view in manifest['views']:view.setdefault('samples',12)
s=bpy.context.scene;s.frame_set(1);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
manifest['settings']['samples']='per-view: 12 left route, 8 remaining CPU previews'
for name in ('03_APPROACH','04_REVERSE','01_CONCEPT'):
    s.camera=bpy.data.objects['CY CAMERA | '+name];p=OUT/(name+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    manifest['views']=[v for v in manifest['views'] if v['name']!=name]
    manifest['views'].append(dict(name=name,path=str(p),sha256=sha(p),samples=8,saved_camera=s.camera.name))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COURTYARD_RENDER',name,flush=True)
manifest['complete']=True;manifest['source_unchanged']=sha(SRC)==report['saved_sha256'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
