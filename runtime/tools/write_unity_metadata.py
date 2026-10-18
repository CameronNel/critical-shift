"""Write missing deterministic first-party source metadata; never launch an editor or replace existing GUIDs."""
import argparse
import uuid
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1]
NAMESPACE = uuid.UUID("c530ffb9-637a-4f5e-840f-c053424e13aa")


def write_metadata(directory: Path) -> int:
    directory = directory.resolve()
    package = RUNTIME / "dotnet/src"
    assets = RUNTIME / "unity/Assets/CriticalShift"
    if not (directory.is_relative_to(package) or directory.is_relative_to(assets)):
        raise ValueError("Only the canonical package and first-party Unity source roots are supported.")
    candidates = sorted(directory.rglob("*"))
    if directory != package:
        candidates.append(directory)
    if directory.is_relative_to(assets):
        candidates.extend(parent for parent in directory.parents if parent.is_relative_to(assets))
    count = 0
    for path in sorted(set(candidates)):
        if path.is_symlink():
            raise ValueError("Source metadata generation does not follow symlinks.")
        if path.suffix == ".meta" or {"bin", "obj", "Generated", "Rooms"}.intersection(path.relative_to(RUNTIME).parts):
            continue
        meta = Path(str(path) + ".meta")
        if meta.exists():
            continue
        identity = uuid.uuid5(NAMESPACE, path.relative_to(RUNTIME).as_posix()).hex
        text = "fileFormatVersion: 2\nguid: " + identity + "\n"
        if path.is_dir():
            text += "folderAsset: yes\nDefaultImporter:\n"
        elif path.suffix == ".cs":
            text += "MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n"
        elif path.suffix == ".asmdef":
            text += "AssemblyDefinitionImporter:\n"
        elif path.suffix in (".md", ".json", ".txt"):
            text += "TextScriptImporter:\n"
        else:
            text += "DefaultImporter:\n"
        if path.suffix != ".cs":
            text += "  externalObjects: {}\n"
        text += "  userData:\n  assetBundleName:\n  assetBundleVariant:\n"
        meta.write_text(text, encoding="utf-8", newline="\n")
        count += 1
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    print("Wrote", sum(write_metadata(path) for path in args.roots), "missing source metadata files; no editor launched.")
