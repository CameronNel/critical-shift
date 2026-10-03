"""R06: distinct optical sorter and transfer hardware; remove obsolete paint."""
for o in list(s.objects):
 if o.name.startswith('Worn_route_edge'):remove_object(o)
# The sorter is a folded optics cabinet over a belt, rather than another green gantry.
for o in list(s.objects):
 if any(o.name.startswith(q) for q in ['Sorter_scanner_upright','Sorter_scanner_bridge','RF1 | Sorter sensor canopy','RF1 | Sorter guarding wing','RF1 | Sorter recessed optics','RF1 | Sorter warm scanner glass','RF1 | Sorter bay id']):remove_object(o)
profile=[(-.65,1.92),(.65,1.92),(.65,2.19),(.40,2.41),(-.44,2.41),(-.65,2.21)]
vs=[(-2.75+x,y,z) for y in [4.315,5.45] for x,z in profile]
fs=[tuple(range(6)),tuple(reversed(range(6,12)))]+[(i,i+6,(i+1)%6+6,(i+1)%6) for i in range(6)]
hood=mesh('Sorter folded optical hood',vs,fs,'ivory');bevel(hood,.004)
volume=sum(hood.data.vertices[p.vertices[0]].co.dot(hood.data.vertices[p.vertices[i]].co.cross(hood.data.vertices[p.vertices[i+1]].co))/6 for p in hood.data.polygons for i in range(1,len(p.vertices)-1))
if volume<0:
 for f in hood.data.polygons:f.flip()
# Cast cheeks link directly to the nominated belt frame with a visible foot.
for x in [-3.24,-2.26]:
 for y in [4.55,5.33]:
  foot=box('Sorter optical foot bracket',(x,y,1.334),(.16,.12,.038),'dark',.002)
  support(foot.name,(x,y,1.315),'Sorter_sideframe.001' if y<5 else 'Sorter_sideframe',(0,0,-1))
  rod('Sorter optical cast upright',(x,y,1.35),(x,y,2.01),.037,'dark')
box('Sorter internal optical cradle',(-2.73,4.934,1.881),(.4,.65,.12),'dark',.003)
box('Sorter sensor front bracket',(-2.73,4.44,1.798),(.075,.085,.245),'dark',.003)
box('Sorter optical front gasket',(-2.75,4.304,2.14),(.72,.022,.162),'dark',.004)
box('Sorter amber scan window',(-2.75,4.288,2.14),(.58,.007,.075),'signal',.002)
for x in [-3.33,-2.17]:
 for z in [2.01,2.17]:cyl('Optical hood captive screw',(x,4.307,z),.020,.013,'steel',(0,-1,0),6)
text('Sorter small bay number','04',(-3.28,4.307,2.29),.080,'green')
# One recessed service split and readable louvered side, not many decorative panels.
for z in [2.08,2.16,2.24]:box('Optical hood side vent',(-2.093,4.90,z),(.004,.32,.017),'dark',.001)
pipe('Sorter sensor power cable',[(-3.25,5.40,2.27),(-3.35,5.80,2.42),(-3.28,6.25,2.88),(-3.28,6.34,3.16)],.017,'black')
clip=box('Sorter cable wall clip',(-3.28,6.396,3.16),(.075,.075,.12),'dark',.002)
support(clip.name,(-3.28,6.4335,3.16),'North_wall',(0,1,0))
# Rejected material exits through a dark worked stainless chute, visibly folded at the edges.
chute_mat=mat('RF1_worked_chute_steel',(.185,.207,.194),.57,.69,.07)
bpy.data.objects['Sorter_reject_slide'].data.materials[0]=chute_mat
for x in [-2.363,-1.75]:
 rod('Sorter chute rolled edge',(x,3.76,.58),(x,4.75,1.31),.018,'steel')
for o in list(s.objects):
 if o.name.startswith('Sorter_rejected_inclusion'):
  c=o.matrix_world.translation.copy();remove_object(o);stone('Rejected mineral fragment',(c.x,c.y,.235),(.10,.085,.09))
