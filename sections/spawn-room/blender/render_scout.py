#!/usr/bin/env python3
"""Render the Scout turnaround headlessly:  python render_scout.py -- <output_dir>"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_scout as SC  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
    s, cam = studio((640, 900), 48)
    # concept-like backdrop: dark olive world, warm yellow floor
    bg = s.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.10, 0.10, 0.03, 1.0)
    bg.inputs[1].default_value = 0.9
    fl = bpy.data.materials["fm"].node_tree.nodes["Principled BSDF"]
    fl.inputs[0].default_value = (0.30, 0.22, 0.03, 1.0)
    for o in bpy.data.objects:
        if o.type == "LIGHT":
            o.data.energy *= 0.55
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"
    root, tris = SC.build_scout()
    print("SCOUT tris", tris)
    views = (("FRONT", (0, 4.3, 1.0)), ("3/4", (3.0, 3.2, 1.1)), ("SIDE", (4.3, 0, 1.0)), ("BACK", (0, -4.3, 1.0)))
    files = []
    for label, loc in views:
        p = os.path.join(out, "s_%s.png" % label.replace("/", ""))
        shoot(cam, loc, (0, 0, 0.98), 55, p)
        files.append((label, p))
    sheet = Image.new("RGB", (2560, 940), (16, 16, 10))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(files):
        sheet.paste(Image.open(p).convert("RGB"), (i * 640, 40))
        d.text((i * 640 + 16, 8), label, font=font, fill=(255, 255, 255))
    d.text((2150, 8), "SCOUT  %d tris" % tris, font=font, fill=(226, 162, 47))
    sheet.save(os.path.join(out, "scout_turnaround.png"))
    shoot(cam, (0.9, 1.9, 1.72), (0, 0, 1.65), 85, os.path.join(out, "scout_face.png"))
    shoot(cam, (1.05, 1.0, 0.60), (0.33, 0.07, 0.56), 85, os.path.join(out, "scout_hand.png"))
    shoot(cam, (0.75, 1.15, 0.30), (0.10, 0.06, 0.06), 90, os.path.join(out, "scout_feet.png"))
    print("SCOUT done")


if __name__ == "__main__":
    main()
