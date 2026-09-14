"""Reproducible stills with the actual authorized render backend recorded."""
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
        "device": s.cycles.device,
        "cpu_threads": s.render.threads,
        "threads_mode": s.render.threads_mode,
        "process_priority": "IDLE" if s.cycles.device=='CPU' else "NORMAL",
        "gpu_denoising": bool(s.cycles.denoising_use_gpu),
        "gpu_backend": s.get('astra_gpu_backend') if s.cycles.device=='GPU' else None,
        "gpu_devices": s.get('astra_gpu_devices') if s.cycles.device=='GPU' else None,
        "hardware_raytracing": s.get('astra_hardware_raytracing') if s.cycles.device=='GPU' else False,
        "persistent_data": s.render.use_persistent_data,
        "samples": samples,
        "resolution": [width, height],
        "render_settings": {key:getattr(s.cycles,key) for key in ['max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','transparent_max_bounces','sample_clamp_indirect','adaptive_threshold','seed','denoiser']},
        "renderer_source_sha256": {name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in ['render.py','resource_guard.py']},
        "cameras": [],
    }
    manifest_path = out / 'render_manifest.json'
    if any(name.startswith('S0') for name in names):
        for name in ['astra_evidence.py','kit.py']:
            log['renderer_source_sha256'][name]=hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding='utf-8'))
        assert previous.get('engine')==s.render.engine, 'Never mix CPU/Cycles and historical EEVEE evidence'
        assert previous.get('samples')==samples and previous.get('resolution')==[width,height], 'Use a separate preview folder for different render settings'
        assert previous.get('blend_sha256')==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(), 'Never mix saved scene revisions'
        assert previous.get('render_settings')==log['render_settings'], 'Render settings changed within the pack'
        assert previous.get('device')==log['device'] and previous.get('gpu_backend')==log['gpu_backend'], 'Render device changed within the pack'
        for field in ['cpu_threads','threads_mode','process_priority','gpu_denoising','gpu_devices','hardware_raytracing','persistent_data']:
            assert previous.get(field)==log[field], f'Resource/backend setting changed within the pack: {field}'
        assert previous.get('renderer_source_sha256')==log['renderer_source_sha256'], 'Renderer source changed within the pack'
        log['cameras'] = [entry for entry in previous.get('cameras', []) if entry['camera'] not in names]
    log['process_id'] = __import__('os').getpid()
    log['source_revision'] = s.get('source_revision')
    log['blend_sha256'] = hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    source_dir=out/'renderer-source';source_dir.mkdir(exist_ok=True)
    for name,digest in log['renderer_source_sha256'].items():
        target=source_dir/name;content=(Path(__file__).parent/name).read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'Renderer source changed while preparing evidence'
        if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==digest, 'Preserved renderer source differs'
        else:target.write_bytes(content)
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
                "matrix_world": [list(row) for row in cam.matrix_world],
                "process_id": __import__('os').getpid(),
            }
        )
        (out / "render_manifest.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
        print("CONDENSER_CAMERA_DONE", name, flush=True)
    print("CONDENSER_RENDER_OK", revision, flush=True)
    return log
