#!/usr/bin/env python3
"""
Spawn Room cozy trinket pass (briefing room + locker room).

Run headlessly (Blender 5.2 / bpy) after restyle_cozy_modern.py and refine_spawn_assets.py:
    python add_cozy_trinkets.py -- <input.blend> <output.blend>

Adds small props, each named COZY_*, placed by raycast onto a real support surface, skipped when
they would collide with existing geometry, and registered for validate_contacts.py
(CS_SUPPORT_REQUIRED + the matching dressing collection, cs_support_target / cs_support_direction).

Rules it enforces:
  * keep-out zones: briefing seating + door path, locker route to the chamber stay clear;
  * wall props are checked in the WALL PLANE (a poster cannot hide behind a wall-mounted TV);
  * no bench-seat clutter in the briefing room; no extra plants; one ceiling fixture type per room
    (briefing = pendants).
Re-running removes previous COZY_* objects first.
"""

import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cozy_geo import B, mat  # noqa: E402,F401
from cozy_props import *  # noqa: E402,F401,F403

random.seed(11)


# ------------------------------------------------------------- placement
LEAF = ("V_leaf", "V_stem", "V_bark", "COZY_")
scene = None
placed = []          # (name, min, max) world bboxes of COZY props
existing = []        # (name, min, max) world bboxes of relevant existing objects
report = {"placed": 0, "skipped": 0, "failed": []}
keepouts = []        # (name, min, max) zones floor/surface props must stay out of


def keepout(name, x0, x1, y0, y1, zmax=1.6):
    keepouts.append((name, Vector((x0, y0, -0.05)), Vector((x1, y1, zmax))))


_DG = {}


def dg():
    """Evaluated once: COZY_ props are skipped by raycasts, so it never needs refreshing."""
    if "g" not in _DG:
        bpy.context.view_layer.update()
        _DG["g"] = bpy.context.evaluated_depsgraph_get()
    return _DG["g"]


def cast(origin, direction, allow=None, dist=12.0):
    depsgraph = dg()
    o = Vector(origin)
    for _ in range(40):
        ok, loc, n, _i, obj, _m = scene.ray_cast(depsgraph, o, Vector(direction), distance=dist)
        if not ok:
            return None
        if obj.name.startswith(LEAF) or (allow and not obj.name.startswith(allow)):
            o = loc + Vector(direction) * 0.002
            continue
        return loc, n, obj
    return None


