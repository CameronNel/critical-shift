from mathutils import Vector
import bpy
p, t = (0.72, 1.48, 3.25), (3.10, 3.70, 5.15)
o = bpy.data.objects["C04_EXHAUST"]
o.location = p
o.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
o.data.lens = 26
bpy.ops.wm.save_mainfile()
print("PATCHED_C04", flush=True)
