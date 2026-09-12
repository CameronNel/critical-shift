"""Read-only nearest ray hits at the cold-render variance region."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();c=s.objects['C08_SERVICE_JUNCTION'];frame=c.data.view_frame(scene=s)
left=min(p.x for p in frame);right=max(p.x for p in frame);bottom=min(p.y for p in frame);top=max(p.y for p in frame)
rows=[]
for x,y in [(1054,550),(1054,600),(1054,695),(1052,550),(1056,550)]:
 direction=(c.matrix_world.to_3x3()@Vector((left+(right-left)*(x+.5)/1440,top+(bottom-top)*(y+.5)/960,frame[0].z))).normalized();origin=c.matrix_world.translation;hits=[]
 for i in range(4):
  hit,p,n,idx,o,m=s.ray_cast(dg,origin,direction,distance=30)
  if not hit:break
  hits.append({'object':o.name,'point':list(p),'material':[z.name for z in o.data.materials]});origin=p+direction*.00001
 rows.append({'pixel':[x,y],'hits':hits})
out=Path(os.environ['FUEL_CORRIDOR_ROOT'])/'production/evidence/final-pass/C08-edge-rays.json';out.write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
