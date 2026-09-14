from mathutils import Vector
import bpy
p = (7.05, 1.90, 3.10)
t = (3.00, 4.05, 5.92)
o = bpy.data.objects["C09_ROOF"]
o.location = p
o.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
o.data.lens = 24
bpy.ops.wm.save_mainfile()
print("PATCHED_C09", list(o.location), flush=True)
