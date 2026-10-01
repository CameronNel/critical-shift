#!/usr/bin/env python3
"""
Hero suit library file: the crew worker's own hazmat suit, as one linkable collection (Blender 5.2).

    blender -b --factory-startup -P build_hero_suit.py -- <hero_suit.blend>

This is the single source of the suit that is placed in the spawn-room lockers (module.blend links the collection
`HERO_SUIT` from this file; edit and re-save this file and every placed suit follows). It is built exactly as the player
character wears it: character_worker.build_worker + character_suit.build_hazmat + equip, default colours, A-pose rest. Only
the wearer is left out (skin regions, head and face), because the suit hangs empty in a locker. Nothing in the suit is
modified after the build.

Measurements the placing script needs (suit frame: feet near z = 0, +y forward) are stored as custom properties on the
collection: cs_top_z, cs_pack_back_y, cs_foot_zmin, cs_sole_x0/x1/y0/y1 (boot footprint), cs_neck_cx/cy/r/z0/z1.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1]
NAME = "HERO_SUIT"

# Existing lockers place the suit from these three library anchors. Preserve
# their coordinates while rebuilding the design, so editing the library alone
# does not lift the boots off their docks or move the pack off the back panel.
placement = None
if os.path.isfile(OUT):
    with bpy.data.libraries.load(OUT, link=False) as (_src, _dst):
        _dst.collections = [NAME]
    previous = _dst.collections[0]
    placement = {k: float(previous[k]) for k in ("cs_top_z", "cs_pack_back_y", "cs_foot_zmin")}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.system.audio_device = "None"
root, _tris = CW.build_worker(name=NAME, collection=bpy.context.scene.collection)
CS.build_hazmat(root, coll=bpy.context.scene.collection)
CS.equip(root)
for o in list(root.children_recursive):                    # no wearer: skin regions, head, face
    if o.name not in bpy.data.objects:
        continue
    if (o.name.startswith(NAME + "_BODY_") or o.name == NAME + "_HEAD" or o.name.startswith("FACE_")):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()

meshes = [o for o in root.children_recursive if o.type == "MESH" and not o.hide_render]
if placement:
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    raw_top, raw_min = max(p.z for p in pts), min(p.z for p in pts)
    scale_z = (placement["cs_top_z"] - placement["cs_foot_zmin"]) / (raw_top - raw_min)
    root.scale.z = scale_z
    root.location.z = placement["cs_foot_zmin"] - raw_min * scale_z
    raw_pack = min((o.matrix_world @ v.co).y for o in meshes if o.name.startswith("SUIT_KIT") for v in o.data.vertices)
    root.location.y = placement["cs_pack_back_y"] - raw_pack
    root["cs_library_placement_scale_z"] = scale_z
    root["cs_library_placement_offset_z"] = root.location.z
    root["cs_library_placement_offset_y"] = root.location.y
    bpy.context.view_layer.update()
top = max((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
body = next(o for o in meshes if o.name.startswith("SUIT_BODY"))
boots = [o for o in meshes if o.name.startswith(("SUIT_BOOTS", "SUIT_KIT"))]
pts = [o.matrix_world @ v.co for o in boots for v in o.data.vertices]
fz = min(p.z for p in pts)
sole = [p for p in pts if p.z < fz + 0.02]
kit = next(o for o in meshes if o.name.startswith("SUIT_KIT"))
pack_back = min((kit.matrix_world @ v.co).y for v in kit.data.vertices)
neck = [body.matrix_world @ v.co for v in body.data.vertices if (body.matrix_world @ v.co).z > 1.25]
ncx = sum(p.x for p in neck) / len(neck)
ncy = sum(p.y for p in neck) / len(neck)
nr = max(math.hypot(p.x - ncx, p.y - ncy) for p in neck)

coll = bpy.data.collections.new(NAME)
bpy.context.scene.collection.children.link(coll)
for o in [root] + list(root.children_recursive):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)
coll["cs_top_z"] = top
coll["cs_pack_back_y"] = pack_back
coll["cs_foot_zmin"] = fz
coll["cs_sole_x0"], coll["cs_sole_x1"] = min(p.x for p in sole), max(p.x for p in sole)
coll["cs_sole_y0"], coll["cs_sole_y1"] = min(p.y for p in sole), max(p.y for p in sole)
coll["cs_neck_cx"], coll["cs_neck_cy"], coll["cs_neck_r"] = ncx, ncy, nr
coll["cs_neck_z0"], coll["cs_neck_z1"] = 1.20, max(p.z for p in neck)
coll["cs_suit_style"] = root.get("cs_suit_style", "legacy")
coll["cs_suit_reference"] = root.get("cs_suit_reference", "Original worker suit")
if placement:
    for k, value in placement.items():
        if abs(coll[k] - value) > 0.00001:
            raise RuntimeError("Hero suit placement anchor changed: " + k)
    coll["cs_placement_preserved"] = True
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("HERO_SUIT saved", OUT, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in coll.items()})
