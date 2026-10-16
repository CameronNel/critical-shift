import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index("--")+1]); sc=bpy.context.scene
for o in sc.objects:
    if o.name.startswith("LP haze"): o.hide_viewport=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def ray(o,d):
    h,l,n,i,ob,m=sc.ray_cast(dg,Vector(o),Vector(d)); return (round(l.y,2),ob.name[:40]) if h else None
def e(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]; return min(q.y for q in p),max(q.y for q in p)
g=bpy.data.objects["MZ window glass"]; b=[o for o in bpy.data.objects if o.name.startswith("R2 control cr back wall")][0]
print("DEPTH glass y=%.2f  back wall inner face y=%.2f  depth=%.2f m (was 3.94)"%(e(g)[1],e(b)[1],e(g)[1]-e(b)[1]))
print("RAYS toward -Y from inside the room (first hit y):")
for x in (-4.0,-2.0,-1.4,0.0,1.5):
    for z in (6.0,7.5,8.5): print("  x=%.1f z=%.1f ->"%(x,z),ray((x,-8.0,z),(0,-1,0)))
print("hall wall seen from the hall side above the room (x=-1.4, z=9.5 should still hit the wall at y=-10.8):",ray((-1.4,-8.0,9.5),(0,-1,0)))
print("hall wall next to the room (x=-5.6, z=7):",ray((-5.6,-8.0,7.0),(0,-1,0)))
