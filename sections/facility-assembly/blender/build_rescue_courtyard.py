"""C01 western rescue courtyard: rough massing, then concept-led detailing.
Source rooms are immutable. All geometry uses assembly world coordinates.
"""
import bpy,math,json,os,random,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
REV=os.environ.get('COURTYARD_REVISION','B01')
DETAIL=not REV.startswith('B')
OUT=ROOT/'connections'/'rescue-courtyard';OUT.mkdir(parents=True,exist_ok=True)
L=json.loads((ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
ext=bpy.data.collections.new('CONNECTION_C01_RESCUE_COURTYARD');scene.collection.children.link(ext)
helpers=(ROOT/'blender/build_exteriors.py').read_text()
exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
floor=mat('C01 warm concrete',(.45,.42,.34),.88)
pathmat=mat('C01 light rescue paving',(.67,.62,.49),.8)
green=mat('C01 sage wayfinding enamel',(.19,.28,.18),.64,.12)
wood=mat('C01 weathered bench timber',(.30,.19,.105),.87)
soil=mat('C01 planter soil',(.075,.058,.038),1)
leaf=mat('C01 olive leaves',(.19,.25,.095),.88)

def strip(name,a,b,width,material,z=-.105,depth=.2):
 a,b=Vector(a),Vector(b);v=b-a
 ob=box(name,((a.x+b.x)/2,(a.y+b.y)/2,z),(v.xy.length+.015,width,depth),material,.008)
 ob.rotation_euler.z=math.atan2(v.y,v.x);return ob

# Persist all-map greybox separately: circulation floors, not finished connectors.
rough=bpy.data.collections.new('CONNECTIONS_ALL_ROUTES_GREYBOX');scene.collection.children.link(rough)
own=ext;ext=rough
for r in L['routes']:
 if r['id']=='R19':continue # vertical access needs a real stair, never a vertical floor strip.
 for j,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
  strip('GREYBOX_'+r['id']+'_'+str(j),a,b,r['width_m'],base,z=-.14)
ext=own

# Existing west route plus a diagonal open-court rescue shortcut.
paths=[('refinery_dispatch',[[0,-8,0],[0,-4,0],[-15,-4,0],[-15,15,0],[-18,28,0],[-18,30.31,0]],4.0),
 ('refinery_staff',[[2.65,-18.40666,0],[6,-18.40666,0],[6,-4,0],[0,-4,0]],4.0),
 ('mine_bypass',[[-10.49,-29,0],[0,-29,0],[6,-29,0],[6,-4,0]],4.5),
 ('spawn_rescue',[[-28,12.3,0],[-28,28,0],[-18,28,0]],4.0),
 ('west_court',[[-41,28,0],[-29,28,0],[-15,28,0],[-7,28,0]],4.5)]
for name,pts,width in paths:
 for j,(a,b) in enumerate(zip(pts,pts[1:])):strip('C01_'+name+'_'+str(j),a,b,width,pathmat)
box('Open rescue courtyard foundation',(-21,22.65,-.18),(28,15.3,.34),floor,.04)
box('Northwest court edge',(-29,31.15,-.18),(12,1.7,.34),floor,.02)
box('Northeast court edge',(-10,31.15,-.18),(6,1.7,.34),floor,.02)
# Branch boundaries stay clear of spawn, fuel and medical shells.
box('North medical apron',(-18,29.3,-.12),(8,2.02,.23),pathmat,.025)

def bench(x,y,angle=0):
 parts=[]
 for dx in [-.7,.7]:
  parts.append(box('Bench steel leg',(x+dx,y,.23),(.08,.5,.44),steel))
  parts.append(box('Bench foot',(x+dx,y,.035),(.22,.62,.06),steel))
 for dy in [-.19,0,.19]:parts.append(box('Bench timber seat',(x,y+dy,.47),(1.9,.16,.07),wood))
 for z in [.7,.91]:parts.append(box('Bench back board',(x,y+.27,z),(1.9,.06,.16),wood))
 for dx in [-.75,.75]:parts.append(rod('Bench back support',(x+dx,y+.27,.08),(x+dx,y+.27,1.0),.035,steel))
 if angle:
  from mathutils import Matrix
  rot=Matrix.Rotation(angle,4,'Z')
  for ob in parts:ob.location=Vector((x,y,0))+rot.to_3x3()@(ob.location-Vector((x,y,0)));ob.rotation_euler.z+=angle

def planter(x,y,sx=2.4,sy=1.1):
 box('Raised planter concrete',(x,y,.27),(sx,sy,.52),cream,.04)
 box('Planter soil',(x,y,.542),(sx-.16,sy-.16,.03),soil,0)
 if DETAIL:
  random.seed(int((x+100)*93+(y+100)))
  for i in range(10):
   px=x+random.uniform(-sx*.38,sx*.38);py=y+random.uniform(-sy*.3,sy*.3)
   rod('Shrub branch',(px,py,.55),(px+.08,py,.95),.018,wood)
   for z in [.75,.92]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.28,location=(px,py,z))
    ob=bpy.context.object;ob.name='Olive shrub foliage';ob.scale=(1,.8,.6)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    ext.objects.link(ob);ob.data.materials.append(leaf)

for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:planter(x,y)
for x,y in [(-32,20),(-24,17),(-33,22)]:bench(x,y)

# Open-sided shade pavilion occupies the east edge, not the diagonal rescue route.
for x in [-11,-7.9]:
 for y in [20.2,24.8]:
  box('Shade pavilion steel post',(x,y,1.6),(.14,.14,3.2),steel)
  box('Pavilion baseplate',(x,y,.04),(.36,.36,.07),steel)
for x in [-11,-7.9]:box('Pavilion longitudinal beam',(x,22.5,3.12),(.18,5.0,.22),steel)
for y in [20.2,22.5,24.8]:box('Pavilion transverse beam',(-9.45,y,3.22),(3.45,.18,.20),steel)
box('Pavilion canopy roof',(-9.45,22.5,3.38),(3.65,5.35,.12),cream,.025)

# An unmistakable sheltered medical approach, leaving the actual door clear.
for x in [-21.1,-14.9]:
 box('Medical canopy wall shoe',(x,30.26,2.8),(.22,.10,.8),green)
 rod('Medical canopy wall brace',(x,30.20,2.6),(x,28.2,3.22),.055,steel)
box('Medical approach canopy',(-18,29.15,3.3),(7.5,2.2,.16),cream,.035)
box('Medical canopy fascia',(-18,28.07,3.12),(7.5,.10,.40),green)
text('Medical courtyard destination','REANIMATION  /  FIRST AID',(-18,28.005,3.00),.25)
bpy.data.objects['Medical courtyard destination'].rotation_euler.z=0

if DETAIL:
 # Expansion joints are shallow and never raised trip strips.
 for x in range(-34,-6,3):box('Paving expansion joint',(x,22.65,-.003),(.012,15.3,.008),rubber,0)
 for y in range(16,31,3):box('Paving expansion joint',(-21,y,-.003),(28,.012,.008),rubber,0)
 # Supported utility spares along the east approach; no loose pieces on the rescue path.
 for y in [1,5,9,13]:
  for dx in [-1,1]:box('Pipe rack leg',(-9+dx,y,.35),(.10,.12,.7),steel)
  box('Pipe rack crossbar',(-9,y,.7),(2.4,.13,.13),steel)
 for i in range(6):
  x=-10+i*.4;rod('Loose stored service pipe',(x,1,.88),(x,13,.88),.12,steel)
  for y in [1,13]:rod('Pipe flange',(x,y-.04,.88),(x,y+.04,.88),.19,accent)
 # Busy repair pocket at the lower courtyard edge, clear of all main lanes.
 for i in range(4):
  x=-21+i*.9
  box('Repair crate',(x,16,.37),(.72,.9,.7),wood,.025)
  for z in [.15,.56]:box('Crate steel strap',(x,15.54,z),(.74,.025,.055),steel,.005)
 for i in range(6):
  rod('Loose pipe offcut',(-33.3,23+i*.26,.12),(-31.5,23+i*.26,.12),.09,accent)
 for x,y in [(-33,31),(-8,31),(-19,15.3)]:
  rod('Yard light column',(x,y,0),(x,y,3.8),.07,steel)
  box('Yard light head',(x,y,3.75),(.46,.4,.15),steel)
  box('Warm light diffuser',(x,y,3.66),(.36,.3,.025),ivory)
 for x,y in [(-34,31),(-12,23)]:
  box('Waste sorting bin',(x,y,.53),(.68,.65,1.04),green,.04)
  box('Bin lid',(x,y,1.07),(.76,.73,.08),steel,.03)
 # Low service edging, deliberately discontinuous at paths and entrances.
 for a,b in [((-35,16,0),(-35,25,0)),((-35,31.8,0),(-31.5,31.8,0))]:
  strip('Courtyard low retaining edge',a,b,.22,cream,z=.22,depth=.44)
 # Wayfinding boards at decision points; not decorative arrows into closed walls.
 for x,y,body in [(-11.2,12,'REANIMATION  /  COURTYARD'),(-10,-.5,'MEDICAL  <  WEST COURT')]:
  for dx in [-1.1,1.1]:box('Wayfinding post',(x+dx,y,1.05),(.08,.08,2.1),green)
  box('Wayfinding board',(x,y,1.9),(2.5,.09,.48),green)
  text('Rescue wayfinding '+str(y),body,(x,y-.055,1.79),.15)
  bpy.data.objects['Rescue wayfinding '+str(y)].rotation_euler.z=0

if DETAIL:
 # Concept R01: folded standing seams, supported rainwater goods and service pockets.
 for x in [-11.1,-10.5,-9.9,-9.3,-8.7,-8.1]:
  box('Pavilion standing seam',(x,22.5,3.465),(.035,5.30,.055),green,.006)
 bpy.data.objects['Pavilion canopy roof'].data.materials[0]=green
 bpy.data.objects['Medical approach canopy'].data.materials[0]=green
 for x in [-21.4,-20.5,-19.6,-18.7,-17.8,-16.9,-16.0,-15.1,-14.5]:
  box('Medical canopy standing seam',(x,29.15,3.40),(.03,2.17,.04),green,.005)
 box('Pavilion gutter',(-7.61,22.5,3.31),(.15,5.42,.15),steel)
 rod('Pavilion downpipe',(-7.65,24.72,.12),(-7.65,24.72,3.35),.055,steel)
 for z in [.25,1.8,3.0]:box('Downpipe saddle',(-7.73,24.72,z),(.20,.12,.04),steel)
 # Flush drainage along the outer edge; no raised grates crossing the rescue lane.
 for x in [-34.6,-7.4]:
  box('Drain channel',(x,22.5,.002),(.24,12,.025),steel,0)
  for i in range(80):box('Drain grate slot',(x,16.6+i*.15,.017),(.19,.04,.006),rubber,0)
 # Service cabinet and hose reel beside the pavilion, away from all route strips.
 box('Services cabinet feet',(-10,23.6,.12),(.78,.64,.24),steel)
 box('Services cabinet',(-10,23.6,.72),(.75,.6,1.0),green,.025)
 box('Cabinet door',(-10,23.285,.72),(.66,.035,.88),steel,.012)
 for z in [.47,.53,.59,.65]:box('Cabinet ventilation slot',(-10,23.263,z),(.43,.008,.015),rubber,0)
 rod('Hose reel shaft',(-10,23.24,1.40),(-10,22.95,1.40),.05,steel)
 box('Hose reel bracket',(-10,23.38,1.32),(.16,.50,.16),steel)
 for y in [22.97,23.17]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.30,minor_radius=.028,major_segments=24,minor_segments=6,location=(-10,y,1.4),rotation=(math.pi/2,0,0))
  ob=bpy.context.object;ob.name='Hose reel rim'
  for c in list(ob.users_collection):c.objects.unlink(ob)
  ext.objects.link(ob);ob.data.materials.append(steel)
 for y in [23.00,23.05,23.10,23.15]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.23,minor_radius=.028,major_segments=24,minor_segments=6,location=(-10,y,1.4),rotation=(math.pi/2,0,0))
  ob=bpy.context.object;ob.name='Coiled service hose'
  for c in list(ob.users_collection):c.objects.unlink(ob)
  ext.objects.link(ob);ob.data.materials.append(accent)
