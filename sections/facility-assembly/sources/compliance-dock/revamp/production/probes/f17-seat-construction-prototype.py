"""Root isolated mesh/UV prototype: selected definitions only, no builder/save."""
import bpy,bmesh,ast,hashlib,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];SOURCE=R/'module_overhaul_R1.blend';H='e33da737e93a730f62f43b09f8348df7133db657c6f6b9efc53651f26df60e39';sha=lambda:hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
COL=bpy.data.collections.new('TEMP root isolated F17 mesh study');S.collection.children.link(COL);ASM=None;ORIGINAL={'Chair seat cushion'};EXCEPTIONS={};MATERIALS={key:bpy.data.materials['CD | '+key] for key in ['fabric','cotton','coral']}
for path,names in [(R/'revamp/reference-tooling/original_build_dock.py',{'put','mesh','line','bevel'}),(R/'overhaul_dock.py',{'use_root','uv','replace','assign','profile'}),(R/'full_detail.py',{'octagon','tapered'}),(R/'full_repairs.py',{'chair_sewn_canvas_finish','sewn_cushion_charts','transit_chest_pressings'})]:
 tree=ast.parse(path.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==len(names);exec(compile(ast.Module(body=defs,type_ignores=[]),str(path),'exec'))
chair_sewn_canvas_finish();transit_chest_pressings();bpy.context.view_layer.update();records=[]
for name in ['Chair seat cushion','Cargo crate base','Cargo crate lid']:
 o=S.objects[name];me=o.data;me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];bad=[]
 for t in me.loop_triangles:
  if (v[t.vertices[1]]-v[t.vertices[0]]).cross(v[t.vertices[2]]-v[t.vertices[0]]).length<1e-10:bad.append(t.index)
 edge={}
 for f in me.polygons:
  for a,b in zip(list(f.vertices),list(f.vertices)[1:]+list(f.vertices)[:1]):edge.setdefault(tuple(sorted((a,b))),[]).append(a<b)
 assert all(len(a)==2 and a[0]!=a[1] for a in edge.values()),name
 assert not bad,(name,bad)
 records.append(dict(object=name,vertices=len(v),triangles=len(me.loop_triangles),closed_consistent_winding=True,degenerate_triangles=bad,bounds=[[min(q[k] for q in v) for k in range(3)],[max(q[k] for q in v) for k in range(3)]]))
o=S.objects['Chair seat cushion'];cut=o.data.uv_layers.new(name='CD_Fabric_Cut_1m');sewn_cushion_charts(o,cut);ratios=[]
for t in o.data.loop_triangles:
 points=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];uvs=[cut.data[i].uv.copy() for i in t.loops]
 r=[(uvs[i]-uvs[j]).length/(points[i]-points[j]).length for i,j in [(0,1),(1,2),(2,0)] if (points[i]-points[j]).length>1e-5];ratios.append(max(r)/min(r))
assert max(ratios)<1.25,max(ratios)
assert sha()==H
Path(__file__).with_suffix('.json').write_text(json.dumps(dict(input_source_sha256=H,source_unchanged=True,native_written=False,full_builder_executed=False,only_selected_authoring_definitions_executed=True,prototype_only=True,results=records,seat_consumed_triangle_edge_anisotropy_max=max(ratios)),indent=2)+'\n')
print('F17_ISOLATED_SEAT_AND_CHEST_CLOSED_NONDEGENERATE_PASS',records,max(ratios),flush=True)
