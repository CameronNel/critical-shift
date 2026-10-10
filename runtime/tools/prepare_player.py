"""Build canonical application/domain DLLs for the local Unity player fixture.

Generated imports are ignored; do not copy runtime implementations into Unity.
Run before opening the Unity project, and rerun after changing canonical C#.
"""
import hashlib
import json
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "dotnet"
IMPORT = ROOT / "unity/Assets/CriticalShift/RuntimeLibraries"
NAMES = ["CriticalShift.Application"] + ["CriticalShift.Features." + name + ".Domain" for name in
    ("Interaction", "Session", "Workers", "Materials", "Production", "Reactor", "Power")]


def source_fingerprint():
    source = sorted(p for p in (PROJECT / "src").rglob("*")
                    if p.is_file() and p.suffix in (".cs", ".csproj") and "obj" not in p.parts and "bin" not in p.parts)
    source += [PROJECT / "Directory.Build.props", PROJECT / "global.json"]
    return hashlib.sha256(b"".join(p.relative_to(PROJECT).as_posix().encode() + b"\0" + p.read_bytes()
                                  for p in source)).hexdigest()


def meta(path, plugin=False):
    guid = uuid.uuid5(uuid.NAMESPACE_URL, "critical-shift:" + path.relative_to(ROOT).as_posix()).hex
    text = "fileFormatVersion: 2\nguid: " + guid + "\n"
    if path.is_dir():
        text += "folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    elif plugin:
        text += """PluginImporter:
  externalObjects: {}
  serializedVersion: 2
  iconMap: {}
  executionOrder: {}
  defineConstraints: []
  isPreloaded: 0
  isOverridable: 0
  isExplicitlyReferenced: 1
  validateReferences: 1
  platformData:
  - first:
      Any:
    second:
      enabled: 1
      settings: {}
  userData:
  assetBundleName:
  assetBundleVariant:
"""
    else:
        text += "DefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    Path(str(path) + ".meta").write_text(text)


def prepare():
    subprocess.run(["dotnet", "build", "src/CriticalShift.Application", "-c", "Release"], cwd=PROJECT, check=True)
    IMPORT.mkdir(parents=True, exist_ok=True)
    meta(IMPORT)
    records = []
    for name in NAMES:
        original = PROJECT / "src" / name / "bin/Release/netstandard2.1" / (name + ".dll")
        destination = IMPORT / original.name
        destination.write_bytes(original.read_bytes()); meta(destination, plugin=True)
        records.append({"assembly": name, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
    records.append({"canonical_source_sha256": source_fingerprint()})
    manifest = IMPORT / "imports.json"; manifest.write_text(json.dumps(records, indent=2) + "\n"); meta(manifest)
    print("Prepared eight canonical DLL imports. Native Unity import has not run.")


if __name__ == "__main__":
    prepare()
