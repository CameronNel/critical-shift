"""One explicit package-initialization process before a separate strict native prepare.

Initialization never grants validation or acceptance. Its original log is passed
unchanged to validate_log; a rejection is retained even after a later clean
prepare. No diagnostic lines are removed, no package source is patched here,
and no failed/nonzero process is retried.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from evidence import EvidenceError, validate_log


LICENSE_FAILURE = re.compile(r"No valid Unity.*license|No valid license|Failed to activate|License is not active|No Unity Editor license", re.I)
GUID_UPDATE_FILES = (
    "Editor/Generation/Contexts/TargetSetupContext.cs",
    "Editor/Generation/Targets/BuiltIn/Editor/ShaderGraph/Targets/BuiltInCanvasSubTarget.cs",
)
MANAGED_EXCEPTION_HEADER = re.compile(
    r"^\s*(?:--->\s*)?(?:[A-Za-z_]\w*[.+])*(?:[A-Za-z_]\w*)?Exception(?:\s*:(?:\s.*)?|\s*)$")


def managed_exception_headers(text: str) -> list[dict]:
    """Identify actual exception headers, not stack-frame arguments such as System.Exception&."""
    return [{"line": index + 1, "text": line} for index, line in enumerate(text.splitlines())
            if MANAGED_EXCEPTION_HEADER.fullmatch(line)]


def classify_shadergraph_guid_update(text: str, project: Path, packages: dict) -> dict:
    """Recognize only the pinned SDK's observed two-error API-updater episode.

    Original strict validation has already Failed. Validate every original log
    line independently to ensure no other strict diagnostic is hidden by this
    initialization-only compatibility classification. The separate prepare
    always validates its complete unmodified log with no compatibility policy.
    """
    evidence = {"status": "Rejected", "diagnostics": [], "updated_sources": []}
    pin = packages.get("packages", {}).get("com.unity.shadergraph", {})
    if pin.get("version") != "17.4.0" or pin.get("source") != "builtin":
        evidence["reason"] = "Known GUID compatibility initialization requires selected builtin ShaderGraph 17.4.0."
        return evidence
    descriptors = packages.get("cached_descriptors", {}).get("com.unity.shadergraph", [])
    if len(descriptors) != 1:
        evidence["reason"] = "The known ShaderGraph update requires its unique verified cached descriptor."
        return evidence
    package_root = Path(descriptors[0]["path"]).parent.as_posix()
    expected = {package_root + "/" + relative for relative in GUID_UPDATE_FILES}
    pattern = re.compile(r"^(Library[/\\]PackageCache[/\\]com\.unity\.shadergraph@[^/\\]+[/\\].+\.cs)"
                         r"\(\d+,\d+\): error CS0246: The type or namespace name 'GUID' could not be found"
                         r" \(are you missing a using directive or an assembly reference\?\)$")
    lines = text.splitlines()
    headers = managed_exception_headers(text)
    if headers:
        evidence.update(reason="A managed exception header is outside the two known ShaderGraph GUID errors.",
                        unexpected_diagnostic=headers[0], managed_exception_headers=headers)
        return evidence
    seen = []
    for index, line in enumerate(lines):
        try:
            validate_log(line)
        except EvidenceError:
            match = pattern.fullmatch(line)
            path = match[1].replace("\\", "/") if match else None
            if path not in expected:
                evidence.update(reason="An initialization diagnostic is outside the two known ShaderGraph GUID errors.",
                                unexpected_diagnostic={"line": index + 1, "text": line})
                return evidence
            seen.append((index, path))
            evidence["diagnostics"].append({"line": index + 1, "path": path, "text": line})
    if len(seen) != 2 or {path for _, path in seen} != expected:
        evidence["reason"] = "The initialization log must contain exactly both known ShaderGraph GUID errors."
        return evidence
    headers = [index for index, line in enumerate(lines) if line == "[API Updater] Updated Files:"]
    if len(headers) != 1 or headers[0] <= max(index for index, _ in seen):
        evidence["reason"] = "The native updater file list is missing or does not follow both known diagnostics."
        return evidence
    updated = []
    end = headers[0] + 1
    while end < len(lines) and re.fullmatch(r"Library[/\\]PackageCache[/\\].+\.cs", lines[end]):
        updated.append(lines[end].replace("\\", "/"))
        end += 1
    if not expected.issubset(updated) or any(not path.startswith(package_root + "/") for path in updated):
        evidence["reason"] = "The native updater must list both diagnostic files inside the verified ShaderGraph package."
        return evidence
    finished = next((index for index in range(end, len(lines)) if lines[index] == "Finished running ScriptUpdaters"), None)
    rebuilt = next((index for index in range(finished + 1, len(lines))
                    if lines[index].startswith("*** Tundra build success ")), None) if finished is not None else None
    if rebuilt is None:
        evidence["reason"] = "A subsequent successful native Tundra rebuild after the SDK updater is required."
        return evidence
    for relative in sorted(expected):
        path = project / relative
        if (not path.is_file() or path.is_symlink() or
                any(parent.is_symlink() or getattr(parent, "is_junction", lambda: False)() for parent in path.parents)):
            evidence["reason"] = "An updater-listed ShaderGraph source file is missing or linked: " + relative
            return evidence
        evidence["updated_sources"].append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    evidence.update(status="ExpectedShaderGraphGuidApiUpdate", updater_list_line=headers[0] + 1,
                    updater_finished_line=finished + 1, subsequent_rebuild_line=rebuilt + 1,
                    updater_listed_files=updated)
    return evidence


def package_snapshot(project: Path) -> dict:
    """Selected pins are independent of package descriptors' requested dependencies."""
    manifest_path, lock_path = project / "Packages/manifest.json", project / "Packages/packages-lock.json"
    manifest_bytes, lock_bytes = manifest_path.read_bytes(), lock_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))["dependencies"]
    dependencies = json.loads(lock_bytes.decode("utf-8-sig"))["dependencies"]
    if not isinstance(manifest, dict) or not isinstance(dependencies, dict):
        raise EvidenceError("Package manifest and lock dependencies must be mappings.")
    packages = {}
    for name, entry in dependencies.items():
        if (not isinstance(entry, dict) or not isinstance(entry.get("version"), str) or not entry["version"] or
                not isinstance(entry.get("source"), str) or not entry["source"]):
            raise EvidenceError("A package lock entry lacks a selected version or source: " + name)
        packages[name] = {key: entry[key] for key in ("version", "source", "url") if key in entry}
    for required in ("com.unity.test-framework", "com.unity.ext.nunit"):
        if required not in packages:
            raise EvidenceError("Required selected package is missing from the lock: " + required)
    return {"manifest_dependencies": manifest, "packages": packages,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "lock_sha256": hashlib.sha256(lock_bytes).hexdigest()}


