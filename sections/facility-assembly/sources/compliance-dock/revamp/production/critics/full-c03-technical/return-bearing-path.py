import bpy,json,importlib.util
from pathlib import Path
from mathutils.bvhtree import BVHTree
r=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');p=r/'revamp/production/critics/full-c03-technical';spec=importlib.util.spec_from_file_location('v',r/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();shapes=[v.Shape(o,dg) for o in bpy.context.scene.objects if o.type in v.GEOMETRY_TYPES];by={s.name:s for s in shapes};steel=by['CD | Joined Cargo Inspection Conveyor / steel'];belt=by['Conveyor return belt'];parent=list(range(len(steel.vertices)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def union(a,b):
 a,b=find(a),find(b)
 if a!=b:parent[b]=a
for t in steel.triangles:union(t[0],t[1]);union(t[1],t[2])
groups={}
for i,t in enumerate(steel.triangles):groups.setdefault(find(t[0]),[]).append(i)
tri_group={i:k for k,idx in groups.items() for i in idx};hit=steel.bvh.overlap(belt.bvh);touching={tri_group[i] for i,j in hit};results=[]
todo=list(touching);done=set()
while todo:
 k=todo.pop()
 if k in done:continue
 done.add(k)
 idx=groups[k];tris=[steel.triangles[i] for i in idx];verts={i for t in tris for i in t};coords=[steel.vertices[i] for i in verts];bounds=v.bounds(coords);tree=BVHTree.FromPolygons(steel.vertices,tris,all_triangles=True);contacts=[]
 for otherk,otheridx in groups.items():
  if otherk==k:continue
  otherts=[steel.triangles[i] for i in otheridx];otherverts={i for t in otherts for i in t};othercoords=[steel.vertices[i] for i in otherverts];otherbounds=v.bounds(othercoords)
  if not v.overlaps(bounds,otherbounds,.00501):continue
  othertree=BVHTree.FromPolygons(steel.vertices,otherts,all_triangles=True);ov=tree.overlap(othertree);best=0. if ov else None;witness=None
  for verts_a,tree_b in ((coords,othertree),(othercoords,tree)):
   for vertex in verts_a:
    h=tree_b.find_nearest(vertex,.00501)
    if h[0] is not None and (best is None or h[3]<best):best=float(h[3]);witness=[list(vertex),list(h[0])]
  if best is not None:
   todo.append(otherk)
   contacts.append({'other_steel_topology_component':otherk,'bounds':[list(x) for x in otherbounds],'gap_m':best,'overlaps':len(ov),'witness':witness})
 for b in shapes:
  if b in (steel,belt) or not b.bvh or not v.overlaps(bounds,b.bounds,.00501):continue
  ov=tree.overlap(b.bvh);best=0. if ov else None;witness=None
  for vertex in coords:
   h=b.bvh.find_nearest(vertex,.00501)
   if h[0] is not None and (best is None or h[3]<best):best=float(h[3]);witness=[list(vertex),list(h[0])]
  for vertex in b.vertices:
   h=tree.find_nearest(vertex,.00501)
   if h[0] is not None and (best is None or h[3]<best):best=float(h[3]);witness=[list(vertex),list(h[0])]
  if best is not None:contacts.append({'other':b.name,'gap_m':best,'overlaps':len(ov),'witness':witness})
 results.append({'steel_topology_component':k,'triangles':len(idx),'bounds':[list(x) for x in bounds],'external_component_contacts':contacts})
(p/'return-bearing-path.json').write_text(json.dumps({'belt_bounds':[list(x) for x in belt.bounds],'belt_steel_overlap_triangle_pairs':len(hit),'separate_steel_topology_components':len(groups),'contacted_steel_parts':results},indent=2));print('RETURN_COMPLETE',len(groups),len(results))
