"""Compile authored C# against real pinned Editor references, without fake stubs.

This supplementary check is NOT Unity's import pipeline or Unity Test Runner.
Real bundled test-runner references can check test APIs without running tests.
Template-cache references do not establish project package resolution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from check_source import check
from editor_identity import inspect_editor
from run_foundation import checkout_revision, utc

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
                  for path in directory.glob(family + ".*.dll") if path.name != family + ".TestRunner.dll"}
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


def discover_assemblies(root: Path) -> dict[str, dict]:
    """Assign each actual C# file to its nearest asmdef, including nested Editor/test boundaries."""
    roots = (root / "unity/Assets", root / "dotnet/src")
    groups, owners = {}, {}
    for directory in roots:
        if not directory.is_dir():
            raise ValueError("A first-party source root is missing: " + str(directory))
        if list(directory.rglob("*.asmref")) or list(directory.rglob("*.rsp")):
            raise ValueError("Assembly references or response-file overrides require an explicit API-check implementation.")
        for path in sorted(directory.rglob("*.asmdef")):
            data = json.loads(path.read_text())
            name = data.get("name")
            if not isinstance(name, str) or not name.startswith("CriticalShift.") or name in groups or path.parent in owners:
                raise ValueError("Duplicate, ambiguous or non-first-party assembly definition: " + str(path))
            if (data.get("includePlatforms", []) not in ([], ["Editor"]) or data.get("excludePlatforms", []) or
                    data.get("defineConstraints", []) or data.get("versionDefines", []) or data.get("allowUnsafeCode", False)):
                raise ValueError("Unsupported conditional/platform/compiler boundary: " + name)
            references = data.get("references", [])
            if (not isinstance(references, list) or any(not isinstance(value, str) for value in references) or
                    len(references) != len(set(references))):
                raise ValueError("Invalid assembly references: " + name)
            optional = data.get("optionalUnityReferences", [])
            if optional not in ([], ["TestAssemblies"]):
                raise ValueError("Unsupported optional Unity reference configuration: " + name)
            test = optional == ["TestAssemblies"]
            editor = data.get("includePlatforms") == ["Editor"]
            implicit = ["UnityEngine.TestRunner", "UnityEditor.TestRunner"] if test or editor else []
            duplicates = set(references).intersection(implicit)
            if duplicates:
                origin = "TestAssemblies" if test else "Editor platform"
                raise ValueError("Explicit " + ", ".join(sorted(duplicates)) + " duplicates the implicit " + origin + " reference: " + name)
            if data.get("precompiledReferences", []) != (["nunit.framework.dll"] if test else []):
                raise ValueError("Unexpected precompiled-reference boundary: " + name)
            groups[name] = {"path": path, "definition": data, "sources": [], "test": test,
                            "editor": editor, "pure": data.get("noEngineReferences") is True,
                            "implicit_references": implicit}
            owners[path.parent] = name
    for directory in roots:
        for source in sorted(directory.rglob("*.cs")):
            owner = next((owners[parent] for parent in (source.parent, *source.parents) if parent in owners), None)
            if owner is None:
                raise ValueError("Unowned first-party C# source: " + str(source))
            groups[owner]["sources"].append(source)
    if not groups or any(not group["sources"] for group in groups.values()):
        raise ValueError("Missing first-party assemblies or an empty authored source group.")
    return groups


def topological_order(groups: dict[str, dict]) -> list[str]:
    external = {"UnityEngine.TestRunner", "UnityEditor.TestRunner"}
    for name, group in groups.items():
        for reference in [*group["definition"].get("references", []), *group["implicit_references"]]:
            if reference not in groups and reference not in external:
                raise ValueError("Unknown declared dependency: " + name + " -> " + reference)
            if reference in groups and not group["test"] and groups[reference]["test"]:
                raise ValueError("A production assembly cannot reference a test assembly: " + name)
    pending, order = set(groups), []
    while pending:
        ready = [name for name in pending if not pending.intersection(groups[name]["definition"].get("references", []))]
        if not ready:
            raise ValueError("Cyclic first-party assembly dependencies: " + ", ".join(sorted(pending)))
        name = min(ready, key=lambda item: (groups[item]["test"], item))
        pending.remove(name)
        order.append(name)
    return order


def bundled_test_references(data: Path) -> tuple[dict[str, Path], dict[str, str]]:
    """Use only real pinned-Editor binaries; conflicting caches block the affected API checks."""
    selected, unavailable = {}, {}
    templates = data / "Resources/PackageManager/ProjectTemplates/libcache"
    for name in ("UnityEngine.TestRunner", "UnityEditor.TestRunner"):
        candidates = sorted({*(data / "Managed").rglob(name + ".dll"),
                             *templates.glob("*/ScriptAssemblies/" + name + ".dll")})
        if not candidates:
            unavailable[name] = "No real test-runner binary is present in the pinned Editor's Managed or bundled template cache."
        elif len({hashlib.sha256(path.read_bytes()).digest() for path in candidates}) != 1:
            unavailable[name] = "Pinned Editor test-runner candidates contain conflicting binary copies."
        else:
            selected[name] = candidates[0]
    return selected, unavailable


