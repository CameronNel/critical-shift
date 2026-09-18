"""Build and validate the actual offline C# sources. No Unity, credentials or local game installation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from check_boundaries import validate, TESTS, RUNNER
from verify_results import validate as validate_results
from check_report_safety import verify as verify_report_safety

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
ENV = {**os.environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}


def run(args: list[str], log: str, expect_failure: bool = False) -> str:
    result = subprocess.run(args, cwd=ROOT, env=ENV, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=600)
    (ARTIFACTS / log).write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="")
    if (expect_failure and result.returncode == 0) or (not expect_failure and result.returncode != 0):
        raise RuntimeError(f"Unexpected exit {result.returncode} for {args}")
    return result.stdout


def main() -> None:
    started = datetime.now(timezone.utc).isoformat()
    ARTIFACTS.mkdir(exist_ok=True)
    for path in [ARTIFACTS / "summary.json", ARTIFACTS / "positive" / "positive.trx", ARTIFACTS / "negative" / "negative.trx"]:
        path.unlink(missing_ok=True)
    errors = validate(ROOT)
    if errors: raise RuntimeError("\n".join(errors))
    run([sys.executable, "tools/test_guards.py"], "guard-tests.log")
    version = run(["dotnet", "--version"], "sdk-version.log").strip()
    run(["dotnet", "--info"], "sdk-info.log")
    run(["dotnet", "restore", TESTS], "restore.log")
    run(["dotnet", "build", TESTS, "--no-restore", "-c", "Release"], "build.log")
    run(["dotnet", "test", TESTS, "--no-build", "--no-restore", "-c", "Release", "--logger",
         "trx;LogFileName=positive.trx", "--results-directory", "artifacts/positive"], "positive.log")
    expected = json.loads((ROOT / "tools/expected-tests.json").read_text())
    counts = validate_results(ARTIFACTS / "positive/positive.trx", expected)
    run(["dotnet", "test", TESTS, "--no-restore", "-c", "NegativeControl", "-p:DefineConstants=NEGATIVE_TEST_CONTROL",
         "--filter", "FullyQualifiedName~IntentionalFailureControl", "--logger", "trx;LogFileName=negative.trx",
         "--results-directory", "artifacts/negative"], "negative-control.log", expect_failure=True)
    negatives = ET.parse(ARTIFACTS / "negative/negative.trx").getroot().findall(".//{*}UnitTestResult")
    if len(negatives) != 1 or negatives[0].attrib.get("outcome") != "Failed" or "IntentionalFailureControl" not in negatives[0].attrib.get("testName", ""):
        raise RuntimeError("The intended failing NUnit fixture was not actually executed and detected.")
    try:
        validate_results(ARTIFACTS / "negative/negative.trx", {"IntentionalFailureControl": 1})
    except ValueError:
        pass
    else:
        raise RuntimeError("The result verifier incorrectly accepted a real failing test.")
    # Run the actual executable against versioned input, not a reimplementation in Python.
    run(["dotnet", "restore", RUNNER], "scenario-restore.log")
    run(["dotnet", "build", RUNNER, "--no-restore", "-c", "Release"], "scenario-build.log")
    executable = str(ROOT / "tools/CriticalShift.Scenarios/bin/Release/net8.0/CriticalShift.Scenarios.dll")
    scenario_manifest = json.loads((ROOT / "tools/expected-scenarios.json").read_text())
    if not scenario_manifest or set(scenario_manifest) != {p.stem for p in (ROOT / "scenarios").glob("*.json")}:
        raise RuntimeError("Scenario discovery does not match the expected manifest.")
    scenario_results = {}
    for name, expected_run in scenario_manifest.items():
        report = ARTIFACTS / "scenarios" / (name + ".json")
        report.unlink(missing_ok=True)
        run(["dotnet", executable, "--scenario", str(ROOT / "scenarios" / (name + ".json")),
             "--report", str(report), "--repeat", str(expected_run["runs"])], "scenario-" + name + ".log")
        data = json.loads(report.read_text())
        if (data["Status"] != "Passed" or data["Name"] != name or
            data["CompletedRuns"] != expected_run["runs"] or
            data["CompletedSteps"] != expected_run["steps_per_run"] * expected_run["runs"] or
            data["Assertions"] != expected_run["assertions_per_run"] * expected_run["runs"]):
            raise RuntimeError("Scenario outcome/discovery mismatch: " + name)
        scenario_results[name] = {k: data[k] for k in ("Status", "CompletedRuns", "CompletedSteps", "Assertions")}
    bad = json.loads((ROOT / "scenarios/worker-recovery.json").read_text())
    bad["steps"][0]["expect"] = "IntentionalMismatch"
    bad_path = ARTIFACTS / "negative-scenario.json"
    bad_path.write_text(json.dumps(bad))
    bad_report = ARTIFACTS / "negative-scenario-result.json"
    bad_report.unlink(missing_ok=True)
    run(["dotnet", executable, "--scenario", str(bad_path), "--report", str(bad_report)],
        "negative-scenario.log", expect_failure=True)
    failed = json.loads(bad_report.read_text())
    if (failed["Status"] != "Failed" or failed["LastStep"] != 1 or failed["CompletedSteps"] != 0 or
        "IntentionalMismatch" not in (failed["Error"] or "")):
        raise RuntimeError("The intended scenario assertion failure was not detected.")
    empty_path = ARTIFACTS / "empty-scenario.json"
    empty_path.write_text(json.dumps({"name": "empty", "steps": []}))
    empty_report = ARTIFACTS / "empty-scenario-result.json"
    empty_report.unlink(missing_ok=True)
    run(["dotnet", executable, "--scenario", str(empty_path), "--report", str(empty_report)],
        "empty-scenario.log", expect_failure=True)
    if empty_report.exists() and json.loads(empty_report.read_text()).get("Status") == "Passed":
        raise RuntimeError("An empty scenario cannot pass.")
    safety = verify_report_safety(Path(executable), ROOT / "scenarios/worker-recovery.json", ENV)
    (ARTIFACTS / "report-safety.json").write_text(json.dumps(safety, indent=2) + "\n")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        commit = "unversioned-local-worktree"
    source_hashes = {}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if path.is_file() and not {"bin", "obj", "artifacts", "__pycache__"}.intersection(relative.parts):
            source_hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    summary = {"status": "Passed", "commit": commit, "sdk": version, "os": platform.platform(),
               "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
               "configuration": "Release", "library_target": "netstandard2.1", "language": "C# 8.0",
               "tests": counts,
               "model_suites": {"ownership": {"sequences": 100, "actions": 20000},
                                "timers": {"sequences": 100, "actions": 20000},
                                "machines": {"sequences": 100, "actions": 20000}},
               "negative_control": "Expected failing NUnit test rejected by process and result checks",
               "scenarios": scenario_results, "report_safety": safety, "scenario_negative_controls": "Assertion mismatch and empty script rejected",
               "unity": "NotRun", "physics": "NotRun", "multiplayer_transport": "NotRun",
               "source_sha256": source_hashes}
    (ARTIFACTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "source_sha256"}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"OFFLINE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
