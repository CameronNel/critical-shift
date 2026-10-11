"""Blender-only repair of derived lighting UVs; no material rebake or source edit."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_mine_materials import geometry_digest
from export_spawn_map import export
from mine_lightmap_uv import generate
from mine_join_rays import generate as join_rays


output = Path(sys.argv[sys.argv.index("--") + 1])
manifest = json.loads((output / "map-bindings.json").read_text())
room = next(r for r in manifest["rooms"] if r["key"] == "mine")
path = output / room["mesh"]
old_sha = hashlib.sha256(path.read_bytes()).hexdigest()
if old_sha != room["meshSha256"]: raise ValueError("Derived mine mesh is stale.")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(path))
bpy.context.view_layer.update()
objects = list(bpy.context.scene.objects)
package=next(p for p in manifest["materials"] if p["room"]=="mine")
package["joinRays"]=join_rays(objects,room["objects"])
(output/"mine-join-rays.json").write_text(json.dumps({"meshSha256":old_sha,"mapCommit":manifest["mapCommit"],
    "rays":package["joinRays"],"limits":"Blender-export geometry expectations; verify in native Unity."},indent=2)+"\n")
if "--join-only" in sys.argv:
    (output/"map-bindings.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("CS_MINE_JOIN_EXPECTATIONS_EXPORTED",flush=True)
    sys.exit(0)
before = geometry_digest(objects)
count = generate(objects)
if before != geometry_digest(objects): raise ValueError("Lighting unwrap changed geometry or placement.")
expected = next(p for p in manifest["materials"] if p["room"] == "mine")["meshes"]
if count != expected: raise ValueError("Lighting UV mesh coverage changed.")
temporary = output / "Room-mine-lighting-refresh.fbx"
export(temporary, objects)
temporary.replace(path)
room["meshSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
(output / "map-bindings.json").write_text(json.dumps(manifest, indent=2) + "\n")
(output / "mine-lightmap-uv.json").write_text(json.dumps({
    "status":"Passed", "meshes":count, "method":"Dedicated per-mesh Blender smart projection, margin 0.002",
    "inputMeshSha256":old_sha, "outputMeshSha256":room["meshSha256"],
    "geometryAndPlacementUnchanged":True, "surfaceUvChannelsUnchanged":True,
    "limits":"Derived FBX refresh only. Native import and lighting still require validation."
}, indent=2) + "\n")
print("CS_MINE_LIGHTMAP_UV_DELIVERY_OK", flush=True)