def assembly_fingerprint(groups: dict[str, dict]) -> str:
    digest = hashlib.sha256()
    paths = {path for group in groups.values() for path in (group["path"], *group["sources"])}
    for path in sorted(paths):
        digest.update(str(path).encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def compile_sources(editor: Path, nunit: Path, output: Path, dotnet: str = "dotnet"):
    output = output.resolve()
    if output.is_relative_to(ROOT.parent) and not output.is_relative_to(ROOT / "out") and not output.is_relative_to(ROOT / "dotnet/artifacts"):
        raise ValueError("Repository compiler output must remain under runtime/out or dotnet/artifacts.")
    output.mkdir(parents=True, exist_ok=True)
    data = editor / "Editor/Data"
    checks, groups, original = [], {}, None
    report = {"runner": "Supplementary SDK compiler against actual pinned Unity references and declared first-party asmdefs",
              "started_utc": utc(), "commit": checkout_revision(ROOT), "native_unity_execution": False,
              "checks": checks, "status": "NotRun", "production_status": "NotRun", "references": [],
              "limits": "API compilation only, with no Unity import, resolved package graph, test execution, serialization, physics, Player or gate acceptance. No Unity-generated symbols or platform variants are claimed.",
              "test_reference_policy": "TestAssemblies or an Editor-only platform implicitly adds UnityEngine.TestRunner and UnityEditor.TestRunner in this Editor compilation, as observed in the pinned native Bee responses. Explicit duplicate references are rejected. Real pinned Editor bundled template/Managed binaries only; does not verify project package resolution."}
    try:
        if not (data / "NetStandard/ref/2.1.0/netstandard.dll").is_file():
            raise ValueError("The pinned editor's .NET Standard 2.1 references were not found.")
        profile = json.loads((ROOT / "toolchain.json").read_text())
        report["profile"] = profile
        executable = editor / ("Editor/Unity.exe" if sys.platform == "win32" else "Editor/Unity")
        if not executable.is_file():
            raise ValueError("The pinned Editor executable is missing.")
        report["editor_file_identity"] = inspect_editor(executable, profile)
        if report["editor_file_identity"]["status"] != "Verified":
            report["status"] = "Blocked"
            raise ValueError("A verified Editor file identity is required before supplementary compilation; native-log-only identity is insufficient here.")
        report["source_check"] = check(ROOT)
        groups = discover_assemblies(ROOT)
        order = topological_order(groups)
        report["assembly_order"] = order
        report["source_sha256"] = original = assembly_fingerprint(groups)
        for name in order:
            group = groups[name]
            checks.append({"assembly": name, "source_files": len(group["sources"]), "kind": "test" if group["test"] else "production",
                           "status": "NotRun", "asmdef": group["path"].relative_to(ROOT).as_posix(),
                           "declared_references": group["definition"].get("references", []),
                           "implicit_references": group["implicit_references"],
                           "implicit_reference_provenance": [{"assembly": reference, "source": "optionalUnityReferences:TestAssemblies" if group["test"] else "includePlatforms:Editor"}
                                                             for reference in group["implicit_references"]]})
        sdk = profile["supplementaryDotnetSdk"]
        if sdk != "8.0.423":
            raise ValueError("This supplementary checker requires the selected SDK 8.0.423.")
        sdks = subprocess.check_output([str(dotnet), "--list-sdks"], text=True, timeout=30).splitlines()
        rows = [match for line in sdks if (match := re.fullmatch(re.escape(sdk) + r" \[(.+)\]", line))]
        if len(rows) != 1:
            raise ValueError("The supplementary check requires one exact .NET SDK 8.0.423 installation.")
        compiler = Path(rows[0][1]) / sdk / "Roslyn/bincore/csc.dll"
        if not compiler.is_file():
            raise ValueError("The selected real SDK compiler is missing.")
        report["compiler"] = {"host": str(dotnet), "sdk": sdk, "path": str(compiler), "sha256": hashlib.sha256(compiler.read_bytes()).hexdigest()}
        base = system_references(data)
        engine = modular_references(data / "Managed", "UnityEngine")
        editor_refs = modular_references(data / "Managed", "UnityEditor")
        runners, missing_runners = bundled_test_references(data)
        report["unavailable_test_references"] = missing_runners
        report["bundled_package_descriptors"] = []
        for package in ("com.unity.test-framework", "com.unity.ext.nunit"):
            descriptor = data / "Resources/PackageManager/BuiltInPackages" / package / "package.json"
            if descriptor.is_file():
                metadata = json.loads(descriptor.read_text(encoding="utf-8-sig"))
                report["bundled_package_descriptors"].append({"name": metadata["name"], "version": metadata["version"],
                                                            "path": str(descriptor), "sha256": hashlib.sha256(descriptor.read_bytes()).hexdigest()})
        inventory = [{"path": path.relative_to(data).as_posix(), "bytes": path.stat().st_size}
                     for path in sorted((data / "Managed").rglob("Unity*.dll"))]
        (output / "managed-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
        real_references = list(dict.fromkeys(base + engine + editor_refs + list(runners.values()) + ([nunit] if nunit.is_file() else [])))
        report["references"] = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in real_references]
        built = {}
        for record in checks:
            name = record["assembly"]
            group = groups[name]
            references = list(base)
            if not group["pure"]:
                references += engine
                if group["editor"]:
                    references += editor_refs
            missing = []
            for reference in [*record["declared_references"], *record["implicit_references"]]:
                if reference in built:
                    references.append(built[reference])
                elif reference in runners:
                    references.append(runners[reference])
                    for provenance in record["implicit_reference_provenance"]:
                        if provenance["assembly"] == reference:
                            provenance.update(binary=str(runners[reference]), sha256=hashlib.sha256(runners[reference].read_bytes()).hexdigest())
                else:
                    missing.append(missing_runners.get(reference, "Prerequisite assembly did not compile: " + reference))
            if group["test"]:
                if nunit.is_file():
                    references.append(nunit)
                else:
                    missing.append("The supplied real Unity NUnit reference is missing.")
            if missing:
                record.update(status="Blocked", reason="; ".join(missing))
                continue
            destination = output / (name + ".dll")
            destination.unlink(missing_ok=True)
            arguments = ["-nologo", "-nostdlib+", "-target:library", "-langversion:9.0", "-warnaserror+", "-out:" + str(destination)]
            arguments += ["-r:" + str(path) for path in dict.fromkeys(references)]
            arguments += [str(path) for path in group["sources"]]
            if any('"' in argument or "\n" in argument or "\r" in argument for argument in arguments):
                raise ValueError("Compiler response-file arguments contain unsupported quotes or newlines.")
            response = output / (name + ".rsp")
            response.write_text("\n".join('"' + argument + '"' for argument in arguments) + "\n", encoding="utf-8")
            record.update(started_utc=utc(), compiler_response=response.name, references=[str(path) for path in dict.fromkeys(references)])
            log = output / (name + ".log")
            try:
                result = subprocess.run([str(dotnet), str(compiler), "-noconfig", "@" + str(response)], text=True, capture_output=True, timeout=120)
            except (OSError, subprocess.SubprocessError) as exception:
                log.write_text(str(exception).replace(str(Path.home()), "<HOME>"))
                record.update(status="Failed", ended_utc=utc(), log=log.name, reason="Compiler launch or completion failed.")
                raise
            log.write_text((result.stdout + result.stderr).replace(str(Path.home()), "<HOME>"))
            passed = result.returncode == 0 and destination.is_file()
            record.update(exit_code=result.returncode, ended_utc=utc(), log=log.name, status="Passed" if passed else "Failed")
            print(name, result.returncode, result.stdout, result.stderr, flush=True)
            if not passed:
                raise RuntimeError("API compile failed: " + name)
            record["output_sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
            built[name] = destination
        report["status"] = "Blocked" if any(record["status"] != "Passed" for record in checks) else "Passed"
    except Exception as exception:
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        report.update(reason=str(exception).replace(str(Path.home()), "<HOME>"), error_type=type(exception).__name__)
        raise
    finally:
        production = [record for record in checks if record["kind"] == "production"]
        if production:
            report["production_status"] = "Passed" if all(record["status"] == "Passed" for record in production) else "Failed" if any(record["status"] == "Failed" for record in production) else "Blocked"
        if original is not None:
            try:
                report["source_unchanged"] = assembly_fingerprint(discover_assemblies(ROOT)) == original
            except Exception as exception:
                report["source_unchanged"] = None
                report["source_audit_error"] = str(exception).replace(str(Path.home()), "<HOME>")
            if report["source_unchanged"] is not True:
                report["status"] = "Failed"
                report.setdefault("reason", "First-party source changed or could not be audited during supplementary compilation.")
        report["ended_utc"] = utc()
        (output / "api-compile.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-root", required=True, type=Path)
    parser.add_argument("--nunit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dotnet", default="dotnet", help="Existing pinned SDK host; no SDK is installed by this checker.")
    args = parser.parse_args()
    result = compile_sources(args.editor_root.resolve(), args.nunit.resolve(), args.out.resolve(), args.dotnet)
    sys.exit(0 if result["status"] == "Passed" else 2 if result["status"] == "Blocked" else 1)
