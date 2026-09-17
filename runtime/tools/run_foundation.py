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

RUNTIME = Path(__file__).resolve().parents[1]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_files(root: Path) -> list[Path]:
    roots = [root / "unity" / name for name in ("Assets", "Packages", "ProjectSettings")]
    files = [root / "toolchain.json"]
    if any(path.is_symlink() for path in [*roots, files[0]]):
        raise EvidenceError("Symlinked source roots are not permitted.")
    for directory in roots:
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise EvidenceError("Symlinks are not permitted in the validation input.")
            if path.is_file():
                files.append(path)
    return sorted(files)


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(root):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def execute(command: list[str], log: Path, timeout: int) -> tuple[int, str]:
    console = log.with_suffix(".console.log")
    with console.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=os.name != "nt",
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=stream, stderr=subprocess.STDOUT, check=False)
            else:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    # Do not retain personal home paths in shared evidence.
    home = str(Path.home())
    for path in (log, console):
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
            path.write_text(content.replace(home, "<HOME>"), encoding="utf-8")
    return code, text


def run(unity: str | None, output_parent: Path, target: str) -> tuple[int, Path]:
    output_parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix="wp01-", dir=output_parent))
    profile = json.loads((RUNTIME / "toolchain.json").read_text())
    catalogue = json.loads((RUNTIME / "validation" / "expected-tests.json").read_text())
    phases = {name: {"status": "NotRun"} for name in ("import", "EditMode", "PlayMode", "build", "player")}
    report = {"started_utc": utc(), "commit": os.environ.get("GITHUB_SHA", "local-uncommitted"),
              "profile": profile, "target": target, "status": "NotRun", "phases": phases,
              "independent_review": "NotRun", "limits": "WP-01 only; not Gate 0 acceptance, gameplay, visual or network validation."}
    current = "import"
    original = fingerprint(RUNTIME)
    report["source_sha256"] = original
    code = 1
    try:
        editor = Path(unity).expanduser().resolve() if unity else None
        if editor is None or not editor.is_file():
            report["status"] = "Blocked"
            raise EvidenceError("An activated Unity 6000.4.3f1 executable is required; pass --unity or UNITY_EDITOR.")
        if target not in ("Linux64", "Win64"):
            raise EvidenceError("Unsupported WP-01 build target.")
        work = out / "workspace" / "runtime"
        for path in source_files(RUNTIME):
            dest = work / path.relative_to(RUNTIME)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        project = work / "unity"
        logs = out / "logs"
        logs.mkdir()
        common = [str(editor), "-batchmode", "-nographics", "-projectPath", str(project),
                  "-buildTarget", target, "-forgetProjectPath"]

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
        if (target == "Win64") != (os.name == "nt"):
            report["status"] = "Blocked"
            raise EvidenceError("Build host cannot natively execute the selected target; use its matching OS.")
        log = logs / "player.log"
        phases["player"]["started_utc"] = utc()
        rc, text = execute([str(binary), "-batchmode", "-nographics", "--cs-smoke", "-logFile", str(log)], log, 60)
        phases["player"].update(exit_code=rc, ended_utc=utc(), log=str(log.relative_to(out)))
        phases["player"].update(validate_player(text, rc, profile["editor"], matches[0]))
        phases["player"]["status"] = "Passed"
        report["status"] = "Passed"
        code = 0
    except (EvidenceError, OSError, ValueError) as exc:
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        phases[current]["status"] = report["status"]
        report["reason"] = str(exc).replace(str(Path.home()), "<HOME>")
        code = 2 if report["status"] == "Blocked" else 1
    finally:
        report["source_unchanged"] = fingerprint(RUNTIME) == original
        if not report["source_unchanged"]:
            report["status"], report["reason"], code = "Failed", "Original input changed during validation.", 1
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
