import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),load_ui=False)
col=bpy.data.collections['19_MAP_COMPLETION'];mat=bpy.data.materials['Map ground warm concrete'];v=[];f=[]
def box(c,s):
 k=len(v);v.extend([(c[0]+a*s[0]/2,c[1]+b*s[1]/2,c[2]+d*s[2]/2) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
 f.extend([tuple(k+i for i in p) for p in [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]])
box((-14,9.5,-8.25),(194,155,.5))
for y in [-67,86]:box((-14,y,-6),(192,.4,4))
for x in [-110,82]:box((x,9.5,-6),(.4,153,4))
me=bpy.data.meshes.new('Closed below-grade site base');me.from_pydata(v,[],f);me.materials.append(mat);ob=bpy.data.objects.new('Closed below-grade site base',me);col.objects.link(ob)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A12_complete.blend'),compress=True)
print('SITE_BASE_CLOSED_Z_MINUS_8',flush=True)
