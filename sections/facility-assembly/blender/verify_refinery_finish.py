"""Checkpoint comparison, fresh main-file readback and CPU-only final evidence."""
import bpy,bmesh,ast,json,hashlib,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-finish';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'verification.json').read_text());assert sha(bpy.data.filepath)==report['before_sha256'],'Launch against finish checkpoint'
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text())
for name in ('fingerprint','material_sig'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
protected={o.name_full:fingerprint(o) for o in bpy.context.scene.objects if not o.name.startswith('RFX |')}
shared={m.name_full:material_sig(m) for m in bpy.data.materials if not m.name.startswith(('RFX |','RFS |'))}
main=Path(bpy.data.filepath).with_name('facility_environment.blend');assert sha(main)==report['saved_sha256']
print('FINISH_BASELINE_CHECKED',len(protected),len(shared),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(main));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
objects={o.name_full:o for o in s.objects};changed=[n for n,h in protected.items() if n not in objects or fingerprint(objects[n])!=h];assert not changed,changed
mats={m.name_full:m for m in bpy.data.materials};changed_mats=[n for n,h in shared.items() if n not in mats or material_sig(mats[n])!=h];assert not changed_mats,changed_mats
badlibs=[p for p,h in report['libraries'].items() if not Path(p).exists() or sha(p)!=h];assert not badlibs,badlibs
missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()];assert not missing,missing
mesh_errors=[];closed_meshes=0;surface_overlays=0
for o in bpy.data.collections['ART | Refinery authored surface finish'].objects:
 if o.type!='MESH':continue
 if o.get('intentional_surface_overlay'):surface_overlays+=1;continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces):mesh_errors.append(o.name)
 bm.free();closed_meshes+=1
assert not mesh_errors,mesh_errors
dg=bpy.context.evaluated_depsgraph_get();floors=[]
for q in report['route_samples']:
 x,y=q['xy'];p=Vector((x,y,.27));found=None
 for i in range(16):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector((0,0,-1)),distance=1)
  if not hit:break
  if 'fog' not in o.name.lower() and 'haze' not in o.name.lower() and n.z>.5:found=dict(route=q['route'],xy=[x,y],z=co.z,object=o.name);break
  p=co-Vector((0,0,.002))
 floors.append(found or dict(route=q['route'],xy=[x,y],gap=True))
gaps=[q for q in floors if q.get('gap')];assert not gaps,gaps
# Check only newly authored non-floor geometry against sampled walk envelopes.
verts=[];faces=[]
for o in bpy.data.collections['ART | Refinery authored surface finish'].objects:
 if o.type!='MESH':continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box]
 if max(v.z for v in bb)<.20:continue
 off=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in o.data.polygons])
bvh=BVHTree.FromPolygons(verts,faces);blockers=[]
for q in floors:
 x,y=q['xy']
 for z in (.5,1.1,1.75):
  p=Vector((x,y,q['z']+z));nearest=bvh.find_nearest(p)
  if nearest[0] is not None and nearest[3]<.38:blockers.append(dict(xy=[x,y],z=z,distance=nearest[3]))
assert not blockers,blockers
audit=dict(source=str(main),source_sha256=sha(main),protected_objects=len(protected),protected_changes=changed,shared_materials=len(shared),shared_material_changes=changed_mats,library_changes=badlibs,missing_images=missing,floor_samples=floors,floor_gaps=gaps,new_route_blockers=blockers,closed_manufactured_meshes=closed_meshes,mesh_errors=mesh_errors,intentional_surface_overlays=surface_overlays,runtime_collision_navigation='not tested',node_drawn_layout='unverified: headless')
(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2));print('FINISH_COLD_VERIFIED',len(floors),flush=True)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.cycles.samples=12;s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
def pixels(p):
 im=bpy.data.images.load(str(p),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(-1,4)
d=np.abs(pixels(OUT/'entry.png')-pixels(OUT/'cold-repeat.png'));audit.update(changed_pixels=int(np.any(d>0,axis=1).sum()),max_channel_difference=float(d.max()),mean_channel_difference=float(d.mean()));(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2))
manifest=dict(source=str(main),source_sha256=sha(main),settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],denoiser='CPU OIDN',seed=73),views=[],complete=False)
for name,file,samples in [('06_WALK_ENTRY','entry.png',12),('05_WALK_MINE','mine-approach.png',8)]:
 cam=bpy.data.objects['RFX CAMERA | '+name];manifest['views'].append(dict(path=str(OUT/file),sha256=sha(OUT/file),camera=cam.name,position=list(cam.location),rotation=list(cam.rotation_euler),lens_mm=cam.data.lens,samples=samples))
for name in ('01_SW','02_SE','03_NE','04_NW'):
 s.camera=bpy.data.objects['RFX CAMERA | '+name];s.cycles.samples=4;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 manifest['views'].append(dict(path=s.render.filepath,sha256=sha(s.render.filepath),camera=s.camera.name,position=list(s.camera.location),rotation=list(s.camera.rotation_euler),lens_mm=s.camera.data.lens,samples=4));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINISH_VIEW',name,flush=True)
assert sha(main)==report['saved_sha256'];manifest.update(complete=True,source_unchanged=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINISH_EVIDENCE_COMPLETE',flush=True)
