"""R08: compact sensing, coherent hero illumination and localized worker equipment."""
# The scanner is a narrow folded reader above the existing optical cradle.
retire=['Sorter folded optical hood','Sorter optical front gasket','Sorter amber scan window','Optical hood captive screw','Sorter small bay number','Optical hood side vent','Sorter optical housing underside socket']
for o in list(s.objects):
 if o.name.startswith('RF1 | ') and any(q in o.name for q in retire):remove_object(o)
profile=[(-.41,1.942),(.41,1.942),(.41,2.035),(.31,2.108),(-.31,2.108),(-.41,2.035)]
vs=[(-2.75+x,y,z) for y in [4.54,5.40] for x,z in profile];K=len(profile)
fs=[tuple(range(K)),tuple(reversed(range(K,2*K)))]+[(i,i+K,(i+1)%K+K,(i+1)%K) for i in range(K)]
hood=positive(mesh('Sorter compact folded reader',vs,fs,'ivory'));bevel(hood,.003)
box('Sorter compact reader front seal',(-2.75,4.531,2.013),(.49,.018,.064),'dark',.001)
quiet_amber=mat('RF1_reader_status_glass',(.72,.23,.035),.38,0,0,.5)
box('Sorter compact status slit',(-2.75,4.520,2.013),(.38,.004,.027),quiet_amber,.001)
for x in [-3.10,-2.40]:cyl('Reader captive front bolt',(x,4.532,2.004),.014,.014,'steel',(0,-1,0),6)
text('Reader stamped bay id','04',(-3.10,4.532,2.065),.040,'green')
for z in [1.975,2.027]:box('Compact reader rear vent',(-2.337,4.96,z),(.004,.22,.011),'dark',0)
# Four measured frame feet stay put; slimmer uprights finish at the housing underside.
posts=[o for o in s.objects if o.name.startswith('RF1 | Sorter optical cast upright')]
for o in posts:
 lo,hi=bounds_world(o);p=(lo+hi)/2;remove_object(o)
 upright=rod('Sorter reader seated upright',(p.x,p.y,1.353),(p.x,p.y,1.942),.028,'dark')
 # Existing feet are nominated by their measured center rather than suffix order.
 foot=min([o for o in s.objects if o.name.startswith('RF1 | Sorter optical foot bracket')],key=lambda o:(o.matrix_world.translation-Vector((p.x,p.y,1.334))).length)
 support(upright.name,(p.x,p.y,1.353),foot.name,(0,0,-1))
 support(hood.name,(p.x,p.y,1.942),upright.name,(0,0,-1))
old=bpy.data.objects.get('RF1 | Sorter sensor power cable')
if old:remove_object(old)
pipe('Sorter compact reader power lead',[(-3.06,5.385,2.05),(-3.11,5.86,2.20),(-3.28,6.25,2.88),(-3.28,6.34,3.16)],.016,'black')

# Retire the added dummy three-button pedestal; the original interactive press controls remain.
for o in list(s.objects):
 if o.name.startswith(('RF1 | Fabrication control pedestal','RF1 | Fabrication control housing','RF1 | Fabrication push button')):remove_object(o)
supports[:]=[r for r in supports if r['group']!='RF1 | Fabrication control pedestal']

# A smaller temperature instrument is mounted at the original screw gearbox, not a second hero dial.
case=bpy.data.objects['Processor_temperature_gauge_case'];pivot=case.matrix_world.translation.copy()
rigid_group([o for o in s.objects if o.name.startswith('Processor_temperature_gauge') or o.name.startswith('ART_Processor_temperature_gauge')],Matrix.Translation(pivot)@Matrix.Diagonal((.72,.72,.72,1))@Matrix.Translation(-pivot))

# Remove the old table-frame scaffold below the pressure vessel.
for o in list(s.objects):
 if any(o.name.startswith(p) for p in ['PROCESSOR_foot','PROCESSOR_leg','PROCESSOR_rail','PROCESSOR_cross','ART_PROCESSOR_foot','RF1 | PV05 cast saddle']):
  remove_object(o);continue
 if o.name.startswith('RF1 | Machine stand diagonal brace'):
  lo,hi=bounds_world(o)
  if lo.x>.10 and hi.x<2.1:remove_object(o)
