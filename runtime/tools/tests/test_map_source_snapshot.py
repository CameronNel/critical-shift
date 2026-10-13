"""Immutable layout/dependency pins must reject stale individually fetched snapshots."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from map_source_snapshot import verified_snapshot

COMMIT="a"*40
TURBINE="b"*40
BASE="sections/facility-assembly/combined/"
TURBINE_PATH="sections/facility-assembly/sources/turbine-room/module_overhaul_R1.blend"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def fixture(root):
    records=[]
    for path in [BASE+"build_compact_map.py",BASE+"build_combined_map.py",BASE+"reactor_links.py",TURBINE_PATH]:
        p=root/"map"/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(path.encode())
        b=p.read_bytes()
        records.append(dict(path=path,source_commit=TURBINE if path==TURBINE_PATH else COMMIT,
            sha256=sha(p),bytes=len(b),gitBlobSha=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()))
    (root/"combined-runtime-source.blend").write_bytes(b"snapshot guard fixture only")
    config=dict(map_commit=COMMIT,turbine_commit=TURBINE,sources=records,
        assembly_builder=BASE+"build_compact_map.py",assembly_dependencies=[BASE+"build_combined_map.py",BASE+"reactor_links.py"],
        rooms=[["turbine-room","turbine-room/module_overhaul_R1.blend"]],exterior_skins={})
    seal(root,config)
    return config


def seal(root,config):
    (root/"map-config.json").write_text(json.dumps(config))
    (root/"build-receipt.json").write_text(json.dumps(dict(
        status="CurrentCompact13SourceDerivativeBuilt_NotUnityAccepted",mapCommit=COMMIT,
        sourceRecords=config["sources"],configSha256=sha(root/"map-config.json"),
        sourceSha256=sha(root/"combined-runtime-source.blend"),rooms=[r[0] for r in config["rooms"]],missingExternalImages=[])))


class MapSnapshotGuardTests(unittest.TestCase):
    def test_valid_pinned_external_turbine_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            self.assertEqual(verified_snapshot(root,COMMIT)[1]["turbine_commit"],TURBINE)

    def test_changed_snapshot_or_dependency_rejects(self):
        for name in ["combined-runtime-source.blend","map/"+BASE+"reactor_links.py"]:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                root=Path(d);fixture(root);(root/name).write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError,"changed"):
                    verified_snapshot(root,COMMIT)

    def test_missing_compact_dependency_rejects_even_with_consistent_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);config=fixture(root);config["sources"]=config["sources"][:-2]+config["sources"][-1:];seal(root,config)
            with self.assertRaisesRegex(ValueError,"missing an assembly dependency"):
                verified_snapshot(root,COMMIT)

    def test_wrong_external_revision_or_blob_rejects(self):
        for key,value in [("source_commit","c"*40),("gitBlobSha","0"*40)]:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                root=Path(d);config=fixture(root);config["sources"][-1][key]=value;seal(root,config)
                with self.assertRaises(ValueError):verified_snapshot(root,COMMIT)

    def test_wrong_map_revision_rejects(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            with self.assertRaisesRegex(ValueError,"different map revision"):
                verified_snapshot(root,"c"*40)

    def test_missing_room_or_exterior_library_rejects(self):
        for field,value in [("rooms",[["missing","missing/module.blend"]]),
                            ("exterior_skins",{"turbine-room":["missing/exterior.blend","EXTERIOR"]})]:
            with self.subTest(field=field),tempfile.TemporaryDirectory() as d:
                root=Path(d);config=fixture(root);config[field]=value;seal(root,config)
                with self.assertRaisesRegex(ValueError,"room or exterior library"):
                    verified_snapshot(root,COMMIT)

    def test_duplicate_room_names_reject(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);config=fixture(root);config["rooms"]*=2;seal(root,config)
            with self.assertRaisesRegex(ValueError,"room inventory"):
                verified_snapshot(root,COMMIT)
