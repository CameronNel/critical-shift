#!/usr/bin/env python3
"""
Render the character concept sheets headlessly (Blender 5.2 bpy + Pillow).

    python render_character_sheet.py -- <output_dir>

Writes turnaround.png, crew.png, options.png (every choosable list, one row each) and
character_options.json (the locked/choosable split, for a future customisation UI).
Nothing here touches the game modules.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_kit as CK  # noqa: E402
import cozy_geo  # noqa: E402


def studio(res, samples=32):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cozy_geo._mats.clear()          # cached materials died with the previous scene
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = res
    w = bpy.data.worlds.new("w")
    s.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.20, 0.22, 0.32, 1.0)
    bg.inputs[1].default_value = 0.8
    s.view_settings.look = "AgX - Medium High Contrast"

    def area(loc, energy, size, col):
        d = bpy.data.lights.new("l", "AREA")
        d.energy, d.size, d.color = energy, size, col
        o = bpy.data.objects.new("l", d)
        o.location = loc
        o.rotation_euler = (Vector((0, 0, 0.8)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        s.collection.objects.link(o)

    area((2.2, 2.6, 3.0), 520, 2.5, (1.0, 0.86, 0.72))
    area((-2.6, 1.6, 1.6), 160, 2.5, (0.75, 0.85, 1.0))
    area((0.0, -2.8, 2.6), 300, 2.0, (1.0, 0.95, 0.9))
    import bmesh
    floor = bpy.data.objects.new("floor", bpy.data.meshes.new("f"))
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=14)
    bm.to_mesh(floor.data)
    bm.free()
    fm = bpy.data.materials.new("fm")
    fm.use_nodes = True
    fm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.055, 0.09, 1.0)
    fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    floor.data.materials.append(fm)
    s.collection.objects.link(floor)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    s.collection.objects.link(cam)
    s.camera = cam
    return s, cam


def shoot(cam, loc, target, lens, path):
    cam.location = loc
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


BASE = dict(skin="peach", outfit_colour="coral", eyes="dots", mouth="smile", hat="hardhat", hat_colour="mustard",
            torso_wear="vest", pack="filter", accessory="badge")
CREW = [
    dict(skin="deep", outfit_colour="olive", eyes="sleepy", mouth="flat", eyewear="shades", hat="hood", hat_colour="olive",
         torso_wear="toolbelt"),
    dict(skin="brown", outfit_colour="sky", eyes="wide", mouth="grin", eyewear="goggles", hat="cap", hat_colour="coral",
         torso_wear="bib", pack="tank", accessory="badge"),
    dict(skin="tan", outfit_colour="mustard", eyes="happy", mouth="tongue", eyewear="round", hat="beanie", hat_colour="navy",
         torso_wear="scarf", pack="satchel", accessory="radio"),
    dict(BASE),
]


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
    CK.write_options_json(os.path.join(out, "character_options.json"))

    # ---- turnaround
    s, cam = studio((640, 860), 40)
    root, tris = CK.build_character("BASE", BASE)
    print("SHEET base tris", tris)
    files = []
    for label, loc in (("FRONT", (0, 3.6, 0.85)), ("3/4", (2.5, 2.6, 0.95)), ("SIDE", (3.7, 0, 0.85)), ("BACK", (0, -3.6, 0.85))):
        p = os.path.join(out, "t_%s.png" % label.replace("/", ""))
        shoot(cam, loc, (0, 0, 0.72), 70, p)
        files.append((label, p))
    sheet = Image.new("RGB", (2560, 900), (16, 18, 28))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(files):
        sheet.paste(Image.open(p).convert("RGB"), (i * 640, 40))
        d.text((i * 640 + 16, 8), label, font=font, fill=(255, 255, 255))
    d.text((2200, 8), "BASE  %d tris" % tris, font=font, fill=(226, 162, 47))
    sheet.save(os.path.join(out, "turnaround.png"))

    # ---- crew
    s, cam = studio((1600, 760), 40)
    counts = []
    for i, cfg in enumerate(CREW):
        _, t = CK.build_character("P%d" % (i + 1), cfg, origin=(1.35 - i * 0.9, 0, 0), yaw=math.radians(8 - i * 5))
        counts.append(t)
    print("SHEET crew tris", counts)
    shoot(cam, (0, 4.6, 0.95), (0, 0, 0.68), 42, os.path.join(out, "crew.png"))

    # ---- option rows: the same head with ONE option varied per cell
    rows = []
    face = dict(skin="peach", eyes="dots", mouth="smile")

    def head_row(label, key, values, extra=None, name=None):
        s2, cam2 = studio((1600, 300), 24)
        n = len(values)
        for i, v in enumerate(values):
            cfg = dict(face)
            if extra:
                cfg.update(extra)
            cfg[key] = v
            if key == "hat_colour":
                cfg["hat"] = "cap"
            if key == "skin":
                cfg["skin"] = v
            CK.build_character("H%d" % i, cfg, origin=(((n - 1) / 2 - i) * 0.56, 0, -0.88), head_only=True)
        p = os.path.join(out, "row_%s.png" % (name or key))
        shoot(cam2, (0, 6.4, 0.55), (0, 0, 0.42), 42, p)
        rows.append((label, list(values), p, 300))

    head_row("EYES", "eyes", CK.OPTIONS["eyes"])
    head_row("MOUTH", "mouth", CK.OPTIONS["mouth"])
    head_row("EYEWEAR", "eyewear", CK.OPTIONS["eyewear"])
    head_row("HATS", "hat", CK.OPTIONS["hat"], extra=dict(hat_colour="mustard"))
    head_row("HAT COLOURS", "hat_colour", CK.OPTIONS["hat_colour"])
    head_row("SKIN", "skin", CK.OPTIONS["skin"])

    s2, cam2 = studio((1600, 560), 24)
    cols = CK.OPTIONS["outfit_colour"]
    for i, c in enumerate(cols):
        CK.build_character("C%d" % i, dict(outfit_colour=c, skin="peach", glove_colour=CK.OPTIONS["glove_colour"][i % 5]),
                           origin=(((len(cols) - 1) / 2 - i) * 0.72, 0, 0))
    p = os.path.join(out, "row_colours.png")
    shoot(cam2, (0, 7.4, 0.75), (0, 0, 0.62), 42, p)
    rows.append(("OUTFIT COLOURS (+ glove colour)", list(cols), p, 560))

    s2, cam2 = studio((1600, 560), 24)
    combos = [("vest", "filter", "badge"), ("bib", "satchel", "radio"), ("scarf", "tank", "none"), ("toolbelt", "none", "none"),
              ("none", "filter", "none"), ("none", "none", "badge")]
    for i, (w_, pk, ac) in enumerate(combos):
        CK.build_character("G%d" % i, dict(outfit_colour=CK.OPTIONS["outfit_colour"][i], torso_wear=w_, pack=pk, accessory=ac),
                           origin=(((len(combos) - 1) / 2 - i) * 0.8, 0, 0), yaw=math.radians(-22 if i % 2 == 0 else 22))
    p = os.path.join(out, "row_gear.png")
    shoot(cam2, (0, 7.0, 0.75), (0, 0, 0.62), 42, p)
    rows.append(("TORSO WEAR / PACK / ACCESSORY", [c[0] + "+" + c[1] + "+" + c[2] for c in combos], p, 560))

    total = sum(r[3] + 60 for r in rows)
    sheet = Image.new("RGB", (1600, total), (16, 18, 28))
    d = ImageDraw.Draw(sheet)
    y = 0
    for label, values, p, h in rows:
        d.text((16, y + 6), label, font=font, fill=(226, 162, 47))
        d.text((16, y + 34), "   ".join(values), font=small, fill=(200, 205, 220))
        sheet.paste(Image.open(p).convert("RGB"), (0, y + 60))
        y += h + 60
    sheet.save(os.path.join(out, "options.png"))
    print("SHEET done")


if __name__ == "__main__":
    main()
