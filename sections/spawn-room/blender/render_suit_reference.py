#!/usr/bin/env python3
"""Render the owner-reference suit with the existing Cycles studio helpers.

blender -b --factory-startup -noaudio --python-exit-code 1 \
  --python render_suit_reference.py -- --output DIR --save SCENE.blend

Use --loaded after opening the saved SCENE.blend to review a cold start. The
reference camera and front/side/back cameras remain fixed between review rounds.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import character_suit as CS
import character_worker as CW
from cozy_geo import tri_count
from render_character_sheet import studio, shoot
from render_worker import backdrop

VIEWS = {
    "hero": ((-2.3, 4.8, 2.05), (0, 0, 0.83), 76),
    "front": ((0, 5.32, 1.58), (0, 0, 0.83), 76),
    "side": ((-5.32, 0, 1.58), (0, 0, 0.83), 76),
    "back": ((0, -5.32, 1.58), (0, 0, 0.83), 76),
}


def evidence(scene, root):
    meshes = [
        o for o in root.children_recursive if o.type == "MESH" and not o.hide_render
    ]
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [
        o.matrix_world @ Vector(c)
        for o in meshes
        for c in o.evaluated_get(dg).bound_box
    ]
    missing = [
        im.filepath
        for im in bpy.data.images
        if im.source == "FILE"
        and not im.packed_file
        and not Path(bpy.path.abspath(im.filepath)).is_file()
    ]
    covers = set().union(
        *(set(o.get("cs_covers", [])) for o in root.children_recursive)
    )
    failures = []
    if missing:
        failures.append("Missing texture images")
    if (
        not {
            "TORSO",
            "ARM_L",
            "ARM_R",
            "LEG_L",
            "LEG_R",
            "HAND_L",
            "HAND_R",
            "FOOT_L",
            "FOOT_R",
        }
        <= covers
    ):
        failures.append("Incomplete equip region coverage")
    for o in meshes:
        if not o.data.materials:
            failures.append("No material: " + o.name)
        if any(not math.isfinite(c) for v in o.data.vertices for c in v.co):
            failures.append("Nonfinite mesh coordinates: " + o.name)
    # These are source/evaluated authoring counts, not draw calls or runtime cost.
    evaluated_tris = 0
    for o in meshes:
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        evaluated_tris += len(me.loop_triangles)
        o.evaluated_get(dg).to_mesh_clear()
    return {
        "blender": bpy.app.version_string,
        "python": sys.version.split()[0],
        "file": bpy.data.filepath,
        "root": root.name,
        "style": root.get("cs_suit_style"),
        "visible_meshes": len(meshes),
        "source_triangles": sum(tri_count(o) for o in meshes),
        "evaluated_triangles": evaluated_tris,
        "bounds_m": {
            axis: [min(p[i] for p in pts), max(p[i] for p in pts)]
            for i, axis in enumerate("xyz")
        },
        "covered_regions": sorted(covers),
        "missing_images": missing,
        "renderer": scene.render.engine,
        "device": scene.cycles.device,
        "color_transform": scene.view_settings.view_transform,
        "samples": scene.cycles.samples,
        "technical_failures": failures,
        "runtime_validation": "Not performed; hero authoring geometry",
        "visual_acceptance": "Requires pixel review; these checks do not establish an exact reference match",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--save", type=Path)
    parser.add_argument("--loaded", action="store_true")
    parser.add_argument("--style", choices=("reference", "legacy"), default="reference")
    parser.add_argument("--views", nargs="+", choices=VIEWS, default=list(VIEWS))
    parser.add_argument("--width", type=int, default=810)
    parser.add_argument("--samples", type=int, default=48)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
    args.output.mkdir(parents=True, exist_ok=True)
    if args.loaded:
        scene = bpy.context.scene
        root = bpy.data.objects["WORKER"]
        cam = scene.camera
    else:
        scene, cam = studio((args.width, round(args.width * 4 / 3)), args.samples)
        bpy.context.preferences.system.audio_device = "None"
        backdrop(scene)
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.40
        # Reuse the studio lights, moving the broad key reflection above the eyes.
        lights = [o for o in scene.objects if o.type == "LIGHT"]
        lights[0].location = (2.5, 1.6, 3.6)
        lights[0].data.energy = 210
        lights[0].data.shape = "RECTANGLE"
        lights[0].data.size = 1.1
        lights[0].data.size_y = 1.5
        lights[1].data.energy = 90
        lights[1].data.shape = "DISK"
        lights[2].data.energy = 170
        bpy.data.objects["floor"].scale.y = 0.32
        bpy.data.objects["floor"].rotation_euler.z = math.atan2(2.3, 4.8)
        for light in lights:
            light.rotation_euler = (
                (Vector((0, 0, 0.95)) - light.location)
                .to_track_quat("-Z", "Y")
                .to_euler()
            )
        root, _ = CW.build_worker()
        CS.build_hazmat(root, style=args.style)
        CS.equip(root)
        cam.data.sensor_fit = "VERTICAL"
        cam.data.sensor_height = 32
        cam.location, target, cam.data.lens = VIEWS["hero"]
        cam.rotation_euler = (
            (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        )
        # All four named inspection cameras are saved in the editable scene.
        for label, (loc, target, lens) in VIEWS.items():
            data = cam.data.copy()
            c = bpy.data.objects.new("SUIT_REVIEW_" + label.upper(), data)
            scene.collection.objects.link(c)
            c.location = loc
            c.rotation_euler = (
                (Vector(target) - c.location).to_track_quat("-Z", "Y").to_euler()
            )
            c.data.lens = lens
        bpy.ops.file.pack_all()
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 5
    scene.cycles.samples = args.samples
    scene.render.resolution_x = args.width
    scene.render.resolution_y = round(args.width * 4 / 3)
    scene.render.resolution_percentage = 100
    scene.cycles.seed = 31
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.save.resolve()))
    report = evidence(scene, root)
    report["cold_start"] = args.loaded
    report["camera_settings"] = {
        label: dict(location=loc, target=tgt, lens_mm=lens)
        for label, (loc, tgt, lens) in VIEWS.items()
    }
    (args.output / "VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n")
    if report["technical_failures"]:
        raise RuntimeError(report["technical_failures"])
    for label in args.views:
        loc, target, lens = VIEWS[label]
        shoot(cam, loc, target, lens, str(args.output / ("suit_" + label + ".png")))
    if len(args.views) == 4:
        from PIL import Image

        sheet = Image.new("RGB", (args.width * 4, scene.render.resolution_y))
        for i, label in enumerate(VIEWS):
            with Image.open(args.output / ("suit_" + label + ".png")) as im:
                sheet.paste(im.convert("RGB"), (i * args.width, 0))
        sheet.save(args.output / "suit_turnaround.png")
    print("SUIT_REFERENCE_VALIDATION", json.dumps(report))


if __name__ == "__main__":
    main()
