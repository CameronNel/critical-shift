"""Fail closed on empty, failed, skipped, duplicated or unexpectedly discovered NUnit/TRX results."""
from collections import Counter
from pathlib import Path
import json
import xml.etree.ElementTree as ET


def validate(result: Path, expected: dict[str, int]) -> dict[str, int]:
    if not expected or any(type(count) is not int or count <= 0 for count in expected.values()):
        raise ValueError("The expected-test manifest is empty or invalid.")
    root = ET.parse(result).getroot()  # Missing or malformed files fail, never become a pass.
    summary = root.find(".//{*}ResultSummary")
    if summary is None or summary.attrib.get("outcome") != "Completed":
        raise ValueError("Missing or non-completed overall test-run outcome.")
    results = root.findall(".//{*}UnitTestResult")
    if not results:
        raise ValueError("Zero test results.")
    counts: Counter[str] = Counter()
    identities: set[str] = set()
    names: set[str] = set()
    for item in results:
        name = item.attrib.get("testName", "")
        test_id = item.attrib.get("testId", "")
        if not name or not test_id or test_id in identities or name in names:
            raise ValueError("Missing or duplicate test identity/name.")
        identities.add(test_id); names.add(name)
        if item.attrib.get("outcome") != "Passed":
            raise ValueError(f"Non-passing test: {name}: {item.attrib.get('outcome')}")
        method = name.split("(", 1)[0].rsplit(".", 1)[-1]
        counts[method] += 1
    if dict(counts) != expected:
        missing = {name: count for name, count in expected.items() if counts[name] != count}
        extra = {name: count for name, count in counts.items() if name not in expected}
        raise ValueError(f"Discovery mismatch. Expected differences={missing}; unexpected={extra}")
    counters = root.find(".//{*}Counters")
    if counters is None:
        raise ValueError("Missing result counters.")
    for key in ("total", "executed", "passed"):
        if int(counters.attrib.get(key, -1)) != len(results):
            raise ValueError(f"Inconsistent result counter: {key}")
    for key in ("failed", "error", "timeout", "aborted", "notExecuted", "notRunnable", "disconnected"):
        if int(counters.attrib.get(key, 0)) != 0:
            raise ValueError(f"Nonzero failure/skip counter: {key}")
    return {"executed": len(results), "passed": len(results), "failed": 0, "skipped": 0}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("expected-tests.json"))
    args = parser.parse_args()
    print(json.dumps(validate(args.results, json.loads(args.manifest.read_text())), indent=2))
