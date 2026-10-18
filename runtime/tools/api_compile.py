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

ROOT = Path(__file__).resolve().parents[1]

from check_source import check
from editor_identity import inspect_editor
from run_foundation import checkout_revision, utc

RUNNER_REFERENCES = ("UnityEngine.TestRunner", "UnityEditor.TestRunner")
UI_REFERENCES = ("UnityEngine.UI", "UnityEditor.UI")
RENDERER_REFERENCES = ("Unity.RenderPipelines.Universal.Runtime", "Unity.RenderPipelines.Core.Runtime")
SDK_PACKAGES = {
    "UnityEngine.UI": "com.unity.ugui",
    "UnityEditor.UI": "com.unity.ugui",
    "Unity.RenderPipelines.Universal.Runtime": "com.unity.render-pipelines.universal",
    "Unity.RenderPipelines.Core.Runtime": "com.unity.render-pipelines.core",
}


def package_pins(project: Path) -> dict:
    """Read selected versions/sources, without substituting vendor dependency requests."""
    manifest = project / "Packages/manifest.json"
    lock = project / "Packages/packages-lock.json"
    manifest_bytes, lock_bytes = manifest.read_bytes(), lock.read_bytes()
    declared = json.loads(manifest_bytes.decode("utf-8-sig"))["dependencies"]
    selected = json.loads(lock_bytes.decode("utf-8-sig"))["dependencies"]
    if (not isinstance(declared, dict) or any(not isinstance(name, str) or not isinstance(version, str)
                                            for name, version in declared.items()) or not isinstance(selected, dict)):
        raise ValueError("Invalid selected project package declarations.")
    pins = {}
    for name, row in selected.items():
        if (not isinstance(name, str) or not isinstance(row, dict) or
                any(not isinstance(row.get(key), str) or not row[key] for key in ("version", "source")) or
                ("url" in row and not isinstance(row["url"], str))):
            raise ValueError("Invalid selected package identity: " + str(name))
        pins[name] = {key: row[key] for key in ("version", "source", "url") if key in row}
    if not set(declared).issubset(pins):
        raise ValueError("A declared package is missing from the selected lock.")
    return {"manifest": declared, "selected": pins,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "lock_sha256": hashlib.sha256(lock_bytes).hexdigest()}


def ordinary_context_file(path: Path) -> None:
    if not path.is_file():
        raise ValueError("Missing ordinary native-context file: " + str(path))
    for item in (path, *path.parents):
        if item.is_symlink() or getattr(item, "is_junction", lambda: False)():
            raise ValueError("Native-context files cannot use symlinks or junctions: " + str(item))


