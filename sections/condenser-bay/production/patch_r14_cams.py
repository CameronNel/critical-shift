from mathutils import Vector
import bpy

def aim(n, p, t, lens):
    o = bpy.data.objects[n]
    o.location = p
    o.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens
    print("AIM", n, list(o.location), flush=True)

aim("C04_EXHAUST", (0.72, 1.48, 3.25), (3.10, 4.05, 5.55), 24)
aim("C05_RETURN", (0.45, 8.55, 1.58), (3.10, 5.85, 1.25), 24)
aim("W05_SE", (8.35, 2.85, 1.72), (6.40, 1.80, 3.55), 24)
aim("W08_GALLERY_TURN", (5.52, 4.88, 5.28), (3.25, 4.05, 5.35), 26)
bpy.ops.wm.save_mainfile()
print("PATCHED_R14_CAMS", flush=True)
