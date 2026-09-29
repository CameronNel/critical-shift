"""Read-only, targeted quick renders for finish diagnosis. Never saves the scene."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/finish-diagnostics';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
s=bpy.context.scene;s.frame_set(1)
data=bpy.data.cameras.new('TEMP | Finish diagnostic');cam=bpy.data.objects.new(data.name,data);s.collection.objects.link(cam);s.camera=cam;data.clip_start=.08;data.clip_end=300
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
views=[
 ('mine-canopy',(-28,-34,1.7),(-37,-29,2.2),24,'Player-height canopy, entrance and structure junction'),
 ('mine-cliff-yard',(-13,-36,1.7),(-24,-39,3.0),32,'Player-height cliff foot and yard transition'),
 ('refinery-floor',(7,-24,1.7),(4.8,-19,.4),35,'Player-height apron, joint edges and wetness'),
 ('refinery-roof',(-1.3,-24,6.9),(-5.5,-15,5.9),28,'Roof-service diagnostic; not a ground-level gameplay view'),
]
m=dict(source=str(src),source_sha256=before,saved_scene=False,settings=dict(device='CPU',threads=1,samples=4,resolution=[960,540],seed=73),views=[],complete=False)
for name,pos,target,lens,role in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 m['views'].append(dict(name=name,path=s.render.filepath,sha256=sha(s.render.filepath),position=pos,target=target,lens=lens,role=role));assert sha(src)==before
 (out/'manifest.json').write_text(json.dumps(m,indent=2));print('DIAGNOSTIC_RENDERED',name,flush=True)
m.update(complete=True,source_unchanged=True);(out/'manifest.json').write_text(json.dumps(m,indent=2));print('DIAGNOSTICS_COMPLETE',flush=True)
