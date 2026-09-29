#!/usr/bin/env python3
"""
Prop recipes for the spawn-room cozy pass. Each returns a cozy_geo.B builder.

Floor/surface props sit on z = 0. Wall props have their back on z = 0, front toward
+z, and +y up. Ceiling props hang toward -z from z = 0.

Triangle budget: small props stay in the low hundreds, large ones under ~1.5k.
"""

import math
import random

from mathutils import Matrix, Vector

from cozy_geo import B, arc, mat

random.seed(11)

def folded_cloth(b, w, d, layers, c, thick=0.011, z0=0.0, R=0.012):
    """Neatly folded cloth: zig-zag ribbon with real fold loops at the ends."""
    prof = []
    for i in range(layers):
        z = z0 + thick / 2 + i * 2 * R
        forward = (i % 2 == 0)
        y_from, y_to = (-d / 2 + R, d / 2 - R) if forward else (d / 2 - R, -d / 2 + R)
        prof.append((y_from, z))
        prof.append((y_to, z))
        if i < layers - 1:
            cy, cz = y_to, z + R
            for k in range(1, 6):
                a = math.radians(-90 + 180 * k / 6) if forward else math.radians(-90 - 180 * k / 6)
                prof.append((cy + R * math.cos(a), cz + R * math.sin(a)))
    b.ribbon(prof, -w / 2, w / 2, thick, mat(c, 0.95))
    return z0 + thick + (layers - 1) * 2 * R


# =========================================================== surface props
def r_mug(c="mustard"):
    b = B()
    b.lathe([(0, 0), (0.030, 0), (0.037, 0.006), (0.039, 0.084), (0.037, 0.090),
             (0.034, 0.089), (0.034, 0.014), (0, 0.014)], (0, 0, 0), mat(c, 0.4), seg=16)
    b.lathe([(0, 0.068), (0.0335, 0.068)], (0, 0, 0), mat("coffee", 0.2), seg=16)
    b.tube(arc(0.038, 0, 0.05, 0.025, 90, -90, 9), 0.0055, mat(c, 0.4), seg=6)
    return b


def r_kettle():
    b = B()
    body = mat("charcoal", 0.35, 0.3)
    b.lathe([(0, 0), (0.06, 0), (0.078, 0.008), (0.087, 0.03), (0.09, 0.065), (0.085, 0.1), (0.07, 0.128),
             (0.05, 0.145), (0.035, 0.152), (0, 0.155)], (0, 0, 0), body, seg=24)
    b.sph(0.014, (0, 0, 0.16), mat("coral", 0.5), seg=10, ring=6)
    b.tube([(-0.075, 0, 0.05), (-0.105, 0, 0.09), (-0.13, 0, 0.138)], lambda t: 0.017 - 0.009 * t, body, seg=8)
    b.tube(arc(0.085, 0, 0.09, 0.06, 112, -112, 11), 0.0085, mat("coral", 0.5), seg=6)
    return b


def r_books(colors=("navy", "mustard", "coral", "denim")):
    b = B()
    z = 0.0
    for i, c in enumerate(colors):
        h = random.uniform(0.026, 0.038)
        w, d = 0.2 - i * 0.008, 0.14
        yaw = Matrix.Rotation(random.uniform(-0.12, 0.12), 3, "Z")
        off = random.uniform(-0.008, 0.008)
        cover = mat(c, 0.7)
        b.box((w, d, 0.003), (off, 0, z + 0.0015), cover, bevel=0, rot=yaw)
        b.box((w, d, 0.003), (off, 0, z + h - 0.0015), cover, bevel=0, rot=yaw)
        b.box((0.004, d, h), (off - w / 2 + 0.002, 0, z + h / 2), cover, bevel=0, rot=yaw)
        b.box((w - 0.006, d - 0.004, h - 0.006), (off + 0.001, 0, z + h / 2), mat("cream_paper", 0.9),
              bevel=0, rot=yaw)
        z += h
    return b


def r_tin(c="rose"):
    b = B()
    b.lathe([(0, 0), (0.05, 0), (0.055, 0.005), (0.055, 0.052), (0, 0.052)], (0, 0, 0), mat(c, 0.35, 0.4), seg=18)
    b.lathe([(0, 0.052), (0.058, 0.052), (0.059, 0.058), (0.055, 0.064), (0, 0.066)], (0, 0, 0),
            mat("white", 0.35, 0.4), seg=18)
    b.lathe([(0.0552, 0.026), (0.0552, 0.032)], (0, 0, 0), mat("mustard", 0.4, 0.3), seg=18)
    return b


def r_lamp():
    b = B()
    b.lathe([(0, 0), (0.055, 0), (0.058, 0.008), (0.04, 0.018), (0.012, 0.022), (0, 0.022)], (0, 0, 0),
            mat("charcoal", 0.4, 0.4), seg=18)
    b.cyl(0.006, 0.19, (0, 0, 0.022), mat("brass", 0.3, 0.9), seg=8)
    b.lathe([(0, 0.295), (0.035, 0.293), (0.088, 0.212), (0.084, 0.207), (0, 0.215)], (0, 0, 0),
            mat("blush", 0.5, emit=3.0), seg=20)
    return b


def r_cushion(c="mustard"):
    b = B()
    b.pillow(0.42, 0.42, 0.13, (0, 0, 0), mat(c, 0.9), n=8)
    return b


def r_pouf(c="denim"):
    b = B()
    b.lathe([(0, 0), (0.20, 0), (0.245, 0.02), (0.256, 0.08), (0.252, 0.26), (0.236, 0.31),
             (0.18, 0.338), (0.06, 0.348), (0, 0.343)], (0, 0, 0), mat(c, 0.9), seg=24)
    b.tube([(0.2555 * math.cos(2 * math.pi * k / 20), 0.2555 * math.sin(2 * math.pi * k / 20), 0.075)
            for k in range(21)], 0.006, mat("navy", 0.8), seg=5, caps=False)
    return b


