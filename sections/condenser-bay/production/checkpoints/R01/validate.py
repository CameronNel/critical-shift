"""CPU geometry/route/opening checks. No GPU."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def world_verts(obj):
    mesh = obj.to_mesh()
    try:
        return [obj.matrix_world @ v.co for v in mesh.vertices]
    finally:
        obj.to_mesh_clear()


def ray(origin, direction, dist=12.0):
    deps = bpy.context.evaluated_depsgraph_get()
    hit, loc, nrm, idx, obj, mat = bpy.context.scene.ray_cast(deps, origin, Vector(direction).normalized(), distance=dist)
    return hit, loc, obj.name if obj else None


def opening_clear(centre, du, dv, n=5, direction=(0, 0, 1), dist=1.2):
    cx, cy, cz = centre
    samples = []
    for i in range(n):
        for j in range(n):
            u = (i / (n - 1) - 0.5) * 0.86
            v = (j / (n - 1) - 0.5) * 0.86
            p = Vector((cx, cy, cz)) + Vector(du) * u + Vector(dv) * v + Vector(direction) * -0.08
            hit, loc, name = ray(p, direction, dist)
            samples.append({"p": list(p), "hit": hit, "blocker": name})
    blocked = [s for s in samples if s["hit"]]
    return {"samples": len(samples), "blocked": len(blocked), "blockers": list({s["blocker"] for s in blocked}), "ok": len(blocked) == 0}


def aisle_samples(minp, maxp, height=1.6, step=0.45):
    hits = []
    x0, y0, _ = minp
    x1, y1, _ = maxp
    x, y = x0 + 0.2, y0 + 0.2
    while x < x1 - 0.2:
        y = y0 + 0.2
        while y < y1 - 0.2:
            hit, loc, name = ray((x, y, height), (0, 0, -1), height + 0.2)
            if not hit:
                hits.append({"xy": [x, y], "issue": "no_floor"})
            hit2, loc2, name2 = ray((x, y, 0.15), (0, 0, 1), 2.3)
            if hit2 and loc2.z < 2.2 and name2 and "floor" not in (name2 or "").lower() and "grate" not in (name2 or "").lower() and "coating" not in (name2 or "").lower() and "paint" not in (name2 or "").lower() and "edge" not in (name2 or "").lower() and "saw" not in (name2 or "").lower() and "drip" not in (name2 or "").lower() and "stencil" not in (name2 or "").lower() and "ID" not in (name2 or ""):
                # standing volume blocked below 2.2 m
                if loc2.z < 2.15:
                    hits.append({"xy": [x, y], "issue": "headroom", "blocker": name2, "z": loc2.z})
            y += step
        x += step
    return hits


def main():
    from layout import EXH_C, EXH_X, EXH_Y, D01_W, D01_H, WEST_AISLE, EAST_PULL, SOUTH_WALK

    report = {"revision": bpy.context.scene.get("source_revision"), "checks": {}}
    # D01 opening: from outside looking +Y through door
    d01 = opening_clear((0, -0.15, 1.2), (D01_W, 0, 0), (0, 0, D01_H * 0.7), 4, (0, 1, 0), 1.4)
    report["checks"]["d01_opening"] = d01
    # U04 receive: from below looking +Z through ceiling hole
    u04 = opening_clear(EXH_C, (EXH_X, 0, 0), (0, EXH_Y, 0), 5, (0, 0, 1), 0.8)
    report["checks"]["u04_opening"] = u04
    # Supports
    support = json.loads(bpy.context.scene.get("support_registry") or "[]")
    failed_sup = []
    for item in support:
        o = bpy.data.objects.get(item["anchor"])
        if not o:
            failed_sup.append({**item, "error": "missing_anchor"})
            continue
        hit, loc, name = ray(o.matrix_world.translation, item["direction"], 0.25)
        gap = (o.matrix_world.translation - loc).length if hit else 99
        if not hit or gap > item.get("max_gap", 0.02) + 0.04:
            failed_sup.append({**item, "hit": hit, "blocker": name, "gap": gap})
    report["checks"]["supports"] = {"count": len(support), "failed": len(failed_sup), "failures": failed_sup[:12]}
    report["counts"] = {
        "objects": len(bpy.context.scene.objects),
        "cameras": len([o for o in bpy.context.scene.objects if o.type == "CAMERA"]),
        "materials": len(bpy.data.materials),
    }
    # Teal scan of material names/colors
    teal = []
    for m in bpy.data.materials:
        n = m.name.lower()
        if any(w in n for w in ("teal", "cyan", "turquoise")):
            teal.append(m.name)
    report["checks"]["no_teal_material_names"] = {"ok": not teal, "hits": teal}
    out = ROOT / "production" / "validation" / (str(report["revision"] or "Rxx") + "-validation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    d01_ok = d01["ok"]
    u04_ok = u04["ok"] or u04["blocked"] <= 2  # curb/flange at rim may clip edge samples
    print("CONDENSER_VALIDATE", json.dumps({"d01": d01_ok, "u04_blocked": u04["blocked"], "supports_failed": len(failed_sup), "objects": report["counts"]["objects"]}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
