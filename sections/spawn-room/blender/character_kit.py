#!/usr/bin/env python3
"""
Modular "bean crew worker" character kit (Blender 5.2 / bpy). Original design.

Style cues only (chunky rounded bodies, big heads, mitten hands, simple flat faces); nothing is
copied from any existing game. This deliberately overrides the grounded-adult character direction
in design/ART_DIRECTION.md section 13, by owner decision, for characters only.

Every swappable part is its own object under one root empty, so heads, faces, headgear, torso
wear, packs and accessories can be exchanged independently. Target: under 5k triangles per
assembled character. Local frame: origin at the feet, +y is the front, height about 1.42 m.
"""

import math

import bpy
from mathutils import Matrix, Vector

from cozy_geo import B, HEX, arc, mat, tri_count

# ------------------------------------------------------------------ palette / options
# LOCKED for every player: body shape, head shape, proportions, art style.
# CHOOSABLE per player: everything listed below (see OPTIONS, also written to character_options.json).
SKIN = {"peach": "#F0C9A8", "tan": "#C58C63", "brown": "#8D5A3B", "deep": "#5A3826",
        "mint": "#A8D8B9", "lilac": "#BFA8E0", "blue": "#9CC3F0"}
for k, v in SKIN.items():
    HEX["skin_" + k] = v
HEX.update({"visor_glass": "#1E2A44", "reflective": "#D7DCE6", "hivis": "#F26B3A", "cloth_cream": "#DDD6CC",
            "tongue": "#E7728A", "teeth": "#F4F1F6", "lens": "#BFD8F0"})

OPTIONS = {
    "skin": tuple(SKIN),
    "outfit_colour": ("coral", "mustard", "sky", "olive", "lilac", "rose", "brick", "navy"),
    "glove_colour": ("navy", "charcoal", "mustard", "coral", "cloth_cream"),
    "eyes": ("dots", "wide", "sleepy", "happy", "angry", "surprised"),
    "mouth": ("smile", "flat", "open", "grin", "frown", "tongue", "cat"),
    "eyewear": ("none", "round", "shades", "goggles", "visor", "monocle", "eyepatch"),
    "hat": ("none", "hardhat", "beanie", "cap", "hood", "earmuffs", "bucket", "headlamp"),
    "hat_colour": ("mustard", "navy", "coral", "olive", "sky", "rose", "lilac", "charcoal"),
    "torso_wear": ("none", "vest", "bib", "scarf", "toolbelt"),
    "pack": ("none", "filter", "satchel", "tank"),
    "accessory": ("none", "badge", "radio"),
}
LOCKED = ("body_shape", "head_shape", "proportions", "art_style")

# the single locked head: (rx, ry, rz, centre z)
RX, RY, RZ, CZ = 0.215, 0.205, 0.205, 1.20


def _front_y(dx, dz):
    """Front surface depth of the locked head at horizontal offset dx and height offset dz from its centre."""
    v = 1.0 - (dx / RX) ** 2 - (dz / RZ) ** 2
    return RY * math.sqrt(max(v, 0.05))


# --------------------------------------------------------------------------- body parts
def part_body(cover="coral", glove_colour="navy"):
    """Legs, boots, torso, arms, mitten hands, neck. ~2.3k triangles."""
    b = B()
    suit = mat(cover, 0.85)
    dark = mat("charcoal", 0.7)
    glove = mat(glove_colour, 0.8)
    torso = [(0, 0.40), (0.15, 0.40), (0.215, 0.47), (0.245, 0.62), (0.235, 0.78), (0.19, 0.92),
             (0.11, 0.99), (0.07, 1.02), (0, 1.03)]
    b.lathe(torso, (0, 0, 0), suit, seg=20, scale=(1.0, 0.82, 1.0))
    for s in (-1, 1):
        b.tube([(s * 0.10, 0.0, 0.46), (s * 0.10, 0.0, 0.26), (s * 0.10, 0.0, 0.10)], 0.07, suit, seg=10)
        b.lathe([(0, 0), (0.075, 0), (0.088, 0.02), (0.088, 0.07), (0.072, 0.115), (0.03, 0.135), (0, 0.14)],
                (s * 0.10, 0.03, 0.0), dark, seg=12, scale=(1.0, 1.55, 1.0))                         # boot
        b.lathe([(0.09, 0.03), (0.092, 0.06)], (s * 0.10, 0.0, 0.10), mat("cloth_cream", 0.9), seg=12)   # sock cuff
        # arm: shoulder sphere, sleeve tube, mitten (fist sphere + thumb)
        b.sph(0.062, (s * 0.245, 0.0, 0.86), suit, seg=10, ring=7)
        b.tube([(s * 0.25, 0.0, 0.85), (s * 0.30, 0.02, 0.68), (s * 0.31, 0.05, 0.56)], lambda t: 0.055 - 0.008 * t,
               suit, seg=10)
        b.sph(0.072, (s * 0.31, 0.06, 0.50), glove, scale=(1.0, 1.0, 0.95), seg=12, ring=8)
        b.sph(0.03, (s * (0.31 - 0.055), 0.09, 0.51), glove, seg=8, ring=6)
    b.cyl(0.075, 0.07, (0, 0, 0.98), mat("skin_peach", 0.8), seg=12)
    return b


