"""CPU-only stills under the user's game-performance resource limit."""
import hashlib
import json
import time
from pathlib import Path

import bpy
from resource_guard import configure_scene


def render_set(root, revision, selection, samples=32, width=1920, height=1080):
    s = bpy.context.scene
    configure_scene(s,samples)
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
        "device": "CPU",
        "cpu_threads": 2,
        "process_priority": "IDLE",
        "gpu_denoising": False,
        "samples": samples,
        "resolution": [width, height],
        "cameras": [],
    }
    manifest_path = out / 'render_manifest.json'
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding='utf-8'))
        assert previous.get('engine')==s.render.engine, 'Never mix CPU/Cycles and historical EEVEE evidence'
        assert previous.get('samples')==samples and previous.get('resolution')==[width,height], 'Use a separate preview folder for different render settings'
        assert previous.get('blend_sha256')==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(), 'Never mix saved scene revisions'
        log['cameras'] = [entry for entry in previous.get('cameras', []) if entry['camera'] not in names]
    log['process_id'] = __import__('os').getpid()
    log['source_revision'] = s.get('source_revision')
    log['blend_sha256'] = hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
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
                "process_id": __import__('os').getpid(),
            }
        )
        (out / "render_manifest.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
        print("CONDENSER_CAMERA_DONE", name, flush=True)
    print("CONDENSER_RENDER_OK", revision, flush=True)
    return log
