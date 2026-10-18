"""Opt-in native sandbox import/physics tests in a disposable source copy. Never run while gaming is constrained.

Uses the already activated pinned Editor. Does not activate accounts, install new
packages, import the map or claim Player/playtest/multiplayer/performance acceptance.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from evidence import EvidenceError, validate_log, validate_results
from run_foundation import RUNTIME, execute, fingerprint, source_files, utc


def run(unity: str | None, output_parent: Path, target: str, build_player: bool = False) -> tuple[int, Path]:
    output_parent = output_parent.resolve()
    if output_parent.is_relative_to(RUNTIME.parent) and not output_parent.is_relative_to(RUNTIME / "out"):
        raise EvidenceError("Repository evidence must remain under runtime/out, outside source and map directories.")
    output_parent.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="sandbox-", dir=output_parent))
    profile = json.loads((RUNTIME / "toolchain.json").read_text())
    expected = json.loads((RUNTIME / "validation/sandbox-expected-tests.json").read_text())["PlayMode"]
    phases = {name: {"status": "NotRun"} for name in ("import", "PlayMode", "build", "player")}
    report = {"started_utc": utc(), "profile": profile, "target": target, "status": "NotRun", "phases": phases,
              "independent_review": "NotRun", "limits": "Sandbox import/declared physics cases only; no Player execution, feel, art, multiplayer, performance or gate acceptance."}
    try:
        report["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RUNTIME, text=True, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        report["commit"] = "unversioned-source-copy"
    original = fingerprint(RUNTIME)
    report["source_sha256"] = original
    current, code = "import", 1
    try:
        editor = Path(unity).expanduser().resolve() if unity else None
        if editor is None or not editor.is_file():
            report["status"] = "Blocked"
            raise EvidenceError("Pass the already activated Unity 6000.4.3f1 executable with --unity.")
        if target not in ("Linux64", "Win64"):
            raise EvidenceError("Unsupported sandbox desktop target.")
        work = output / "workspace/runtime"
        for path in source_files(RUNTIME):
            destination = work / path.relative_to(RUNTIME)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        logs = output / "logs"
        logs.mkdir()
        common = [str(editor), "-batchmode", "-nographics", "-projectPath", str(work / "unity"),
                  "-buildTarget", target, "-forgetProjectPath"]

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
            return text

        text = invoke("import", ["-quit", "-executeMethod", "CriticalShift.Sandbox.Editor.SandboxSceneBuilder.Prepare"], 480)
        if "CS_SANDBOX_PREPARED" not in text or profile["editor"] not in text or profile["revision"] not in text:
            raise EvidenceError("The sandbox prepare marker or exact native Editor identity is missing.")
        phases["import"]["status"] = "Passed"
        result = output / "PlayMode.xml"
        # No -quit here: the actual test runner owns termination after results are written.
        invoke("PlayMode", ["-runTests", "-testPlatform", "PlayMode", "-assemblyNames", "CriticalShift.Sandbox.Tests.PlayMode",
                            "-testResults", str(result)], 480)
        phases["PlayMode"].update(validate_results(result, set(expected), phases["PlayMode"]["exit_code"]))
        phases["PlayMode"]["status"] = "Passed"
        if build_player:
            binary = output / "player" / ("CriticalShiftSandbox.exe" if target == "Win64" else "CriticalShiftSandbox.x86_64")
            text = invoke("build", ["-quit", "-executeMethod", "CriticalShift.Sandbox.Editor.SandboxSceneBuilder.Build",
                                    "-csSandboxBuildPath", str(binary)], 600)
            identities = re.findall(r"CS_SANDBOX_BUILD_OK guid=([0-9a-fA-F]{32})", text)
            if len(identities) != 1 or not binary.is_file():
                raise EvidenceError("The sandbox build executable or identity is missing.")
            phases["build"].update(status="Passed", build_guid=identities[0])
        report["status"], code = "Passed", 0
    except (EvidenceError, OSError, ValueError) as exception:
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        phases[current]["status"] = report["status"]
        report["reason"] = str(exception).replace(str(Path.home()), "<HOME>")
        code = 2 if report["status"] == "Blocked" else 1
    finally:
        report["source_unchanged"] = fingerprint(RUNTIME) == original
        if not report["source_unchanged"]:
            report["status"], report["reason"], code = "Failed", "Original source changed during native validation.", 1
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
    arguments = parser.parse_args()
    sys.exit(run(arguments.unity, arguments.out, arguments.target, arguments.build_player)[0])
