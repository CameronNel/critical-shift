"""EEVEE stills. Must run inside a process that already holds gpu_gate.py."""
import hashlib
import json
import time
from pathlib import Path

import bpy


def render_set(root, revision, selection, samples=32, width=1920, height=1080):
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE"
    s.eevee.use_raytracing = False
    s.eevee.taa_render_samples = max(16, samples)
    s.render.resolution_x = width
    s.render.resolution_y = height
    s.render.image_settings.file_format = "PNG"
    out = Path(root) / "production" / "renders" / "review" / revision
    out.mkdir(parents=True, exist_ok=True)
    names = (
        sorted(o.name for o in s.objects if o.type == "CAMERA")
        if selection in ("all", "")
        else [n.strip() for n in selection.split(",") if n.strip()]
    )
    log = {
        "revision": revision,
        "engine": s.render.engine,
        "raytracing": bool(s.eevee.use_raytracing),
        "samples": samples,
        "resolution": [width, height],
        "cameras": [],
    }
    print("CONDENSER_RENDER_START", revision, names, flush=True)
    for name in names:
        cam = s.objects[name]
        s.camera = cam
        path = out / (name + ".png")
        s.render.filepath = str(path)
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        log["cameras"].append(
            {
                "camera": name,
                "seconds": round(time.time() - t0, 2),
                "sha256": digest,
                "location": list(cam.location),
                "lens": cam.data.lens,
            }
        )
        (out / "render_manifest.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
        print("CONDENSER_CAMERA_DONE", name, flush=True)
    print("CONDENSER_RENDER_OK", revision, flush=True)
    return log