plinth=bpy.data.objects['RF1 | PV05 service plinth']
support(plinth.name,(1.043,4.984,0),'Floor',(0,0,-1))
body=bpy.data.objects['RF1 | PV05 cast pressure vessel']
# Exact formed bearing faces are cut from the pressure body; base bottoms meet the plinth.
for x in [.44,1.65]:
 yoke=plate('Pressure vessel formed bearing yoke',(x,4.984,.695),.14,.590,1.05,'dark',.055)
 if REV>=9:
  for modifier in list(yoke.modifiers):yoke.modifiers.remove(modifier)
 boolean=yoke.modifiers.new('Dish-shaped bearing seat','BOOLEAN');boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.object=body
 bpy.context.view_layer.objects.active=yoke;yoke.select_set(True);bpy.ops.object.modifier_apply(modifier=boolean.name);yoke.select_set(False)
 if REV>=9:bevel(yoke,.002)
 support(yoke.name,(x,4.984,.400),plinth.name,(0,0,-1))
 # Bearings and their body interface share the same exact contour after the cut.
 for y in [4.53,5.43]:cyl('Pressure yoke plinth bolt',(x,y,.427),.023,.054,'steel',(0,0,1),6)

# The vessel service ledge is carried by cantilever ribs from its cast plinth.
for o in list(s.objects):
 if any(o.name.startswith(p) for p in ['Processor_service_ledge_foot','Processor_service_ledge_leg','Processor_service_ledge_rail','Processor_service_ledge_cross','ART_Processor_service_ledge_foot']):remove_object(o)
for x in [.71,1.37]:
 yz=[(4.255,.365),(4.255,.825),(3.804,.825),(3.804,.768)]
 vs=[(xx,y,z) for xx in [x-.045,x+.045] for y,z in yz]
 rib=positive(mesh('PV service shelf cast cantilever',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'dark'));bevel(rib,.002)
 support(rib.name,(x,4.255,.380),plinth.name,(0,1,0))
 support('PV supported service shelf',(x,3.95,.825),rib.name,(0,0,-1))

# Folded filter storage replaces the dryer's second generic four-legged table.
for o in list(s.objects):
 if any(o.name.startswith(p) for p in ['Dryer_filter_service_ledge_foot','Dryer_filter_service_ledge_leg','Dryer_filter_service_ledge_rail','Dryer_filter_service_ledge_cross','ART_Dryer_filter_service_ledge_foot']):remove_object(o)
toe=box('Filter service cabinet toe',(3.493,3.974,.060),(.84,.29,.12),'dark',.002)
support(toe.name,(3.493,3.974,0),'Floor',(0,0,-1))
cab=box('Filter folded service cabinet',(3.493,3.974,.493),(.83,.31,.746),'green',.003)
support(cab.name,(3.493,3.974,.12),toe.name,(0,0,-1))
support('Dryer service worktop',(3.493,3.974,.866),cab.name,(0,0,-1))
cover=plate('Filter cabinet access sheet',(3.493,3.811,.515),.69,.55,.014,'ivory',.040)
support(cover.name,(3.493,3.818,.515),cab.name,(0,1,0))
rod('Filter cabinet recessed pull',(3.37,3.789,.685),(3.61,3.789,.685),.011,'dark')
text('Filter cabinet purpose','FILTER STOCK / 06',(3.245,3.801,.425),.038,'green')

# Diagnostic normal/128-sample passes showed shadows, not geometric dents.
# Hero fixtures now hang from the existing front girder, with large true apertures.
for o in list(s.objects):
 if o.name.startswith(('RF1 | PV task wall anchor','RF1 | PV task arm','RF1 | PV task folded hood','RF1 | PV task actual lens','RF1 | PV aimed reflector hinge')):remove_object(o)
