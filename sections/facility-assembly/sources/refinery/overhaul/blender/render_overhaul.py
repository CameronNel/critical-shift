"""Fixed-camera CPU review, source stays unchanged. Arguments: revision [cameras...]."""
import bpy,sys,json,hashlib,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['slice']
rev=a[0];names=a[1:] or ['CAM_ENTRY','CAM_MAIN_ROUTE','CAM_PROCESS','CAM_REVERSE','CAM_PINCH','CAM_MATERIAL','CAM_ASSEMBLY','CAM_DISPATCH','CAM_MINE_TO_CRUSHER','CAM_WORK_NOOK','CAM_HERO_DETAIL']
out=root/'production/renders'/rev;out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(src)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.seed=73;s.cycles.max_bounces=8
s.render.threads_mode='FIXED';s.render.threads=8;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
manifest=dict(source=str(src),source_sha256=before,blender=bpy.app.version_string,settings=dict(engine='CYCLES',device='CPU',samples=24,resolution=[960,540],seed=73,world_strength=0),views=[],complete=False)
for name in names:
 s.camera=s.objects[name];s.render.filepath=str(out/(name+'.png'));t=time.monotonic();bpy.ops.render.render(write_still=True)
 manifest['views'].append(dict(camera=name,matrix=[list(r) for r in s.camera.matrix_world],lens=s.camera.data.lens,path=s.render.filepath,sha256=sha(Path(s.render.filepath)),seconds=time.monotonic()-t));(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('RENDERED',name,flush=True)
manifest.update(complete=True,source_unchanged=sha(src)==before);assert manifest['source_unchanged'];(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
