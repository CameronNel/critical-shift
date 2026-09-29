"""Fresh-open preservation, measured reveals, route checks and CPU evidence."""
import bpy,bmesh,ast,json,hashlib,ctypes,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/exterior-joints';src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((OUT/'verification.json').read_text());assert sha(src)==r['saved_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for fn in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
objects={o.name_full:o for o in s.objects};allowed=set(r['removed'])|set(r['changed']);protected={n:h for n,h in r['original_objects'].items() if n not in allowed};bad=[n for n,h in protected.items() if n not in objects or fingerprint(objects[n])!=h];assert not bad,bad
assert all(n not in objects for n in r['removed'])
mats={m.name_full:m for m in bpy.data.materials};badm=[n for n,h in r['materials'].items() if n not in mats or material_sig(mats[n])!=h];assert not badm,badm
badlibs=[p for p,h in r['libraries'].items() if sha(p)!=h];assert not badlibs,badlibs
missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()];assert not missing,missing
coll=bpy.data.collections['ART | Exterior construction joints'];check=set(coll.objects)|{objects[n] for n in r['changed'] if n in objects};errors=[];mesh_count=0
for o in check:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces) or abs(bm.calc_volume())<1e-12:errors.append(o.name)
 bm.free();mesh_count+=1
assert not errors,errors
def bvh_for(items):
 vs=[];fs=[]
 for o in items:
  if o.type!='MESH':continue
  off=len(vs);vs.extend([o.matrix_world@v.co for v in o.data.vertices]);fs.extend([tuple(off+i for i in p.vertices) for p in o.data.polygons])
 return BVHTree.FromPolygons(vs,fs)
panel_bvh=bvh_for([o for o in coll.objects if o.name.startswith(('RFX | Solid mineral facade panel','RFX | Recessed panel joint bedding'))])
def P(side,u,d,z):return {'W':(-10.87-d,u,z),'E':(2.72+d,u,z),'S':(u,-24.5-d,z),'N':(u,-8.7+d,z)}[side]
measures=[]
for j in [q for q in r['joints'] if q['type']=='facade' and q['z']<1.1]:
 side,u=j['side'],j['u'];direction=(Vector(P(side,u,0,0))-Vector(P(side,u,1,0))).normalized();face=panel_bvh.ray_cast(Vector(P(side,u,1,j['z'])),direction,2);gap=panel_bvh.ray_cast(Vector(P(side,u,1,1.4555)),direction,2)
 assert face[0] is not None and gap[0] is not None,(side,u)
 recess=gap[3]-face[3];assert .035<recess<.048,(side,u,recess);measures.append(dict(side=side,u=u,measured_recess_m=recess))
# Walking support: use a small foot footprint, so a legitimate narrow drain slot
# is not confused with a missing walkway. Keep fog out of all support tests.
routes=json.loads((ROOT/'runtime/out/environment/refinery-build/build-verification.json').read_text())['route_samples']+json.loads((ROOT/'runtime/out/environment/courtyard/build-verification.json').read_text())['route_samples'];dg=bpy.context.evaluated_depsgraph_get();floors=[];gaps=[]
def floor(x,y):
 p=Vector((x,y,.34))
 for i in range(16):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector((0,0,-1)),distance=1.05)
  if not hit:return None
  if 'fog' not in o.name.lower() and 'haze' not in o.name.lower() and n.z>.45:return float(co.z)
  p=co-Vector((0,0,.002))
 return None
baseline=json.loads((OUT/'route-baseline.json').read_text());assert baseline['source_sha256']==r['before_sha256'];preexisting_uneven=[]
for index,q in enumerate(routes):
 x,y=q['xy'];heights=[floor(x+dx,y+dy) for dx,dy in ((0,0),(.12,0),(-.12,0),(0,.12),(0,-.12))];valid=[h for h in heights if h is not None];top=max(valid) if valid else None;support=sum(abs(h-top)<.06 for h in valid) if top is not None else 0
 row=dict(route=q['route'],xy=[x,y],floor=top,support_samples=support)
 row['heights']=heights
 if support<3:
  previous=baseline['samples'][index];assert previous['xy']==[x,y] and previous['route']==q['route']
  same=all(a is None and b is None or a is not None and b is not None and abs(a-b)<.001 for a,b in zip(heights,previous['heights']))
  if same:preexisting_uneven.append(row)
  else:gaps.append(row)
 floors.append(row)
assert not gaps,gaps
# Only new construction is checked here; pre-existing props are not new blockers.
obstacles=bvh_for([o for o in coll.objects if o.type=='MESH' and max((o.matrix_world@Vector(v)).z for v in o.bound_box)>.3]);blockers=[]
for q in floors:
 x,y=q['xy']
 for dz in (.50,1.1,1.75):
  p=Vector((x,y,q['floor']+dz));near=obstacles.find_nearest(p)
  if near[0] is not None and near[3]<.37:blockers.append(dict(xy=[x,y],height=dz,distance=near[3]))
assert not blockers,blockers
audit=dict(source_sha256=sha(src),protected_objects=len(protected),protected_changes=bad,unchanged_materials=len(r['materials']),material_changes=badm,missing_images=missing,library_changes=badlibs,closed_meshes=mesh_count,mesh_errors=errors,measured_panel_reveals=measures,route_samples=floors,route_gaps=gaps,new_blockers=blockers,runtime_collision_navigation='not tested',independent_art_review='not requested')
audit['preexisting_uneven_route_samples']=preexisting_uneven
(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2));print('JOINT_COLD_VERIFIED',len(protected),len(measures),len(floors),flush=True)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['JNT CAMERA | WALL DETAIL'];s.cycles.samples=12;s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
def pixels(p):
 im=bpy.data.images.load(str(p),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(-1,4)
d=np.abs(pixels(OUT/'wall-detail.png')-pixels(OUT/'cold-repeat.png'));audit.update(changed_pixels=int(np.any(d>0,axis=1).sum()),max_channel_difference=float(d.max()),mean_channel_difference=float(d.mean()));(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2))
manifest=dict(source=str(src),source_sha256=sha(src),settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],seed=73,denoiser='CPU OIDN'),views=[],complete=False)
def record(file,cam,samples):
 c=bpy.data.objects[cam];manifest['views'].append(dict(path=str(OUT/file),sha256=sha(OUT/file),camera=cam,position=list(c.location),rotation=list(c.rotation_euler),lens=c.data.lens,samples=samples));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
record('wall-detail.png','JNT CAMERA | WALL DETAIL',12);record('entry.png','RFX CAMERA | 06_WALK_ENTRY',8)
for file,cam in [('mine-approach.png','RFX CAMERA | 05_WALK_MINE'),('courtyard-south.png','JNT CAMERA | COURTYARD SOUTH'),('courtyard-north.png','JNT CAMERA | COURTYARD NORTH'),('overview.png','RFX CAMERA | 01_SW')]:
 s.camera=bpy.data.objects[cam];s.cycles.samples=4;s.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);record(file,cam,4);print('JOINT_VIEW',file,flush=True)
assert sha(src)==r['saved_sha256'];manifest.update(complete=True,source_unchanged=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('JOINT_EVIDENCE_COMPLETE',flush=True)
