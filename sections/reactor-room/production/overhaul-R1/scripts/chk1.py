import bpy,sys,math
from mathutils import Vector
S=sys.argv[sys.argv.index("--")+1]; f=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.open_mainfile(filepath=S+"/"+f); sc=bpy.context.scene
for o in sc.objects:
    if o.name.startswith("LP haze"): o.hide_viewport=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def ray(o,d):
    h,l,n,i,ob,m=sc.ray_cast(dg,Vector(o),Vector(d)); return (round((l-Vector(o)).length,2),ob.name[:40]) if h else None
print("DOOR AXIS RAYS (from hall, height 1.5 and 3.0; expect first hit at the outer door plane, not the wall)")
for z in (1.5,3.0):
    print(" W  z",z,ray((-8.0,0.0,z),(-1,0,0)),"| expected door plane x=-14.39 -> dist 6.39")
    print(" N  z",z,ray((0.0,8.0,z),(0,1,0)),"| expected y=14.39 -> dist 6.39")
    r=1/math.sqrt(2); print(" SE z",z,ray((8.0,-8.0,z),(r,-r,0)),"| door at (10.92,-10.92)-> dist ~4.1")
for z in (1.5,):
    print(" W offset y=+2.5",ray((-8.0,2.5,z),(-1,0,0)),"| y=-2.5",ray((-8.0,-2.5,z),(-1,0,0)))
