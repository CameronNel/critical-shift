#!/usr/bin/env python3
"""
"Crew worker": the game's player character (Blender 5.2 / bpy). Original design, shaped from the Scout base.

Design intent (Critical Shift: four players in one room, suits layered on top later):
  * readable silhouette at distance: wide egg torso, short thick legs, big round head, short neck;
  * a simple solid volume for the hazmat suit, gloves and boots to sit on;
  * big mitten hands and chunky feet, because grabbing, carrying and walking are the game's readable actions;
  * about 1.5 m tall so it fits the facility's door and room scale; neutral face by default.

The body is one blended surface (overlapping closed primitives -> voxel remesh -> smooth -> decimate). The head and
face reuse the Scout's parts, scaled, on a neck pivot so faces/hats/accessories stay swappable.
"""

import math

import bpy
from mathutils import Vector

import character_scout as SC
from cozy_geo import B, mat, tri_count

BODY_TRIS = 5200                      # refined: enough triangles to keep curves smooth and silhouettes round
H_SCALE = 0.94                        # head kept close to the previous size (slightly trimmed so the taller body reads ~3.1 heads)
LEG_DROP = -0.11                      # negative: the hips sit higher (0.66 m) so the legs are ~35% longer
TORSO_SQUASH = 1.05                   # torso a little taller than the source profile
HEAD_CENTRE_Z = 1.38
PIVOT_Z = HEAD_CENTRE_Z - SC.HZ * H_SCALE


def T(z):
    """Map a source torso height (0.55 = hip line) onto the shorter, squashed torso."""
    return (0.55 - LEG_DROP) + (z - 0.55) * TORSO_SQUASH


def spline(points, n=18):
    """Uniform Catmull-Rom curve through the control points, sampled n times (smooth limb centre-lines)."""
    pts = [Vector(p) for p in points]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    segs = len(pts) - 1
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        f = u - k
        p0, p1, p2, p3 = ext[k], ext[k + 1], ext[k + 2], ext[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3))
    return out


def bump(u, centre, width, amount):
    return amount * math.exp(-((u - centre) / width) ** 2)


def part_worker_raw():
    """Overlapping closed primitives for the merged body. Final coordinates, feet at z = 0, +y forward.
    Pear/bean silhouette: narrow shoulders, wide low belly, a soft blended hip, stubby arms, big flat-soled feet."""
    b = B()
    skin = mat("sc_skin", 0.8)
    prof = [(0, 0.55), (0.17, 0.55), (0.25, 0.60), (0.30, 0.70), (0.297, 0.80), (0.245, 0.90), (0.18, 0.96),
            (0.115, 1.00), (0.075, 1.04), (0, 1.06)]
    b.lathe([(r * 0.90, T(z)) for r, z in prof], (0, 0, 0), skin, seg=24, scale=(1.0, 0.86, 1.0))
    b.cyl(0.085, 0.20, (0, 0, T(1.0) - 0.02), skin, seg=16)                                 # slim neck, tucked into the head
    # soft hip mass so the legs grow out of the belly instead of being attached to it
    b.sph(1.0, (0, 0.0, T(0.54)), skin, scale=(0.225, 0.185, 0.145), seg=18, ring=10)
    zs = T(0.94)                                                                      # shoulder height
    # soft shoulder yoke: fills the dip between the head and the shoulders so the neckline flows
    b.sph(1.0, (0, 0.0, zs + 0.05), skin, scale=(0.19, 0.125, 0.085), seg=18, ring=10)
    for s in (-1, 1):
        x = s * 0.098
        leg = spline([(x * 0.70, 0, 0.80), (x * 0.95, 0, 0.64), (x * 1.04, 0.006, 0.44), (x * 1.06, 0.012, 0.25),
                      (x * 1.06, 0.016, 0.11)])
        b.tube([tuple(p) for p in leg],
               lambda u: 0.108 - 0.040 * u + bump(u, 0.55, 0.20, 0.010) - bump(u, 0.95, 0.10, 0.006), skin, seg=18)
        # big toeless foot with a flatter sole
        xf = x * 1.06
        b.sph(1.0, (xf, 0.088, 0.088), skin, scale=(0.098, 0.168, 0.074), seg=14, ring=10)
        b.sph(1.0, (xf, 0.084, 0.028), skin, scale=(0.094, 0.152, 0.028), seg=12, ring=6)
        # small, soft buttcheeks
        b.sph(1.0, (s * 0.088, -0.142, T(0.575)), skin, scale=(0.088, 0.084, 0.098), seg=14, ring=10)
        # short thick arm out of the narrow shoulder
        arm = spline([(s * 0.13, 0.0, zs), (s * 0.22, 0.0, zs - 0.022), (s * 0.29, 0.015, zs - 0.138),
                      (s * 0.325, 0.04, zs - 0.288), (s * 0.345, 0.065, zs - 0.385)])
        b.tube([tuple(p) for p in arm], lambda u: 0.094 - 0.040 * u + bump(u, 0.15, 0.12, 0.006) - bump(u, 0.95, 0.08, 0.004),
               skin, seg=16)
        # bigger oven-mitten hand with a short, tucked thumb
        hx, hy, hz = s * 0.345, 0.075, zs - 0.455
        b.sph(1.0, (hx, hy, hz), skin, scale=(0.068, 0.092, 0.092), seg=14, ring=10)
        b.sph(1.0, (hx - s * 0.003, hy + 0.012, hz - 0.066), skin, scale=(0.062, 0.092, 0.100), seg=14, ring=10)
        tb = Vector((hx - s * 0.048, hy + 0.036, hz + 0.018))
        tp = [tb, tb + Vector((-s * 0.007, 0.030, -0.014)), tb + Vector((-s * 0.010, 0.046, -0.034))]
        b.tube(tp, lambda u: 0.043 - 0.007 * u, skin, seg=10, caps=True)
        b.sph(0.036, tp[-1], skin, seg=10, ring=7)
    return b


