import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/exterior-final'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),load_ui=False)
ext=bpy.data.collections.new('25_MINE_REFINERY_IDENTITIES');bpy.context.scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
for sid,body,p,n,width in [('mine','GULLET MINE',(-10.36,-29,3.35),(1,0,0),3.3),('refinery','FUEL REFINERY',(0,-7.87,3.55),(0,1,0),3.6)]:
 p=Vector(p);n=Vector(n);t=Vector((n.y,-n.x,0));o=box(sid+' department identity fascia',p,(width,.10,.45),accent,.012);o.rotation_euler.z=math.atan2(t.y,t.x)
 cu=bpy.data.curves.new(sid+' identity','FONT');cu.body=body;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.27;cu.extrude=.001;o=bpy.data.objects.new(cu.name,cu);ext.objects.link(o);o.location=p+n*.061;o.rotation_euler=n.to_track_quat('Z','Y').to_euler();cu.materials.append(ivory)
 for side in [-1,1]:q=p+t*width*.40*side;rod(sid+' sign stand-off',q-n*.2,q,.022,steel)
# These six additions are already cheap, and remain independently editable.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']:bpy.data.collections[name].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A14_exterior.blend'),compress=True)
(O/'EXTRA_IDENTITIES.json').write_text(json.dumps({'sections':['mine','refinery'],'source_port_coordinates':True},indent=2));print('MINE_REFINERY_IDENTITIES_SAVED',flush=True)
