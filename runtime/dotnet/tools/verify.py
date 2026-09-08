"""Build and validate the actual offline C# sources. No Unity, credentials or local game installation."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from check_boundaries import validate, TESTS
from verify_results import validate as validate_results

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
ENV = {**os.environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}


def run(args: list[str], log: str, expect_failure: bool = False) -> str:
    result = subprocess.run(args, cwd=ROOT, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (ARTIFACTS / log).write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="")
    if (expect_failure and result.returncode == 0) or (not expect_failure and result.returncode != 0):
        raise RuntimeError(f"Unexpected exit {result.returncode} for {args}")
    return result.stdout


def main() -> None:
    ARTIFACTS.mkdir(exist_ok=True)
    # A stale successful result must not survive a failed/unexecuted invocation.
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
    # A separate configuration prevents the deliberate failure from contaminating Release binaries.
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
               "configuration": "Release", "library_target": "netstandard2.1", "language": "C# 8.0",
               "tests": counts, "model_sequences": 100, "model_actions": 20000,
               "negative_control": "Expected failing NUnit test rejected by process and result checks",
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