def part_head(skin="peach"):
    """The single locked head."""
    b = B()
    m = mat("skin_" + skin, 0.75)
    b.sph(1.0, (0, 0, CZ), m, scale=(RX, RY, RZ), seg=22, ring=14)
    for s in (-1, 1):
        b.sph(0.045, (s * (RX - 0.005), 0.0, CZ - 0.01), m, scale=(0.55, 1.0, 1.15), seg=10, ring=7)
    return b


EYE_X, EYE_Z = 0.075, CZ + 0.015


def part_eyes(kind="dots"):
    b = B()
    ink = mat("ink", 0.35)
    white = mat("white", 0.3)
    for s in (-1, 1):
        x = s * EYE_X
        y = _front_y(x, EYE_Z - CZ) - 0.006
        if kind == "dots":
            b.sph(0.034, (x, y, EYE_Z), ink, scale=(1.0, 0.45, 1.3), seg=10, ring=7)
        elif kind == "wide":
            b.sph(0.05, (x, y, EYE_Z), white, scale=(1.0, 0.4, 1.15), seg=12, ring=8)
            b.sph(0.024, (x - s * 0.004, y + 0.012, EYE_Z - 0.004), ink, scale=(1.0, 0.4, 1.0), seg=8, ring=6)
        elif kind == "surprised":
            b.sph(0.058, (x, y, EYE_Z + 0.005), white, scale=(1.0, 0.4, 1.1), seg=12, ring=8)
            b.sph(0.016, (x, y + 0.014, EYE_Z + 0.005), ink, scale=(1.0, 0.4, 1.0), seg=8, ring=6)
            b.tube([(x - 0.035, y - 0.004, EYE_Z + 0.085), (x, y + 0.004, EYE_Z + 0.097), (x + 0.035, y - 0.004, EYE_Z + 0.085)],
                   0.006, ink, seg=4)
        elif kind == "sleepy":
            b.sph(0.045, (x, y, EYE_Z), white, scale=(1.0, 0.4, 1.0), seg=12, ring=8)
            b.sph(0.022, (x, y + 0.012, EYE_Z - 0.01), ink, scale=(1.0, 0.4, 1.0), seg=8, ring=6)
            b.sph(0.05, (x, y + 0.004, EYE_Z + 0.022), mat("skin_tan", 0.8), scale=(1.0, 0.45, 0.5), seg=10, ring=6)
        elif kind == "happy":
            b.tube(arc(x, y, EYE_Z - 0.012, 0.032, 20, 160, 8, plane="XZ"), 0.0075, ink, seg=5)
        elif kind == "angry":
            b.sph(0.03, (x, y, EYE_Z - 0.006), ink, scale=(1.0, 0.45, 1.2), seg=10, ring=7)
            b.tube([(x + s * 0.04, y - 0.002, EYE_Z + 0.085), (x - s * 0.035, y - 0.002, EYE_Z + 0.045)], 0.008, ink, seg=4)   # outer end high, inner end low
    return b


