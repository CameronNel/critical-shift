import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w38.blend")
x0,x1,y0,y1,z0,z1=[float(a) for a in sys.argv[sys.argv.index("--")+1:][:6]]
for o in bpy.data.objects:
    if o.type not in("MESH","CURVE","FONT"): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    ax=(min(p.x for p in bb),max(p.x for p in bb),min(p.y for p in bb),max(p.y for p in bb),min(p.z for p in bb),max(p.z for p in bb))
    if ax[1]>=x0 and ax[0]<=x1 and ax[3]>=y0 and ax[2]<=y1 and ax[5]>=z0 and ax[4]<=z1:
        print("Q",o.users_collection[0].name[:16],"|",o.name[:44],o.type,"%.2f..%.2f %.2f..%.2f %.2f..%.2f"%ax)
