"""Visible neglect: worn traffic paint, cracked screed and localized spalling."""
# Independent R16 audit: the north films were seated correctly but wound toward
# the wall. Reverse the open film faces without altering their protected targets.
for o in s.objects:
 if o.name.startswith(('RF1 | Wall utility damp plume','RF1 | Wall dried mineral trickle')):
  for polygon in o.data.polygons:polygon.flip()

# A nominal cylinder radius missed the actual evaluated lathe flats and foot
# transition. Project every corrosion vertex onto the evaluated real vessel.
bpy.context.view_layer.update()
vessel=bpy.data.objects['RF1 | PV05 cast pressure vessel'];shell_tree=evaluated_tree(vessel)
for o in s.objects:
 if not o.name.startswith('RF1 | PV local seal corrosion run'):continue
 for vertex in o.data.vertices:
  point=o.matrix_world@vertex.co;hit,normal,_,distance=shell_tree.find_nearest(point)
  assert hit is not None and distance<.005,(o.name,distance)
  vertex.co=o.matrix_world.inverted()@(hit+normal*.00002)
 anchor=o.matrix_world@o.data.vertices[0].co
 _,normal,_,_=shell_tree.find_nearest(anchor)
 for record in supports:
  if record['group']==o.name:record['anchor']=list(anchor);record['direction']=list(-normal)

# A single room-coordinate mapping keeps broad damp discoloration continuous
# across screed panels. Low frequency colour masks; no geometry displacement.
mapping=link(bpy.data.objects.new('RF17 | Wear coordinates',None));mapping.hide_render=True
floor_materials=[bpy.data.materials['RF1_screed_'+str(i)] for i in range(4)]+[M['concrete'],M['epoxy']]
for material in floor_materials:
 nodes=material.node_tree.nodes;links=material.node_tree.links
 p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color'];previous=base.links[0].from_socket if base.is_linked else None
 coord=nodes.new('ShaderNodeTexCoord');coord.object=mapping
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.87;noise.inputs['Detail'].default_value=1.0
 links.new(coord.outputs['Object'],noise.inputs['Vector'])
 mask=nodes.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.35;mask.color_ramp.elements[0].color=(0,0,0,1)
 mask.color_ramp.elements[1].position=.64;mask.color_ramp.elements[1].color=(.76,.76,.76,1)
 links.new(noise.outputs['Fac'],mask.inputs['Fac'])
 mix=nodes.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.023,.036,.025,1)
 if previous:links.new(previous,mix.inputs[1])
 else:mix.inputs[1].default_value=base.default_value
 links.new(mask.outputs['Color'],mix.inputs[0]);links.new(mix.outputs[0],base)

