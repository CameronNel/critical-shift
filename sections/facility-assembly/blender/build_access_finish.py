"""Build the condenser passage concept into additive, replayable scenery."""
import bpy,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish';O.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
ext=bpy.data.collections.new('13_FINISHED_ACCESS_SCENERY');bpy.context.scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
rawrod=rod
def rod(*args,**kwargs):
 o=rawrod(*args,**kwargs)
 for p in list(o.data.polygons)[2:]:p.use_smooth=True
 return o
olive=mat('ACCESS FINISH olive enamel',(.19,.23,.135),.72,.35)
ochre=mat('ACCESS FINISH safety paint',(.59,.36,.075),.74,.15)
red=mat('ACCESS FINISH hose red rubber',(.29,.055,.025),.82)
pipe=mat('ACCESS FINISH galvanized services',(.29,.31,.28),.52,.70)
lens=mat('ACCESS FINISH frosted lamp',(.86,.80,.63),.65)
for m in [olive,ochre,pipe,steel]:
 n=m.node_tree.nodes;links=m.node_tree.links;geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=45
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.008
 links.new(geo.outputs['Position'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
lens.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.86,.80,.63,1)
lens.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.35
def label(name,body,p,size,normal):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0005
 ob=bpy.data.objects.new(name,cu);ext.objects.link(ob);ob.location=p;ob.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();cu.materials.append(ivory);return ob
def tube(name,points,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,q in zip(sp.points,points):p.co=(*q,1)
 ob=bpy.data.objects.new(name,cu);ext.objects.link(ob);cu.materials.append(m);return ob
for side,y in [(-1,43.18),(1,46.62)]:
 inward=-side
 for i in range(8):
  x=35.15+i*1.40
  box('Bolted olive access panel',(x,y,-5.46),(1.38,.055,1.04),olive,.006)
  box('Steel kick guard',(x,y+inward*.04,-5.87),(1.39,.025,.24),steel,.003)
  for xx in [x-.62,x+.62]:
   for zz in [-5.84,-5.04]:rod('Recessed panel fastener',(xx,y+inward*.032,zz),(xx,y+inward*.045,zz),.019,pipe)
 for z in [-4.93,-5.96]:box('Continuous folded panel cap',(40.05,y+inward*.01,z),(11.2,.085,.035),steel,.003)
 for z,off,radius in [(-3.42,.31,.12),(-3.40,.63,.085)]:
  yy=y+inward*off
  rod('Continuous overhead service pipe',(34.7,yy,z),(45.6,yy,z),radius,pipe)
  for x in [35,37.2,39.4,41.6,43.8,45.3]:
   rod('Pipe union collar',(x-.055,yy,z),(x+.055,yy,z),radius+.022,steel)
 for x in [35.1,38.4,41.7,45]:
  box('Pipe bracket wall plate',(x,y+inward*.06,-3.57),(.18,.08,.50),steel,.004)
  box('Pipe bracket cantilever',(x,y+inward*.43,-3.60),(.09,.78,.085),steel,.004)
  rod('Pipe bracket knee',(x,y+inward*.1,-3.8),(x,y+inward*.77,-3.60),.028,steel)
  for zz in [-3.76,-3.37]:rod('Bracket anchor bolt',(x,y+inward*.10,zz),(x,y+inward*.13,zz),.025,pipe)
 # Conduit remains against the wall, with clipped vertical drops to each box.
 yy=y+inward*.09;rod('Surface conduit',(34.7,yy,-3.82),(45.4,yy,-3.82),.025,steel)
 for x in ([37.6,44.0] if side==-1 else [40.9]):
  box('Weatherproof service box',(x,y+inward*.13,-4.35),(.45,.22,.66),olive,.016)
  box('Service box lid',(x,y+inward*.25,-4.35),(.40,.028,.59),steel,.006)
  rod('Box feed conduit',(x,yy,-3.82),(x,yy,-4.03),.025,steel)
  for zz in [-3.87,-3.98]:box('Conduit saddle',(x,yy,zz),(.085,.09,.02),pipe,.002)
  label('Equipment label','LOCAL\nSERVICE',(x,y+inward*.27,-4.36),.07,(0,inward,0))
  for xx in [x-.15,x+.15]:
   for zz in [-4.57,-4.13]:rod('Lid captive screw',(xx,y+inward*.27,zz),(xx,y+inward*.277,zz),.011,pipe)
# Warm sealed luminaires with end clips and a protective frame.
for x in [35.5,39.1,42.7,45.8]:
 box('Sealed luminaire body',(x,44.9,-3.22),(1.05,.30,.11),steel,.018)
 box('Frosted lamp diffuser',(x,44.9,-3.285),(.94,.22,.035),lens,.012)
 for xx in [x-.46,x+.46]:box('Luminaire end clip',(xx,44.9,-3.30),(.034,.26,.025),pipe,.003)
 d=bpy.data.lights.new('Warm access downlight','AREA');d.energy=130;d.color=(1,.86,.68);d.shape='RECTANGLE';d.size=1.0;d.size_y=.3
 ob=bpy.data.objects.new(d.name,d);ext.objects.link(ob);ob.location=(x,44.9,-3.34)
# Recessed-edge drain cover, concrete joints and narrow navigation line.
for i in range(55):
 x=34.65+i*.205
 box('Drain cover segment',(x,43.43,-5.994),(.195,.16,.012),steel,.001)
 for off in [-.055,0,.055]:box('Drain inlet slot',(x,43.43+off,-5.985),(.145,.016,.004),rubber,.0005)
box('Ochre floor route stripe',(40.1,43.61,-5.991),(11.1,.055,.006),ochre,.001)
for x in [35.5,37.8,40.1,42.4,44.7]:box('Floor expansion seam',(x,44.95,-5.991),(.014,2.92,.005),rubber,.0005)
# Proper wall-mounted hose reel, supported hub, coiled hose and hanging nozzle.
x=43.5;y=46.43;z=-4.45
box('Hose bracket',(x,46.57,z),(.24,.18,.30),steel,.006)
rod('Hose reel spindle',(x,46.60,z),(x,46.18,z),.07,pipe)
for yy in [46.25,46.40]:
 tube('Hose reel rim',[(x+.34*math.cos(a*math.tau/48),yy,z+.34*math.sin(a*math.tau/48)) for a in range(49)],.024,red)
 for a in range(6):rod('Hose reel spoke',(x,yy,z),(x+.33*math.cos(a*math.tau/6),yy,z+.33*math.sin(a*math.tau/6)),.018,red)
for radius in [.15,.20,.25,.29]:tube('Coiled service hose',[(x+radius*math.cos(a*math.tau/48),46.33,z+radius*math.sin(a*math.tau/48)) for a in range(49)],.024,red)
tube('Hanging hose tail',[(x+.28,46.30,z),(x+.36,46.30,z-.45),(x+.23,46.30,z-.73),(x+.07,46.30,z-.68)],.025,red)
rod('Hose nozzle',(x+.07,46.30,z-.68),(x+.02,46.30,z-.49),.036,pipe)
o=label('Condenser passage identification','CONDENSER BAY',(39.9,43.218,-4.10),.28,(0,1,0));o.data.materials.clear();o.data.materials.append(steel)
o=label('Condenser level identification','-06',(39.9,43.218,-4.62),.32,(0,1,0));o.data.materials.clear();o.data.materials.append(steel)
box('Department sign underline',(39.9,43.215,-4.24),(3.6,.014,.055),ochre,.001)
label('Lift wayfinding','CART LIFT  /  STAIRS',(34.05,40.6,-4.45),.13,(1,0,0))
# Upper/lower lift identification and functional-looking floor indicator surrounds.
for z in [0,-6]:
 box('Lift landing call panel',(31.42,36.29,z+1.2),(.18,.16,.36),olive,.008)
 label('Lift floor plate','G' if z==0 else '-06',(31.52,36.29,z+1.62),.17,(1,0,0))
label('Stair upper direction','CONDENSER  -06',(31.1,43.53,2.93),.16,(0,1,0))
# Modest, supported stair-wall practicals.
for x,y,z in [(30.24,40.5,-.8),(33.55,41.5,-3.8)]:
 box('Stair wall bulkhead',(x,y,z),(.11,.36,.18),steel,.008)
 d=bpy.data.lights.new('Stair warm bulkhead','POINT');d.energy=65;d.color=(1,.86,.68);d.shadow_soft_size=.22;o=bpy.data.objects.new(d.name,d);ext.objects.link(o);o.location=(x+.20 if x<31 else x-.20,y,z)
cache=bpy.data.collections.new('14_ACCESS_FINISH_VIEWPORT_CACHE');bpy.context.scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in list(ext.objects):
 if o.type not in {'MESH','CURVE','FONT'}:continue
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);copies.append(cp)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_ACCESS_FINISH';cache.hide_render=True
bpy.data.libraries.write(str(O/'access-finish-A09.blend'),{ext,cache},compress=True,path_remap='RELATIVE')
(O/'ACCESS_BUILD.json').write_text(json.dumps({'objects':len(ext.objects),'clear_lower_lane_y':[43.65,46.15],'services_min_height_m':2.43,'concept':'concepts/CONDESER_ACCESS.png','scope':'Additive passage and lift/stair finishing; original architecture preserved'},indent=2))
print('ACCESS_FINISH_BUILT',len(ext.objects),flush=True)
