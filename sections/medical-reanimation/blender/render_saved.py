"""Fresh-process reopen/render proof. Does not run the authoring script."""
import bpy,sys,argparse,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--revision',required=True)
ap.add_argument('--cameras',default='all')
ap.add_argument('--samples',type=int,default=64)
ap.add_argument('--width',type=int,default=1440)
ap.add_argument('--cpu',action='store_true')
ap.add_argument('--final',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
scene=bpy.context.scene
CAMERAS=json.loads((ROOT/'production/cameras.json').read_text())
out=ROOT/'production/renders'/('final' if args.final else 'review')/args.revision
out.mkdir(parents=True,exist_ok=True)
saved_checks={}
for n,(loc,target,lens) in CAMERAS.items():
    ob=bpy.data.objects.get(n)
    wanted=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y')
    saved_checks[n]=bool(ob and (ob.location-Vector(loc)).length<1e-5 and abs(ob.data.lens-lens)<1e-5 and abs(abs(ob.rotation_euler.to_quaternion().dot(wanted))-1)<1e-5)
scene.render.resolution_x=args.width;scene.render.resolution_y=round(args.width*.625)
scene.render.resolution_percentage=100;scene.cycles.samples=args.samples;scene.cycles.seed=841
scene.cycles.use_denoising=True;scene.cycles.device='CPU'
if not args.cpu:
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='HIP';p.get_devices()
    for d in p.devices:d.use=d.type=='HIP'
    if any(d.use for d in p.devices):scene.cycles.device='GPU'
exec(compile((ROOT/'blender/validate.py').read_text(),str(ROOT/'blender/validate.py'),'exec'))
manifest={'opened_blend':Path(bpy.data.filepath).name,'saved_scene_revision':scene['revision'],'render_revision':args.revision,
          'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'fresh_process':True,'authoring_script_executed':False,'fixed_camera_checks':saved_checks,'device':scene.cycles.device,
          'samples':args.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y],
          'validation_pass':report['pass'],'renders':[]}
names=([n for n in CAMERAS if n.startswith(tuple('C%02d'%i for i in range(1,11)))] if args.cameras=='all' else args.cameras.split(','))
if not all(saved_checks.values()):raise RuntimeError('Saved camera differs from committed camera contract')
for n in names:
    scene.camera=bpy.data.objects[n];scene.render.filepath=str(out/(n+'.png'));bpy.ops.render.render(write_still=True)
    manifest['renders'].append({'camera':n,'file':n+'.png','sha256':hashlib.sha256((out/(n+'.png')).read_bytes()).hexdigest()})
(out/'cold-start.json').write_text(json.dumps(manifest,indent=2))
print('MEDICAL_COLD_RENDER_COMPLETE',json.dumps(manifest),flush=True)
