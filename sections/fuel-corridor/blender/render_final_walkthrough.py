"""Supplementary player-eye views of a saved file; temporary camera, no save.

Launch only through shared GPU gate. These support authored-room inspection,
not a game engine controller, collision or timing claim.
"""
import bpy,json,hashlib,sys,datetime
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;path=Path(bpy.data.filepath);before=hashlib.sha256(path.read_bytes()).hexdigest()
assert bpy.app.background and s.get('stage')=='full'
views=[
 ('W01_REFINERY_APPROACH',(0,3.6,1.7),(0,0,1.7)),
 ('W02_SERVICE_ENTRY',(0,9.5,1.7),(0,16,1.7)),
 ('W03_PLANT_APPROACH',(-1,17.4,1.7),(-5.4,17.4,1.6)),
 ('W04_PLANT_RETURN',(-4,17.4,1.7),(0,17.4,1.6)),
 ('W05_CLEAN_APPROACH',(6.6,18.5,1.7),(6.6,21,1.7)),
 ('W06_WASTE_APPROACH',(12.8,16,1.7),(16.4,16,1.7)),
 ('W07_DELIVERY_RETURN',(14.2,20,1.7),(14.2,13.4,1.6)),
 ('W08_EAST_TURN_RETURN',(14.2,10,1.7),(8.5,10,1.6)),
 ('W09_BENCH_ACCESS',(0,10.6,1.7),(-2.2,10.6,1.3)),
 ('W10_GATE_APPROACH',(3,10,1.7),(6.35,10,1.85)),
 ('W11_CARRIER_ACCESS',(4,12,1.7),(2.6,12.3,.8)),
 ('W12_CLEAN_TURN',(1,19.2,1.7),(6.6,20,1.6)),
]
d=bpy.data.cameras.new('Walkthrough_evidence_only');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam)
d.lens=22;d.clip_start=.04;s.camera=cam
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
s.cycles.samples=32;s.cycles.use_denoising=True;s.render.use_persistent_data=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.get_devices()
for dev in p.devices:dev.use=dev.type=='HIP'
assert any(dev.use for dev in p.devices);s.cycles.device='GPU'
report={'blend':str(path),'blend_sha256_before':before,'revision':s.get('revision'),'eye_height_m':1.7,'resolution':[1200,800],'samples':32,'lens_mm':22,'renders':[],'scene_saved':False,'scope':'Fixed player-eye approach observations, not continuous engine locomotion or runtime validation.'}
for name,loc,target in views:
    cam.location=loc;cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    report['renders'].append({'view':name,'position':loc,'target':target,'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()})
    (out/'manifest-in-progress.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
report['blend_sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest();assert report['blend_sha256_after']==before
report['complete']=True;(out/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('WALKTHROUGH_COMPLETE',len(views))
