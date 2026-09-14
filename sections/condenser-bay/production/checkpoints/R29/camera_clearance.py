"""CPU: fail cameras that start inside geometry or hit within 0.35 m."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "production" / "validation"
out.mkdir(parents=True, exist_ok=True)
deps = bpy.context.evaluated_depsgraph_get()
rows = []
for cam in [o for o in bpy.context.scene.objects if o.type == "CAMERA"]:
    origin = cam.matrix_world.translation
    forward = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    hit, loc, nrm, idx, obj, mat = bpy.context.scene.ray_cast(deps, origin, forward, distance=0.35)
    dist = (loc - origin).length if hit else None
    rows.append(
        {
            "camera": cam.name,
            "origin": list(origin),
            "hit": bool(hit),
            "dist": dist,
            "blocker": obj.name if obj else None,
            "ok": not hit,
        }
    )
rep = {"revision": bpy.context.scene.get("source_revision"), "cameras": rows, "failed": [r for r in rows if not r["ok"]]}
(out / f"{rep['revision']}-camera-clearance.json").write_text(json.dumps(rep, indent=2, default=str), encoding="utf-8")
print("CAMERA_CLEARANCE", json.dumps({"failed": [r['camera'] for r in rep['failed']], "count": len(rows)}), flush=True)
