"""Opt-in native sandbox import/physics tests in a disposable source copy. Never run while gaming is constrained.

Uses the already activated pinned Editor. Does not activate accounts, install new
packages or import the map. Optional headless Player smoke is startup/teardown
evidence only, not rendered playtest, multiplayer or performance acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

from evidence import EvidenceError, read_result_evidence, validate_log, validate_results, validate_sandbox_player
from editor_identity import inspect_editor
from check_source import check
from run_foundation import RUNTIME, audit_original, checkout_revision, copy_inputs, execute, fingerprint, utc
from package_initialization import audit_package_pins, initialize_packages, package_snapshot


def run(unity: str | None, output_parent: Path, target: str, build_player: bool = False, run_player: bool = False) -> tuple[int, Path]:
    output_parent = output_parent.resolve()
    if output_parent.is_relative_to(RUNTIME.parent) and not output_parent.is_relative_to(RUNTIME / "out"):
        raise EvidenceError("Repository evidence must remain under runtime/out, outside source and map directories.")
    output_parent.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="sandbox-", dir=output_parent))
    phases = {name: {"status": "NotRun"} for name in ("source", "package-initialize", "import", "PlayMode", "build", "player")}
    report = {"started_utc": utc(), "commit": checkout_revision(RUNTIME), "target": target, "status": "NotRun", "phases": phases,
              "independent_review": "NotRun", "limits": "Sandbox source/import/declared physics cases and explicitly requested build/headless startup phases only; no rendered playtest, feel, art, multiplayer, performance or gate acceptance."}
    original = None
    project, expected_packages, native_attempted = None, None, False
    current, code = "source", 1
    try:
        profile = json.loads((RUNTIME / "toolchain.json").read_text())
        expected = json.loads((RUNTIME / "validation/sandbox-expected-tests.json").read_text())["PlayMode"]
        report.update(profile=profile, expected_playmode_tests=expected)
        original = fingerprint(RUNTIME)
        report["source_sha256"] = original
        if run_player and not build_player:
            raise EvidenceError("Sandbox Player execution requires an explicit --build-player in the same source run.")
        phases["source"] = check(RUNTIME)
        current = "import"
        editor = Path(unity).expanduser().resolve() if unity else None
        if editor is None or not editor.is_file():
            report["status"] = "Blocked"
            raise EvidenceError("Pass the already activated Unity 6000.4.3f1 executable with --unity.")
        if target not in ("Linux64", "Win64"):
            raise EvidenceError("Unsupported sandbox desktop target.")
        report["editor_file_identity"] = inspect_editor(editor, profile)
        work = output / "workspace/runtime"
        report["copied_source_sha256"] = copy_inputs(RUNTIME, work)
        if report["copied_source_sha256"] != original:
            raise EvidenceError("Disposable inputs differ from the recorded source fingerprint; Unity was not launched.")
        project = work / "unity"
        report["expected_package_pins"] = expected_packages = package_snapshot(project)
        logs = output / "logs"
        logs.mkdir()
        common = [str(editor), "-batchmode", "-nographics", "-projectPath", str(work / "unity"),
                  "-buildTarget", target, "-forgetProjectPath"]

        current = "package-initialize"
        phases[current]["log"] = "logs/package-initialize.log"
        native_attempted = True
        initialize_packages(editor, work / "unity", target, profile, logs / "package-initialize.log", phases[current], execute,
                            report["editor_file_identity"])

        def invoke(name: str, options: list[str], timeout: int) -> str:
            nonlocal current
            current = name
            log = logs / (name + ".log")
            phases[name] = {"status": "NotRun", "started_utc": utc()}
            rc, text = execute(common + options + ["-logFile", str(log)], log, timeout)
            phases[name].update(exit_code=rc, ended_utc=utc(), log=str(log.relative_to(output)))
            if re.search(r"No valid Unity.*license|No valid license|Failed to activate|License is not active|No Unity Editor license", text, re.I):
                report["status"] = "Blocked"
                raise EvidenceError("The pinned Editor could not obtain its license.")
            if name == "build" and "owner-selected URP pipeline must be configured" in text:
                report["status"] = "Blocked"
                raise EvidenceError("URP project migration is required before a sandbox Player build.")
            if rc != 0 or not text:
                raise EvidenceError(f"{name} returned {rc} or produced no native log.")
            validate_log(text)
            audit_package_pins(report, project, expected_packages, "after_" + name)
            return text

        text = invoke("import", ["-quit", "-executeMethod", "CriticalShift.Sandbox.Editor.SandboxSceneBuilder.Prepare"], 480)
        if "CS_SANDBOX_PREPARED" not in text or profile["editor"] not in text or profile["revision"] not in text:
            raise EvidenceError("The sandbox prepare marker or exact native Editor identity is missing.")
        graphs = re.findall(r"CS_SANDBOX_ASSEMBLIES count=(\d+)", text)
        if len(graphs) != 1 or int(graphs[0]) != phases["source"]["production_asmdefs"]:
            raise EvidenceError("The native production-assembly graph inventory differs from the checked source declarations.")
        phases["import"]["production_assemblies"] = int(graphs[0])
        phases["import"]["status"] = "Passed"
        result = output / "PlayMode.xml"
        # No -quit here: the actual test runner owns termination after results are written.
        try:
            invoke("PlayMode", ["-runTests", "-testPlatform", "PlayMode", "-assemblyNames", "CriticalShift.Sandbox.Tests.PlayMode",
                                "-testResults", str(result)], 480)
            phases["PlayMode"].update(validate_results(result, set(expected), phases["PlayMode"]["exit_code"]))
            phases["PlayMode"]["status"] = "Passed"
        finally:
            # A real failed Test Runner commonly exits 2. Preserve its XML before
            # propagating that first failure; observations never substitute for validation.
            phases["PlayMode"]["result_artifact"] = result.relative_to(output).as_posix()
            phases["PlayMode"]["result_evidence"] = read_result_evidence(result, set(expected))
        if build_player:
            binary = output / "player" / ("CriticalShiftSandbox.exe" if target == "Win64" else "CriticalShiftSandbox.x86_64")
            text = invoke("build", ["-quit", "-executeMethod", "CriticalShift.Sandbox.Editor.SandboxSceneBuilder.Build",
                                    "-csSandboxBuildPath", str(binary)], 600)
            identities = re.findall(r"CS_SANDBOX_BUILD_OK guid=([0-9a-fA-F]{32})", text)
            if len(identities) != 1 or not binary.is_file():
                raise EvidenceError("The sandbox build executable or identity is missing.")
            phases["build"].update(status="Passed", build_guid=identities[0], executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
            if run_player:
                current = "player"
                if (target == "Win64" and sys.platform != "win32") or (target == "Linux64" and not sys.platform.startswith("linux")):
                    report["status"] = "Blocked"
                    raise EvidenceError("The build host cannot natively execute this Player target; use its matching OS.")
                log = logs / "player.log"
                phases["player"] = {"status": "NotRun", "started_utc": utc()}
                rc, text = execute([str(binary), "-batchmode", "-nographics", "--cs-sandbox-smoke", "-logFile", str(log)], log, 60)
                phases["player"].update(exit_code=rc, ended_utc=utc(), log=str(log.relative_to(output)))
                phases["player"].update(validate_sandbox_player(text, rc, profile["editor"], identities[0]))
                phases["player"]["status"] = "Passed"
        audit_package_pins(report, project, expected_packages, "before_success")
        report["status"], code = "Passed", 0
    except Exception as exception:
        if phases[current]["status"] == "Blocked":
            report["status"] = "Blocked"
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        phases[current]["status"] = report["status"]
        report["error_type"] = type(exception).__name__
        report["reason"] = str(exception).replace(str(Path.home()), "<HOME>")
        code = 2 if report["status"] == "Blocked" else 1
    finally:
        if native_attempted and not audit_package_pins(report, project, expected_packages, "final", required=False) and report["status"] == "Passed":
            report["status"], code = "Failed", 1
            report.setdefault("reason", "Final native package pin audit failed; see package_pin_audits.final.")
        if not audit_original(report, RUNTIME, original):
            code = 1
        report["ended_utc"] = utc()
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        print("EVIDENCE_DIRECTORY=" + str(output))
    return code, output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unity")
    parser.add_argument("--out", type=Path, default=RUNTIME / "out")
    parser.add_argument("--target", choices=("Win64", "Linux64"), default="Win64")
    parser.add_argument("--build-player", action="store_true")
    parser.add_argument("--run-player", action="store_true", help="Opt in to a headless startup/teardown smoke for this run's new Player build.")
    arguments = parser.parse_args()
    sys.exit(run(arguments.unity, arguments.out, arguments.target, arguments.build_player, arguments.run_player)[0])