def part_worker_face():
    """Minimal face: larger, slightly closer, deeper (protruding) round eyes, no brows, no nose, tiny black smile."""
    b = B()
    ink = mat("sc_black", 0.35)
    white = mat("white", 0.3)
    iris = mat("sc_iris", 0.25)
    ez = SC.HZ + 0.02
    for s in (-1, 1):
        x = s * 0.098
        y = SC._fy(x, ez - SC.HZ) - 0.002
        b.sph(0.078, (x, y, ez), white, scale=(1.0, 0.62, 1.0), seg=SC.EYE_SEG[0], ring=SC.EYE_SEG[1])
        b.sph(0.057, (x, y + 0.032, ez), iris, scale=(1.0, 0.5, 1.0), seg=SC.EYE_SEG[0], ring=SC.EYE_SEG[1])
        b.sph(0.026, (x, y + 0.046, ez), ink, scale=(1.0, 0.5, 1.0), seg=16, ring=8)
        b.sph(0.013, (x + s * 0.016, y + 0.056, ez + 0.022), white, scale=(1.0, 0.5, 1.0), seg=8, ring=6)
    mz = SC.HZ - 0.115
    pts = []
    for i in range(-4, 5):
        x = i * 0.016
        z = mz + 0.02 * (x / 0.064) ** 2 - 0.008
        pts.append((x, SC._fy(x, z - SC.HZ) + 0.004, z))
    b.tube(pts, 0.0065, ink, seg=5)
    return b


def build_worker(name="WORKER", origin=(0.0, 0.0, 0.0), yaw=0.0, collection=None, face="neutral", accessories=False,
                 eyes="round", mouth="smile", regions=True):
    scene = bpy.context.scene
    coll = collection or scene.collection
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.2
    coll.objects.link(root)
    root.location = origin
    root.rotation_euler = (0, 0, yaw)
    tris = 0
    body = SC.smooth_body_object("%s_BODY" % name, target_tris=BODY_TRIS, voxel=0.0055, builder=part_worker_raw,
                                 smooth1=9, smooth2=3, quad=True)
    if regions:
        import character_regions as CR
        for o in CR.split_body(body, coll, name).values():
            o.parent = root
            tris += tri_count(o)
        bpy.data.objects.remove(body, do_unlink=True)
    else:
        if body.name not in coll.objects:
            coll.objects.link(body)
        if coll is not scene.collection and body.name in scene.collection.objects:
            scene.collection.objects.unlink(body)
        body.parent = root
        tris += tri_count(body)
    pivot = bpy.data.objects.new(name + "_HEAD_PIVOT", None)
    pivot.empty_display_size = 0.06
    coll.objects.link(pivot)
    pivot.parent = root
    pivot.location = (0, 0, PIVOT_Z)
    pivot.scale = (H_SCALE, H_SCALE, H_SCALE)
    SC.EYE_SEG = (20, 12)
    flat_face = face == "neutral"
    parts = [("HEAD", SC.part_head(seg=32, ring=22))]
    if not flat_face:
        parts.append(("FACE", SC.part_face(face) if face != "3d" else part_worker_face()))
    if accessories:
        parts += [("GLASSES", SC.part_glasses()), ("HAT", SC.part_hat())]
    for label, builder in parts:
        o = builder.build("%s_%s" % (name, label), floor_normalize=False)
        coll.objects.link(o)
        o.parent = pivot
        tris += tri_count(o)
    if flat_face:
        import character_face as CF
        _, _, ft = CF.build_face(coll, pivot, eyes=eyes, mouth=mouth)
        tris += ft
    return root, tris
