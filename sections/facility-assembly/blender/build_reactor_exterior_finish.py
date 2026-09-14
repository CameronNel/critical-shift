"""Assembly-local seam backing and supported reactor identification/service details."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R/'exteriors/reactor-room/exterior-R05.blend'),link=False) as (src,dst):dst.collections=['EXTERIOR_reactor-room']
baseline=dst.collections[0];bpy.context.scene.collection.children.link(baseline)
ext=bpy.data.collections.new('17_REACTOR_EXTERIOR_FINISH');bpy.context.scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
seal=mat('Reactor rainscreen dark joint backing',(.12,.13,.115),.91)
count=0
for o in baseline.objects:
 if not o.name.startswith('Reactor exterior Shell'):continue
 pts=[v.co for v in o.data.vertices];size=Vector([max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)])
 backing=box('Reactor closed rainscreen joint backing',(0,0,0),(size.x+.10,.008,size.z+.10),seal,.001)
 backing.matrix_world=o.matrix_basis@Matrix.Translation((0,-.008,0));count+=1
# Identification is now carried on a solid bolted sign instead of crossing facade joints.
box('Reactor identification signboard',(0,-11.23,8.24),(5.9,.075,1.22),steel,.015)
text('Reactor sign lettering','REACTOR',(0,-11.272,7.96),.75)
ob=bpy.data.objects['Reactor sign lettering'];ob.rotation_euler=(math.pi/2,0,0)
for x in [-2.75,2.75]:
 for z in [7.8,8.68]:rod('Reactor sign anchor',(x,-11.277,z),(x,-11.294,z),.035,ivory)
# Small wall-mounted service runs use existing uninterrupted panels as their support.
for x in [-3.4,3.4]:
 box('Reactor exterior services cabinet',(x,-11.20,5.5),(.60,.25,1.0),steel,.015)
 box('Reactor services cabinet lid',(x,-11.34,5.5),(.52,.03,.91),base,.009)
 rod('Reactor facade sealed conduit',(x,-11.22,6),(x,-11.22,7.6),.035,steel)
 for z in [6.3,7.2]:box('Reactor conduit saddle',(x,-11.20,z),(.13,.16,.06),steel,.004)
 for dx in [-.21,.21]:
  for z in [5.12,5.88]:rod('Reactor cabinet captive screw',(x+dx,-11.36,z),(x+dx,-11.373,z),.016,ivory)
# Convert source-local package coordinates into the established assembled-map placement.
pose=json.loads((R/'production/LAYOUT_A08.json').read_text())['placements']['reactor-room']
transform=Matrix.Translation(Vector(pose['translation']))@Matrix.Rotation(math.radians(pose['rotation_z_degrees']),4,'Z')
for o in ext.objects:o.matrix_world=transform@o.matrix_basis
baseline.hide_viewport=True;baseline.hide_render=True
cache=bpy.data.collections.new('18_REACTOR_FINISH_VIEWPORT_CACHE');bpy.context.scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');items=[]
for o in ext.objects:
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);items.append(cp)
bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_REACTOR_FINISH';cache.hide_render=True
bpy.data.libraries.write(str(O/'reactor-finish-A11.blend'),{ext,cache},compress=True,path_remap='RELATIVE')
(O/'REACTOR_BUILD.json').write_text(json.dumps({'backed_panels':count,'source_exterior_preserved':'exteriors/reactor-room/exterior-R05.blend','scope':'Exterior rainscreen joints and service details only; reactor interior unchanged'},indent=2));print('REACTOR_FINISH_BUILT',count,flush=True)