def world_bbox(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def bbox_under(obj, m4):
    pts = [m4 @ Vector(c) for c in obj.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def pool_near(lo, hi, pad=0.4):
    """Existing + placed bboxes that could touch the region [lo, hi] (padded)."""
    out = []
    for name, elo, ehi in existing + placed:
        if (elo.x < hi.x + pad and ehi.x > lo.x - pad and elo.y < hi.y + pad and ehi.y > lo.y - pad
                and elo.z < hi.z + pad and ehi.z > lo.z - pad):
            out.append((name, elo, ehi))
    return out


def collides(bb, ignore=(), pool=None):
    lo, hi = bb
    tol = 0.004
    for name, elo, ehi in (pool if pool is not None else existing + placed):
        if name in ignore:
            continue
        if (lo.x < ehi.x - tol and hi.x > elo.x + tol and lo.y < ehi.y - tol and hi.y > elo.y + tol
                and lo.z < ehi.z - tol and hi.z > elo.z + tol):
            return name
    return None


def nearest_axis(v):
    a = max(range(3), key=lambda i: abs(v[i]))
    return "WORLD_%s%s" % ("+" if v[a] > 0 else "-", "XYZ"[a])


def add_anchor(obj, name, xy, k=0, z=0.0):
    """Measured contact point for validate_contacts.py (raycast onto the real support)."""
    e = bpy.data.objects.new("%s_anchor%d" % (name, k), None)
    e.empty_display_size = 0.02
    e.parent = obj
    e.location = (xy[0], xy[1], z)
    e["cs_support_anchor"] = True
    bpy.context.scene.collection.objects.link(e)


def register(obj, room, kind, target, direction):
    obj["cs_support_target"] = target
    obj["cs_support_direction"] = direction
    dress = {"floor": "CS_FLOOR_DRESSING", "wall": "CS_WALL_DRESSING", "ceiling": "CS_CEILING_DRESSING"}[kind]
    for cname in (room, dress, "CS_SUPPORT_REQUIRED"):
        col = bpy.data.collections.get(cname)
        if col and obj.name not in col.objects:
            col.objects.link(obj)


def surface_place(recipe, xy_candidates, allow, room, name, yaws=(0.0,), light=None, free=False):
    """Drop a floor/surface prop onto the first candidate that has support and no collision."""
    obj = recipe().build(name)
    xs = [c[0] for c in xy_candidates]
    ys = [c[1] for c in xy_candidates]
    size = max(obj.dimensions)
    lo_r = Vector((min(xs) - size, min(ys) - size, -0.2))
    hi_r = Vector((max(xs) + size, max(ys) + size, 3.4))
    pool = pool_near(lo_r, hi_r)
    if not free:
        pool += [k for k in keepouts if k[1].x < hi_r.x and k[2].x > lo_r.x and k[1].y < hi_r.y and k[2].y > lo_r.y]
    why = "nosupport"
    for (x, y) in xy_candidates:
        hit = cast((x, y, 3.3), (0, 0, -1), allow=allow)
        if hit is None:
            continue
        loc, n, sup = hit
        if n.z < 0.985:
            continue
        for yaw in yaws:
            m4 = Matrix.Translation(Vector((x, y, loc.z))) @ Matrix.Rotation(yaw, 4, "Z")
            bb = bbox_under(obj, m4)
            hit_name = collides(bb, ignore=(sup.name,), pool=pool)
            why = "hit:" + str(hit_name)
            if hit_name is None:
                obj.matrix_world = m4
                bpy.context.scene.collection.objects.link(obj)
                add_anchor(obj, name, (0.0, 0.0))
                register(obj, room, "floor", sup.name, "WORLD_-Z")
                placed.append((obj.name, *bb))
                if light:
                    add_light(obj, *light)
                report["placed"] += 1
                return obj
    bpy.data.objects.remove(obj, do_unlink=True)
    report["skipped"] += 1
    report["failed"].append(name + ":" + why)
    return None


def wall_place_any(recipe, wall, alongs, z, allow, room, name, **kw):
    """Try several positions along a wall; keep the first that fits."""
    for a in alongs:
        if wall_place(recipe, wall, a, z, allow, room, name, quiet=True, **kw):
            return True
    report["skipped"] += 1
    report["failed"].append(name + ":nofit")
    return False


def snap_axis(v):
    a = max(range(2), key=lambda i: abs(v[i]))       # walls are vertical: X or Y
    out = Vector((0.0, 0.0, 0.0))
    out[a] = 1.0 if v[a] > 0 else -1.0
    return out


def wall_place(recipe, wall, along, z, allow, room, name, spin=0.0, anchors=None, light=None, quiet=False):
    """Mount a wall prop. wall = (cast_from_axis_point, direction). along is x or y."""
    origin_fn, direction = wall
    hit = cast(origin_fn(along, z), direction, allow=allow)

    def fail(why):
        if not quiet:
            report["skipped"] += 1
            report["failed"].append(name + ":" + why)
        return None

    if hit is None:
        return fail("nowall")
    loc, n, sup = hit
    n = snap_axis(n)
    if n.length < 0.5 or abs(loc.z - z) > 0.6:
        return fail("notvertical")
    obj = recipe().build(name, floor_normalize=False)
    dx, dy = obj.dimensions.x, obj.dimensions.y

    # Mean wall depth over the prop footprint (plaster relief is about +/-1 mm).
    axis = 0 if abs(n.x) > 0.5 else 1
    depths = []
    for du in (-0.5, 0.0, 0.5):
        for dv in (-0.5, 0.0, 0.5):
            tang = Vector((0.0, 1.0, 0.0)) if axis == 0 else Vector((1.0, 0.0, 0.0))
            o = Vector(origin_fn(along, z)) + tang * du * dx + Vector((0, 0, dv * dy))
            h2 = cast(o, direction, allow=allow)
            if h2 is None or h2[2].name != sup.name and not h2[2].name.startswith(allow):
                continue
            if abs(h2[0][axis] - loc[axis]) < 0.004:      # same flat wall, not a recess behind
                depths.append(h2[0][axis])
    if len(depths) < 8:
        bpy.data.objects.remove(obj, do_unlink=True)
        return fail("wallgap")
    # Seat the back plane on the most proud point so nothing pokes into the plaster relief.
    plane = max(d * n[axis] for d in depths) * n[axis]
    loc = loc.copy()
    loc[axis] = plane

    up = Vector((0, 0, 1))
    xaxis = up.cross(n).normalized()
    yaxis = n.cross(xaxis).normalized()
    rot = Matrix((xaxis, yaxis, n)).transposed()
    rot = rot @ Matrix.Rotation(spin, 3, "Z")
    m4 = Matrix.Translation(loc) @ rot.to_4x4()
    bb = bbox_under(obj, m4)
    lo_b, hi_b = bb[0].copy(), bb[1].copy()
    if n[axis] > 0:
        hi_b[axis] += 0.35        # anything standing in front of this patch of wall counts
    else:
        lo_b[axis] -= 0.35
    hit_name = collides((lo_b, hi_b), ignore=(sup.name,), pool=pool_near(lo_b, hi_b, pad=0.02))
    if hit_name is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
        return fail("hit:" + hit_name)

    # Every back-face corner must land flat on this same wall object (no dado steps, no recesses).
    bx = [obj.bound_box[0][0], obj.bound_box[6][0]]
    by = [obj.bound_box[0][1], obj.bound_box[6][1]]
    for cx in bx:
        for cy in by:
            wp = m4 @ Vector((cx, cy, 0.0))
            hc = cast(wp + n * 0.2, -n, allow=allow, dist=0.5)
            if hc is None or hc[2].name != sup.name or abs((hc[0] - wp).dot(n)) > 0.0035:
                bpy.data.objects.remove(obj, do_unlink=True)
                return fail("cornerfail")

    # Spanning props (pennants, lights): both hooks must land on real wall.
    hooks = []
    for (ax, ay) in anchors or ():
        wp = m4 @ Vector((ax, ay, 0.0))
        h3 = cast(wp + n * 0.3, -n, allow=allow, dist=0.6)
        if h3 is None or h3[2].name != sup.name or abs((h3[0] - wp).dot(n)) > 0.006:
            bpy.data.objects.remove(obj, do_unlink=True)
            return fail("hookmiss")
        hooks.append((ax, ay, (m4.inverted() @ h3[0]).z))

    obj.matrix_world = m4
    bpy.context.scene.collection.objects.link(obj)
    for k, (ax, ay, az) in enumerate(hooks):
        add_anchor(obj, name, (ax, ay), k, az)
    register(obj, room, "wall", sup.name, nearest_axis(-n))
    placed.append((obj.name, *bb))
    if light:
        add_light(obj, *light)
    report["placed"] += 1
    return obj


def ceiling_place(recipe, x, y, room, name, light=None):
    hit = cast((x, y, 0.5), (0, 0, 1), allow=("BRIEFING_ceiling", "LOCKER_ceiling", "HALL_ceiling"))
    if hit is None:
        report["skipped"] += 1
        report["failed"].append(name + ":noceiling")
        return None
    loc, n, sup = hit
    obj = recipe().build(name, floor_normalize=False)
    m4 = Matrix.Translation(loc)
    bb = bbox_under(obj, m4)
    hit_name = collides(bb, ignore=(sup.name,), pool=pool_near(bb[0], bb[1], pad=0.05))
    if hit_name is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
        report["skipped"] += 1
        report["failed"].append(name + ":hit:" + hit_name)
        return None
    obj.matrix_world = m4
    bpy.context.scene.collection.objects.link(obj)
    register(obj, room, "ceiling", sup.name, "WORLD_+Z")
    placed.append((obj.name, *bb))
    if light:
        add_light(obj, *light)
    report["placed"] += 1
    return obj


def add_light(obj, local_offset, watts, color=(1.0, 0.72, 0.45), radius=0.08):
    data = bpy.data.lights.new("COZY_light_" + obj.name, "POINT")
    data.energy = watts
    data.color = color
    data.shadow_soft_size = radius
    lo = bpy.data.objects.new("COZY_light_" + obj.name, data)
    lo.parent = obj
    lo.location = local_offset
    bpy.context.scene.collection.objects.link(lo)


# ------------------------------------------------------------------- run
def wall_defs():
    return {
        # briefing room
        "BN": (lambda a, z: (a, 5.2, z), (0, 1, 0)),
        "BS": (lambda a, z: (a, 2.6, z), (0, -1, 0)),
        "BW": (lambda a, z: (-5.6, a, z), (-1, 0, 0)),
        # locker room
        "LN": (lambda a, z: (a, 6.3, z), (0, 1, 0)),
        "LS": (lambda a, z: (a, 2.0, z), (0, -1, 0)),
        "LE": (lambda a, z: (8.0, a, z), (1, 0, 0)),
    }


B_WALLS = ("BRIEFING_north", "BRIEFING_south", "BRIEFING_focal_wall", "BRIEFING_recess")
L_WALLS = ("LOCKER_north", "LOCKER_south", "LOCKER_far", "LOCKER_shared_wall", "LOCKER_entry")


def clear_previous():
    for o in [o for o in bpy.data.objects if o.name.startswith("COZY_")]:
        bpy.data.objects.remove(o, do_unlink=True)
    for l in [l for l in bpy.data.lights if l.name.startswith("COZY_")]:
        bpy.data.lights.remove(l)


def index_existing():
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(LEAF) or o.hide_render:
            continue
        lo, hi = world_bbox(o)
        if max(hi.x - lo.x, hi.y - lo.y) > 3.5 and (hi.z - lo.z) < 0.5:
            continue          # big floor/ceiling slabs are the supports
        dims = sorted((hi.x - lo.x, hi.y - lo.y, hi.z - lo.z))
        if dims[0] < 0.03 and dims[2] > 2.0:
            continue          # wall-length skins/dados are supports, not obstacles
        if (hi.z - lo.z) > 3.0 and min(hi.x - lo.x, hi.y - lo.y) < 0.3:
            continue          # full-height walls: handled by support ignore
        existing.append((o.name, lo, hi))


def sweep(x0, x1, y0, y1, step=0.07, near=None):
    """Grid of candidate (x, y) points, nearest to `near` first."""
    pts = []
    x = x0
    while x <= x1 + 1e-9:
        y = y0
        while y <= y1 + 1e-9:
            pts.append((round(x, 3), round(y, 3)))
            y += step
        x += step
    if near is not None:
        pts.sort(key=lambda p: (p[0] - near[0]) ** 2 + (p[1] - near[1]) ** 2)
    return pts


def rng(a, b, step=0.15):
    n = int(abs(b - a) / step) + 1
    return [round(a + (b - a) * i / max(n - 1, 1), 3) for i in range(n)]


def main():
    global scene
    src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
    bpy.ops.wm.open_mainfile(filepath=src)
    scene = bpy.context.scene
    clear_previous()
    index_existing()
    W = wall_defs()
    S = surface_place
    WA = wall_place_any
    BR, LK = "BRIEFING_ROOM", "LOCKER_ROOM"

    # keep-out zones: seating + legroom + aisle, and the door-to-chamber routes
    keepout("KEEPOUT_briefing_seating", -6.45, -3.0, 2.1, 4.95)
    keepout("KEEPOUT_briefing_door_path", -3.45, -1.85, 2.6, 5.4)
    keepout("KEEPOUT_locker_route", 1.85, 8.1, 3.08, 4.92)

    # ================= briefing: tea corner on the sideboard
    side = ("BRIEFING_sideboard",)
    top = sweep(-7.16, -6.86, 1.25, 2.25, 0.06)
    fine = sweep(-7.17, -6.85, 1.24, 2.26, 0.04)
    S(r_lamp, sweep(-7.17, -6.85, 1.24, 2.26, 0.04, near=(-7.0, 1.4)), side, BR, "COZY_B_lamp", light=((0, 0, 0.2), 45))
    S(r_kettle, fine, side, BR, "COZY_B_kettle", yaws=(0.0, 1.57))
    S(lambda: r_mug("coral"), fine, side, BR, "COZY_B_mug_coral")
    S(r_tin, fine, side, BR, "COZY_B_tin")
    S(r_duck, fine, side, BR, "COZY_B_duck")
    S(lambda: r_mug("denim"), fine, side, BR, "COZY_B_mug_denim")
    S(r_books, fine, side, BR, "COZY_B_books", yaws=(0.0, 1.57))
    S(r_noodles, fine, side, BR, "COZY_B_noodles")
    S(r_photo, fine, side, BR, "COZY_B_photo", yaws=(1.57, 0.0))
    S(r_clock_desk, fine, side, BR, "COZY_B_alarm", yaws=(1.57, 0.0))
    S(r_radio, fine, side, BR, "COZY_B_radio", yaws=(1.57, 0.0))

    # ================= briefing floor: only along the walls, never in the seating zone or aisle
    floor = ("BRIEFING_carpet", "BRIEFING_wood_floor", "BRIEFING_wood_underlay")
    S(lambda: r_pouf("denim"), sweep(-6.9, -2.4, 1.5, 5.85, 0.12, near=(-6.6, 5.4)), floor, BR, "COZY_B_pouf")
    S(lambda: r_pouf("rose"), sweep(-6.9, -2.4, 1.5, 5.85, 0.12, near=(-6.1, 1.6)), floor, BR, "COZY_B_pouf2")
    S(lambda: r_tote("coral"), sweep(-6.9, -2.4, 1.4, 5.85, 0.1, near=(-6.75, 2.6)), floor, BR, "COZY_B_tote")
    S(lambda: r_bottle("sky"), sweep(-6.9, -2.4, 1.4, 5.85, 0.1, near=(-6.7, 4.9)), floor, BR, "COZY_B_bottle2")
    S(r_candle, sweep(-6.9, -2.4, 1.4, 5.9, 0.1, near=(-2.6, 5.8)), floor, BR, "COZY_B_candle", light=((0, 0, 0.07), 5))
    S(r_stool, sweep(-6.9, -2.4, 1.4, 5.9, 0.1, near=(-2.7, 5.5)), floor, BR, "COZY_B_stool")
    S(f_shelving, sweep(-6.6, -3.0, 5.6, 5.85, 0.1, near=(-3.6, 5.8)), floor, BR, "COZY_B_shelving", yaws=(0.0,))
    S(r_hamper, sweep(-6.9, -2.4, 1.4, 5.9, 0.1, near=(-2.7, 1.7)), floor, BR, "COZY_B_basket")

    # ================= briefing walls
    ba = B_WALLS
    WA(lambda: w_sun_mural(0.8), W["BS"], rng(-6.0, -3.0, 0.2), 2.05, ba, BR, "COZY_B_sun")
    WA(lambda: w_frame(0.42, 0.56, 0), W["BS"], rng(-6.9, -2.6, 0.15), 1.85, ba, BR, "COZY_B_frame1")
    WA(lambda: w_frame(0.34, 0.44, 1, "charcoal"), W["BS"], rng(-6.9, -2.6, 0.15), 1.85, ba, BR, "COZY_B_frame2")
    WA(lambda: w_frame(0.5, 0.36, 2, "oak"), W["BS"], rng(-6.9, -2.6, 0.15), 1.8, ba, BR, "COZY_B_frame3")
    WA(w_cork, W["BS"], rng(-6.9, -2.6, 0.1), 1.75, ba, BR, "COZY_B_cork")
    WA(w_shelf, W["BN"], rng(-6.9, -2.6, 0.1), 2.0, ba, BR, "COZY_B_shelf")
    WA(w_clock, W["BN"], rng(-6.9, -2.6, 0.1), 2.55, ba, BR, "COZY_B_clock")
    WA(w_neon, W["BS"], rng(-6.9, -2.6, 0.1), 2.2, ba, BR, "COZY_B_neon", light=((0, 0, 0.15), 18, (1.0, 0.45, 0.35)))
    WA(lambda: w_pennants(2.6, 10), W["BN"], rng(-6.2, -3.4, 0.2), 3.0, ba, BR, "COZY_B_pennants", anchors=[(-1.3, 0), (1.3, 0)])
    WA(lambda: w_stringlights(2.0, 8), W["BS"], rng(-6.3, -3.4, 0.15), 2.9, ba, BR, "COZY_B_lights",
       anchors=[(-1.0, 0), (1.0, 0)], light=((0, -0.1, 0.1), 20))
    WA(w_hooks, W["BS"], rng(-3.3, -2.6, 0.1), 1.95, ba, BR, "COZY_B_hooks")
    WA(w_plaque, W["BN"], rng(-6.9, -2.6, 0.1), 1.9, ba, BR, "COZY_B_plaque")
    WA(lambda: w_poster(2, 0.5, 0.7), W["BW"], rng(1.3, 5.8, 0.1), 1.75, ba, BR, "COZY_B_poster1")
    WA(lambda: w_poster(0, 0.45, 0.62), W["BW"], rng(1.3, 5.8, 0.1), 1.7, ba, BR, "COZY_B_poster2")
    WA(lambda: w_frame(0.34, 0.46, 0, "walnut"), W["BN"], rng(-6.9, -2.6, 0.1), 1.85, ba, BR, "COZY_B_frame4")

    # ================= briefing ceiling: pendants are the ONE fixture type here
    for k, (x, y) in enumerate(((-5.25, 3.6), (-3.75, 3.6))):
        ceiling_place(lambda: c_pendant("mustard"), x, y, BR, "COZY_B_pendant%d" % k,
                      light=((0, 0, -0.80), 950, (1.0, 0.72, 0.46), 0.05))

    # ================= locker benches (things people leave while suiting up)
    lb = ("LOCKER_changing_bench",)
    lb1 = sweep(3.05, 4.7, 2.75, 2.95, 0.07)
    lb2 = sweep(3.05, 4.7, 5.05, 5.25, 0.07)
    S(r_towels, lb1, lb, LK, "COZY_L_towels", yaws=(0.05, 0.0))
    S(lambda: r_bottle("mustard"), lb1, lb, LK, "COZY_L_bottle1")
    S(r_headphones, lb1, lb, LK, "COZY_L_headphones", yaws=(0.3, 0.0))
    S(lambda: r_cushion("denim"), lb2, lb, LK, "COZY_L_cushion1", yaws=(0.1, 0.0))
    S(lambda: r_hardhat("mustard"), lb2, lb, LK, "COZY_L_hardhat1", yaws=(0.4, 0.0))
    S(lambda: r_mug("navy"), lb1, lb, LK, "COZY_L_mug1")
    S(r_clipboard, lb2, lb, LK, "COZY_L_clipboard", yaws=(-0.3, 0.0))
    S(lambda: r_tote("mustard"), lb1, lb, LK, "COZY_L_tote")
    S(r_towels, lb2, lb, LK, "COZY_L_towels2", yaws=(0.05, 0.0))
    S(lambda: r_hardhat("coral"), lb1, lb, LK, "COZY_L_hardhat2", yaws=(-0.4, 0.0))

    # ================= locker floor (never in the door-to-chamber route)
    lf = ("V_LOCKER_porcelain_tiles", "LOCKER_floor")
    S(r_doormat, sweep(2.3, 2.9, 3.3, 4.2, 0.1, near=(2.55, 3.72)), lf, LK, "COZY_L_doormat", yaws=(1.5708,), free=True)
    S(r_hamper, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(7.5, 1.6)), lf, LK, "COZY_L_hamper")
    S(r_hose, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(7.4, 6.5)), lf, LK, "COZY_L_hose")
    S(r_filters, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(5.9, 1.55)), lf, LK, "COZY_L_filters")
    S(r_stool, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(5.8, 6.5)), lf, LK, "COZY_L_stool")
    S(lambda: r_bottle("coral"), sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(5.3, 2.4)), lf, LK, "COZY_L_bottle2")
    S(r_duck, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(2.5, 1.4)), lf, LK, "COZY_L_duck")
    S(lambda: r_pouf("coral"), sweep(5.2, 8.0, 1.4, 6.9, 0.15, near=(7.4, 2.0)), lf, LK, "COZY_L_pouf")
    S(r_radio, sweep(5.2, 8.0, 1.4, 6.9, 0.15, near=(6.6, 1.4)), lf, LK, "COZY_L_radio", yaws=(0.0, 1.57))
    S(r_slippers, sweep(2.2, 8.0, 1.4, 6.9, 0.15, near=(6.3, 6.6)), lf, LK, "COZY_L_slippers", yaws=(0.4, 1.4))

    # ================= locker walls
    la = L_WALLS
    WA(w_mirror, W["LE"], rng(1.2, 6.9, 0.2), 1.55, la, LK, "COZY_L_mirror")
    WA(w_mirror, W["LE"], rng(1.2, 6.9, 0.2), 1.6, la, LK, "COZY_L_mirror2")
    WA(w_roster, W["LE"], rng(1.2, 6.9, 0.2), 1.7, la, LK, "COZY_L_roster")
    WA(w_hooks, W["LN"], rng(5.3, 8.0, 0.1), 1.95, la, LK, "COZY_L_hooks")
    WA(w_hooks, W["LS"], rng(5.3, 8.0, 0.1), 1.95, la, LK, "COZY_L_hooks2")
    WA(w_towelrack, W["LN"], rng(5.3, 8.0, 0.1), 1.25, la, LK, "COZY_L_towelrack")
    WA(w_clock, W["LN"], rng(5.3, 8.0, 0.1), 2.7, la, LK, "COZY_L_clock")
    WA(lambda: w_frame(0.5, 0.36, 2, "charcoal"), W["LS"], rng(5.3, 8.0, 0.1), 1.9, la, LK, "COZY_L_frame1")
    WA(lambda: w_frame(0.34, 0.46, 0, "walnut"), W["LN"], rng(5.3, 8.0, 0.1), 1.9, la, LK, "COZY_L_frame2")
    WA(lambda: w_frame(0.42, 0.56, 1, "oak"), W["LS"], rng(5.3, 8.0, 0.1), 1.85, la, LK, "COZY_L_frame3")
    WA(lambda: w_pennants(2.4, 9), W["LE"], rng(1.6, 6.6, 0.2), 3.05, la, LK, "COZY_L_pennants", anchors=[(-1.2, 0), (1.2, 0)])
    WA(lambda: w_stringlights(2.4, 9), W["LN"], rng(6.0, 7.2, 0.15), 2.85, la, LK, "COZY_L_lights",
       anchors=[(-1.2, 0), (1.2, 0)], light=((0, -0.1, 0.1), 18))
    WA(w_shelf, W["LS"], rng(5.3, 8.0, 0.1), 2.15, la, LK, "COZY_L_shelf")
    WA(w_plaque, W["LE"], rng(1.2, 6.9, 0.2), 2.05, la, LK, "COZY_L_plaque")
    WA(lambda: w_poster(1, 0.5, 0.7), W["LE"], rng(1.2, 6.9, 0.2), 1.6, la, LK, "COZY_L_poster1")
    WA(lambda: w_sun_mural(0.6), W["LE"], rng(1.2, 6.9, 0.15), 2.35, la, LK, "COZY_L_sun")
    WA(w_neon, W["LE"], rng(1.2, 6.9, 0.2), 2.3, la, LK, "COZY_L_neon", light=((0, 0, 0.15), 18, (1.0, 0.45, 0.35)))
    WA(w_cork, W["LE"], rng(1.2, 6.9, 0.2), 1.75, la, LK, "COZY_L_cork")

    bpy.context.view_layer.update()
    print("TRINKETS placed=%d skipped=%d" % (report["placed"], report["skipped"]))
    print("TRINKETS failed:", report["failed"])
    bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)


if __name__ == "__main__":
    main()
