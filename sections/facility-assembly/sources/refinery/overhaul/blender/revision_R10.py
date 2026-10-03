"""R10: distinct folded machine construction, seated marks and broader practical apertures."""

# Set world poses explicitly on hatch children. Their parent frame is rotated.
for name, point in [('PV worker tag checked',(1.166,4.02599,1.395)),
                    ('PV worker tag shift',(1.166,4.02599,1.358)),
                    ('PV tag approval ink',(1.21,4.02597,1.327))]:
 o=bpy.data.objects['RF1 | '+name];bpy.context.view_layer.update()
 world=o.matrix_world.copy();world.translation=Vector(point);o.matrix_world=world
 bpy.context.view_layer.update()
 assert (o.matrix_world.translation-Vector(point)).length<1e-5
s['printed_surface_registry']=json.dumps([dict(mark='RF1 | '+name,target='RF1 | PV signed service tag',direction=[0,1,0]) for name in ['PV worker tag checked','PV worker tag shift','PV tag approval ink']])
for o in s.objects:
 if o.name.startswith(('RF1 | Ear defender soft sealing pad','RF1 | Ear defender ochre cup')):
  # Cylinder Z follows world X; local X follows world Y, and local Y follows world Z.
  o.scale=(.76,1.18,1.0)

# Two rear folded cantilevers expose the conveyor instead of four gate posts.
retired_reader=[]
for o in list(s.objects):
 if o.name.startswith('RF1 | Sorter reader seated upright'):
  retired_reader.append(o.name);remove_object(o)
 elif o.name.startswith('RF1 | Sorter optical foot bracket') and o.matrix_world.translation.y<5:
  retired_reader.append(o.name);remove_object(o)
supports[:]=[r for r in supports if r['group'] not in retired_reader and r['target'] not in retired_reader]
hood=bpy.data.objects['RF1 | Sorter compact folded reader']
for vertex in hood.data.vertices:
 if vertex.co.y>5:vertex.co.y=5.24
rear_feet=[o for o in s.objects if o.name.startswith('RF1 | Sorter optical foot bracket')]
for foot in rear_feet:
 x=foot.matrix_world.translation.x
 yz=[(5.36,1.353),(5.28,1.353),(5.28,1.892),(4.66,1.892),(4.66,1.942),(5.36,1.942)]
 vs=[(xx,y,z) for xx in [x-.028,x+.028] for y,z in yz];N=len(yz)
 fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 arm=positive(mesh('Reader folded rear cantilever',vs,fs,'dark'));bevel(arm,.002)
 support(arm.name,(x,5.33,1.353),foot.name,(0,0,-1))
 support(hood.name,(x,5.10,1.942),arm.name,(0,0,-1))
cradle=bpy.data.objects['RF1 | Sorter internal optical cradle'];cradle.location.z+=.001
support(cradle.name,(-2.73,4.934,1.942),hood.name,(0,0,1))
lead=bpy.data.objects['RF1 | Sorter compact reader power lead']
lead.data.splines[0].bezier_points[0].co.y=5.225

# The crusher has a recessed jaw in a folded surround rather than a solid flat badge.
for name in ['RF1 | Crusher angular front cowling','RF1 | Crusher mouth gasket','Crusher_feed_throat']:
 o=bpy.data.objects.get(name)
 if o:remove_object(o)
def clipped_profile(width,height,cut,cx=-5.56,cz=2.62):
 x,z=width/2,height/2
 return [(cx+a,cz+b) for a,b in [(-x+cut,-z),(x-cut,-z),(x,-z+cut),(x,z-cut),(x-cut,z),(-x+cut,z),(-x,z-cut),(-x,-z+cut)]]
def folded_ring(name,outer,inner,front,back,material):
 vs=[(x,y,z) for y,ps in [(front,outer),(back,outer),(front,inner),(back,inner)] for x,z in ps]
 fs=[]
 for i in range(8):
  j=(i+1)%8
  fs += [(i,j,16+j,16+i),(8+i,24+i,24+j,8+j),
         (i,8+i,8+j,j),(16+i,16+j,24+j,24+i)]
 return bevel(positive(mesh(name,vs,fs,material)),.002)
outer=clipped_profile(2.0,1.13,.20)
inner=clipped_profile(1.28,.65,.035,cz=2.58)
surround=folded_ring('Crusher folded jaw surround',outer,inner,4.000,4.100,'oxide')
gasket=folded_ring('Crusher jaw recessed lip',clipped_profile(1.32,.69,.035,cz=2.58),
                   clipped_profile(1.17,.54,.035,cz=2.58),3.996,4.024,'black')
support(gasket.name,(-6.21,4.000,2.58),surround.name,(0,1,0))
back=bpy.data.objects['RF1 | Crusher jaw shadow'];back.location.y=4.315
for o in s.objects:
 if o.name.startswith('RF1 | Crusher worn tooth'):o.location.y=4.080
cheek=bpy.data.objects['Crusher_cast_cheek'];cheek_lo,cheek_hi=bounds_world(cheek)
for x in [-6.40,-4.72]:
 mount=box('Crusher jaw cast mounting shoe',(x,(4.100+cheek_lo.y)/2,2.18),(.085,cheek_lo.y-4.100,.08),'dark',.002)
 support(mount.name,(x,cheek_lo.y,2.18),cheek.name,(0,1,0))
 support(surround.name,(x,4.100,2.18),mount.name,(0,1,0))