def part_mouth(kind="smile"):
    b = B()
    ink = mat("ink", 0.35)
    z = CZ - 0.085
    y = _front_y(0.0, z - CZ) - 0.004
    if kind == "smile":
        b.tube([(-0.035, y, z + 0.008), (0.0, y + 0.006, z - 0.012), (0.035, y, z + 0.008)], 0.006, ink, seg=5)
    elif kind == "flat":
        b.tube([(-0.03, y, z), (0.03, y, z)], 0.006, ink, seg=5)
    elif kind == "frown":
        b.tube([(-0.035, y, z - 0.008), (0.0, y + 0.006, z + 0.012), (0.035, y, z - 0.008)], 0.006, ink, seg=5)
    elif kind == "open":
        b.sph(0.03, (0, y - 0.004, z - 0.005), ink, scale=(1.0, 0.35, 1.05), seg=10, ring=7)
        b.sph(0.016, (0, y + 0.002, z - 0.022), mat("tongue", 0.5), scale=(1.0, 0.3, 0.6), seg=8, ring=5)
    elif kind == "grin":
        b.tube(arc(0, y, z + 0.03, 0.05, 215, 325, 9, plane="XZ"), 0.007, ink, seg=5)
        b.box((0.075, 0.006, 0.014), (0, y + 0.002, z - 0.012), mat("teeth", 0.3), bevel=0, seg=1)
    elif kind == "tongue":
        b.tube([(-0.035, y, z + 0.008), (0.0, y + 0.006, z - 0.012), (0.035, y, z + 0.008)], 0.006, ink, seg=5)
        b.sph(0.016, (0.012, y + 0.002, z - 0.024), mat("tongue", 0.5), scale=(1.0, 0.35, 1.25), seg=8, ring=5)
    elif kind == "cat":
        b.tube([(-0.05, y, z + 0.006), (-0.025, y + 0.004, z - 0.01), (0.0, y + 0.004, z + 0.004),
                (0.025, y + 0.004, z - 0.01), (0.05, y, z + 0.006)], 0.005, ink, seg=5)
    return b


def part_eyewear(kind="round"):
    b = B()
    if kind == "none":
        return b
    rim = mat("charcoal", 0.4, 0.4)
    for s in (-1, 1):
        x = s * EYE_X
        y = _front_y(x, EYE_Z - CZ) + 0.018
        if kind == "round":
            b.tube(arc(x, y, EYE_Z, 0.052, 0, 360, 17, plane="XZ"), 0.007, rim, seg=5, caps=False)
            b.lathe([(0.0, 0), (0.05, 0)], (x, y, EYE_Z), mat("lens", 0.05, 0.0), seg=14, rot=Matrix.Rotation(-math.pi / 2, 3, "X"))
        elif kind == "shades":
            b.box((0.09, 0.012, 0.065), (x, y + 0.004, EYE_Z), mat("ink", 0.12, 0.3), bevel=0.012, seg=2)
        elif kind == "goggles":
            b.cyl(0.06, 0.035, (x, y - 0.006, EYE_Z), mat("hazard", 0.5), seg=14, axis="Y")
            b.lathe([(0.0, 0), (0.05, 0)], (x, y + 0.03, EYE_Z), mat("lens", 0.05), seg=14, rot=Matrix.Rotation(-math.pi / 2, 3, "X"))
        elif kind == "monocle" and s == 1:
            b.tube(arc(x, y, EYE_Z, 0.055, 0, 360, 17, plane="XZ"), 0.007, mat("brass", 0.3, 0.9), seg=5, caps=False)
            b.tube([(x + 0.03, y, EYE_Z - 0.055), (x + 0.05, y - 0.02, EYE_Z - 0.16), (x + 0.02, y - 0.05, EYE_Z - 0.3)],
                   0.0025, mat("brass", 0.3, 0.9), seg=4)
        elif kind == "eyepatch" and s == -1:
            b.sph(0.05, (x, y - 0.008, EYE_Z), mat("ink", 0.7), scale=(1.0, 0.35, 0.85), seg=10, ring=7)
    if kind in ("round", "shades"):
        z = EYE_Z
        yb = _front_y(0.0, z - CZ) + 0.02
        b.tube([(-EYE_X + 0.05, yb, z), (EYE_X - 0.05, yb, z)], 0.006, rim, seg=4)
    if kind in ("round", "shades", "goggles", "eyepatch"):
        b.tube([((RX + 0.012) * math.cos(a_), (RY + 0.012) * math.sin(a_), EYE_Z)
                for a_ in [math.radians(a) for a in range(0, 361, 20)]], 0.007 if kind != "goggles" else 0.02,
               mat("charcoal", 0.6) if kind != "goggles" else mat("navy", 0.8), seg=5, caps=False)
    if kind == "visor":
        b.tube(arc(0, 0, EYE_Z, RY + 0.012, 35, 145, 16, plane="XY"), 0.05, mat("visor_glass", 0.12, 0.2), seg=8)
        b.sph(0.02, (-0.09, RY * 0.97, EYE_Z + 0.03), mat("reflective", 0.2, emit=1.5), scale=(1.4, 0.4, 0.5), seg=8, ring=5)
    return b


