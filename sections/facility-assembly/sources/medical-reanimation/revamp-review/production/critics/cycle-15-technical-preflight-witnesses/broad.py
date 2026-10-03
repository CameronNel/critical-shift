import bpy,json,hashlib,math,bmesh,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');OUT=Path('/tmp/medical15-technical')
with bpy.data.libraries.load(str(ROOT/'module_overhaul_R2.blend'),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
g={};bounds={};dup={};uvreports=[];normals=[];materials={}
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
 v=[o.matrix_world@x.co for x in me.vertices];f=[tuple(x.vertices) for x in me.loop_triangles]
 if v and f:
  g[o.name]=(v,f,BVHTree.FromPolygons(v,f,all_triangles=True))
  bounds[o.name]=[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]]
  sig=hashlib.sha256(json.dumps([sorted(tuple(round(x,7) for x in p) for p in v),len(f)]).encode()).hexdigest()
  dup.setdefault(sig,[]).append(o.name)
 if o.type=='MESH':
  ratios=[];degenerate=0;missing=False
  uv=me.uv_layers.get('MED_Physical_1m')
  required=any(mat and mat.use_nodes and any(n.type=='UVMAP' and n.uv_map=='MED_Physical_1m' and n.outputs[0].is_linked for n in mat.node_tree.nodes) for mat in me.materials)
  if uv:
   for poly in me.polygons:
    ls=list(poly.loop_indices);ids=list(poly.vertices)
    for k in range(1,len(ls)-1):
     wa=(v[ids[k]]-v[ids[0]]).cross(v[ids[k+1]]-v[ids[0]]).length/2
     ua=(uv.data[ls[k]].uv-uv.data[ls[0]].uv).cross(uv.data[ls[k+1]].uv-uv.data[ls[0]].uv)/2
     if wa>1e-12:
      if abs(ua)<1e-12:degenerate+=1
      else:ratios.append(abs(ua)/wa)
   uvreports.append({'object':o.name,'required_by_material':required,'uv_triangles_with_area':len(ratios),'degenerate_nonzero_geometry_triangles':degenerate,'uv_area_per_m2_min':min(ratios) if ratios else None,'uv_area_per_m2_max':max(ratios) if ratios else None,'uv_area_per_m2_median':statistics.median(ratios) if ratios else None})
  elif required:uvreports.append({'object':o.name,'required_by_material':True,'missing_named_uv':True})
  bm=bmesh.new();bm.from_mesh(me)
  inconsistent=sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in bm.edges)
  normals.append({'object':o.name,'inconsistent_edges':inconsistent,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'negative_total_closed_volume':all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)<-1e-10})
  bm.free()
 ev.to_mesh_clear()