def r_blanket():
    b = B()
    top = folded_cloth(b, 0.56, 0.40, 3, "mustard", thick=0.014, R=0.016)
    for x in (0.16, 0.19):
        b.box((0.014, 0.36, 0.004), (x, 0, top + 0.002 - 0.0), mat("navy", 0.9), bevel=0, seg=1)
    return b


def r_clipboard():
    b = B()
    b.box((0.23, 0.32, 0.012), (0, 0, 0.006), mat("walnut", 0.6), bevel=0.003)
    b.box((0.205, 0.285, 0.002), (0, -0.005, 0.013), mat("paper", 0.9), bevel=0)
    b.box((0.06, 0.03, 0.012), (0, 0.14, 0.017), mat("brass", 0.3, 0.9), bevel=0.002)
    return b


def r_towels():
    b = B()
    z = 0.0
    for c, stripe in (("blush", "coral"), ("sky", "denim"), ("white", "steel")):
        top = folded_cloth(b, random.uniform(0.33, 0.35), 0.24, 2, c, thick=0.010, z0=z, R=0.011)
        b.box((0.012, 0.22, 0.003), (0.10, 0, top + 0.0015), mat(stripe, 0.9), bevel=0, seg=1)
        z = top + 0.004
    return b


def r_bottle(c="sky"):
    b = B()
    b.lathe([(0, 0), (0.028, 0), (0.033, 0.008), (0.034, 0.14), (0.03, 0.165), (0.017, 0.182),
             (0.015, 0.19), (0, 0.19)], (0, 0, 0), mat(c, 0.3, 0.6), seg=14)
    b.cyl(0.0175, 0.022, (0, 0, 0.19), mat("charcoal", 0.5), seg=10)
    return b


def r_headphones():
    """Upright on a surface: cups standing, band arching over."""
    b = B()
    dark = mat("charcoal", 0.5)
    b.tube(arc(0, 0, 0.046, 0.088, 0, 180, 15), 0.007, dark, seg=6)
    for s in (-1, 1):
        b.lathe([(0, 0), (0.038, 0), (0.044, 0.006), (0.044, 0.022), (0.036, 0.03), (0, 0.032)],
                (0.088 * s, 0, 0.046), mat("coral", 0.5), seg=14, rot=Matrix.Rotation(s * math.pi / 2, 3, "Y"))
    return b


def r_hardhat(c="mustard"):
    b = B()
    m = mat(c, 0.35)
    b.lathe([(0.112, 0), (0.115, 0.006), (0.105, 0.012), (0.1, 0.03), (0.09, 0.058), (0.068, 0.08),
             (0.035, 0.09), (0, 0.093)], (0, 0, 0), m, seg=22)
    b.prism([(-0.075, 0.095), (0.075, 0.095), (0.09, 0.15), (-0.09, 0.15)], 0.006, m, z0=0.0)
    for x in (-0.032, 0.0, 0.032):
        pts = [(x, 0.10 * math.cos(math.radians(a)), 0.093 * math.sin(math.radians(a)) + 0.004)
               for a in range(20, 161, 20)]
        b.tube(pts, 0.005, m, seg=5)
    b.box((0.04, 0.012, 0.024), (0, 0.105, 0.07), mat("ink", 0.5), bevel=0.002, seg=1)
    return b


def r_trophy():
    b = B()
    b.cyl(0.045, 0.014, (0, 0, 0), mat("walnut", 0.5), seg=14)
    b.lathe([(0, 0.014), (0.03, 0.014), (0.012, 0.03), (0.009, 0.06), (0.018, 0.07), (0.03, 0.095),
             (0.042, 0.13), (0.04, 0.133), (0.032, 0.128), (0, 0.125)], (0, 0, 0), mat("brass", 0.25, 1.0), seg=14)
    return b


def r_filters():
    b = B()
    b.box((0.16, 0.11, 0.09), (-0.07, 0, 0.045), mat("white", 0.8), bevel=0.003, seg=1)
    b.box((0.161, 0.111, 0.028), (-0.07, 0, 0.045), mat("coral", 0.7), bevel=0, seg=1)
    for x, y in ((0.06, -0.03), (0.06, 0.04)):
        b.lathe([(0, 0), (0.038, 0), (0.042, 0.005), (0.042, 0.012), (0.036, 0.016), (0.036, 0.04),
                 (0.042, 0.044), (0.042, 0.075), (0.03, 0.084), (0, 0.086)], (x, y, 0), mat("charcoal", 0.6), seg=14)
        b.lathe([(0.0422, 0.048), (0.0422, 0.068)], (x, y, 0), mat("mustard", 0.5), seg=14)
    return b


def r_hose():
    b = B()
    n = 64
    pts = []
    for i in range(n):
        t = i / (n - 1)
        a = t * 2.6 * 2 * math.pi
        pts.append((0.16 * math.cos(a), 0.16 * math.sin(a), 0.02 + 0.046 * 2.6 * t))
    b.tube(pts, 0.018, mat("mustard", 0.6), seg=6)
    e = Vector(pts[-1])
    tan = (Vector(pts[-1]) - Vector(pts[-2])).normalized()
    b.tube([e, e + tan * 0.11], 0.024, mat("charcoal", 0.4, 0.4), seg=8)
    return b