def part_headgear(kind="hardhat", colour="mustard"):
    b = B()
    top = CZ + RZ
    c = mat(colour, 0.4)
    if kind == "hardhat":
        b.lathe([(0.29, 0), (0.295, 0.012), (0.27, 0.02), (0.255, 0.06), (0.23, 0.11), (0.17, 0.15), (0.08, 0.17), (0, 0.175)],
                (0, 0, top - 0.075), c, seg=22)
        b.prism([(-0.13, 0.2), (0.13, 0.2), (0.16, 0.31), (-0.16, 0.31)], 0.012, c, z0=top - 0.075)
        for x in (-0.05, 0.0, 0.05):
            b.tube([(x, 0.22 * math.cos(math.radians(a)), top - 0.075 + 0.175 * math.sin(math.radians(a)) + 0.004)
                    for a in range(15, 166, 15)], 0.009, c, seg=5)
        b.cyl(0.03, 0.03, (0, 0.235, top - 0.005), mat("reflective", 0.2, emit=4.0), seg=10, axis="Y")
    elif kind == "beanie":
        b.lathe([(0.235, 0), (0.24, 0.05), (0.225, 0.1), (0.17, 0.15), (0.07, 0.19), (0, 0.2)], (0, 0, top - 0.11), c, seg=20)
        b.tube([(0.236 * math.cos(a), 0.236 * math.sin(a) * RY / RX, top - 0.11 + 0.02)
                for a in [i * 2 * math.pi / 22 for i in range(23)]], 0.03, mat("navy", 0.9), seg=6, caps=False)
        b.sph(0.05, (0, 0, top + 0.09), mat("cloth_cream", 0.95), seg=10, ring=7)
    elif kind == "cap":
        b.lathe([(0.225, 0), (0.228, 0.05), (0.2, 0.11), (0.12, 0.15), (0, 0.165)], (0, 0, top - 0.09), c, seg=20)
        b.prism([(-0.13, 0.17), (0.13, 0.17), (0.11, 0.3), (-0.11, 0.3)], 0.014, mat("navy", 0.6), z0=top - 0.09)
    elif kind == "bucket":
        b.lathe([(0.34, -0.005), (0.345, 0.0), (0.27, 0.03), (0.225, 0.045), (0.215, 0.13), (0.17, 0.16), (0, 0.165)],
                (0, 0, top - 0.10), c, seg=22)
    elif kind == "headlamp":
        b.tube([((RX + 0.012) * math.cos(a_), (RY + 0.012) * math.sin(a_), CZ + 0.105)
                for a_ in [math.radians(a) for a in range(0, 361, 20)]], 0.012, mat("charcoal", 0.6), seg=5, caps=False)
        b.cyl(0.04, 0.05, (0, RY + 0.012, CZ + 0.105), mat("charcoal", 0.5), seg=12, axis="Y")
        b.cyl(0.03, 0.006, (0, RY + 0.062, CZ + 0.105), mat("hazard", 0.3, emit=9.0), seg=12, axis="Y")
    elif kind == "hood":
        # open-front shell over the back and top of the head, so the face stays visible
        b.lathe([(0.0, -1.0), (0.55, -0.93), (0.95, -0.6), (1.06, -0.05), (1.02, 0.35), (0.9, 0.55)],
                (0, -0.05, CZ), c, seg=20, rot=Matrix.Rotation(-math.pi / 2, 3, "X"),
                scale=(RX + 0.06, RZ + 0.06, RY + 0.08))
    elif kind == "earmuffs":
        b.tube(arc(0, 0, CZ + 0.02, RX + 0.02, 0, 180, 14, plane="XZ"), 0.014, mat("charcoal", 0.5), seg=6)
        for s in (-1, 1):
            b.lathe([(0, 0), (0.06, 0), (0.065, 0.012), (0.06, 0.05), (0.04, 0.07), (0, 0.075)],
                    (s * (RX + 0.03), 0.0, CZ + 0.02), c, seg=12, rot=Matrix.Rotation(s * math.pi / 2, 3, "Y"))
    return b


