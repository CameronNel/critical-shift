"""Apply R20 camera recrops to the saved blend without a factory rebuild."""
from pathlib import Path
from mathutils import Vector
import bpy

BLEND = Path(__file__).resolve().parent / "condenser_bay.blend"

CAMS = [
    ("C04_EXHAUST", (5.82, 4.05, 5.12), (3.00, 4.05, 6.18), 26),
    ("C06_COOLING", (6.55, 2.20, 2.45), (8.55, 4.15, 4.55), 28),
    ("C09_ROOF", (5.45, 5.90, 4.95), (3.00, 4.05, 6.05), 28),
    ("W08_GALLERY_TURN", (5.85, 5.40, 5.12), (5.85, 3.55, 5.00), 28),
]


def aim(name, loc, target, lens):
    o = bpy.data.objects[name]
    o.location = loc
    o.data.lens = lens
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


for n, p, t, lens in CAMS:
    aim(n, p, t, lens)

for o in bpy.data.objects:
    if o.name.startswith("OP ") and " glass" in o.name:
        o.hide_render = True
        o.hide_viewport = True

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), compress=True)
print("R20_CAMERAS_PATCHED", flush=True)
