"""R05: architectural value grouping, inspection construction and tactile worker detail."""
# Two cool painted-concrete wings frame the warmer processing wall.
M['coolwall']=mat('RF1_cool_service_plaster',(.205,.248,.236),.91,0,.075)
M['ceiling']=mat('RF1_neutral_ceiling',(.245,.256,.236),.94,0,.04)
for o in s.objects:
 if o.type!='MESH':continue
 if o.name.startswith('RF1 | Side flush panel') or o.name in ['South_left','South_right','East_main','East_front_pier','West_main','West_front_pier']:
  for i,m in enumerate(o.data.materials):
   if m==M['warmwall'] or m==M['wallpatch']:o.data.materials[i]=M['coolwall']
 if o.name=='Ceiling':
  for i in range(len(o.data.materials)):o.data.materials[i]=M['ceiling']
# Material-specific grain is restrained and physically scaled; wood has long grain.
nodes=M['wood'].node_tree.nodes;links=M['wood'].node_tree.links
p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
tc=nodes.new('ShaderNodeTexCoord');vec=nodes.new('ShaderNodeVectorMath');vec.operation='MULTIPLY';vec.inputs[1].default_value=(1,13,4)
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=2
links.new(tc.outputs['Object'],vec.inputs[0]);links.new(vec.outputs[0],noise.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.15,.065,.026,1);ramp.color_ramp.elements[1].color=(.215,.110,.049,1)
links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],p.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.001
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
for key,low,high in [('steel',.31,.48),('oxide',.55,.70),('green',.61,.77),('concrete',.84,.96)]:
 nodes=M[key].node_tree.nodes;links=M[key].node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 tc=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=12;noise.inputs['Detail'].default_value=1
 links.new(tc.outputs['Object'],noise.inputs['Vector']);r=nodes.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=0;r.inputs['From Max'].default_value=1;r.inputs['To Min'].default_value=low;r.inputs['To Max'].default_value=high
 links.new(noise.outputs['Fac'],r.inputs['Value']);links.new(r.outputs['Result'],p.inputs['Roughness'])
# Cool forecourt practical balances warm process pools. It stays at its original visible lens.
bpy.data.objects['RF1 LIGHT | Ceiling pendant 0'].data.energy=155

# Inspection uses folded stainless furniture and an angled instrument bridge.
work=bpy.data.objects['Inspection_work_surface'];work.data.materials[0]=M['steel']
work.data.materials[1]=M['steel']
# The actual top remains at the measured 1.0425m, retaining every supported sample/record.
for y in [-3.375,-1.385]:
 box('Inspection worktop folded return',(5.806,y,1.015),(1.36,.024,.078),'steel',.002)
box('Inspection bench operator rolled lip',(5.142,-2.38,1.014),(.023,2.02,.078),'steel',.002)
# Under-counter storage has a kick recess, drawers and folded cabinet sides.
base=box('Inspection cabinet toe plinth',(6.115,-2.4,.059),(.60,1.59,.118),'dark',.002)
support(base.name,(6.115,-2.4,0),'Floor',(0,0,-1))
box('Inspection sheet cabinet',(6.105,-2.4,.50),(.63,1.62,.764),'green',.003)
for y in [-2.91,-2.40,-1.89]:
 box('Inspection cabinet folded door',(5.779,y,.55),(.018,.478,.62),'green',.002)
 rod('Inspection cabinet metal handle',(5.755,y-.10,.63),(5.755,y+.10,.63),.010,'steel')
 box('Inspection door paper label',(5.765,y,.75),(.002,.21,.052),'ivory',0)
# Custom tapered scanner cheeks replace the original straight table-like upright pair.
for o in list(s.objects):
 if o.name.startswith('Inspection_scanner_upright') or o.name.startswith('Inspection_scanner_crossbar'):remove_object(o)
