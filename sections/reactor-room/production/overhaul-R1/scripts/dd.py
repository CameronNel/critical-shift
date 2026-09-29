import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index("--")+1])
for o in bpy.data.objects:
    if "closed distant doors" in o.name:
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]
        print("DOOR",o.name,"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%(min(p.x for p in bb),max(p.x for p in bb),min(p.y for p in bb),max(p.y for p in bb),min(p.z for p in bb),max(p.z for p in bb)))
