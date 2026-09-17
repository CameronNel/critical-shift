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
    """Find one API family across Unity's shared module directory and root.

    Editor modules can live in Managed/UnityEngine, not Managed/UnityEditor.
    Combined legacy assemblies are excluded rather than mixed with modules.
    """
    if family not in ("UnityEngine", "UnityEditor"):
        raise ValueError("Unknown Unity reference family.")
    directories = (managed, managed / "UnityEngine", managed / "UnityEditor")
    candidates = {path for directory in directories
                  for path in directory.glob(family + ".*.dll")}
    selected = {}
    for path in sorted(candidates):
        if path.name in selected and selected[path.name].read_bytes() != path.read_bytes():
            raise ValueError("Conflicting reference copies: " + path.name)
        selected[path.name] = path
    if family + ".CoreModule.dll" not in selected:
        raise ValueError("The pinned Editor's modular " + family + " API is missing; see managed-inventory.json.")
    return [selected[name] for name in sorted(selected)]


def system_references(data: Path) -> list[Path]:
    """Use the Editor's Standard API plus its real Framework compatibility facades.

    The Unity-supplied NUnit binary targets Framework mscorlib. A Standard
    reference alone is insufficient, and a full Framework core would conflict.
    """
    standard = data / "NetStandard/ref/2.1.0"
    compatibility = data / "NetStandard/compat/2.1.0/shims"
    if not (standard / "netstandard.dll").is_file():
        raise ValueError("The pinned editor's .NET Standard 2.1 reference is missing.")
    if not (compatibility / "netfx/mscorlib.dll").is_file():
        raise ValueError("The pinned editor's Framework-to-Standard mscorlib facade is missing.")
    directories = (standard, compatibility / "netstandard", compatibility / "netfx")
    selected = {}
    for directory in directories:
        for path in sorted(directory.glob("*.dll")):
            if path.name in selected and selected[path.name].read_bytes() != path.read_bytes():
                raise ValueError("Conflicting system reference copies: " + path.name)
            selected[path.name] = path
    return [selected[name] for name in sorted(selected)]


def compile_sources(editor: Path, nunit: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    data = editor / "Editor/Data"
    source = ROOT / "unity/Assets/CriticalShift"
    checks = []
    report = {"runner": "Supplementary .NET SDK compiler against official Unity 6000.4.3f1 reference assemblies",
              "native_unity_execution": False, "checks": checks, "status": "NotRun",
              "reference_policy": "Modular APIs grouped by assembly name, including Editor modules in the shared UnityEngine directory; legacy combined DLLs excluded; real Framework-to-Standard facades included",
              "references": []}
    inventory = [{"path": str(p.relative_to(data)), "bytes": p.stat().st_size}
                 for p in sorted((data / "Managed").rglob("Unity*.dll"))]
    (output / "managed-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")

    def build(name, sources, references, compiler):
        destination = output / (name + ".dll")
        destination.unlink(missing_ok=True)
        arguments = ["-nologo", "-noconfig", "-nostdlib+", "-target:library", "-langversion:9.0",
                     "-warnaserror+", "-out:" + str(destination)]
        arguments += ["-r:" + str(p) for p in dict.fromkeys(references)]
        arguments += [str(p) for p in sources]
        result = subprocess.run(["dotnet", str(compiler), *arguments], text=True,
                                capture_output=True, timeout=120)
        (output / (name + ".log")).write_text(result.stdout + result.stderr)
        passed = result.returncode == 0 and destination.is_file()
        checks.append({"assembly": name, "source_files": len(sources), "exit_code": result.returncode,
                       "status": "Passed" if passed else "Failed"})
        print(name, result.returncode, result.stdout, result.stderr, flush=True)
        if not passed:
            raise RuntimeError("API compile failed: " + name)
        return destination

    try:
        net = data / "NetStandard/ref/2.1.0"
        if not (net / "netstandard.dll").is_file():
            raise ValueError("The pinned editor's .NET Standard 2.1 references were not found.")
        if not nunit.is_file():
            raise ValueError("The real Unity-supplied NUnit assembly is required.")
        sdks = subprocess.check_output(["dotnet", "--list-sdks"], text=True).splitlines()
        rows = [line for line in sdks if line.startswith("8.0.423 ")]
        if len(rows) != 1:
            raise ValueError("The supplementary check requires .NET SDK 8.0.423.")
        sdkroot = Path(rows[0].split("[", 1)[1].rstrip("]"))
        compiler = sdkroot / "8.0.423/Roslyn/bincore/csc.dll"
        base = system_references(data)
        engine = modular_references(data / "Managed", "UnityEngine")
        editor_refs = modular_references(data / "Managed", "UnityEditor")
        report["references"] = [{"path": str(p.relative_to(data)),
                                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                for p in dict.fromkeys(base + engine + editor_refs)]
        application = build("CriticalShift.Application", list((source / "Application").glob("*.cs")), base, compiler)
        bootstrap = build("CriticalShift.Bootstrap", list((source / "Bootstrap").glob("*.cs")),
                          base + engine + [application], compiler)
        build_editor = build("CriticalShift.Bootstrap.Editor", list((source / "Bootstrap/Editor").glob("*.cs")),
                             base + engine + editor_refs + [application, bootstrap], compiler)
        build("CriticalShift.Tests.EditMode", list((source / "Tests/EditMode").glob("*.cs")),
              base + engine + editor_refs + [application, bootstrap, build_editor, nunit], compiler)
        report["status"] = "Passed"
    except Exception as exc:
        report["status"] = "Failed"
        report["reason"] = str(exc)
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
