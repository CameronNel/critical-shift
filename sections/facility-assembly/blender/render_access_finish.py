import bpy,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish/renders-access';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A09_access_finish.blend'),load_ui=False)
# Render the context display meshes; new passage detail retains its authored materials.
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE']:
 c=bpy.data.collections[n];c.hide_render=False;c.hide_viewport=False
 for o in c.objects:
  if 'GREYBOX' not in o.name:o.hide_render=False
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 c=bpy.data.collections[n];c.hide_render=True;c.hide_viewport=True
bpy.data.collections['13_FINISHED_ACCESS_SCENERY'].hide_viewport=False
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='GPU';p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.refresh_devices()
for d in p.devices:d.use=d.type=='HIP'
if hasattr(p,'use_hiprt'):p.use_hiprt=True
s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.05;s.render.use_persistent_data=False
s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
cam=bpy.data.objects.new('ACCESS_FINISH_CAMERA',bpy.data.cameras.new('ACCESS_FINISH_CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.lens=23
views=[('PASSAGE',(35.4,44.9,-4.3),(48.2,44.9,-4.6)),('REVERSE',(45.2,44.9,-4.3),(34,44.9,-4.5)),('STAIR',(31.1,45.9,1.7),(31.1,40,-2)),('LIFT',(34,36,1.7),(30,34.8,1))]
for name,pos,target in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED_ACCESS',name,flush=True)