def r_hamper():
    b = B()
    b.lathe([(0, 0.03), (0.2, 0.0), (0.245, 0.02), (0.275, 0.5), (0.285, 0.53), (0.272, 0.53),
             (0.262, 0.06), (0, 0.05)], (0, 0, 0), mat("blush", 0.9), seg=22)
    b.sph(0.2, (0, 0, 0.5), mat("white", 0.95), scale=(1.1, 1.0, 0.45), seg=12, ring=6)
    b.sph(0.11, (0.08, 0.05, 0.56), mat("sky", 0.95), scale=(1.0, 1.0, 0.7), seg=10, ring=6)
    return b


def r_doormat():
    b = B()
    b.box((0.9, 0.55, 0.014), (0, 0, 0.007), mat("navy", 0.95), bevel=0.004, seg=1)
    b.box((0.8, 0.45, 0.004), (0, 0, 0.015), mat("mustard", 0.95), bevel=0, seg=1)
    b.box((0.72, 0.37, 0.004), (0, 0, 0.018), mat("navy", 0.95), bevel=0, seg=1)
    return b


def r_stool():
    b = B()
    b.lathe([(0, 0.40), (0.16, 0.40), (0.17, 0.408), (0.17, 0.43), (0.15, 0.44), (0, 0.44)], (0, 0, 0),
            mat("coral", 0.6), seg=20)
    metal = mat("charcoal", 0.4, 0.5)
    for k in range(3):
        a = 2 * math.pi * k / 3
        b.tube([(0.10 * math.cos(a), 0.10 * math.sin(a), 0.40), (0.16 * math.cos(a), 0.16 * math.sin(a), 0.0)],
               0.012, metal, seg=6)
    b.tube([(0.13 * math.cos(2 * math.pi * k / 16), 0.13 * math.sin(2 * math.pi * k / 16), 0.17)
            for k in range(17)], 0.006, metal, seg=5, caps=False)
    return b


def r_tote(c="coral"):
    b = B()
    b.box((0.3, 0.11, 0.3), (0, 0, 0.15), mat(c, 0.85), bevel=0.012, seg=2, taper_top=0.05)
    b.box((0.265, 0.075, 0.004), (0, 0, 0.299), mat("ink", 0.9), bevel=0, seg=1)       # dark opening
    b.box((0.2, 0.004, 0.11), (0, 0.056, 0.13), mat("navy", 0.85), bevel=0.002, seg=1)   # print
    b.box((0.3, 0.004, 0.02), (0, 0.055, 0.285), mat("navy", 0.85), bevel=0, seg=1)      # hem band
    for y in (-0.028, 0.028):
        b.tube(arc(0, y, 0.298, 0.085, 180, 0, 10), 0.009, mat("navy", 0.85), seg=6)
    return b


def r_duck():
    b = B()
    y = mat("mustard", 0.4)
    b.sph(0.03, (0, 0, 0.03), y, scale=(1.2, 1.0, 0.95), seg=10, ring=7)
    b.sph(0.02, (0.022, 0, 0.063), y, seg=9, ring=6)
    b.cyl(0.009, 0.014, (0.038, 0, 0.058), mat("coral", 0.5), r2=0.004, seg=8, axis="X")
    b.cyl(0.012, 0.02, (-0.036, 0, 0.04), y, r2=0.003, seg=8, axis="X")
    for s in (-1, 1):
        b.sph(0.004, (0.034, 0.011 * s, 0.068), mat("ink", 0.3), seg=6, ring=4)
    return b


def r_noodles():
    b = B()
    b.lathe([(0, 0), (0.033, 0), (0.052, 0.09), (0, 0.09)], (0, 0, 0), mat("white", 0.6), seg=16)
    b.lathe([(0.0395, 0.025), (0.0468, 0.06)], (0, 0, 0), mat("coral", 0.6), seg=16)
    b.lathe([(0.052, 0.09), (0.055, 0.095), (0, 0.098)], (0, 0, 0), mat("mustard", 0.5), seg=16)
    return b


def r_radio():
    b = B()
    b.box((0.26, 0.09, 0.15), (0, 0, 0.075), mat("sky", 0.5), bevel=0.01, seg=2)
    b.lathe([(0, 0), (0.05, 0), (0.05, 0.003), (0, 0.003)], (-0.06, -0.045, 0.075), mat("charcoal", 0.6),
            seg=14, rot=Matrix.Rotation(math.pi / 2, 3, "X"))
    for z in (0.1, 0.05):
        b.cyl(0.013, 0.012, (0.07, -0.05, z), mat("white", 0.4), seg=10, axis="Y")
    b.tube(arc(0, 0, 0.15, 0.07, 160, 20, 9), 0.005, mat("charcoal", 0.5), seg=5)
    b.tube([(0.1, 0.02, 0.15), (0.16, 0.04, 0.3)], 0.003, mat("steel", 0.3, 1.0), seg=5)
    return b


def r_photo(c="blush"):
    b = B()
    b.box((0.13, 0.014, 0.16), (0, 0, 0.08), mat("walnut", 0.5), bevel=0.003, seg=1)
    b.box((0.105, 0.016, 0.135), (0, 0, 0.08), mat(c, 0.7), bevel=0, seg=1)
    b.sph(0.02, (0, 0.0, 0.10), mat("mustard", 0.7), scale=(1, 0.2, 1), seg=10, ring=6)
    b.box((0.06, 0.05, 0.008), (0, 0.03, 0.004), mat("walnut", 0.5), bevel=0.002, seg=1)
    return b


def r_candle():
    b = B()
    b.lathe([(0, 0), (0.035, 0), (0.04, 0.006), (0.04, 0.068), (0.037, 0.07), (0.035, 0.068),
             (0.035, 0.01), (0, 0.008)], (0, 0, 0), mat("glass", 0.15), seg=14)
    b.cyl(0.034, 0.05, (0, 0, 0.008), mat("blush", 0.7), seg=14)
    b.lathe([(0, 0), (0.004, 0.004), (0.006, 0.012), (0.003, 0.022), (0, 0.03)], (0, 0, 0.058),
            mat("mustard", 0.4, emit=8.0), seg=8)
    return b


