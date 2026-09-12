"""Render fixed cameras from an existing save; no scene save or geometry mutation.

Always launch through run_saved.ps1 / the shared facility GPU gate.
"""
import argparse, bpy, datetime, hashlib, json, os, sys
from pathlib import Path

root=Path(os.environ['FUEL_CORRIDOR_ROOT'])
p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--cameras',default='all');p.add_argument('--require-full',action='store_true')
p.add_argument('--preview',action='store_true',help='Temporary 960x640 / 16-sample correction check, not final evidence')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene
assert bpy.app.background and bpy.data.filepath,'Fresh background process must open a saved scene'
assert not a.require_full or s.get('stage')=='full','Final cold evidence requires full scene'
path=Path(bpy.data.filepath);before=hashlib.sha256(path.read_bytes()).hexdigest()
names=[c[0] for c in json.loads(s['fixed_camera_spec'])] if a.cameras=='all' else a.cameras.split(',')
assert all(bpy.data.objects.get(n) and bpy.data.objects[n].type=='CAMERA' for n in names)
assert s.render.resolution_x==1440 and s.render.resolution_y==960 and s.cycles.samples==32
if a.preview:s.render.resolution_x=960;s.render.resolution_y=640;s.cycles.samples=16
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='HIP';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='HIP'
assert any(device.use for device in prefs.devices),'No HIP render device enabled'
s.cycles.device='GPU'
s.render.use_persistent_data=True
a.out.mkdir(parents=True,exist_ok=True)
report={'utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blend':str(path),'blend_sha256_before':before,'revision':s.get('revision'),'stage':s.get('stage'),'fresh_background_process':True,'scene_saved':False,'renders':[]}
report['preview']=a.preview;report['resolution']=[s.render.resolution_x,s.render.resolution_y];report['samples']=s.cycles.samples
for name in names:
    camera=bpy.data.objects[name];s.camera=camera;output=a.out/(name+'.png');s.render.filepath=str(output)
    bpy.ops.render.render(write_still=True)
    report['renders'].append({'camera':name,'position':list(camera.location),'lens_mm':camera.data.lens,'image':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
report['blend_sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest()
report['saved_file_unchanged']=report['blend_sha256_after']==before
report['utc_completed']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(a.out/'cold_render_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
assert report['saved_file_unchanged']
print('FUEL_SAVED_RENDER_COMPLETE',len(names),str(a.out),flush=True)
