"""Read-only orthographic refinery capture, 10 m beyond its facade on each side."""
import bpy,json,hashlib,ctypes,math
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/refinery-top';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
walls=[o for o in s.objects if o.name.startswith('RFX | Solid mineral facade panel')];assert len(walls)==75,len(walls)
points=[o.matrix_world@Vector(v) for o in walls for v in o.bound_box]
lo=[min(p[i] for p in points) for i in (0,1)];hi=[max(p[i] for p in points) for i in (0,1)]
width=hi[0]-lo[0]+20;height=hi[1]-lo[1]+20;cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2
cam=bpy.data.objects.new('CAPTURE | Refinery top 10m margin',bpy.data.cameras.new('CAPTURE | Refinery top 10m margin'));s.collection.objects.link(cam)
cam.location=(cx,cy,65);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.clip_start=.1;cam.data.clip_end=200;cam.data.sensor_fit='HORIZONTAL'
s.render.resolution_y=720;s.render.resolution_x=math.ceil(720*width/height);s.render.resolution_percentage=100;s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1
cam.data.ortho_scale=height*s.render.resolution_x/720;s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'refinery-top-10m.png')
print('TOP_FRAMED',lo,hi,width,height,s.render.resolution_x,s.render.resolution_y,flush=True)
bpy.ops.render.render(write_still=True)
assert sha(src)==before,'Source changed concurrently; render still records its loaded revision'
(out/'manifest.json').write_text(json.dumps(dict(source=str(src),source_sha256=before,source_unchanged=True,saved_scene=False,facade_bounds_xy=[lo,hi],minimum_margin_m=10,camera_position=list(cam.location),camera_rotation=list(cam.rotation_euler),projection='ORTHO',ortho_scale=cam.data.ortho_scale,frame_size_m=[cam.data.ortho_scale,height],resolution=[s.render.resolution_x,720],engine='CYCLES',device='CPU',threads=1,samples=8,image=str(out/'refinery-top-10m.png'),image_sha256=sha(out/'refinery-top-10m.png')),indent=2));print('TOP_RENDER_COMPLETE',flush=True)
