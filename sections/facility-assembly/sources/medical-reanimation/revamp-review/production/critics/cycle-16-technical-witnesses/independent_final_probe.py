exec(compile(open('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation/revamp-review/production/critics/cycle-16-technical-witnesses/independent_inventory_full.py').read(),'/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation/revamp-review/production/critics/cycle-16-technical-witnesses/independent_inventory_full.py','exec'))
import bmesh
from mathutils.bvhtree import BVHTree
from collections import Counter
cache={}
def geom(name):
 if name not in cache:
  o=s.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(x.vertices) for x in m.polygons];edges=[tuple(x.vertices) for x in m.edges];tree=BVHTree.FromPolygons(v,f);cache[name]=(v,f,edges,tree);ev.to_mesh_clear()
 return cache[name]
pairs=[('Rail support crosshead','Telescopic lift inner','crosshead retained inserted telescopic stem'),('Rail support crosshead.001','Telescopic lift inner.001','crosshead retained inserted telescopic stem'),('Basin bottom','Sink wall bracket','basin seated into retained wall bracket'),('Sealed chamber pan','Chassis longitudinal channel','pan rigid chassis lap joint'),('Sealed chamber pan','Chassis longitudinal channel.001','pan rigid chassis lap joint'),('Serviceable inner access panel','Inner service panel rear support','retained access panel mounting overlap'),('Serviceable inner access panel.001','Inner service panel rear support.001','retained access panel mounting overlap'),('Rear machine skin','Chamber structural upright','rear sheet attached to structural end'),('Rear machine skin','Chamber structural upright.001','rear sheet attached to structural end')]
contacts=[]
for name,target,mechanism in pairs:
 ov,of,oe,ot=geom(name);tv,tf,te,tt=geom(target);hits=[]
 for vs,eds,tree in [(ov,oe,tt),(tv,te,ot)]:
  for i,j in eds:
   delta=vs[j]-vs[i]
   if delta.length<1e-10:continue
   hit,n,index,distance=tree.ray_cast(vs[i],delta.normalized(),delta.length+1e-8)
   if hit is not None:
    own=ot.find_nearest(hit);to=tt.find_nearest(hit)
    if own[3]<=1e-6 and to[3]<=1e-6:hits.append({'point':list(hit),'source_surface_error_m':own[3],'target_surface_error_m':to[3],'source_normal':list(own[1]),'target_normal':list(to[1]),'source_face':own[2],'target_face':to[2]})
 contacts.append({'object':name,'target':target,'mechanism':mechanism,'exact_boundary_intersection_witnesses':len(hits),'witnesses':hits[:12],'status':'PHYSICAL_JOIN' if hits else 'REVIEW'})
# Independently audit winding on the exact physical-UV/modified mesh scope.
normals=[]
for rec in result['physical_uv']:
 o=s.objects[rec['object']];ev=o.evaluated_get(dg);md=ev.to_mesh();bm=bmesh.new();bm.from_mesh(md);pending=set(bm.faces);negative=0;closed=0
 inconsistent=sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in bm.edges)
 while pending:
  todo=[pending.pop()];island=set(todo)
  while todo:
   f=todo.pop()
   for edge in f.edges:
    for n in edge.link_faces:
     if n in pending:pending.remove(n);island.add(n);todo.append(n)
  if all(len(e.link_faces)==2 for f in island for e in f.edges):
   closed+=1;volume=0
   for f in island:
    vs=[loop.vert.co for loop in f.loops];volume+=sum(vs[0].dot(vs[i].cross(vs[i+1]))/6 for i in range(1,len(vs)-1))
   if volume < -1e-10:negative+=1
 normals.append({'object':o.name,'inconsistent_shared_edges':inconsistent,'closed_islands':closed,'negative_closed_islands':negative});bm.free();ev.to_mesh_clear()
# Use the live Material Output ancestry to distinguish active UV users from
# spare nodes that happen to carry links.
materials=[]
for m in {m for o in s.objects if o.type=='MESH' for m in o.data.materials if m and m.use_nodes}:
 active=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output];todo=list(active);seen=set()
 while todo:
  n=todo.pop()
  if n in seen:continue
  seen.add(n)
  for socket in n.inputs:
   for link in socket.links:todo.append(link.from_node)
 maps=[n.uv_map for n in seen if n.type=='UVMAP']
 if maps:materials.append({'material':m.name,'active_uv_maps':maps})
fonts=[{'name':f.name,'filepath':f.filepath,'packed':bool(f.packed_file),'builtin':f.filepath=='<builtin>'} for f in bpy.data.fonts]
(W/'independent-final-probe.json').write_text(json.dumps({'source_sha256':before,'retained_physical_joins':contacts,'independent_winding':normals,'live_output_uv_materials':materials,'fonts':fonts,'source_sha256_after':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2));assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('FINAL_PROBE',len(result['physical_uv']),len(normals),len(contacts),sum(c['status']=='PHYSICAL_JOIN' for c in contacts),flush=True)
