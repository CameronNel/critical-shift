#!/usr/bin/env python3
"""
Locker LOD of the hero suit (Blender 5.2): decimate the HERO_SUIT library to a triangle budget.

    blender -b --factory-startup -P lod_hero_suit.py -- <hero_suit.blend> [--full-copy <hero_suit_full.blend>]

Run after build_hero_suit.py. It refuses a library that is already the locker LOD (rebuild with build_hero_suit.py first), so a retry cannot decimate twice. The library the four spawn lockers link is a background prop seen from a few metres, so the
authoring-detail suit (about 114,000 triangles) is reduced here object by object (Decimate collapse, solidify applied first,
smooth shading and every material kept). The full-detail suit stays available in the wearable scene
(crew_hazmat_reference.blend) and can be rebuilt with build_hero_suit.py. Measurements stored on the collection are
unchanged; the collection records `cs_lod = "locker"` and the triangle counts before and after.
"""
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
PATH = args[0]
FULL = args[args.index("--full-copy") + 1] if "--full-copy" in args else None

# object name prefix -> collapse ratio (None = leave as is). Ratios were chosen by eye against renders at locker distance.
RATIOS = {
    "SUIT_BODY": 0.20, "SUIT_KIT": 0.15, "SUIT_HOOD_KIT": 0.15, "SUIT_HOOD": 0.22, "SUIT_BOOTS": 0.25,
    "SUIT_GLOVES": 0.35, "SUIT_VISOR": 0.20, "SUIT_COLLAR": 0.30, "SUIT_LABEL_SHOULDER_STITCH": 0.25,
    "SUIT_LABEL_BIOHAZARD_CHEST": 0.30,
}


def tri_count(o):
    dg = bpy.context.evaluated_depsgraph_get()
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    n = sum(len(p.vertices) - 2 for p in m.polygons)
    e.to_mesh_clear()
    return n


bpy.ops.wm.open_mainfile(filepath=PATH)
if FULL:
    bpy.ops.wm.save_as_mainfile(filepath=FULL, copy=True)
col = bpy.data.collections["HERO_SUIT"]
if col.get("cs_lod") == "locker":
    # decimating again would degrade the delivered locker mesh and overwrite the recorded full-detail count
    raise SystemExit("lod_hero_suit.py: %s is already the locker LOD (cs_lod = locker); rebuild the full-detail suit with build_hero_suit.py first" % PATH)
before = after = 0
for o in list(col.all_objects):
    if o.type != "MESH":
        continue
    before += tri_count(o)
    ratio = next((r for k, r in sorted(RATIOS.items(), key=lambda kv: -len(kv[0])) if o.name.startswith(k)), None)
    for x in bpy.context.view_layer.objects:
        x.select_set(False)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    for m in list(o.modifiers):                       # solidify etc. become real geometry first
        bpy.ops.object.modifier_apply(modifier=m.name)
    if ratio:
        d = o.modifiers.new("LOD", "DECIMATE")
        d.decimate_type = "COLLAPSE"
        d.ratio = ratio
        d.use_collapse_triangulate = False
        bpy.ops.object.modifier_apply(modifier=d.name)
    for p in o.data.polygons:
        p.use_smooth = True
    after += tri_count(o)
col["cs_lod"] = "locker"
col["cs_tris_full"], col["cs_tris_lod"] = before, after
bpy.ops.wm.save_as_mainfile(filepath=PATH)
print("LOD", before, "->", after)