def r_clock_desk():
    b = B()
    b.cyl(0.05, 0.034, (0, -0.017, 0.055), mat("rose", 0.4, 0.2), seg=18, axis="Y")
    b.cyl(0.042, 0.003, (0, -0.0185, 0.055), mat("paper", 0.5), seg=18, axis="Y")
    b.box((0.004, 0.003, 0.03), (0, -0.0205, 0.065), mat("ink", 0.5), bevel=0, seg=1)
    b.box((0.003, 0.003, 0.02), (0.008, -0.0205, 0.055), mat("coral", 0.5), bevel=0, seg=1,
          rot=Matrix.Rotation(-1.0, 3, "Y"))
    for s in (-1, 1):
        b.sph(0.016, (0.033 * s, 0, 0.1), mat("charcoal", 0.4, 0.5), scale=(1, 0.6, 0.6), seg=8, ring=6)
        b.box((0.008, 0.008, 0.02), (0.032 * s, 0, 0.01), mat("charcoal", 0.5), bevel=0, seg=1)
    b.box((0.004, 0.004, 0.012), (0, 0, 0.11), mat("charcoal", 0.5), bevel=0, seg=1)
    return b


def r_slippers():
    b = B()
    for s in (-0.07, 0.07):
        pts = []
        for k in range(18):
            t_ = 2 * math.pi * k / 18
            pts.append((s + 0.048 * math.cos(t_) * (1.0 - 0.2 * math.sin(t_)), 0.13 * math.sin(t_)))
        b.prism(pts, 0.012, mat("white", 0.9), z0=0.0)
        b.lathe([(0.05, 0), (0.049, 0.012), (0.042, 0.032), (0.024, 0.046), (0, 0.05)], (s, 0.055, 0.012),
                mat("lilac", 0.95), seg=12, scale=(1, 1.5, 1))
    return b


def f_floorlamp():
    b = B()
    b.lathe([(0, 0), (0.13, 0), (0.13, 0.012), (0.02, 0.02), (0, 0.02)], (0, 0, 0), mat("charcoal", 0.4, 0.5), seg=20)
    b.cyl(0.009, 1.28, (0, 0, 0.02), mat("brass", 0.3, 0.9), seg=8)
    b.lathe([(0.10, 1.3), (0.19, 1.3), (0.19, 1.56), (0.11, 1.56)], (0, 0, 0), mat("blush", 0.5, emit=2.6), seg=22)
    return b


def f_shelving():
    b = B()
    w, d, h = 0.95, 0.32, 1.25
    wood = mat("walnut", 0.55)
    for sx in (-w / 2 + 0.015, w / 2 - 0.015):
        b.box((0.03, d, h), (sx, 0, h / 2), wood, bevel=0.003, seg=1)
    for z in (0.015, 0.435, 0.835, h - 0.015):
        b.box((w, d, 0.03), (0, 0, z), wood, bevel=0.003, seg=1)
    b.box((w, 0.012, h), (0, d / 2 - 0.006, h / 2), mat("charcoal", 0.6), bevel=0, seg=1)
    x = -w / 2 + 0.05
    for c in ("navy", "coral", "mustard", "denim", "blush", "navy", "olive"):
        bw = random.uniform(0.04, 0.06)
        b.box((bw, 0.24, 0.3), (x + bw / 2, 0, 0.45 + 0.15), mat(c, 0.7), bevel=0.002, seg=1)
        x += bw + 0.004
    b.box((0.36, 0.26, 0.24), (-0.2, 0, 0.03 + 0.12), mat("blush", 0.95), bevel=0.02, seg=2, taper_top=0.05)
    b.box((0.36, 0.26, 0.24), (0.22, 0, 0.03 + 0.12), mat("denim", 0.95), bevel=0.02, seg=2, taper_top=0.05)
    b.box((0.18, 0.2, 0.12), (-0.25, 0, 0.85 + 0.06), mat("white", 0.8), bevel=0.004, seg=1)
    b.box((0.18, 0.2, 0.09), (-0.25, 0, 0.85 + 0.12 + 0.045), mat("coral", 0.8), bevel=0.004, seg=1)
    b.lathe([(0, 0), (0.05, 0), (0.052, 0.01), (0.05, 0.1), (0.04, 0.11), (0, 0.11)], (0.15, 0, 0.85),
            mat("sky", 0.3, 0.3), seg=14)
    b.box((0.09, 0.03, 0.12), (0.28, 0, 0.85 + 0.06), mat("walnut", 0.5), bevel=0.002, seg=1)
    return b


# ================================================================ wall props
def art(b, w, h, style, z0):
    cols = [("mustard", "coral", "navy"), ("blush", "denim", "ink"), ("sky", "rose", "navy")][style % 3]
    b.box((w, h, 0.004), (0, 0, z0), mat("paper", 0.8), bevel=0, seg=1)
    if style % 3 == 0:
        b.cyl(min(w, h) * 0.17, 0.004, (w * 0.12, h * 0.15, z0), mat(cols[0], 0.6), seg=24)
        b.prism([(-w * .4, -h * .38), (-w * .05, h * .1), (w * .2, -h * .38)], 0.004, mat(cols[2], 0.7), z0=z0)
        b.prism([(-w * .05, -h * .38), (w * .2, -h * .02), (w * .42, -h * .38)], 0.005, mat(cols[1], 0.7), z0=z0)
    elif style % 3 == 1:
        for k in range(3):
            b.box((w * .7, h * .16, 0.004), (0, h * (0.22 - .24 * k), z0 + 0.002 * k), mat(cols[k], 0.7), bevel=0, seg=1)
    else:
        b.cyl(min(w, h) * 0.22, 0.004, (-w * .1, h * .05, z0), mat(cols[0], 0.6), seg=24)
        b.box((w * .16, h * .55, 0.004), (w * .25, -h * .08, z0 + 0.002), mat(cols[1], 0.7), bevel=0, seg=1)
        b.box((w * .5, h * .06, 0.004), (0, -h * .38, z0 + 0.003), mat(cols[2], 0.7), bevel=0, seg=1)


