"""Remove coplanar landing overlaps without changing the access footprint."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),load_ui=False)
rects=[(30.25,35.5,44.4,46.65),(33.5,48.3,43.15,46.65),(31.15,35.5,33.3,36.5),(33.5,35.5,35,44.4)]
names=['Lower landing','Condenser passage','Lift lower passage','Lift branch'];material=bpy.data.objects['Condenser passage'].data.materials[0]
xs=sorted({x for r in rects for x in r[:2]});ys=sorted({y for r in rects for y in r[2:]});cells=set()
for i,(a,b) in enumerate(zip(xs,xs[1:])):
 for j,(c,d) in enumerate(zip(ys,ys[1:])):
  if any(x1<(a+b)/2<x2 and y1<(c+d)/2<y2 for x1,x2,y1,y2 in rects):cells.add((i,j))
vertices=[];faces=[];index={}
def vi(p):
 if p not in index:index[p]=len(vertices);vertices.append(p)
 return index[p]
def face(points):faces.append(tuple(vi(p) for p in points))
for i,j in cells:
 a,b=xs[i:i+2];c,d=ys[j:j+2];z=-6.;low=-6.2
 face([(a,c,z),(b,c,z),(b,d,z),(a,d,z)]);face([(a,d,low),(b,d,low),(b,c,low),(a,c,low)])
 if (i-1,j) not in cells:face([(a,c,low),(a,c,z),(a,d,z),(a,d,low)])
 if (i+1,j) not in cells:face([(b,d,low),(b,d,z),(b,c,z),(b,c,low)])
 if (i,j-1) not in cells:face([(b,c,low),(b,c,z),(a,c,z),(a,c,low)])
 if (i,j+1) not in cells:face([(a,d,low),(a,d,z),(b,d,z),(b,d,low)])
me=bpy.data.meshes.new('Continuous lower access floor mesh');me.from_pydata(vertices,[],faces);me.materials.append(material);o=bpy.data.objects.new('Continuous lower access floor',me);bpy.data.collections['11_ACCESS_ARCHITECTURE'].objects.link(o)
for name in names+['R19 flight 1 tread 18','R19 flight 2 tread 18']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
bpy.context.scene.name='FACILITY_A11_MAP_FINISH_MASTER';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A11_map_finish.blend'),compress=True)
(R/'connections/map-finish/FLOOR_UNION.json').write_text(json.dumps({'rectangles':rects,'union_cells':len(cells),'coplanar_overlaps_removed':True,'stair_risers':36,'separate_treads':34,'landing_risers':2},indent=2));print('ACCESS_FLOOR_UNION_SAVED',flush=True)
