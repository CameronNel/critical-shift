#!/usr/bin/env python3
"""
Hand tools for the crew worker (Blender 5.2 / bpy): a shovel and a pickaxe, low-poly, stylised to match the suit.

Each tool is authored with its origin at the right-hand grip and its shaft along +Z, so a hold animation can place it
with one matrix. `GRIP_LEFT` is where the second hand grips, in the same local frame. The rig skins each tool rigidly to
the `Tool` bone (see character_rig.add_tools) and keys that bone per animation.
"""

import math

import bmesh
import bpy

from cozy_geo import B, mat

GRIP_LEFT = {"SHOVEL": (0.0, 0.0, 0.22), "PICKAXE": (0.0, 0.0, 0.34)}


def _shovel():
    """Origin at the right-hand grip; shaft along +Z; handle top at +0.30, blade bottom at -0.86 (1.16 m overall)."""
    b = B()
    wood, steel = mat("oak", 0.8), mat("charcoal", 0.4, 0.75)
    b.cyl(0.019, 0.83, (0, 0, -0.55), wood, seg=10)                          # shaft
    b.cyl(0.026, 0.09, (0, 0, -0.58), steel, r2=0.02, seg=10)                # ferrule
    b.tube([(-0.09 + 0.09 * (1 - math.cos(a)), 0.0, 0.255 + 0.055 * math.sin(a)) for a in [math.pi * i / 12 for i in range(13)]],
           0.014, wood, seg=6)                                                # D-handle
    b.box((0.21, 0.014, 0.30), (0, 0.0, -0.66), steel, bevel=0.006, seg=2)     # blade
    b.box((0.15, 0.012, 0.12), (0, 0.0, -0.80), steel, bevel=0.005, seg=1, taper_top=0.35)
    b.box((0.10, 0.022, 0.05), (0, 0.0, -0.53), steel, bevel=0.005, seg=1)      # socket
    return b


def _pickaxe():
    b = B()
    wood, steel = mat("oak", 0.8), mat("charcoal", 0.4, 0.75)
    b.cyl(0.021, 0.96, (0, 0, -0.22), wood, seg=10)                          # handle
    b.sph(0.03, (0, 0, -0.22), wood, seg=8, ring=6)                          # knob
    b.box((0.075, 0.055, 0.11), (0, 0, 0.74), steel, bevel=0.008, seg=1)     # head collar
    tip = []
    for i in range(13):
        x = -0.30 + 0.60 * i / 12
        tip.append((x, 0.0, 0.76 - 0.14 * (x / 0.30) ** 2))
    b.tube(tip, lambda u: 0.006 + 0.026 * (1 - abs(2 * u - 1) ** 1.6), steel, seg=8)
    return b


def build_tool(kind, coll=None, name=None):
    """Build 'SHOVEL' or 'PICKAXE'. Returns the object (origin at the right-hand grip, shaft along +Z)."""
    coll = coll or bpy.context.scene.collection
    b = _shovel() if kind == "SHOVEL" else _pickaxe()
    o = b.build(name or ("TOOL_" + kind), floor_normalize=False)
    coll.objects.link(o)
    o["cs_tool"] = kind
    return o
