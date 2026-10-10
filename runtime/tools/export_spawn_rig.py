"""Blender derivative exporter; reuses existing rig/clip builders without rewriting them."""
import hashlib
import json
import sys
from pathlib import Path
import bpy


def main():
    source, output, commit = sys.argv[sys.argv.index("--") + 1:]
    source, output = Path(source), Path(output)
    sys.path.insert(0, str(source))
    import character_worker as worker
    import character_suit as suit
    import character_rig as rig
    import character_clips as character_clips  # Registers the existing 43 clips, including SUIT_UP.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    root, _ = worker.build_worker()
    suit.build_hazmat(root)
    suit.equip(root)
    arm = rig.build_rig(root)
    rig.skin_worker(root, arm)
    clips = []
    for name, (build, _tool) in rig.ACTIONS.items():
        build(arm)
        action = bpy.data.actions[name]
        clips.append({"name": name, "first": action.frame_range[0], "last": action.frame_range[1],
                      "loop": bool(action.get("cs_loop", True))})
        print("REUSE CLIP", name, flush=True)
    # Minimal room-only derivatives on the unchanged skeleton. The 49 existing clips remain unchanged.
    seated = dict(character_clips.STAND, hips=(0, 0, -0.20),
                  lf=character_clips.foot("Left", y=0.34), rf=character_clips.foot("Right", y=0.34))
    derivatives = [
        character_clips.clip("SPAWN_SIT_DOWN", 18, [(0, character_clips.STAND), (1, seated)]),
        character_clips.clip("SPAWN_SEATED_IDLE", 48, [(0, seated), (1, seated)], loop=True),
        character_clips.clip("SPAWN_STAND_UP", 18, [(0, seated), (1, character_clips.STAND)]),
    ]
    for clip in derivatives:
        action = clip.build(arm)
        clips.append({"name": clip.name, "first": action.frame_range[0], "last": action.frame_range[1],
                      "loop": bool(action.get("cs_loop", False)), "derivative": True})
    rig.set_action(arm, "IDLE")
    bpy.context.scene.frame_set(0)
    meshes = [o for o in arm.children_recursive if o.type == "MESH" and not o.get("cs_tool")]
    records = [{"name": o.name, "suit": o.name.startswith("SUIT_"), "head": bool(o.get("cs_head_rigid")),
                "region": str(o.get("cs_region", "")), "visible_unsuited": not o.name.startswith("SUIT_")} for o in meshes]
    # Export both outfit projections. Their visibility is owned by WorkerAnimation after import.
    bpy.ops.object.select_all(action="DESELECT")
    for o in [arm, *meshes]:
        o.hide_set(False); o.hide_viewport = False; o.hide_render = False; o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.context.scene.render.fps = 24
    path = output / "CrewWorker.fbx"
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"ARMATURE", "MESH"},
        add_leaf_bones=False, primary_bone_axis="Y", secondary_bone_axis="X", axis_forward="-Z", axis_up="Y",
        bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", path_mode="COPY", embed_textures=True)
    report = {"rig_commit": commit, "fps": 24, "in_place": True, "unity_rig": "Generic (existing skeleton, no retargeting)",
              "source_forward": "+Y", "source_up": "+Z", "fbx_forward": "-Z", "fbx_up": "+Y", "unit": "metre",
              "bones": [b.name for b in arm.data.bones], "meshes": records, "clips": clips, "seatedSupportHeight": 0.34,
              "fbx_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "native_unity": "NotRun: validate this export in the pinned editor",
              "limits": "Source clip contact defects remain. Three simple sitting derivatives fill the source inventory gap. No preview props exported."}
    (output / "rig-bindings.json").write_text(json.dumps(report, indent=2) + "\n")
    # Verify actual export in a fresh empty Blender scene, rather than declaring success from the operator result.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    imported = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(imported) != 1 or set(b.name for b in imported[0].data.bones) != set(report["bones"]):
        raise ValueError("FBX round trip changed the skeleton.")
    actions = {a.name.rsplit("|", 1)[-1] for a in bpy.data.actions}
    if set(c["name"] for c in clips) != actions:
        raise ValueError("FBX round trip changed the clip inventory: " + str(sorted(actions)))
    (output / "rig-roundtrip.json").write_text(json.dumps({"status": "Passed", "bones": len(report["bones"]),
        "clips": len(clips), "native_unity": False, "real_time_playback": "NotRun"}, indent=2) + "\n")


if __name__ == "__main__": main()
