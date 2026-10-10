"""Supplementary compile against real pinned Editor APIs; never a native Unity pass."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from api_compile import modular_references, system_references
from prepare_player import ROOT, PROJECT, IMPORT, NAMES, source_fingerprint


def check(editor, output):
    profile = json.loads((ROOT / "toolchain.json").read_text())
    data = editor / "Editor/Data"
    # Query the installed binary; do not accept arbitrary engine APIs.
    native_version = subprocess.run([str(editor / "Editor/Unity"), "-version"], capture_output=True, text=True, timeout=30)
    if profile["editor"] not in native_version.stdout + native_version.stderr:
        raise ValueError("Expected the repository's exact Unity version.")
    output.mkdir(parents=True, exist_ok=True)
    sdk = subprocess.check_output(["dotnet", "--version"], cwd=PROJECT, text=True).strip()
    if not sdk.startswith("8."): raise ValueError("Use the canonical .NET 8 SDK selection.")
    rows = subprocess.check_output(["dotnet", "--list-sdks"], cwd=PROJECT, text=True).splitlines()
    row = next(line for line in rows if line.startswith(sdk + " "))
    compiler = Path(row.split("[", 1)[1].rstrip("]")) / sdk / "Roslyn/bincore/csc.dll"
    base = system_references(data); engine = modular_references(data / "Managed", "UnityEngine")
    editor_refs = modular_references(data / "Managed", "UnityEditor")
    dlls = [IMPORT / (name + ".dll") for name in NAMES]
    imports = json.loads((IMPORT / "imports.json").read_text())
    imported = {row["assembly"]: row["sha256"] for row in imports if "assembly" in row}
    if set(imported) != set(NAMES) or imports[-1].get("canonical_source_sha256") != source_fingerprint():
        raise ValueError("Canonical sources changed; rerun prepare_player.py before compiling the Unity binding.")
    for dll in dlls:
        if hashlib.sha256(dll.read_bytes()).hexdigest() != imported[dll.stem]:
            raise ValueError("A generated import changed: " + dll.name)
    nunit = data / "Resources/PackageManager/BuiltInPackages/com.unity.ext.nunit/net40/unity-custom/nunit.framework.dll"
    source = ROOT / "unity/Assets/CriticalShift"
    report = {"status": "NotRun", "native_unity_execution": False, "editor": profile["editor"], "sdk": sdk, "checks": [],
              "limits": "API compile only. No native import, Test Runner, physical execution, build or human review."}
    def compile(name, paths, references):
        destination = output / (name + ".dll"); destination.unlink(missing_ok=True)
        args = ["-nologo", "-noconfig", "-nostdlib+", "-target:library", "-langversion:9.0", "-warnaserror+", "-out:" + str(destination)]
        result = subprocess.run(["dotnet", str(compiler), *args, *["-r:" + str(p) for p in dict.fromkeys(references)],
                                 *map(str, paths)], cwd=PROJECT, text=True, capture_output=True, timeout=120)
        (output / (name + ".log")).write_text(result.stdout + result.stderr)
        report["checks"].append({"assembly": name, "files": len(paths), "status": "Passed" if result.returncode == 0 else "Failed"})
        print(name, result.stdout, result.stderr, flush=True)
        if result.returncode: raise RuntimeError("API compilation failed: " + name)
        return destination
    try:
        feature = compile("CriticalShift.Features.Player.Unity", sorted((source / "Features/Player").glob("*.cs")), base + engine + dlls)
        host = compile("CriticalShift.Player.Bootstrap", sorted((source / "Bootstrap/Player").glob("*.cs")), base + engine + dlls + [feature])
        compile("CriticalShift.Player.Editor", sorted((source / "Bootstrap/Player/Editor").glob("*.cs")), base + engine + editor_refs + dlls + [feature, host])
        compile("CriticalShift.Player.Tests.PlayMode", sorted((source / "Tests/Player").glob("*.cs")), base + engine + dlls + [feature, host, nunit])
        report["source_sha256"] = hashlib.sha256(b"".join(p.read_bytes() for directory in
            [source / "Features/Player", source / "Bootstrap/Player", source / "Tests/Player"] for p in sorted(directory.rglob("*.cs")))).hexdigest()
        report["references"] = [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in dict.fromkeys(base + engine + editor_refs + dlls + [nunit])]
        report["status"] = "Passed"
    except Exception as error:
        report.update(status="Failed", reason=str(error)); raise
    finally:
        (output / "player-api.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-root", required=True, type=Path); parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(); check(args.editor_root.resolve(), args.out.resolve())
