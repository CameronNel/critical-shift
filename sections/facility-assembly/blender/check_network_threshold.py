import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'review-R03.blend'),load_ui=False)
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [-42,-41.1,-40.9,-40,-39]:
 for y in [25.4,25.6,25.8,26,27,28]:
  hit,loc,normal,face,ob,m=bpy.context.scene.ray_cast(dg,Vector((x,y,.2)),Vector((0,0,-1)),distance=1)
  rows.append({'x':x,'y':y,'z':round(loc.z,4) if hit else None,'object':ob.name if hit else None})
(OUT/'R12_SURFACE_HEIGHTS.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
