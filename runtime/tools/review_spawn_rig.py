"""Blender-only sampled pose/loop evidence and contact sheet for the exported rig."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def review(folder, output):
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((folder / "rig-bindings.json").read_text())
    asset = folder / "CrewWorker.fbx"
    if hashlib.sha256(asset.read_bytes()).hexdigest() != metadata["fbx_sha256"]:
        raise ValueError("The reviewed FBX differs from its binding record.")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(asset))
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    # Align the exported posterior contact to the authored 0.462m bench surface.
    support_height = metadata["seatedSupportHeight"]
    actions = {a.name.rsplit("|", 1)[-1]: a for a in bpy.data.actions}

    def pose(name, frame):
        action = actions[name]
        arm.animation_data.action = action
        arm.animation_data.action_slot = action.slots[0]
        bpy.context.scene.frame_set(frame)
        evaluated = arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return {b.name: list(evaluated.matrix_world @ b.head) for b in evaluated.pose.bones}

    samples = []
    for clip in metadata["clips"]:
        for frame in (clip["first"], (clip["first"] + clip["last"]) / 2, clip["last"]):
            # Subframes also exercise the interpolation rather than sampling key poses alone.
            whole = math.floor(frame)
            values = pose(clip["name"], whole)
            bpy.context.scene.frame_set(whole, subframe=frame - whole)
            evaluated = arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
            values = {b.name: list(evaluated.matrix_world @ b.head) for b in evaluated.pose.bones}
            if not all(math.isfinite(x) for p in values.values() for x in p):
                raise ValueError("Non-finite exported pose: " + clip["name"])
            samples.append({"clip": clip["name"], "frame": frame, "bones": values})
    first, last = pose("SPAWN_SEATED_IDLE", 0), pose("SPAWN_SEATED_IDLE", 48)
    seam = max((Vector(first[b]) - Vector(last[b])).length for b in first)
    if seam > 0.002:
        raise ValueError("The simple seated idle has a position seam greater than 2mm.")
    offset = bpy.data.objects.new("Runtime seated model offset", None)
    bpy.context.scene.collection.objects.link(offset)
    for obj in list(bpy.data.objects):
        if obj != offset and obj.parent is None: obj.parent = offset

    def matte(name, color):
        material = bpy.data.materials.new(name); material.diffuse_color = (*color, 1)
        material.use_nodes = True
        material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (*color, 1)
        return material

    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.data.materials.append(matte("QA floor", (0.08, 0.10, 0.13)))
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.06, 0.42), scale=(0.45, 0.24, 0.042))
    bench = bpy.context.object
    bench.data.materials.append(matte("Seat surface at 0.462m", (0.32, 0.18, 0.07)))
    for location, energy, size in [((3, 3, 5), 700, 4), ((-3, 1, 3), 450, 3)]:
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object; lamp.data.energy = energy; lamp.data.shape = "DISK"; lamp.data.size = size
        lamp.rotation_euler = (Vector((0, 0, 0.7)) - lamp.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.camera_add(location=(2.6, 3.8, 2.15))
    camera = bpy.context.object; camera.data.type = "ORTHO"; camera.data.ortho_scale = 1.9
    camera.rotation_euler = (Vector((0, 0.08, 0.72)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene = bpy.context.scene; scene.camera = camera
    scene.render.engine = "CYCLES"; scene.cycles.samples = 12; scene.cycles.use_denoising = True
    scene.render.resolution_x = 360; scene.render.resolution_y = 420; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("QA world"); scene.world.color = (0.15, 0.15, 0.15)
    images = []
    for name, frames in [("SPAWN_SIT_DOWN", (0, 9, 18)), ("SPAWN_SEATED_IDLE", (0, 24, 48)),
                         ("SPAWN_STAND_UP", (0, 9, 18)), ("SUIT_UP", (0, 32, 64))]:
        for frame in frames:
            suited = name == "SUIT_UP"
            offset.location.z = 0 if suited else 0.462 - support_height
            for record in metadata["meshes"]:
                bpy.data.objects[record["name"]].hide_render = not suited if record["suit"] else suited and bool(record["region"])
            bench.hide_render = suited
            pose(name, frame)
            path = output / (name + "-" + str(frame) + ".png")
            scene.render.filepath = str(path); bpy.ops.render.render(write_still=True)
            images.append((path, name + " f" + str(frame)))
    from PIL import Image, ImageDraw
    sheet = Image.new("RGB", (1080, 4 * 446), "#18202b"); draw = ImageDraw.Draw(sheet)
    for i, (path, label) in enumerate(images):
        x, y = i % 3 * 360, i // 3 * 446
        with Image.open(path) as rendered: sheet.paste(rendered, (x, y + 26))
        draw.text((x + 8, y + 6), label, fill="white")
    sheet.save(output / "poses.png")
    (output / "pose-evidence.json").write_text(json.dumps({"status": "SampledTechnicalChecksPassed",
        "asset_sha256": metadata["fbx_sha256"], "sample_count": len(samples), "poses": samples,
        "seated_idle_position_seam_metres": seam, "images": [p.name for p, _ in images],
        "real_time_playback": "NotRun", "native_unity": False,
        "limits": "Sampled transforms and still images do not prove continuous contacts or perceived timing."}, indent=2) + "\n")


if __name__ == "__main__":
    folder, output = sys.argv[sys.argv.index("--") + 1:]
    review(Path(folder), Path(output))
