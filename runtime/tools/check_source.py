"""Static WP-01 checks. Does not claim Unity import or resolved-assembly validation."""
import json
import re
import subprocess
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1]


def check() -> dict:
    assets = RUNTIME / "unity/Assets"
    guids = set()
    for meta in assets.rglob("*.meta"):
        target = meta.with_suffix("")
        if not target.exists():
            raise ValueError("Orphaned metadata: " + str(meta.relative_to(RUNTIME)))
        matches = re.findall(r"^guid: ([0-9a-f]{32})$", meta.read_text(), re.M)
        if len(matches) != 1 or matches[0] in guids:
            raise ValueError("Missing, invalid or duplicate asset GUID.")
        guids.add(matches[0])
    for asset in assets.rglob("*"):
        if not asset.name.endswith(".meta") and not Path(str(asset) + ".meta").is_file():
            raise ValueError("Missing metadata: " + str(asset.relative_to(RUNTIME)))
    definitions = {}
    for path in assets.rglob("*.asmdef"):
        data = json.loads(path.read_text())
        if data["name"] in definitions:
            raise ValueError("Duplicate assembly name.")
        definitions[data["name"]] = data
    for path in assets.rglob("*.cs"):
        owner = next((p for p in [path.parent, *path.parents] if p.is_relative_to(assets) and list(p.glob("*.asmdef"))), None)
        if owner is None:
            raise ValueError("Unowned first-party C# file: " + str(path))
    pure = definitions["CriticalShift.ProcessLifetime"]
    if not pure["noEngineReferences"] or pure["references"]:
        raise ValueError("The WP-01 process-lifetime assembly must remain engine-independent.")
    profile = json.loads((RUNTIME / "toolchain.json").read_text())
    manifest = json.loads((RUNTIME / "unity/Packages/manifest.json").read_text())
    if manifest["dependencies"]["com.unity.test-framework"] != profile["testFramework"]:
        raise ValueError("Manifest and profile versions differ.")
    version = (RUNTIME / "unity/ProjectSettings/ProjectVersion.txt").read_text()
    if f'm_EditorVersion: {profile["editor"]}\n' not in version or profile["revision"] not in version:
        raise ValueError("Editor profile differs from ProjectVersion.txt.")
    return {"status": "Passed", "check": "static-source-only", "metadata_guids": len(guids),
            "asmdefs": len(definitions), "csharp_files": len(list(assets.rglob("*.cs"))),
            "limits": "Not a resolved Unity graph, native import, gameplay or art review."}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
