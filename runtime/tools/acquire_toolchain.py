"""Fetch pinned official public toolchain inputs. Does not activate Unity."""
import argparse
import base64
import hashlib
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

VERSION = "6000.4.3f1"
REVISION = "39d1a88d4dd1"
EDITOR_BYTES = 4140156068
EDITOR_MD5 = "VDyS6NleQ2P1BmgnQgh+uQ=="
EDITOR_URL = f"https://download.unity3d.com/download_unity/{REVISION}/LinuxEditorInstaller/Unity-{VERSION}.tar.xz"
RUNTIME = Path(__file__).resolve().parents[1]


def download(url, destination):
    with urllib.request.urlopen(url, timeout=120) as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target, 1024 * 1024)


def digest(path, algorithm):
    result = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(data)
    return result


def bundled_nunit(editor: Path, lock: Path) -> tuple[Path, dict]:
    """Select the acquired Editor's actual NUnit bundle; never fetch a different registry version."""
    selected = json.loads(lock.read_text())["dependencies"]["com.unity.ext.nunit"]
    expected = selected["version"]
    if selected.get("source") != "builtin" or not isinstance(expected, str) or not expected:
        raise ValueError("The selected NUnit reference must be pinned to the Editor's built-in package in packages-lock.json.")
    package = editor / "Editor/Data/Resources/PackageManager/BuiltInPackages/com.unity.ext.nunit"
    descriptor = package / "package.json"
    if not descriptor.is_file():
        raise ValueError("The pinned Editor's bundled NUnit descriptor is missing; no registry fallback is permitted.")
    metadata = json.loads(descriptor.read_text(encoding="utf-8-sig"))
    if metadata.get("name") != "com.unity.ext.nunit" or metadata.get("version") != expected:
        raise ValueError("The acquired Editor's bundled NUnit package differs from the selected project lock.")
    matches = sorted(package.rglob("nunit.framework.dll"))
    if len(matches) != 1:
        raise ValueError("Expected exactly one real NUnit framework DLL in the pinned Editor's bundled package.")
    binary = matches[0]
    return binary, {"package": "com.unity.ext.nunit", "version": expected, "source": "pinned-editor-builtin",
                    "lock_sha256": digest(lock, "sha256").hexdigest(),
                    "descriptor": descriptor.relative_to(editor).as_posix(), "descriptor_sha256": digest(descriptor, "sha256").hexdigest(),
                    "dll": binary.relative_to(editor).as_posix(), "dll_bytes": binary.stat().st_size,
                    "dll_sha256": digest(binary, "sha256").hexdigest()}


def acquire(root: Path, evidence: Path):
    root.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    archive = root / "editor.tar.xz"
    marker = root / "official-editor.json"
    if not marker.exists() or not (root / "Editor/Unity").is_file():
        download(EDITOR_URL, archive)
        if archive.stat().st_size != EDITOR_BYTES or base64.b64encode(digest(archive, "md5").digest()).decode() != EDITOR_MD5:
            raise ValueError("Official Editor archive length/integrity mismatch.")
        record = {"version": VERSION, "revision": REVISION, "url": EDITOR_URL,
                  "bytes": archive.stat().st_size, "official_md5_base64": EDITOR_MD5,
                  "sha256": digest(archive, "sha256").hexdigest()}
        with tarfile.open(archive) as package:
            package.extractall(root, filter="data")
        marker.write_text(json.dumps(record, indent=2) + "\n")
        archive.unlink()
    record = json.loads(marker.read_text())
    if record["version"] != VERSION or record["revision"] != REVISION:
        raise ValueError("Cached editor does not match the selected profile.")
    nunit, record["nunit"] = bundled_nunit(root, RUNTIME / "unity/Packages/packages-lock.json")
    record["editor_binary_exists"] = (root / "Editor/Unity").is_file()
    (evidence / "toolchain-download.json").write_text(json.dumps(record, indent=2) + "\n")
    print("EDITOR=" + str(root / "Editor/Unity"))
    print("NUNIT=" + str(nunit))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    acquire(args.root.resolve(), args.evidence.resolve())
