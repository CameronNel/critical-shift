import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for origin,direction in [((5,-20,1.8),(-1,0,0)),((5,-15.2,2.3),(-1,0,0)),((5,-20.6,2),(-1,0,0)),((-14,-19,1.5),(1,0,0)),((-7,-27,1.9),(0,1,0))]:
 p=Vector(origin);hits=[]
 for i in range(8):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector(direction),distance=8)
  if not hit:break
  hits.append(dict(object=o.name,co=list(co),normal=list(n),material=o.data.materials[o.data.polygons[fi].material_index].name if o.type=='MESH' and fi<len(o.data.polygons) and len(o.data.materials) else ''))
  p=co+Vector(direction)*.002
 rows.append(dict(origin=origin,hits=hits))
(Path(__file__).resolve().parents[3]/'runtime/out/environment/refinery-finish/probe.json').write_text(json.dumps(rows,indent=2))
