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
    before = {r["key"]:{k:r[k] for k in ("translation","yaw","collisionSha256","meshSha256")} for r in manifest["rooms"]}
    audit = ROOT / "runtime/out/mine-bake-audit"; audit.mkdir(parents=True,exist_ok=True)
    (audit / "before-bindings.json").write_text(json.dumps(manifest,indent=2)+"\n")
    environment = dict(os.environ, CS_MINE_BAKE="1", CS_REUSE_COLLISION="1", CS_SURFACE_SIZE=str(args.size))
    subprocess.run([args.blender,"-b",str(scratch/"combined-runtime-source.blend"),"--disable-autoexec",
        "--python-exit-code","1","--python",str(ROOT/"runtime/tools/export_spawn_map.py"),"--",
        str(scratch/"map-config.json"),str(output),"mine"],check=True,env=environment)
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
        "assemblyCommit":config["map_commit"],"sourceRecords":config["sources"],"roomPlacementsAndCollisionsUnchanged":True,
        "otherRoomMeshesUnchanged":True,"sourceFilesUnchanged":True},indent=2)+"\n")
    print("CS_MINE_DELIVERY_OK",flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map-ref",default="d9eb1c5642273722f2ecee7179e958f05d39fa61")
    parser.add_argument("--blender",default="blender")
    parser.add_argument("--size",type=int,choices=(2048,4096,8192),default=4096)
    prepare(parser.parse_args())
