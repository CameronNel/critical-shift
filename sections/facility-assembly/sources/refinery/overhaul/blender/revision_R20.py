"""Conform thin floor fractures to actual evaluated floor faces, not bounds."""
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
ground=[o for o in s.objects if o.name=='Floor' or o.name.startswith(('RF1 | Worked floor panel','RF1 | Process epoxy field','RF1 | Fabrication epoxy field','RF1 | Swept floor repaired screed','Floor_maintenance_seam'))]
world_vertices=[];ground_faces=[];face_owners=[];projected_faces=[]
for o in ground:
 evaluated=o.evaluated_get(dg);me=evaluated.to_mesh();world=[evaluated.matrix_world@v.co for v in me.vertices];offset=len(world_vertices);world_vertices.extend(world)
 for face in me.polygons:
  ground_faces.append(tuple(offset+i for i in face.vertices));face_owners.append(o.name)
  points=[world[i] for i in face.vertices]
  # All near-ground face edges describe step/bevel boundaries. Include the
  # irregular repaired patch, rather than pretending its AABB is its top face.
  if all(-.002<=point.z<=.015 for point in points):projected_faces.append(points)
 evaluated.to_mesh_clear()
ground_tree=BVHTree.FromPolygons(world_vertices,ground_faces)
def xy_half(poly,n,d,positive_side):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=n.dot(a)-d;db=n.dot(b)-d
  ia=da>=-1e-11 if positive_side else da<=1e-11
  ib=db>=-1e-11 if positive_side else db<=1e-11
  if ia:result.append(a)
  if ia!=ib:result.append(a+(b-a)*(da/(da-db)))
 return result
def signed_area(poly):return sum(a.x*b.y-b.x*a.y for a,b in zip(poly,poly[1:]+poly[:1]))/2
cracks=[o for o in s.objects if o.name.startswith('RF1 | Hairline service-floor fracture')]
names={o.name for o in cracks};supports[:]=[r for r in supports if r['group'] not in names]
film_checks=[]
for o in cracks:
 world=[o.matrix_world@v.co for v in o.data.vertices]
 polygons=[[Vector((world[i].x,world[i].y)) for i in face.vertices] for face in o.data.polygons]
 lo,hi=bounds_world(o);lines={}
 for face in projected_faces:
  if max(p.x for p in face)<lo.x-.0001 or min(p.x for p in face)>hi.x+.0001 or max(p.y for p in face)<lo.y-.0001 or min(p.y for p in face)>hi.y+.0001:continue
  for a,b in zip(face,face[1:]+face[:1]):
   edge=Vector((b.x-a.x,b.y-a.y))
   if edge.length<1e-9:continue
   n=Vector((-edge.y,edge.x)).normalized();d=n.dot(Vector((a.x,a.y)))
   if n.x<0 or (abs(n.x)<1e-9 and n.y<0):n=-n;d=-d
   lines[(round(n.x,8),round(n.y,8),round(d,8))]=(n,d)
 for n,d in lines.values():
  pieces=[]
  for poly in polygons:
   distances=[n.dot(point)-d for point in poly]
   if min(distances)<-1e-10 and max(distances)>1e-10:
    pieces.extend(part for part in [xy_half(poly,n,d,False),xy_half(poly,n,d,True)] if len(part)>=3 and abs(signed_area(part))>1e-11)
   else:pieces.append(poly)
  polygons=pieces
 vertices=[];faces=[]
 for poly in polygons:
  if abs(signed_area(poly))<1e-11:continue
  centre=sum(poly,Vector((0,0)))/len(poly)
  hit,normal,face_index,distance=ground_tree.ray_cast(Vector((centre.x,centre.y,.04)),Vector((0,0,-1)),.08)
  assert hit is not None and normal.z>.05,(o.name,list(centre))
  owner=face_owners[face_index];start=len(vertices)
  for point in poly:
   # Micro-inset prevents exact shared-edge precision from selecting a lower
   # neighbouring slab in the independent ray test. It does not bridge steps.
   toward=centre-point
   inset=point+toward*min(.015,.000005/max(toward.length,1e-9))
   z=hit.z-(normal.x*(inset.x-hit.x)+normal.y*(inset.y-hit.y))/normal.z
   vertices.append((inset.x,inset.y,z+.00002))
  faces.append(tuple(range(start,len(vertices))))
  support(o.name,(centre.x,centre.y,hit.z+.00002),owner,tuple(-normal))
  film_checks.append(dict(group=o.name,target=owner,point=[centre.x,centre.y,hit.z+.00002],normal=list(normal),vertical_offset_m=.00002))
 me=bpy.data.meshes.new(o.name+' actual-floor film');me.from_pydata(vertices,[],faces);me.materials.append(M['scar']);o.data=me;o.matrix_world=Matrix.Identity(4)
 for polygon in me.polygons:
  if polygon.normal.z<0:polygon.flip()
s['floor_film_registry']=json.dumps(film_checks)
bpy.context.view_layer.update()