# A tapered folded roof reads as pressed sheet rather than an oversized rectangular block.
roof=bpy.data.objects['Crusher_feed_hood_roof']
for child in list(roof.children):
 if child.name.startswith('ART_'):remove_object(child)
profile=[(-6.611664,3.070),(-6.336664,3.190),(-4.976664,3.190),(-4.701664,3.070),
         (-4.701664,3.105),(-4.976664,3.225),(-6.336664,3.225),(-6.611664,3.105)]
vs=[roof.matrix_world.inverted()@Vector((x,y,z)) for y in [4.444283,5.564283] for x,z in profile]
N=len(profile);fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
me=bpy.data.meshes.new('Crusher pressed roof');me.from_pydata(vs,[],fs);me.materials.append(M['ivory']);roof.data=me;positive(roof)

# Retain every original interactive button and name, but distinguish each station's case.
control_material={'RECEIVING':'dark','CRUSHER':'dark','SORTER':'ivory',
                  'DRYER':'oxide_edge','ASSEMBLY':'green','INSPECTION':'ivory'}
for prefix,material in control_material.items():
 o=bpy.data.objects[prefix+'_Control_enclosure']
 for index in range(len(o.data.materials)):o.data.materials[index]=M[material]
 # A formed weather lip belongs to ore-handling controls, not every station.
 if prefix not in ['RECEIVING','CRUSHER']:continue
 bpy.context.view_layer.update();matrix=o.matrix_world.copy();inv=matrix.inverted()
 coords=[v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 thin=min(range(3),key=lambda i:hi[i]-lo[i]);plane=[i for i in range(3) if i!=thin]
 vertical=max(plane,key=lambda i:abs(matrix.col[i].z));horizontal=next(i for i in plane if i!=vertical)
 buttons=[p for p in s.objects if p.name.startswith(prefix+'_') and '_button' in p.name]
 assert buttons
 average=sum((inv@p.matrix_world.translation)[thin] for p in buttons)/len(buttons)
 front=lo[thin] if abs(average-lo[thin])<abs(average-hi[thin]) else hi[thin]
 normal_sign=-1 if front==lo[thin] else 1
 top=hi[vertical] if matrix.col[vertical].z>0 else lo[vertical]
 center=(lo+hi)/2;center[thin]=front+normal_sign*.008;center[vertical]=top-math.copysign(.010,matrix.col[vertical].z)
 dims=hi-lo;dims[thin]=.018;dims[vertical]=.025
 lip=box(prefix+' folded console weather lip',center,dims,'ochre',.001);lip.matrix_world=matrix@Matrix.Translation(center)
 anchor=center.copy();anchor[thin]=front
 direction=Vector((0,0,0));direction[thin]=-normal_sign
 support(lip.name,matrix@anchor,o.name,(matrix.to_3x3()@direction).normalized())

# Broad real diffuser panes soften the small instrumentation's projected shadows.
clips=[o for o in s.objects if o.name.startswith('RF1 | PV diffuser folded edge retainer')]
clip_names={o.name for o in clips}
supports[:]=[r for r in supports if r['group'] not in clip_names]
for o in clips:remove_object(o)
for i,x in enumerate([.46,1.66]):
 suffix='' if i==0 else '.001'
 housing=bpy.data.objects['RF1 | PV suspended task reflector'+suffix];housing.scale.x=1.18/.66;housing.scale.y=.39/.30
 lens=bpy.data.objects['RF1 | PV suspended task diffuser'+suffix];lens.scale.x=1.04/.56;lens.scale.y=.33/.24
 lamp=bpy.data.objects['RF1 LIGHT | PV hood '+str(i)];lamp.data.size=1.03;lamp.data.size_y=.32
 for xx in [x-.526,x+.526]:
  clip=box('PV broad diffuser folded retainer',(xx,3.86,3.6405),(.012,.365,.012),'steel',.001)
  support(clip.name,(xx,3.86,3.6465),housing.name,(0,0,1))

# The refined product hose visibly couples the preserved processor outlet to the dryer inlet.
inlet=cyl('Dryer product inlet flange',(2.894,4.970,1.520),.155,.035,'steel',(1,0,0),24)
support(inlet.name,(2.910,4.970,1.520),'RF1 | DR06 horizontal thermal drum',(1,0,0))
coupling=cyl('Processor product coupling',(2.448,4.898283,1.438),.146,.030,'steel',(1,0,0),24)
support(coupling.name,(2.433553,4.898283,1.575),'Processor_product_nozzle_flange',(-1,0,0))
hose=pipe('Refined product interstage hose',[(2.455,4.898283,1.438),(2.62,4.920,1.463),(2.77,4.951,1.50),(2.883,4.970,1.520)],.067,'dark')
hose['support_group']=coupling.name
support(hose.name,(2.462,4.898283,1.438),coupling.name,(-1,0,0))
for x,y,z in [(2.476,4.901,1.442),(2.863,4.967,1.516)]:ring('Interstage hose compression band',(x,y,z),.069,.006,'steel',(1,0,0))

# Use marks belong on the actual ore-contact jaw, inspection ledge and service handles.
for x,z,width in [(-6.13,2.258,.13),(-5.71,2.254,.16),(-5.04,2.254,.10)]:
 box('Crusher jaw abrasion',(x,3.995,z),(width,.001,.010),'steel',0)
for y in [-3.14,-2.94]:box('Inspection loading sill rub',(4.927,y,1.0428),(.085,.033,.0005),'steel',0)
bpy.context.view_layer.update()