for mat in {m for o in s.objects if hasattr(o.data,'materials') for m in o.data.materials if m}:
 if not mat.use_nodes:continue
 materials[mat.name]={'users':[o.name for o in s.objects if hasattr(o.data,'materials') and mat.name in o.data.materials], 'nodes':[{'type':n.type,'name':n.name,'uv_map':n.uv_map if n.type=='UVMAP' else None,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':{i.name:str(i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked},'linked_outputs':[x.name for x in n.outputs if x.is_linked]} for n in mat.node_tree.nodes],'links':[{'from_node':l.from_node.name,'from_socket':l.from_socket.name,'to_node':l.to_node.name,'to_socket':l.to_socket.name} for l in mat.node_tree.links]}
(OUT/'surfacing.json').write_text(json.dumps({'uv':uvreports,'materials':materials,'normal_scan':normals,'coincident_vertex_geometry_candidates':[n for n in dup.values() if len(n)>1]},indent=2))
def near(a,b,t=.005):return all(a[0][i]<=b[1][i]+t and b[0][i]<=a[1][i]+t for i in range(3))
def contact(a,b,detail=False):
 av,af,at=g[a];bv,bf,bt=g[b];overlap=at.overlap(bt)
 if overlap and not detail:return {'triangle_intersections':len(overlap),'sampled_distance_m':None}
 best=(math.inf,None,None)
 for vs,fs,tree,rev in [(av,af,bt,False),(bv,bf,at,True)]:
  points=list(vs)
  if detail:
   points.extend((vs[f[0]]+vs[f[1]]+vs[f[2]])/3 for f in fs)
   es={tuple(sorted((f[k],f[(k+1)%3]))) for f in fs for k in range(3)}
   points.extend((vs[i]+vs[j])/2 for i,j in es)
  for p in points:
   q,n,i,d=tree.find_nearest(p)
   if d is not None and d<best[0]:best=(d,list(q) if rev else list(p),list(p) if rev else list(q))
 return {'triangle_intersections':len(overlap),'sampled_distance_m':best[0],'point_a':best[1],'point_b':best[2]}
ns=list(g);adj={n:[] for n in ns};edges=[];pairs=0
for i,a in enumerate(ns):
 for b in ns[:i]:
  if not near(bounds[a],bounds[b]):continue
  pairs+=1;c=contact(a,b)
  if c['triangle_intersections'] or c['sampled_distance_m']<=.0050001:
   adj[a].append(b);adj[b].append(a);edges.append({'a':a,'b':b,**c})
 if i%100==0:print('PHYSICAL_GRAPH_PROGRESS',i,len(ns),pairs,len(edges),flush=True)
architecture=['Floor','Decon floor','West wall','East wall','Entry wall','Entry wall.001','Entry lintel','Rear west wall','Rear east wall','Decon west wall','Decon east wall','Decon rear wall pier','Decon rear wall pier.001','Decon rear wall below extract','Decon rear wall above extract','Ceiling','Decon ceiling']
seen=set(architecture);queue=list(architecture)
for a in queue:
 for b in adj.get(a,[]):
  if b not in seen:seen.add(b);queue.append(b)
remaining=set(ns)-seen;clusters=[]
while remaining:
 a=remaining.pop();cl=[a]
 for t in cl:
  for b in adj[t]:
   if b in remaining:remaining.remove(b);cl.append(b)
 clusters.append(cl)
(OUT/'physical-graph.json').write_text(json.dumps({'geometry_objects':len(g),'candidate_pairs':pairs,'edges':edges,'architecture_seed_objects':architecture,'unrooted_clusters':clusters,'warning':'Evaluated BVH triangle intersections and sampled distance establish surface connection only. A plausible load-bearing mechanism still requires inspection; arbitrary neighboring overlap is not support.'},indent=2))
# Exact targeted cabinet stock bearing and plumbing witnesses.
targeted=[]
for i in range(12):
 case='Sealed supply case'+('' if i==0 else '.'+str(i).zfill(3));shelf='Supply cabinet shelf'+('' if i%3==0 else '.'+str(i%3).zfill(3))
 for host in [shelf,'Supply cabinet back']:
  targeted.append({'a':case,'b':host,**contact(case,host,True)})
for a,b in [('Wash rose','Shower arch'),('Shower arch','Wash pipe wall clip.001'),('Controlled drain sump cover','Contained drain connection'),('Contained drain connection','Decon rear wall below extract'),('Wash fitting union.001','Regulator shower branch'),('Regulator shower branch','Rear wash control backing'),('Recovery longitudinal support','Tubular recovery leg'),('Tubular recovery leg','Recovery foot cap'),('Supply bench top','Bench rear apron'),('Bench rear apron','Supply bench leg.001'),('Supply bench leg.001','Floor'),('Reserve folded cap','Battery plinth'),('Reserve service hinge','MED_R2 | Reserve fixed front crosschannel 0.14')]:
 if a in g and b in g:targeted.append({'a':a,'b':b,**contact(a,b,True)})
(OUT/'targeted-bearings.json').write_text(json.dumps(targeted,indent=2))
print('BROAD_AUDIT_COMPLETE',len(g),pairs,len(edges),'unrooted',clusters,flush=True)
