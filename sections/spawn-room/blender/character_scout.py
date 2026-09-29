#!/usr/bin/env python3
"""
"Scout" character built from the owner's concept image (big round head, buck-toothed grin, mismatched eyes),
made taller and goofier, in a plain unisex crew-neck t-shirt and straight-leg jeans with brown shoes.
Glasses and hat exist but are off by default (accessories come later).

Blender 5.2 / bpy. Every group is its own object under one root so parts can be swapped later:
LEGS (shoes + jeans), TORSO (t-shirt, arms, hands), HEAD, FACE, and opt-in GLASSES / HAT (off by default). The head group hangs off a pivot empty
at the neck, tilted for personality. Original model: nothing here is copied from another game.
Local frame: origin at the feet, +y is the front, total height about 1.85 m with the hat.
"""

import math

import bpy
from mathutils import Matrix, Vector

from cozy_geo import B, HEX, arc, mat, tri_count

HEX.update({
    "sc_skin": "#E2683B", "sc_blush": "#C9553B", "sc_shirt": "#E6C978", "sc_shirt_dk": "#C9A95C",
    "sc_sleeve": "#D9A63A", "sc_shorts": "#7E9038", "sc_shorts_dk": "#5F6B25", "sc_sock": "#F2EEE4",
    "sc_shoe": "#6B2B14", "sc_sole": "#2A1208", "sc_hat": "#E8C45A", "sc_leaf": "#7FA84A",
    "sc_iris": "#141C4A", "sc_mouth": "#2A0F12", "sc_black": "#101014",
    "sc_tee": "#E8C45A", "sc_tee_dk": "#D2AB40", "sc_denim": "#4F70A8", "sc_denim_dk": "#3B5687", "sc_denim_lt": "#6E8FC4",
    "sc_stitch": "#E6C46A",
})

LIFT = 0.10                          # extra leg length; the upper body group is raised by this
PIVOT_Z = 1.17 + LIFT                # neck pivot height
HZ = 0.28                            # head centre above the pivot
HRX, HRY, HRZ = 0.29, 0.268, 0.28    # head radii


def _fy(dx, dz):
    """Front surface depth of the head at horizontal offset dx and vertical offset dz from its centre."""
    v = 1.0 - (dx / HRX) ** 2 - (dz / HRZ) ** 2
    return HRY * math.sqrt(max(v, 0.04))


def part_legs():
    """Shoes and straight-leg jeans (unisex cut). Jeans run from the hip down to a turned-up cuff."""
    b = B()
    shoe = mat("sc_shoe", 0.55)
    sole = mat("sc_sole", 0.7)
    denim = mat("sc_denim", 0.92)
    denim_dk = mat("sc_denim_dk", 0.92)
    denim_lt = mat("sc_denim_lt", 0.9)
    stitch = mat("sc_stitch", 0.8)
    for s in (-1, 1):
        x = s * 0.115
        b.lathe([(0, 0.025), (0.078, 0.025), (0.092, 0.05), (0.092, 0.085), (0.072, 0.118), (0.032, 0.14), (0, 0.145)],
                (x, 0.045, 0.0), shoe, seg=14, scale=(1.0, 1.95, 1.0))
        b.lathe([(0, 0), (0.08, 0), (0.094, 0.012), (0.094, 0.03), (0, 0.03)], (x, 0.045, 0.0), sole, seg=14,
                scale=(1.0, 1.95, 1.0))
        b.box((0.07, 0.05, 0.02), (x, 0.13, 0.135), shoe, bevel=0.008, seg=1)
        # jeans leg: straight cut, slightly wider at the thigh, cuffed at the ankle
        b.cyl(0.098, 0.72, (x * 1.02, 0.0, 0.135), denim, r2=0.122, seg=16)
        b.tube([(x * 1.02, 0.0, 0.135), (x * 1.02, 0.0, 0.16)], 0.106, denim_lt, seg=16)               # turned-up cuff
        b.tube([(x * 1.02, 0.0, 0.16), (x * 1.02, 0.0, 0.165)], 0.100, denim_dk, seg=16)
        # outer-seam stitching
        ox = x * 1.02 + s * 0.108
        b.tube([(ox, 0.0, 0.18), (ox + s * 0.006, 0.0, 0.5), (ox + s * 0.012, 0.0, 0.84)], 0.0032, stitch, seg=4)
        # front pocket edge
        b.tube(arc(x * 1.02 + s * 0.05, 0.118, 0.82, 0.07, 200 if s > 0 else -20, 340 if s > 0 else 120, 8, plane="XZ"),
               0.0032, stitch, seg=4)
    # hips, waistband and fly
    b.box((0.31, 0.225, 0.11), (0, 0, 0.80), denim, bevel=0.03, seg=2)
    b.tube([(0.16 * math.cos(a), 0.118 * math.sin(a), 0.855) for a in [i * 2 * math.pi / 20 for i in range(21)]],
           0.014, denim_dk, seg=5, caps=False)
    b.sph(0.013, (0.0, 0.122, 0.855), mat("brass", 0.3, 0.9), scale=(1.0, 0.5, 1.0), seg=8, ring=5)  # button
    b.tube([(0.0, 0.118, 0.85), (0.0, 0.121, 0.74), (-0.014, 0.121, 0.73)], 0.0028, stitch, seg=4)      # fly stitch
    for s in (-1, 1):                                                                                # back pockets
        b.box((0.075, 0.01, 0.075), (s * 0.075, -0.12, 0.79), denim_dk, bevel=0.004, seg=1)
    return b


