"""Current critic closure: real stain fade, joined PPE, printed sketch and legibility."""
# Explicit colour-to-value conversion uses the authored greyscale coverage. A
# bounded shader probe confirmed Fac already produced the same gradient in 5.2;
# R21's effect was subtle, not absent. This rewiring is clarity, not a new fade.
nodes=M['old_leak'].node_tree.nodes;links=M['old_leak'].node_tree.links
attribute=next(n for n in nodes if n.type=='ATTRIBUTE');strength=next(n for n in nodes if n.type=='MATH')
links.new(attribute.outputs['Color'],strength.inputs[0])

# Four manufactured finger roots extend into each actual palm. The original
# outer fingers stopped before the clipped palm corners, leaving 9–12mm gaps.
for o in s.objects:
 if not o.name.startswith('RF1 | Glove finger'):continue
 minimum=min(v.co.y for v in o.data.vertices)
 for vertex in o.data.vertices:
  if abs(vertex.co.y-minimum)<1e-7:vertex.co.y-=.025

# The diagram is ink on paper, not millimetre-thick floating torus/rod geometry.
paper=bpy.data.objects['RF1 | Pinned shift paper 1'];lo,hi=bounds_world(paper);front=hi.y+.00002
printed=json.loads(s['printed_surface_registry'])
ring_object=bpy.data.objects['RF1 | Pump sketch case'];centre=ring_object.matrix_world.translation.copy();verts=[];faces=[];count=48
for i in range(count):
 angle=i*math.tau/count
 for radius in [.0666,.0654]:verts.append((centre.x+radius*math.cos(angle),front,centre.z+radius*math.sin(angle)))
for i in range(count):
 j=(i+1)%count;faces.append((2*i,2*j,2*j+1,2*i+1))
me=bpy.data.meshes.new('RF22 printed pump circle');me.from_pydata(verts,[],faces);me.materials.append(M['ink']);ring_object.data=me;ring_object.matrix_world=Matrix.Identity(4);ring_object.modifiers.clear()
for polygon in me.polygons:
 if polygon.normal.y<0:polygon.flip()
printed.append(dict(mark=ring_object.name,target=paper.name,direction=[0,-1,0]))
for o in [ob for ob in s.objects if ob.name.startswith('RF1 | Pump schematic line')]:
 # The original rod axis is local Z. Preserve its measured endpoints and width.
 depth=max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)
 aa=o.matrix_world@Vector((0,0,-depth/2));bb=o.matrix_world@Vector((0,0,depth/2))
 a,b=Vector((aa.x,aa.z)),Vector((bb.x,bb.z));side=Vector((-(b-a).y,(b-a).x)).normalized()*.0006
 points=[a-side,b-side,b+side,a+side]
 me=bpy.data.meshes.new(o.name+' printed ink');me.from_pydata([(p.x,front,p.y) for p in points],[],[(0,1,2,3)]);me.materials.append(M['ink']);o.data=me;o.matrix_world=Matrix.Identity(4);o.modifiers.clear()
 for polygon in me.polygons:
  if polygon.normal.y<0:polygon.flip()
 printed.append(dict(mark=o.name,target=paper.name,direction=[0,-1,0]))
s['printed_surface_registry']=json.dumps(printed)

