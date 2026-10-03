"""Luna mood correction: plausible leak paths and an interrupted worker shift."""
# Broad hard-cut R17 shapes read as graphics. Replace them with narrow tapered
# leaks descending from the overhead service line, with small paint-loss scabs.
removed={o.name for o in s.objects if o.name.startswith(('RF1 | North spalled service paint','RF1 | North broken plaster lip'))}
supports[:]=[r for r in supports if r['group'] not in removed]
for name in removed:remove_object(bpy.data.objects[name])
M['old_plaster']=mat('RF19_exposed_mineral_plaster',(.127,.145,.119),.99,0,.06)
leak=mat('RF19_softened_old_wall_leak',(.042,.066,.043),.99,0,.10)
nodes=leak.node_tree.nodes;links=leak.node_tree.links;out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');surface=out.inputs['Surface'].links[0].from_socket
transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.67
links.new(transparent.outputs[0],mix.inputs[1]);links.new(surface,mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
M['old_leak']=leak
for j,(x,width,top,bottom,bay) in enumerate([(-2.59,.25,3.86,1.67,1),(-3.57,.16,4.19,2.46,1),(.25,.13,3.98,2.15,2)]):
 vertices=[];faces=[];steps=30
 for k in range(steps+1):
  t=k/steps;z=top+(bottom-top)*t
  # Width tapers toward gravity-driven tails; broad irregularity stays calm.
  centre=x+.028*math.sin(t*8+j)+.014*math.sin(t*21+j)
  half=width*(.5*(1-t)**.42+.025)*(.86+.14*math.sin(t*19+j))
  vertices.extend([(centre-half,6.37998,z),(centre+half,6.37998,z)])
 for k in range(steps):faces.append((2*k,2*k+2,2*k+3,2*k+1))
 stain=mesh('Gravity-shaped old service leak '+str(j),vertices,faces,'old_leak')
 for polygon in stain.data.polygons:
  if polygon.normal.y>0:polygon.flip()
 target='RF1 | North acoustic concrete bay '+str(bay)
 support(stain.name,vertices[0],target,(0,1,0))
 # Small irregular losses at the damp tail; avoid graphic-scale angular shapes.
 pts=[(x-.10,bottom+.44),(x-.036,bottom+.48),(x+.047,bottom+.40),(x+.083,bottom+.24),(x+.064,bottom+.10),(x-.018,bottom+.08),(x-.092,bottom+.19),(x-.075,bottom+.30)]
 chip=north_mark('Local flaked paint at leak tail '+str(j),pts,'old_plaster',target)
 for polygon in chip.data.polygons:
  if polygon.normal.y>0:polygon.flip()

# Crooked service notice still hangs from its original physical pin. Its mark
# group rotates rigidly with the paper, preserving the printed-face contracts.
paper=bpy.data.objects['RF1 | Pinned shift paper 1'];pin=bpy.data.objects['RF1 | Drawing pin.001'];pivot=pin.matrix_world.translation.copy()
marks=[o for o in s.objects if o.name.startswith(('RF1 | Board pump service header','RF1 | Pump sketch case','RF1 | Pump schematic line','RF1 | Pump scribbled note'))]
rotation=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-11),4,'Y')@Matrix.Translation(-pivot)
rigid_group([paper]+marks,rotation)

# Separate and misalign the actual leather gloves (not food). Keep both complete
# groups within the measured timber; avoid spilling unrelated props into routes.
table=bpy.data.objects['RF1 | Workbench timber top'];tl,th=bounds_world(table)
for g,offset,angle in [(0,(-.30,.06,0),.16),(1,(-.14,.12,0),-.58)]:
 suffix='' if g==0 else '.001'
 names=['RF1 | Work glove palm'+suffix,'RF1 | Glove gauntlet cuff'+suffix,'RF1 | Glove thumb'+suffix]
 names += ['RF1 | Glove finger'+('' if k==0 else '.'+str(k).zfill(3)) for k in range(g*4,g*4+4)]
 group=[bpy.data.objects[name] for name in names];pivot=group[0].matrix_world.translation.copy()
 change=Matrix.Translation(Vector(offset))@Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)
 rigid_group(group,change);bpy.context.view_layer.update()
 bounds=[bounds_world(o) for o in group]
 low=Vector([min(lo[i] for lo,hi in bounds) for i in range(3)]);high=Vector([max(hi[i] for lo,hi in bounds) for i in range(3)])
 shift=Vector((0,0,0))
 for axis in [0,1]:
  if low[axis]<tl[axis]+.022:shift[axis]=tl[axis]+.022-low[axis]
  if high[axis]+shift[axis]>th[axis]-.022:shift[axis]=th[axis]-.022-high[axis]
 if shift.length:rigid_group(group,Matrix.Translation(shift))
 support(group[0].name,tuple(group[0].matrix_world@Vector((0,0,0)) - Vector((0,0,.011))),table.name,(0,0,-1))

# Empty cup knocked onto its side. Remove the liquid disk before tipping, seat
# the complete mug/handle group on the real worktop, and add a dry spill film.
coffee=bpy.data.objects.get('RF1 | Coffee surface')
if coffee:remove_object(coffee)
mug=bpy.data.objects['RF1 | Worker enamel mug'];handle=bpy.data.objects['RF1 | Mug handle'];pivot=mug.matrix_world.translation.copy()
change=Matrix.Translation(Vector((.22,0,0)))@Matrix.Translation(pivot)@Matrix.Rotation(-math.pi/2,4,'Y')@Matrix.Translation(-pivot)
rigid_group([mug,handle],change);bpy.context.view_layer.update()
lowest=min((o.matrix_world@v.co for o in [mug,handle] for v in o.data.vertices),key=lambda point:point.z)
raise_by=th.z-lowest.z;rigid_group([mug,handle],Matrix.Translation(Vector((0,0,raise_by))))
lowest=min((mug.matrix_world@v.co for v in mug.data.vertices),key=lambda point:point.z)
for record in supports:
 if record['group']=='Enamel mug':record['anchor']=list(lowest)
spill_points=[(.827,-5.621),(.852,-5.663),(.912,-5.661),(.954,-5.635),(1.017,-5.611),(1.028,-5.568),(.979,-5.551),(.934,-5.535),(.884,-5.558),(.846,-5.569)]
spill=mesh('Nook old dried coffee spill',[(x,y,th.z+.00002) for x,y in spill_points],[tuple(range(len(spill_points)))],'grease')
support(spill.name,(.912,-5.61,th.z+.00002),table.name,(0,0,-1))

# Local task visibility is restored by existing actual lamps only. Keep the
# ceiling dark; dull visible lens luminance so strips no longer dominate pixels.
for key,energy in [('Press task bar',24),('Inspection sample practical',16),('Fuel transfer wall bulkhead',16)]:
 bpy.data.objects['RF1 LIGHT | '+key].data.energy=energy
for light in [o for o in s.objects if o.type=='LIGHT' and o.data.energy>0]:
 lens=bpy.data.objects[light['fixture_lens']]
 for material in lens.data.materials:
  for node in material.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':node.inputs['Emission Strength'].default_value=.65
bpy.context.view_layer.update()