def part_torso():
    """Plain crew-neck t-shirt, arms and neck. Built low and raised by LIFT as one object."""
    b = B()
    skin = mat("sc_skin", 0.8)
    tee = mat("sc_tee", 0.92)
    tee_dk = mat("sc_tee_dk", 0.92)
    for s in (-1, 1):
        sx = s * 0.285
        # short tee sleeve with a hem, then bare arm and a simple mitt hand
        b.tube([(sx - s * 0.02, 0.0, 1.08), (sx + s * 0.02, 0.005, 0.99)], 0.088, tee, seg=12)
        b.tube([(sx + s * 0.022, 0.006, 0.985), (sx + s * 0.026, 0.008, 0.968)], 0.091, tee_dk, seg=12)
        b.tube([(sx + s * 0.03, 0.01, 0.98), (sx + s * 0.075, 0.03, 0.78), (sx + s * 0.088, 0.06, 0.56)], 0.045, skin, seg=10)
        hx, hy, hz = sx + s * 0.092, 0.075, 0.50
        b.sph(0.068, (hx, hy, hz), skin, scale=(1.0, 1.0, 1.1), seg=12, ring=8)
        b.sph(0.03, (hx - s * 0.05, hy + 0.045, hz + 0.02), skin, seg=8, ring=6)
    b.box((0.50, 0.30, 0.44), (0, 0, 0.935), tee, bevel=0.03, seg=2)
    b.box((0.51, 0.31, 0.04), (0, 0, 0.745), tee, bevel=0.015, seg=2)
    b.tube([(0.512 * math.cos(a) * 0.5, 0.31 * math.sin(a) * 0.5 + 0.0, 0.727) for a in [i * 2 * math.pi / 20 for i in range(21)]],
           0.006, tee_dk, seg=4, caps=False)                                                          # hem stitch
    # ribbed crew neckline and neck
    b.tube([(0.105 * math.cos(a), 0.085 * math.sin(a), 1.152) for a in [i * 2 * math.pi / 18 for i in range(19)]],
           0.026, tee_dk, seg=6, caps=False)
    b.cyl(0.072, 0.10, (0, 0, 1.10), skin, seg=12)
    return b


def part_head():
    """Big round head (local frame: pivot at the neck, head centre at z = HZ)."""
    b = B()
    b.sph(1.0, (0, 0, HZ), mat("sc_skin", 0.8), scale=(HRX, HRY, HRZ), seg=28, ring=18)
    return b


def part_face():
    b = B()
    ink = mat("sc_black", 0.35)
    white = mat("white", 0.3)
    iris = mat("sc_iris", 0.25)
    blush = mat("sc_blush", 0.85)
    ez = HZ + 0.03
    # mismatched eyes: the wearer's left is bigger and wider open
    for s, big in ((-1, 1.25), (1, 0.95)):
        x = s * 0.118
        y = _fy(x, ez - HZ) - 0.004
        b.sph(0.062 * big, (x, y, ez), white, scale=(1.0, 0.45, 1.08), seg=14, ring=10)
        b.sph(0.046 * big, (x - s * 0.006, y + 0.014, ez - 0.006), iris, scale=(1.0, 0.4, 1.1), seg=12, ring=8)
        b.sph(0.021 * big, (x - s * 0.006, y + 0.024, ez - 0.006), ink, scale=(1.0, 0.4, 1.1), seg=8, ring=6)
        b.sph(0.011, (x + s * 0.012, y + 0.03, ez + 0.016), white, scale=(1.0, 0.4, 1.0), seg=6, ring=4)
    def brow(x0, z0, x1, z1):
        b.tube([(x0, _fy(x0, z0 - HZ) + 0.014, z0), (x1, _fy(x1, z1 - HZ) + 0.014, z1)], 0.0135, ink, seg=5)

    brow(-0.19, ez + 0.10, -0.045, ez + 0.062)       # furrowed
    brow(0.05, ez + 0.145, 0.17, ez + 0.165)         # raised
    for s in (-1, 1):
        x = s * 0.195
        z = HZ - 0.07
        b.sph(0.05, (x, _fy(x, z - HZ) - 0.004, z), blush, scale=(1.0, 0.2, 0.85), seg=10, ring=6)
    # wide clenched-teeth grin: dark mouth, two rows of blocky teeth with dark gaps between them
    mz = HZ - 0.13
    my = _fy(0, mz - HZ)
    b.sph(0.15, (0, my - 0.001, mz), mat("sc_mouth", 0.5), scale=(1.0, 0.07, 0.42), seg=16, ring=8)   # flat dark opening
    tooth = mat("white", 0.35)
    for i in range(-4, 5):
        x = i * 0.027
        b.box((0.023, 0.014, 0.036), (x, _fy(x, mz + 0.022 - HZ) + 0.007, mz + 0.022), tooth, bevel=0.003, seg=1)
    for i in range(-3, 4):
        x = i * 0.027
        b.box((0.023, 0.014, 0.03), (x, _fy(x, mz - 0.024 - HZ) + 0.007, mz - 0.024), tooth, bevel=0.003, seg=1)
    b.box((0.03, 0.016, 0.058), (0.0135, _fy(0.0135, mz - HZ) + 0.010, mz - 0.002), tooth, bevel=0.004, seg=1)   # buck tooth
    return b


