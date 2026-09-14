"""Additive exterior packages. Original room libraries remain read-only."""
import bpy, math, json, hashlib, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SID=os.environ.get('EXTERIOR_SECTION','compliance-dock')
REV=os.environ.get('EXTERIOR_REVISION','R08')
OUT=ROOT/'exteriors'/SID;OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'sources'/SID/'module.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
ext=bpy.data.collections.new('EXTERIOR_'+SID);scene.collection.children.link(ext)
def mat(name,color,rough,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=2
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(c*.84 for c in color),1);ramp.color_ramp.elements[1].color=(*(min(1,c*1.06) for c in color),1)
 m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 if metal==0:
  geo=n.new('ShaderNodeNewGeometry');fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=32;fine.inputs['Detail'].default_value=2
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.025
  m.node_tree.links.new(geo.outputs['Position'],fine.inputs['Vector']);m.node_tree.links.new(fine.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
cream=mat('EXT mineral painted concrete',(.55,.51,.42),.82)
base=mat('EXT exposed plinth',(.19,.20,.19),.9)
steel=mat('EXT charcoal coated steel',(.065,.077,.078),.48,.55)
accent=mat('EXT terracotta department',(.37,.14,.065),.64,.15)
ivory=mat('EXT sign enamel',(.78,.73,.59),.45,.15)
rubber=mat('EXT EPDM seam',(.025,.027,.028),.9)
def box(name,c,s,m,bevel=.012):
 x,y,z=s;verts=[(a*x/2,b*y/2,d*z/2) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[tuple(reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]);mesh.update()
 ob=bpy.data.objects.new(name,mesh);ext.objects.link(ob);ob.location=c;mesh.materials.append(m)
 if bevel:mod=ob.modifiers.new('Construction edge','BEVEL');mod.width=bevel;mod.segments=2
 return ob
def rod(name,a,b,r,m):
 a,b=Vector(a),Vector(b);v=b-a;verts=[];faces=[];N=12
 for z in [-v.length/2,v.length/2]:
  for i in range(N):verts.append((r*math.cos(i*2*math.pi/N),r*math.sin(i*2*math.pi/N),z))
 faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);ext.objects.link(ob);ob.location=(a+b)/2;ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();mesh.materials.append(m);return ob
def text(name,body,loc,size):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0008
 ob=bpy.data.objects.new(name,cu);ext.objects.link(ob);ob.location=loc;ob.rotation_euler=(math.pi/2,0,math.pi);cu.materials.append(ivory)
def front_panel(a,b,y,h):
 width=b-a;count=max(1,round(width/1.45))
 for i in range(count):
  lo=a+i*width/count;hi=a+(i+1)*width/count
  box('Precast facade panel',((lo+hi)/2,y,h/2),(hi-lo-.018,.065,h),cream)
  box('Concrete kick plinth',((lo+hi)/2,y+.025,.34),(hi-lo-.018,.09,.68),base)
  box('Department paint strip',((lo+hi)/2,y+.036,1.28),(hi-lo-.022,.015,.24),accent,.002)
def build_compliance():
 for a,b in [(-6.8,-2.3),(2.3,6.8)]:front_panel(a,b,16.112,4.4)
 box('Gate lintel concrete skin',(0,16.112,3.95),(4.6,.065,.9),cream)
 box('Continuous top coping',(0,16.10,4.46),(14.18,.42,.16),steel)
 for x in [-7.10,7.10]:
  for i in range(11):
   y=.1+(i+.5)*15.6/11
   box('Side mineral panel',(x,y,2.2),(.065,15.6/11-.018,4.4),cream)
   box('Side concrete plinth',(x,y,.34),(.09,15.6/11-.018,.68),base)
  box('Side coping',(x,7.9,4.46),(.35,16.0,.16),steel)
 # Entire existing 4.6 x 3.5 m gate aperture is left untouched.
 box('Folded canopy roof',(0,16.34,4.32),(5.65,.48,.09),steel)
 box('Canopy front folded fascia',(0,16.555,4.23),(5.65,.045,.20),steel)
 for x in [-2.66,2.66]:
  box('Canopy wall bearing plate',(x,16.19,3.89),(.14,.09,.74),steel)
  rod('Triangular canopy strut',(x,16.23,3.57),(x,16.55,4.25),.035,steel)
  for z in [3.63,4.14]:rod('Canopy anchor bolt',(x,16.23,z),(x,16.255,z),.032,ivory)
 box('Compliance sign backing',(0,16.185,3.89),(2.85,.085,.43),steel)
 text('Compliance external sign','COMPLIANCE',(0,16.229,3.80),.22)
 for x in [-1.98,1.98]:
  box('Shielded dock task light',(x,16.39,4.19),(.42,.24,.09),steel)
  box('Dock light canopy mounting shoe',(x,16.39,4.255),(.26,.16,.045),steel,.003)
  em=bpy.data.materials.get('EXT warm lens')
  if not em:
   em=mat('EXT warm lens',(.8,.64,.38),.3);p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.76,.42,1);p.inputs['Emission Strength'].default_value=3
  box('Recessed luminaire lens',(x,16.39,4.137),(.34,.18,.016),em,.002)
  ld=bpy.data.lights.new('Dock downlight','AREA');ld.energy=30;ld.color=(1,.78,.52);ld.shape='RECTANGLE';ld.size=.32;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(x,16.39,4.11)
 box('Intercom mounting block',(2.66,16.19,1.46),(.24,.12,.48),steel)
 for z in [1.38,1.41,1.44]:box('Intercom speaker slot',(2.66,16.256,z),(.15,.006,.009),rubber,.001)
 rod('Intercom push button',(2.66,16.253,1.29),(2.66,16.27,1.29),.03,accent)
 rod('Rainwater downpipe',(-6.5,16.26,.16),(-6.5,16.26,4.43),.064,steel)
 for z in [.4,2,3.9]:
  box('Downpipe wall shoe',(-6.5,16.19,z),(.20,.16,.06),steel)
 rod('Downpipe discharge elbow',(-6.5,16.26,.16),(-6.5,16.45,.10),.064,steel)
 # Roof cap rests above original ceiling, no interior ceiling replacement.
 box('Roof waterproof cap',(0,7.9,4.46),(13.6,15.8,.035),base,.002)
 # Rear elevation retains the existing staff passage and its full 2.4 m width.
 old=set(ext.objects)
 for a,b in [(-6.8,-1.3),(1.3,6.8)]:front_panel(a,b,.312,4.4)
 for o in set(ext.objects)-old:o.location.y=-o.location.y
 box('Rear coping',(0,-.28,4.46),(14.18,.42,.16),steel)
 # Folded coping return lips and corner flashings create specific construction.
 for x in [-7.16,7.16]:
  for y in [.06,15.84]:box('Corner sheet flashing',(x,y,2.2),(.065,.22,4.4),steel,.003)
 for y in [0,15.8]:box('Roof end flashing',(0,y,4.49),(13.6,.12,.04),steel,.003)
 for i in range(8):box('Roof membrane lap',(0,1+i*1.85,4.481),(13.4,.025,.006),rubber,.001)
 # Weatherproof service box bolted to the side wall, with attached conduit.
 box('Exterior services cabinet',(-7.22,12.5,1.6),(.21,.85,1.1),steel)
 box('Service cabinet inset door',(-7.34,12.5,1.6),(.035,.75,.99),base)
 for y in [12.17,12.83]:
  for z in [1.15,2.05]:rod('Service cabinet bolt',(-7.357,y,z),(-7.38,y,z),.02,ivory)
 rod('Sealed service conduit',(-7.24,12.5,2.15),(-7.24,12.5,4.38),.025,steel)
 for z in [2.5,3.4,4.2]:box('Conduit saddle',(-7.20,12.5,z),(.12,.10,.055),steel,.003)
 box('Conduit weather termination',(-7.22,12.5,4.37),(.16,.18,.16),steel)
 # Compact visitor/inspection station: all five props supported by one wall rail.
 paper=mat('EXT weathered inspection card',(.61,.57,.43),.94)
 brass=mat('EXT handled brass',(.36,.24,.09),.38,.7)
 box('Inspection station backing',(4.02,16.175,1.6),(1.45,.065,1.12),steel)
 for x in [3.40,4.64]:
  for z in [1.14,2.06]:rod('Station anchor',(x,16.20,z),(x,16.226,z),.025,ivory)
 box('Manifest weather hood',(4.02,16.31,2.19),(1.55,.40,.05),steel)
 box('Clipboard fibre board',(3.60,16.229,1.70),(.35,.035,.48),base)
 box('Inspection sheet',(3.60,16.252,1.70),(.29,.006,.40),paper,.001)
 box('Clipboard spring clip',(3.60,16.27,1.92),(.16,.025,.07),brass,.008)
 text('Inspection heading','INSPECT',(3.60,16.262,1.80),.045)
 for z in [1.73,1.67,1.61]:box('Inspection ruled line',(3.60,16.257,z),(.23,.003,.003),steel,.0005)
 box('Visitor document pocket',(4.15,16.29,1.61),(.42,.18,.29),steel)
 box('Document stack',(4.15,16.285,1.79),(.31,.04,.27),paper,.002)
 text('Manifest heading','MANIFEST',(4.15,16.31,1.86),.035)
 box('Permit stamp shelf',(4.05,16.34,1.23),(1.20,.29,.035),steel)
 rod('Stamp handle',(4.38,16.34,1.29),(4.38,16.34,1.44),.038,rubber)
 box('Stamp rubber base',(4.38,16.34,1.27),(.12,.09,.045),rubber,.004)
 rod('Marker holder',(4.62,16.27,1.55),(4.62,16.27,1.74),.025,brass)
 for z in [1.58,1.71]:box('Marker holder attachment',(4.62,16.239,z),(.07,.066,.035),brass,.003)
 rod('Marker pen',(4.62,16.27,1.66),(4.62,16.27,1.89),.012,rubber)
 # Localized handling chips and shelf abrasion, deliberately sparse.
 for x,z,w in [(2.58,1.33,.036),(2.71,1.55,.025),(3.50,1.24,.08),(4.34,1.24,.11)]:
  box('Localized hand wear',(x,16.2515 if x<3 else 16.487,z),(w,.003,.007),brass,.001)
 for x in [-2.25,2.25]:
  for z in [.19,.42,.65]:
   wear=box('Gate edge exposed metal',(x,15.893,z),(.016,.005,.065),base,.001);wear['runtime_binding']='P2 blast leaf '+('west' if x<0 else 'east')
 # Original rear closure stays closed; exposed sleeve gets proper removable cap detailing.
 for x in [-1.315,1.315]:box('Rear sleeve side jacket',(x,-1.14,1.30),(.035,1.95,2.6),base)
 box('Rear sleeve top flashing',(0,-1.15,2.64),(2.68,2.02,.06),steel)
 for x in [-1.24,1.24]:box('Rear cap vertical frame',(x,-2.12,1.3),(.075,.055,2.6),steel)
 box('Rear cap head flashing',(0,-2.12,2.66),(2.55,.055,.075),steel)
 for x in [-1.24,1.24]:
  for z in [.2,.93,1.66,2.4]:rod('Rear cap fixing',(x,-2.15,z),(x,-2.17,z),.026,ivory)
