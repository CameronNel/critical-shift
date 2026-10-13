"""Validate individually fetched map sources without a bulk repository checkout."""
import hashlib
import json
import posixpath
from pathlib import Path


def verified_snapshot(directory, map_ref):
    if len(map_ref)!=40 or any(c not in "0123456789abcdef" for c in map_ref):
        raise ValueError("Source snapshot requires an exact map commit.")
    directory=Path(directory).resolve()
    config_path=directory/"map-config.json"
    config=json.loads(config_path.read_text())
    receipt=json.loads((directory/"build-receipt.json").read_text())
    if receipt["status"]!="CurrentCompact13SourceDerivativeBuilt_NotUnityAccepted":
        raise ValueError("Source snapshot is not a completed compact-map build.")
    if config["map_commit"]!=map_ref or receipt["mapCommit"]!=map_ref:
        raise ValueError("Source snapshot belongs to a different map revision.")
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(config_path)!=receipt["configSha256"] or sha(directory/"combined-runtime-source.blend")!=receipt["sourceSha256"]:
        raise ValueError("Source snapshot or layout configuration changed after its build.")
    records=config["sources"]
    if records!=receipt["sourceRecords"] or len({r["path"] for r in records})!=len(records):
        raise ValueError("Source snapshot inventory differs from its build receipt.")
    required={config["assembly_builder"],*config["assembly_dependencies"]}
    if not required.issubset({r["path"] for r in records}):
        raise ValueError("Source snapshot is missing an assembly dependency.")
    rooms=config["rooms"]
    names=[r[0] for r in rooms]
    if not names or len(set(names))!=len(names) or names!=receipt["rooms"]:
        raise ValueError("Source snapshot room inventory differs from its build receipt.")
    libraries={posixpath.normpath("sections/facility-assembly/sources/"+r[1]) for r in rooms}
    libraries.update(posixpath.normpath("sections/facility-assembly/exteriors/"+r[0])
        for r in config["exterior_skins"].values())
    if any(p.startswith("../") or p.startswith("/") for p in libraries) or not libraries.issubset({r["path"] for r in records}):
        raise ValueError("Source snapshot is missing a room or exterior library.")
    for r in records:
        p=directory/"map"/r["path"]
        if Path(r["path"]).is_absolute() or ".." in Path(r["path"]).parts:
            raise ValueError("Invalid source snapshot path.")
        b=p.read_bytes()
        if sha(p)!=r["sha256"] or len(b)!=r["bytes"]:
            raise ValueError("Source snapshot input changed: "+r["path"])
        git_blob=lambda data:hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        pointer=("version https://git-lfs.github.com/spec/v1\noid sha256:"+r["sha256"]+"\nsize "+str(len(b))+"\n").encode()
        if r["gitBlobSha"] not in {git_blob(b),git_blob(pointer)}:
            raise ValueError("Source input does not match its pinned Git blob: "+r["path"])
        turbine=r["path"]=="sections/facility-assembly/sources/turbine-room/module_overhaul_R1.blend"
        expected=config["turbine_commit"] if turbine else map_ref
        if r["source_commit"]!=expected:
            raise ValueError("Source input belongs to an unexpected revision: "+r["path"])
    if receipt["missingExternalImages"]:
        raise ValueError("Source snapshot has missing external textures.")
    return directory,config