def native_sdk_references(project: Path | None, canonical: Path, profile: dict,
                          required: set[str]) -> tuple[dict[str, Path], dict[str, str], dict]:
    """Select four named SDK binaries from one existing, pinned native context.

    No build, resolution, extraction, source copy, or download occurs here.
    Hashing an existing native DLL does not establish its freshness or a Player pass.
    """
    if not required.issubset(SDK_PACKAGES):
        raise ValueError("Unsupported native-context SDK reference.")
    evidence = {"project": str(project) if project is not None else None, "status": "NotRun",
                "native_unity_execution": False, "required_references": sorted(required),
                "packages": [], "binaries": [], "inputs": [],
                "limits": "Existing same-context Editor SDK DLLs supplement API compilation only. ProjectVersion and current package pins/descriptors are checked; binary hashes identify the existing files but do not establish a fresh native import, compiler invocation, SDK ABI identity, test execution or Player acceptance."}
    if project is None:
        if (canonical / "Packages").exists():
            evidence["canonical_pins"] = package_pins(canonical)
            for relative, key in (("Packages/manifest.json", "manifest_sha256"), ("Packages/packages-lock.json", "lock_sha256")):
                evidence["inputs"].append({"path": str(canonical / relative), "sha256": evidence["canonical_pins"][key]})
        reason = "A --unity-project context is required for selected UGUI or explicit renderer SDK references."
        if required:
            evidence.update(status="Blocked", reason=reason)
        return {}, dict.fromkeys(required, reason), evidence
    project = project.absolute()

    selected = {}
    try:
        for relative in ("ProjectSettings/ProjectVersion.txt", "Packages/manifest.json", "Packages/packages-lock.json"):
            ordinary_context_file(project / relative)
        version_path = project / "ProjectSettings/ProjectVersion.txt"
        version_bytes = version_path.read_bytes()
        version = "\n".join(version_bytes.decode("utf-8-sig").splitlines())
        if (re.findall(r"^m_EditorVersion: (.+)$", version, re.M) != [profile["editor"]] or
                re.findall(r"^m_EditorVersionWithRevision: (.+)$", version, re.M) !=
                [profile["editor"] + " (" + profile["revision"] + ")"]):
            raise ValueError("Native SDK context Editor identity differs from the exact canonical profile.")
        evidence["project_version_sha256"] = hashlib.sha256(version_bytes).hexdigest()
        evidence["inputs"].append({"path": str(version_path), "sha256": evidence["project_version_sha256"]})
        evidence["canonical_pins"] = expected = package_pins(canonical)
        evidence["context_pins"] = actual = package_pins(project)
        for context, pins in ((canonical, expected), (project, actual)):
            for relative, key in (("Packages/manifest.json", "manifest_sha256"), ("Packages/packages-lock.json", "lock_sha256")):
                evidence["inputs"].append({"path": str(context / relative), "sha256": pins[key]})
        if expected["manifest"] != actual["manifest"]:
            raise ValueError("Native SDK context manifest differs from canonical package pins.")
        if expected["selected"] != actual["selected"]:
            raise ValueError("Native SDK context selected package versions/sources differ from canonical pins.")
        evidence["pins_match"] = True
    except (OSError, ValueError, KeyError, TypeError) as exception:
        reason = str(exception)
        evidence.update(status="Blocked", pins_match=False, reason=reason)
        return {}, dict.fromkeys(required, reason), evidence

    missing, packages = {}, {}
    for assembly in sorted(required):
        package = SDK_PACKAGES[assembly]
        pin = actual["selected"].get(package)
        if pin is None:
            missing[assembly] = "SDK package is absent from the selected lock: " + package
            continue
        try:
            if package not in packages:
                candidates = sorted((project / "Library/PackageCache").glob(package + "@*/package.json"))
                unversioned = project / "Library/PackageCache" / package / "package.json"
                if unversioned.is_file():
                    candidates.append(unversioned)
                if len(candidates) != 1:
                    raise ValueError("Expected one native-context cached SDK descriptor: " + package)
                descriptor = candidates[0]
                ordinary_context_file(descriptor)
                descriptor_bytes = descriptor.read_bytes()
                record = {"name": package, **pin, "path": str(descriptor),
                          "sha256": hashlib.sha256(descriptor_bytes).hexdigest(), "matches_selected": False}
                if not any(item["path"] == str(descriptor) for item in evidence["packages"]):
                    evidence["packages"].append(record)
                    evidence["inputs"].append({"path": str(descriptor), "sha256": record["sha256"]})
                metadata = json.loads(descriptor_bytes.decode("utf-8-sig"))
                if not isinstance(metadata, dict) or metadata.get("name") != package or metadata.get("version") != pin["version"]:
                    raise ValueError("Native SDK descriptor differs from selected lock: " + package)
                record["matches_selected"] = True
                packages[package] = record
            binary = project / "Library/ScriptAssemblies" / (assembly + ".dll")
            ordinary_context_file(binary)
            selected[assembly] = binary
            evidence["binaries"].append({"assembly": assembly, "package": package, "path": str(binary),
                                         "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()})
            evidence["inputs"].append({"path": str(binary), "sha256": evidence["binaries"][-1]["sha256"]})
        except (OSError, ValueError, KeyError, TypeError) as exception:
            missing[assembly] = str(exception)
    evidence["unavailable_references"] = missing
    evidence["status"] = "Blocked" if missing else "Verified"
    return selected, missing, evidence


def modular_references(managed: Path, family: str) -> list[Path]:
    """Find one API family across Unity's shared module directory and root.

    Editor modules can live in Managed/UnityEngine, not Managed/UnityEditor.
    Combined legacy assemblies are excluded rather than mixed with modules.
    """
    if family not in ("UnityEngine", "UnityEditor"):
        raise ValueError("Unknown Unity reference family.")
    directories = (managed, managed / "UnityEngine", managed / "UnityEditor")
    candidates = {path for directory in directories
                  for path in directory.glob(family + ".*.dll")
                  if path.stem not in (*RUNNER_REFERENCES, *SDK_PACKAGES)}
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
    packages = package_pins(root / "unity")["selected"] if (root / "unity/Packages").exists() else {}
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
            pure = data.get("noEngineReferences") is True
            implicit = list(RUNNER_REFERENCES) if test or editor else []
            provenance = [{"assembly": reference, "source": "optionalUnityReferences:TestAssemblies" if test else "includePlatforms:Editor"}
                          for reference in implicit]
            if not pure and "com.unity.ugui" in packages:
                implicit.extend(UI_REFERENCES)
                provenance.extend({"assembly": reference, **packages["com.unity.ugui"],
                                   "package_source": packages["com.unity.ugui"]["source"], "source": "selected-lock:com.unity.ugui"}
                                  for reference in UI_REFERENCES)
            duplicates = set(references).intersection(implicit)
            if duplicates:
                origin = "selected UGUI package" if duplicates.intersection(UI_REFERENCES) else "TestAssemblies" if test else "Editor platform"
                raise ValueError("Explicit " + ", ".join(sorted(duplicates)) + " duplicates the implicit " + origin + " reference: " + name)
            if data.get("precompiledReferences", []) != (["nunit.framework.dll"] if test else []):
                raise ValueError("Unexpected precompiled-reference boundary: " + name)
            groups[name] = {"path": path, "definition": data, "sources": [], "test": test,
                            "editor": editor, "pure": pure, "implicit_references": implicit,
                            "implicit_reference_provenance": provenance}
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
    external = {*RUNNER_REFERENCES, *SDK_PACKAGES}
    for name, group in groups.items():
        for reference in [*group["definition"].get("references", []), *group["implicit_references"]]:
            if group["pure"] and reference in external:
                raise ValueError("A pure assembly cannot reference an engine or SDK assembly: " + name + " -> " + reference)
            if reference in RENDERER_REFERENCES and (name != "CriticalShift.Sandbox.Editor" or not group["editor"] or group["test"]):
                raise ValueError("Renderer SDK references are allowed only in production CriticalShift.Sandbox.Editor: " + name)
            if reference in UI_REFERENCES and reference in group["definition"].get("references", []):
                raise ValueError("UI SDK references must come from the selected UGUI implicit graph: " + name)
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
    for name in RUNNER_REFERENCES:
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


def compile_sources(editor: Path, nunit: Path, output: Path, dotnet: str = "dotnet", unity_project: Path | None = None):
    output = output.resolve()
    if output.is_relative_to(ROOT.parent) and not output.is_relative_to(ROOT / "out") and not output.is_relative_to(ROOT / "dotnet/artifacts"):
        raise ValueError("Repository compiler output must remain under runtime/out or dotnet/artifacts.")
    if unity_project is not None and output.is_relative_to(unity_project.absolute()):
        raise ValueError("Compiler output must remain outside the input native Unity SDK context.")
    output.mkdir(parents=True, exist_ok=True)
    data = editor / "Editor/Data"
    checks, groups, original = [], {}, None
    report = {"runner": "Supplementary SDK compiler against actual pinned Unity references and declared first-party asmdefs",
              "started_utc": utc(), "commit": checkout_revision(ROOT), "native_unity_execution": False,
              "checks": checks, "status": "NotRun", "production_status": "NotRun", "references": [],
              "limits": "API compilation only, with no new Unity import, package resolution, test execution, serialization, physics, Player or gate acceptance. Existing native-context package pins may be inspected; no fresh native graph, Unity-generated symbols or platform variants are claimed.",
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
                           "implicit_reference_provenance": [dict(item) for item in group["implicit_reference_provenance"]]})
        sdk_required = {reference for group in groups.values()
                        for reference in [*group["definition"].get("references", []), *group["implicit_references"]]
                        if reference in SDK_PACKAGES}
        sdk_references, missing_sdk, report["native_sdk_context"] = native_sdk_references(unity_project, ROOT / "unity", profile, sdk_required)
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
        external_references = {**runners, **sdk_references}
        real_references = list(dict.fromkeys(base + engine + editor_refs + list(external_references.values()) + ([nunit] if nunit.is_file() else [])))
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
                elif reference in external_references:
                    binary = external_references[reference]
                    references.append(binary)
                    for provenance in record["implicit_reference_provenance"]:
                        if provenance["assembly"] == reference:
                            provenance.update(binary=str(binary), sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
                else:
                    missing.append(missing_runners.get(reference, missing_sdk.get(reference, "Prerequisite assembly did not compile: " + reference)))
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
        invalid_context = report["native_sdk_context"].get("pins_match") is False
        report["status"] = "Blocked" if invalid_context or any(record["status"] != "Passed" for record in checks) else "Passed"
        if invalid_context:
            report.setdefault("reason", report["native_sdk_context"]["reason"])
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
        context = report.get("native_sdk_context", {})
        if context.get("inputs"):
            try:
                for item in context["inputs"]:
                    ordinary_context_file(Path(item["path"]))
                context["inputs_unchanged"] = all(hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
                                                  for item in context["inputs"])
            except (OSError, ValueError) as exception:
                context["inputs_unchanged"] = None
                context["audit_error"] = str(exception).replace(str(Path.home()), "<HOME>")
            if context["inputs_unchanged"] is not True:
                report["status"] = "Failed"
                report.setdefault("reason", "Canonical package pins or native SDK context inputs changed or could not be audited during supplementary compilation.")
        report["ended_utc"] = utc()
        (output / "api-compile.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-root", required=True, type=Path)
    parser.add_argument("--nunit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dotnet", default="dotnet", help="Existing pinned SDK host; no SDK is installed by this checker.")
    parser.add_argument("--unity-project", type=Path, help="Existing same-pinned native project supplying compiled UGUI/URP SDK DLLs; its manifest and selected lock must match canonical pins. Never built or modified by this checker.")
    args = parser.parse_args()
    result = compile_sources(args.editor_root.resolve(), args.nunit.resolve(), args.out.resolve(), args.dotnet,
                             args.unity_project.absolute() if args.unity_project is not None else None)
    sys.exit(0 if result["status"] == "Passed" else 2 if result["status"] == "Blocked" else 1)