# Surface contact at the sorter feed rollers is visible use, not global scratches.
for x,y,z in [(-3.83,4.53,1.315),(-3.78,4.53,1.315),(-.78,4.54,1.315)]:
 box('Sorter rail hand wear',(x,y,z),(.16,.037,.003),'steel',0)
# The dryer has a wound flange / insulated jacket rather than a pristine cylinder end.
for x in [2.92,5.26]:
 ring('Thermal drum end gasket',(x,4.97,1.52),.303,.011,'dark',(1,0,0))
 ring('Thermal drum cast end rim',(x,4.97,1.52),.314,.018,'steel',(1,0,0))
for a in [0,math.pi/2,math.pi,3*math.pi/2]:
 y=4.97+.292*math.cos(a);z=1.52+.292*math.sin(a)
 cyl('Thermal end flange stud',(2.901,y,z),.021,.028,'steel',(1,0,0),6)
# Broad, purposeful insulated top shield follows the drum and steam service, with sharp folded ends.
vs=[];fs=[]
for x in [3.56,4.72]:
 for a in [math.radians(t) for t in [40,65,90,115,140]]:
  vs.append((x,4.97+.717*math.cos(a),1.52+.717*math.sin(a)))
for i in range(4):fs.append((i,i+1,i+6,i+5))
shield=mesh('Thermal removable insulation saddle',vs,fs,'ivory');sol=shield.modifiers.new('Insulation panel thickness','SOLIDIFY');sol.thickness=.022
for x in [3.60,4.68]:
 for side in [-1,1]:
  y=4.97+side*.529;z=2.008
  box('Thermal cover hold-down',(x,y,z),(.095,.067,.11),'steel',.003)
# A rail-mounted replaceable cartridge communicates a specific dryer maintenance task.
tray=box('Dryer filter service tray',(3.37,3.974,.9225),(.72,.33,.025),'steel',.002)
support(tray.name,(3.37,3.974,.91),'Dryer_filter_service_ledge_top',(0,0,-1))
for x in [3.025,3.715]:box('Filter tray folded lip',(x,3.974,.97),(.025,.33,.07),'dark',.002)
rigid_group([o for o in s.objects if any(o.name.startswith(prefix) for prefix in ['Dryer_Spare_','Dryer_Removed_dirty_','ART_Dryer_Spare_','ART_Dryer_Removed_dirty_'])],Matrix.Translation(Vector((0,0,.025))))
for name in ['Dryer_Spare_filter_frame','Dryer_Removed_dirty_filter_frame']:
 bpy.data.objects[name]['cs_support_target']=tray.name
text('Filter tray service mark','FILTER / 06',(3.18,3.804,.954),.036,'ivory')
# Replace the scanner's old broad slab foot with seated cheek pads and a sample locator.
old=bpy.data.objects.get('Inspection_scanner_foot')
if old:remove_object(old)
for y in [-2.32,-1.72]:
 pad=box('Inspection scanner bolted foot pad',(5.978,y,1.05375),(.27,.16,.0225),'dark',.002)
 support(pad.name,(5.978,y,1.0425),'Inspection_work_surface',(0,0,-1))
 for o in [o for o in s.objects if o.name.startswith('RF1 | Inspection tapered scanner cheek')]:
  lo,hi=bounds_world(o)
  if abs((lo.y+hi.y)/2-y)<.01:support(o.name,(5.978,y,1.065),pad.name,(0,0,-1))
 for x in [5.89,6.06]:cyl('Inspection foot captive bolt',(x,y,1.079),.015,.026,'steel',(0,0,1),6)
base=box('Inspection sample locating plinth',(5.727,-2.02,1.09),(.43,.42,.095),'dark',.003)
support(base.name,(5.727,-2.02,1.0425),'Inspection_work_surface',(0,0,-1))