supports[:]=[r for r in supports if not r['group'].startswith('RF1 | PV task wall anchor')]
for i,x in enumerate([.46,1.66]):
 clamp=box('PV overhead girder clamp',(x,3.86,4.5235),(.14,.28,.048),'dark',.002)
 support(clamp.name,(x,3.86,4.5475),'RF1 | I girder lower flange.002',(0,0,1))
 for yy in [3.77,3.95]:rod('PV suspended task fixture stay',(x,yy,4.4995),(x,yy,3.726),.013,'steel')
 housing=plate('PV suspended task reflector',(x,3.86,3.686),.66,.080,.30,'dark',.020)
 lens=box('PV suspended task diffuser',(x,3.86,3.642),(.56,.24,.006),'lens',.001)
 support(housing.name,(x,3.77,3.726),'RF1 | PV suspended task fixture stay'+('' if i==0 else '.002'),(0,0,1))
 lamp=bpy.data.objects['RF1 LIGHT | PV hood '+str(i)];lamp.location=(x,3.86,3.634);lamp.rotation_euler=(0,0,0);lamp.data.size=.55;lamp.data.size_y=.23;lamp.data.energy=95;lamp['fixture_lens']=lens.name
 for record in lights:
  if record['name']==lamp.name:record['lens']=lens.name
 # Housing/lens share an assembly; it is carried by the two steel stays above.
 lens['support_group']=housing.name

# Hearing protection hangs from the crusher's existing service casting.
start=len(new)
back=box('Ear defender hook mounting plate',(-4.48,4.313,1.78),(.095,.022,.10),'dark',.002)
support(back.name,(-4.48,4.324,1.78),'Crusher_southeast_service_mount',(0,1,0))
rod('Ear defender hook arm',(-4.48,4.302,1.78),(-4.48,4.21,1.78),.012,'steel')
hook=rod('Ear defender retaining hook',(-4.48,4.21,1.78),(-4.48,4.21,1.830),.012,'steel')
band=pipe('Worker ear defender headband',[(-4.62,4.21,1.63),(-4.62,4.21,1.78),(-4.48,4.21,1.842),(-4.34,4.21,1.78),(-4.34,4.21,1.63)],.013,'black')
support(band.name,(-4.48,4.21,1.829),hook.name,(0,0,-1))
for side in [-1,1]:
 x=-4.48+side*.15
 cushion=cyl('Ear defender soft sealing pad',(x-side*.022,4.21,1.63),.084,.039,'black',(side,0,0),20);cushion.scale.y=.76;cushion.scale.z=1.18
 cup=cyl('Ear defender ochre cup',(x+side*.011,4.21,1.63),.079,.038,'ochre',(side,0,0),20);cup.scale.y=.76;cup.scale.z=1.18
 cyl('Ear defender cup pivot',(x+side*.033,4.21,1.63),.017,.015,'dark',(side,0,0),12)
for name in new[start:]:
 o=bpy.data.objects.get(name)
 if o and o!=back:o['support_group']=back.name

# A signed lockout inspection tag moves with the actual interactive hatch.
start=len(new);dog=bpy.data.objects['RF1 | PV hatch bridge dog.001']
clip=box('PV service ticket spring clip',(1.23,4.037,1.58),(.034,.012,.045),'steel',.001)
support(clip.name,(1.23,4.042,1.58),dog.name,(0,1,0))
rod('PV signed tag wire',(1.23,4.030,1.557),(1.21,4.030,1.443),.0025,'steel',8)
tag_paper=plate('PV signed service tag',(1.21,4.027,1.367),.104,.150,.002,'paper',.012)
text('PV worker tag checked','CHECKED',(1.166,4.024,1.395),.017,'ink')
text('PV worker tag shift','07 / M.A.',(1.166,4.024,1.358),.016,'ink')
box('PV tag approval ink',(1.21,4.024,1.327),(.077,.001,.008),'green',0)
bpy.context.view_layer.update()
for name in new[start:]:
 o=bpy.data.objects.get(name)
 if o:
  world=o.matrix_world.copy();o.parent=bpy.data.objects['Processor_sealed_hatch'];o.matrix_world=world;o['support_group']=clip.name