def resolved_package_evidence(project: Path, expected: dict) -> dict:
    evidence = {"status": "NotRun", "limits": "Native workspace lock and cached descriptors only; no package, gameplay or gate acceptance."}
    try:
        actual = package_snapshot(project)
        evidence.update(actual)
        problems = []
        if actual["packages"] != expected["packages"]:
            problems.append("Native selected package versions or sources differ from the copied source pins.")
        if actual["manifest_dependencies"] != expected["manifest_dependencies"]:
            problems.append("Native manifest dependencies differ from the copied source manifest.")
        descriptors, absent = {}, []
        observed = {"com.unity.test-framework", "com.unity.ext.nunit"}
        observed.update(name for name in ("com.unity.render-pipelines.universal", "com.unity.render-pipelines.core",
                                         "com.unity.shadergraph", "com.unity.render-pipelines.universal-config", "com.unity.ugui")
                        if name in expected["packages"])
        for name in sorted(observed):
            candidates = sorted((project / "Library/PackageCache").glob(name + "@*/package.json"))
            unversioned = project / "Library/PackageCache" / name / "package.json"
            if unversioned.is_file():
                candidates.append(unversioned)
            rows = []
            for path in candidates:
                if path.is_symlink() or any(getattr(parent, "is_junction", lambda: False)() or parent.is_symlink()
                                            for parent in path.parents):
                    raise EvidenceError("Native package descriptors cannot use symlinks or junctions.")
                raw = path.read_bytes()
                descriptor = json.loads(raw.decode("utf-8-sig"))
                rows.append({"name": descriptor.get("name"), "version": descriptor.get("version"),
                             "path": path.relative_to(project).as_posix(), "sha256": hashlib.sha256(raw).hexdigest()})
            descriptors[name] = rows
            if not rows:
                absent.append(name)
            elif len(rows) != 1 or rows[0]["name"] != name or rows[0]["version"] != actual["packages"][name]["version"]:
                problems.append("Native cached descriptor does not uniquely match the selected lock entry: " + name)
        evidence["cached_descriptors"] = descriptors
        if problems:
            evidence.update(status="Failed", reason=" ".join(problems))
        elif absent:
            evidence["reason"] = "Native package resolution has no cached descriptor evidence for: " + ", ".join(absent)
        else:
            evidence["status"] = "Passed"
    except Exception as exception:
        evidence.update(status="Failed", reason=("Native package evidence is unavailable or malformed: " + str(exception)).replace(str(Path.home()), "<HOME>"))
    return evidence