def w_frame(w=0.42, h=0.56, style=0, fr="walnut"):
    b = B()
    t, d = 0.03, 0.028
    b.box((w, h, 0.006), (0, 0, 0.003), mat("paper", 0.8), bevel=0, seg=1)
    for (sx, sy, px, py) in ((w, t, 0, h / 2 - t / 2), (w, t, 0, -h / 2 + t / 2),
                              (t, h, w / 2 - t / 2, 0), (t, h, -w / 2 + t / 2, 0)):
        b.box((sx, sy, d), (px, py, d / 2), mat(fr, 0.5), bevel=0.003, seg=1)
    art(b, w - 2 * t - 0.03, h - 2 * t - 0.03, style, 0.008)
    return b


def w_clock():
    b = B()
    b.cyl(0.17, 0.035, (0, 0, 0), mat("charcoal", 0.4, 0.4), seg=32)
    b.cyl(0.145, 0.006, (0, 0, 0.035), mat("paper", 0.5), seg=32)
    for k in range(12):
        a = k * math.pi / 6
        b.box((0.006, 0.02 if k % 3 == 0 else 0.012, 0.004), (0.12 * math.sin(a), 0.12 * math.cos(a), 0.043),
              mat("ink", 0.5), bevel=0, rot=Matrix.Rotation(-a, 3, "Z"), seg=1)
    b.box((0.008, 0.075, 0.005), (0.0, 0.03, 0.046), mat("ink", 0.5), bevel=0, seg=1)
    b.box((0.008, 0.055, 0.005), (0.027, 0.0, 0.048), mat("coral", 0.5), bevel=0,
          rot=Matrix.Rotation(-1.1, 3, "Z"), seg=1)
    return b


def w_shelf():
    b = B()
    b.box((0.85, 0.03, 0.18), (0, 0, 0.09), mat("walnut", 0.55), bevel=0.003, seg=1)
    for sx in (-0.33, 0.33):
        b.box((0.025, 0.08, 0.14), (sx, -0.055, 0.07), mat("charcoal", 0.4, 0.5), bevel=0.002, seg=1)
    x = -0.34
    for c in ("navy", "coral", "mustard"):
        bw = random.uniform(0.028, 0.04)
        b.box((bw, 0.2, 0.13), (x + bw / 2, 0.015 + 0.1, 0.09), mat(c, 0.7), bevel=0.002, seg=1)
        x += bw + 0.004
    b.lathe([(0, 0), (0.038, 0), (0.04, 0.01), (0.04, 0.09), (0.03, 0.105), (0, 0.105)], (0.06, 0.015, 0.09),
            mat("glass", 0.12), seg=12, rot=Matrix.Rotation(0, 3, "Z"))
    b.box((0.08, 0.1, 0.08), (0.14, 0.065, 0.09), mat("rose", 0.6), bevel=0.008, seg=2)
    b.lathe([(0, 0), (0.03, 0), (0.03, 0.02), (0, 0.03)], (0.25, 0.015, 0.09), mat("sky", 0.4), seg=10,
            rot=Matrix.Rotation(-math.pi / 2, 3, "X"))
    b.cyl(0.04, 0.014, (0.33, 0.015, 0.09), mat("walnut", 0.5), seg=12, axis="Y")
    return b


def w_cork():
    b = B()
    w, h = 0.9, 0.6
    b.box((w, h, 0.012), (0, 0, 0.006), mat("cork", 0.95), bevel=0, seg=1)
    t = 0.028
    for (sx, sy, px, py) in ((w + 2 * t, t, 0, h / 2 + t / 2), (w + 2 * t, t, 0, -h / 2 - t / 2),
                              (t, h, w / 2 + t / 2, 0), (t, h, -w / 2 - t / 2, 0)):
        b.box((sx, sy, 0.03), (px, py, 0.015), mat("walnut", 0.5), bevel=0.003, seg=1)
    cols = ("mustard", "blush", "sky", "coral", "lilac", "paper")
    for k in range(9):
        px, py = random.uniform(-w * 0.38, w * 0.38), random.uniform(-h * 0.33, h * 0.33)
        sw = random.uniform(0.07, 0.11)
        sh = sw * random.uniform(0.9, 1.3)
        b.box((sw, sh, 0.003), (px, py, 0.0135 + 0.0005 * k), mat(random.choice(cols), 0.85), bevel=0,
              rot=Matrix.Rotation(random.uniform(-.25, .25), 3, "Z"), seg=1)
        if k % 3 == 0:
            b.box((sw * .78, sh * .62, 0.0022), (px, py + sh * .07, 0.017 + 0.0005 * k), mat("denim", 0.7), bevel=0, seg=1)
        b.cyl(0.006, 0.008, (px, py + sh * .4, 0.0165 + 0.0005 * k), mat(random.choice(("coral", "navy", "mustard")), 0.4),
              r2=0.003, seg=6)
    return b


