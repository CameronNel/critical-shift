#!/usr/bin/env python3
"""Render the crew worker turnaround, a head close-up and a size comparison:  python render_worker.py -- <output_dir>"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_scout as SC  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402


def backdrop(s):
    s.world.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.10, 0.03, 1.0)
    s.world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    bpy.data.materials["fm"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.30, 0.22, 0.03, 1.0)
    for o in bpy.data.objects:
        if o.type == "LIGHT":
            o.data.energy *= 0.55
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
    s, cam = studio((640, 900), 48)
    backdrop(s)
    root, tris = CW.build_worker()
    print("WORKER tris", tris)
    files = []
    for label, loc in (("FRONT", (0, 4.0, 0.85)), ("3/4", (2.8, 3.0, 0.95)), ("SIDE", (4.0, 0, 0.85)), ("BACK", (0, -4.0, 0.85))):
        p = os.path.join(out, "w_%s.png" % label.replace("/", ""))
        shoot(cam, loc, (0, 0, 0.78), 52, p)
        files.append((label, p))
    sheet = Image.new("RGB", (2560, 940), (16, 16, 10))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(files):
        sheet.paste(Image.open(p).convert("RGB"), (i * 640, 40))
        d.text((i * 640 + 16, 8), label, font=font, fill=(255, 255, 255))
    d.text((2120, 8), "CREW WORKER  %d tris" % tris, font=font, fill=(226, 162, 47))
    sheet.save(os.path.join(out, "worker_turnaround.png"))
    shoot(cam, (0.9, 1.7, 1.42), (0, 0, 1.30), 80, os.path.join(out, "worker_head.png"))
    shoot(cam, (1.5, 1.4, 0.55), (0.30, 0.06, 0.42), 80, os.path.join(out, "worker_hand.png"))

    # size comparison: Scout (left) next to the worker (right), both in the same frame
    s, cam = studio((1400, 900), 40)
    backdrop(s)
    SC.build_scout("SCOUT", origin=(-0.6, 0, 0))
    CW.build_worker("WORKER", origin=(0.6, 0, 0))
    shoot(cam, (0, 5.4, 0.95), (0, 0, 0.92), 50, os.path.join(out, "worker_vs_scout.png"))
    print("WORKER done")


if __name__ == "__main__":
    main()
