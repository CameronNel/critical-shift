"""Export the isolated assembly build; restore spawn's authored leaves only in this derivative."""
import hashlib
import json
import math
import os
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_spawn_materials import bake_surfaces
from mine_join_rays import collision_eligible


def matrix(o):
    return matrix(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis if o.parent else o.matrix_basis.copy()


def pose(o):
    location, rotation, _ = (o.matrix_parent_inverse @ o.matrix_basis).decompose()
    return {"position": list(location), "rotation": [rotation.x, rotation.y, rotation.z, rotation.w]}


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects: o.hide_set(False); o.hide_viewport = False; o.hide_render = False; o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH", "EMPTY"},
        bake_anim=False, axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS", path_mode="COPY", embed_textures=True, use_custom_props=True,
        use_triangles=True)


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    config_path, output_path = args[:2]
    only = args[2] if len(args) > 2 else None
    config, output = json.loads(Path(config_path).read_text()), Path(output_path)
    if only and only not in {r[0] for r in config["rooms"]}: raise ValueError("Unknown partial-export room: " + only)
    previous = json.loads((output / "map-bindings.json").read_text()) if only else None
    if previous and previous["mapCommit"] != config["map_commit"]: raise ValueError("Partial export requires the same pinned map revision.")
    source_scene = bpy.context.scene
    source_scene.frame_set(1)
    manifest = {"schema": 1, "mapCommit": config["map_commit"], "sourceFrame": "plan metres: +X east, +Y north, +Z up",
                "unityFrame": "+X east, +Z north, +Y up; Blender yaw is negated", "rooms": [], "anchors": [],
                "doors": [], "materials": [], "nativeUnity": "NotRun: validate this export in the pinned editor"}
    original = bpy.data.collections.get("MODULE_spawn-room")
    if original is None:
        source_path = Path(config_path).parent / "map/sections/facility-assembly/sources/spawn-room/module.blend"
        with bpy.data.libraries.load(str(source_path), link=True) as (src, dst):
            if "MODULE_spawn-room" not in src.collections: raise ValueError("Spawn source contract collection is missing.")
            dst.collections = ["MODULE_spawn-room"]
        original = dst.collections[0]
    if original.name not in source_scene.collection.children: source_scene.collection.children.link(original)
    dg = bpy.context.evaluated_depsgraph_get()
    source_objects = {o.name: o for o in original.all_objects}
    source_path=Path(config_path).parent / "map/sections/facility-assembly/sources/spawn-room/module.blend"
    if Path(bpy.data.filepath).resolve()==source_path.resolve(): authored_spawn=source_scene
    else:
        with bpy.data.libraries.load(str(source_path),link=True) as (src,dst): dst.scenes=[src.scenes[0]]
        authored_spawn=dst.scenes[0]
    view=authored_spawn.view_settings
    source_view={"transform":view.view_transform,"look":view.look,"exposure":view.exposure,"gamma":view.gamma}
    if only == "mine":
        view = source_scene.view_settings
        source_view = {"transform":view.view_transform,"look":view.look,"exposure":view.exposure,"gamma":view.gamma}
    def authored_lights(objects,parent=Matrix.Identity(4)):
        result=[]
        for o in objects:
            if o.hide_render: continue
            world=parent @ matrix(o)
            if o.type=="LIGHT":
                result.append({"name":o.name,"position":list(world.translation),"rotation":list(world.to_quaternion()),
                    "color":list(o.data.color),"power":float(o.data.energy),"type":o.data.type,
                    "size":float(getattr(o.data,"size",0)),"sizeY":float(getattr(o.data,"size_y",0)),
                    "radius":float(getattr(o.data,"shadow_soft_size",0.05))})
            elif o.instance_type=="COLLECTION" and o.instance_collection:
                result.extend(authored_lights(o.instance_collection.all_objects,world @ Matrix.Translation(-o.instance_collection.instance_offset)))
        return result
    manifest["validationViews"]={"views":[]}
    for name in ("VALIDATE_Spawn","VALIDATE_BriefingDoor","VALIDATE_LockerDoor"):
        o=source_objects[name]; rotation=matrix(o).to_quaternion()
        manifest["validationViews"]["views"].append({"name":name,"position":list(matrix(o).translation),
            "forward":list(rotation @ Vector((0,0,-1))),"up":list(rotation @ Vector((0,1,0))),
            "verticalFov":math.degrees(2*math.atan(math.tan(o.data.angle_x/2)*810/1440))})
    required = [*[f"SPAWN_{i}" for i in range(1, 5)], *[f"PPE_{i:02}_suit" for i in range(1, 5)],
                "AIRLOCK_leaf_L", "AIRLOCK_leaf_R", "BRIEFING_bench_01", "BRIEFING_bench_02", "INTEGRITY_POD",
                "INTERACT_integrity", "POD_door_L", "POD_door_R", "POD_physical_button", "POD_physical_button.001"]
    for name in required:
        if name not in source_objects: raise ValueError("Missing exact spawn object: " + name)
    for name in required:
        o = source_objects[name]
        manifest["anchors"].append({"name": name, "node": "CS_spawn-room_" + name,
            "position": list(matrix(o).translation), "properties": {k: str(o[k]) for k in o.keys()}})
    # Preserve authored open/closed poses. The locker file is posed open; closed is its hinge's zero rotation.
    for name in ["AIRLOCK_leaf_L", "AIRLOCK_leaf_R", *[f"BELONG_{i:02}_door_{side}" for i in range(1, 5) for side in ("L", "R")]]:
        o = source_objects[name]; current = pose(o); closed = dict(current); opened = dict(current)
        if name.startswith("AIRLOCK"):
            opened = {"position": [current["position"][0] + float(o["open_translation_x"]), *current["position"][1:]], "rotation": current["rotation"]}
        else: closed = {"position": current["position"], "rotation": [0, 0, 0, 1]}
        manifest["doors"].append({"name": name, "node": "CS_spawn-room_" + name, "closed": closed, "opened": opened})
    for name in ("POD_door_L", "POD_door_R"):
        o = source_objects[name]; source_scene.frame_set(1); opened = pose(o)
        source_scene.frame_set(31); closed = pose(o)
        manifest["doors"].append({"name": name, "node": "CS_spawn-room_" + name, "closed": closed, "opened": opened})
    source_scene.frame_set(1)
    # A runtime-only scene contains local copies; no linked source datablock is edited or saved.
    target_scene = bpy.data.scenes.new("CS_RUNTIME_EXPORT")
    bpy.context.window.scene = target_scene
    dynamic = {"AIRLOCK_leaf_L", "AIRLOCK_leaf_R", "POD_door_L", "POD_door_R",
               *[f"BELONG_{i:02}_door_{s}" for i in range(1, 5) for s in ("L", "R")],
               *[f"PPE_{i:02}_suit" for i in range(1, 5)]}
    dynamic.update({"BELONG_01_thermos", "BELONG_03_thermos"})
    for key, _lib, _collection, placement, yaw, _note in config["rooms"]:
        if only and key != only: continue
        instance = source_scene.objects.get("ROOM_" + key)
        if instance is None and only=="spawn-room":
            # The PR95 wrapper only omits these named objects. Read the exact module directly for
            # a scoped conversion, instead of loading four million unrelated mine triangles.
            exterior_file,exterior_collection=config["exterior_skins"][key]
            exterior_path=Path(config_path).parent / "map/sections/facility-assembly/exteriors" / exterior_file
            with bpy.data.libraries.load(str(exterior_path),link=True) as (src,dst): dst.collections=[exterior_collection]
            exterior=dst.collections[0];source_scene.collection.children.link(exterior)
            bpy.context.window.scene=source_scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
            bpy.context.window.scene=target_scene
            members=[*exterior.all_objects,*[o for o in original.all_objects if o.name not in config["spawn_omitted"]]]
        elif instance is None: raise ValueError("Assembly is missing ROOM_" + key)
        else: members = list(instance.instance_collection.all_objects)
        if key == "spawn-room":
            # The assembly deliberately removed these leaves/gauges for viewing. Runtime adds their original geometry.
            members.extend(source_objects[name] for name in config["spawn_omitted"] if not name.startswith("SERVICE_end"))
        root = bpy.data.objects.new("CS_ROOM_" + key, None); target_scene.collection.objects.link(root)
        copies, mappings, collider_vertices, collider_faces, lights, collision_omissions = [], [], [], [], [], []

        def clone_group(objects, parent, prefix, inherited_dynamic=False):
            unique = list(dict.fromkeys(objects)); made = {}
            def clone(o):
                if o in made: return made[o]
                owned_parent = clone(o.parent) if o.parent in unique else parent
                local = o.matrix_parent_inverse @ o.matrix_basis if o.parent in unique else matrix(o)
                mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg) if o.type in {"MESH", "FONT", "CURVE"} else None
                n = bpy.data.objects.new(prefix + o.name, mesh); target_scene.collection.objects.link(n)
                n.parent = owned_parent; n.matrix_basis = local; made[o] = n; copies.append(n)
                ancestry = []; p = o
                while p: ancestry.append(p.name); p = p.parent
                movable = inherited_dynamic or (key == "spawn-room" and any(a in dynamic for a in ancestry))
                visible = not o.hide_render
                mappings.append({"source": o.name, "node": n.name, "visible": visible, "dynamic": movable})
                if o.type == "LIGHT":
                    lights.append({"name":o.name,"position":list(matrix(o).translation),"rotation":list(matrix(o).to_quaternion()),
                        "color":list(o.data.color),"power":float(o.data.energy),"type":o.data.type,
                        "size":float(getattr(o.data,"size",0)),"sizeY":float(getattr(o.data,"size_y",0)),
                        "radius":float(getattr(o.data,"shadow_soft_size",0.05))})
                    if o.data.type=="SUN": lights[-1]["angle"]=math.degrees(o.data.angle)
                if o.instance_type == "COLLECTION" and o.instance_collection:
                    n.matrix_basis = local @ Matrix.Translation(-o.instance_collection.instance_offset)
                    clone_group(list(o.instance_collection.all_objects), n, prefix + o.name + "__", movable)
                return n
            for o in unique: clone(o)
        clone_group(members, root, "CS_" + key + "_")
        if key=="spawn-room": lights=authored_lights(authored_spawn.objects)
        if previous:
            old=next(room for room in previous["rooms"] if room["key"]==key)
            fields=("source","node","visible","dynamic")
            # A prior mine delivery intentionally hides the source volume containers.
            # The pinned source hashes still guard author visibility; that explicit
            # delivery override must not make a second surface refresh reject itself.
            volume_overrides={u["node"] for p in previous.get("materials",[]) if p["room"]=="mine"
                for u in p.get("unsupported",[])} if key=="mine" else set()
            inventory=lambda items: sorted(tuple(True if field=="visible" and item["node"] in volume_overrides else item[field]
                for field in fields) for item in items)
            if inventory(old["objects"])!=inventory(mappings): raise ValueError("Scoped export changed assembled object bindings: "+key)
        bpy.context.view_layer.update()
        # Build collision after all parent transforms have evaluated (matrix_world otherwise starts as identity).
        reuse_collision = only == "mine" and os.environ.get("CS_REUSE_COLLISION") == "1"
        collider_vertices.clear(); collider_faces.clear()
        by_name = {o.name: o for o in copies}
        for mapping in mappings:
            o = by_name[mapping["node"]]
            if o.type != "MESH" or not collision_eligible(mapping): continue
            if mapping["source"].lower().startswith(("stain_", "decal_", "scuff_")):
                collision_omissions.append({"source": mapping["source"], "node": mapping["node"], "reason": "decorative surface graphic"})
                continue
            if reuse_collision: continue
            offset = len(collider_vertices); mesh = o.data
            transform = root.matrix_world.inverted() @ o.matrix_world
            collider_vertices.extend(tuple(transform @ v.co) for v in mesh.vertices)
            mesh.calc_loop_triangles(); collider_faces.extend(tuple(offset + v for v in tri.vertices) for tri in mesh.loop_triangles)
        mesh_file = "Room-" + key + ".fbx"
        if key == "mine" and os.environ.get("CS_MINE_BAKE") == "1":
            # The fully assembled scene is needed to capture the owner's patches, not to
            # bake them. Release every unrelated source room before creating atlas copies.
            frames = {n.object for o in copies if o.type == "MESH" for m in o.data.materials if m and m.use_nodes
                      for n in m.node_tree.nodes if n.type == "TEX_COORD" and n.object}
            ancestors=set()
            for frame in frames:
                parent=frame.parent
                while parent:
                    ancestors.add(parent); parent=parent.parent
            keep = {*copies, root, *frames, *ancestors}
            bpy.data.batch_remove([o for o in bpy.data.objects if o not in keep])
            bpy.data.batch_remove([s for s in bpy.data.scenes if s != target_scene])
            bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
            import ctypes
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        if key == "spawn-room" and os.environ.get("CS_SKIP_SURFACES")!="1":
            manifest["materials"].append(bake_surfaces(target_scene,copies,mappings,output,source_view))
        if key == "mine" and os.environ.get("CS_MINE_BAKE")=="1":
            from export_mine_materials import bake_mine
            manifest["materials"].append(bake_mine(target_scene,copies,mappings,output,source_view))
        export(output / mesh_file, [root, *copies])
        if reuse_collision:
            old = next(r for r in previous["rooms"] if r["key"] == key)
            if hashlib.sha256((output / old["collision"]).read_bytes()).hexdigest() != old["collisionSha256"]:
                raise ValueError("Previously verified mine collision was modified.")
            updated_room = dict(old, objects=mappings, lights=lights,
                meshSha256=hashlib.sha256((output / mesh_file).read_bytes()).hexdigest())
            manifest["rooms"].append(updated_room)
            print("RUNTIME ROOM", key, len(copies), "objects; verified collision reused", flush=True)
            for o in [*copies, root]: bpy.data.objects.remove(o, do_unlink=True)
            continue
        collision = bpy.data.meshes.new("CS_COLLISION_" + key); collision.from_pydata(collider_vertices, [], collider_faces); collision.update()
        collider = bpy.data.objects.new("CS_COLLISION_" + key, collision); target_scene.collection.objects.link(collider)
        collision_file = "Collision-" + key + ".fbx"
        export(output / collision_file, [collider])
        bounds = [[min(v[a] for v in collider_vertices), max(v[a] for v in collider_vertices)] for a in range(3)]
        manifest["rooms"].append({"key": key, "mesh": mesh_file, "collision": collision_file, "translation": placement,
            "yaw": yaw, "objects": mappings, "lights": lights, "collisionOmissions": collision_omissions,
            "collisionBounds": bounds, "collisionTriangles": len(collider_faces),
            "meshSha256": hashlib.sha256((output / mesh_file).read_bytes()).hexdigest(),
            "collisionSha256": hashlib.sha256((output / collision_file).read_bytes()).hexdigest()})
        print("RUNTIME ROOM", key, len(copies), "objects", len(collider_faces), "collision triangles", flush=True)
        for o in [*copies, root, collider]: bpy.data.objects.remove(o, do_unlink=True)
    manifest["sources"] = config["sources"]
    if previous:
        updated = {r["key"]: r for r in manifest["rooms"]}
        manifest["rooms"] = [updated.get(r["key"], r) for r in previous["rooms"]]
        manifest["materials"] += [m for m in previous.get("materials",[]) if m["room"] not in updated]
    converted = [p["room"] for p in manifest["materials"]]
    manifest["limits"] = "Pinned assembly; unlit material delivery for " + ", ".join(converted) + ". Remaining rooms have preview materials. Native lighting and visual review are required. Static collision is unprofiled. Source rooms are not modified."
    (output / "map-bindings.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Check one compact collision import per room, including unit scale and exact geometry bounds.
    checked=[room for room in manifest["rooms"] if not only or room["key"]==only]
    if only == "mine" and os.environ.get("CS_REUSE_COLLISION") == "1":
        (output / "mine-roundtrip.json").write_text(json.dumps({"status":"Passed", "geometryPreserved":True,
            "collision":"Unmodified previously round-tripped FBX, SHA-256 verified", "mapCommit":manifest["mapCommit"],
            "nativeUnity":False},indent=2)+"\n")
        return
    for room in checked:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(output / room["collision"]))
        vertices = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH" for v in o.data.vertices]
        actual = [[min(v[a] for v in vertices), max(v[a] for v in vertices)] for a in range(3)]
        error = max(abs(actual[a][b] - room["collisionBounds"][a][b]) for a in range(3) for b in range(2))
        if error > 0.002: raise ValueError("Collision round trip changed metre scale: " + room["key"] + " " + str(error))
    (output / "map-roundtrip.json").write_text(json.dumps({"status": "Passed", "rooms": len(manifest["rooms"]),
        "checkedRooms":[room["key"] for room in checked],"unchangedRoomsReused":len(manifest["rooms"])-len(checked),
        "scaleToleranceMetres": 0.002, "nativeUnity": False}, indent=2) + "\n")


if __name__ == "__main__": main()
