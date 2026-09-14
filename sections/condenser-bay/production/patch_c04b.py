from mathutils import Vector
import bpy
p, t = (1.55, 2.18, 4.88), (3.05, 3.55, 5.45)
o = bpy.data.objects["C04_EXHAUST"]
o.location = p
o.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
o.data.lens = 28
bpy.ops.wm.save_mainfile()
print("PATCHED_C04B", list(o.location), flush=True)
