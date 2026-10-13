"""Refresh the mine's surfaces in an already prepared combined-map Unity delivery."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from prepare_spawn import ROOT, assignments, sha
from prepare_player import meta

RECIPE_FILES = (
    "prepare_mine.py", "export_spawn_map.py", "export_spawn_materials.py",
    "export_mine_materials.py", "export_mine_context.py", "export_mine_volumes.py",
    "export_source_wood.py", "normal_bake_pixels.py", "mine_delivery_uv.py", "mine_lightmap_uv.py", "mine_join_rays.py",
)


def export_recipe(root, blender_version, batched, runtime_scene_sha256=None):
    return {"blender": blender_version, "batched": batched, "runtimeSceneSha256":runtime_scene_sha256, "tools": {
        name: hashlib.sha256((root / "runtime/tools" / name).read_bytes()).hexdigest()
        for name in RECIPE_FILES}}


def validate_cache(cached, config, size, recipe):
    if cached.get("method") != "source-recipe-v2" or cached.get("size") != size or cached.get("sources") != config["sources"]:
        raise ValueError("Cached mine atlas belongs to a different source or bake recipe.")
    if cached.get("exportRecipe") != recipe:
        raise ValueError("Cached mine exporter/UV recipe changed. Generate a fresh cache with prepare_mine.py.")


def texture_metadata(output, package):
    """Specify new mine PNG runtime formats before first import; retain source bytes/GUIDs."""
    for atlas in package["atlases"]:
        for channel in ("albedo", "normal", "metallicSmoothness"):
            record = atlas[channel]
            path = output / record["file"]
            metadata = Path(str(path)+".meta")
            if not metadata.exists(): meta(path)
            previous = metadata.read_text()
            if "TextureImporter:" in previous: continue  # Native importer owns existing settings.
            guid = re.search(r"^guid: ([0-9a-f]{32})$", previous, re.M).group(1)
            metadata.write_text(f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  serializedVersion: 13
  internalIDToNameTable: []
  externalObjects: {{}}
  mipmaps:
    enableMipMap: 1
    sRGBTexture: {1 if channel == 'albedo' else 0}
  isReadable: 0
  textureType: {1 if channel == 'normal' else 0}
  textureShape: 1
  nPOTScale: 0
  alphaUsage: 1
  alphaIsTransparency: 0
  textureSettings:
    filterMode: 2
    aniso: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: {record['size']}
    textureFormat: -1
    textureCompression: 2
    compressionQuality: 100
    overridden: 0
  - serializedVersion: 4
    buildTarget: Standalone
    maxTextureSize: {record['size']}
    textureFormat: {26 if channel == 'normal' else 25}
    textureCompression: 2
    compressionQuality: 100
    overridden: 1
  userData:
  assetBundleName:
  assetBundleVariant:
""")


