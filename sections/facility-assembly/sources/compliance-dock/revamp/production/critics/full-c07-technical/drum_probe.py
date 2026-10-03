import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/critics/full-c07-technical');S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get();trees={};centers={}
for name in ['Transit drum A','Transit drum B']:
 o=S.objects[name];ev=o.evaluated_get(D);m=ev.to_mesh();m.calc_loop_triangles();ps=[o.matrix_world@x.co for x in m.vertices];trees[name]=BVHTree.FromPolygons(ps,[list(t.vertices) for t in m.loop_triangles],all_triangles=True);centers[name]=Vector([(min(p[i] for p in ps)+max(p[i] for p in ps))*.5 for i in range(3)]);ev.to_mesh_clear()
a=centers['Transit drum A'];b=centers['Transit drum B'];d=b-a;d.z=0;sep=d.length;d.normalize();rows=[]
for z in [.15,.3,.5,.7,.85]:
 p=a.copy();p.z=z;ha=trees['Transit drum A'].ray_cast(p,d,1);hb=trees['Transit drum B'].ray_cast(p,d,1);rows.append({'z_m':z,'a_exit_distance_m':ha[3],'b_entry_distance_m':hb[3],'a_exit_point':list(ha[0]) if ha[0] else None,'b_entry_point':list(hb[0]) if hb[0] else None,'a_exit_triangle':ha[2],'b_entry_triangle':hb[2],'solid_overlap_length_m':ha[3]-hb[3] if ha[0] and hb[0] else None})
pairs=json.loads((O/'coplanar-overlap.json').read_text())['pairs'];top=[r for r in pairs if {r['a'][0],r['b'][0]}=={'Transit drum A','Transit drum B'} and r['normal'][2]>.9999];out={'centers':{n:list(c) for n,c in centers.items()},'horizontal_center_distance_m':sep,'direction':list(d),'evaluated_cross_sections':rows,'top_overlap_m2':sum(x['same_orientation_overlap_m2'] for x in top),'top_overlap_triangle_pairs':len(top)};(O/'drum-actual-interpenetration.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
