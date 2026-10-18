"""Fail-closed validation of actual NUnit XML and standalone Player logs."""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


class EvidenceError(ValueError):
    """The supplied execution evidence does not meet the declared fixture."""


def read_result_evidence(path: Path, expected: set[str]) -> dict:
    """Retain what an XML artifact actually reports; this never grants test acceptance."""
    evidence = {"artifact_present": False}
    try:
        evidence["artifact_present"] = path.is_file()
        if not evidence["artifact_present"]:
            evidence["read_error"] = "The native test result artifact is missing."
            return evidence
        raw = path.read_bytes()
        evidence["sha256"] = hashlib.sha256(raw).hexdigest()
        root = ET.fromstring(raw)
        if root.tag != "test-run":
            raise EvidenceError("The result artifact is not a NUnit test-run.")
        evidence["reported_result"] = root.get("result")
        evidence["reported_counts"] = {}
        malformed = []
        for name in ("total", "passed", "failed", "skipped", "inconclusive"):
            value = root.get(name)
            if value is None or not re.fullmatch(r"\d+", value):
                malformed.append(name)
            else:
                evidence["reported_counts"][name] = int(value)
        if malformed:
            evidence["invalid_summary_fields"] = malformed
        cases = list(root.iter("test-case"))
        names = [case.get("fullname", "") for case in cases]
        results = [case.get("result", "Missing") for case in cases]
        counts = Counter(names)
        evidence.update(xml_test_cases=len(cases), test_identities=names, observed_case_results=dict(Counter(results)),
                        duplicate_test_identities=sorted(name for name, count in counts.items() if count > 1),
                        missing_expected_tests=sorted(expected - set(names)), unexpected_tests=sorted(set(names) - expected))
        failures = []
        for case in cases:
            failure = case.find("failure")
            if failure is not None or case.get("result", "").startswith("Failed"):
                failures.append({"fullname": case.get("fullname", ""), "result": case.get("result"),
                                 "label": case.get("label"),
                                 "message": (case.findtext("failure/message") or "").replace(str(Path.home()), "<HOME>"),
                                 "stack_trace": (case.findtext("failure/stack-trace") or "").replace(str(Path.home()), "<HOME>")})
        evidence["failed_cases"] = failures
        evidence["failed_test_identities"] = [case["fullname"] for case in failures]
    except Exception as exception:
        evidence["read_error"] = ("Native test evidence could not be parsed: " + str(exception)).replace(str(Path.home()), "<HOME>")
    return evidence


def validate_results(path: Path, expected: set[str], exit_code: int) -> dict:
    if exit_code != 0:
        raise EvidenceError(f"Test process exited {exit_code}.")
    if not expected:
        raise EvidenceError("The expected test catalogue is empty.")
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as exc:
        raise EvidenceError("Missing or malformed test results.") from exc
    root = tree.getroot()
    if root.tag != "test-run" or root.get("result") != "Passed":
        raise EvidenceError("The NUnit run did not pass.")
    cases = list(root.iter("test-case"))
    names = [case.get("fullname", "") for case in cases]
    if len(names) != len(set(names)) or set(names) != expected:
        raise EvidenceError("Discovered test identities differ from the required catalogue.")
    if any(case.get("result") != "Passed" for case in cases):
        raise EvidenceError("A required test failed, was skipped or did not run.")
    try:
        counts = {key: int(root.get(key, "-1"))
                  for key in ("total", "passed", "failed", "skipped", "inconclusive")}
    except ValueError as exc:
        raise EvidenceError("Malformed NUnit summary counts.") from exc
    if (counts["total"] != len(expected) or counts["passed"] != len(expected)
            or any(counts[k] != 0 for k in ("failed", "skipped", "inconclusive"))):
        raise EvidenceError("NUnit summary counts disagree with the required results.")
    if any(node.get("result") not in (None, "Passed") for node in root.iter("test-suite")):
        raise EvidenceError("A containing test suite failed or did not run.")
    return {"discovered": len(cases), "executed": len(cases), **counts}