def part_torsowear(kind="vest", cover="coral"):
    b = B()
    if kind == "vest":
        vest = mat("hivis", 0.6)
        b.lathe([(0.226, 0.60), (0.25, 0.65), (0.242, 0.78), (0.2, 0.90), (0.15, 0.94)], (0, 0, 0), vest, seg=20,
                scale=(1.0, 0.85, 1.0))
        for z, rr in ((0.68, 0.2455), (0.82, 0.238)):
            b.tube([(rr * math.cos(a_), 0.85 * rr * math.sin(a_), z) for a_ in [i * 2 * math.pi / 22 for i in range(23)]],
                   0.012, mat("reflective", 0.3, 0.6), seg=5, caps=False)
    elif kind == "bib":
        deniM = mat("denim", 0.85)
        b.lathe([(0.226, 0.42), (0.246, 0.55), (0.246, 0.74)], (0, 0, 0), deniM, seg=20, scale=(1.0, 0.84, 1.0))
        for s in (-1, 1):
            b.tube([(s * 0.14, 0.2, 0.74), (s * 0.13, 0.12, 0.98), (s * 0.17, -0.1, 0.96)], 0.018, deniM, seg=6)
        b.box((0.12, 0.02, 0.09), (0, 0.205, 0.66), deniM, bevel=0.006, seg=1)
    elif kind == "scarf":
        sc = mat("mustard", 0.95)
        b.tube([(0.1 * math.cos(a), 0.1 * math.sin(a), 0.99) for a in [i * 2 * math.pi / 14 for i in range(15)]], 0.045, sc,
               seg=8, caps=False)
        b.box((0.06, 0.02, 0.26), (0.06, 0.11, 0.85), sc, bevel=0.006, seg=1)
    elif kind == "toolbelt":
        leather = mat("walnut", 0.7)
        b.tube([(0.235 * math.cos(a), 0.2 * math.sin(a), 0.56) for a in [i * 2 * math.pi / 22 for i in range(23)]], 0.022, leather,
               seg=6, caps=False)
        for s, w in ((-1, 0.07), (1, 0.09)):
            b.box((w, 0.05, 0.1), (s * 0.15, 0.17, 0.53), leather, bevel=0.008, seg=1)
        b.box((0.03, 0.03, 0.03), (0, 0.205, 0.56), mat("brass", 0.3, 0.9), bevel=0.004, seg=1)
    return b


def part_pack(kind="filter"):
    b = B()
    if kind == "filter":
        b.box((0.32, 0.15, 0.4), (0, -0.2, 0.72), mat("charcoal", 0.6), bevel=0.02, seg=2)
        for s in (-1, 1):
            b.lathe([(0, 0), (0.06, 0), (0.065, 0.01), (0.065, 0.14), (0.05, 0.16), (0, 0.165)], (s * 0.08, -0.29, 0.62),
                    mat("hazard", 0.5), seg=12, rot=Matrix.Rotation(-math.pi / 2, 3, "X"))
        b.box((0.2, 0.01, 0.06), (0, -0.28, 0.86), mat("coral", 0.5), bevel=0.003, seg=1)
    elif kind == "satchel":
        b.box((0.34, 0.12, 0.26), (0, -0.2, 0.66), mat("brick", 0.85), bevel=0.03, seg=2)
        b.box((0.34, 0.125, 0.09), (0, -0.2, 0.75), mat("walnut", 0.8), bevel=0.02, seg=2)
        b.tube([(0.2, -0.12, 0.92), (0.05, 0.22, 0.85), (-0.12, 0.2, 0.6), (-0.2, -0.14, 0.58)], 0.016, mat("walnut", 0.8), seg=6)
    elif kind == "tank":
        for s in (-1, 1):
            b.lathe([(0, 0), (0.07, 0), (0.08, 0.02), (0.08, 0.34), (0.06, 0.4), (0.025, 0.43), (0, 0.44)],
                    (s * 0.085, -0.22, 0.42), mat("sky", 0.4, 0.3), seg=12)
        b.box((0.24, 0.02, 0.04), (0, -0.22, 0.6), mat("charcoal", 0.5), bevel=0.004, seg=1)
        b.box((0.24, 0.02, 0.04), (0, -0.22, 0.78), mat("charcoal", 0.5), bevel=0.004, seg=1)
    return b