# Smaller industrial dials retain their original interactive component names and pivots.
for prefix in ['Processor_pressure_gauge','Processor_temperature_gauge']:
 case=bpy.data.objects[prefix+'_case'];pivot=case.matrix_world.translation.copy()
 rigid_group([o for o in s.objects if o.name.startswith(prefix) or o.name.startswith('ART_'+prefix)],Matrix.Translation(pivot)@Matrix.Diagonal((.78,.78,.78,1))@Matrix.Translation(-pivot))

# Put under-crown lamps below the solid casting, with real contact at their mounts.
for name in ['Press fixture casing','Press actual lens']:
 bpy.data.objects['RF1 | '+name].location.z-=.1175
bpy.data.objects['RF1 LIGHT | Press task bar'].location.z-=.1175
support('Press task fixture',(5.81,1.15,2.335),'RF1 | Press stepped crown',(0,0,1))
for name in ['Inspection task lamp housing','Inspection task actual lens']:
 bpy.data.objects['RF1 | '+name].location.z-=.0585
bpy.data.objects['RF1 LIGHT | Inspection sample practical'].location.z-=.0585

# Physical reflector heads now aim where their area sources emit.
bpy.context.view_layer.update()
for i in [0,1]:
 suffix='' if i==0 else '.001'
 lens=bpy.data.objects['RF1 | PV task actual lens'+suffix];hood=bpy.data.objects['RF1 | PV task folded hood'+suffix]
 lamp=bpy.data.objects['RF1 LIGHT | PV hood '+str(i)];center=lens.matrix_world.translation.copy();direction=(lamp.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 turn=Vector((0,0,-1)).rotation_difference(direction).to_matrix().to_4x4()
 transform=Matrix.Translation(center)@turn@Matrix.Translation(-center)
 rear=transform@Vector((center.x,center.y,3.635))
 rigid_group([lens,hood],transform);lamp.location=center+direction*.005
 rod('PV aimed reflector hinge',(center.x,5.96,3.65),rear,.020,'dark')
# The inspection strip pivots under its actual bridge; a hinge links it to the cast underside.
lens=bpy.data.objects['RF1 | Inspection task actual lens'];hood=bpy.data.objects['RF1 | Inspection task lamp housing'];lamp=bpy.data.objects['RF1 LIGHT | Inspection sample practical']
center=lens.matrix_world.translation.copy();direction=(lamp.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
turn=Vector((0,0,-1)).rotation_difference(direction).to_matrix().to_4x4();transform=Matrix.Translation(center)@turn@Matrix.Translation(-center)
rigid_group([lens,hood],transform);lamp.location=center+direction*.004
rod('Inspection strip cast mounting hinge',(5.925,-2.02,1.669),center-direction*.035,.011,'dark')
support('Inspection task strip',(5.925,-2.02,1.669),'RF1 | Inspection folded optics bridge',(0,0,1))
# Existing flush wall lenses face down: align the proxy surface instead of aiming it through a housing.
for i in range(4):bpy.data.objects['RF1 LIGHT | Wall service lamp '+str(i)].rotation_euler=(0,0,0)

# Girder end bearings physically seat the ceiling structure on the protected walls.
for y in [-5.15,-.64,3.86]:
 for side in [-1,1]:
  pad=box('Ceiling girder wall bearing',(side*7.44,y,4.59),(.13,.46,.18),'dark',.003)
  support(pad.name,(side*7.505,y,4.59),('West_header' if side<0 else 'East_header') if y<-3 else ('West_main' if side<0 else 'East_main'),(side,0,0))

# Nook wear belongs on the metal edge, rather than random strips across the timber.
for o in list(s.objects):
 if o.name.startswith('RF1 | Nook bench strap rubbed edge'):remove_object(o)
for x,w in [(.72,.085),(.94,.055)]:box('Nook front strap hand rub',(x,-5.064,.9875),(w,.008,.0014),'steel',0)
text('Worker reminder note','ASK MARA\nFILTER STOCK',(1.40,-6.3075,1.825),.021,'ink',(math.pi/2,0,math.pi))