def validate_log(text: str) -> None:
    # Unity logs are not structured: reject known critical signatures and all
    # first-party C# diagnostics. This is not a universal error detector.
    patterns = (
        r"\b(?:NullReference|InvalidOperation|MissingReference|Argument|TypeLoad|FileNotFound|NotImplemented)Exception\b",
        r"\b(?:error CS\d+|Unhandled [Ee]xception|Assertion failed|Aborting batchmode|Fatal error)\b",
        r"(?:Assets[/\\]CriticalShift[/\\]|Packages[/\\]com\.criticalshift\.gameplay[/\\]|runtime[/\\]dotnet[/\\]src[/\\]).*\b(?:warning|error)\b",
    )
    if any(re.search(pattern, text) for pattern in patterns):
        raise EvidenceError("Execution log contains a critical error or first-party diagnostic.")


def validate_player(text: str, exit_code: int, editor: str, build_guid: str) -> dict:
    if exit_code != 0:
        raise EvidenceError(f"Player exited {exit_code}.")
    validate_log(text)
    ready = re.findall(r"^CS_FOUNDATION_READY unity=(\S+) build=(\S+)$", text, re.M)
    stopped = re.findall(r"^CS_FOUNDATION_STOPPED frames=(\d+) errors=(\d+)$", text, re.M)
    if len(ready) != 1 or len(stopped) != 1:
        raise EvidenceError("Expected one Ready and one Stopped marker from the Player.")
    if ready[0] != (editor, build_guid) or not re.fullmatch(r"[0-9a-fA-F]{32}", build_guid):
        raise EvidenceError("Player version or build identity does not match this build.")
    if text.index("CS_FOUNDATION_READY") > text.index("CS_FOUNDATION_STOPPED"):
        raise EvidenceError("Player stopped before becoming ready.")
    frames, errors = map(int, stopped[0])
    if frames < 12 or errors != 0:
        raise EvidenceError("Player did not finish the required error-free frame lifetime.")
    return {"frames": frames, "errors": errors, "build_guid": build_guid, "exit_code": exit_code}


def validate_sandbox_player(text: str, exit_code: int, editor: str, build_guid: str) -> dict:
    if exit_code != 0:
        raise EvidenceError(f"Sandbox Player exited {exit_code}.")
    validate_log(text)
    ready = re.findall(r"^CS_SANDBOX_PLAYER_READY unity=(\S+) build=(\S+) epoch=([0-9a-fA-F]{32}) bindings=(\d+) bodies=(\d+) meshes=(\d+)$", text, re.M)
    stopped = re.findall(r"^CS_SANDBOX_PLAYER_STOPPED epoch=([0-9a-fA-F]{32}) frames=(\d+) milliseconds=(\d+) errors=(\d+) bindings=(\d+) bodies=(\d+) objects=(\d+) claims=(\d+) timers=(\d+) connections=(\d+)$", text, re.M)
    if (len(ready) != 1 or len(stopped) != 1 or text.count("CS_SANDBOX_PLAYER_READY") != 1
            or text.count("CS_SANDBOX_PLAYER_STOPPED") != 1):
        raise EvidenceError("Expected one sandbox Player Ready and one complete Stopped marker.")
    version, identity, epoch, bindings, bodies, meshes = ready[0]
    if version != editor or identity != build_guid or not re.fullmatch(r"[0-9a-fA-F]{32}", build_guid):
        raise EvidenceError("Sandbox Player version or build identity differs from this build.")
    if epoch == "0" * 32 or stopped[0][0] != epoch or text.index("CS_SANDBOX_PLAYER_READY") > text.index("CS_SANDBOX_PLAYER_STOPPED"):
        raise EvidenceError("Sandbox Player world identity or lifecycle ordering is invalid.")
    if (int(bindings), int(bodies)) != (10, 31) or int(meshes) < 1:
        raise EvidenceError("Sandbox Player has an incomplete physical or generated-mesh inventory.")
    frames, milliseconds, errors, *remaining = map(int, stopped[0][1:])
    if frames < 120 or milliseconds < 2000 or errors != 0 or any(remaining):
        raise EvidenceError("Sandbox Player did not complete its required clean lifetime and zero-reference teardown.")
    return {"frames": frames, "milliseconds": milliseconds, "errors": errors, "meshes": int(meshes),
            "initial_bindings": int(bindings), "initial_bodies": int(bodies), "epoch": epoch,
            "remaining_bindings": remaining[0], "remaining_bodies": remaining[1], "remaining_objects": remaining[2],
            "remaining_claims": remaining[3], "remaining_timers": remaining[4], "remaining_connections": remaining[5],
            "build_guid": build_guid, "exit_code": exit_code}
