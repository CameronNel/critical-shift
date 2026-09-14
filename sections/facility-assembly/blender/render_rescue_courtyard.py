import bpy,os,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/rescue-courtyard';REV=os.environ.get('COURTYARD_REVISION','B01')
source=OUT/f'review-{REV}.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
if REV.startswith('B'):
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True
else:
 scene.render.engine='CYCLES';scene.cycles.device='GPU'
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.refresh_devices()
 for d in p.devices:d.use=d.type=='HIP'
 if hasattr(p,'use_hiprt'):p.use_hiprt=True
 scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.05;scene.render.use_persistent_data=False
dest=OUT/f'renders-{REV}';dest.mkdir(exist_ok=True)
for name in ['TOP','COURT','EYE']:
 scene.camera=bpy.data.objects[name];scene.render.filepath=str(dest/f'{name}.png');bpy.ops.render.render(write_still=True);print('COURTYARD_RENDER',REV,name,flush=True)

