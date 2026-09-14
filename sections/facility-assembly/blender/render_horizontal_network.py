import bpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network';REV=os.environ.get('NETWORK_REVISION','R02')
bpy.ops.wm.open_mainfile(filepath=str(OUT/f'review-{REV}.blend'),load_ui=False)
from mathutils import Vector
cam=bpy.data.objects['PROMENADE'];cam.location=(-35,28,1.7);cam.rotation_euler=(Vector((-10,28,1.7))-cam.location).to_track_quat('-Z','Y').to_euler()
for name,loc,target in [('WASTE',(49,8,1.7),(49,17,1.7)),('COMPLIANCE',(-41,21,1.7),(-41,29,1.7)),('LOWER',(20,-4,1.7),(40,-4,1.7)),('MINE',(-6,-29,1.7),(0,-26,1.7))]:
 cam=bpy.data.objects[name];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='GPU';p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.refresh_devices()
for d in p.devices:d.use=d.type=='HIP'
if hasattr(p,'use_hiprt'):p.use_hiprt=True
s.cycles.samples=24;s.cycles.adaptive_threshold=.06;s.cycles.use_denoising=True;s.render.use_persistent_data=False
out=OUT/f'renders-{REV}';out.mkdir(exist_ok=True)
views=os.environ.get('NETWORK_VIEWS','TOP,PROCESS,TRANSFER,POWER,PROMENADE,COOLING,WASTE,COMPLIANCE,LOWER,MINE').split(',')
for name in views:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED',REV,name,flush=True)
