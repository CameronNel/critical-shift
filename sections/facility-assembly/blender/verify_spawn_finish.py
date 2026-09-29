"""Cold-read additive scope, routes and dependencies before promotion."""
import bpy,bmesh,json,hashlib,ctypes,ast,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath);MAIN=SRC.with_name('facility_environment.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();start_sha=sha(SRC)
r=json.loads((OUT/'construction.json').read_text());s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for fname in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
obmap={o.name_full:o for o in s.objects};mmap={m.name_full:m for m in bpy.data.materials}
changed=[n for n,h in r['original'].items() if n not in obmap or fingerprint(obmap[n])!=h]
mat_changed=[n for n,h in r['materials'].items() if n not in mmap or material_sig(mmap[n])!=h]
libs_changed=[p for p,h in r['libraries'].items() if not Path(p).exists() or sha(p)!=h]
assert not changed and not mat_changed and not libs_changed,(changed,mat_changed,libs_changed)
coll=bpy.data.collections['ART | Spawn and medical courtyard'];bad=[];zero=[];obstacles=[];floors=[]
for o in coll.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=np.min(np.asarray(pts),axis=0);hi=np.max(np.asarray(pts),axis=0)
 if hi[2]>.12 and lo[2]<1.85:obstacles.append((o.name,lo,hi))
 if o.name.startswith('SY | Dimensional courtyard slab'):floors.append((o.name,lo,hi))
 if o.name.startswith('SY | Cliff-foot'):continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces):bad.append(o.name)
 if abs(bm.calc_volume())<1e-10:zero.append(o.name)
 bm.free()
assert not bad and not zero,(bad,zero)
routes=[('entry-to-medical',[(-28,13.8),(-28,22),(-18,25),(-18,30.65)]),('cross-yard',[(-34,21),(-11,21)]),('spawn-east',[(-17.2,8.5),(-17.2,13.8),(-16.4,18),(-16.4,25)])]
samples=[];blockers=[]
for name,path in routes:
 for a,b in zip(path,path[1:]):
  a,b=np.array(a),np.array(b);steps=int(np.linalg.norm(b-a)/.25)+1
  for t in np.linspace(0,1,steps):
   p=a+(b-a)*t;samples.append([name,*map(float,p)])
   for on,lo,hi in obstacles:
    near=np.maximum(lo[:2],np.minimum(hi[:2],p))
    if np.linalg.norm(p-near)<.32:blockers.append(dict(route=name,xy=list(p),object=on))
assert not blockers,blockers[:12]
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.filepath and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()]
assert not missing,missing
report=dict(source=str(SRC),sha256=start_sha,protected_objects=len(r['original']),protected_materials=len(r['materials']),protected_libraries=len(r['libraries']),changed_original_objects=changed,changed_original_materials=mat_changed,changed_libraries=libs_changed,new_mesh_manifold_failures=bad,new_mesh_zero_volume=zero,route_samples=len(samples),route_radius=.32,route_headroom=1.85,new_route_blockers=blockers,route_method='Conservative world AABB overlap against new geometry only; retained baseline circulation not recertified',missing_images=missing,floor=r.get('floor'),node_layout='No original graphs edited; copies of approved paving graphs use a new packed mask. Headless canvas bounds/wire geometry remain unverified.',complete=True,runtime_verified=False)
if '--promote' in sys.argv:
 assert r['complete'] and start_sha==r['candidate_sha256']
 assert sha(MAIN)==r['before_sha256'],'Main changed concurrently'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MAIN));report['source']=str(MAIN);report['sha256']=sha(MAIN);report['promoted']=True
(OUT/('cold-open.json' if '--cold' in sys.argv else 'verification.json')).write_text(json.dumps(report,indent=2));print('SPAWN_VERIFIED',report['sha256'],len(samples),flush=True)