if SID=='compliance-dock':build_compliance()
elif SID=='spawn-room':exec((ROOT/'blender/exterior_spawn.py').read_text(),globals())
elif SID=='medical-reanimation':exec((ROOT/'blender/exterior_medical.py').read_text(),globals())
elif SID=='waste-storage':exec((ROOT/'blender/exterior_waste.py').read_text(),globals())
elif SID=='electrical-room':exec((ROOT/'blender/exterior_electrical.py').read_text(),globals())
elif SID=='turbine-room':exec((ROOT/'blender/exterior_turbine.py').read_text(),globals())
elif SID=='condenser-bay':exec((ROOT/'blender/exterior_condenser.py').read_text(),globals())
elif SID=='cooling-plant':exec((ROOT/'blender/exterior_cooling.py').read_text(),globals())
elif SID=='reactor-room':exec((ROOT/'blender/exterior_reactor.py').read_text(),globals())
elif SID=='fuel-corridor':exec((ROOT/'blender/exterior_fuel.py').read_text(),globals())
elif SID=='refinery':exec((ROOT/'blender/exterior_refinery.py').read_text(),globals())
elif SID=='mine':exec((ROOT/'blender/exterior_mine.py').read_text(),globals())
else:raise ValueError('Exterior section has no authored design: '+SID)
with bpy.data.libraries.load(str(source),link=True) as (src,dst):dst.collections=['MODULE_'+SID]
ob=bpy.data.objects.new('READ_ONLY_ORIGINAL_'+SID,None);scene.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=dst.collections[0]
emitter_sizes={'reactor-room':{'Stair practical':(.18,.18),'Stair practical.001':(.18,.18),'Stair practical.002':(.18,.18),'Stair practical.003':(.18,.18),'Stair practical.004':(.18,.18),'Ground stair working light':(.15,.15),'RF skylight daylight.003':(4,3)},'mine':{'CSM_Bay_warm_bounce':(.5,.5),'CSM_Portal_daylight_fill':(1.2,1.2)},'cooling-plant':{'exchanger side wall shaping':(.8,.8)},'spawn-room':{'V_LIGHT_BRIEF_wall':(.3,.3),'V_LIGHT_HALL_info':(.3,.3),'V_LIGHT_HALL_staff':(.3,.3),'V_LIGHT_LOCKER_bays':(.3,.3)},'turbine-room':{'Entry broad fill':(1,1),'Hall broad daylight':(.8,.8),'Clerestory broad fill':(.6,.4),'Clerestory broad fill.001':(.6,.4),'Clerestory broad fill.002':(.6,.4)}}.get(SID,{})
if any(o.type=='LIGHT' and (not o.data.use_shadow or o.name in emitter_sizes) for o in dst.collections[0].all_objects):
 # Preserve source collection hierarchy/visibility while copying only changed lights.
 fixes=[]
 light_copies={}
 def clone_source_collection(col,root=False):
  copy=bpy.data.collections.new('SOURCE_REVIEW_'+SID if root else 'SOURCE_TREE_'+SID+'_'+col.name)
  copy.hide_render=col.hide_render;copy.hide_viewport=col.hide_viewport;copy.instance_offset=col.instance_offset
  for original in col.objects:
   target=original
   if original.type=='LIGHT' and (not original.data.use_shadow or original.name in emitter_sizes):
    if original not in light_copies:
     light=original.copy();light.data=original.data.copy();light.data.use_shadow=True
     if original.name in emitter_sizes:light.data.size,light.data.size_y=emitter_sizes[original.name]
     light_copies[original]=light;fixes.append(original.name)
    target=light_copies[original]
   copy.objects.link(target)
  for child in col.children:copy.children.link(clone_source_collection(child))
  return copy
 wrapper=clone_source_collection(dst.collections[0],True)
 ob.instance_collection=wrapper
 scene['source_review_collection']='SOURCE_REVIEW_'+SID;scene['assembly_light_shadow_corrections']=json.dumps(fixes)