# Union overlapping pavement solids so intersections cannot z-fight in renders.
floors=[o for o in ext.objects if o.name.startswith('C01_') or o.name in ['Open rescue courtyard foundation','Northwest court edge','Northeast court edge','North medical apron']]
base_floor=floors[0]
for ob in floors:
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 ob.select_set(False)
operands=bpy.data.collections.new('PAVING_BOOLEAN_INPUT');scene.collection.children.link(operands)
for ob in floors[1:]:operands.objects.link(ob)
bpy.context.view_layer.objects.active=base_floor
mod=base_floor.modifiers.new('Unified pavement intersections','BOOLEAN');mod.operation='UNION';mod.operand_type='COLLECTION';mod.collection=operands;mod.solver='EXACT'
bpy.ops.object.modifier_apply(modifier=mod.name)
for ob in floors[1:]:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(operands)
base_floor.name='Continuous rescue courtyard pavement'
asset=OUT/f'courtyard-{REV}.blend'
bpy.data.libraries.write(str(asset),{ext},path_remap='RELATIVE',fake_user=True,compress=True)
bpy.data.libraries.write(str(OUT/'all-routes-greybox.blend'),{rough},path_remap='RELATIVE',fake_user=True,compress=True)

# Reference context is an append of disposable cached geometry, never a source edit.
with bpy.data.libraries.load(str(ROOT/'blender/walkthrough_proxy_meshes.blend'),link=False) as (src,dst):dst.collections=['07_FAST_WALKTHROUGH_PROXIES']
context=dst.collections[0];scene.collection.children.link(context);context.hide_render=False
for ob in context.objects:
 ob.hide_render=False
 if ob.name in ['WALK_PROXY_medical-reanimation','WALK_PROXY_EXTERIOR_INSTANCE_medical-reanimation']:ob.location+=Vector((11,-6,0))
for name,loc,target,ortho in [('TOP',( -8,12,180),(-8,12,0),200),('COURT',(-36,12,16),(-20,25,0),None),('EYE',(-21,13,1.7),(-18,30.31,1.8),None)]:
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();data.lens=32;data.clip_end=500
 if ortho:data.type='ORTHO';data.ortho_scale=ortho
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Neutral courtyard daylight');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.8,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.5;scene.world=world
ld=bpy.data.lights.new('Courtyard afternoon sun','SUN');ld.energy=2.2;ld.angle=.16;ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.rotation_euler=(.4,-.5,-.5)
scene.view_settings.view_transform='AgX';scene.camera=bpy.data.objects['COURT']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'review-{REV}.blend'),compress=True)
(OUT/f'build-{REV}.json').write_text(json.dumps({'revision':REV,'source_rooms_unchanged':True,'asset':str(asset),'objects':len(ext.objects),'paths':paths,'new_shortcut':{'id':'R22','points':[[-15,15,0],[-18,28,0]],'width_m':4},'scope':'First western rescue courtyard; other connectors remain explicit greybox. No game collision/navmesh or working door/lift claim.'},indent=2))
print('COURTYARD_BUILT',REV,len(ext.objects),flush=True)