for y in [-2.32,-1.72]:
 # Side profile in XZ: widening cast foot, sloping shoulder, thin upper head.
 vs=[(x,yy,z) for yy in [y-.05,y+.05] for x,z in [(5.87,1.065),(6.075,1.065),(6.04,1.53),(6.10,1.69),(5.91,1.69),(5.935,1.45)]]
 fs=[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
 o=mesh('Inspection tapered scanner cheek',vs,fs,'ivory');bevel(o,.003)
 # Winding in this XZ extrusion is checked below from signed volume, then corrected.
 volume=sum(o.data.vertices[p.vertices[0]].co.dot(o.data.vertices[p.vertices[i]].co.cross(o.data.vertices[p.vertices[i+1]].co))/6 for p in o.data.polygons for i in range(1,len(p.vertices)-1))
 if volume<0:
  for f in o.data.polygons:f.flip()
plate('Inspection folded optics bridge',(5.965,-2.02,1.742),.38,.146,.77,'ivory',.042)
box('Inspection dark sensor seam',(5.764,-2.02,1.712),(.006,.59,.025),'dark',.001)
# A visible task light mounted to the scanner bridge illuminates the sample work.
box('Inspection task lamp housing',(5.85,-2.02,1.711),(.10,.43,.033),'dark',.002)
lens=box('Inspection task actual lens',(5.85,-2.02,1.691),(.074,.37,.004),'coldlens',.001)
practical('Inspection sample practical',(5.85,-2.02,1.687),(5.60,-2.08,1.06),22,(.76,.87,1),(.07,.36),lens)

# A height-adjustable operator stool belongs in the fabrication side bay, clear of ports/route.
stool_start=len(new);cx,cy=5.83,-.83
for a in range(5):
 t=a*math.tau/5;x=cx+.28*math.cos(t);y=cy+.28*math.sin(t)
 rod('Operator stool star base',(cx,cy,.11),(x,y,.074),.018,'dark')
 wheel=cyl('Operator stool caster',(x,y,.037),.037,.036,'black',(math.cos(t),math.sin(t),0),16)
 support('Operator stool',(x,y,0),'Floor',(0,0,-1))
lathe('Operator stool hydraulic post',(cx,cy,0),[(.08,.07),(.15,.065),(.48,.046),(.52,.06)],'steel',24)
seat=lathe('Operator worn seat cushion',(cx,cy,0),[(.50,.20),(.525,.233),(.584,.225),(.592,.20)],'leather',32)
ring('Seat stitched perimeter',(cx,cy,.575),.223,.003,'wood')
rod('Stool height lever',(cx+.04,cy,.49),(cx+.25,cy,.49),.009,'steel')
cyl('Stool lever rubber handle',(cx+.26,cy,.49),.016,.10,'black',(1,0,0))

# Large legible floor framing gives negative space a circulation purpose.
for y in [-.96,1.96]:
 for x in [-3.54,-2.50,-1.46,-.42,.62,1.66,2.70,3.74]:
  box('Walkway broken paint border',(x,y,.0022),(.69,.065,.0011),'ivory',0)
text('Main route keep-clear stencil','KEEP CLEAR',(-1.15,-1.52,.0035),.135,'ivory',(0,0,0))
# One broad resurfaced patch and its scored corners are integrated into the slab plane.
patch=mesh('Swept floor repaired screed',[(-4.28,-2.47,.0019),(-3.1,-2.47,.0019),(-2.88,-2.32,.0019),(-2.88,-1.74,.0019),(-4.13,-1.74,.0019),(-4.28,-1.87,.0019)],[(0,1,2,3,4,5)],'concrete')
for a,b in [((-4.22,-2.42,.0026),(-3.1,-2.42,.0026)),((-2.94,-2.29,.0026),(-2.94,-1.80,.0026))]:rod('Screed patch score line',a,b,.0011,'dark',6)

# Worker board: a specific shift roster, pump sketch and personal postcard, no graphic overlap.
for o in list(s.objects):
 if o.name.startswith('RF1 | Paper ink rule'):remove_object(o)
# Board faces south; text's local right matches viewer-facing world -X.
text('Roster title','SHIFT / 07',(1.335,-6.3075,2.225),.039,'ink',(math.pi/2,0,math.pi))
for z,body in [(2.145,'FEED   04:00'),(2.085,'CHECK  06:30'),(2.025,'SEALS  08:00')]:text('Roster shift entry',body,(1.337,-6.3075,z),.022,'ink',(math.pi/2,0,math.pi))
text('Board pump service header','PUMP / PV-05',(.805,-6.3075,2.28),.025,'ink',(math.pi/2,0,math.pi))
# Ink schematic is drawn flat on the paper, an intentional technician's note.
ring('Pump sketch case',(.673,-6.3075,2.10),.066,.0018,'ink',(0,1,0))
for a,b in [((.74,-6.3075,2.10),(.80,-6.3075,2.10)),((.61,-6.3075,2.10),(.565,-6.3075,2.10)),((.673,-6.3075,2.166),(.673,-6.3075,2.218))]:rod('Pump schematic line',a,b,.0013,'ink',6)
text('Pump scribbled note','CHECK SEAL',(.80,-6.3075,1.948),.021,'ink',(math.pi/2,0,math.pi))
# A small hand-drawn landscape below the shift sheet adds a personal, restrained accent.
old=bpy.data.objects.get('RF1 | Crew handwritten postcard')
if old:remove_object(old)
mesh('Crew postcard mountain print',[(.568,-6.3075,1.687),(.660,-6.3075,1.754),(.72,-6.3075,1.687)],[(0,1,2)],'green')
mesh('Crew postcard second peak',[(.658,-6.3074,1.687),(.738,-6.3074,1.738),(.810,-6.3074,1.687)],[(0,1,2)],'blue')
cyl('Postcard small sun',(.779,-6.3070,1.775),.013,.001,'ochre',(0,1,0),16)
text('Crew postcard caption','SEE YOU SUNDAY',(.803,-6.3070,1.663),.013,'ink',(math.pi/2,0,math.pi))
# Used but maintained bench: worn metal strap edges and a cup ring, not global rust.
for x in [.952,.967]:
 box('Nook bench strap rubbed edge',(x,-5.148,.983),(.008,.41,.002),'steel',0)
# Ring is seated to the timber, distinct from the opaque coffee in the mug.
ring('Worktop old mug ring',(.915,-5.425,.981),.078,.0011,'wood')
# Service equipment is now parked against the west wall, clear of entry compositions.
cart_pivot=Vector((-2.20,3.69,0))
cart_move=Matrix.Translation(Vector((-6.88,2.32,0)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-cart_pivot)
rigid_group(cart_members,cart_move)
for r in supports:
 if r['group']=='MaintenanceCart':r['anchor']=list(cart_move@Vector(r['anchor']))
rigid_group([o for o in s.objects if o.name.startswith('RF1 | Service parking paint') or o.name.startswith('RF1 | Service parked stencil')],cart_move)
# Further recess the compact crusher head on its drive-side bracket.
head=bpy.data.objects['CRUSHER_Control_enclosure'];pivot=head.matrix_world.translation.copy()
members=[o for o in s.objects if (o.name.startswith('CRUSHER_') or o.name.startswith('ART_CRUSHER_') or o.name.startswith('RF1 | CRUSHER_')) and any(q in o.name for q in ['_button','_engraving','Control_enclosure'])]
rigid_group(members,Matrix.Translation(Vector((0,.16,.13)))@Matrix.Translation(pivot)@Matrix.Diagonal((.76,.97,.93,1))@Matrix.Translation(-pivot))
rod('Crusher compact console rear bracket',(-4.65,4.13,1.25),(-4.65,3.93,1.28),.033,'dark')

# Avoid a face-like pair of identical dials: temperature belongs on the screw-lift service column.
for prefix,delta in [('Processor_pressure_gauge',(-.10,0,.02)),('Processor_temperature_gauge',(-1.33,.48,0))]:
 rigid_group([o for o in s.objects if o.name.startswith(prefix) or o.name.startswith('ART_'+prefix)],Matrix.Translation(Vector(delta)))
for prefix,delta in [('Vessel gauge welded standoff',(-.10,0,.02)),('Gauge brass union',(-.10,0,.02))]:
 o=bpy.data.objects.get('RF1 | '+prefix)
 if o:o.location+=Vector(delta)
 o=bpy.data.objects.get('RF1 | '+prefix+'.001')
 if o:o.location+=Vector((-1.33,.48,0))
# Retire the two source identity-sign studs left hovering above the hatch after sign replacement.
for o in list(s.objects):
 if o.name.startswith('Processor_ID_plate') or o.name.startswith('ART_Processor_ID_plate'):
  # The department label now lives on the actual upper collar; no redundant face studs.
  remove_object(o)

# Working freight thresholds have a rolled shutter, guides and motor. Clear apertures are untouched.
for side,title in [(-1,'Mine transfer'),(1,'Fuel transfer')]:
 x=side*7.13;y=-4.084
 for yy in [-5.58,-2.539]:
  guide=box(title+' shutter guide',(side*7.405,yy,1.58),(.20,.046,3.16),'dark',.003)
  support(guide.name,(side*7.505,yy,1.58),'West_front_pier' if side<0 and yy<-4 else 'West_main' if side<0 else 'East_front_pier' if yy<-4 else 'East_main',(side,0,0))
  box(title+' guide bright inner lip',(side*7.301,yy,1.58),(.012,.020,3.11),'steel',.001)
 # The roll axis follows the wide doorway; polygonal winding reads at gameplay distance.
 cyl(title+' rolled steel shutter',(x,y,3.64),.215,2.96,'steel',(0,1,0),32)
 for yy in [-5.53,-2.64]:
  plate(title+' roll bearing cheek',(x,yy,3.65),.46,.50,.09,'dark',.045)
 hood=box(title+' folded shutter head',(side*7.3965,y,3.87),(.22,3.08,.10),'green',.003)
 support(hood.name,(side*7.5065,y,3.87),'West_header' if side<0 else 'East_header',(side,0,0))
 # Mounted reduction drive, distinct from machine motors.
 cyl(title+' shutter geared motor',(x,-2.45,3.64),.128,.29,'dark',(0,1,0),24)
 for yy in [-2.57,-2.50,-2.43]:ring(title+' shutter motor fin',(x,yy,3.64),.138,.009,'dark',(0,1,0))
 pipe(title+' motor power conduit',[(side*7.13,-2.45,3.64),(side*7.29,-2.40,3.98),(side*7.39,-1.99,4.13)],.013,'black')
 # An in-room wall bulkhead reveals the threshold floor and the inside of its return.
 yy=-5.67
 mount=box(title+' bulkhead wall base',(side*7.469,yy,1.92),(.073,.20,.30),'dark',.003)
 support(mount.name,(side*7.5055,yy,1.92),'West_front_pier' if side<0 else 'East_front_pier',(side,0,0))
 center=Vector((side*7.423,yy,1.92));target=Vector((side*6.55,-4.75,.75));direction=(target-center).normalized()
 rod(title+' bulkhead cast bracket',(side*7.469,yy,1.92),center-direction*.035,.014,'dark')
 cyl(title+' bulkhead cast rim',center-direction*.025,.111,.058,'dark',direction,24)
 lens=cyl(title+' bulkhead frosted lens',center,.091,.016,'coldlens' if side<0 else 'lens',direction,24)
 ring(title+' bulkhead lens retaining ring',center+direction*.005,.097,.009,'steel',direction)
 practical(title+' wall bulkhead',center+direction*.012,target,48,(.75,.86,1) if side<0 else (1,.83,.59),(.15,.15),lens)

# Give the original ready lamp a visible mounted face rather than two buried edge slivers.
state=bpy.data.objects['Processor_state_light'];state.location.y-=.056;state.data.materials[0]=M['signal']
bezel=box('PV ready indicator mounting bezel',(1.043,4.31,2.3),(.123,.025,.095),'dark',.002)
support(bezel.name,(1.043,4.3225,2.3),'RF1 | PV05 cast pressure vessel',(0,1,0))
# Seat the relocated pressure gauge's stem on the curved vessel skin.
stem=bpy.data.objects.get('RF1 | Vessel gauge welded standoff')
if stem:remove_object(stem)
x=.529;z=2.345;body_y=4.984-math.sqrt(.66*.66-(x-1.043)**2)
rod('Pressure gauge correctly seated nipple',(x,body_y, z),(x,4.28,z),.025,'dark')
support('Pressure gauge', (x,body_y,z),'RF1 | PV05 cast pressure vessel',(1.043-x,4.984-body_y,0))
support('Temperature gauge',(.113,4.774283,2.325),'Processor_screw_head_gearbox',(0,1,0))
