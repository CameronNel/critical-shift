"""Compile authored C# against real pinned Editor references, without fake stubs.

This supplementary check is NOT Unity's import pipeline or Unity Test Runner.
PlayMode tests need package assemblies produced by native Unity import.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def modular_references(managed: Path, family: str) -> list[Path]:
    """Select modular APIs, never the duplicate combined IntelliSense assembly."""
    if family not in ("UnityEngine", "UnityEditor"):
        raise ValueError("Unknown Unity reference family.")
    candidates = [*(managed / family).glob("*.dll"), *managed.glob(family + ".*Module.dll")]
    selected = {}
    for path in sorted(candidates):
        if path.name == family + ".dll":
            continue
        if path.name in selected and selected[path.name].read_bytes() != path.read_bytes():
            raise ValueError("Conflicting reference copies: " + path.name)
        selected[path.name] = path
    if family + ".CoreModule.dll" not in selected:
        raise ValueError("The pinned Editor's modular " + family + " API is missing.")
    return [selected[name] for name in sorted(selected)]


def compile_sources(editor: Path, nunit: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    data = editor / "Editor/Data"
    net = data / "NetStandard/ref/2.1.0"
    if not (net / "netstandard.dll").is_file():
        raise ValueError("The pinned editor's .NET Standard 2.1 references were not found.")
    sdks = subprocess.check_output(["dotnet", "--list-sdks"], text=True).splitlines()
    rows = [line for line in sdks if line.startswith("8.0.423 ")]
    if len(rows) != 1:
        raise ValueError("The supplementary check requires .NET SDK 8.0.423.")
    sdkroot = Path(rows[0].split("[", 1)[1].rstrip("]"))
    compiler = sdkroot / "8.0.423/Roslyn/bincore/csc.dll"
    base = sorted(net.glob("*.dll"))
    engine = modular_references(data / "Managed", "UnityEngine")
    editor_refs = modular_references(data / "Managed", "UnityEditor")
    source = ROOT / "unity/Assets/CriticalShift"
    checks = []

    def build(name, sources, references):
        destination = output / (name + ".dll")
        arguments = ["-nologo", "-noconfig", "-nostdlib+", "-target:library", "-langversion:9.0",
                     "-warnaserror+", "-out:" + str(destination)]
        arguments += ["-r:" + str(p) for p in dict.fromkeys(references)]
        arguments += [str(p) for p in sources]
        result = subprocess.run(["dotnet", str(compiler), *arguments], text=True, capture_output=True)
        (output / (name + ".log")).write_text(result.stdout + result.stderr)
        checks.append({"assembly": name, "source_files": len(sources), "exit_code": result.returncode,
                       "status": "Passed" if result.returncode == 0 and destination.exists() else "Failed"})
        print(name, result.returncode, result.stdout, result.stderr, flush=True)
        if result.returncode:
            raise RuntimeError("API compile failed: " + name)
        return destination

    report = {"runner": "Supplementary .NET SDK compiler against official Unity 6000.4.3f1 reference assemblies",
              "native_unity_execution": False, "checks": checks, "status": "NotRun",
              "reference_policy": "Modular engine/editor APIs only; combined UnityEngine.dll and UnityEditor.dll excluded",
              "references": [{"path": str(p.relative_to(data)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                             for p in dict.fromkeys(base + engine + editor_refs)]}
    try:
        application = build("CriticalShift.Application", list((source / "Application").glob("*.cs")), base)
        bootstrap = build("CriticalShift.Bootstrap", list((source / "Bootstrap").glob("*.cs")), base + engine + [application])
        build_editor = build("CriticalShift.Bootstrap.Editor", list((source / "Bootstrap/Editor").glob("*.cs")),
                             base + engine + editor_refs + [application, bootstrap])
        build("CriticalShift.Tests.EditMode", list((source / "Tests/EditMode").glob("*.cs")),
              base + engine + editor_refs + [application, bootstrap, build_editor, nunit])
        report["status"] = "Passed"
    except Exception:
        report["status"] = "Failed"
        raise
    finally:
        (output / "api-compile.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-root", required=True, type=Path)
    parser.add_argument("--nunit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    compile_sources(args.editor_root.resolve(), args.nunit.resolve(), args.out.resolve())
