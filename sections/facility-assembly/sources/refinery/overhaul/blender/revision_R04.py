"""R04 structural correction. Executed by build_overhaul.py in its authoring context."""
def rigid_group(objects, transform):
 bpy.context.view_layer.update()
 matrices={o.name:o.matrix_world.copy() for o in objects}
 def level(o):
  k=0
  while o.parent:k+=1;o=o.parent
  return k
 for o in sorted(objects,key=level):o.matrix_world=transform@matrices[o.name]
 bpy.context.view_layer.update()

def bounds_world(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return Vector([min(p[i] for p in ps) for i in range(3)]),Vector([max(p[i] for p in ps) for i in range(3)])

# Compact operator console: retain component identities, scale the whole head once.
head=bpy.data.objects['CRUSHER_Control_enclosure'];pivot=head.matrix_world.translation.copy()
members=[o for o in s.objects if (o.name.startswith('CRUSHER_') or o.name.startswith('ART_CRUSHER_')) and any(q in o.name for q in ['_button','_engraving','Control_enclosure'])]
transform=Matrix.Translation(Vector((-.29,.12,0)))@Matrix.Translation(pivot)@Matrix.Diagonal((.78,.96,.91,1))@Matrix.Translation(-pivot)
rigid_group(members,transform)
# The control head remains mounted to the crusher casting via a short steel outrigger.
rod('Crusher console cast support',(-4.52,4.10,1.0),(-4.64,3.80,1.10),.039,'dark')

# Function-specific controls break the repeated anonymous button rows.
rotary_words=['SPEED','SENSITIVITY','DIVERTER','INCREASE_HEAT','ALIGNMENT','SIZE_GATE','BLEND']
for o in list(s.objects):
 if o.type!='MESH' or not o.name.endswith('_button'):continue
 rotary=any(q in o.name for q in rotary_words)
 matrix=o.matrix_world.copy()
 if rotary:
  o.data.materials[0]=M['black']
  start=len(new)
  cap=box(o.name+' selector grip',(0,0,.025),(.032,.075,.022),'black',.003)
  box(o.name+' ivory index',(0,.014,.037),(.005,.027,.002),'ivory',0)
  bpy.context.view_layer.update()
  for n in new[start:]:
   part=bpy.data.objects[n];part.matrix_world=matrix@part.matrix_world
   world_matrix=part.matrix_world.copy();part.parent=o;part.matrix_world=world_matrix
 elif 'EMERGENCY' in o.name or '_STOP_' in o.name:
  o.data.materials[0]=M['red']
  start=len(new)
  cyl(o.name+' mushroom cap',(0,0,.027),.053,.028,'red',(0,0,1),24)
  ring(o.name+' emergency collar',(0,0,-.023),.054,.012,'ochre')
  bpy.context.view_layer.update()
  for n in new[start:]:
   part=bpy.data.objects[n];part.matrix_world=matrix@part.matrix_world
   world_matrix=part.matrix_world.copy();part.parent=o;part.matrix_world=world_matrix
 else:
  # Distinct calm state controls, without more screen clutter.
  o.data.materials[0]=M['ivory' if 'CHECK' in o.name or 'LATCH' in o.name else 'green']

# Park the service cart inside the process bay rather than the entry foreground.
cart_terms=['Service cart','Caster metal','Caster fork','Cart drawer','Cart tray','Cart tubular','Cart service','Spanner','Cart spare','Bearing visible','Service bottle','Bottle ribbed','Bottle taped','Folded cart','Cart maintenance']
cart_members=[bpy.data.objects[n] for n in new if bpy.data.objects.get(n) and any(q in n for q in cart_terms)]
rigid_group(cart_members,Matrix.Translation(Vector((1.20,1.02,0))))
for r in supports:
 if r['group']=='MaintenanceCart':r['anchor'][0]+=1.20;r['anchor'][1]+=1.02
# Two short boundaries mark a parked servicing spot, never a barrier in the aisle.
for xx in [-2.67,-1.74]:box('Service parking paint',(xx,3.69,.0032),(.028,.64,.001),'ivory',0)
text('Service parked stencil','SERVICE',(-2.48,3.37,.004),.08,'ivory',(0,0,0))

# Crusher foundation now has cast side yokes, no repeated four-legged table read.
for o in list(s.objects):
 if any(o.name.startswith(q) for q in ['CRUSHER_foot','CRUSHER_leg','CRUSHER_rail','CRUSHER_cross','ART_CRUSHER_foot','RF1 | Machine stand diagonal brace']):
  if o.name.startswith('RF1 | Machine stand'):
   lo,hi=bounds_world(o)
   if lo.x>-4.4:continue
  remove_object(o)
for x in [-6.65,-4.42]:
 foot=box('Crusher cast yoke sole',(x,4.884,.06),(.46,1.81,.12),'dark',.004)
 support(foot.name,(x,4.884,0),'Floor',(0,0,-1))
 plate('Crusher heavy cast yoke',(x,4.884,.61),.31,.98,1.63,'dark',.09)
 box('Crusher sole worn edge',(x,4.014,.095),(.43,.036,.023),'steel',.002)
 for y in [4.12,5.65]:
  cyl('Crusher sole anchor bolt',(x,y,.145),.037,.05,'steel',(0,0,1),6)
  ring('Crusher anchor washer',(x,y,.126),.045,.009,'steel')
rod('Crusher underbody drive brace',(-6.65,5.53,.77),(-4.42,5.53,.29),.04,'dark')

# Keep the two original functional gauges; retire the added duplicate pair.
for o in list(s.objects):
 if o.name.startswith('RF1 | ') and any(q in o.name for q in ['Pressure gauge backing','Pressure gauge ivory face','Gauge tick','Gauge needle']):remove_object(o)
for prefix,delta in [('Processor_pressure_gauge',(.006,-.077,.095)),('Processor_temperature_gauge',(.020,-.077,.095))]:
 members=[o for o in s.objects if o.name.startswith(prefix) or o.name.startswith('ART_'+prefix)]
 rigid_group(members,Matrix.Translation(Vector(delta)))
for x in [.629,1.443]:
 rod('Vessel gauge welded standoff',(x,4.45,2.325),(x,4.28,2.325),.026,'dark')
 cyl('Gauge brass union',(x,4.32,2.325),.043,.061,'brass',(0,1,0),12)

# Access hatch: flange/gasket, raised dish, observation port, hinge and dog bridge.
hatch=bpy.data.objects['Processor_sealed_hatch'];hatch.data.materials[0]=M['oxide']
start=len(new)
ring('PV hatch rolled steel lip',(1.043,4.218,1.71),.336,.013,'steel',(0,-1,0))
ring('PV hatch peripheral gasket',(1.043,4.225,1.71),.35,.009,'black',(0,-1,0))
dish=lathe('PV dished service cover',(1.043,4.225,1.71),[(0,.292),(.045,.257),(.065,.21),(.070,.10)],'oxide',32)
dish.rotation_mode='QUATERNION';dish.rotation_quaternion=Vector((0,-1,0)).to_track_quat('Z','Y')
cyl('PV observation port casing',(1.043,4.137,1.78),.089,.038,'dark',(0,-1,0))
cyl('PV observation port glass',(1.043,4.116,1.78),.063,.004,'black',(0,-1,0))
ring('PV sightport brass seal',(1.043,4.110,1.78),.071,.007,'brass',(0,-1,0))
# Simple cast locking bridge leaves the port visible and reads at gameplay distance.
plate('PV service hatch locking bridge',(1.043,4.10,1.58),.46,.070,.04,'dark',.013)
for x in [.856,1.23]:cyl('PV hatch bridge dog',(x,4.061,1.58),.026,.04,'steel',(0,-1,0),6)
rod('PV hatch lever',(1.05,4.073,1.58),(1.12,4.07,1.70),.014,'steel')
cyl('PV hatch lever grip',(1.135,4.07,1.726),.023,.105,'black',(.5,0,1))
rod('PV hatch hinge pin',(.70,4.26,1.57),(.70,4.26,1.91),.024,'steel')
for z in [1.61,1.86]:
 box('PV hinge strap',(.775,4.22,z),(.19,.035,.065),'dark',.004)
 cyl('PV hinge knuckle',(.70,4.26,z),.039,.070,'steel')
# Added hatch dressing follows the retained interactive hatch when moved/opened.
bpy.context.view_layer.update()
for n in new[start:]:
 o=bpy.data.objects[n];matrix=o.matrix_world.copy();o.parent=hatch;o.matrix_world=matrix

# Complete the manifold return instead of ending a pipe in open air.
pipe('PV cooled return route',[(2.12,4.02,.44),(2.26,4.10,.30),(2.26,5.89,.30),(2.26,6.31,.80)],.042,'steel')
wall=box('PV return wall union',(2.26,6.396,.80),(.19,.075,.19),'dark',.003)
support(wall.name,(2.26,6.4335,.80),'North_wall',(0,1,0))
for y in [4.32,5.35]:ring('Return bolted union',(2.26,y,.30),.069,.016,'dark',(0,1,0))
for y in [4.9,5.65]:
 base=box('Return floor pipe saddle',(2.26,y,.035),(.17,.14,.070),'dark',.002)
 support(base.name,(2.26,y,0),'Floor',(0,0,-1));rod('Return pipe saddle stem',(2.26,y,.07),(2.26,y,.30),.021,'dark')

# Selective enamel loss is authored on handling points, not noisy full-surface damage.
for theta,z,w,h in [(-1.94,1.12,.042,.11),(-1.1,2.45,.06,.025),(-1.62,2.45,.041,.018),(-1.48,1.06,.067,.022),(-2.01,1.8,.026,.038)]:
 vs=[]
 for dt,dz in [(-w/1.32,-h/2),(w/1.32,-h*.38),(w*.8/1.32,h/2),(-w*.7/1.32,h*.36)]:
  a=theta+dt;vs.append((1.043+.662*math.cos(a),4.984+.662*math.sin(a),z+dz))
 mesh('PV handling edge enamel chip',vs,[(0,1,2,3)],'steel')
# Flat hatch corners carry small metal chips and softened rub marks.
for x,z in [(3.61,1.93),(4.52,1.18),(3.65,1.19),(4.61,1.89)]:
 chip=mesh('Dryer access hand-worn enamel',[(x,4.242,z),(x+.031,4.242,z+.004),(x+.02,4.242,z+.022)],[(0,1,2)],'steel')

# A hung work apron gives the cleanup corner a human silhouette without occupying routes.
apron_start=len(new)
hook=rod('Apron wall hook',(-4.08,-6.434,2.08),(-4.08,-6.27,2.08),.013,'steel')
support('Hung work apron',(-4.08,-6.433,2.08),'South_left',(0,-1,0))
outline=[(-.15,1.80),(.15,1.80),(.17,1.53),(.29,1.42),(.30,.97),(.22,.91),(-.21,.90),(-.29,.96),(-.28,1.42),(-.17,1.53)]
verts=[(-4.08+x,-6.28+.02*math.sin(z*6),z) for x,z in outline]
apron=mesh('Worker heavy canvas apron',verts,[tuple(range(len(verts)))],'leather');sol=apron.modifiers.new('Canvas thickness','SOLIDIFY');sol.thickness=.004
for x in [-4.20,-3.96]:pipe('Apron neck strap',[(x,-6.28,1.78),(x,-6.28,1.94),(-4.08,-6.28,2.08)],.010,'leather')
box('Apron stitched pocket',(-4.08,-6.248,1.27),(.26,.014,.18),'wood',.003)
for x in [-4.203,-3.956]:rod('Apron pocket seam',(x,-6.236,1.19),(x,-6.236,1.355),.0015,'ivory',6)
pipe('Apron waist tie',[(-4.36,-6.29,1.45),(-4.50,-6.29,1.4),(-4.46,-6.29,1.14)],.009,'leather')
# Ore crests visibly above the receiving-cart rim while remaining contained.
for o in s.objects:
 if o.name.startswith('RF1 | Ore load upper layer'):o.location.z+=.145

# An uncluttered inspection backdrop: mounted sample rack and current batch record.
rack=plate('Inspection wall sample rack',(7.4415,-2.27,1.91),.13,.83,1.28,'green',.025)
support(rack.name,(7.5065,-2.27,1.91),'East_main',(1,0,0))
for z in [1.58,1.88]:
 box('Sample wall rack tray',(7.20,-2.27,z),(.49,1.22,.033),'dark',.002)
 for y in [-2.65,-2.27,-1.89]:
  cyl('Wall retained sample canister',(7.17,y,z+.094),.065,.155,'steel')
  cyl('Wall sample bay cap',(7.17,y,z+.179),.068,.023,'green')
  box('Sample bay paper tag',(7.098,y,z+.105),(.003,.08,.045),'paper',0)
for z in [1.58,1.88]:rod('Sample retaining rail',(6.97,-2.91,z+.08),(6.97,-1.63,z+.08),.012,'steel')
# Resolve overlapping postcard / long shift paper in the worker nook.
postcard=bpy.data.objects['RF1 | Crew postcard'];postcard.location.z-=.11
note=bpy.data.objects['RF1 | Crew handwritten postcard'];note.location=(.69,-6.3078,1.75);note.data.size=.034
cyl('Crew postcard pin',(.69,-6.305,1.795),.008,.010,'red',(0,1,0),12)
