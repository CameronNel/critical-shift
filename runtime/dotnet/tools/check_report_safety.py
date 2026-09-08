"""Execute the real scenario CLI against alias paths. Never touch source fixtures."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile


def verify(executable: Path, source: Path, environment: dict) -> dict:
    cases = []
    with tempfile.TemporaryDirectory(prefix="scenario-output-safety-") as temp:
        root = Path(temp)
        original = root / "Input.json"
        original.write_bytes(source.read_bytes())
        digest = hashlib.sha256(original.read_bytes()).hexdigest()
        def attempt(label, report):
            result = subprocess.run(["dotnet", str(executable), "--scenario", str(original), "--report", str(report)],
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment, timeout=60)
            if result.returncode == 0 or hashlib.sha256(original.read_bytes()).hexdigest() != digest:
                raise RuntimeError("Unsafe report handling: " + label)
            cases.append(label)
        attempt("identical", original)
        attempt("parent-dot-alias", root / "." / "Input.json")
        hardlink = root / "hardlink.json"
        os.link(original, hardlink)
        attempt("hardlink", hardlink)
        if os.name == "nt":
            attempt("case-alias", root / "input.JSON")
        else:
            symlink = root / "symlink.json"; symlink.symlink_to(original)
            attempt("symlink", symlink)
            directory = root / "dir-alias"; directory.symlink_to(root, target_is_directory=True)
            attempt("symlinked-parent", directory / "Input.json")
        unrelated = root / "existing-report.json"; unrelated.write_text("do not replace")
        attempt("existing-unrelated-report", unrelated)
        if unrelated.read_text() != "do not replace": raise RuntimeError("Existing report was overwritten.")
    return {"status": "Passed", "cases": cases, "contract": "create-new only; existing paths are never overwritten"}
