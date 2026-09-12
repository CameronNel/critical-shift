import bpy,json
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for name,u,v in [('C07_BYPASS',.300,.887),('C07_BYPASS',.32,.86),('C07_BYPASS',.4,.90)]:
    c=s.objects[name];frame=c.data.view_frame(scene=s)
    left=min(p.x for p in frame);right=max(p.x for p in frame)
    bottom=min(p.y for p in frame);top=max(p.y for p in frame)
    direction=(c.matrix_world.to_3x3()@Vector((left+(right-left)*u,top+(bottom-top)*v,frame[0].z))).normalized()
    origin=c.matrix_world.translation;hits=[]
    for i in range(5):
        hit,p,n,idx,o,m=s.ray_cast(dg,origin,direction,distance=50)
        if not hit:break
        hits.append({'object':o.name,'point':list(p),'materials':[x.name for x in o.data.materials]})
        origin=p+direction*.001
    rows.append({'camera':name,'uv':[u,v],'hits':hits})
print(json.dumps(rows,indent=2))
