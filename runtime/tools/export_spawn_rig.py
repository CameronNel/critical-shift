"""Blender derivative exporter; reuses existing rig/clip builders without rewriting them."""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_spawn_materials import bake_atlas, constant_inputs


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
    deliver(arm, output, commit, clips)


def deliver(arm, output, commit, clips):
    # Appearance reimports retain the previously validated animation payload.
    # Fresh workspaces export source actions before touching delivery UV/materials.
    animation_path=output/"CrewWorkerAnimations.fbx"
    previous_path=output/"rig-bindings.json"
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else None
    if previous and previous["rig_commit"]==commit:
        old=output/previous.get("animationFile","CrewWorker.fbx")
        expected=previous.get("animationSha256",previous["fbx_sha256"])
        if hashlib.sha256(old.read_bytes()).hexdigest()!=expected: raise ValueError("Stale animation export")
        if old!=animation_path: shutil.copy2(old,animation_path)
    else:
        export_fbx(arm, output, animation_path, animated=True)
    meshes = [o for o in arm.children_recursive if o.type == "MESH" and not o.get("cs_tool")]
    records = [{"name": o.name, "suit": o.name.startswith("SUIT_"), "head": bool(o.get("cs_head_rigid")),
                "node": o.name, "region": str(o.get("cs_region", "")), "visible_unsuited": not o.name.startswith("SUIT_")} for o in meshes]
    def geometry_digest():
        data=[(o.name, [list(v.co) for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons],
               [[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]) for o in meshes]
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()
    geometry_before=geometry_digest()
    reference=os.environ.get("CS_SUIT_REFERENCE")
    if reference:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(reference).resolve()))
    for o in meshes:
        if o.name.startswith("SUIT_"):
            o.hide_set(False); o.hide_viewport=False; o.hide_render=False
    map_package=next(p for p in json.loads((output/"map-bindings.json").read_text())["materials"] if p["room"]=="spawn-room")
    surfaces=bake_atlas(bpy.context.scene,[o for o in meshes if o.name.startswith("SUIT_")],records,output,
                        map_package["sourceView"],"worker-suit")
    surfaces["atlases"]=[surfaces["maps"]]
    for d in surfaces["definitions"]: d["atlas"]=0
    bind_character_surfaces(meshes,records,surfaces,output)
    if geometry_digest()!=geometry_before: raise ValueError("Suit surfacing changed geometry or skin weights")
    # Export both outfit projections. Their visibility is owned by WorkerAnimation after import.
    path = output / "CrewWorker.fbx"
    export_fbx(arm, output, path, animated=False)
    report = {"rig_commit": commit, "fps": 24, "in_place": True, "unity_rig": "Generic (existing skeleton, no retargeting)",
              "source_forward": "+Y", "source_up": "+Z", "fbx_forward": "-Z", "fbx_up": "+Y", "unit": "metre",
              "bones": [b.name for b in arm.data.bones], "meshes": records, "clips": clips, "seatedSupportHeight": 0.34,
              "surfaces": surfaces, "geometry_and_weights_sha256":geometry_before,
              "animationFile":animation_path.name,"animationSha256":hashlib.sha256(animation_path.read_bytes()).hexdigest(),
              "fbx_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "native_unity": "NotRun: validate this export in the pinned editor",
              "limits": "Source clip contact defects remain. Three simple sitting derivatives fill the source inventory gap. No preview props exported."}
    (output / "rig-bindings.json").write_text(json.dumps(report, indent=2) + "\n")
    # Verify actual export in a fresh empty Blender scene, rather than declaring success from the operator result.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    imported = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(imported) != 1 or set(b.name for b in imported[0].data.bones) != set(report["bones"]):
        raise ValueError("FBX round trip changed the skeleton.")
    rest={b.name:[list(row) for row in b.matrix_local] for b in imported[0].data.bones}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(animation_path))
    animation_arm=next(o for o in bpy.data.objects if o.type=="ARMATURE")
    if rest!={b.name:[list(row) for row in b.matrix_local] for b in animation_arm.data.bones}:
        raise ValueError("Animation and suit skeleton bind poses differ")
    actions = {a.name.rsplit("|", 1)[-1] for a in bpy.data.actions}
    if set(c["name"] for c in clips) != actions:
        raise ValueError("FBX round trip changed the clip inventory: " + str(sorted(actions)))
    (output / "rig-roundtrip.json").write_text(json.dumps({"status": "Passed", "bones": len(report["bones"]),
        "clips": len(clips), "native_unity": False, "real_time_playback": "NotRun"}, indent=2) + "\n")


def bind_character_surfaces(meshes, records, surfaces, output):
    """Keep authored face decals and uniform body inputs visible behind the visor."""
    definitions={}
    for o in meshes:
        if o.name.startswith("SUIT_"): continue
        record=next(r for r in records if r["name"]==o.name)
        keys=[]
        for material in o.data.materials:
            if material not in definitions:
                key="CS_spawn_surface_worker-detail_"+str(len(definitions)).zfill(3)
                d=dict(constant_inputs(material),key=key,source=material.name,atlas=0,
                       transmission=0.0,alpha=1.0,transparent=False)
                image_node=material.node_tree.nodes.get("FACE_TEXTURE")
                if image_node:
                    bsdf=next(n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
                    if any(bsdf.inputs[k].links[0].from_node!=image_node for k in ("Base Color","Alpha")):
                        raise ValueError("Unsupported face decal graph: "+material.name)
                    image=image_node.image;source=Path(bpy.path.abspath(image.filepath))
                    destination=output/"Surfaces/worker-face"/source.name;destination.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source,destination)
                    d.update(transparent=True,alphaMapped=True,baseConstant=False,surfaceOpacity=1.0,
                        directAlbedo={"file":destination.relative_to(output).as_posix(),
                            "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
                            "colorSpace":"sRGB","size":max(image.size)})
                elif not all(d[k] for k in ("baseConstant","normalConstant","metallicConstant","roughnessConstant","emissionConstant")):
                    raise ValueError("Worker detail needs an explicit material conversion: "+material.name)
                definitions[material]=d;surfaces["definitions"].append(d)
            keys.append(definitions[material]["key"])
        record["materials"]=keys


def export_fbx(arm, output, path, animated):
    meshes=[o for o in arm.children_recursive if o.type=="MESH" and not o.get("cs_tool")]
    bpy.ops.object.select_all(action="DESELECT")
    for o in [arm,*meshes]:
        o.hide_set(False);o.hide_viewport=False;o.hide_render=False;o.select_set(True)
    bpy.context.view_layer.objects.active=arm;bpy.context.scene.render.fps=24
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={"ARMATURE","MESH"},
        add_leaf_bones=False,primary_bone_axis="Y",secondary_bone_axis="X",axis_forward="-Z",axis_up="Y",
        bake_anim=animated,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,
        apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",path_mode="COPY",embed_textures=True)


if __name__ == "__main__": main()
