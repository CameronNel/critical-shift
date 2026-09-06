import bpy,json
from mathutils import Vector
s=bpy.context.scene;c=bpy.data.objects['REFERENCE_LOCKER'];dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for x,y in [(150,420),(200,600),(370,440),(450,500)]:
    d=Vector(((x/1600-.5)*c.data.sensor_width/c.data.lens,(.5-y/900)*c.data.sensor_width/c.data.lens*900/1600,-1)).normalized()
    hit,loc,n,face,o,_=s.ray_cast(dg,c.matrix_world.translation,c.matrix_world.to_3x3()@d)
    if hit:rows.append({'pixel':[x,y],'object':o.name,'point':list(loc),'normal':list(n),'bounds':[list(p) for p in o.bound_box],'materials':[m.name if m else None for m in o.data.materials],'parent':o.parent.name if o.parent else None})
print('SURFACES',json.dumps(rows),flush=True)
