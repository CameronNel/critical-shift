"""Export the isolated assembly build; restore spawn's authored leaves only in this derivative."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector


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
        apply_scale_options="FBX_SCALE_UNITS", path_mode="COPY", embed_textures=True, use_custom_props=True)


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
                "doors": [], "materials": [], "nativeUnity": "Blocked: activation required"}
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
        if instance is None: raise ValueError("Assembly is missing ROOM_" + key)
        members = list(instance.instance_collection.all_objects)
        if key == "spawn-room":
            # The assembly deliberately removed these leaves/gauges for viewing. Runtime adds their original geometry.
            members.extend(source_objects[name] for name in config["spawn_omitted"] if not name.startswith("SERVICE_end"))
        root = bpy.data.objects.new("CS_ROOM_" + key, None); target_scene.collection.objects.link(root)
        copies, mappings, collider_vertices, collider_faces, lights = [], [], [], [], []

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
                    lights.append({"position": list(matrix(o).translation), "color": list(o.data.color), "power": float(o.data.energy), "type": o.data.type})
                if o.instance_type == "COLLECTION" and o.instance_collection:
                    n.matrix_basis = local @ Matrix.Translation(-o.instance_collection.instance_offset)
                    clone_group(list(o.instance_collection.all_objects), n, prefix + o.name + "__", movable)
                return n
            for o in unique: clone(o)
        clone_group(members, root, "CS_" + key + "_")
        bpy.context.view_layer.update()
        # Build collision after all parent transforms have evaluated (matrix_world otherwise starts as identity).
        collider_vertices.clear(); collider_faces.clear()
        by_name = {o.name: o for o in copies}
        for mapping in mappings:
            o = by_name[mapping["node"]]
            if o.type != "MESH" or not mapping["visible"] or mapping["dynamic"] or any(t in mapping["source"].lower() for t in ("haze", "fog", "leaf", "paper", "rug", "carpet", "state_")): continue
            offset = len(collider_vertices); mesh = o.data
            transform = root.matrix_world.inverted() @ o.matrix_world
            collider_vertices.extend(tuple(transform @ v.co) for v in mesh.vertices)
            mesh.calc_loop_triangles(); collider_faces.extend(tuple(offset + v for v in tri.vertices) for tri in mesh.loop_triangles)
        mesh_file = "Room-" + key + ".fbx"
        export(output / mesh_file, [root, *copies])
        collision = bpy.data.meshes.new("CS_COLLISION_" + key); collision.from_pydata(collider_vertices, [], collider_faces); collision.update()
        collider = bpy.data.objects.new("CS_COLLISION_" + key, collision); target_scene.collection.objects.link(collider)
        collision_file = "Collision-" + key + ".fbx"
        export(output / collision_file, [collider])
        bounds = [[min(v[a] for v in collider_vertices), max(v[a] for v in collider_vertices)] for a in range(3)]
        manifest["rooms"].append({"key": key, "mesh": mesh_file, "collision": collision_file, "translation": placement,
            "yaw": yaw, "objects": mappings, "lights": lights, "collisionBounds": bounds, "collisionTriangles": len(collider_faces),
            "meshSha256": hashlib.sha256((output / mesh_file).read_bytes()).hexdigest(),
            "collisionSha256": hashlib.sha256((output / collision_file).read_bytes()).hexdigest()})
        print("RUNTIME ROOM", key, len(copies), "objects", len(collider_faces), "collision triangles", flush=True)
        for o in [*copies, root, collider]: bpy.data.objects.remove(o, do_unlink=True)
    manifest["sources"] = config["sources"]
    if previous:
        updated = {r["key"]: r for r in manifest["rooms"]}
        manifest["rooms"] = [updated.get(r["key"], r) for r in previous["rooms"]]
    manifest["limits"] = "Current six-room assembly only. Static collision is a prototype, not profiled. FBX preserves geometry and image textures; procedural shaders/light rigs are not equivalent in Unity. Source rooms are not modified."
    (output / "map-bindings.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Check one compact collision import per room, including unit scale and exact geometry bounds.
    for room in manifest["rooms"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(output / room["collision"]))
        vertices = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH" for v in o.data.vertices]
        actual = [[min(v[a] for v in vertices), max(v[a] for v in vertices)] for a in range(3)]
        error = max(abs(actual[a][b] - room["collisionBounds"][a][b]) for a in range(3) for b in range(2))
        if error > 0.002: raise ValueError("Collision round trip changed metre scale: " + room["key"] + " " + str(error))
    (output / "map-roundtrip.json").write_text(json.dumps({"status": "Passed", "rooms": len(manifest["rooms"]),
        "scaleToleranceMetres": 0.002, "nativeUnity": False}, indent=2) + "\n")


if __name__ == "__main__": main()