def _catenary(span, sag, n=24):
    return [(-span / 2 + span * i / n, -sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


def w_pennants(span=2.6, n=9):
    b = B()
    cols = ("mustard", "coral", "navy", "blush", "denim")
    pts = _catenary(span, 0.16)
    b.tube([(x, y, 0.012) for x, y in pts], 0.002, mat("charcoal", 0.6), seg=4)
    for k in range(n):
        t = (k + 0.5) / n
        x = -span / 2 + span * t
        y = -0.16 * 4 * t * (1 - t)
        w = span / n * 0.72
        b.prism([(x - w / 2, y), (x + w / 2, y), (x, y - w * 1.1)], 0.004, mat(cols[k % len(cols)], 0.85), z0=0.013)
    for s in (-1, 1):
        b.box((0.03, 0.03, 0.012), (s * span / 2, 0, 0.006), mat("brass", 0.3, 0.9), bevel=0.002, seg=1)
    return b


def w_stringlights(span=2.6, n=9):
    b = B()
    pts = _catenary(span, 0.22)
    b.tube([(x, y, 0.02) for x, y in pts], 0.0015, mat("charcoal", 0.6), seg=4)
    for k in range(n):
        t = (k + 0.5) / n
        x = -span / 2 + span * t
        y = -0.22 * 4 * t * (1 - t)
        b.sph(0.018, (x, y - 0.03, 0.028), mat("mustard", 0.3, emit=9.0), seg=8, ring=6)
    for s in (-1, 1):
        b.box((0.03, 0.03, 0.02), (s * span / 2, 0, 0.01), mat("charcoal", 0.5), bevel=0.002, seg=1)
    return b


def w_hooks():
    """Hook rail with a hung tote, cap, keys and a lanyard badge (wall frame: y up, z out)."""
    b = B()
    b.box((1.0, 0.07, 0.022), (0, 0, 0.011), mat("walnut", 0.55), bevel=0.004, seg=1)
    brass = mat("brass", 0.3, 0.9)
    for x in (-0.4, -0.2, 0.0, 0.2, 0.4):
        b.tube([(x, 0, 0.022), (x, 0, 0.07), (x, -0.004, 0.09)], 0.007, brass, seg=6)
        b.sph(0.014, (x, -0.004, 0.09), brass, seg=8, ring=5)
    # tote hung by its handle from the first hook
    b.box((0.26, 0.28, 0.05), (-0.4, -0.2, 0.085), mat("denim", 0.85), bevel=0.012, seg=2, taper_top=0.05)
    b.tube(arc(-0.4, -0.06, 0.09, 0.05, 0, 180, 9, plane="XY"), 0.006, mat("navy", 0.85), seg=5)
    b.box((0.2, 0.12, 0.004), (-0.4, -0.25, 0.112), mat("mustard", 0.8), bevel=0, seg=1)
    # cap hanging from the second hook (dome pointing down)
    b.lathe([(0.085, 0), (0.084, 0.02), (0.07, 0.05), (0.04, 0.07), (0, 0.075)], (-0.2, -0.045, 0.085),
            mat("mustard", 0.7), seg=14, rot=Matrix.Rotation(math.pi / 2, 3, "X"), scale=(1, 1, 1))
    # keys
    b.tube(arc(0.0, -0.03, 0.09, 0.022, 0, 360, 12, plane="XY"), 0.003, mat("steel", 0.3, 1.0), seg=5)
    b.box((0.03, 0.06, 0.004), (0.0, -0.1, 0.09), mat("brass", 0.3, 1.0), bevel=0.001, seg=1)
    b.box((0.03, 0.055, 0.004), (0.012, -0.1, 0.098), mat("steel", 0.3, 1.0), bevel=0.001, seg=1)
    # lanyard and badge
    b.box((0.03, 0.22, 0.008), (0.2, -0.11, 0.092), mat("mustard", 0.7), bevel=0.002, seg=1)
    b.box((0.06, 0.09, 0.008), (0.2, -0.27, 0.096), mat("white", 0.5), bevel=0.003, seg=1)
    b.box((0.05, 0.02, 0.002), (0.2, -0.245, 0.101), mat("coral", 0.5), bevel=0, seg=1)
    return b


def w_mirror():
    b = B()
    b.cyl(0.29, 0.024, (0, 0, 0), mat("charcoal", 0.4, 0.5), seg=36)
    b.cyl(0.26, 0.006, (0, 0, 0.024), mat("steel", 0.06, 1.0), seg=36)
    return b


def w_roster():
    b = B()
    w, h = 0.72, 0.5
    b.box((w, h, 0.016), (0, 0, 0.008), mat("white", 0.35), bevel=0.004, seg=1)
    for (sx, sy, px, py) in ((w + .04, .02, 0, h / 2 + .01), (w + .04, .02, 0, -h / 2 - .01),
                              (.02, h, w / 2 + .01, 0), (.02, h, -w / 2 - .01, 0)):
        b.box((sx, sy, 0.028), (px, py, 0.014), mat("steel", 0.4, 0.7), bevel=0.002, seg=1)
    for r in range(4):
        b.box((w * .9, 0.003, 0.002), (0, h * (0.32 - 0.2 * r), 0.017), mat("denim", 0.6), bevel=0, seg=1)
    for c in range(4):
        b.box((0.003, h * .8, 0.002), (w * (-0.3 + 0.2 * c), 0, 0.017), mat("denim", 0.6), bevel=0, seg=1)
    for k, cc in enumerate(("coral", "mustard", "sky", "rose", "olive")):
        b.cyl(0.014, 0.008, (-0.25 + 0.13 * k, 0.16 - 0.1 * (k % 3), 0.016), mat(cc, 0.4), seg=10)
    b.box((0.6, 0.03, 0.03), (0, -h / 2 - 0.03, 0.02), mat("steel", 0.4, 0.7), bevel=0.003, seg=1)
    return b


def w_neon():
    b = B()
    b.tube(arc(0, 0, 0.03, 0.15, 0, 360, 33, plane="XY"), 0.007, mat("coral", 0.3, emit=7.0), seg=6, caps=False)
    b.tube(arc(0, 0, 0.03, 0.075, 0, 360, 25, plane="XY"), 0.007, mat("mustard", 0.3, emit=7.0), seg=6, caps=False)
    for k in range(8):
        a = k * math.pi / 4
        b.box((0.01, 0.06, 0.012), (0.24 * math.sin(a), 0.24 * math.cos(a), 0.03), mat("blush", 0.3, emit=6.0),
              bevel=0, rot=Matrix.Rotation(-a, 3, "Z"), seg=1)
    for sx, sy in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)):
        b.cyl(0.006, 0.03, (sx, sy, 0), mat("charcoal", 0.5), seg=6)
    return b


