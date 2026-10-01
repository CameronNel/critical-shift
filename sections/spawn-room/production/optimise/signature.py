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


def fcurves_of(action):
    """All F-curves of an action: the legacy list, or every channelbag of every layered-action strip."""
    out = list(getattr(action, "fcurves", []) or [])
    for layer in getattr(action, "layers", []) or []:
        for strip in getattr(layer, "strips", []) or []:
            for cb in getattr(strip, "channelbags", []) or []:
                out.extend(cb.fcurves)
    return out


def action_content(action):
    if action is None:
        return None
    curves = []
    for fc in fcurves_of(action):
        curves.append([fc.data_path, fc.array_index, fc.extrapolation,
                       [[round(k.co[0], 4), round(k.co[1], 5), k.interpolation, round(k.handle_left[0], 3),
                         round(k.handle_left[1], 4), round(k.handle_right[0], 3), round(k.handle_right[1], 4)]
                        for k in fc.keyframe_points],
                       [m.type for m in fc.modifiers]])
    slots = sorted(sl.name_display for sl in getattr(action, "slots", []) or [])
    return {"curves": sorted(curves, key=str), "slots": slots, "frame_range": list(action.frame_range)}


def driver_content(ad):
    out = []
    for dr in ad.drivers:
        d = dr.driver
        out.append([dr.data_path, dr.array_index, d.type, d.expression,
                    [[v.name, v.type, [[t.id.name if t.id else None, t.data_path, t.transform_type, t.transform_space,
                                         t.bone_target] for t in v.targets]] for v in d.variables]])
    return sorted(out, key=str)


def nla_content(ad):
    return [[tr.name, tr.mute, [[st.name, st.action.name if st.action else None, st.frame_start, st.frame_end,
                                  st.action_frame_start, st.action_frame_end, st.scale, st.repeat, st.blend_type,
                                  st.extrapolation, st.mute] for st in tr.strips]] for tr in ad.nla_tracks]


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    bpy.ops.wm.open_mainfile(filepath=a[0])
    sc = bpy.context.scene
    pal = None
    if "OPT_PALETTE" in bpy.data.texts:
        cells = json.loads(bpy.data.texts["OPT_PALETTE"].as_string())
        grid = cells["grid"]
        pal = {c: n for n, c in cells["cells"].items()}
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
        mats = [s.material.name.replace("__noattr", "") if s.material else "" for s in o.material_slots]
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
            for owner in (idb, getattr(idb, "node_tree", None)):
                ad = getattr(owner, "animation_data", None) if owner is not None else None
                if ad and (ad.action or ad.drivers or ad.nla_tracks):
                    animation.append([coll_name, idb.name, ad.action.name if ad.action else None,
                                      digest(action_content(ad.action)), digest(driver_content(ad)),
                                      digest(nla_content(ad))])
    lights = {o.name: [round(o.data.energy, 3), o.get("cs_rt_role")] for o in sc.objects if o.type == "LIGHT"}
    import hashlib
    vh = hashlib.md5(repr(sorted(vset)).encode()).hexdigest()
    out = {"vertex_hash": vh, "unique_vertices_1mm": len(vset), "triangles": tris, "bbox": [lo, hi], "area_by_material": dict(area), "asset_bbox": asset_box, "identity": ids,
           "lights": lights, "animation": sorted(animation, key=str)}
    import numpy as np
    np.save(a[1].replace(".json", ".verts.npy"), np.unique(np.round(np.array(vlist, dtype=np.float64), 4), axis=0).astype(np.float32))
    with open(a[1], "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("SIG ok", len(area), "materials", tris, "triangles")


main()
