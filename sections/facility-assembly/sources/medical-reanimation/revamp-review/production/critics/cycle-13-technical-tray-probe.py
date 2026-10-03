import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');O=R/'revamp-review/production/critics'
sha=hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()
with bpy.data.libraries.load(str(R/'module_overhaul_R2.blend'),link=False) as(a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
obj=s.objects['MED_R2 | Constructed clinical dispensing bottles and tray'];ev=obj.evaluated_get(dep);md=ev.to_mesh();vs=[obj.matrix_world@v.co for v in md.vertices]
adj=[set() for v in vs]
for e in md.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
pending=set(range(len(vs)));islands=[]
while pending:
 seed=pending.pop();ids={seed};todo=[seed]
 while todo:
  for n in adj[todo.pop()]:
   if n in pending:pending.remove(n);ids.add(n);todo.append(n)
 islands.append(ids)
base=islands[72];tree=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in md.polygons if all(v in base for v in p.vertices)])
bench=s.objects['Supply bench top'];bev=bench.evaluated_get(dep);bm=bev.to_mesh();bt=BVHTree.FromPolygons([bench.matrix_world@v.co for v in bm.vertices],[tuple(p.vertices) for p in bm.polygons])
records=[]
for ii in (73,74):
 points=[vs[i] for i in islands[ii]];best=min((tree.find_nearest(p)[3],j,tree.find_nearest(p)) for j,p in enumerate(points))
 p=points[best[1]];surface,normal,face,dist=tree.ray_cast(p,Vector((0,0,-1)),.04)
 br=bt.find_nearest(p)
 records.append({'island':ii,'intended_part':'Instrument tray rolled lip','base_island':72,'base_top_z_m':max(vs[i].z for i in base),'lip_bottom_z_m':min(v.z for v in points),'lip_to_base_minimum_vertex_surface_distance_m':best[0],'lip_witness_world':list(p),'base_witness_world':list(surface),'vertical_ray_distance_m':dist,'base_surface_normal_world':list(normal),'signed_gap_m':(p-surface).dot(normal),'bench_nearest_surface_m':br[3],'max_allowed_gap_m':.005,'status':'FAIL' if dist>.005 else 'PASS'})
result={'source_sha256':sha,'object':obj.name,'creator':'skill_redo.py:372-377 / consumable_profiles','tray_support_geometry':'one thin closed pan island72; no rising tray sidewall; two separate open rolled tubes islands73/74','records':records,'unrelated_inventory_clipboard_is_not_intended_tray_support':True,'source_saved':False,'source_checksum_unchanged':sha==hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()}
(O/'cycle-13-technical-tray-probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
bev.to_mesh_clear();ev.to_mesh_clear()