def prepare(args):
    output = ROOT / "runtime/unity/Assets/CriticalShift/Generated/Spawn"
    scratch = ROOT / "runtime/out/spawn-export-source"
    config = json.loads((scratch / "map-config.json").read_text())
    manifest = json.loads((output / "map-bindings.json").read_text())
    if config["map_commit"] != manifest["mapCommit"]: raise ValueError("Prepared assembly revision differs from its source.")
    builder_path = "sections/facility-assembly/combined/build_combined_map.py"
    current = sha(args.map_ref)
    builder = subprocess.check_output(["git", "show", current+":"+builder_path], cwd=ROOT)
    pinned = next(r for r in config["sources"] if r["path"] == builder_path)
    if hashlib.sha256(builder).hexdigest() != pinned["sha256"]:
        raise ValueError("Assembly builder changed. Refresh the assembled delivery before applying a scoped mine bake.")
    for source in config["sources"]:
        if source["path"]==builder_path: continue
        pointer = subprocess.check_output(["git", "show", current+":"+source["path"]], cwd=ROOT)
        expected = (dict(line.split(" ",1) for line in pointer.decode().splitlines())["oid"].removeprefix("sha256:")
                    if pointer.startswith(b"version https://git-lfs.github.com/spec/v1\n") else hashlib.sha256(pointer).hexdigest())
        if expected != source["sha256"]:
            raise ValueError("Source changed. Refresh the assembly before baking: "+source["path"])
    for record in config["sources"]:
        path = scratch / "map" / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]: raise ValueError("Source hash mismatch: "+record["path"])
    blender_version = subprocess.check_output([args.blender, "--version"], text=True).splitlines()[0]
    runtime_scene = scratch / "combined-runtime-source.blend"
    recipe = export_recipe(ROOT, blender_version, bool(getattr(args,"batched",False)),
        hashlib.sha256(runtime_scene.read_bytes()).hexdigest())
    reuse=getattr(args,"reuse_atlases",None)
    if reuse:
        cached=json.loads(Path(reuse).read_text())
        validate_cache(cached, config, args.size, recipe)
    before = {r["key"]:{k:r[k] for k in ("translation","yaw","collisionSha256","meshSha256")} for r in manifest["rooms"]}
    audit = ROOT / "runtime/out/mine-bake-audit"; audit.mkdir(parents=True,exist_ok=True)
    (audit / "before-bindings.json").write_text(json.dumps(manifest,indent=2)+"\n")
    environment = dict(os.environ, CS_MINE_BAKE="1", CS_REUSE_COLLISION="1", CS_SURFACE_SIZE=str(args.size))
    environment.pop("CS_MINE_JOIN_BAKE", None)
    environment.pop("CS_REUSE_MINE_ATLASES", None)
    if getattr(args,"batched",False): environment["CS_MINE_JOIN_BAKE"]="1"
    if reuse: environment["CS_REUSE_MINE_ATLASES"]=str(Path(reuse).resolve())
    if not getattr(args,"context_only",False):
        subprocess.run([args.blender,"-b",str(scratch/"combined-runtime-source.blend"),"--disable-autoexec",
            "--python-exit-code","1","--python",str(ROOT/"runtime/tools/export_spawn_map.py"),"--",
            str(scratch/"map-config.json"),str(output),"mine"],check=True,env=environment)
    else:
        package=next(p for p in manifest["materials"] if p["room"]=="mine")
        if package.get("contextMesh"):
            raise ValueError("Context is already attached; run a full preparation before rebuilding it.")
        room=next(r for r in manifest["rooms"] if r["key"]=="mine")
        if hashlib.sha256((output/room["mesh"]).read_bytes()).hexdigest()!=room["meshSha256"]:
            raise ValueError("Completed core mesh changed before context resume.")
        for atlas in package["atlases"]:
            for record in atlas.values():
                if hashlib.sha256((output/record["file"]).read_bytes()).hexdigest()!=record["sha256"]:
                    raise ValueError("Completed core atlas changed before context resume.")
    if not getattr(args,"skip_context",False):
        subprocess.run([args.blender,"-b",str(scratch/"combined-runtime-source.blend"),"--disable-autoexec",
            "--python-exit-code","1","--python",str(ROOT/"runtime/tools/export_mine_context.py"),"--",str(output)],check=True,env=environment)
    if export_recipe(ROOT, blender_version, recipe["batched"],hashlib.sha256(runtime_scene.read_bytes()).hexdigest()) != recipe:
        raise ValueError("Exporter changed during preparation. Regenerate the delivery before using its cache.")
    after = json.loads((output / "map-bindings.json").read_text())
    for room in after["rooms"]:
        for field,value in before[room["key"]].items():
            if room["key"] == "mine" and field == "meshSha256": continue
            if room[field] != value: raise ValueError("Scoped bake changed other geometry, collision or placement.")
    mine = next(p for p in after["materials"] if p["room"] == "mine")
    mine["assemblyLighting"] = assignments(builder.decode())["SCENE_LIGHT"]
    (output / "map-bindings.json").write_text(json.dumps(after,indent=2)+"\n")
    for path in [output,*sorted(output.rglob("*"))]:
        if not path.name.endswith(".meta") and not Path(str(path)+".meta").exists(): meta(path)
    texture_metadata(output,mine)
    for record in config["sources"]:
        if hashlib.sha256((scratch/"map"/record["path"]).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Bake mutated source: "+record["path"])
    (audit / "preservation.json").write_text(json.dumps({"status":"Passed","inspectedMain":current,
        "assemblyCommit":config["map_commit"],"sourceRecords":config["sources"],"roomPlacementsUnchanged":True,
        "otherRoomCollisionsUnchanged":True,
        "mineCollisionUnchanged":next(r for r in after["rooms"] if r["key"]=="mine")["collisionSha256"]==before["mine"]["collisionSha256"],
        "otherRoomMeshesUnchanged":True,"sourceFilesUnchanged":True},indent=2)+"\n")
    if not getattr(args,"context_only",False):
        # A context resume has not established current-recipe core provenance.
        # Never certify its existing core as a newly produced v2 cache.
        from export_source_wood import RECIPE as wood_recipe
        cache = {"method":"source-recipe-v2", "size":args.size, "sources":config["sources"],
            "exportRecipe":recipe, "woodRecipe":wood_recipe,
            "atlases":{Path(atlas["albedo"]["file"]).parent.name:atlas for atlas in mine["atlases"]}}
        (audit / "surface-cache.json").write_text(json.dumps(cache,indent=2)+"\n")
    print("CS_MINE_DELIVERY_OK",flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map-ref",default="d9eb1c5642273722f2ecee7179e958f05d39fa61")
    parser.add_argument("--blender",default="blender")
    parser.add_argument("--batched",action="store_true",help="Batch compatible mine meshes with explicit coordinates and hidden originals.")
    parser.add_argument("--reuse-atlases",type=Path,help="Verified source-pinned cache record for completed object-preserving atlas passes.")
    parser.add_argument("--skip-context",action="store_true",help="Debug only: omit the source-authored depot mesh/material overlay.")
    parser.add_argument("--context-only",action="store_true",help="Resume a completed core bake whose context export failed.")
    parser.add_argument("--size",type=int,choices=(2048,4096,8192),default=4096)
    prepare(parser.parse_args())
