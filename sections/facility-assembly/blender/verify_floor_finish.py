"""Cold-open audit of the bounded floor pass, plus matched CPU renders."""
import bpy,bmesh,ast,json,hashlib,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/floor-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==r['saved_sha256'];s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for fn in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
objects={o.name_full:o for o in s.objects};excluded=set(r['removed'])|set(r['changed']);protected={n:h for n,h in r['original_objects'].items() if n not in excluded}
bad=[n for n,h in protected.items() if n not in objects or fingerprint(objects[n])!=h];assert not bad,bad
assert all(n not in objects for n in r['removed'])
mats={m.name_full:m for m in bpy.data.materials};retired=[];badm=[]
allowed_retirement={'RFS | Dust worn paving 0','RFS | Dust worn paving 1','RFS | Dust worn paving 3','RFS | Older concrete infill'}
inspection=json.loads((OUT/'inspection.json').read_text())
for n,h in r['materials'].items():
 if n in mats:
  if material_sig(mats[n])!=h:badm.append(n)
 elif n in allowed_retirement:
  users=[q['name'] for q in inspection['objects'] if n in q['materials']]
  assert users and all(u in r['removed'] for u in users),(n,users)
  # Protected object fingerprints already verify every surviving original mesh's
  # material-slot identities. These old floor-only materials lost their users.
  retired.append(dict(material=n,removed_users=users))
 else:badm.append(n)
assert not badm,badm
badlibs=[p for p,h in r['libraries'].items() if sha(p)!=h];assert not badlibs,badlibs
missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()];assert not missing,missing
coll=bpy.data.collections['ART | Dimensional floor finish'];errors=[];closed=0;water=0
for o in coll.objects:
 if o.type!='MESH':continue
 if o.get('intentional_surface_overlay'):water+=1;continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces) or abs(bm.calc_volume())<1e-12:errors.append(o.name)
 bm.free();closed+=1
assert not errors,errors
frames=[]
for name,h in r['new_materials'].items():
 m=bpy.data.materials[name];assert material_sig(m)==h
 ns=m.node_tree.nodes;loose=[n.name for n in ns if n.type!='FRAME' and not n.parent];counts={f.name:sum(n.parent==f for n in ns) for f in ns if f.type=='FRAME'}
 assert not loose and all(4<=c<=19 for c in counts.values()),(name,loose,counts)
 frames.append(dict(material=name,unframed=loose,counts=counts))
# The preceding approved revision provides an exact baseline of the same routes.
baseline=json.loads((ROOT/'runtime/out/environment/exterior-joints/cold-open.json').read_text());assert baseline['source_sha256']==r['before_sha256'];dg=bpy.context.evaluated_depsgraph_get()
def floor(x,y):
 p=Vector((x,y,.34))
 for i in range(16):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector((0,0,-1)),distance=1.05)
  if not hit:return None
  if 'fog' not in o.name.lower() and 'haze' not in o.name.lower() and n.z>.45:return float(co.z)
  p=co-Vector((0,0,.002))
 return None
routes=[];fail=[];max_rise=0;max_drop=0
for q in baseline['route_samples']:
 x,y=q['xy'];heights=[floor(x+dx,y+dy) for dx,dy in ((0,0),(.12,0),(-.12,0),(0,.12),(0,-.12))]
 for a,b in zip(heights,q['heights']):
  if b is not None and (a is None or a-b>.008 or b-a>.040):fail.append(dict(xy=[x,y],before=b,after=a))
  if a is not None and b is not None:max_rise=max(max_rise,a-b);max_drop=max(max_drop,b-a)
 routes.append(dict(route=q['route'],xy=[x,y],heights=heights))
assert not fail,fail
assert all(max((o.matrix_world@Vector(v)).z for v in o.bound_box)<.17 for o in coll.objects if o.type=='MESH'),'New tall obstacle in floor collection'
audit=dict(source_sha256=sha(SRC),protected_objects=len(protected),protected_changes=bad,unchanged_materials=len(r['materials'])-len(retired),retired_unused_floor_materials=retired,material_changes=badm,library_changes=badlibs,missing_images=missing,closed_meshes=closed,water_surfaces=water,mesh_errors=errors,node_frames=frames,node_drawn_bounds='unverified headless; existing four-node layout copied without changes',route_samples=routes,route_failures=fail,maximum_route_rise_m=max_rise,maximum_route_drop_m=max_drop,runtime_collision_navigation_performance='not tested')
(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2));print('FLOOR_COLD_VERIFIED',len(protected),len(routes),flush=True)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH'];s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
def pixels(p):
 im=bpy.data.images.load(str(p),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(-1,4)
d=np.abs(pixels(OUT/'courtyard.png')-pixels(OUT/'cold-repeat.png'));audit.update(changed_pixels=int(np.any(d>0,axis=1).sum()),maximum_channel_difference=float(d.max()));(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2))
manifest=dict(source=str(SRC),source_sha256=sha(SRC),settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],seed=73,denoiser='CPU OIDN'),views=[],complete=False)
def record(file,cam,samples):
 c=bpy.data.objects[cam];manifest['views'].append(dict(path=str(OUT/file),sha256=sha(OUT/file),camera=cam,position=list(c.location),rotation=list(c.rotation_euler),lens=c.data.lens,samples=samples))
record('courtyard.png','JNT CAMERA | COURTYARD SOUTH',8);record('refinery.png','RFX CAMERA | 06_WALK_ENTRY',8)
s.camera=bpy.data.objects['JNT CAMERA | COURTYARD NORTH'];s.cycles.samples=4;s.render.filepath=str(OUT/'courtyard-north.png');bpy.ops.render.render(write_still=True);record('courtyard-north.png','JNT CAMERA | COURTYARD NORTH',4)
assert sha(SRC)==r['saved_sha256'];manifest.update(complete=True,source_unchanged=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FLOOR_EVIDENCE_COMPLETE',flush=True)
