#!/usr/bin/env python3
"""
Spawn Room hero suits: the crew worker's own hazmat suit, LINKED into each locker.

Run headlessly (Blender 5.2):
    blender -b <input.blend> -P add_hero_suits.py -- <output.blend>

The suit is not copied into the module. `hero_suit.blend` (built by build_hero_suit.py with the same code the player
character wears) holds the collection `HERO_SUIT`; each locker PPE_01..PPE_04 gets a collection instance of it
(`PPE_0n_suit_model`), so editing and re-saving hero_suit.blend changes all four placed suits (reload the library in the
module). The suit hangs empty (no wearer), faces the open front of the locker with its pack against the back panel, is held
by a strap from the rescue handle to a hook over the hanger rail, and stands on a low boot dock. A dark collar around the
neck stub hides it behind the empty visor (a separate object, the suit itself is unmodified).

Support registration (validate_contacts.py): the PPE_0n_suit root rests on the hanger rail via the hook, the dock on the
locker floor shelf, the strip light under the upper shelf; contact points are raycast onto the real geometry.
Re-running rebuilds everything (the earlier hand-modelled and copied suits are deleted).
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector


OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
ZO = 0.01                          # world z of each locker origin
Y_BACK = 0.275                     # pack back plate sits just in front of the back panel (local y)
ROOF = 1.985                       # highest point of the suit, under the rail / upper shelf
STRIP_Y = 0.19                      # behind the hood so the visor does not mirror the strip
LOCKER_LIGHT_W = float(os.environ.get("LOCKER_LIGHT_W", "40"))
scene = bpy.context.scene
COLS = [c for c in (bpy.data.collections.get("MODULE_spawn-room"), bpy.data.collections.get("PPE_STATIONS")) if c]
STEEL = bpy.data.materials["steel"]


def kill(obj):
    for c in list(obj.children_recursive):
        bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


def clear_old(n):
    names = [o.name for o in bpy.data.objects if o.name.startswith(("PPE_0%d_suit" % n, "PPE_0%d_helmet" % n, "WORKER_0%d" % n, "PPE_0%d_locker_light" % n, "PPE_0%d_boot_dock" % n))]
    for pat in ("BELONG_0%d_jacket" % n, "BELONG_0%d_hanger_" % n, "BELONG_0%d_fold_" % n, "BELONG_0%d_bag" % n,
                "BELONG_0%d_mid_shelf" % n, "PPE_0%d_work_boot" % n):
        names += [o.name for o in bpy.data.objects
                  if o.name.startswith(pat) and o.parent and o.parent.name == "PPE_0%d" % n]
    for nm in names:
        o = bpy.data.objects.get(nm)
        if o is not None:
            kill(o)


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


# remove the earlier hand-modelled suit pass (and its materials once unused)
for n in (1, 2, 3, 4):
    clear_old(n)
for m in list(bpy.data.materials):
    if m.name.startswith("SUIT_") and m.name != "SUIT_glass" and m.users == 0:
        bpy.data.materials.remove(m)

# ---------------------------------------------------------------- the linked hero suit
LIB_PATH = os.environ.get("HERO_SUIT_LIB") or os.path.join(os.path.dirname(bpy.data.filepath), "hero_suit.blend")
for _lib in list(bpy.data.libraries):                    # drop a previous link so a re-run picks up the file as saved
    if _lib.name == "hero_suit.blend" or os.path.basename(_lib.filepath) == "hero_suit.blend":
        bpy.data.libraries.remove(_lib)
with bpy.data.libraries.load(LIB_PATH, link=True, relative=True) as (_src, _dst):
    _dst.collections = ["HERO_SUIT"]
HERO = _dst.collections[0]
HP = {k: HERO[k] for k in HERO.keys()}                   # measurements stored with the suit
DARK = bpy.data.materials["darksteel"]


def cylinder(name, c, r, h, parent, seg=28):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    for v in ret["verts"]:
        v.co = Vector((v.co.x + c[0], v.co.y + c[1], v.co.z + c[2]))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(DARK)
    for p_ in me.polygons:
        p_.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.parent = parent
    link_cols(o)
    return o


report = {}
for n in (1, 2, 3, 4):
    P = bpy.data.objects["PPE_0%d" % n]
    bpy.context.view_layer.update()

    # asset root carrying the support registration
    asset = bpy.data.objects.new("PPE_0%d_suit" % n, None)
    asset.empty_display_size = 0.05
    asset.parent = P
    asset.matrix_parent_inverse = Matrix.Identity(4)
    top_z, pack_back = HP["cs_top_z"], HP["cs_pack_back_y"]
    z0 = ROOF - top_z                                   # world z of the suit origin
    yoff = Y_BACK + pack_back                           # locker-local y of the suit origin
    zmin, zmax = z0 + HP["cs_foot_zmin"], ROOF
    inst = bpy.data.objects.new("PPE_0%d_suit_model" % n, None)   # the linked hero suit
    inst.instance_type = "COLLECTION"
    inst.instance_collection = HERO
    inst.empty_display_size = 0.05
    inst.parent = asset
    inst.matrix_parent_inverse = Matrix.Identity(4)
    inst.rotation_euler = (0, 0, math.pi)               # face the open front of the locker
    inst.location = (0.0, yoff, z0 - ZO)
    link_cols(inst)
    # collar around the neck stub (visible through the empty visor), a separate object: the suit is not modified
    cylinder("PPE_0%d_suit_neck_collar" % n,
             (-HP["cs_neck_cx"], yoff - HP["cs_neck_cy"], z0 + (HP["cs_neck_z0"] + HP["cs_neck_z1"]) / 2 - ZO),
             HP["cs_neck_r"] + 0.004, HP["cs_neck_z1"] - HP["cs_neck_z0"], asset)
    link_cols(asset)

    # hook over the rail, strap down to the rescue handle behind the hood
    hit, ro = cast(P, (0.0, 0.15, 2.03 - ZO), (0, 0, -1), 0.5)
    rail_top = hit.z + ZO + 0.0004                      # world z of the rail top
    ys = 0.255                                          # strap sits between the hood back and the back panel
    handle_y = yoff + 0.255
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
    asset["cs_hide_on_equip"] = True               # hidden while the player wears it
    asset["cs_show_on_unequip"] = True             # reappears when it is taken off
    asset["cs_unequip_only_at_station"] = True     # it can only be taken off at its own locker
    asset["cs_support_target"] = ro.name
    asset["cs_support_direction"] = "WORLD_-Z"
    for cname in ("MODULE_spawn-room", "PPE_STATIONS", "CS_SUPPORT_REQUIRED", "CS_FLOOR_DRESSING"):
        c = bpy.data.collections.get(cname)
        if c and asset.name not in c.objects:
            c.objects.link(asset)
    for o in [asset] + list(asset.children_recursive):
        if o.name in scene.collection.objects:
            scene.collection.objects.unlink(o)


    # ---- boot dock: a low steel dock on the locker floor that the suit boots rest on (the suit no longer floats)
    bpy.context.view_layer.update()
    fz = z0 + HP["cs_foot_zmin"] - ZO                   # locker-local z of the lowest point of the boots
    x0, x1 = -HP["cs_sole_x1"] - 0.015, -HP["cs_sole_x0"] + 0.015
    y0 = max(yoff - HP["cs_sole_y1"] - 0.015, -0.30)
    y1 = min(yoff - HP["cs_sole_y0"] + 0.015, 0.20)
    droot = bpy.data.objects.new("PPE_0%d_boot_dock" % n, None)
    droot.empty_display_size = 0.04
    droot.parent = P
    droot.matrix_parent_inverse = Matrix.Identity(4)
    fl, floor_obj = cast(P, (0.0, 0.0, 0.5 - ZO), (0, 0, -1), 0.6)      # top of the locker floor shelf (local z)
    pad_t = 0.006
    plate_t = 0.024
    top = fz + ZO                                       # world z of the sole underside
    plate_top = top - pad_t
    plate_bot = plate_top - plate_t
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    box_mesh("PPE_0%d_boot_dock_plate" % n, (cxm, cym, (plate_top + plate_bot) / 2 - ZO), (x1 - x0, y1 - y0, plate_t), droot)
    pad = box_mesh("PPE_0%d_boot_dock_pad" % n, (cxm, cym, plate_top + pad_t / 2 - ZO), (x1 - x0 - 0.03, y1 - y0 - 0.03, pad_t), droot)
    pad.data.materials.clear()
    pad.data.materials.append(bpy.data.materials["rubber"])
    leg_h = plate_bot - (fl.z + ZO)
    for i, lx in enumerate((x0 + 0.03, x1 - 0.03)):
        box_mesh("PPE_0%d_boot_dock_leg_%d" % (n, i), (lx, cym, fl.z + leg_h / 2), (0.03, y1 - y0 - 0.04, leg_h), droot)
        e = bpy.data.objects.new("PPE_0%d_boot_dock_contact_%02d" % (n, i), None)
        e.empty_display_size = 0.01
        e.parent = droot
        e.matrix_parent_inverse = Matrix.Identity(4)
        e.location = (lx, cym, fl.z + 0.0004)
        e["cs_support_anchor"] = True
        link_cols(e)
    droot["cs_support_target"] = floor_obj.name
    droot["cs_support_direction"] = "WORLD_-Z"
    for cname in ("MODULE_spawn-room", "PPE_STATIONS", "CS_SUPPORT_REQUIRED", "CS_FLOOR_DRESSING"):
        c = bpy.data.collections.get(cname)
        if c and droot.name not in c.objects:
            c.objects.link(droot)
    for o in [droot] + list(droot.children_recursive):
        if o.name in scene.collection.objects:
            scene.collection.objects.unlink(o)
    report_dock = {"sole_z": round(top, 4), "leg_h": round(leg_h, 3), "x": [round(x0, 3), round(x1, 3)], "y": [round(y0, 3), round(y1, 3)]}

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
    P["contents"] = "One hanging crew hazmat suit (linked from hero_suit.blend, empty) on the hanger rail, personal items on the upper shelf"
    report[n] = {"rail": ro.name, "z_origin": round(z0, 3), "suit_zmin": round(zmin, 3), "suit_zmax": round(zmax, 3), "dock": report_dock}

print("SUIT_REPORT", report)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)   # copies from earlier passes
if OUT:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("saved", OUT)