for side,a,b in ([('west',-2.23,-.07),('east',.07,2.23)] if SID=='compliance-dock' else []):
 leaf=bpy.data.objects.get('P2 blast leaf '+side)
 for i in range(12):
  rib=box('Gate exterior pressed rib '+side,(a+(i+.5)*(b-a)/12,15.914,1.75),(.035,.048,3.30),steel,.005)
  if leaf:
   rib['runtime_binding']='P2 blast leaf '+side;rib['runtime_note']='Attach to corresponding door leaf during engine import; review geometry in closed pose'
scene.render.engine='CYCLES';scene.cycles.samples=32
world=bpy.data.worlds.new('Neutral exterior review daylight');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.8,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.45;scene.world=world
ld=bpy.data.lights.new('Review sun','SUN');ld.energy=2;ld.angle=.15;ob=bpy.data.objects.new('Review sun',ld);scene.collection.objects.link(ob);ob.rotation_euler=(.4,-.5,-.5)
camera_specs=globals().get('camera_specs',[('FRONT',(0,32,2.5),(0,16,2.2)),('OBLIQUE',(-19,31,9),(0,9,2.5)),('REVERSE',(17,-14,8),(0,8,2.5)),('DETAIL',(5.5,21.0,1.65),(3.45,16.15,1.70))])
for name,loc,target in camera_specs:
 cu=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cu.lens=32;cu.clip_end=300
scene.camera=bpy.data.objects['FRONT'];scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
scene['scope']='Additive exterior candidate '+REV+'. Original room and portal dimensions preserved. Acceptance recorded separately.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'exterior-{REV}.blend'),compress=True,relative_remap=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
with (OUT/'TASK_STATE.md').open('a') as f:f.write('\n\n## Build '+REV+'\nConcept preview exists; additive candidate built. Review and validation status must be read from revision-specific reports. Source SHA256 '+digest+' unchanged. No acceptance implied by this build.\n')
print('EXTERIOR_BUILD_DONE',SID,len(ext.objects),flush=True)
