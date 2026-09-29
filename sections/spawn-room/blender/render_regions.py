#!/usr/bin/env python3
"""Check the body regions: seams (each region a different colour), the normal skin look, and an outfit hiding regions.
    python render_regions.py -- <output_dir>"""
import colorsys
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_regions as CR  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402


def tint_regions(root):
    for i, r in enumerate(CR.REGIONS):
        o = next((c for c in root.children if c.get("cs_region") == r), None)
        if o is None:
            continue
        m = bpy.data.materials.new("DBG_" + r)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*colorsys.hsv_to_rgb(i / len(CR.REGIONS), 0.7, 0.9), 1)
        o.data.materials.clear()
        o.data.materials.append(m)


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    shots = []
    for label, mode in (("regions", "tint"), ("skin", "plain"), ("suit_hides", "hide")):
        s, cam = studio((640, 900), 48)
        backdrop(s)
        root, tris = CW.build_worker()
        if mode == "tint":
            tint_regions(root)
        if mode == "hide":
            CR.set_hidden(root, ["TORSO", "ARM_L", "ARM_R", "LEG_L", "LEG_R"])
        n = sum(1 for o in bpy.data.objects if o.get("cs_region"))
        print(label, "regions:", n, "tris:", tris)
        for view, loc in (("front", (0, 4.0, 0.85)), ("back", (0, -4.0, 0.85))):
            p = os.path.join(out, "r_%s_%s.png" % (label, view))
            shoot(cam, loc, (0, 0, 0.78), 52, p)
            shots.append(p)
    sheet = Image.new("RGB", (640 * len(shots), 900), (16, 16, 10))
    for i, p in enumerate(shots):
        sheet.paste(Image.open(p).convert("RGB"), (i * 640, 0))
    sheet.save(os.path.join(out, "regions_sheet.png"))
    print("REGIONS done")


if __name__ == "__main__":
    main()