def w_plaque():
    b = B()
    b.box((0.36, 0.26, 0.02), (0, 0, 0.01), mat("walnut", 0.5), bevel=0.004, seg=1)
    b.box((0.3, 0.12, 0.004), (0, 0.03, 0.022), mat("brass", 0.25, 1.0), bevel=0, seg=1)
    b.box((0.26, 0.012, 0.004), (0, -0.08, 0.022), mat("brass", 0.25, 1.0), bevel=0, seg=1)
    b.sph(0.025, (0, 0.03, 0.024), mat("coral", 0.5), scale=(1, 1, 0.15), seg=10, ring=6)
    return b


def w_towelrack():
    """Rail with two towels hung over the bar (cloth ribbons, closed thin shells)."""
    b = B()
    metal = mat("charcoal", 0.4, 0.5)
    b.tube([(-0.42, 0.0, 0.06), (0.42, 0.0, 0.06)], 0.009, metal, seg=8)
    for x in (-0.4, 0.4):
        b.box((0.03, 0.04, 0.06), (x, 0, 0.03), metal, bevel=0.002, seg=1)
    for x, c, drop in ((-0.2, "sky", 0.58), (0.12, "blush", 0.5)):
        prof = [(-drop, 0.082), (-0.04, 0.081), (0.008, 0.075), (0.016, 0.06), (0.008, 0.045),
                (-0.02, 0.041), (-drop * 0.8, 0.038)]
        b.ribbon(prof, x - 0.14, x + 0.14, 0.008, mat(c, 0.95))
    return b


def w_poster(style=1, w=0.5, h=0.7):
    b = B()
    art(b, w, h, style, 0.002)
    for sx in (-1, 1):
        b.box((0.05, 0.02, 0.005), (sx * (w / 2 - 0.02), h / 2 - 0.01, 0.006), mat("blush", 0.7), bevel=0, seg=1)
    return b


def w_sun_mural(r=0.85):
    b = B()
    for i, c in enumerate(("navy", "coral", "mustard", "blush", "paper")):
        b.cyl(r * (1 - i * 0.18), 0.004, (0, 0, 0.001 * i), mat(c, 0.85), seg=36)
    return b


# ============================================================== ceiling props
def c_pendant(shade="mustard"):
    """Top face touches the ceiling at z = 0; hangs toward -z. Open-bottom cone shade."""
    b = B()
    b.lathe([(0.0, 0), (0.05, 0), (0.05, -0.014), (0.0, -0.014)], (0, 0, 0), mat("charcoal", 0.5), seg=14)
    b.tube([(0, 0, -0.014), (0, 0, -0.62)], 0.004, mat("charcoal", 0.5), seg=6)
    b.lathe([(0.03, -0.62), (0.13, -0.86), (0.128, -0.864), (0.028, -0.626)], (0, 0, 0),
            mat(shade, 0.4, 0.3), seg=24)
    b.lathe([(0.026, -0.63), (0.124, -0.858)], (0, 0, 0), mat("white", 0.6, emit=1.5), seg=24)
    b.sph(0.035, (0, 0, -0.80), mat("blush", 0.4, emit=8.0), seg=10, ring=7)
    return b


