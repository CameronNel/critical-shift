"""Render the fixed validation cameras of a spawn-room module at low cost, for before/after comparison.
    python render_cams.py -- <module.blend> <out_dir> [cam,cam,...]
env: SAMPLES=48  RES=960x540
"""
import os
import sys

import bpy

CAMS = ["VALIDATE_Spawn", "VALIDATE_LockerDoor", "VALIDATE_BriefingDoor", "VALIDATE_ExitReverse", "VALIDATE_Hero_A",
        "VALIDATE_Material_A"]


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    src, out = a[0], a[1]
    cams = a[2].split(",") if len(a) > 2 else CAMS
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=src)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = int(os.environ.get("SAMPLES", "48"))
    sc.cycles.use_denoising = True
    sc.cycles.seed = 7
    w, h = [int(x) for x in os.environ.get("RES", "960x540").split("x")]
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.image_settings.file_format = "PNG"
    for name in cams:
        cam = bpy.data.objects.get(name)
        if cam is None:
            print("CAM missing", name)
            continue
        sc.camera = cam
        sc.render.filepath = os.path.join(out, name + ".png")
        bpy.ops.render.render(write_still=True)
        print("CAM done", name)


if __name__ == "__main__":
    main()
