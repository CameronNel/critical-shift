"""Independent R17 audit closure; keep the established gloomy composition."""
# Orient every open lip and hatch film against its actual supporting face.
for o in s.objects:
 if o.name.startswith('RF1 | North broken plaster lip'):
  for polygon in o.data.polygons:
   if polygon.normal.y>0:polygon.flip()
 if o.name.startswith('RF1 | Hatch latch rust bleed'):
  target=evaluated_tree(bpy.data.objects['Processor_sealed_hatch'])
  for polygon in o.data.polygons:
   point=o.matrix_world@polygon.center;_,normal,_,_=target.find_nearest(point)
   if (o.matrix_world.to_3x3()@polygon.normal).dot(normal)<0:polygon.flip()

# Keep indoor floor discoloration on its own material; restore exterior sills to
# their prior R15 concrete response instead of exporting the room's dirt to them.
indoor=M['concrete'].copy();indoor.name='RF18_indoor_worn_concrete'
for name in ['Floor','RF1 | Swept floor repaired screed']:
 o=bpy.data.objects.get(name)
 if o:
  for i,material in enumerate(o.data.materials):
   if material==M['concrete']:o.data.materials[i]=indoor
nodes=M['concrete'].node_tree.nodes;links=M['concrete'].node_tree.links
p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color']
macro=base.links[0].from_node;assert macro.type=='MIX_RGB'
original=macro.inputs[1].links[0].from_socket
links.new(original,base)
aged_colour('RF1_concrete',(.185,.174,.147))

# A quad whose ends lie on different floor levels slopes through the overlay.
# Clip each existing crack face at every actual slab boundary, then seat each
# resulting planar part on the highest local floor. No sloping or buried strip.
boundaries=[set(),set()]
for target in floors:
 lo,hi=bounds_world(target)
 for axis in [0,1]:boundaries[axis].update([lo[axis],hi[axis]])
def cut_polygon(poly,axis,value,greater):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=a[axis]-value;db=b[axis]-value
  inside_a=da>=-1e-10 if greater else da<=1e-10
  inside_b=db>=-1e-10 if greater else db<=1e-10
  if inside_a:result.append(a)
  if inside_a!=inside_b:
   t=da/(da-db);result.append(a+(b-a)*t)
 return result
cracks=[o for o in s.objects if o.name.startswith('RF1 | Hairline service-floor fracture')]
crack_names={o.name for o in cracks};supports[:]=[r for r in supports if r['group'] not in crack_names]
for o in cracks:
 world=[o.matrix_world@vertex.co for vertex in o.data.vertices]
 polygons=[[Vector((world[i].x,world[i].y)) for i in face.vertices] for face in o.data.polygons]
 for axis in [0,1]:
  for boundary in sorted(boundaries[axis]):
   pieces=[]
   for poly in polygons:
    if min(point[axis] for point in poly)+1e-9<boundary<max(point[axis] for point in poly)-1e-9:
     pieces.extend(part for part in [cut_polygon(poly,axis,boundary,False),cut_polygon(poly,axis,boundary,True)] if len(part)>=3)
    else:pieces.append(poly)
   polygons=pieces
 vertices=[];faces=[]
 for poly in polygons:
  centre=sum(poly,Vector((0,0)))/len(poly);z,target=floor_face(centre.x,centre.y)
  start=len(vertices);vertices.extend([(point.x,point.y,z+.00002) for point in poly]);faces.append(tuple(range(start,len(vertices))))
  support(o.name,(centre.x,centre.y,z+.00002),target.name,(0,0,-1))
 me=bpy.data.meshes.new(o.name+' conformed film');me.from_pydata(vertices,[],faces);me.materials.append(M['scar']);o.data=me;o.matrix_world=Matrix.Identity(4)
 for polygon in o.data.polygons:
  if polygon.normal.z<0:polygon.flip()
bpy.context.view_layer.update()