# Broader residue is restricted to real interior surfaces. World-coordinate
# elongated grain and soft spatial masks follow service traffic and wall leaks.
def surface_residue(material,centres,colour,stretch,scale):
 nodes=material.node_tree.nodes;links=material.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 coord=nodes.new('ShaderNodeTexCoord');coord.object=mapping
 vector=nodes.new('ShaderNodeVectorMath');vector.operation='MULTIPLY';vector.inputs[1].default_value=stretch
 links.new(coord.outputs['Object'],vector.inputs[0])
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=1.3
 links.new(vector.outputs[0],noise.inputs['Vector'])
 mask_noise=nodes.new('ShaderNodeMapRange');mask_noise.clamp=True;mask_noise.inputs['From Min'].default_value=.29;mask_noise.inputs['From Max'].default_value=.64
 links.new(noise.outputs['Fac'],mask_noise.inputs['Value'])
 combined=None
 for centre,dimensions in centres:
  delta=nodes.new('ShaderNodeVectorMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=centre;links.new(coord.outputs['Object'],delta.inputs[0])
  normalized=nodes.new('ShaderNodeVectorMath');normalized.operation='MULTIPLY';normalized.inputs[1].default_value=dimensions;links.new(delta.outputs[0],normalized.inputs[0])
  length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';links.new(normalized.outputs[0],length.inputs[0])
  spatial=nodes.new('ShaderNodeMapRange');spatial.clamp=True;spatial.inputs['From Min'].default_value=.30;spatial.inputs['From Max'].default_value=1.05
  spatial.inputs['To Min'].default_value=.88;spatial.inputs['To Max'].default_value=0;links.new(length.outputs['Value'],spatial.inputs['Value'])
  if combined is None:combined=spatial.outputs['Result']
  else:
   maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';links.new(combined,maximum.inputs[0]);links.new(spatial.outputs['Result'],maximum.inputs[1]);combined=maximum.outputs[0]
 mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';links.new(combined,mask.inputs[0]);links.new(mask_noise.outputs['Result'],mask.inputs[1])
 base=p.inputs['Base Color'];previous=base.links[0].from_socket if base.is_linked else None
 blend=nodes.new('ShaderNodeMixRGB');blend.inputs[2].default_value=(*colour,1)
 if previous:links.new(previous,blend.inputs[1])
 else:blend.inputs[1].default_value=base.default_value
 links.new(mask.outputs[0],blend.inputs[0]);links.new(blend.outputs[0],base)

for material in [indoor,M['epoxy']]+[bpy.data.materials['RF1_screed_'+str(i)] for i in range(4)]:
 surface_residue(material,[((-1.45,-2.25,0),(.30,1.45,0)),((3.50,.72,0),(.52,1.0,0)),((-5.74,-4.04,0),(.65,.62,0))],(.015,.026,.016),(1,4.8,1),7)

wall_materials={}
for o in s.objects:
 if not o.name.startswith(('RF1 | North acoustic concrete bay','RF1 | Side flush panel')):continue
 for i,material in enumerate(list(o.data.materials)):
  if material.name not in wall_materials:
   copy=material.copy();copy.name='RF22_residue_'+material.name
   surface_residue(copy,[((-2.6,6.38,2.60),(1.1,0,.55)),((3.9,6.38,2.75),(1.0,0,.59)),((7.45,1.55,2.26),(0,1.0,.62))],(.057,.080,.056),(3.1,3.1,.25),3)
   wall_materials[material.name]=copy
  o.data.materials[i]=wall_materials[material.name]

# Depleted traffic paint: lower its reflectance and lose a few heavily rubbed
# segments. The aisle geometry remains entirely open and its surviving edges clear.
for material in paint_materials.values():
 nodes=material.node_tree.nodes;links=material.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color'];previous=base.links[0].from_socket
 dim=nodes.new('ShaderNodeMixRGB');dim.blend_type='MULTIPLY';dim.inputs[0].default_value=1;dim.inputs[2].default_value=(.62,.65,.58,1)
 links.new(previous,dim.inputs[1]);links.new(dim.outputs[0],base)
for suffix in ['.003','.009','.014']:
 o=bpy.data.objects.get('RF1 | Walkway broken paint border'+suffix)
 if o:remove_object(o)

# All recovery of detail uses existing room fixtures, with six outages retained.
for key,energy in [('PV hood 0',72),('Press task bar',38),('Inspection sample practical',22),
                   ('Wall service lamp 1',14),('Wall service lamp 3',13),
                   ('Mine threshold practical',45),('Fuel transfer threshold practical',40),
                   ('Personnel threshold practical',22),('Mine transfer wall bulkhead',25),('Fuel transfer wall bulkhead',24)]:
 bpy.data.objects['RF1 LIGHT | '+key].data.energy=energy
for light in [o for o in s.objects if o.type=='LIGHT' and o.data.energy>0]:
 lens=bpy.data.objects[light['fixture_lens']]
 for material in lens.data.materials:
  for node in material.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':
    node.inputs['Base Color'].default_value=(.12,.145,.102,1)
    node.inputs['Emission Strength'].default_value=.30
bpy.context.view_layer.update()
