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

H_SCALE = 0.90                        # head scale relative to the Scout head
HEAD_CENTRE_Z = 1.295                 # world height of the head centre (raised a touch so a slim neck shows)
PIVOT_Z = HEAD_CENTRE_Z - SC.HZ * H_SCALE


def part_worker_raw():
    """Overlapping closed primitives for the merged body. Final coordinates, feet at z = 0, +y forward."""
    b = B()
    skin = mat("sc_skin", 0.8)
    # wide egg torso; the top tucks into the head so there is almost no neck
    b.lathe([(0, 0.55), (0.14, 0.55), (0.22, 0.60), (0.27, 0.72), (0.285, 0.84), (0.255, 0.95), (0.19, 1.00),
             (0.12, 1.035), (0.075, 1.07), (0, 1.09)], (0, 0, 0), skin, seg=24, scale=(1.0, 0.86, 1.0))
    b.cyl(0.062, 0.14, (0, 0, 1.00), skin, seg=14)                                   # slim neck, tucked into the head
    for s in (-1, 1):
        x = s * 0.11
        # short, thick legs
        b.tube([(x * 0.7, 0, 0.68), (x, 0, 0.52), (x * 1.05, 0.01, 0.28), (x * 1.05, 0.015, 0.10)],
               lambda u: 0.098 - 0.038 * u, skin, seg=14)
        # chunky foot: big bean, a big toe that protrudes, little toes fused into a lower lobe
        xf = x * 1.05
        b.sph(1.0, (xf, 0.080, 0.064), skin, scale=(0.076, 0.136, 0.066), seg=14, ring=10)
        b.sph(1.0, (xf, 0.074, 0.028), skin, scale=(0.072, 0.120, 0.030), seg=12, ring=6)
        b.sph(1.0, (xf - s * 0.042, 0.208, 0.050), skin, scale=(0.042, 0.062, 0.046), seg=10, ring=8)
        b.sph(1.0, (xf + s * 0.036, 0.174, 0.037), skin, scale=(0.042, 0.044, 0.032), seg=10, ring=8)
        # thick arm flowing out of the upper chest (starts inside the torso, no shoulder corner) and tapering to the wrist
        b.tube([(s * 0.15, 0.0, 0.94), (s * 0.255, 0.0, 0.915), (s * 0.335, 0.02, 0.79), (s * 0.37, 0.05, 0.62),
                (s * 0.385, 0.07, 0.52)], lambda u: 0.078 - 0.034 * u, skin, seg=12)
        # big oven-mitten hand: fused fingers plus a distinct, chunky thumb
        hx, hy, hz = s * 0.385, 0.078, 0.462
        b.sph(1.0, (hx, hy, hz), skin, scale=(0.055, 0.076, 0.074), seg=14, ring=10)
        b.sph(1.0, (hx - s * 0.003, hy + 0.010, hz - 0.056), skin, scale=(0.050, 0.076, 0.084), seg=14, ring=10)
        tb = Vector((hx - s * 0.036, hy + 0.044, hz + 0.016))
        tp = [tb, tb + Vector((-s * 0.012, 0.048, -0.005)), tb + Vector((-s * 0.017, 0.078, -0.038))]
        b.tube(tp, lambda u: 0.039 - 0.009 * u, skin, seg=10, caps=True)      # closed: the remesh needs solid volumes
        b.sph(0.031, tp[-1], skin, seg=10, ring=7)
    return b


def build_worker(name="WORKER", origin=(0.0, 0.0, 0.0), yaw=0.0, collection=None, face="neutral", accessories=False):
    scene = bpy.context.scene
    coll = collection or scene.collection
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.2
    coll.objects.link(root)
    root.location = origin
    root.rotation_euler = (0, 0, yaw)
    tris = 0
    body = SC.smooth_body_object("%s_BODY" % name, target_tris=3100, voxel=0.0085, builder=part_worker_raw)
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
    parts = [("HEAD", SC.part_head()), ("FACE", SC.part_face(face))]
    if accessories:
        parts += [("GLASSES", SC.part_glasses()), ("HAT", SC.part_hat())]
    for label, builder in parts:
        o = builder.build("%s_%s" % (name, label), floor_normalize=False)
        coll.objects.link(o)
        o.parent = pivot
        tris += tri_count(o)
    return root, tris
