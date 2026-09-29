"""Close visible duct elbow gaps; edits only this pass's owned duct geometry."""
import bpy,bmesh,ast,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-build';SRC=Path(bpy.data.filepath)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'build-verification.json').read_text());initial=sha(SRC);assert initial==report['saved_sha256']
s=bpy.context.scene;coll=bpy.data.collections['ART | Refinery exterior process systems']
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text())
for name in ('mesh','box','beam'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<helper>','exec'))
steel=bpy.data.materials['RFX | Charcoal coated steel'];zinc=bpy.data.materials['RFX | Dusty galvanized duct']
removed=[]
for o in list(coll.objects):
 if o.name.startswith(('RFX | Extraction duct section','RFX | Duct standing seam')):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)==10
path=[Vector(p) for p in [(-10.78,2.8),(-11.55,2.8),(-11.55,5.5),(-10.8,6.1),(-7.4,6.1)]]
dirs=[(b-a).normalized() for a,b in zip(path,path[1:])];norms=[Vector((-d.y,d.x)) for d in dirs]
left=[];right=[]
for j,p in enumerate(path):
 if j==0:offset=norms[0]*.45
 elif j==len(path)-1:offset=norms[-1]*.45
 else:
  bis=(norms[j-1]+norms[j]).normalized();offset=bis*(.45/bis.dot(norms[j]))
 left.append(p+offset);right.append(p-offset)
outline=left+list(reversed(right));N=len(outline)
vs=[(p.x,y,p.y) for y in (-22.275,-21.325) for p in outline]
fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
o=mesh('Continuous mitered extraction duct',vs,fs,zinc)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
box('Extraction final corner',(-7.4,-21.8,6.1),(.95,.95,.90),zinc,.014)
beam('Extraction filter inlet',(-7.4,-21.8,6.1),(-7.4,-20.2,6.1),.95,.9,zinc)
box('Duct upright clamp',(-11.55,-21.8,3.55),(.96,1.01,.065),steel,.003)
box('Duct horizontal clamp',(-9.45,-21.8,6.1),(.065,1.01,.96),steel,.003)
box('Duct inlet clamp',(-7.4,-20.8,6.1),(1.01,.065,.96),steel,.003)
bpy.context.view_layer.update();errors=[]
for o in coll.objects:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free()
 if bad or deg:errors.append((o.name,bad,deg))
assert not errors,errors
assert sha(SRC)==initial
bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
report.update(saved_sha256=sha(SRC),new_objects=len(coll.objects),mesh_errors=errors,correction='Eye-height review exposed gaps in separate duct elbow beams. Replaced with continuous closed mitered main duct and overlapping closed inlet elbow. Prior gallery belongs to superseded revision and is overwritten by current fixed-name captures.')
(OUT/'build-verification.json').write_text(json.dumps(report,indent=2))
print('DUCT_REPAIR_SAVED',report['saved_sha256'],flush=True)
s.camera=bpy.data.objects['RFX CAMERA | 01_SW'];s.render.filepath=str(OUT/'01_SW.png');bpy.ops.render.render(write_still=True)
