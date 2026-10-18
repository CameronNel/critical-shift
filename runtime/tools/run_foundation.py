"""Prepare, test, build and launch in a disposable copy; never edit source assets.

Uses an already activated Unity Editor. No credential collection or activation
bypass. An unavailable editor/license is Blocked, not a passing runtime check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from evidence import EvidenceError, validate_log, validate_player, validate_results
from editor_identity import inspect_editor
from package_initialization import audit_first_party_code, first_party_code_fingerprint, audit_package_pins, initialize_packages, package_snapshot

RUNTIME = Path(__file__).resolve().parents[1]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_files(root: Path) -> list[Path]:
    roots = [root / "unity" / name for name in ("Assets", "Packages", "ProjectSettings")]
    # Preserve the relative local-package location in the disposable runtime tree.
    # .NET output is configured outside this package; stale output must not be copied.
    package = root / "dotnet" / "src"
    if not (package / "package.json").is_file():
        raise EvidenceError("The canonical local gameplay source package is missing.")
    roots.append(package)
    files = [root / "toolchain.json"]
    def linked(path: Path) -> bool:
        return path.is_symlink() or getattr(path, "is_junction", lambda: False)()

    if any(linked(path) for path in [*roots, files[0]]):
        raise EvidenceError("Symlinks or junctions are not permitted in source roots.")
    if not files[0].is_file() or any(not directory.is_dir() for directory in roots):
        raise EvidenceError("A required toolchain file or Unity source directory is missing.")
    for directory in roots:
        for path in directory.rglob("*"):
            if linked(path):
                raise EvidenceError("Symlinks or junctions are not permitted in the validation input.")
            if directory == package and ({"bin", "obj"}.intersection(part.casefold() for part in path.relative_to(package).parts) or path.suffix.lower() == ".dll"):
                raise EvidenceError("Build output inside the Unity source package must be removed before validation.")
            if path.is_file():
                files.append(path)
    return sorted(files)


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(root):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def copy_inputs(root: Path, destination: Path) -> str:
    """Copy the declared inputs and return the fingerprint of what Unity will read."""
    for directory in ("unity/Assets", "unity/Packages", "unity/ProjectSettings", "dotnet/src"):
        (destination / directory).mkdir(parents=True, exist_ok=True)
    for path in source_files(root):
        target = destination / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return fingerprint(destination)


def checkout_revision(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                       text=True, stderr=subprocess.DEVNULL, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        return "unversioned-source-copy"


def audit_original(report: dict, root: Path, original: str | None) -> bool:
    """Keep the first failure even if the final source-integrity check also fails."""
    report["source_unchanged"] = None
    if original is None:
        return False
    try:
        report["source_unchanged"] = fingerprint(root) == original
        if not report["source_unchanged"]:
            report["source_audit_error"] = "Original input changed during validation."
    except Exception as exception:
        report["source_audit_error"] = ("Final source audit failed: " + str(exception)).replace(str(Path.home()), "<HOME>")
    if report["source_unchanged"] is not True:
        report["status"] = "Failed"
        report.setdefault("reason", report["source_audit_error"])
        return False
    return True


def execute(command: list[str], log: Path, timeout: int) -> tuple[int, str]:
    console = log.with_suffix(".console.log")
    try:
        with console.open("w", encoding="utf-8") as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=os.name != "nt",
                                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
            try:
                code = process.wait(timeout=timeout)
            except BaseException as interrupted:
                # Cancellation must also stop the process tree. Both cleanup operations
                # are bounded: failed taskkill must not leave an unbounded wait behind.
                try:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                       stdout=stream, stderr=subprocess.STDOUT, check=False, timeout=10)
                    else:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # The process group finished between timeout and cleanup.
                    process.wait(timeout=10)
                except (OSError, subprocess.SubprocessError) as cleanup:
                    raise EvidenceError(f"Native process cleanup failed ({type(cleanup).__name__}); verify process {process.pid} has stopped before retrying.") from interrupted
                if not isinstance(interrupted, subprocess.TimeoutExpired):
                    raise
                code = 124
    finally:
        # Do not retain personal home paths even after interruption or failed cleanup.
        home = str(Path.home())
        for path in (log, console):
            if path.exists():
                content = path.read_text(encoding="utf-8", errors="replace")
                path.write_text(content.replace(home, "<HOME>"), encoding="utf-8")
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    return code, text


def run(unity: str | None, output_parent: Path, target: str) -> tuple[int, Path]:
    output_parent = output_parent.resolve()
    if output_parent.is_relative_to(RUNTIME.parent) and not output_parent.is_relative_to(RUNTIME / "out"):
        raise EvidenceError("Inside the repository, evidence must stay under runtime/out, never source or art directories.")
    output_parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix="wp01-", dir=output_parent))
    phases = {name: {"status": "NotRun"} for name in ("package-initialize", "import", "EditMode", "PlayMode", "build", "player")}
    report = {"started_utc": utc(), "commit": checkout_revision(RUNTIME),
              "target": target, "status": "NotRun", "phases": phases,
              "independent_review": "NotRun", "limits": "WP-01 only; not Gate 0 acceptance, gameplay, visual or network validation."}
    current = "import"
    original = None
    project, expected_packages, native_attempted = None, None, False
    expected_code = None
    code = 1
    try:
        profile = json.loads((RUNTIME / "toolchain.json").read_text())
        catalogue = json.loads((RUNTIME / "validation" / "expected-tests.json").read_text())
        report.update(profile=profile, expected_tests=catalogue)
        original = fingerprint(RUNTIME)
        report["source_sha256"] = original
        editor = Path(unity).expanduser().resolve() if unity else None
        if editor is None or not editor.is_file():
            report["status"] = "Blocked"
            raise EvidenceError("An activated Unity 6000.4.3f1 executable is required; pass --unity or UNITY_EDITOR.")
        if target not in ("Linux64", "Win64"):
            raise EvidenceError("Unsupported WP-01 build target.")
        report["editor_file_identity"] = inspect_editor(editor, profile)
        work = out / "workspace" / "runtime"
        report["copied_source_sha256"] = copy_inputs(RUNTIME, work)
        if report["copied_source_sha256"] != original:
            raise EvidenceError("Disposable inputs differ from the recorded source fingerprint; Unity was not launched.")
        project = work / "unity"
        report["copied_code_sha256"] = expected_code = first_party_code_fingerprint(project)
        report["expected_package_pins"] = expected_packages = package_snapshot(project)
        logs = out / "logs"
        logs.mkdir()
        common = [str(editor), "-batchmode", "-nographics", "-projectPath", str(project),
                  "-buildTarget", target, "-forgetProjectPath"]

        current = "package-initialize"
        phases[current]["log"] = "logs/package-initialize.log"
        native_attempted = True
        initialize_packages(editor, project, target, profile, logs / "package-initialize.log", phases[current], execute,
                            report["editor_file_identity"])

        def invoke(name: str, options: list[str], timeout: int) -> str:
            nonlocal current
            current = name
            log = logs / (name + ".log")
            phases[name] = {"status": "NotRun", "started_utc": utc()}
            rc, text = execute(common + options + ["-logFile", str(log)], log, timeout)
            phases[name].update(exit_code=rc, ended_utc=utc(), log=str(log.relative_to(out)))
            if re.search(r"No valid Unity.*license|No valid license|Failed to activate|License is not active|No Unity Editor license", text, re.I):
                report["status"] = "Blocked"
                raise EvidenceError("Unity could not obtain a valid Editor license on this runner.")
            if rc != 0 or not text:
                raise EvidenceError(f"{name} returned {rc} or produced no native log.")
            validate_log(text)
            audit_package_pins(report, project, expected_packages, "after_" + name)
            audit_first_party_code(report, project, expected_code, "after_" + name)
            return text

        text = invoke("import", ["-quit", "-executeMethod", "CriticalShift.Bootstrap.Editor.FoundationBuild.Prepare"], 360)
        if "CS_FOUNDATION_PREPARED" not in text:
            raise EvidenceError("Native prepare entrypoint did not complete.")
        phases["import"]["status"] = "Passed"
        for suite in ("EditMode", "PlayMode"):
            result = out / (suite + ".xml")
            # -quit would allow Unity to terminate before the test runner finishes.
            invoke(suite, ["-runTests", "-testPlatform", suite, "-assemblyNames",
                           "CriticalShift.Tests." + suite, "-testResults", str(result)], 300)
            phases[suite].update(validate_results(result, set(catalogue[suite]), phases[suite]["exit_code"]))
            phases[suite]["status"] = "Passed"
        binary = out / "player" / ("CriticalShift.exe" if target == "Win64" else "CriticalShift.x86_64")
        text = invoke("build", ["-quit", "-executeMethod", "CriticalShift.Bootstrap.Editor.FoundationBuild.Build",
                                 "-csBuildPath", str(binary)], 480)
        matches = re.findall(r"CS_FOUNDATION_BUILD_OK guid=([0-9a-fA-F]{32})", text)
        if len(matches) != 1 or not binary.is_file():
            raise EvidenceError("Build identity or executable is missing.")
        phases["build"].update(status="Passed", build_guid=matches[0], executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
        current = "player"
        if (target == "Win64" and sys.platform != "win32") or (target == "Linux64" and not sys.platform.startswith("linux")):
            report["status"] = "Blocked"
            raise EvidenceError("Build host cannot natively execute the selected target; use its matching OS.")
        log = logs / "player.log"
        phases["player"]["started_utc"] = utc()
        rc, text = execute([str(binary), "-batchmode", "-nographics", "--cs-smoke", "-logFile", str(log)], log, 60)
        phases["player"].update(exit_code=rc, ended_utc=utc(), log=str(log.relative_to(out)))
        phases["player"].update(validate_player(text, rc, profile["editor"], matches[0]))
        phases["player"]["status"] = "Passed"
        audit_package_pins(report, project, expected_packages, "before_success")
        audit_first_party_code(report, project, expected_code, "before_success")
        report["status"] = "Passed"
        code = 0
    except Exception as exc:
        if phases[current]["status"] == "Blocked":
            report["status"] = "Blocked"
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        phases[current]["status"] = report["status"]
        report["error_type"] = type(exc).__name__
        report["reason"] = str(exc).replace(str(Path.home()), "<HOME>")
        code = 2 if report["status"] == "Blocked" else 1
    finally:
        if native_attempted and not audit_first_party_code(report, project, expected_code, "final", required=False):
            report["status"], code = "Failed", 1
            report.setdefault("reason", "Final copied code audit failed; see copied_code_audits.final.")
        if native_attempted and not audit_package_pins(report, project, expected_packages, "final", required=False) and report["status"] == "Passed":
            report["status"], code = "Failed", 1
            report.setdefault("reason", "Final native package pin audit failed; see package_pin_audits.final.")
        if not audit_original(report, RUNTIME, original):
            code = 1
        report["ended_utc"] = utc()
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        print("EVIDENCE_DIRECTORY=" + str(out))
    return code, out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unity", default=os.environ.get("UNITY_EDITOR"))
    parser.add_argument("--out", type=Path, default=RUNTIME / "out")
    parser.add_argument("--target", choices=("Linux64", "Win64"), default="Win64" if os.name == "nt" else "Linux64")
    args = parser.parse_args()
    sys.exit(run(args.unity, args.out.resolve(), args.target)[0])
