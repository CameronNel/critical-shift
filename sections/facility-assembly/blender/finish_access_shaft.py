"""Finish the below-grade retaining enclosure; callable in live or headless Blender."""
import bpy,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
if bpy.app.background:bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A08_access.blend'),load_ui=False)
col=bpy.data.collections['11_ACCESS_ARCHITECTURE'];template=bpy.data.objects['Lift branch west retaining wall']
for name,loc,size in [('Stair shaft west retaining wall',(30.10,42.28,-3),(.20,8.96,6)),('Stair shaft south retaining wall',(31.83,37.8,-3),(3.66,.20,6)),('Stair shaft north retaining wall',(32.25,46.76,-3),(4.3,.20,6)),('Stair shaft east upper retaining wall',(33.68,40.65,-1.5),(.20,5.5,3))]:
 if name in bpy.data.objects:continue
 o=template.copy();o.data=template.data.copy();col.objects.link(o);o.name=name;o.location=loc;o.dimensions=size
# The displaced pipe rack left six end flanges behind; remove its remaining parts.
network=bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'];boxes=[]
for o in list(network.objects):
 if not o.name.startswith('R14') or not any(k in o.name for k in ['spare flange','spare rack legs']):continue
 if 29.3<o.location.x<31.7 and 31<o.location.y<33.15:
  pts=[o.matrix_basis@Vector(v) for v in o.bound_box];lo=Vector([min(v[i] for v in pts)-.01 for i in range(3)]);hi=Vector([max(v[i] for v in pts)+.01 for i in range(3)]);boxes.append((lo,hi));bpy.data.objects.remove(o,do_unlink=True)
proxy=bpy.data.objects['WALK_PROXY_HORIZONTAL_NETWORK'];bm=bmesh.new();bm.from_mesh(proxy.data);m=proxy.matrix_basis
vs={v for v in bm.verts if any(all(lo[i]<=(m@v.co)[i]<=hi[i] for i in range(3)) for lo,hi in boxes)}
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v in vs for v in f.verts)],context='FACES');bm.to_mesh(proxy.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A08_access.blend'),compress=True)
names=['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE'];before={n:bpy.data.collections[n].hide_viewport for n in names}
for n in names:bpy.data.collections[n].hide_viewport=n in names[-2:]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A08_access.blend'),compress=True,copy=True)
for n,val in before.items():bpy.data.collections[n].hide_viewport=val
print('ACCESS_SHAFT_COMPLETE',len(boxes),flush=True)
