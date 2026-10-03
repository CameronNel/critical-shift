import bpy, hashlib,json,collections,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');O=R/'revamp/production/critics/full-c08-technical';S=R/'module_overhaul_R1.blend';H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
sha=lambda:hashlib.sha256(S.read_bytes()).hexdigest()
assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False);sc=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=sc;dg=bpy.context.evaluated_depsgraph_get()
shapes=[]
for ob in sc.objects:
 if ob.type not in {'MESH','CURVE','FONT','SURFACE','META'}:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@p.co for p in me.vertices];t=[tuple(p.vertices) for p in me.loop_triangles]
 if not v or not t:ev.to_mesh_clear();continue
 lo=[min(p[k] for p in v) for k in range(3)];hi=[max(p[k] for p in v) for k in range(3)]
 samples=v[::max(1,len(v)//512)]+[sum((v[i] for i in tri),Vector())/3 for tri in t[::max(1,len(t)//512)]]
 shapes.append({'name':ob.name,'v':v,'t':t,'bvh':BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=1e-7),'lo':lo,'hi':hi,'samples':samples,'parent':ob.parent.name if ob.parent else None})
 ev.to_mesh_clear()
print('SHAPES',len(shapes),flush=True)
edges=[];near=[];adj=collections.defaultdict(set);candidates=0
for ia,a in enumerate(shapes):
 if ia%100==0:print('PROGRESS',ia,'contacts',len(edges),flush=True)
 for ib in range(ia+1,len(shapes)):
  b=shapes[ib]
  if any(a['lo'][k]>b['hi'][k]+.005001 or b['lo'][k]>a['hi'][k]+.005001 for k in range(3)):continue
  candidates+=1;over=a['bvh'].overlap(b['bvh'])
  witness=None;mind=1
  if over:
   mind=0;witness={'method':'actual_triangle_overlap','triangle_pair':list(over[0]),'overlap_pair_count':len(over)}
  else:
   for frm,to in ((a,b),(b,a)):
    for p in frm['samples']:
     if any(p[k]<to['lo'][k]-.005001 or p[k]>to['hi'][k]+.005001 for k in range(3)):continue
     q,n,fi,d=to['bvh'].find_nearest(p,.005001)
     if q is not None and d<mind:
      mind=d;witness={'method':'sampled_vertex_or_triangle_centroid_to_actual_triangle','from':frm['name'],'point':list(p),'target_point':list(q),'target_triangle':fi,'distance_m':d}
      if d<1e-7:break
    if mind<1e-7:break
  if witness and mind<=.005001:
   edges.append({'a':a['name'],'b':b['name'],'witness':witness});adj[a['name']].add(b['name']);adj[b['name']].add(a['name'])
seed='Floor slab';rooted={seed};queue=[seed]
while queue:
 for n in adj[queue.pop()]:
  if n not in rooted:rooted.add(n);queue.append(n)
remaining={a['name'] for a in shapes}-rooted;components=[]
while remaining:
 first=next(iter(remaining));group={first};queue=[first];remaining.remove(first)
 while queue:
  for n in adj[queue.pop()]:
   if n in remaining:remaining.remove(n);group.add(n);queue.append(n)
 components.append(sorted(group))
report={'source_sha256':H,'geometry_shapes':len(shapes),'aabb_candidate_count':candidates,'surface_contact_edges':edges,'rooted_seed':seed,'rooted_count':len(rooted),'unrooted_contact_components':sorted(components,key=lambda g:-len(g)),'limitations':['Broad phase uses world AABBs only to select candidates; every graph edge has actual triangle overlap or actual triangle nearest-surface witness.','Nearest-surface sampling bounded to approximately 512 vertices and 512 triangle centres per object; no-contact result is a candidate needing targeted full-surface follow-up, not conclusive proof of a gap.','5mm proximity establishes bounded geometric continuity, not structural strength, stability or runtime collision.','Intersections are potential construction contacts and need separate inspection; triangle overlap alone is not a defect.']}
assert sha()==H
(O/'contacts.json').write_text(json.dumps(report,indent=2));print('RESULT',len(rooted),'UNROOTED',json.dumps(report['unrooted_contact_components']),flush=True)