# Isolate traffic paint from all equipment labels. Missing paint reveals the
# real floor rather than an opaque dark overlay. Keep enough surviving dashes to
# establish the primary aisle from every fixed gameplay view.
paint_materials={}
for o in list(s.objects):
 if o.type not in {'MESH','FONT','CURVE'}:continue
 lo,hi=bounds_world(o)
 if hi.z>.015 or lo.z<-.001:continue
 for i,material in enumerate(list(o.data.materials)):
  if material not in [M['ivory'],M['ochre']]:continue
  key=material.name
  if key not in paint_materials:
   mm=material.copy();mm.name='RF17_worn_traffic_'+key;nodes=mm.node_tree.nodes;links=mm.node_tree.links
   output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');previous=output.inputs['Surface'].links[0].from_socket
   coord=nodes.new('ShaderNodeTexCoord');coord.object=mapping
   noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=26;noise.inputs['Detail'].default_value=1
   links.new(coord.outputs['Object'],noise.inputs['Vector'])
   ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
   ramp.color_ramp.elements[0].position=.46;ramp.color_ramp.elements[0].color=(0,0,0,1)
   ramp.color_ramp.elements[1].position=.47;ramp.color_ramp.elements[1].color=(1,1,1,1)
   links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
   transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader')
   links.new(ramp.outputs['Color'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(previous,mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
   paint_materials[key]=mm
  # Mesh data can be shared with equipment; copy before modifying material slots.
  o.data=o.data.copy();o.data.materials[i]=paint_materials[key]

M['scar']=mat('RF17_concrete_fissure',(.017,.025,.019),1,0,0)
M['spall']=mat('RF17_exposed_old_plaster',(.062,.083,.067),.99,0,.06)
M['flakedge']=mat('RF17_chalky_fracture_edge',(.153,.174,.141),.99,0,.04)

floors=[o for o in s.objects if o.name.startswith('RF1 | Worked floor panel')]+[bpy.data.objects['Floor'],bpy.data.objects['RF1 | Process epoxy field'],bpy.data.objects['RF1 | Fabrication epoxy field']]
def floor_face(x,y):
 choices=[]
 for target in floors:
  lo,hi=bounds_world(target)
  if lo.x<=x<=hi.x and lo.y<=y<=hi.y:choices.append((hi.z,target))
 return max(choices,key=lambda item:item[0])

def cracked_line(name,points,width=.0035):
 # Short ribbons sample the actual floor at each end, including panel joints.
 for i,(aa,bb) in enumerate(zip(points,points[1:])):
  a,b=Vector(aa),Vector(bb);side=Vector((-(b-a).y,(b-a).x));side.normalize();side*=width*(.7+.3*math.sin(i+1))
  coords=[a-side,b-side,b+side,a+side];verts=[]
  for point in coords:
   z,target=floor_face(point.x,point.y);verts.append((point.x,point.y,z+.00002))
  o=mesh(name,verts,[(0,1,2,3)],'scar')
  centre=(a+b)/2;z,target=floor_face(centre.x,centre.y)
  support(o.name,(centre.x,centre.y,z+.00002),target.name,(0,0,-1))

for j,points in enumerate([
 [(-3.86,-3.05),(-3.58,-2.87),(-3.40,-2.57),(-3.02,-2.38),(-2.85,-2.04),(-2.54,-1.94)],
 [(-3.40,-2.57),(-3.62,-2.24),(-3.61,-2.04)],
 [(.12,-.56),(.40,-.43),(.57,-.20),(.83,-.17),(1.13,.13),(1.50,.22),(1.76,.59)],
 [(.83,-.17),(.75,.13),(.59,.32)],
 [(2.64,2.04),(2.40,2.37),(2.06,2.48),(1.78,2.76),(1.33,2.88)],
 [(2.06,2.48),(2.14,2.86),(1.96,3.04)],
 [(-6.35,-4.25),(-6.12,-3.89),(-5.90,-3.70),(-5.64,-3.18)],
 [(4.31,-2.38),(4.06,-2.19),(3.72,-1.94),(3.62,-1.62)]
]):cracked_line('Hairline service-floor fracture '+str(j),points)

# Spalled paint below a leaking pipe beside the lit 02 bay. Irregular authored
# shapes create decay at gameplay scale; fine chips stay subordinate to it.
for j,points in enumerate([
 [(-2.97,2.23),(-2.82,2.30),(-2.79,2.59),(-2.44,2.66),(-2.31,2.51),(-2.37,2.34),(-2.12,2.16),(-2.15,1.74),(-2.39,1.58),(-2.74,1.72),(-2.68,1.91),(-2.96,1.98)],
 [(-3.71,3.81),(-3.48,3.78),(-3.38,3.59),(-3.49,3.26),(-3.70,3.13),(-3.89,3.34),(-3.84,3.64)],
 [(.06,2.69),(.27,2.74),(.42,2.55),(.53,2.59),(.68,2.35),(.53,2.07),(.35,2.13),(.12,2.01),(.03,2.29)],
]):
 target='RF1 | North acoustic concrete bay '+('1' if j<2 else '2')
 patch=north_mark('North spalled service paint '+str(j),points,'spall',target)
 for polygon in patch.data.polygons:polygon.flip()
 # A narrow pale broken lip signals missing paint instead of a painted graphic.
 a,b=points[1],points[2]
 edge=north_mark('North broken plaster lip '+str(j),[a,b,(b[0]+.014,b[1]+.017),(a[0]+.011,a[1]+.018)],'flakedge',target)
 for polygon in edge.data.polygons:polygon.flip()

# The worker recess has the same neglected fabric rather than a pristine island.
south=bpy.data.objects['South_right'];lo,hi=bounds_world(south);yy=hi.y+.00002
pts=[(.03,3.64),(.20,3.73),(.31,3.32),(.43,3.06),(.35,2.73),(.22,2.88),(.12,2.37),(.04,2.71)]
patch=mesh('Nook old wall seep',[(x,yy,z) for x,z in pts],[tuple(range(len(pts)))],'damp')
for polygon in patch.data.polygons:
 if polygon.normal.y<0:polygon.flip()
support(patch.name,(.20,yy,3.32),south.name,(0,-1,0))

# Tight contact corrosion follows the bolt line on the front flat hatch. Points
# are measured against its actual evaluated face before creating the paint film.
hatch=bpy.data.objects['Processor_sealed_hatch'];lo,hi=bounds_world(hatch)
for x,z,w,h in [(1.17,1.70,.055,.14),(1.46,1.93,.047,.12),(.91,1.65,.045,.18)]:
 centre=Vector((x,lo.y-.01,z));hit,normal,ix,distance=evaluated_tree(hatch).ray_cast(centre,Vector((0,1,0)),.1)
 if hit is None:continue
 # Curved/dished face films are ray-projected at every vertex independently.
 points=[(x-w,z+h*.30),(x-w*.6,z-h*.50),(x+w*.12,z-h*.59),(x+w*.55,z+h*.1),(x+w*.32,z+h*.47)]
 vertices=[]
 for xx,zz in points:
  p,n,_,_=evaluated_tree(hatch).ray_cast(Vector((xx,lo.y-.03,zz)),Vector((0,1,0)),.2)
  if p is not None:vertices.append(tuple(p+n*.00003))
 if len(vertices)!=len(points):continue
 o=mesh('Hatch latch rust bleed',vertices,[tuple(reversed(range(len(vertices))))],'rust')
 support(o.name,tuple(hit+normal*.00003),hatch.name,(0,1,0))
bpy.context.view_layer.update()
