"""Fresh-process readback and CPU repeat from the saved courtyard revision."""
import bpy, bmesh, ast, json, hashlib, ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/courtyard'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'build-verification.json').read_text());source=Path(bpy.data.filepath)
assert sha(source)==report['saved_sha256'],'Different revision than build evidence'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
# Reuse only the pure fingerprint function, without executing the build script.
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text())
fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fingerprint')
exec(compile(ast.Module(body=[fun],type_ignores=[]),'<fingerprint>','exec'))
objects={o.name_full:o for o in s.objects}
changed=[n for n,h in report['protected_fingerprints'].items() if n not in objects or fingerprint(objects[n])!=h]
assert not changed,changed
missing_libraries=[p for p,h in report['libraries'].items() if not Path(p).exists() or sha(p)!=h]
assert not missing_libraries,missing_libraries
missing_images=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file and im.filepath:
        p=Path(bpy.path.abspath(im.filepath,library=im.library))
        if not p.exists():missing_images.append(dict(name=im.name,path=str(p)))
for r in report['rocks']:
    o=bpy.data.objects[r['name']];src=bpy.data.objects[r['source']]
    assert o.data==src.data,'Boulder no longer shares original source mesh'
dg=bpy.context.evaluated_depsgraph_get();floor=[]
obstacles=[]
for o in bpy.data.collections['ART | Courtyard mine-to-refinery'].objects:
    if o.type!='MESH' or o.get('terrain_open_surface') or o.get('surface_decal'):continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)]
    if hi[2]>.35:obstacles.append((o,lo,hi))
route_blockers=[]
for p in report['route_samples']:
    x,y=p['xy'];hit,co,no,face,o,mat=s.ray_cast(dg,Vector((x,y,.34)),Vector((0,0,-1)),distance=.85)
    floor.append(dict(route=p['route'],xy=[x,y],floor=round(co.z,5) if hit else None,object=o.name if hit else None))
    blocked=[ob.name for ob,lo,hi in obstacles if lo[0]-.45<x<hi[0]+.45 and lo[1]-.45<y<hi[1]+.45 and lo[2]<2]
    if blocked:route_blockers.append(dict(route=p['route'],xy=[x,y],objects=blocked))
floor_failures=[p for p in floor if p['floor'] is None or p['floor']<-.35]
floor_steps=[]
for a,b in zip(floor,floor[1:]):
    if a['route']==b['route'] and a['floor'] is not None and b['floor'] is not None:
        floor_steps.append(dict(route=a['route'],start=a['xy'],end=b['xy'],height_change=round(abs(a['floor']-b['floor']),5)))
settings=dict(engine=s.render.engine,device=s.cycles.device,width=s.render.resolution_x,height=s.render.resolution_y,threads=s.render.threads,samples=s.cycles.samples,seed=s.cycles.seed,denoising_use_gpu=s.cycles.denoising_use_gpu)
assert settings==dict(engine='CYCLES',device='CPU',width=1280,height=720,threads=1,samples=12,seed=73,denoising_use_gpu=False),settings
result=dict(source=str(source),source_sha256=sha(source),protected_changes=changed,protected_objects_checked=len(report['protected_fingerprints']),missing_or_changed_libraries=missing_libraries,missing_images=missing_images,boulder_source_meshes_verified=len(report['rocks']),floor_samples=floor,floor_failures=floor_failures,route_blockers=route_blockers,settings=settings,cold_render_pending=True)
result['floor_height_changes']=floor_steps
result['maximum_sampled_floor_height_change']=max((v['height_change'] for v in floor_steps),default=0)
result['floor_continuity_note']='Measured 0.5 m sample spacing; shallow service curb is intentionally retained. Runtime step height, collision and navigation are not verified by this Blender audit.'
mesh_errors=[];surface_count=0
for o in bpy.data.collections['ART | Courtyard mine-to-refinery'].objects:
    if o.type!='MESH':continue
    if o.get('surface_decal') or o.get('terrain_open_surface'):
        surface_count+=1
        continue
    if o.name.startswith(('CY | Existing boulder','CY | Edge fieldstone')):continue
    bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free()
    if bad or deg:mesh_errors.append((o.name,bad,deg))
result['manufactured_mesh_errors']=mesh_errors;result['intentional_open_surfaces']=surface_count
(OUT/'cold-open.json').write_text(json.dumps(result,indent=2))
print('COLD_READBACK',len(changed),len(missing_images),len(floor_failures),flush=True)
assert not floor_failures,floor_failures
assert not route_blockers,route_blockers
assert not mesh_errors,mesh_errors
manifest=json.loads((OUT/'manifest.json').read_text());view=next(v for v in manifest['views'] if v['name']=='01_CONCEPT')
s.cycles.samples=view.get('samples',12);result['repeat_render_samples']=s.cycles.samples
s.camera=bpy.data.objects['CY CAMERA | 01_CONCEPT'];s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
def pixels(path):
    im=bpy.data.images.load(str(path),check_existing=False)
    a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(-1,4);bpy.data.images.remove(im);return a
a=pixels(OUT/'01_CONCEPT.png');b=pixels(OUT/'cold-repeat.png');delta=np.abs(a-b)
result.update(cold_render_pending=False,max_channel_difference=float(delta.max()),mean_channel_difference=float(delta.mean()),changed_pixels=int(np.any(delta>0,axis=1).sum()),source_unchanged=sha(source)==report['saved_sha256'])
(OUT/'cold-open.json').write_text(json.dumps(result,indent=2));print('COLD_COMPLETE',result['changed_pixels'],flush=True)
