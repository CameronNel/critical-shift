"""Static WP-01 checks. Does not claim Unity import or resolved-assembly validation."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1]


def gameplay_sources(root: Path) -> Path:
    package = root / "dotnet/src"
    manifest = json.loads((root / "unity/Packages/manifest.json").read_text())
    dependency = manifest["dependencies"].get("com.criticalshift.gameplay")
    if dependency != "file:../../dotnet/src":
        raise ValueError("The Unity gameplay package must reference the canonical local source path.")
    descriptor = json.loads((package / "package.json").read_text())
    if descriptor["name"] != "com.criticalshift.gameplay" or descriptor.get("dependencies") != {}:
        raise ValueError("Unexpected gameplay package identity or external runtime dependency.")
    properties = ET.parse(package / "Directory.Build.props").getroot()
    output = "$(MSBuildThisFileDirectory)../artifacts/compiled/$(MSBuildProjectName)/"
    if ([element.tag for element in properties] != ["Import", "PropertyGroup"] or
            properties[0].attrib != {"Project": "../Directory.Build.props"} or
            [element.tag for element in properties[1]] != ["BaseOutputPath", "BaseIntermediateOutputPath"] or
            properties.findtext(".//BaseOutputPath") != output + "bin/" or
            properties.findtext(".//BaseIntermediateOutputPath") != output + "obj/"):
        raise ValueError("Canonical source-project outputs must remain outside Unity's package.")
    names = {"CriticalShift.Application"} | {
        "CriticalShift.Features." + feature + ".Domain" for feature in
        ("Interaction", "Session", "Workers", "Materials", "Production", "Reactor", "Power")}
    paths = list(package.rglob("*.asmdef"))
    definitions = {path.parent.name: path for path in paths}
    if len(paths) != len(names) or set(definitions) != names:
        raise ValueError("Missing or unexpected canonical gameplay assembly definitions.")
    for name, path in definitions.items():
        if path.name != name + ".asmdef":
            raise ValueError("Unexpected gameplay assembly filename: " + str(path))
        definition = json.loads(path.read_text())
        project = ET.parse(path.with_suffix(".csproj")).getroot()
        references = {Path(p.attrib["Include"]).stem for p in project.findall(".//ProjectReference")}
        if (definition["name"] != name or set(definition["references"]) != references or
                not definition["noEngineReferences"] or not definition["overrideReferences"] or
                definition["autoReferenced"] or definition["allowUnsafeCode"] or
                any(definition[field] for field in ("includePlatforms", "excludePlatforms", "precompiledReferences", "defineConstraints", "versionDefines"))):
            raise ValueError("Unity/.NET source assembly mismatch: " + name)
    for path in package.rglob("*"):
        if path.is_symlink():
            raise ValueError("Gameplay sources must be portable ordinary files, not symlinks.")
        if {"bin", "obj"}.intersection(path.relative_to(package).parts) or path.suffix == ".dll":
            raise ValueError("Build output must remain outside the canonical Unity source package.")
    return package


def check(root: Path = RUNTIME) -> dict:
    assets = root / "unity/Assets"
    package = gameplay_sources(root)
    roots = (assets, package)
    guids = set()
    for meta in (path for directory in roots for path in directory.rglob("*.meta")):
        target = meta.with_suffix("")
        if not target.exists():
            raise ValueError("Orphaned metadata: " + str(meta.relative_to(root)))
        matches = re.findall(r"^guid: ([0-9a-f]{32})$", meta.read_text(), re.M)
        if len(matches) != 1 or matches[0] in guids:
            raise ValueError("Missing, invalid or duplicate asset GUID.")
        guids.add(matches[0])
    for asset in (path for directory in roots for path in directory.rglob("*")):
        if not asset.name.endswith(".meta") and not Path(str(asset) + ".meta").is_file():
            raise ValueError("Missing metadata: " + str(asset.relative_to(root)))
    definitions = {}
    for path in (path for directory in roots for path in directory.rglob("*.asmdef")):
        data = json.loads(path.read_text())
        if data["name"] in definitions:
            raise ValueError("Duplicate assembly name.")
        definitions[data["name"]] = data
    for path in (path for directory in roots for path in directory.rglob("*.cs")):
        source_root = assets if path.is_relative_to(assets) else package
        owner = next((p for p in [path.parent, *path.parents] if p.is_relative_to(source_root) and list(p.glob("*.asmdef"))), None)
        if owner is None:
            raise ValueError("Unowned first-party C# file: " + str(path))
    pure = definitions["CriticalShift.ProcessLifetime"]
    if not pure["noEngineReferences"] or pure["references"]:
        raise ValueError("The WP-01 process-lifetime assembly must remain engine-independent.")
    profile = json.loads((root / "toolchain.json").read_text())
    manifest = json.loads((root / "unity/Packages/manifest.json").read_text())
    if manifest["dependencies"]["com.unity.test-framework"] != profile["testFramework"]:
        raise ValueError("Manifest and profile versions differ.")
    version = (root / "unity/ProjectSettings/ProjectVersion.txt").read_text()
    if f'm_EditorVersion: {profile["editor"]}\n' not in version or profile["revision"] not in version:
        raise ValueError("Editor profile differs from ProjectVersion.txt.")
    return {"status": "Passed", "check": "static-source-only", "metadata_guids": len(guids),
            "asmdefs": len(definitions), "csharp_files": sum(len(list(p.rglob("*.cs"))) for p in roots),
            "limits": "Not a resolved Unity graph, native import, gameplay or art review."}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
