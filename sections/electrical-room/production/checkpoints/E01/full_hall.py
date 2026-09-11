"""Original complete electrical hall assemblies; called by factory-empty builder."""
import math,json
import bpy
from mathutils import Vector

def build(B):
 box,cyl,beam,tube,ring=B.box,B.cyl,B.beam,B.tube,B.ring
 def root(name,loc,rot=0,target='Floor',anchors=None):
  return B.assembly(name,loc,rot,target,anchors or [[0,0,0]])
 def panel(r,label,loc,w,h,size=.07,mat='darkpaint'):
  B.plaque(r,label,loc,w,h,mat,size)
 def duct(r,name,a,b,w=.32,h=.24,mat='bus'):
  av,bv=Vector(a),Vector(b);d=bv-av
  o=box(name,(av+bv)/2,(w,h,d.length),mat,r,.006);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
 # Remaining switchgear, with a single isolated service bay.
 for y,kind,label in [(6.3,'feeder','03  COOLING'),(7.5,'feeder','04  PRODUCTION'),(8.7,'feeder','05  FACILITY'),(9.9,'repair','06  SERVICE')]:
  B.switchgear('SG'+label[:2]+'_'+label[4:].strip(),y,kind,label)
 B.mat_strip(8.55,4.1)
 B.current='Architecture'
 box('Reserve floor',(6.9,13.2,-.12),(2.8,4.4,.24),'floor',bevel=0)
 box('Reserve ceiling',(6.9,13.2,3.7),(2.8,4.4,.2),'wall',bevel=0)
 box('Reserve east wall',(8.425,13.2,1.8),(.25,4.9,3.6),'wall',bevel=.008)
 box('Reserve south wall',(6.9,10.875,1.8),(2.8,.25,3.6),'wall',bevel=.008)
 box('Reserve north wall',(6.9,15.525,1.8),(2.8,.25,3.6),'wall',bevel=.008)
 # These level seam slabs fill wall-thickness thresholds, with no scenic closure.
 box('Entry seam slab',(0,-.125,-.12),(2.9,.25,.24),'floor',bevel=0)
 box('Waste seam slab',(0,16.65,-.12),(3,.5,.24),'floor',bevel=0)
 # Floor mounted, connected transformer and safety cage.
 B.current='Transformer'
 tx=root('TX01_Guarded_dry_transformer',(4.175,6.4,0),-math.pi/2,anchors=[[-1.35,-.8,0],[1.35,-.8,0],[-1.35,.8,0],[1.35,.8,0]])
 box('Transformer concrete plinth',(0,0,.12),(3.35,2.2,.24),'patch',tx,.012)
 for x in [-1.18,1.18]:
  box('Transformer anchored base channel',(x,0,.32),(.17,1.6,.16),'darkpaint',tx,.006)
  for y in [-.64,.64]:cyl('TX foundation bolt',(x,y,.42),.025,.045,'metal',tx,vertices=8)
 for z in [.5,2.35]:
  box('Laminated core yoke',(0,.14,z),(2.85,.52,.30),'darkpaint',tx,.004)
  for i in range(11):box('Core lamination seam',(0,-.126,z-.12+i*.023),(2.74,.007,.004),'metal',tx,0)
 for x in [-.91,0,.91]:
  box('Core vertical leg',(x,.14,1.41),(.34,.40,1.6),'darkpaint',tx,.003)
  for z in [.72,2.02]:box('Coil insulating saddle',(x,.12,z),(.73,.76,.13),'ceramic',tx,.009)
  cyl('Cast resin coil body',(x,.12,1.39),.355,1.26,'orange',tx,vertices=48)
  for z in [.80,.98,1.20,1.42,1.64,1.86,1.98]:ring('Cast coil cooling band',(x,.12,z),.348,.017,'paint',tx)
  for yy in [-.35,.5]:
   cyl('Terminal porcelain standoff',(x,yy,2.20),.062,.3,'ceramic',tx)
   for z in [2.12,2.18,2.24]:cyl('Terminal insulation skirt',(x,yy,z),.09,.025,'ceramic',tx)
   box('Copper terminal lug',(x,yy,2.39),(.17,.23,.055),'copper',tx,.007)
   cyl('Terminal clamp bolt',(x,yy,2.435),.023,.035,'metal',tx,vertices=8)
  tube('TX primary insulated lead',[(x,.5,2.41),(x,.58,2.66),(x,.35,2.9),(x,.1,3.13)],.035,'rubber',tx)
  tube('TX secondary enclosed lead',[(x,-.35,2.41),(x,-.45,2.60),(x,-.30,2.82),(x,-.1,3.13)],.028,'rubber',tx)
 box('Transformer terminal enclosure',(0,0,3.02),(2.75,.7,.26),'darkpaint',tx,.012)
 for x in [-1.57,1.57]:
  for y in [-.99,.99]:
   box('Guard post foot',(x,y,.285),(.18,.18,.09),'metal',tx,.004)
   box('Guard square tube post',(x,y,1.6),(.055,.055,2.55),'darkpaint',tx,.004)
 for y in [-.99,.99]:
  for z in [.36,2.89]:box('Guard front rear frame',(0,y,z),(3.2,.045,.055),'darkpaint',tx,.003)
  for x in [i*.12-1.5 for i in range(26)]:beam('Guard vertical wire',(x,y,.39),(x,y,2.87),.009,'metal',tx)
  for z in [i*.12+.45 for i in range(21)]:beam('Guard horizontal wire',(-1.54,y,z),(1.54,y,z),.009,'metal',tx)
 for x in [-1.57,1.57]:
  for z in [.36,2.89]:box('Guard side rail',(x,0,z),(.05,2.0,.055),'darkpaint',tx,.003)
  for y in [i*.14-.91 for i in range(14)]:beam('Guard side vertical wire',(x,y,.39),(x,y,2.87),.009,'metal',tx)
  for z in [i*.14+.45 for i in range(18)]:beam('Guard side horizontal wire',(x,-.97,z),(x,.97,z),.009,'metal',tx)
 # Centre service leaf is closed and within equipment footprint; hinge pivot retained.
 gate=B.assembly('TX_GUARD_SERVICE_PIVOT',(-1.54,-1.018,.36),parent=tx)
 gate['assembly_root']=False
 for z in [0,2.50]:box('Gate leaf horizontal',(1.54,0,z),(3.08,.035,.04),'yellow',gate,.003)
 for x in [0,3.08]:box('Gate leaf stile',(x,0,1.25),(.045,.035,2.5),'yellow',gate,.003)
 for z in [.25,2.23]:cyl('Guard gate hinge',(0,0,z),.035,.14,'metal',gate)
 B.handle(gate,2.85,-.06,1.05,height=.2)
 panel(tx,'TX / 01',(0,-1.035,1.56),.75,.26,.11)
 panel(tx,'ISOLATE BEFORE ACCESS',(0,-1.04,1.25),1.55,.15,.071)
 box('Transformer grounding lug',(1.2,.88,.42),(.14,.15,.08),'copper',tx,.004)
 box('Transformer earth anchor',(1.45,.91,.30),(.12,.12,.12),'metal',tx,.004)
 tube('Transformer earth bond',[(1.2,.88,.42),(1.35,.91,.45),(1.45,.91,.30)],.018,'copper',tx)
 # Manual transfer station, face toward main hall (-world X).
 B.current='Essential'
 td=root('TD01_Manual_transfer',(4.825,10.3,0),-math.pi/2,anchors=[[-.70,-.35,0],[.70,-.35,0]])
 box('Transfer base',(0,0,.09),(1.65,.92,.18),'darkpaint',td,.008)
 box('Transfer rear shell',(0,.40,1.26),(1.62,.07,2.15),'darkpaint',td,.006)
 for x in [-.79,.79]:box('Transfer side return',(x,0,1.26),(.06,.86,2.15),'pale',td,.006)
 box('Transfer crown',(0,0,2.365),(1.68,.94,.09),'pale',td,.006)
 box('Transfer fascia',(0,-.40,1.39),(1.48,.065,1.72),'pale',td,.006)
 panel(td,'MANUAL TRANSFER',(0,-.441,2.12),1.33,.15,.09)
 for x,label in [(-.40,'NORMAL'),(.40,'RESERVE')]:
  panel(td,label,(x,-.444,1.91),.58,.12,.07)
  box('Source mechanism inset',(x,-.45,1.64),(.43,.04,.34),'darkpaint',td,.004)
  cyl('Source lever hub',(x,-.50,1.63),.073,.06,'metal',td,'Y')
  beam('Source cast arm',(x,-.54,1.63),(x,-.57,1.76),.032,'metal',td)
  cyl('Source insulated grip',(x,-.58,1.77),.028,.13,'red' if x<0 else 'black',td)
 box('Interlock slide',(0,-.492,1.41),(1.13,.052,.065),'metal',td,.003)
 for x in [-.28,.28]:box('Interlock stop block',(x,-.528,1.44),(.075,.03,.13),'darkpaint',td,.003)
 panel(td,'ESSENTIAL PRIORITY',(0,-.444,1.20),1.30,.12,.075)
 B.rotary(td,0,-.475,.98,'black')
 for x,t in [(-.48,'COOLING'),(0,'HOLD'),(.49,'MEDICAL')]:panel(td,t,(x,-.446,.79),.45,.085,.045)
 box('Transfer lower service panel',(0,-.41,.40),(1.46,.06,.32),'darkpaint',td,.004)
 B.handle(td,.57,-.47,.4,height=.18)
 for z in [.43,1.06,1.76]:box('Transfer lift-off hinge',(-.76,-.443,z),(.07,.06,.14),'metal',td,.004)
 cyl('Manual crank socket',(-.51,-.48,.41),.043,.038,'metal',td,'Y')
 panel(td,'CRANK',(-.47,-.451,.23),.42,.07,.04)
 tube('Stowed transfer crank',[(.54,.41,.5),(.54,.41,.78),(.63,.41,.78),(.63,.41,.94)],.015,'metal',td)
 for z in [.57,.84]:box('Crank retaining clip',(.55,.4,z),(.09,.07,.04),'black',td,.003)
 # Three accessible reserve modules; a single shared gameplay pool.
 for i,yy in enumerate([12.18,13.2,14.22],1):
  rb=root('RB0'+str(i)+'_Reserve_module',(7.73,yy,0),-math.pi/2,target='Reserve floor',anchors=[[-.40,-.30,0],[.40,-.30,0]])
  box('Reserve anchored base',(0,0,.10),(.98,.73,.2),'darkpaint',rb,.007)
  for x in [-.45,.45]:box('Reserve folded vertical',(x,0,1.25),(.075,.69,2.1),'darkpaint',rb,.005)
  box('Reserve rear shell',(0,.31,1.25),(.89,.06,2.1),'darkpaint',rb,.005)
  for z in [.33,.88,1.43]:
   box('Battery module tray',(0,0,z),(.83,.61,.045),'metal',rb,.003)
   box('Sealed reserve cell module',(0,-.005,z+.225),(.79,.54,.41),'black',rb,.02)
   box('Battery service band',(0,-.28,z+.24),(.69,.02,.10),'orange',rb,.004)
   for x in [-.27,.27]:B.handle(rb,x,-.302,z+.24,height=.095)
   for x in [-.29,.29]:cyl('Recessed battery terminal',(x,.19,z+.455),.032,.045,'copper',rb)
  box('Reserve upper panel',(0,-.32,2.09),(.83,.055,.44),'pale',rb,.005)
  panel(rb,'RESERVE / 0'+str(i),(0,-.358,2.23),.75,.105,.055)
  B.gauge(rb,-.19,-.361,2.05,.083,'SOC',.5)
  B.rotary(rb,.19,-.37,2.05,'red')
  box('Reserve top cap',(0,0,2.34),(.98,.75,.07),'pale',rb,.005)
  for z in [.6,1.15]:tube('Covered series interconnect',[(.29,.19,z+.185),(.33,.23,z+.28),(.33,.23,z+.65),(-.29,.19,z+.73)],.015,'rubber',rb)
 # Wall mounted portable power inlet in bay, outside straight approach.
 r=root('Portable_blackstart_connection',(6.4,15.345,0),0,target='Reserve north wall',anchors=[[0,.055,1.34]])
 r['support_direction']=json.dumps([0,1,0])
 box('Portable inlet backplate',(0,0,1.34),(.62,.11,.57),'darkpaint',r,.006)
 cyl('Portable inlet collar',(0,-.10,1.29),.12,.14,'metal',r,'Y')
 cyl('Portable socket insulator',(0,-.175,1.29),.094,.02,'black',r,'Y')
 for x,z in [(-.035,1.31),(.035,1.31),(0,1.25)]:cyl('Recessed connector pin',(x,-.188,z),.009,.016,'copper',r,'Y')
 panel(r,'PORTABLE INPUT',(0,-.062,1.54),.56,.095,.046)
 # Equipped repair bench.
 B.current='Workshop'
 wb=root('WB01_Repair_bench',(-4.42,13.88,0),math.pi/2,anchors=[[-1.08,-.61,0],[1.08,-.61,0],[-1.08,.61,0],[1.08,.61,0]])
 for x in [-1.08,1.08]:
  for y in [-.61,.61]:
   box('Bench foot pad',(x,y,.025),(.16,.16,.05),'rubber',wb,.006)
   beam('Bench tubular leg',(x,y,.05),(x,y,.94),.055,'darkpaint',wb)
 for y in [-.61,.61]:box('Bench longitudinal apron',(0,y,.84),(2.3,.06,.13),'darkpaint',wb,.004)
 for x in [-1.08,1.08]:box('Bench cross brace',(x,0,.31),(.055,1.28,.055),'darkpaint',wb,.003)
 box('Bench lower shelf',(0,0,.31),(2.23,1.25,.035),'darkpaint',wb,.004)
 box('Phenolic worktop',(0,0,.975),(2.5,1.55,.09),'undercoat',wb,.012)
 box('Insulating work surface',(0,-.14,1.025),(1.63,.99,.01),'rubber',wb,.003)
 box('Bench tool drawer',(0,0,.68),(1.00,1.05,.23),'orange',wb,.005);B.handle(wb,0,-.57,.68,height=.14)
 # Original loose three-pole fuse cartridge on a supporting cradle.
 box('Fuse service cradle',(0,-.04,1.08),(.73,.44,.1),'darkpaint',wb,.005)
 for x in [-.23,0,.23]:
  cyl('Bench spare ceramic fuse',(x,-.04,1.19),.095,.36,'ceramic',wb,'Y')
  for yy in [-.24,.16]:cyl('Bench fuse end cap',(x,yy,1.19),.10,.045,'metal',wb,'Y')
 box('Open service toolcase',(.86,.05,1.095),(.48,.60,.14),'orange',wb,.015)
 box('Toolcase foam insert',(.86,.05,1.17),(.40,.51,.018),'rubber',wb,.005)
 for yy in [-.1,.04,.18]:
  cyl('Insulated screwdriver handle',(.94,yy,1.20),.026,.16,'red',wb,'X')
  cyl('Screwdriver steel shaft',(.77,yy,1.20),.007,.19,'metal',wb,'X')
 box('Repair clipboard',(-.84,.04,1.039),(.43,.59,.024),'darkpaint',wb,.005)
 box('Repair work sheet',(-.84,.04,1.052),(.38,.52,.002),'paper',wb,0)
 B.text('Bench repair record','ISOLATION CHECK\n\n01  OPEN\n02  TEST\n03  REPAIR',(-1.0,.20,1.054),.035,'ink',wb,rot=(0,0,0))
 # Backboard is braced from the bench frame, not floating on the wall.
 for x in [-1.07,1.07]:box('Bench backboard upright',(x,.63,1.49),(.045,.045,1.15),'darkpaint',wb,.003)
 box('Bench supported toolboard',(0,.63,1.72),(2.3,.055,.58),'pale',wb,.005)
 panel(wb,'REPAIR / 01',(0,.595,1.87),1.3,.16,.10)
 for x in [-.75,-.42,.42,.75]:
  cyl('Toolboard peg',(x,.54,1.64),.012,.15,'metal',wb,'Y')
  ring('Spanner ring end',(x,.48,1.59),.049,.014,'metal',wb,'Y')
  beam('Spanner handle',(x,.48,1.54),(x,.48,1.35),.032,'metal',wb)
 # Complete supported overhead utility topology.
 B.current='Utilities';bus=bpy.data.objects['Enclosed main busway']
 duct(bus,'Transformer branch duct',(0,6.4,0),(8.495,6.4,0),.42,.34)
 duct(bus,'Transformer terminal drop',(8.495,6.4,0),(8.495,6.4,-.74),.54,.42)
 for x in [2,4.5,7]:
  box('TX branch hanger saddle',(x,6.4,-.22),(.13,.69,.06),'darkpaint',bus,.003)
  for y in [6.1,6.7]:cyl('TX branch hanger rod',(x,y,.35),.014,1.14,'metal',bus)
 for y in [6.4,10.3]:box('Branch bolted tee',(8.495,y,0),(.62,.65,.48),'darkpaint',bus,.009)
 duct(bus,'TX secondary enclosed run',(8.495,6.4,0),(8.495,10.3,0),.34,.26)
 duct(bus,'Transfer top link',(8.495,10.3,0),(9.145,10.3,0),.32,.26)
 duct(bus,'Transfer entry drop',(9.145,10.3,0),(9.145,10.3,-1.49),.38,.30)
 duct(bus,'Reserve charging duct',(9.145,10.3,0),(9.145,13.2,0),.26,.22)
 duct(bus,'Reserve ceiling transition',(9.145,13.2,0),(9.145,13.2,-.85),.26,.22)
 duct(bus,'Reserve bay overhead trunk',(9.145,13.2,-.85),(12.05,13.2,-.85),.26,.22)
 duct(bus,'Reserve bank header',(12.05,12.18,-.85),(12.05,14.22,-.85),.24,.20)
 for y in [12.18,13.2,14.22]:duct(bus,'Reserve cabinet charging riser',(12.05,y,-.85),(12.05,y,-1.50),.19,.19)
 duct(bus,'Essential external inlet',(12.05,14,-1.08),(12.62,14,-1.08),.20,.20)
 duct(bus,'Essential inlet inner link',(12.05,14,-.85),(12.05,14,-1.08),.20,.20)
 duct(bus,'Essential wall sleeve',(12.62,14,-1.08),(12.87,14,-1.08),.20,.20)
 # Flared inlet mates the already saved Turbine 0.40 x 0.30 m bus face.
 verts=[]
 for y,w,h in [(-.25,.4,.3),(0,.72,.48)]:
  verts.extend([(x,y,z) for x,z in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]])
 me=bpy.data.meshes.new('Incoming adapter formed enclosure');me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]);me.update()
 ob=bpy.data.objects.new('Turbine mating adapter',me);B.COL['Utilities'].objects.link(ob);ob.parent=bus;me.materials.append(B.M['bus']);ob['assembly_member']=bus.name
 # Real wall penetrations: hidden exact Boolean operands, retained for editing.
 for name,loc,dims,targets in [
  ('U01 wall aperture',(-4.32,0,3.88),(.80,.8,.60),[o for o in bpy.data.objects if o.name.startswith('Portal wall return') and o.location.x<0 and o.location.y<1]),
  ('U02 wall aperture',(-4.32,16.4,3.88),(.80,.8,.60),[o for o in bpy.data.objects if o.name.startswith('Portal wall return') and o.location.x<0 and o.location.y>15]),
  ('U03 wall aperture',(8.425,14,2.8),(.7,.30,.30),[bpy.data.objects['Reserve east wall']])]:
  cutter=box(name,loc,dims,None,bevel=0);cutter.hide_render=True;cutter.hide_set(True);cutter['intent']='Boolean wall service opening operand'
  for target in targets:
   mod=target.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 # Mechanical junctions, not unsupported decorative tubes.
 for x,y,z in [(8.495,6.4,0),(8.495,10.3,0),(9.145,10.3,0),(9.145,13.2,-.85),(12.05,13.2,-.85)]:
  box('Utility bolted corner cover',(x,y,z),(.44,.43,.32),'metal',bus,.006)
 # Named scene interfaces and engine-owned behavior contracts.
 B.current='Validation';contract=json.loads((B.ROOT/'interface.json').read_text(encoding='utf-8'))
 for item in contract['portals']+contract['utilities']:
  e=bpy.data.objects.new(item['marker'],None);B.COL['Validation'].objects.link(e);e.location=item['centre'];e['connection_id']=item['id'];e['outward_normal']=json.dumps(item['outward_normal'])
 hooks={'INTERACT_TURBINE_ISOLATOR':(-3.52,3.9,1.4),'INTERACT_LOAD_SHED':(-3.52,7.5,1.4),'INTERACT_MANUAL_TRANSFER':(4.245,10.3,1.65),'INTERACT_PRIORITY_SELECTOR':(4.35,10.3,.98),'INTERACT_RESERVE_SERVICE':(7.35,13.2,2.05),'INTERACT_COMPONENT_REPAIR':(-3.6,13.88,1.05),'HOOK_SHARED_RESERVE':(7.73,13.2,1),'INTERACT_PORTABLE_INPUT':(6.4,15.12,1.29)}
 for name,co in hooks.items():
  e=bpy.data.objects.new(name,None);B.COL['Validation'].objects.link(e);e.location=co;e['authority']='engine_host';e['implemented']='visual_anchor_only'
 for name,co in [('AUDIO_ELECTRICAL_HALL',(0,8,2)),('INCIDENT_BLACKOUT',(0,8,1)),('INCIDENT_LIVE_REPAIR',(-3.4,9.9,1.1)),('PLAYER_ENTRY_EYE',(0,1.2,1.68)),('NAV_MAIN_ROUTE',(0,8,0))]:
  e=bpy.data.objects.new(name,None);B.COL['Validation'].objects.link(e);e.location=co;e['runtime_pending']=True
 # A full set established before formal room polish.
 for name,loc,target,lens in [
 ('C01_Entry',(0,1.2,1.68),(-.3,9,1.85),23),
 ('C02_Hero',(-.35,6.5,1.68),(-4.15,6.7,1.7),25),
 ('C03_Reverse',(0,15.1,1.68),(-.2,5,1.7),23),
 ('C04_Route',(0,5,1.68),(0,16.4,1.65),23),
 ('C05_Drawout_Clearance',(-1.35,11.7,1.68),(-3.8,9.9,1.2),28),
 ('C06_Transformer',(1.4,8.9,1.68),(4.15,6.4,1.65),26),
 ('C07_Reserve_Bay',(4.2,13.2,1.68),(7.8,13.2,1.3),24),
 ('C08_Material_Detail',(-2.8,12.7,1.68),(-4.3,13.8,1.22),36),
 ('C09_Workbench',(-.7,14.7,1.68),(-4.35,13.7,1.4),28),
 ('C10_Transfer',(2.5,10.2,1.68),(4.8,10.3,1.35),26),
 ('W01_Turbine_Return',(0,3.9,1.68),(0,0,1.6),24),
 ('W02_Waste_Approach',(0,12.8,1.68),(0,16.4,1.6),24),
 ('W03_Reserve_Return',(6.75,13.2,1.68),(2,13.2,1.6),24),
 ('W04_Switchgear_Approach',(-2,2.7,1.68),(-3.8,5.4,1.6),26)]:B.camera(name,loc,target,lens)
 B.light_fixture('Rear hall practical',(0,14.2,4.6),550,True)
 B.light_fixture('Transformer task practical',(2.3,6.4,4.6),650)
 B.light_fixture('West rear practical',(-2.5,10,4.6),600,True)
 B.light_fixture('Transfer task practical',(3,10.1,4.6),450)
 baylight=B.light_fixture('Reserve bay practical',(6.7,13.2,3.4),220,True)
 baylight['support_target']='Reserve ceiling'
