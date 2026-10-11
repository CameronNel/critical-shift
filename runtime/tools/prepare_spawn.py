"""Export the current combined map and existing rig into isolated Unity derivatives."""
import argparse
import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = "bb6b4924849d38097ee629a6fa2c00dc1b56095f"
RIG = "90a42290df627330e4c4e445b6bfa7fba0464e3a"


def sha(ref):
    resolved = subprocess.run(["git", "rev-parse", "--verify", ref + "^{commit}"], cwd=ROOT,
                              text=True, capture_output=True)
    if resolved.returncode:
        # The existing rig is still on PR 55. Fetch its exact object for fresh/shallow clones.
        if len(ref) != 40 or any(c not in "0123456789abcdef" for c in ref):
            raise ValueError("Missing local ref; fetch the requested branch first: " + ref)
        subprocess.run(["git", "fetch", "--no-tags", "origin", ref], cwd=ROOT, check=True)
        return subprocess.check_output(["git", "rev-parse", "--verify", ref + "^{commit}"], cwd=ROOT, text=True).strip()
    return resolved.stdout.strip()


def stage(ref, path, directory, records):
    destination = directory / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    blob = subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT)
    if blob.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        pointer = dict(line.split(" ", 1) for line in blob.decode().splitlines())
        expected = pointer["oid"].removeprefix("sha256:")
        if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == expected:
            blob = destination.read_bytes()
        else:
            blob = subprocess.check_output(["git", "lfs", "smudge"], input=blob, cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("LFS source was not hydrated: " + path)
    digest = hashlib.sha256(blob).hexdigest()
    destination.write_bytes(blob)
    records.append({"path": path, "source_commit": ref, "sha256": digest})
    return destination


def assignments(source):
    values = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                def evaluate(n):
                    if isinstance(n, ast.Name): return values[n.id]
                    if isinstance(n, (ast.List, ast.Tuple)): return [evaluate(x) for x in n.elts]
                    return ast.literal_eval(n)
                values[node.targets[0].id] = evaluate(node.value)
            except (ValueError, KeyError, TypeError): pass
    return values


def prepare(args):
    map_sha, rig_sha = sha(args.map_ref), sha(args.rig_ref)
    scratch = ROOT / "runtime/out/spawn-export-source"
    output = ROOT / "runtime/unity/Assets/CriticalShift/Generated/Spawn"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    if not args.rig_only:
        builder_path = "sections/facility-assembly/combined/build_combined_map.py"
        builder = stage(map_sha, builder_path, scratch / "map", records)
        values = assignments(builder.read_text())
        rooms = values["ROOMS"]
        spawn = next(row for row in rooms if row[0] == "spawn-room")
        if list(spawn[3]) != [8.0, -92.38, 0.0] or spawn[4] != 0:
            raise ValueError("Spawn placement changed; review its runtime interface before exporting.")
        source_base = Path("sections/facility-assembly/sources")
        for row in rooms:
            path = str(Path(os.path.normpath(source_base / row[1])))
            stage(map_sha, path, scratch / "map", records)
        for lib, _collection in values.get("EXTERIOR_SKINS", {}).values():
            stage(map_sha, "sections/facility-assembly/exteriors/" + lib, scratch / "map", records)
        stage(map_sha, "sections/facility-assembly/sources/spawn-room/hero_suit.blend", scratch / "map", records)
        config = {"map_commit": map_sha, "rooms": rooms, "sources": records.copy(),
                  "spawn_omitted": values.get("OMIT", {}).get("spawn-room", []),"exterior_skins":values.get("EXTERIOR_SKINS",{})}
        (scratch / "map-config.json").write_text(json.dumps(config, indent=2))
        subprocess.run([args.blender, "-b", "--disable-autoexec", "--python-exit-code", "1", "--python", str(builder), "--",
                        "--through", rooms[-1][0], "--output", str(scratch / "combined-runtime-source.blend")], check=True)
        geometry_environment=os.environ.copy(); geometry_environment["CS_SKIP_SURFACES"]="1"
        subprocess.run([args.blender, "-b", str(scratch / "combined-runtime-source.blend"), "--disable-autoexec", "--python-exit-code", "1", "--python",
                        str(ROOT / "runtime/tools/export_spawn_map.py"), "--", str(scratch / "map-config.json"), str(output)], check=True,env=geometry_environment)
        # Material baking needs only the source room, not the entire seven-million-triangle assembly.
        subprocess.run([args.blender,"-b",str(scratch / "map/sections/facility-assembly/sources/spawn-room/module.blend"),
                        "--disable-autoexec","--python-exit-code","1","--python",str(ROOT / "runtime/tools/export_spawn_map.py"),
                        "--",str(scratch / "map-config.json"),str(output),"spawn-room"],check=True)
        subprocess.run([args.blender,"-b",str(scratch / "map/sections/facility-assembly/sources/spawn-room/module.blend"),
                        "--disable-autoexec","--python-exit-code","1","--python",str(ROOT / "runtime/tools/export_spawn_floor.py"),
                        "--",str(output),"--lettering"],check=True)
        subprocess.run([args.blender,"-b",str(scratch / "map/sections/facility-assembly/sources/spawn-room/module.blend"),
                        "--disable-autoexec","--python-exit-code","1","--python",str(ROOT / "runtime/tools/export_spawn_floor.py"),
                        "--",str(output),"--walls"],check=True)
    if not args.skip_rig:
        prefix = "sections/spawn-room/blender/"
        paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", rig_sha, prefix], cwd=ROOT, text=True).splitlines()
        for path in paths:
            if path.endswith(".py") or "/character_faces/" in path:
                stage(rig_sha, path, scratch / "rig", records)
        subprocess.run([args.blender, "-b", "--disable-autoexec", "--python-exit-code", "1", "--python", str(ROOT / "runtime/tools/export_spawn_rig.py"),
                        "--", str(scratch / "rig" / prefix), str(output), rig_sha], check=True)
    for row in records:
        path = (scratch / ("rig" if row["source_commit"] == rig_sha else "map")) / row["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("An export mutated its input: " + row["path"])
    (scratch / "source-integrity.json").write_text(json.dumps({"status": "Passed", "sources": records}, indent=2) + "\n")
    # Metadata uses the same deterministic mapping as canonical DLL/scene preparation.
    import sys
    sys.path.insert(0, str(ROOT / "runtime/tools"))
    from prepare_player import meta
    for path in [output.parent, output, *sorted(output.rglob("*"))]:
        if not path.name.endswith(".meta"): meta(path)
    print("Runtime derivatives:", output, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map-ref", default=MAP)
    parser.add_argument("--rig-ref", default=RIG)
    parser.add_argument("--blender", default="blender")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--rig-only", action="store_true")
    mode.add_argument("--skip-rig", action="store_true")
    prepare(parser.parse_args())
