"""Read-only current courtyard inventory; no GUI, saves or GPU work."""
import bpy, json, ctypes, hashlib
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
out=Path(__file__).resolve().parents[3]/'runtime/out/environment/courtyard'
out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
s.frame_set(s.frame_current)
bpy.context.view_layer.update()
rows=[]
for o in s.objects:
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]
        if lo[0]<15 and hi[0]>-80 and lo[1]<0 and hi[1]>-66:
            rows.append(dict(name=o.name,lo=lo,hi=hi,mesh=o.data.name,verts=len(o.data.vertices),local=not bool(o.library),visible=o.visible_get(),hide_render=o.hide_render,collections=[c.name for c in o.users_collection],materials=[m.name if m else None for m in o.data.materials]))
cams=[dict(name=o.name,location=list(o.location),rotation=list(o.rotation_euler),lens=o.data.lens,type=o.data.type,ortho=o.data.ortho_scale) for o in s.objects if o.type=='CAMERA']
report=dict(source=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),version=bpy.app.version_string,units=s.unit_settings.scale_length,objects=rows,cameras=cams,libraries=[dict(name=l.name,path=bpy.path.abspath(l.filepath)) for l in bpy.data.libraries])
(out/'inventory.json').write_text(json.dumps(report,indent=2))
print('COURTYARD_INVENTORY',len(rows),'objects',len(cams),'cameras',str(out),flush=True)
cd=bpy.data.cameras.new('TEMP courtyard baseline'); cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam)
cam.location=(14,-64,33);cam.rotation_euler=(Vector((-22,-26,1))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=43;s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.seed=73
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'baseline.png')
bpy.ops.render.render(write_still=True)