def audit_package_pins(report: dict, project: Path, expected: dict, checkpoint: str, required: bool = True) -> bool:
    """Retain each native package audit independently of the first phase failure."""
    evidence = resolved_package_evidence(project, expected)
    initial = report.get("phases", {}).get("package-initialize", {}).get("resolved_packages", {}).get("cached_descriptors")
    if initial is not None and evidence["status"] == "Passed":
        evidence["descriptor_hashes_match_initialization"] = evidence["cached_descriptors"] == initial
        if not evidence["descriptor_hashes_match_initialization"]:
            evidence.update(status="Failed", reason="Native cached package descriptor hashes differ from completed initialization.")
    evidence["observed_utc"] = datetime.now(timezone.utc).isoformat()
    report.setdefault("package_pin_audits", {})[checkpoint] = evidence
    passed = evidence["status"] == "Passed"
    if required and not passed:
        raise EvidenceError("Native package pin audit " + checkpoint + " failed: " +
                            evidence.get("reason", "Selected pins or descriptors are unavailable."))
    return passed


def first_party_code_fingerprint(project: Path) -> str:
    """SDK initialization may create derived assets, but cannot rewrite code or its serialized identity."""
    digest = hashlib.sha256()
    code_extensions = (".cs", ".asmdef", ".asmref", ".rsp")
    directories = (project / "Assets", project.parent / "dotnet/src")
    for directory in directories:
        if not directory.is_dir():
            raise EvidenceError("The copied first-party source root is missing.")
        if any(item.is_symlink() or getattr(item, "is_junction", lambda: False)() for item in (directory, *directory.parents)):
            raise EvidenceError("Copied first-party source roots cannot use symlinks or junctions.")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
                raise EvidenceError("Copied first-party code cannot contain symlinks or junctions.")
            if path.is_file() and (directory.name == "src" or path.suffix.casefold() in code_extensions or
                                   path.name.casefold().endswith(tuple(extension + ".meta" for extension in code_extensions))):
                digest.update(path.relative_to(project.parent).as_posix().encode() + b"\0")
                digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def initialize_packages(editor: Path, project: Path, target: str, profile: dict, log: Path,
                        record: dict, execute: Callable, identity: dict, timeout: int = 480) -> None:
    """Populate one disposable project, retaining every strict log rejection.

    Completed/CompletedWithDiagnostics are operational outcomes, never Passed.
    Every caller must independently run its normal prepare in a NEW process,
    using a NEW log and the unchanged strict validator, before any test/build.
    """
    record.update(status="NotRun", acceptance_status="NotRun", started_utc=datetime.now(timezone.utc).isoformat(),
                  strict_log_status="NotRun", limits="Package initialization only; no clean import, preparation, tests, Player or gate acceptance.")
    original = None
    try:
        if project.absolute() != (log.parent.parent / "workspace/runtime/unity").absolute():
            raise EvidenceError("Package initialization must target this evidence directory's disposable project copy.")
        if target not in ("Win64", "Linux64"):
            raise EvidenceError("Unsupported package initialization target.")
        if identity.get("status") == "Mismatch":
            record["status"] = "Blocked"
            raise EvidenceError("Package initialization requires the pinned Editor file identity.")
        if identity.get("status") not in ("Verified", "NativeLogRequired"):
            record["status"] = "Blocked"
            raise EvidenceError("Editor identity inspection is unavailable for package initialization.")
        expected = package_snapshot(project)
        record["expected_package_pins"] = expected
        original = record["first_party_code_sha256"] = first_party_code_fingerprint(project)
        command = [str(editor), "-batchmode", "-nographics", "-quit", "-accept-apiupdate", "-projectPath", str(project),
                   "-buildTarget", target, "-forgetProjectPath", "-logFile", str(log)]
        record["command"] = command
        rc, text = execute(command, log, timeout)
        record.update(exit_code=rc, native_log_sha256=hashlib.sha256(log.read_bytes()).hexdigest() if log.is_file() else None)
        if text:
            try:
                validate_log(text)
                record["strict_log_status"] = "Passed"
            except EvidenceError as exception:
                diagnostics = [line for line in text.splitlines() if re.search(r"error CS\d+|\b\w*Exception\b|Assertion failed|Aborting batchmode|Fatal error|\b(?:warning|error)\b", line)]
                record.update(strict_log_status="Failed", strict_log_error_type=type(exception).__name__, strict_log_reason=str(exception),
                              diagnostic_lines=diagnostics, first_diagnostic=next(iter(diagnostics), None))
        record["updater_observations"] = [line for line in text.splitlines()
                                          if "ApiUpdater" in line or "API Updater" in line or "Finished running ScriptUpdaters" in line or
                                          re.match(r"Library[/\\]PackageCache[/\\].+\.cs$", line)]
        record["managed_exception_headers"] = managed_exception_headers(text)
        if LICENSE_FAILURE.search(text):
            record["status"] = "Blocked"
            raise EvidenceError("The pinned Editor could not obtain its license during package initialization.")
        if rc != 0 or not text or not log.is_file():
            raise EvidenceError(f"Package initialization returned {rc} or produced no native log artifact.")
        if log.read_text(encoding="utf-8", errors="replace") != text:
            raise EvidenceError("Package initialization native log text differs from its retained artifact.")
        if not re.search(r"Version is '" + re.escape(profile["editor"]) + r" \(" + re.escape(profile["revision"]) + r"\)", text):
            record["status"] = "Blocked"
            raise EvidenceError("Exact native Editor version and revision are missing from package initialization.")
        record["resolved_packages"] = resolved_package_evidence(project, expected)
        if record["resolved_packages"]["status"] != "Passed":
            raise EvidenceError(record["resolved_packages"].get("reason", "Initialized selected package pins could not be verified."))
        if record["strict_log_status"] == "Failed":
            record["known_sdk_update"] = classify_shadergraph_guid_update(text, project, record["resolved_packages"])
            if record["known_sdk_update"]["status"] != "ExpectedShaderGraphGuidApiUpdate":
                raise EvidenceError("Unexpected package-initialization diagnostics: " + record["known_sdk_update"]["reason"])
        elif record["managed_exception_headers"]:
            raise EvidenceError("Package initialization contains a managed exception header outside the strict log validator's signatures.")
        record["status"] = "CompletedWithDiagnostics" if record["strict_log_status"] == "Failed" else "Completed"
    except Exception as exception:
        if record["status"] != "Blocked":
            record["status"] = "Failed"
        record.update(error_type=type(exception).__name__, reason=str(exception).replace(str(Path.home()), "<HOME>"))
        raise
    finally:
        if original is not None:
            try:
                record["first_party_code_unchanged"] = first_party_code_fingerprint(project) == original
            except Exception as exception:
                record["first_party_code_unchanged"] = None
                record["code_audit_error"] = str(exception).replace(str(Path.home()), "<HOME>")
            if record["first_party_code_unchanged"] is not True:
                record["status"] = "Failed"
                record.setdefault("reason", "Package initialization changed first-party code or its final audit failed.")
        record["ended_utc"] = datetime.now(timezone.utc).isoformat()
    if record["status"] == "Failed":
        raise EvidenceError(record["reason"])
