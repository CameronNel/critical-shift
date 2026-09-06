"""Run in a fresh Blender process after building and saving the level.
Example:
 blender --background output/CriticalShift_Gullet.blend --python tools/cold_start_check.py -- --render entry,main_route
This checker validates reopening, packaged images, cameras and renderability.
"""
from pathlib import Path
import argparse,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import build_mine as B
p=argparse.ArgumentParser();p.add_argument('--render',default='entry,main_route');p.add_argument('--output',type=Path,default=ROOT/'output'/'cold_start');p.add_argument('--device',choices=['cpu','auto'],default='auto')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
a.output.mkdir(parents=True,exist_ok=True)
scene=next((s for s in bpy.data.scenes if s.get('csm_generator')),None)
if scene is None:raise RuntimeError('Open the generated .blend on the Blender command line before this script.')
if bpy.context.window:bpy.context.window.scene=scene
issues=[];meshes=[o for o in scene.objects if o.type=='MESH'];ids=[o.get('csm_id') for o in meshes]
if len(ids)!=len(set(ids)):issues.append('Duplicate semantic mesh IDs')
expected={'entry','bay_overview','dispatch','charge_issue','main_route','reverse_route','dry_cut','sump','wet_cut','collapse'}
keys={o.get('csm_camera_key') for o in scene.objects if o.type=='CAMERA'}
if not expected.issubset(keys):issues.append('Missing review cameras: '+str(expected-keys))
images=[]
for image in bpy.data.images:
 if image.type=='RENDER_RESULT':continue
 if image.source=='FILE':
  okay=bool(image.packed_file) or Path(bpy.path.abspath(image.filepath)).is_file();images.append({'image':image.name,'packed':bool(image.packed_file),'available':okay})
  if not okay:issues.append('Missing image '+image.name)
for obj in meshes:
 if not len(obj.data.polygons):issues.append('Empty mesh '+obj.name)
 if len(obj.data.uv_layers)==0:issues.append('No UV map '+obj.name)
 if not obj.material_slots:issues.append('No material '+obj.name)
B.install_api(scene);B.register_controls();B.apply_visibility(scene)
report={'status':'FAIL' if issues else 'PASS','issues':issues,'executed_in_blender':True,'version':bpy.app.version_string,'opened_file':bpy.data.filepath,'mesh_objects':len(meshes),'images':images,'rendered_cameras':[],'pixel_review':'NOT AUTOMATICALLY PASSED','runtime_validation':'NOT PERFORMED'}
try:
 if not issues and a.render:
  B.configure_device(bpy,scene,a.device);scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.cycles.samples=64;report['rendered_cameras']=B.render_cameras(scene,a.output,a.render)
except Exception as exc:
 report['status']='FAIL';report['issues'].append(repr(exc));raise
finally:(a.output/'cold_start_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if issues:raise RuntimeError('Cold-start checks failed; inspect cold_start_report.json')