# ================================================================ hung clothing
def _loft(b, rings, m, seg=14):
    """Loft elliptical rings [(z, hw, hd, yoff), ...] with fan caps at both ends."""
    vr = []
    for (z, hw, hd, yo) in rings:
        vr.append([b.bm.verts.new((hw * math.cos(2 * math.pi * k / seg),
                                   yo + hd * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for i in range(len(vr) - 1):
        for k in range(seg):
            b.bm.faces.new((vr[i][k], vr[i][(k + 1) % seg], vr[i + 1][(k + 1) % seg], vr[i + 1][k]))
    for ring in (vr[0], vr[-1]):
        try:
            b.bm.faces.new(ring)
        except ValueError:
            pass
    b._fin([v for r in vr for v in r], m)


def jacket(cloth="khaki"):
    """Work jacket on a wooden hanger. Origin = hanger apex; hook rises to +0.06; front is +y."""
    b = B()
    fab = mat(cloth, 0.95)
    dark = mat("charcoal", 0.7)
    rings = [(-0.005, 0.07, 0.045, 0), (-0.028, 0.13, 0.055, 0), (-0.07, 0.20, 0.072, 0),
             (-0.12, 0.222, 0.092, 0.004), (-0.28, 0.215, 0.10, 0.006), (-0.46, 0.22, 0.105, 0.006),
             (-0.60, 0.228, 0.108, 0.006), (-0.64, 0.228, 0.108, 0.006)]
    _loft(b, rings, fab)
    for s in (-1, 1):   # sleeves hang close to the body, slightly forward
        b.tube([(s * 0.205, 0.0, -0.08), (s * 0.245, 0.03, -0.16), (s * 0.255, 0.05, -0.34),
                (s * 0.255, 0.06, -0.54)], lambda t: 0.048 - 0.008 * t, fab, seg=9)
        b.tube([(s * 0.255, 0.06, -0.52), (s * 0.255, 0.06, -0.565)], 0.042, dark, seg=9)   # cuff
    b.sph(0.09, (0, -0.095, -0.075), fab, scale=(1.15, 0.4, 0.62), seg=10, ring=7)        # folded hood
    b.tube(arc(0, 0.0, -0.028, 0.07, 200, 340, 11, plane="XY"), 0.015, fab, seg=6)        # collar
    b.box((0.006, 0.006, 0.5), (0, 0.111, -0.33), dark, bevel=0, seg=1)                   # zip
    for s in (-1, 1):
        b.box((0.09, 0.007, 0.1), (s * 0.11, 0.111, -0.45), fab, bevel=0.002, seg=1)     # pockets
    b.tube([(0.23 * math.cos(2 * math.pi * k / 20), 0.006 + 0.11 * math.sin(2 * math.pi * k / 20), -0.62)
            for k in range(21)], 0.005, dark, seg=5, caps=False)                          # hem band
    wood = mat("walnut", 0.5)
    b.tube([(-0.21, 0, -0.10), (-0.10, 0, -0.045), (0, 0, 0.0), (0.10, 0, -0.045), (0.21, 0, -0.10)],
           0.005, wood, seg=5)
    b.tube([(0, 0, 0.0), (0, 0, 0.03), (0.012, 0, 0.055), (0.03, 0, 0.06), (0.04, 0, 0.045)], 0.0035,
           mat("steel", 0.3, 1.0), seg=5)
    return b


def hung_towel(cloth="sky"):
    """Towel folded over a wall hook. Local: x along wall, y up, z out from wall. Origin = hook."""
    b = B()
    prof = [(-0.70, 0.045), (-0.04, 0.042), (0.0, 0.033), (-0.004, 0.02), (-0.03, 0.014), (-0.56, 0.02)]
    b.ribbon(prof, -0.21, 0.21, 0.01, mat(cloth, 0.95))
    b.box((0.42, 0.006, 0.012), (0.0, -0.66, 0.048), mat("white", 0.9), bevel=0, seg=1)
    return b


# ============================================================ replacements for lumpy assets
def r_boot(upper="forest"):
    """Work boot, toe toward +y, standing on z = 0. About 500 triangles."""
    b = B()
    rubber = mat("ink", 0.8)
    hide = mat(upper, 0.7)
    lace = mat("paper", 0.8)
    pts = []
    for k in range(20):
        t_ = 2 * math.pi * k / 20
        y = 0.145 * math.sin(t_)
        w = 0.054 * (1.0 - 0.18 * max(math.sin(t_), 0)) * (1.0 - 0.12 * max(-math.sin(t_), 0))
        pts.append((w * math.cos(t_), y))
    b.prism(pts, 0.03, rubber, z0=0.0)                                            # sole
    b.box((0.095, 0.05, 0.024), (0, -0.115, 0.012), rubber, bevel=0.004, seg=1)    # heel block
    b.lathe([(0.058, 0), (0.058, 0.024), (0.052, 0.058), (0.032, 0.082), (0, 0.092)], (0, 0.03, 0.028),
            hide, seg=14, scale=(1, 2.5, 1))                                       # toe box and vamp
    b.lathe([(0.048, 0), (0.048, 0.06), (0.05, 0.12), (0.056, 0.168), (0.062, 0.184), (0.056, 0.19),
             (0.046, 0.184), (0.044, 0.06), (0, 0.06)], (0, -0.06, 0.03), hide, seg=14,
            scale=(1, 1.05, 1))                                                    # tapered shaft
    b.tube([(0.0, -0.006, 0.19 + 0.03), (0.0, -0.0, 0.16 + 0.03), (0.0, 0.012, 0.11 + 0.03)], 0.02, hide,
           seg=6)                                                                  # tongue
    for z in (0.10, 0.13, 0.16, 0.19):
        b.cyl(0.0035, 0.075, (-0.0375, -0.004 + (0.19 - z) * -0.06, z), lace, seg=4, axis="X")  # laces
    return b


def r_duffel(cloth="forest"):
    """Gym duffel lying on the floor: barrel body, two straps, side pocket. Long axis = x."""
    b = B()
    fab = mat(cloth, 0.9)
    strap = mat("navy", 0.85)
    b.lathe([(0, -0.30), (0.08, -0.29), (0.125, -0.24), (0.14, -0.14), (0.142, 0.0), (0.14, 0.14),
             (0.125, 0.24), (0.08, 0.29), (0, 0.30)], (0, 0, 0.135), fab, seg=16,
            rot=Matrix.Rotation(math.pi / 2, 3, "Y"), scale=(1.0, 1.0, 1.0))
    for x in (-0.1, 0.1):
        b.tube(
               [(x, 0.145 * math.sin(a), 0.135 + 0.145 * math.cos(a)) for a in [i * 2 * math.pi / 16 for i in range(17)]],
               0.008, strap, seg=5, caps=False)
    b.tube([(-0.12, 0.0, 0.29), (-0.10, 0.0, 0.36), (0.10, 0.0, 0.36), (0.12, 0.0, 0.29)], 0.009, strap, seg=6)
    b.box((0.16, 0.05, 0.11), (0.0, 0.135, 0.11), fab, bevel=0.012, seg=2)               # side pocket
    b.tube([(-0.26, 0.0, 0.275), (0.26, 0.0, 0.275)], 0.004, mat("charcoal", 0.6), seg=4)  # zip
    return b
