#!/usr/bin/env python3
"""
Spawn Room 90+ pass: plants, signage, locker door angles and hall lighting (the open items from final-pass/REPORT.md).

Run headlessly (Blender 5.2) on the canonical module, after polish_spawn.py:
    blender -b <input.blend> -P pass_90plus.py -- <output.blend>

Idempotent: every step removes by name or sets absolute values.
  1. Plants: the low-poly ficus, snake plants and pothos in the hall and locker room are removed (the critics read them
     as filler). The briefing ficus and the briefing sideboard pothos stay as the room's one planted corner.
  2. Signage: the two slogan notices on the hall shift board ("SAME TEAM A BRIGHTER TOMORROW", "SAFETY BUILDS
     CONFIDENCE") are removed and the board is scaled down; the duplicate hall notice board by the spawn doors is removed.
  3. Locker doors: the open doors keep their 108 degree angle (the suits stay visible) but their inside faces were blank
     red slabs filling the foreground of LockerDoor/LockerReverse. Each of the eight leaves gets a raised, bevelled stiffener
     panel; the four left-hand leaves also get a polished plate (mirror) above the panel. Parented to the leaf, so they
     follow it. Door sizes are unchanged.
  4. Hall lighting: the three ceiling tubes get graded power (bright at the spawn end, dim in the middle, mid at the
     airlock end) so the hall has falloff instead of an even wash. They stay baked emissive fixtures; light budget unchanged.
"""
import re
import sys

import bmesh
import bpy

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
D = bpy.data.objects


def remove_tree(root):
    """Delete an object and its children; orphaned mesh data is dropped when the file is saved."""
    victims = [root] + list(root.children_recursive)
    for o in victims:
        bpy.data.objects.remove(o, do_unlink=True)
    return len(victims)


# ---------------------------------------------------------------- 1. plants
PLANTS = ["COZY_H_ficus", "COZY_H_snake", "COZY_H_pothos", "COZY_L_ficus", "COZY_L_snake", "COZY_L_pothos", "COZY_L_pothos2"]
for name in PLANTS:
    o = D.get(name)
    if o is not None:
        remove_tree(o)
# anchors / lights that belonged to the removed plants
for o in [o for o in D if re.match(r"COZY_(H|L)_(ficus|snake|pothos2?)(_anchor\d+)?$", o.name)]:
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- 2. signage
for idx in (0, 3):
    for o in [o for o in D if o.name.startswith("V_HALL_notice_%d" % idx)]:
        bpy.data.objects.remove(o, do_unlink=True)
board = D.get("V_HALL_shift_board")
if board is not None:
    board.scale = (0.9, 1.0, 0.78)  # was (1.3, 1.0, 1.1)
# the duplicate notice board: its root is named exactly HALL_notice (the prefix match below does not catch it), so take
# the root's whole tree first, then any stragglers
root = D.get("HALL_notice")
if root is not None:
    remove_tree(root)
for o in [o for o in D if o.name == "HALL_notice" or o.name.startswith(("HALL_notice_", "LIFE_changed_shift"))]:
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- 3. locker door inside faces
for o in [o for o in D if o.name.startswith("DOORIN_")]:
    bpy.data.objects.remove(o, do_unlink=True)


def box(name, parent, centre, size, mat, bevel):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=2, affect="EDGES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(bpy.data.materials[mat])
    ob = bpy.data.objects.new(name, me)
    (parent.users_collection[0]).objects.link(ob)
    ob.parent = parent
    ob.location = centre
    ob["asset_role"] = "locker_door_detail"
    return ob


for lk in (1, 2, 3, 4):
    for side, sx in (("L", 1.0), ("R", -1.0)):
        door = D["BELONG_%02d_door_%s" % (lk, side)]
        # leaf: local x centre sx*0.25, 0.49 wide, 2.09 tall, inside face at local +y
        base = "DOORIN_%02d_%s" % (lk, side)
        box(base + "_panel", door, (sx * 0.25, 0.0165, 0.95), (0.33, 0.013, 1.30), "V_locker_steel", 0.004)
        if side == "L":
            # wholly above the panel (panel top at local z 1.60) and clear of the leaf face (local y 0.010), so it shares no
            # surface with either
            box(base + "_mirror", door, (sx * 0.25, 0.0155, 1.82), (0.24, 0.009, 0.34), "steel", 0.002)

# ---------------------------------------------------------------- 4. hall lighting
for name, watts in (("HALL_light_00_area", 150.0), ("HALL_light_01_area", 70.0), ("HALL_light_02_area", 105.0)):
    D[name].data.energy = watts

if OUT:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("saved", OUT)
