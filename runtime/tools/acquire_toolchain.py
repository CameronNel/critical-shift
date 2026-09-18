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


def download(url, destination):
    with urllib.request.urlopen(url, timeout=120) as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target, 1024 * 1024)


def digest(path, algorithm):
    result = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(data)
    return result


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
    nunit = root / "nunit"
    nunit.mkdir(exist_ok=True)
    with urllib.request.urlopen("https://packages.unity.com/com.unity.ext.nunit", timeout=60) as response:
        metadata = json.load(response)["versions"]["2.0.3"]
    nunit_archive = root / "nunit.tgz"
    download(metadata["dist"]["tarball"], nunit_archive)
    if digest(nunit_archive, "sha1").hexdigest() != metadata["dist"]["shasum"]:
        raise ValueError("Unity NUnit package integrity mismatch.")
    with tarfile.open(nunit_archive) as package:
        package.extractall(nunit, filter="data")
    record["nunit"] = {"package": "com.unity.ext.nunit", "version": "2.0.3", "dist": metadata["dist"],
                       "sha256": digest(nunit_archive, "sha256").hexdigest()}
    nunit_archive.unlink()
    matches = sorted(nunit.rglob("nunit.framework.dll"))
    if len(matches) != 1:
        raise ValueError("Expected exactly one official NUnit framework DLL.")
    record["editor_binary_exists"] = (root / "Editor/Unity").is_file()
    (evidence / "toolchain-download.json").write_text(json.dumps(record, indent=2) + "\n")
    print("EDITOR=" + str(root / "Editor/Unity"))
    print("NUNIT=" + str(matches[0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    acquire(args.root.resolve(), args.evidence.resolve())
