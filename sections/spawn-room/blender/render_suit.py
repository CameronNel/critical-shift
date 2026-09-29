#!/usr/bin/env python3
"""Outfit test: crew worker in the hazmat suit, turnaround + close-ups.  python render_suit.py -- <output_dir>"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    s, cam = studio((640, 900), 48)
    backdrop(s)
    root, tris = CW.build_worker()
    pieces, suit_tris = CS.build_hazmat(root)
    hidden = CS.equip(root)
    visible = sum(len(o.data.polygons) * 2 for o in root.children_recursive if o.type == "MESH" and not o.hide_render)
    print("SUIT hidden regions:", sorted(hidden))
    print("SUIT piece tris:", suit_tris, "| skin tris incl. head:", tris, "| drawn (est):", visible)
    shots = []
    for label, loc, tgt, lens in (("FRONT", (0, 4.0, 0.85), (0, 0, 0.82), 52), ("3/4", (2.8, 3.0, 0.95), (0, 0, 0.82), 52),
                                  ("SIDE", (4.0, 0, 0.85), (0, 0, 0.82), 52), ("BACK", (0, -4.0, 0.85), (0, 0, 0.82), 52)):
        p = os.path.join(out, "s_%s.png" % label.replace("/", ""))
        shoot(cam, loc, tgt, lens, p)
        shots.append(p)
    sheet = Image.new("RGB", (2560, 900), (16, 16, 10))
    for i, p in enumerate(shots):
        sheet.paste(Image.open(p).convert("RGB"), (i * 640, 0))
    sheet.save(os.path.join(out, "suit_turnaround.png"))
    shoot(cam, (1.6, 1.9, 1.25), (0, 0, 1.15), 75, os.path.join(out, "suit_upper.png"))
    shoot(cam, (-1.4, -2.0, 1.15), (0, -0.2, 0.98), 70, os.path.join(out, "suit_pack.png"))
    shoot(cam, (1.6, 1.3, 0.35), (0.10, 0.05, 0.30), 70, os.path.join(out, "suit_boots.png"))
    # colour variants: suit, gloves, boots, accent, pack and visor tint are all swappable
    variants = [dict(suit="#E3A22F"), dict(suit="#E0654A", gloves="#ECE9F0", boots="#2B3350", accent="#E3A22F", pack="#30323C"),
                dict(suit="#A99BC8", gloves="#E9B7A5", boots="#6B4028", accent="#ECE9F0", pack="#2B3350", visor=(0.9, 0.7, 0.85)),
                dict(suit="#8A9A5B", gloves="#E3A22F", boots="#30323C", accent="#E0654A", pack="#6079AD")]
    s, cam = studio((2400, 900), 40)
    backdrop(s)
    for i, col in enumerate(variants):
        r, _ = CW.build_worker("W%d" % i, origin=(-1.35 + i * 0.9, 0, 0), eyes=["round", "happy", "wide", "dot"][i],
                               mouth=["smile", "grin", "o", "smirk"][i])
        CS.build_hazmat(r, colors=col)
        CS.equip(r)
    shoot(cam, (0, 5.2, 0.85), (0, 0, 0.82), 42, os.path.join(out, "suit_variants.png"))
    print("SUIT done")


if __name__ == "__main__":
    main()