def part_accessory(kind="badge"):
    b = B()
    if kind == "badge":
        b.box((0.07, 0.012, 0.09), (0.11, 0.2, 0.8), mat("white", 0.5), bevel=0.004, seg=1)
        b.box((0.05, 0.014, 0.018), (0.11, 0.203, 0.83), mat("coral", 0.5), bevel=0, seg=1)
    elif kind == "radio":
        b.box((0.07, 0.05, 0.11), (-0.2, 0.09, 0.93), mat("charcoal", 0.5), bevel=0.01, seg=2)
        b.tube([(-0.2, 0.09, 0.985), (-0.19, 0.09, 1.12)], 0.006, mat("steel", 0.3, 1.0), seg=5)
        b.sph(0.012, (-0.2, 0.118, 0.95), mat("coral", 0.4, emit=3.0), seg=6, ring=4)
    return b


# ------------------------------------------------------------------------- assembly
def _link(obj, coll, parent=None):
    coll.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


DEFAULTS = dict(skin="peach", outfit_colour="coral", glove_colour="navy", eyes="dots", mouth="smile", eyewear="none",
                hat="none", hat_colour="mustard", torso_wear="none", pack="none", accessory="none")


def _cfg(cfg):
    out = dict(DEFAULTS)
    out.update(cfg or {})
    for key, val in out.items():
        assert val in OPTIONS[key], "unknown %s option %r" % (key, val)
    return out


def head_parts(cfg):
    """(label, builder) pairs for the head-only options."""
    cfg = _cfg(cfg)
    parts = [("HEAD", part_head(cfg["skin"])), ("EYES", part_eyes(cfg["eyes"])), ("MOUTH", part_mouth(cfg["mouth"]))]
    if cfg["eyewear"] != "none":
        parts.append(("EYEWEAR", part_eyewear(cfg["eyewear"])))
    if cfg["hat"] != "none":
        parts.append(("HAT", part_headgear(cfg["hat"], cfg["hat_colour"])))
    return parts


def body_parts(cfg):
    cfg = _cfg(cfg)
    parts = [("BODY", part_body(cfg["outfit_colour"], cfg["glove_colour"]))]
    if cfg["torso_wear"] != "none":
        parts.append(("TORSOWEAR", part_torsowear(cfg["torso_wear"], cfg["outfit_colour"])))
    if cfg["pack"] != "none":
        parts.append(("PACK", part_pack(cfg["pack"])))
    if cfg["accessory"] != "none":
        parts.append(("ACCESSORY", part_accessory(cfg["accessory"])))
    return parts


def build_character(name, cfg, origin=(0.0, 0.0, 0.0), yaw=0.0, collection=None, head_only=False):
    """Build one player. Each swappable part is its own object under one root empty."""
    cfg = _cfg(cfg)
    coll = collection or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.15
    coll.objects.link(root)
    root.location = origin
    root.rotation_euler = (0, 0, yaw)
    parts = head_parts(cfg) + ([] if head_only else body_parts(cfg))
    tris = 0
    for label, builder in parts:
        obj = builder.build("%s_%s" % (name, label), floor_normalize=False)
        _link(obj, coll, root)
        tris += tri_count(obj)
    for sock, loc in (("SOCKET_head", (0, 0, 1.2)), ("SOCKET_hat", (0, 0, 1.41)), ("SOCKET_back", (0, -0.15, 0.72)),
                      ("SOCKET_hand_L", (-0.31, 0.06, 0.5)), ("SOCKET_hand_R", (0.31, 0.06, 0.5))):
        e = bpy.data.objects.new("%s_%s" % (name, sock), None)
        e.empty_display_size = 0.04
        e.location = loc
        _link(e, coll, root)
    root["character_config"] = str(cfg)
    return root, tris


def write_options_json(path):
    import json
    with open(path, "w") as fh:
        json.dump({"locked": list(LOCKED), "choosable": {k: list(v) for k, v in OPTIONS.items()}}, fh, indent=2)
