"""Objective layout checks for the spawn room (CHECKLIST.md 'Objective layout'), run on the canonical module.
    blender -b --factory-startup <module.blend> -P check_layout.py -- <out.json>
Every check records the numbers it used. A check that cannot be made from named objects is reported MISSING, not passed."""
import json
import math
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sc = bpy.context.scene
W = lambda o: o.matrix_world.translation


def coll_bounds(name):
    xs, ys = [], []
    for o in bpy.data.collections[name].objects:
        if o.type == "MESH" and not o.hide_render:
            for v in o.bound_box:
                w = o.matrix_world @ Vector(v)
                xs.append(w.x)
                ys.append(w.y)
    return min(xs), max(xs), min(ys), max(ys)


def cam_forward(cam):
    return (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()


res = {}


class Missing(Exception):
    pass


def need(name):
    o = bpy.data.objects.get(name)
    if o is None:
        raise Missing("object " + name)
    return o


def need_bounds(name):
    if bpy.data.collections.get(name) is None or not any(o.type == "MESH" for o in bpy.data.collections[name].objects):
        raise Missing("collection " + name)
    return coll_bounds(name)


def check(key, fn):
    """Run one check; a named object or collection that is absent is reported MISSING with its name, never an abort."""
    try:
        res[key] = fn()
    except Missing as e:
        res[key] = {"pass": None, "status": "MISSING: " + str(e)}


def c_sides():
    spawn = need("VALIDATE_Spawn")
    fwd = cam_forward(spawn)
    bx0, bx1, _, _ = need_bounds("BRIEFING_ROOM")
    lx0, lx1, _, _ = need_bounds("LOCKER_ROOM")
    sp = W(spawn)
    right = Vector((fwd.y, -fwd.x, 0)).normalized()          # camera's right in the plan
    lat = lambda p: (p - sp).dot(right)
    return {"pass": lat(Vector(((bx0 + bx1) / 2, 4, 0))) < 0 < lat(Vector(((lx0 + lx1) / 2, 4, 0))),
            "briefing_lateral_m": round(lat(Vector(((bx0 + bx1) / 2, 4, 0))), 2),
            "locker_lateral_m": round(lat(Vector(((lx0 + lx1) / 2, 4, 0))), 2)}


def c_exit():
    spawn, air = need("VALIDATE_Spawn"), need("AIRLOCK")
    fwd = cam_forward(spawn)
    sp = W(spawn)
    right = Vector((fwd.y, -fwd.x, 0)).normalized()
    ahead = (W(air) - sp).dot(Vector((fwd.x, fwd.y, 0)).normalized())
    lat_a = (W(air) - sp).dot(right)
    return {"pass": ahead > 5.0 and abs(lat_a) < 1.0, "airlock_ahead_m": round(ahead, 2), "airlock_lateral_m": round(lat_a, 2)}


ppe = sorted((o for o in sc.objects if o.type == "EMPTY" and len(o.name) == 6 and o.name.startswith("PPE_0")), key=lambda o: o.name)


def door_frame():
    door = need("VALIDATE_LockerDoor")
    df = cam_forward(door)
    dr = Vector((df.y, -df.x, 0)).normalized()
    return lambda p: (p - W(door)).dot(dr)


def c_stations():
    dl = door_frame()
    left = [o.name for o in ppe if dl(W(o)) < 0]
    right_ = [o.name for o in ppe if dl(W(o)) > 0]
    return {"pass": len(ppe) == 4 and len(left) == 2 and len(right_) == 2, "stations": [o.name for o in ppe],
            "left_of_locker_door_view": left, "right": right_}


def c_pod():
    dl = door_frame()
    pod = need("INTEGRITY_POD")
    if not ppe:
        raise Missing("objects PPE_0n")
    lats = [dl(W(o)) for o in ppe]
    return {"pass": min(lats) < dl(W(pod)) < max(lats) and abs(dl(W(pod)) - (min(lats) + max(lats)) / 2) < 0.5,
            "pod_lateral_m": round(dl(W(pod)), 2), "stations_lateral_range_m": [round(min(lats), 2), round(max(lats), 2)]}


def c_seats():
    seats = sum(int(o.get("seat_capacity", 0)) for o in sc.objects if o.type == "EMPTY")
    return {"pass": seats >= 4, "seat_capacity_total": seats}


check("briefing_left_locker_right", c_sides)
check("exit_forward", c_exit)
check("four_suit_stations_two_each_side", c_stations)
check("integrity_chamber_central", c_pod)
check("briefing_seating", c_seats)
# Owner decision: the Geiger/radiation check is a player-HUD element, not room geometry (spawnroom.md section 12).
res["geiger_station_at_exit"] = {"pass": None, "status": "N/A by owner decision: radiation readout is a HUD element, not built in the room"}

def c_route():
    spawn, air = need("VALIDATE_Spawn"), need("AIRLOCK")
    sp = W(spawn)
    # route: 0.3 m radius, five heights, from the spawn camera to the airlock along the straight hall line
    dg = bpy.context.evaluated_depsgraph_get()
    tris, verts = [], []
    for o in sc.objects:
        if o.type != "MESH" or o.hide_render or o.name.startswith(("BRIEFING_carpet",)):
            continue
        if o.name.startswith(("FACILITY_floor",)) or "ceiling" in o.name.lower():
            continue
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        base = len(verts)
        verts.extend(o.matrix_world @ v.co for v in m.vertices)
        for p in m.polygons:
            vs = list(p.vertices)
            for i in range(1, len(vs) - 1):
                tris.append((base + vs[0], base + vs[i], base + vs[i + 1]))
        e.to_mesh_clear()
    bvh = BVHTree.FromPolygons(verts, tris)
    start, end = Vector((sp.x, sp.y + 0.3, 0)), Vector((W(air).x, W(air).y - 1.0, 0))
    steps = int((end - start).length / 0.2)
    worst = 9.0
    hit_at = None
    for i in range(steps + 1):
        p = start + (end - start) * (i / steps)
        for h in (0.3, 0.7, 1.1, 1.5, 1.8):
            o3 = Vector((p.x, p.y, h))
            for a in range(8):
                d = Vector((math.cos(a * math.pi / 4), math.sin(a * math.pi / 4), 0))
                r = bvh.ray_cast(o3, d, 3.0)
                if r[0] is not None and r[3] < worst:
                    worst, hit_at = r[3], (round(p.x, 2), round(p.y, 2), h)
    return {"pass": worst >= 0.3, "min_clearance_m": round(worst, 2) if worst < 9 else None, "tightest_at": hit_at,
                              "method": "5 heights x 8 directions every 0.2 m, spawn to 1 m before the airlock, 3 m rays"}


check("primary_route_clear", c_route)
res["all_pass_or_missing"] = {k: v["pass"] for k, v in res.items()}
out = sys.argv[sys.argv.index("--") + 1]
json.dump(res, open(out, "w"), indent=1)
for k, v in res.items():
    if k != "all_pass_or_missing":
        print("LAYOUT", k, "PASS" if v["pass"] else ("MISSING" if v["pass"] is None else "FAIL"), {x: y for x, y in v.items() if x != "pass"})
