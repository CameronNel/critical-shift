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
PIVOT_Z = 1.17 + LIFT                # neck pivot height (head sits on the neck at the top of the base body)
HZ = 0.28                            # head centre above the pivot
HRX, HRY, HRZ = 0.29, 0.268, 0.28    # head radii


def _fy(dx, dz):
    """Front surface depth of the head at horizontal offset dx and vertical offset dz from its centre."""
    v = 1.0 - (dx / HRX) ** 2 - (dz / HRZ) ** 2
    return HRY * math.sqrt(max(v, 0.04))


def part_body_base():
    """Raw skin primitives for the base body (mannequin-style: no clothes, no anatomical detail, unisex).
    These overlap on purpose: smooth_body_object() merges them into ONE blended surface, so there are no
    ball joints or steps. Built in final coordinates."""
    b = B()
    skin = mat("sc_skin", 0.8)
    # torso: soft pear/egg shell, a little narrower at the shoulders than the hips
    b.lathe([(0, 0.79), (0.13, 0.79), (0.185, 0.84), (0.215, 0.94), (0.215, 1.05), (0.20, 1.16), (0.15, 1.24),
             (0.085, 1.29), (0, 1.31)], (0, 0, 0), skin, seg=22, scale=(1.0, 0.80, 1.0))
    b.cyl(0.078, 0.14, (0, 0, 1.20), skin, r2=0.062, seg=14)                            # neck, flaring into the shoulders
    for s in (-1, 1):
        x = s * 0.095
        # leg: thick at the hip, tapering to the ankle, buried in the pelvis at the top and in the foot at the bottom
        b.tube([(x * 0.6, 0, 0.90), (x, 0, 0.78), (x * 1.05, 0.005, 0.48), (x * 1.05, 0.01, 0.06)],
               lambda u: 0.095 - 0.05 * u, skin, seg=14)
        # oven-mitten foot: one bean-shaped foot, a big toe that clearly protrudes, little toes fused into one low lobe
        xf = x * 1.05
        b.sph(1.0, (xf, 0.062, 0.052), skin, scale=(0.057, 0.096, 0.050), seg=14, ring=10)         # foot
        b.sph(1.0, (xf, 0.058, 0.022), skin, scale=(0.054, 0.086, 0.024), seg=12, ring=6)          # broader sole
        b.sph(1.0, (xf - s * 0.034, 0.170, 0.040), skin, scale=(0.033, 0.050, 0.036), seg=10, ring=8)   # big toe
        b.sph(1.0, (xf + s * 0.026, 0.142, 0.030), skin, scale=(0.032, 0.034, 0.024), seg=10, ring=8)   # fused little toes
        # arm: leaves the upper chest and flows down (no shoulder ball), thicker at the top
        b.tube([(s * 0.14, 0.0, 1.19), (s * 0.24, 0.0, 1.15), (s * 0.31, 0.015, 0.98), (s * 0.345, 0.04, 0.78),
                (s * 0.355, 0.07, 0.625)], lambda u: 0.066 - 0.031 * u, skin, seg=12)
        # oven-mitten hand: one fused palm-and-fingers mitten, plus a clearly separate thumb
        hx, hy, hz = s * 0.355, 0.075, 0.585
        b.sph(1.0, (hx, hy, hz), skin, scale=(0.040, 0.058, 0.056), seg=14, ring=10)                 # palm
        b.sph(1.0, (hx - s * 0.003, hy + 0.008, hz - 0.040), skin, scale=(0.038, 0.060, 0.062), seg=14, ring=10)  # fused fingers
        tb = Vector((hx - s * 0.026, hy + 0.034, hz + 0.014))
        tp = [tb, tb + Vector((-s * 0.010, 0.036, -0.004)), tb + Vector((-s * 0.014, 0.060, -0.030))]
        b.tube(tp, lambda u: 0.030 - 0.007 * u, skin, seg=10, caps=True)     # closed: the remesh needs solid volumes
        b.sph(0.024, tp[-1], skin, seg=10, ring=7)                                                   # thumb
    return b


def smooth_body_object(name, target_tris=3400, voxel=0.0075, builder=None):
    """Merge the overlapping primitives into one continuous surface: voxel remesh, smooth, then decimate."""
    scene = bpy.context.scene
    obj = (builder or part_body_base)().build(name, floor_normalize=False)
    scene.collection.objects.link(obj)

    def bake(obj):
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        old = obj.data
        obj.modifiers.clear()
        obj.data = me
        if old.users == 0:
            bpy.data.meshes.remove(old)
        return me

    md = obj.modifiers.new("cs_remesh", "REMESH")
    md.mode = "VOXEL"
    md.voxel_size = voxel
    md.adaptivity = 0.0
    md = obj.modifiers.new("cs_smooth", "LAPLACIANSMOOTH")
    md.iterations = 6
    md.lambda_factor = 0.55
    md.use_volume_preserve = True
    me = bake(obj)
    me.calc_loop_triangles()
    current = max(len(me.loop_triangles), 1)
    md = obj.modifiers.new("cs_decimate", "DECIMATE")
    md.decimate_type = "COLLAPSE"
    md.ratio = min(1.0, target_tris / current)
    md2 = obj.modifiers.new("cs_smooth2", "LAPLACIANSMOOTH")           # relax the decimation facets
    md2.iterations = 4
    md2.lambda_factor = 0.45
    md2.use_volume_preserve = True
    me = bake(obj)
    me.shade_smooth()
    return obj


