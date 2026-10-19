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
from check_boundaries import validate, TESTS, RUNNER, LINKS
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
    # Short compositional endurance smoke and a real failing invariant control.
    soak_paths = {name: ARTIFACTS / ("soak-" + name + ".jsonl") for name in ("smoke", "negative", "medical-negative", "contamination-negative", "backup-negative", "fitting-negative", "replay")}
    for path in soak_paths.values(): path.unlink(missing_ok=True)
    run(["dotnet", executable, "--soak", "--cases", "12", "--report", str(soak_paths["smoke"])], "soak-smoke.log")
    pulses = [json.loads(line) for line in soak_paths["smoke"].read_text().splitlines()]
    if pulses[0]["Status"] != "Running" or pulses[-1]["Status"] != "Passed" or pulses[-1]["Cases"] != 12 or pulses[-1]["CheckedSteps"] <= 0:
        raise RuntimeError("Endurance smoke did not execute its requested cases.")
    assembly_hashes = pulses[0]["Assemblies"]
    required_assemblies = {"CriticalShift.Application.dll", "CriticalShift.Scenarios.dll"} | {
        "CriticalShift.Features." + feature + ".Domain.dll" for feature in ("Interaction", "Session", "Workers", "Materials", "Production", "Reactor", "Power")}
    if set(assembly_hashes) != required_assemblies or assembly_hashes != pulses[-1]["Assemblies"]:
        raise RuntimeError("Endurance report does not identify its complete gameplay assembly closure.")
    for filename, digest in assembly_hashes.items():
        if hashlib.sha256(Path(executable).with_name(filename).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Endurance assembly provenance mismatch: " + filename)
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--control", "failure", "--report", str(soak_paths["negative"])],
        "soak-negative.log", expect_failure=True)
    failed_soak = json.loads(soak_paths["negative"].read_text().splitlines()[-1])
    if failed_soak["Status"] != "Failed" or failed_soak["CaseSeed"] != 55 or failed_soak["Invariant"] != "Intentional negative control.":
        raise RuntimeError("The intentional endurance invariant failure was not reported.")
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--control", "medical-ledger", "--report", str(soak_paths["medical-negative"])],
        "soak-medical-negative.log", expect_failure=True)
    failed_medical = json.loads(soak_paths["medical-negative"].read_text().splitlines()[-1])
    if (failed_medical["Status"] != "Failed" or failed_medical["CaseSeed"] != 55 or
            failed_medical["Invariant"] != "Mixed medical stock disagrees with distinct new paid starts."):
        raise RuntimeError("The intentionally missing medical start was not caught by the independent ledger.")
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--control", "contamination-ledger", "--report", str(soak_paths["contamination-negative"])],
        "soak-contamination-negative.log", expect_failure=True)
    failed_contact = json.loads(soak_paths["contamination-negative"].read_text().splitlines()[-1])
    if (failed_contact["Status"] != "Failed" or failed_contact["CaseSeed"] != 55 or
            failed_contact["Invariant"] != "Contact meter differs from independent raw-load ledger."):
        raise RuntimeError("The intentionally missing exposure was not caught by the independent contact ledger.")
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--control", "backup-ledger", "--report", str(soak_paths["backup-negative"])],
        "soak-backup-negative.log", expect_failure=True)
    failed_backup = json.loads(soak_paths["backup-negative"].read_text().splitlines()[-1])
    if (failed_backup["Status"] != "Failed" or failed_backup["CaseSeed"] != 55 or
            failed_backup["Invariant"] != "Backup reserve differs from independent source chronology."):
        raise RuntimeError("The intentionally missing backup credit was not caught by the independent source ledger.")
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--control", "fitting-ledger", "--report", str(soak_paths["fitting-negative"])],
        "soak-fitting-negative.log", expect_failure=True)
    failed_fitting = json.loads(soak_paths["fitting-negative"].read_text().splitlines()[-1])
    if (failed_fitting["Status"] != "Failed" or failed_fitting["CaseSeed"] != 55 or
            failed_fitting["Invariant"] != "Suit protection differs from independent fitting ledger."):
        raise RuntimeError("The intentionally missing suit upgrade was not caught by the independent fitting ledger.")
    run(["dotnet", executable, "--soak", "--case-seed", "55", "--report", str(soak_paths["replay"])], "soak-replay.log")
    replay = json.loads(soak_paths["replay"].read_text().splitlines()[-1])
    if replay["Status"] != "Passed" or replay["Cases"] != 1: raise RuntimeError("Endurance seed reproduction failed.")
    before = soak_paths["smoke"].read_bytes()
    run(["dotnet", executable, "--soak", "--cases", "1", "--report", str(soak_paths["smoke"])], "soak-overwrite.log", expect_failure=True)
    if soak_paths["smoke"].read_bytes() != before: raise RuntimeError("Endurance report overwrote an existing file.")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        commit = "unversioned-local-worktree"
    source_hashes = {}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if path.is_file() and not {"bin", "obj", "artifacts", "__pycache__"}.intersection(relative.parts):
            source_hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for project, declarations in LINKS.items():
        for declaration in declarations:
            linked = (ROOT / project).parent.joinpath(declaration["Include"]).resolve()
            source_hashes["../" + linked.relative_to(ROOT.parent).as_posix()] = hashlib.sha256(linked.read_bytes()).hexdigest()
    summary = {"status": "Passed", "commit": commit, "sdk": version, "os": platform.platform(),
               "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
               "configuration": "Release", "library_target": "netstandard2.1", "language": "C# 8.0",
               "tests": counts,
               "model_suites": {"ownership": {"sequences": 100, "actions": 20000},
                                "timers": {"sequences": 100, "actions": 20000},
                                "machines": {"sequences": 100, "actions": 20000}},
               "negative_control": "Expected failing NUnit test rejected by process and result checks",
               "scenarios": scenario_results, "report_safety": safety, "scenario_negative_controls": "Assertion mismatch and empty script rejected",
               "logical_endurance_smoke": {"cases": 12, "seed_replay": "Passed", "invariant_negative_control": "Rejected", "medical_ledger_negative_control": "Rejected", "contamination_ledger_negative_control": "Rejected", "backup_ledger_negative_control": "Rejected", "fitting_ledger_negative_control": "Rejected", "report_overwrite": "Rejected", "assembly_sha256": assembly_hashes},
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
