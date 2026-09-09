"""Objective geometry, clearance, support-contact and camera checks."""
from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector

import config
import mesh as g


def _bbox(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs, ys, zs = zip(*corners)
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def _ray_support(anchor, direction, max_dist=0.25):
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    origin = Vector(anchor) - direction * 0.002
    hit, loc, nrm, idx, obj, mat = scene.ray_cast(deps, origin, direction, distance=max_dist)
    if not hit:
        return None
    gap = (loc - Vector(anchor)).dot(direction)
    return {"object": obj.name if obj else None, "gap": gap, "normal": list(nrm)}


DIR = {
    "WORLD_-Z": Vector((0, 0, -1)),
    "WORLD_+Z": Vector((0, 0, 1)),
    "WORLD_-Y": Vector((0, -1, 0)),
    "WORLD_+Y": Vector((0, 1, 0)),
    "WORLD_-X": Vector((-1, 0, 0)),
    "WORLD_+X": Vector((1, 0, 1)),
}


def _fix_dir():
    DIR["WORLD_+X"] = Vector((1, 0, 0))


def _plan_clear(x, y, blockers, radius=0.18):
    for mn in blockers:
        if mn[0] - radius <= x <= mn[3] + radius and mn[1] - radius <= y <= mn[4] + radius:
            return False
    return True


def run(path=None, check_saved=False):
    _fix_dir()
    fails = []
    notes = []
    bpy.context.view_layer.update()
    scene = bpy.context.scene

    # Cameras
    for name in config.CAMERAS:
        if name not in bpy.data.objects:
            fails.append(f"missing camera {name}")
        else:
            cam = bpy.data.objects[name]
            if cam.location.z < 1.2 or cam.location.z > 1.9:
                if name not in {"CAM_MATERIALS", "CAM_RECOVERY"}:
                    notes.append(f"{name} eye height {cam.location.z:.2f}")

    # Door clear
    door_ok = True
    for obj in scene.objects:
        if not obj.get("ocru_authored") or obj.type != "MESH":
            continue
        if obj.name.startswith("Door_leaf") or obj.name.startswith("Door_frame") or obj.name.startswith("Door_"):
            continue
        if "Wall_S" in obj.name or obj.name.startswith("Ext_"):
            continue
        bb = _bbox(obj)
        # objects blocking the clear opening x -1.1..1.1, y -0.02..0.15, z 0.1..2.5
        if bb[3] > -1.05 and bb[0] < 1.05 and bb[4] > -0.02 and bb[1] < 0.12 and bb[5] > 0.15 and bb[2] < 2.45:
            if "grate" not in obj.name.lower() and "Mark" not in obj.name and "sill" not in obj.name.lower():
                fails.append(f"door clear blocked by {obj.name}")
                door_ok = False
                break
    if door_ok:
        notes.append("door clear opening unobstructed by non-door meshes")

    # Berth size
    pads = [o for o in scene.objects if o.name.startswith("OCRU_pad_")]
    if pads:
        bbs = [_bbox(o) for o in pads]
        span_x = max(b[3] for b in bbs) - min(b[0] for b in bbs)
        span_y = max(b[4] for b in bbs) - min(b[1] for b in bbs)
        z = max(b[5] for b in bbs)
        if span_x < 0.80 or span_x > 1.05:
            fails.append(f"berth width {span_x:.3f}")
        if span_y < 2.00 or span_y > 2.45:
            fails.append(f"berth length {span_y:.3f}")
        if z < 0.95 or z > 1.15:
            fails.append(f"berth surface {z:.3f}")
        notes.append(f"berth span {span_x:.3f} x {span_y:.3f} z={z:.3f}")
    else:
        fails.append("no OCRU pads")

    # Support contacts
    for rec in g.supports():
        direction = DIR.get(rec["direction"])
        if direction is None:
            fails.append(f"bad support dir {rec['object']} {rec['direction']}")
            continue
        if rec["object"] not in bpy.data.objects:
            fails.append(f"support object missing {rec['object']}")
            continue
        for i, anc in enumerate(rec["anchors"]):
            hit = _ray_support(anc, direction)
            if hit is None:
                fails.append(f"support miss {rec['object']}[{i}] -> {rec['target']}")
                continue
            gap = hit["gap"]
            if gap > rec["max_gap"]:
                fails.append(f"support gap {rec['object']}[{i}] {gap*1000:.1f}mm > {rec['max_gap']*1000:.1f}")
            if gap < -rec["max_pen"]:
                fails.append(f"support pen {rec['object']}[{i}] {gap*1000:.1f}mm")

    # Plan occupancy of named equipment vs reserved arrival lane
    blockers = []
    for name in ["OCRU_plinth", "Con_body", "CartBank", "Batt", "Rec_frame", "Bench", "Trolley_frame", "Util_top"]:
        if name in bpy.data.objects:
            blockers.append(_bbox(bpy.data.objects[name]))
    arrival_fail = 0
    samples = 0
    y = 0.3
    while y < 3.1:
        x = -1.0
        while x < 1.0:
            samples += 1
            if not _plan_clear(x, y, blockers, radius=0.05):
                arrival_fail += 1
            x += 0.25
        y += 0.25
    if arrival_fail > samples * 0.08:
        fails.append(f"arrival lane occupancy {arrival_fail}/{samples}")
    else:
        notes.append(f"arrival lane blocked samples {arrival_fail}/{samples}")

    # East bypass with simulated dropped body at (0,1.9)
    body = (-0.90, 1.55, 0, 0.90, 2.25, 0.4)
    bypass_ok = 0
    bypass_n = 0
    y = 2.7
    while y < 8.0:
        bypass_n += 1
        if _plan_clear(2.05, y, blockers + [body], radius=0.20):
            bypass_ok += 1
        y += 0.3
    if bypass_ok < bypass_n * 0.7:
        fails.append(f"east bypass with ragdoll {bypass_ok}/{bypass_n}")
    else:
        notes.append(f"east bypass with ragdoll {bypass_ok}/{bypass_n}")

    # Materials assigned
    missing_mat = 0
    for o in scene.objects:
        if o.type == "MESH" and o.get("ocru_authored") and not o.data.materials:
            missing_mat += 1
    if missing_mat:
        fails.append(f"{missing_mat} meshes without materials")

    # Collection presence
    for c in config.COLLECTIONS:
        if c not in bpy.data.collections:
            fails.append(f"missing collection {c}")

    if check_saved and not bpy.data.filepath:
        fails.append("blend not saved")

    report = {
        "status": "PASS" if not fails else "FAIL",
        "failures": fails,
        "notes": notes,
        "object_count": len(scene.objects),
        "mesh_count": sum(1 for o in scene.objects if o.type == "MESH"),
        "support_count": len(g.supports()),
        "cameras": list(config.CAMERAS),
        "revision": config.REVISION,
    }
    out = Path(path) if path else config.PRODUCTION / "validation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("VALIDATE", report["status"], "fails", len(fails), "objects", report["object_count"], flush=True)
    for f in fails:
        print("FAIL", f, flush=True)
    return report
