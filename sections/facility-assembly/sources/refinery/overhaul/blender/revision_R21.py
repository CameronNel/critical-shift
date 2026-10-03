"""Feather water-film coverage; preserve the established dark composition."""
# Per-vertex coverage fades across the actual tapered leak outline. No texture
# card or high-frequency grunge: the physical wall remains visible at the edges.
for o in s.objects:
 if not o.name.startswith('RF1 | Gravity-shaped old service leak'):continue
 old=[o.matrix_world@v.co for v in o.data.vertices];vertices=[];faces=[];coverage=[]
 columns=[0,.18,.50,.82,1];levels=[0,.48,.82,.45,0]
 rows=len(old)//2
 for row in range(rows):
  a,b=old[2*row:2*row+2]
  fade=min(1,(rows-1-row)/3+.25)
  for t,alpha in zip(columns,levels):vertices.append(tuple(a+(b-a)*t));coverage.append(alpha*fade)
 for row in range(rows-1):
  for col_index in range(4):
   i=row*5+col_index;faces.append((i,i+5,i+6,i+1))
 me=bpy.data.meshes.new(o.name+' feathered film');me.from_pydata(vertices,[],faces);me.materials.append(M['old_leak'])
 attribute=me.color_attributes.new(name='RF21_water_coverage',type='FLOAT_COLOR',domain='POINT')
 for datum,value in zip(attribute.data,coverage):datum.color=(value,value,value,1)
 o.data=me;o.matrix_world=Matrix.Identity(4)
 for polygon in me.polygons:
  if polygon.normal.y>0:polygon.flip()
nodes=M['old_leak'].node_tree.nodes;links=M['old_leak'].node_tree.links
blend=next(node for node in nodes if node.type=='MIX_SHADER')
attribute=nodes.new('ShaderNodeAttribute');attribute.attribute_name='RF21_water_coverage'
strength=nodes.new('ShaderNodeMath');strength.operation='MULTIPLY';strength.inputs[1].default_value=.67
links.new(attribute.outputs['Fac'],strength.inputs[0]);links.new(strength.outputs[0],blend.inputs[0])
bpy.context.view_layer.update()
