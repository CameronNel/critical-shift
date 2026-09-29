import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w39.blend")
pre=sys.argv[sys.argv.index("--")+1]
for o in bpy.data.objects:
    if o.name.startswith(pre) and o.type in("MESH","CURVE","FONT"):
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]
        print("Q",o.name[:48],o.type,"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%(min(p.x for p in bb),max(p.x for p in bb),min(p.y for p in bb),max(p.y for p in bb),min(p.z for p in bb),max(p.z for p in bb)))
