"""Geometry/material/identity signature of a spawn-room module, to prove an optimised derivative did not change it.
    blender -b --factory-startup -P signature.py -- <module.blend> <signature.json>
Palette materials are decoded back to the original material name through the OPT_PALETTE text block.
"""
import collections
import json
import sys

import bpy
from mathutils import Vector

GEO = ("MESH", "CURVE", "FONT", "SURFACE")


def props(o):
    return {k: o[k] for k in o.keys() if not k.startswith("_") and k != "cycles" and not k.startswith("cs_merged")}


def jsonable(v):
    try:
        json.dumps(v)
        return v
    except TypeError:
        try:
            return [jsonable(x) for x in v]
        except TypeError:
            return str(v)


def digest(x):
    import hashlib
    return hashlib.md5(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:12]


SKIP_PROPS = {"rna_type", "bl_rna", "id_data", "original", "users", "session_uid", "is_evaluated", "tag", "is_runtime_data",
              "is_missing", "library", "library_weak_reference", "override_library", "asset_data", "preview",
              "name_full", "is_embedded_data", "use_extra_user", "is_library_indirect", "is_editable"}


def rna_deep(x, depth=0, seen=None):
    """Stable, JSON-able dump of an RNA struct: every plain property, every nested struct and every collection, to a fixed
    depth. Pointers to other datablocks are recorded by name, except Actions, which are dumped in full (an NLA strip's
    action, a driver-less owner's action). Selection state is skipped: it is editor state, not motion."""
    if seen is None:
        seen = set()
    if depth > 9:
        return "<depth>"
    try:
        key = x.as_pointer()
    except Exception:
        key = None
    if key is not None:
        if (key, type(x).__name__) in seen:
            return "<seen>"
        seen = seen | {(key, type(x).__name__)}
    out = {}
    for prop in x.bl_rna.properties:
        ident = prop.identifier
        if ident in SKIP_PROPS or ident.startswith("select") or ident.startswith("is_selected"):
            continue
        try:
            v = getattr(x, ident)
        except Exception:
            continue
        if prop.type in ("BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"):
            if hasattr(v, "__len__") and not isinstance(v, str):
                v = [round(e, 5) if isinstance(e, float) else e for e in v]
            elif isinstance(v, float):
                v = round(v, 5)
            elif isinstance(v, set):
                v = sorted(v)
            out[ident] = v
        elif prop.type == "POINTER":
            if v is None:
                out[ident] = None
            elif isinstance(v, bpy.types.ID):
                out[ident] = rna_deep(v, depth + 1, seen) if isinstance(v, bpy.types.Action) else "%s:%s" % (type(v).__name__, v.name)
            else:
                out[ident] = rna_deep(v, depth + 1, seen)
        elif prop.type == "COLLECTION":
            items = []
            for it in v:
                if isinstance(it, bpy.types.ID):
                    items.append(rna_deep(it, depth + 1, seen) if isinstance(it, bpy.types.Action) else "%s:%s" % (type(it).__name__, it.name))
                else:
                    items.append(rna_deep(it, depth + 1, seen))
            out[ident] = items
    return out


def animation_entry(coll_name, idb, ad, owner_kind="id"):
    """[collection, name, action name, digest of the whole animation data (owner settings, action with all layers, slots,
    F-curves, keyframes, modifiers; drivers; NLA tracks and strips with the actions they play)]"""
    return [coll_name, owner_kind, idb.name, ad.action.name if ad.action else None, digest(rna_deep(ad))]


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    bpy.ops.wm.open_mainfile(filepath=a[0])
    sc = bpy.context.scene
    pal = None
    if "OPT_PALETTE" in bpy.data.texts:
        cells = json.loads(bpy.data.texts["OPT_PALETTE"].as_string())
        grid = cells["grid"]
        pal = {c: n for n, c in cells["cells"].items()}
    family_map = {}
    if "OPT_FAMILIES" in bpy.data.texts:
        for fam, members in json.loads(bpy.data.texts["OPT_FAMILIES"].as_string()).items():
            for m in members:
                family_map[m] = fam
    dg = bpy.context.evaluated_depsgraph_get()
    area = collections.Counter()
    vset = set()
    vlist = []
    tris = 0
    lo = [1e9] * 3
    hi = [-1e9] * 3
    asset_box = {}
    for o in sc.objects:
        if o.type not in GEO or o.hide_render:
            continue
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        mw = o.matrix_world
        uvl = m.uv_layers.get("CS_PAL")
        mats = [family_map.get(s.material.name.replace("__noattr", ""), s.material.name.replace("__noattr", ""))
                if s.material else "" for s in o.material_slots]
        asset = o.parent
        while asset and not props(asset):
            asset = asset.parent
        key = asset.name if asset else "-"
        box = asset_box.setdefault(key, [[1e9] * 3, [-1e9] * 3])
        for v in m.vertices:
            w = mw @ v.co
            vset.add((round(w.x, 3), round(w.y, 3), round(w.z, 3)))
            vlist.append((w.x, w.y, w.z))
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
                box[0][i] = min(box[0][i], w[i])
                box[1][i] = max(box[1][i], w[i])
        for p in m.polygons:
            pts = [mw @ m.vertices[i].co for i in p.vertices]
            ar = 0.0
            for i in range(1, len(pts) - 1):
                ar += ((pts[i] - pts[0]).cross(pts[i + 1] - pts[0])).length * 0.5
            name = mats[p.material_index] if p.material_index < len(mats) else ""
            if name == "PAL_flat" and uvl is not None and pal is not None:
                u, v = uvl.uv[p.loop_start].vector
                c = int(v * grid) * grid + int(u * grid)
                name = pal.get(c, "PAL?%d" % c)
            area[name] += ar
            tris += len(p.vertices) - 2
        e.to_mesh_clear()
    ids = {}
    for o in sc.objects:
        pr = props(o)
        if pr or o.type == "EMPTY":
            ids[o.name] = {"type": o.type, "props": jsonable(pr), "parent": o.parent.name if o.parent else None,
                           "matrix": [round(x, 5) for r in o.matrix_world for x in r]}
    animation = []
    for coll_name in ("objects", "materials", "meshes", "curves", "lights", "cameras", "worlds", "node_groups", "shape_keys"):
        for idb in getattr(bpy.data, coll_name):
            for owner_kind, owner in (("id", idb), ("node_tree", getattr(idb, "node_tree", None))):
                ad = getattr(owner, "animation_data", None) if owner is not None else None
                if ad and (ad.action or ad.drivers or ad.nla_tracks):
                    animation.append(animation_entry(coll_name, idb, ad, owner_kind))
    lights = {o.name: [round(o.data.energy, 3), o.get("cs_rt_role")] for o in sc.objects if o.type == "LIGHT"}
    import hashlib
    vh = hashlib.md5(repr(sorted(vset)).encode()).hexdigest()
    out = {"vertex_hash": vh, "unique_vertices_1mm": len(vset), "triangles": tris, "bbox": [lo, hi], "area_by_material": dict(area), "asset_bbox": asset_box, "identity": ids,
           "lights": lights, "family_map": family_map, "animation": sorted(animation, key=str)}
    import numpy as np
    np.save(a[1].replace(".json", ".verts.npy"), np.unique(np.round(np.array(vlist, dtype=np.float64), 4), axis=0).astype(np.float32))
    with open(a[1], "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("SIG ok", len(area), "materials", tris, "triangles")


main()
