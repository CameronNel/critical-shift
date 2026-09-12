"""Read-only camera obstruction probe from a saved scene; no render or save."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
name=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'D05_GATE_MECHANISM'
camera=bpy.data.objects[name];origin=camera.matrix_world.translation.copy();rotation=camera.matrix_world.to_3x3()
if '--pose' in sys.argv:
    i=sys.argv.index('--pose'); values=list(map(float,sys.argv[i+1:i+7]));origin=Vector(values[:3]);rotation=(Vector(values[3:])-origin).to_track_quat('-Z','Y').to_matrix()
inside=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    if all(min(v[i] for v in bb)-.001<=origin[i]<=max(v[i] for v in bb)+.001 for i in range(3)):inside.append(ob.name)
rows=[];dg=bpy.context.evaluated_depsgraph_get()
for u,v in [(0,0),(-.2,0),(.2,0),(0,-.15),(0,.15),(-.2,-.15),(.2,.15)]:
    direction=rotation@Vector((u,v,-1)).normalized()
    hit,loc,normal,index,obj,matrix=bpy.context.scene.ray_cast(dg,origin,direction,distance=8)
    rows.append({'uv':[u,v],'hit':bool(hit),'object':obj.name if hit else None,'distance':(loc-origin).length if hit else None,'point':list(loc) if hit else None})
report={'camera':name,'origin':list(origin),'inside_bounds':inside,'rays':rows,'scene_modified':False,'rendered':False}
print(json.dumps(report,indent=2))
