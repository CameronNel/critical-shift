"""Headless OCRU builder. Factory empty only. Never attach to an occupied GUI."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))

import architecture
import cameras
import config
import labels
import lighting
import materials
import mesh as g
import ocru
import stations
import validate


def _argv():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return []


def _hash_sources():
    blob = []
    for p in sorted(Path(__file__).resolve().parent.glob("*.py")):
        blob.append(p.name + hashlib.sha256(p.read_bytes()).hexdigest())
    return hashlib.sha256("\n".join(blob).encode()).hexdigest()


def _purge():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _render(directory, names, samples, width, height, device):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    lighting.setup_cycles(scene, samples, device)
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    for name in names:
        scene.camera = bpy.data.objects[name]
        scene.render.filepath = str(directory / f"{name}.png")
        print("RENDER_CAMERA", name, flush=True)
        bpy.ops.render.render(write_still=True)


def build_scene():
    scene = bpy.context.scene
    scene.name = "CRITICAL_SHIFT_OCRU"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    for name in config.COLLECTIONS:
        g.collection(name)
    materials.build()
    labels.build()
    architecture.build()
    ocru.build()
    stations.build()
    lighting.build()
    cameras.build()
    lighting.setup_world(scene)
    scene["source_entrypoint"] = "build_ocru.py"
    scene["revision"] = config.REVISION
    scene["source_hash"] = _hash_sources()


def main():
    if not bpy.app.background:
        raise RuntimeError("Run in a new --background --factory-startup process; never the occupied GUI.")
    p = argparse.ArgumentParser()
    p.add_argument("--save", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--render", default="none")
    p.add_argument("--pass-name", default="review")
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--width", type=int, default=1600)
    p.add_argument("--height", type=int, default=900)
    p.add_argument("--device", default="CPU", choices=["CPU", "GPU"])
    p.add_argument("--open", default="")
    p.add_argument("--cold-start", action="store_true")
    args = p.parse_args(_argv())
    start = time.time()
    config.PRODUCTION.mkdir(parents=True, exist_ok=True)
    if args.cold_start and args.open:
        bpy.ops.wm.open_mainfile(filepath=args.open)
        report = validate.run(config.PRODUCTION / "cold_start_report.json", check_saved=True)
        if args.render != "none":
            names = list(config.CAMERAS) if args.render == "all" else args.render.split(",")
            _render(config.PRODUCTION / "renders" / "cold-start", names, args.samples, args.width, args.height, args.device)
        report["elapsed_seconds"] = time.time() - start
        (config.PRODUCTION / "cold_start_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("COLD_START", report["status"], flush=True)
        return
    _purge()
    build_scene()
    report = validate.run() if args.validate else {"status": "SKIPPED"}
    if args.save:
        config.BLEND.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(config.BLEND))
        if args.validate:
            report = validate.run(check_saved=True)
    if args.render != "none":
        names = list(config.CAMERAS) if args.render == "all" else [n for n in args.render.split(",") if n]
        _render(config.PRODUCTION / "renders" / args.pass_name, names, args.samples, args.width, args.height, args.device)
    elapsed = time.time() - start
    (config.PRODUCTION / "build_report.json").write_text(
        json.dumps(
            {
                "status": report.get("status"),
                "elapsed_seconds": elapsed,
                "blender_version": bpy.app.version_string,
                "source": str(Path(__file__).resolve()),
                "source_hash": _hash_sources(),
                "output": str(config.BLEND),
                "revision": config.REVISION,
                "device": args.device,
                "samples": args.samples,
                "validation": report,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("OCRU_BUILD_COMPLETE", elapsed, report.get("status"), flush=True)
    if report.get("status") == "FAIL":
        sys.exit(2)


if __name__ == "__main__":
    main()