def part_jeans_shoes():
    """OUTFIT LAYER (off by default): straight-leg jeans with a cuff, plus brown shoes."""
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
        b.cyl(0.098, 0.72, (x * 1.02, 0.0, 0.135), denim, r2=0.122, seg=16)
        b.tube([(x * 1.02, 0.0, 0.135), (x * 1.02, 0.0, 0.16)], 0.106, denim_lt, seg=16)
        b.tube([(x * 1.02, 0.0, 0.16), (x * 1.02, 0.0, 0.165)], 0.100, denim_dk, seg=16)
        ox = x * 1.02 + s * 0.108
        b.tube([(ox, 0.0, 0.18), (ox + s * 0.006, 0.0, 0.5), (ox + s * 0.012, 0.0, 0.84)], 0.0032, stitch, seg=4)
    b.box((0.31, 0.225, 0.11), (0, 0, 0.80), denim, bevel=0.03, seg=2)
    b.tube([(0.16 * math.cos(a), 0.118 * math.sin(a), 0.855) for a in [i * 2 * math.pi / 20 for i in range(21)]],
           0.014, denim_dk, seg=5, caps=False)
    b.sph(0.013, (0.0, 0.122, 0.855), mat("brass", 0.3, 0.9), scale=(1.0, 0.5, 1.0), seg=8, ring=5)
    for s in (-1, 1):
        b.box((0.075, 0.01, 0.075), (s * 0.075, -0.12, 0.79), denim_dk, bevel=0.004, seg=1)
    return b


def part_tee():
    """OUTFIT LAYER (off by default): plain crew-neck t-shirt with short sleeves. Built low, raised by LIFT."""
    b = B()
    tee = mat("sc_tee", 0.92)
    tee_dk = mat("sc_tee_dk", 0.92)
    for s in (-1, 1):
        sx = s * 0.285
        b.tube([(sx - s * 0.02, 0.0, 1.08), (sx + s * 0.02, 0.005, 0.99)], 0.088, tee, seg=12)
        b.tube([(sx + s * 0.022, 0.006, 0.985), (sx + s * 0.026, 0.008, 0.968)], 0.091, tee_dk, seg=12)
    b.box((0.50, 0.30, 0.44), (0, 0, 0.935), tee, bevel=0.03, seg=2)
    b.box((0.51, 0.31, 0.04), (0, 0, 0.745), tee, bevel=0.015, seg=2)
    b.tube([(0.105 * math.cos(a), 0.085 * math.sin(a), 1.152) for a in [i * 2 * math.pi / 18 for i in range(19)]],
           0.026, tee_dk, seg=6, caps=False)
    return b


def part_head():
    """Big round head (local frame: pivot at the neck, head centre at z = HZ)."""
    b = B()
    b.sph(1.0, (0, 0, HZ), mat("sc_skin", 0.8), scale=(HRX, HRY, HRZ), seg=22, ring=14)
    return b


def part_face_goofy():
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


def part_face(style="neutral"):
    """Default: two round matching eyes, no eyebrows, a plain black-line smile. style='goofy' keeps the old face."""
    if style == "goofy":
        return part_face_goofy()
    b = B()
    ink = mat("sc_black", 0.35)
    white = mat("white", 0.3)
    iris = mat("sc_iris", 0.25)
    ez = HZ + 0.02
    for s in (-1, 1):
        x = s * 0.112
        y = _fy(x, ez - HZ) - 0.004
        b.sph(0.066, (x, y, ez), white, scale=(1.0, 0.45, 1.0), seg=16, ring=10)
        b.sph(0.048, (x, y + 0.014, ez), iris, scale=(1.0, 0.4, 1.0), seg=14, ring=8)
        b.sph(0.022, (x, y + 0.024, ez), ink, scale=(1.0, 0.4, 1.0), seg=10, ring=6)
        b.sph(0.011, (x + s * 0.014, y + 0.03, ez + 0.02), white, scale=(1.0, 0.4, 1.0), seg=6, ring=4)
    mz = HZ - 0.115
    pts = []
    for i in range(-4, 5):
        x = i * 0.016
        u = x / 0.064
        z = mz + 0.02 * u * u - 0.008
        pts.append((x, _fy(x, z - HZ) + 0.004, z))
    b.tube(pts, 0.0065, ink, seg=5)
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


def build_scout(name="SCOUT", origin=(0.0, 0.0, 0.0), yaw=0.0, collection=None, tilt=0.0, turn=0.0,
                clothes=False, accessories=False, face="neutral"):
    """Default is the nude, featureless base body with the neutral face; clothes/accessories are opt-in layers."""
    coll = collection or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.2
    coll.objects.link(root)
    root.location = origin
    root.rotation_euler = (0, 0, yaw)
    tris = 0
    body = smooth_body_object("%s_BODY" % name)
    if body.name not in coll.objects:
        coll.objects.link(body)
    if coll is not bpy.context.scene.collection and body.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(body)
    body.parent = root
    tris += tri_count(body)
    if clothes:
        for label, builder, lift in (("JEANS_SHOES", part_jeans_shoes(), 0.0), ("TEE", part_tee(), LIFT)):
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
    pivot.rotation_euler = (0, math.radians(tilt), math.radians(turn))
    heads = [("HEAD", part_head()), ("FACE", part_face(face))]
    if accessories:
        heads += [("GLASSES", part_glasses()), ("HAT", part_hat())]
    for label, builder in heads:
        o = builder.build("%s_%s" % (name, label), floor_normalize=False)
        coll.objects.link(o)
        o.parent = pivot
        tris += tri_count(o)
    return root, tris
