#!/usr/bin/env python3
"""
Spawn Room hero suits: the crew worker's own hazmat suit (character_worker + character_suit) hung in each locker.

Run headlessly (Blender 5.2):
    blender -b <input.blend> -P add_hero_suits.py -- <output.blend>

One suit per locker PPE_01..PPE_04 (one per player), identical suit, per-player accent colour. The suit is the exact
build the player character wears (build_worker + build_hazmat + equip, A-pose rest), minus the wearer: skin regions,
head and face are removed so it hangs empty. It faces the open front of the locker, its pack against the back panel, and
is hung from the hanger rail by a strap from the rescue handle to a hook over the rail.

Replaces the earlier hand-modelled suit (PPE_0n_suit / helmet / cradle objects are deleted on every run). The
personal-belongings dressing that sat in the suit's space was removed by that earlier pass and stays removed.
Support registration (validate_contacts.py): the PPE_0n_suit root rests on the hanger rail via the hook; the contact
points are raycast onto the real rail. Re-running rebuilds everything.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
ZO = 0.01                          # world z of each locker origin
Y_BACK = 0.275                     # pack back plate sits just in front of the back panel (local y)
ROOF = 1.985                       # highest point of the suit, under the rail / upper shelf
STRIP_Y = 0.19                      # behind the hood so the visor does not mirror the strip
LOCKER_LIGHT_W = float(os.environ.get("LOCKER_LIGHT_W", "40"))
PLAYER_ACCENT = {1: "#3C7DDB", 2: "#4CAF50", 3: "#D6407F", 4: "#E8E2D0"}
scene = bpy.context.scene
COLS = [c for c in (bpy.data.collections.get("MODULE_spawn-room"), bpy.data.collections.get("PPE_STATIONS")) if c]
STEEL = bpy.data.materials["steel"]


def kill(obj):
    for c in list(obj.children_recursive):
        bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


def clear_old(n):
    names = [o.name for o in bpy.data.objects if o.name.startswith(("PPE_0%d_suit" % n, "PPE_0%d_helmet" % n, "WORKER_0%d" % n, "PPE_0%d_locker_light" % n))]
    for pat in ("BELONG_0%d_jacket" % n, "BELONG_0%d_hanger_" % n, "BELONG_0%d_fold_" % n, "BELONG_0%d_bag" % n,
                "BELONG_0%d_mid_shelf" % n, "PPE_0%d_work_boot" % n):
        names += [o.name for o in bpy.data.objects
                  if o.name.startswith(pat) and o.parent and o.parent.name == "PPE_0%d" % n]
    for nm in names:
        o = bpy.data.objects.get(nm)
        if o is not None:
            kill(o)


def world_zrange(root):
    bpy.context.view_layer.update()
    zmax, zmin = -1e9, 1e9
    for o in root.children_recursive:
        if o.type == "MESH" and not o.hide_render:
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                zmax, zmin = max(zmax, w.z), min(zmin, w.z)
    return zmin, zmax


def cast(parent, local_origin, local_dir, dist=1.0):
    mw = parent.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    o = mw @ Vector(local_origin)
    d = (mw.to_3x3() @ Vector(local_dir)).normalized()
    ok, loc, nrm, _i, obj, _m = scene.ray_cast(dg, o, d, distance=dist)
    return (mw.inverted() @ loc, obj) if ok else (None, None)


def link_cols(o):
    for c in COLS:
        if o.name not in c.objects:
            c.objects.link(o)


def box_mesh(name, c, s, parent):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * s[0] + c[0], v.co.y * s[1] + c[1], v.co.z * s[2] + c[2]))
    bmesh.ops.bevel(bm, geom=list({e for v in r["verts"] for e in v.link_edges}), offset=0.002, segments=2, affect="EDGES")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(STEEL)
    o = bpy.data.objects.new(name, me)
    o.parent = parent
    link_cols(o)
    return o


def cap_neck(root):
    """The skin is gone, so the suit body's neck stub shows through the empty visor: cut it and close the opening with a
    dark inner cap (a seal ring seen from outside, a dark empty collar through the visor)."""
    body = next(o for o in root.children_recursive if o.name.startswith("SUIT_BODY"))
    dark = bpy.data.materials.get("COZY_#30323C_85_0_0")
    bm = bmesh.new()
    bm.from_mesh(body.data)
    cut = [f for f in bm.faces if min(v.co.z for v in f.verts) > 1.20]
    bmesh.ops.delete(bm, geom=cut, context="FACES")
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    edges = [e for e in bm.edges if e.is_boundary and min(v.co.z for v in e.verts) > 1.0]
    new = bmesh.ops.triangle_fill(bm, edges=edges, use_beauty=True)["geom"]
    if dark is not None:
        body.data.materials.append(dark)
        idx = len(body.data.materials) - 1
        for f in [g for g in new if isinstance(g, bmesh.types.BMFace)]:
            f.material_index = idx
    bm.to_mesh(body.data)
    bm.free()
    for p in body.data.polygons:
        p.use_smooth = True


# remove the earlier hand-modelled suit pass (and its materials once unused)
for n in (1, 2, 3, 4):
    clear_old(n)
for m in list(bpy.data.materials):
    if m.name.startswith("SUIT_") and m.name != "SUIT_glass" and m.users == 0:
        bpy.data.materials.remove(m)

report = {}
for n in (1, 2, 3, 4):
    P = bpy.data.objects["PPE_0%d" % n]
    bpy.context.view_layer.update()

    # ---- the crew worker's hazmat suit, built exactly as the player character wears it
    root, _tris = CW.build_worker(name="WORKER_0%d" % n, collection=scene.collection)
    CS.build_hazmat(root, coll=scene.collection, colors={"accent": PLAYER_ACCENT[n]})
    CS.equip(root)
    for o in list(root.children_recursive):          # empty suit: no wearer (skin, head, face)
        if o.name not in bpy.data.objects:
            continue
        if (o.name.startswith(("WORKER_0%d_BODY_" % n, "WORKER_0%d_HEAD" % n)) and not o.name.endswith("_HEAD_PIVOT")) \
                or o.name.startswith("FACE_"):
            bpy.data.objects.remove(o, do_unlink=True)
    cap_neck(root)
    zmin, zmax = world_zrange(root)

    # asset root carrying the support registration
    asset = bpy.data.objects.new("PPE_0%d_suit" % n, None)
    asset.empty_display_size = 0.05
    asset.parent = P
    asset.matrix_parent_inverse = Matrix.Identity(4)
    z0 = ROOF - zmax                                    # world z of the character origin
    pack_back = -0.345                                  # SUIT_KIT back plate (character y)
    root.parent = asset
    root.matrix_parent_inverse = Matrix.Identity(4)
    root.rotation_euler = (0, 0, math.pi)               # face the open front of the locker
    root.location = (0.0, Y_BACK + pack_back, z0 - ZO)
    for o in [root] + list(root.children_recursive):
        link_cols(o)

    # hook over the rail, strap down to the rescue handle behind the hood
    hit, ro = cast(P, (0.0, 0.15, 2.03 - ZO), (0, 0, -1), 0.5)
    rail_top = hit.z + ZO + 0.0004                      # world z of the rail top
    ys = 0.255                                          # strap sits between the hood back and the back panel
    handle_y = Y_BACK + pack_back + 0.255
    handle_top = z0 + 1.19
    box_mesh("PPE_0%d_suit_strap" % n, (0.0, ys, (handle_top + rail_top) / 2 - ZO),
             (0.03, 0.012, rail_top - handle_top), asset)
    box_mesh("PPE_0%d_suit_handle_link" % n, (0.0, (ys + handle_y) / 2, handle_top - ZO),
             (0.03, abs(ys - handle_y) + 0.012, 0.012), asset)
    box_mesh("PPE_0%d_suit_hook_bridge" % n, (0.0, 0.195, rail_top + 0.007 - ZO), (0.03, 0.14, 0.014), asset)
    box_mesh("PPE_0%d_suit_hook_lip" % n, (0.0, 0.126, rail_top - 0.012 - ZO), (0.03, 0.012, 0.04), asset)
    for i, ax in enumerate((-0.07, 0.07)):
        h2, _ = cast(P, (ax, 0.15, 2.03 - ZO), (0, 0, -1), 0.5)
        e = bpy.data.objects.new("PPE_0%d_suit_contact_%02d" % (n, i), None)
        e.empty_display_size = 0.01
        e.parent = asset
        e.matrix_parent_inverse = Matrix.Identity(4)
        e.location = (ax, 0.15, h2.z + 0.0009)
        e["cs_support_anchor"] = True
        link_cols(e)
    asset["asset_role"] = "equippable_suit"
    asset["cs_equip_station"] = n                  # player/station i; equipping hides this asset until it is returned
    asset["cs_hide_on_equip"] = True
    asset["cs_support_target"] = ro.name
    asset["cs_support_direction"] = "WORLD_-Z"
    for cname in ("MODULE_spawn-room", "PPE_STATIONS", "CS_SUPPORT_REQUIRED", "CS_FLOOR_DRESSING"):
        c = bpy.data.collections.get(cname)
        if c and asset.name not in c.objects:
            c.objects.link(asset)
    # the working copies were built in the scene root: keep them only in the room collections
    for o in [asset, root] + list(root.children_recursive) + list(asset.children_recursive):
        if o.name in scene.collection.objects:
            scene.collection.objects.unlink(o)

    # ---- interior strip light under the upper shelf (visible fixture + baked light), lights the suit and the bay
    lroot = bpy.data.objects.new("PPE_0%d_locker_light" % n, None)
    lroot.empty_display_size = 0.04
    lroot.parent = P
    lroot.matrix_parent_inverse = Matrix.Identity(4)
    shelf, shelf_obj = cast(P, (-0.25, STRIP_Y, 1.9 - ZO), (0, 0, 1), 0.5)
    sz = shelf.z + ZO                                   # world z of the shelf underside
    strip = box_mesh("PPE_0%d_locker_light_strip" % n, (0.0, STRIP_Y, sz - 0.006 - ZO), (0.70, 0.035, 0.012), lroot)
    strip.data.materials.clear()
    strip.data.materials.append(bpy.data.materials["COZY_white_55_10_0"])
    for i, ax in enumerate((-0.25, 0.25)):
        e = bpy.data.objects.new("PPE_0%d_locker_light_contact_%02d" % (n, i), None)
        e.empty_display_size = 0.01
        e.parent = lroot
        e.matrix_parent_inverse = Matrix.Identity(4)
        e.location = (ax, STRIP_Y, sz - ZO - 0.0009)
        e["cs_support_anchor"] = True
        link_cols(e)
    ld = bpy.data.lights.new("LOCKER_light_PPE_0%d_area" % n, "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = 0.70, 0.12
    ld.energy = LOCKER_LIGHT_W
    ld.color = (1.0, 0.88, 0.72)
    lo = bpy.data.objects.new("LOCKER_light_PPE_0%d_area" % n, ld)
    lo.parent = lroot
    lo.matrix_parent_inverse = Matrix.Identity(4)
    lo.location = (0.0, STRIP_Y, sz - 0.014 - ZO)
    lo["cs_rt_role"] = "baked_plus_emissive_fixture"
    lo["cs_rt_group"] = "locker_power"
    lo["cs_rt_shadow"] = False
    link_cols(lo)
    lroot["cs_support_target"] = shelf_obj.name
    lroot["cs_support_direction"] = "WORLD_+Z"
    for cname in ("MODULE_spawn-room", "PPE_STATIONS", "CS_SUPPORT_REQUIRED", "CS_CEILING_DRESSING"):
        c = bpy.data.collections.get(cname)
        if c and lroot.name not in c.objects:
            c.objects.link(lroot)
    for o in [lroot] + list(lroot.children_recursive):
        if o.name in scene.collection.objects:
            scene.collection.objects.unlink(o)
    P["contents"] = "One hanging crew hazmat suit (the player's own suit, empty) on the hanger rail, personal items on the upper shelf"
    report[n] = {"rail": ro.name, "z_origin": round(z0, 3), "suit_zmin": round(zmin, 3), "suit_zmax": round(zmax, 3)}

print("SUIT_REPORT", report)
if OUT:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("saved", OUT)
