#!/usr/bin/env python3
"""Rig check: crew worker (bare or in the hazmat suit) posed through the run cycle.
    python render_rig.py -- <output_dir>     env: SUIT=1 to wear the suit, FRAMES=0,3,6,... to pick frames"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_rig as RIG  # noqa: E402
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image, ImageDraw
    s, cam = studio((480, 640), 48)
    backdrop(s)
    root, tris = CW.build_worker()
    if os.environ.get("SUIT") == "1":
        CS.build_hazmat(root)
        CS.equip(root)
    arm = RIG.build_rig(root)
    n, missing = RIG.skin_worker(root, arm)
    print("RIG skinned meshes:", n, "verts without heat weights (fallback):", missing)
    act = RIG.make_run_cycle(arm, frames=24)
    print("RIG action", act.name, "frame range", act.frame_range[:])
    frames = [int(x) for x in os.environ.get("FRAMES", "0,3,6,9,12,15,18,21").split(",")]
    tag = "suit" if os.environ.get("SUIT") == "1" else "bare"
    for view, loc, tgt, lens in (("side", (4.2, 0.0, 0.85), (0, 0, 0.82), 52), ("front", (0.0, 4.2, 0.85), (0, 0, 0.82), 52),
                                 ("shoulder", (2.0, 1.6, 1.2), (0.1, 0.0, 0.95), 70)):
        files = []
        for f in frames:
            s.frame_set(f)
            p = os.path.join(out, "rig_%s_%s_%02d.png" % (tag, view, f))
            shoot(cam, loc, tgt, lens, p)
            files.append(p)
        sheet = Image.new("RGB", (480 * len(files), 640), (16, 16, 10))
        for i, p in enumerate(files):
            sheet.paste(Image.open(p).convert("RGB"), (i * 480, 0))
        sheet.save(os.path.join(out, "run_%s_%s.png" % (tag, view)))
    if os.environ.get("EXPORT"):
        path = RIG.export_fbx(root, arm, os.environ["EXPORT"])
        print("RIG fbx", path, os.path.getsize(path) // 1024, "KB")
    if os.environ.get("GIF") == "1":
        tagged = []
        for view, loc in (("side", (4.2, 0.0, 0.85)), ("front", (0.0, 4.2, 0.85))):
            ims = []
            for f in range(24):
                s.frame_set(f)
                p = os.path.join(out, "gif_%s_%s_%02d.png" % (tag, view, f))
                shoot(cam, loc, (0, 0, 0.82), 52, p)
                ims.append(Image.open(p).convert("P", palette=Image.ADAPTIVE))
            ims[0].save(os.path.join(out, "run_%s_%s.gif" % (tag, view)), save_all=True, append_images=ims[1:], duration=42, loop=0)
    print("RIG done")


if __name__ == "__main__":
    main()
