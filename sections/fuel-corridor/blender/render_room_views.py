"""Read saved slice03; render presentation views without saving scene changes."""
import bpy, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
out=root/'production/renders/room-views-20260910'
out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
views=[
 ('01_southwest',(-1.82,7.38,1.85),(1.45,10.55,1.95)),
 ('02_southeast',(4.02,7.38,1.85),(.8,10.6,1.95)),
 ('03_northeast',(4.02,12.82,1.85),(.7,9.55,1.95)),
 ('04_northwest',(-1.82,12.82,1.85),(1.5,9.6,1.95)),
 ('05_overhead',(1.1,10.1,12),(1.1,10.1,0))]
d=bpy.data.cameras.new('Presentation_only');cam=bpy.data.objects.new('Presentation_only',d);s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.cycles.samples=32;s.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.get_devices()
for dev in p.devices:dev.use=dev.type=='HIP'
s.cycles.device='GPU'
for name,loc,target in views:
 cam.location=loc;cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
 d.type='PERSP';d.lens=18;d.clip_start=.04
 if name=='05_overhead':
  d.type='ORTHO';d.ortho_scale=9.7
  for obj in s.objects:
   if obj.name.startswith('Ceiling_'):obj.hide_render=True
 s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/'manifest.json').write_text(json.dumps({'source_blend':bpy.data.filepath,'saved_revision':s.get('revision'),'views':views,'note':'Presentation only. Saved blend unchanged. Overhead hides ceiling slab.'},indent=2))
