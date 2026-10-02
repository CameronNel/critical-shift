"""Additional infrastructure closeups; never replace fixed area views or save native.

blender -b --python render_detail_proofs.py -- native.blend output [camera-list]
All camera offsets are fixed in the relevant assembly's authored coordinates.
No light, material, object visibility or frame state is altered for a closeup.
"""
import bpy,sys,os,json,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
args=sys.argv[sys.argv.index('--')+1:]
src=Path(args[0]).resolve();out=Path(args[1]).resolve();out.mkdir(parents=True,exist_ok=True)
original_sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene;sc.frame_set(1);sc.render.engine='CYCLES';sc.cycles.device='CPU'
sc.cycles.samples=int(os.environ.get('SAMPLES','32'));sc.cycles.seed=7;sc.cycles.use_denoising=True
sc.render.resolution_x,sc.render.resolution_y=map(int,os.environ.get('RES','1280x853').split('x'))
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
specs=[
 ('P01_BENCH_POWER','FC | Bench weatherproof receptacle bank',(.16,-1.20,.22),(.17,-.05,-.03),46),
 ('P02_PROCESS_JUNCTION','FC | Process distribution junction box',(-.28,-1.55,.44),(-.27,-.04,.21),40),
 ('P03_REACTOR_INTERCOM','FC | Reactor local call intercom',(.23,-1.05,.20),(0,-.04,-.06),43),
 ('P04_FLOOR_STRAINER','FC | Wet-service recessed floor strainer',(.38,.52,.83),(0,0,0),48),
]
selected=args[2].split(',') if len(args)>2 else [s[0] for s in specs]
report={'schema':'fuel-detail-view-evidence/1','scene':str(src.relative_to(ROOT)),
 'scene_sha256':original_sha,'blender':bpy.app.version_string,'engine':sc.render.engine,
 'device':sc.cycles.device,'samples':sc.cycles.samples,'seed':sc.cycles.seed,
 'denoise':sc.cycles.use_denoising,'resolution':[sc.render.resolution_x,sc.render.resolution_y],
 'view_transform':sc.view_settings.view_transform,'look':sc.view_settings.look,
 'exposure':sc.view_settings.exposure,'frame':1,
 'scope':'Additional fixed closeups only; native lighting and visibility unchanged; full area set still required.',
 'cameras':[]}
for name,owner,offset,target,lens in specs:
 if name not in selected:continue
 ob=bpy.data.objects[owner];eye=ob.matrix_world@Vector(offset);aim=ob.matrix_world@Vector(target)
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);sc.collection.objects.link(cam)
 cam.location=eye;cam.rotation_euler=(aim-eye).to_track_quat('-Z','Y').to_euler();data.lens=lens
 sc.camera=cam;png=out/(name+'.png');sc.render.filepath=str(png);bpy.ops.render.render(write_still=True)
 report['cameras'].append({'name':name,'owner':owner,'matrix_world':[list(r) for r in cam.matrix_world],
  'lens':lens,'image':png.name,'sha256':hashlib.sha256(png.read_bytes()).hexdigest()})
assert len(report['cameras'])==len(selected)
assert hashlib.sha256(src.read_bytes()).hexdigest()==original_sha
(out/'RENDER_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
print('DETAIL_PROOFS',out,len(report['cameras']),flush=True)
