"""Fail-closed validation of actual NUnit XML and standalone Player logs."""
from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET


class EvidenceError(ValueError):
    """The supplied execution evidence does not meet the declared fixture."""


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
        r"Assets[/\\]CriticalShift[/\\].*\b(?:warning|error)\b",
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