def part_glasses():
    b = B()
    rim = mat("sc_black", 0.4)
    ez = HZ + 0.03
    for s in (-1, 1):
        x = s * 0.118
        y = _fy(x, ez - HZ) + 0.022
        b.tube(arc(x, y, ez, 0.098, 0, 360, 20, plane="XZ"), 0.0135, rim, seg=6, caps=False)
        # temple arm running back past the head
        b.tube([(x + s * 0.098, y - 0.03, ez), (s * (HRX + 0.012), 0.05, ez), (s * (HRX + 0.008), -0.08, ez)], 0.008, rim, seg=4)
    b.tube([(-0.02, _fy(0, ez - HZ) + 0.03, ez + 0.005), (0.0, _fy(0, ez - HZ) + 0.036, ez + 0.012),
            (0.02, _fy(0, ez - HZ) + 0.03, ez + 0.005)], 0.0095, rim, seg=4)                            # bridge
    return b


def part_hat():
    """Small floppy beret-blob with a leaf sprig, sitting on top and tilted."""
    b = B()
    hat = mat("sc_hat", 0.9)
    top = HZ + HRZ - 0.035
    b.lathe([(0.0, 0), (0.115, 0.004), (0.15, 0.03), (0.125, 0.075), (0.06, 0.098), (0.0, 0.1)], (0, 0, top), hat,
            seg=18, scale=(1.0, 0.9, 1.0))
    green = mat("sc_leaf", 0.6)
    b.tube([(0.0, 0.0, top + 0.095), (0.01, 0.0, top + 0.13), (0.045, 0.0, top + 0.155)], 0.008, green, seg=5)
    for k, (dx, ang) in enumerate(((0.05, 30), (0.02, 150))):
        b.sph(0.03, (dx + 0.035, 0.0, top + 0.16 + 0.01 * k), green, scale=(1.6, 0.35, 0.8), seg=8, ring=6)
    b.tube(arc(-0.02, 0.09, top + 0.05, 0.04, 20, 200, 8, plane="XZ"), 0.005, mat("sc_shorts", 0.8), seg=4)
    return b


def build_scout(name="SCOUT", origin=(0.0, 0.0, 0.0), yaw=0.0, collection=None, tilt=8.0, turn=7.0, accessories=False):
    coll = collection or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.2
    coll.objects.link(root)
    root.location = origin
    root.rotation_euler = (0, 0, yaw)
    tris = 0
    for label, builder, lift in (("LEGS", part_legs(), 0.0), ("TORSO", part_torso(), LIFT)):
        o = builder.build("%s_%s" % (name, label), floor_normalize=False)
        coll.objects.link(o)
        o.parent = root
        o.location = (0, 0, lift)
        tris += tri_count(o)
    pivot = bpy.data.objects.new(name + "_HEAD_PIVOT", None)
    pivot.empty_display_size = 0.06
    coll.objects.link(pivot)
    pivot.parent = root
    pivot.location = (0, 0, PIVOT_Z)
    pivot.rotation_euler = (0, math.radians(tilt), math.radians(turn))        # goofy head tilt
    heads = [("HEAD", part_head()), ("FACE", part_face())]
    if accessories:                      # glasses and hat are kept for later, off by default
        heads += [("GLASSES", part_glasses()), ("HAT", part_hat())]
    for label, builder in heads:
        o = builder.build("%s_%s" % (name, label), floor_normalize=False)
        coll.objects.link(o)
        o.parent = pivot
        tris += tri_count(o)
    return root, tris
