"""Static WP-01 checks. Does not claim Unity import or resolved-assembly validation."""
import json
import re
import subprocess
import hashlib
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
    for name, definition in definitions.items():
        for reference in definition["references"]:
            if reference not in definitions and reference not in {"UnityEngine.TestRunner", "UnityEditor.TestRunner"}:
                raise ValueError("Unresolved first-party assembly reference: " + reference)
        if name in {"CriticalShift.Unity.Shared", "CriticalShift.Features.Workers.Unity", "CriticalShift.FacilityPhysics.Unity"}:
            if any(reference.startswith("CriticalShift.") and reference != "CriticalShift.Unity.Shared" for reference in definition["references"]):
                raise ValueError("Forbidden peer implementation reference: " + name)
    rules = assets / "CriticalShift/Plugins/Rules"
    if rules.exists():
        build = json.loads((rules / "rules-build.json").read_text())
        if build["target"] != "netstandard2.1" or len(build["assemblies"]) != 8:
            raise ValueError("Wrong canonical rule-library inventory.")
        for relative, expected in build["sources"].items():
            if hashlib.sha256((RUNTIME / relative).read_bytes()).hexdigest() != expected:
                raise ValueError("Canonical rules changed; rebuild Unity DLLs: " + relative)
        for filename, expected in build["assemblies"].items():
            if hashlib.sha256((rules / filename).read_bytes()).hexdigest() != expected:
                raise ValueError("Rule DLL differs from its build manifest: " + filename)
        for definition in definitions.values():
            for filename in definition["precompiledReferences"]:
                if filename != "nunit.framework.dll" and filename not in build["assemblies"]:
                    raise ValueError("Unresolved first-party plugin reference: " + filename)
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
