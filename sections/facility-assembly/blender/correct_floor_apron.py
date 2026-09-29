"""Bounded pixel-review correction: varied apron faces and small seated relief."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/floor-finish';src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((OUT/'verification.json').read_text());before=sha(src);assert before==r['saved_sha256']
assert not r.get('apron_corrected'),'Correction already applied'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();coll=bpy.data.collections['ART | Dimensional floor finish']
def bounds(o):
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector(tuple(min(v[i] for v in bb) for i in range(3))),Vector(tuple(max(v[i] for v in bb) for i in range(3)))
slabs=sorted([o for o in coll.objects if o.name.startswith('FLR | Refinery dimensional slab')],key=lambda o:o.name)
for i,o in enumerate(slabs):
 lo,hi=bounds(o);lift=(.004,.007,.005,.006)[i%4];variant=(1,2,0,3,2,1,3)[i%7];o.data.materials[0]=bpy.data.materials['FLR | Worn mineral face '+str(variant)];o.data.materials[3]=bpy.data.materials['FLR | Absorbed moisture '+str(variant)];o.location.z+=lift
 # Water stays at the same depth in its own slab depression.
 for p in coll.objects:
  if not p.name.startswith('FLR | Water in shallow slab depression'):continue
  a,b=bounds(p);c=(a+b)/2
  if lo.x<c.x<hi.x and lo.y<c.y<hi.y:p.location.z+=lift
 for mark in s.objects:
  if not mark.name.startswith('RFX | Worn apron boundary dash'):continue
  a,b=bounds(mark);c=(a+b)/2
  if lo.x<c.x<hi.x and lo.y<c.y<hi.y:
   mark.location.z+=lift
   if mark.name not in r['changed']:r['changed'].append(mark.name)
 for p in r['panels']:
  if p['name']==o.name:p['lo'][2]+=lift;p['hi'][2]+=lift;p['settlement_lift_m']=lift;p['face_variant']=variant
bpy.context.view_layer.update();assert sha(src)==before
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH']
bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False);r.update(saved_sha256=sha(src),apron_corrected=True,visual_correction='Apron material selection no longer aliases every fourth index; slab tops lifted 4–7 mm, markings and pooled water follow their slab. Sparse off-centre puddles replace the evenly repeated first preview.');(OUT/'verification.json').write_text(json.dumps(r,indent=2));print('FLOOR_APRON_CORRECTED',flush=True)
for file,cam in [('refinery.png','RFX CAMERA | 06_WALK_ENTRY'),('courtyard.png','JNT CAMERA | COURTYARD SOUTH')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);print('FLOOR_VIEW',file,flush=True)
