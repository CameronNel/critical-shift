import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');OUT=Path('/tmp/medical15-technical')
with bpy.data.libraries.load(str(ROOT/'module_overhaul_R2.blend'),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
g={};bounds={};coverage=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@x.co for x in me.vertices];f=[tuple(x.vertices) for x in me.loop_triangles]
 if v and f:g[o.name]=(v,f,BVHTree.FromPolygons(v,f,all_triangles=True));bounds[o.name]=[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]]
 if o.get('assembly_contact_contracts'):
  tags=me.attributes.get('med_assembly_part');actual=set(x.value for x in tags.data) if tags else set();contracts=json.loads(o['assembly_contact_contracts']);declared={x['part_id'] for x in contracts}
  coverage.append({'object':o.name,'evaluated_vertices':len(v),'actual_tag_ids':sorted(actual),'declared_ids':sorted(declared),'unregistered_tag_ids':sorted(actual-declared),'ids_without_vertices':sorted(declared-actual),'negative_tag_vertices':sum(x.value<0 for x in tags.data) if tags else None})
 ev.to_mesh_clear()
def aabbdistance(a,b):return math.sqrt(sum(max(0,a[0][i]-b[1][i],b[0][i]-a[1][i])**2 for i in range(3)))
def contact(a,b):
 av,af,at=g[a];bv,bf,bt=g[b];best=(math.inf,None,None)
 for vs,fs,tree,rev in [(av,af,bt,False),(bv,bf,at,True)]:
  pts=list(vs);pts.extend((vs[f[0]]+vs[f[1]]+vs[f[2]])/3 for f in fs);es={tuple(sorted((f[k],f[(k+1)%3]))) for f in fs for k in range(3)};pts.extend((vs[i]+vs[j])/2 for i,j in es)
  for p in pts:
   q,n,i,d=tree.find_nearest(p)
   if d is not None and d<best[0]:best=(d,list(q) if rev else list(p),list(p) if rev else list(q))
 return {'sampled_distance_m':best[0],'point_a':best[1],'point_b':best[2],'triangle_intersections':len(at.overlap(bt))}
clusters=json.loads((OUT/'physical-graph.json').read_text())['unrooted_clusters'];results=[]
for cl in clusters:
 rows=[]
 for a in cl:
  nearest=sorted((aabbdistance(bounds[a],bounds[b]),b) for b in g if b not in cl)[:7]
  for distance,b in nearest:rows.append({'a':a,'b':b,'aabb_separation_m':distance,**contact(a,b)})
 rec={'cluster':cl,'nearest_external_contacts':sorted(rows,key=lambda x:x['sampled_distance_m'])};results.append(rec);print('CLUSTER',cl,'NEAREST',rec['nearest_external_contacts'][:2],flush=True)
(OUT/'cluster-contact-probes.json').write_text(json.dumps(results,indent=2));(OUT/'assembly-coverage.json').write_text(json.dumps(coverage,indent=2))
print('CLUSTER_PROBES_COMPLETE',flush=True)
