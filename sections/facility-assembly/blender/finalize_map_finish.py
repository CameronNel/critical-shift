import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A10_map_finish.blend'),load_ui=False)
with bpy.data.libraries.load(str(O/'reactor-finish-A11.blend'),link=False) as (src,dst):dst.collections=['17_REACTOR_EXTERIOR_FINISH','18_REACTOR_FINISH_VIEWPORT_CACHE']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
bpy.data.collections['17_REACTOR_EXTERIOR_FINISH'].hide_viewport=True
col=bpy.data.collections['11_ACCESS_ARCHITECTURE'];template=bpy.data.objects['R19 actual stair portal header']
def box(name,loc,size):
 ob=template.copy();ob.data=template.data.copy();col.objects.link(ob);ob.name=name;ob.location=loc;ob.dimensions=size;return ob
box('Stair hanging direction board',(31.1,43.81,2.99),(2.1,.035,.30))
for x in [30.3,31.9]:box('Direction board support',(x,43.74,3.20),(.035,.06,.22))
box('Lift branch route plaque',(33.786,40.6,-4.37),(.025,2.1,.30))
o=bpy.data.objects['Lift wayfinding'];o.location.x=33.801
o=bpy.data.objects['Stair upper direction'];o.location.y=43.833;o.location.z=2.90
cache=bpy.data.objects['WALK_PROXY_ACCESS_FINISH'];m=np.asarray(cache.matrix_basis);inv=np.linalg.inv(m);v=np.empty(len(cache.data.vertices)*3,dtype=np.float32);cache.data.vertices.foreach_get('co',v);v=v.reshape(-1,3);w=v@m[:3,:3].T+m[:3,3]
mask=(np.abs(w[:,0]-34.05)<.008)&(w[:,2]>-4.46)&(w[:,2]<-4.15)&(w[:,1]>39)&(w[:,1]<42);w[mask,0]-=.249
mask=(np.abs(w[:,1]-43.53)<.008)&(w[:,2]>2.92)&(w[:,2]<3.13)&(w[:,0]>29.8)&(w[:,0]<32.4);w[mask,1]+=.303;w[mask,2]-=.03
v=w@inv[:3,:3].T+inv[:3,3];cache.data.vertices.foreach_set('co',v.astype(np.float32).ravel());cache.data.update()
# A moving cabin carries its own practical light.
lift=bpy.data.objects['ACCESS_CART_LIFT'];d=bpy.data.lights.new('Lift cabin courtesy light','AREA');d.energy=75;d.color=(1,.86,.68);d.shape='RECTANGLE';d.size=.8;d.size_y=.3
ob=bpy.data.objects.new(d.name,d);bpy.data.collections['12_ACCESS_MOVING_PARTS'].objects.link(ob);ob.parent=lift;ob.location=(30.05,34.85,2.25)
d=bpy.data.lights.new('Upper stair approach practical','POINT');d.energy=45;d.color=(1,.86,.68);d.shadow_soft_size=.22;ob=bpy.data.objects.new(d.name,d);col.objects.link(ob);ob.location=(30.35,44.05,1.45)
bpy.context.scene.name='FACILITY_A11_MAP_FINISH'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
bpy.context.scene.name='FACILITY_A11_MAP_FINISH_MASTER';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A11_map_finish.blend'),compress=True)
print('A11_FINISH_SAVED',flush=True)
