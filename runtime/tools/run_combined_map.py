"""Prepare the combined map's collision/anchor export in a disposable Unity project.

This imports no room art or bakes and runs no PlayMode, Player, route, ladder,
visual or performance acceptance. Export provenance remains unreviewed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

from check_source import check
from editor_identity import inspect_editor
from evidence import EvidenceError, validate_log
from run_foundation import RUNTIME, audit_original, checkout_revision, copy_inputs, execute, fingerprint, utc
from package_initialization import audit_first_party_code, first_party_code_fingerprint, audit_package_pins, initialize_packages, package_snapshot

DEFAULT_MAP_SOURCE = RUNTIME.parent / "sections/facility-assembly/combined"
SCENE_PATH = "Assets/CriticalShift/Sandbox/Generated/CombinedMapTraversal.unity"
MAP_INPUTS = (
    "export/compact_map_colliders_anchors.fbx",
    "export/binding_manifest.json",
    "validation/doors.json",
    "validation/colliders.json",
)
STATES = {"open", "closed", "locked"}
ROLES = {"floor", "wall", "roof", "ramp", "ladder", "door_blocker", "door_threshold"}
LIMITS = ("Source declarations and native collision/anchor preparation only; not PlayMode, Player, "
          "route traversal, ladder operation, room art, materials, lighting, feel, multiplayer, FPS or gate acceptance. "
          "The combined-map export is unreviewed and its dirty export revision is provenance, not approval.")


def map_files(root: Path) -> list[Path]:
    """Return only the four declared ordinary inputs, rejecting linked ancestors too."""
    root = root.absolute()
    paths = [root / relative for relative in MAP_INPUTS]
    inspected = {root, *root.parents}
    for path in paths:
        inspected.update((path, path.parent))
    if any(path.is_symlink() or getattr(path, "is_junction", lambda: False)() for path in inspected):
        raise EvidenceError("Combined-map inputs and their directories must not be symlinks or junctions.")
    if not root.is_dir() or any(not path.is_file() for path in paths):
        raise EvidenceError("A required combined-map input is missing or is not an ordinary file.")
    return paths


def map_fingerprint(root: Path) -> str:
    root = root.absolute()
    digest = hashlib.sha256()
    for path in map_files(root):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def audit_copied_map(report: dict, root: Path, expected: str, checkpoint: str, required: bool = True) -> bool:
    evidence = {"status": "Failed", "expected_sha256": expected}
    try:
        evidence["actual_sha256"] = map_fingerprint(root)
        if evidence["actual_sha256"] == expected:
            evidence["status"] = "Passed"
        else:
            evidence["reason"] = "Copied map inputs changed during native preparation."
    except Exception as exception:
        evidence["reason"] = str(exception).replace(str(Path.home()), "<HOME>")
    report.setdefault("copied_map_audits", {})[checkpoint] = evidence
    if required and evidence["status"] != "Passed":
        raise EvidenceError("Copied map audit " + checkpoint + " failed: " + evidence["reason"])
    return evidence["status"] == "Passed"


def _number(value, label: str, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (positive and value <= 0):
        raise EvidenceError("Invalid finite numeric value: " + label)
    return value


def _vector(value, size: int, label: str) -> list:
    if not isinstance(value, list) or len(value) != size:
        raise EvidenceError("Invalid coordinate vector: " + label)
    for number in value:
        _number(number, label)
    return value


def _identity(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError("Missing logical identity: " + label)
    return value


def inspect_map_inputs(root: Path) -> dict:
    root = root.absolute()
    contents = {path.relative_to(root).as_posix(): path.read_bytes() for path in map_files(root)}
    manifest = json.loads(contents[MAP_INPUTS[1]].decode("utf-8-sig"))
    door_table = json.loads(contents[MAP_INPUTS[2]].decode("utf-8-sig"))
    collider_table = json.loads(contents[MAP_INPUTS[3]].decode("utf-8-sig"))
    exported = manifest["export"]
    fbx_sha256 = hashlib.sha256(contents[MAP_INPUTS[0]]).hexdigest()
    if (exported.get("format") != "FBX" or exported.get("file") != Path(MAP_INPUTS[0]).name or
            exported.get("sha256") != fbx_sha256):
        raise EvidenceError("The combined-map FBX identity or SHA256 differs from its binding manifest.")
    provenance = manifest["source"]
    if (provenance.get("scene") != "sections/facility-assembly/combined/combined_map.blend" or
            provenance.get("builder") != "build_compact_map.py" or
            not isinstance(provenance.get("worktree_dirty_at_export"), bool)):
        raise EvidenceError("The export must identify the compact combined map and its dirty/clean source state.")
    _identity(provenance.get("git_revision_at_export"), "export revision")
    doors = door_table["doors"]
    colliders = collider_table["colliders"]
    rooms = manifest["room_placements"]
    if any(not isinstance(rows, list) or not rows for rows in (doors, colliders, rooms)):
        raise EvidenceError("Combined-map door, collider and room placement inventories must be nonempty lists.")
    door_ids, room_ids, collider_names = set(), set(), set()
    for door in doors:
        identity = _identity(door.get("id"), "door")
        if identity in door_ids:
            raise EvidenceError("Duplicate combined-map door identity: " + identity)
        door_ids.add(identity)
        if door.get("state") not in STATES or door.get("evac_state") not in STATES:
            raise EvidenceError("Unknown normal or evacuation door state: " + identity)
        _vector(door.get("plan"), 3, identity + " position")
        outward = _vector(door.get("outward"), 2, identity + " outward")
        if math.hypot(*outward) == 0:
            raise EvidenceError("Door outward direction must not be zero: " + identity)
        _number(door.get("clear_w"), identity + " width", positive=True)
        _number(door.get("clear_h"), identity + " height", positive=True)
    door_roles = Counter()
    role_counts = Counter()
    for collider in colliders:
        name = _identity(collider.get("name"), "collider")
        if name in collider_names:
            raise EvidenceError("Duplicate combined-map collider name: " + name)
        collider_names.add(name)
        role, door_id = collider.get("role"), collider.get("door_id")
        if role not in ROLES or type(collider.get("trigger")) is not bool:
            raise EvidenceError("Unknown collider role or trigger state: " + name)
        if collider["trigger"] != (role in {"ladder", "door_threshold"}):
            raise EvidenceError("Collider trigger state conflicts with its declared role: " + name)
        bounds = collider.get("bounds")
        if not isinstance(bounds, list) or len(bounds) != 2:
            raise EvidenceError("Missing collider bounds: " + name)
        lower, upper = (_vector(value, 3, name + " bounds") for value in bounds)
        if any(low >= high for low, high in zip(lower, upper)):
            raise EvidenceError("Collider bounds must have positive extent: " + name)
        if role in {"door_blocker", "door_threshold"}:
            if door_id not in door_ids:
                raise EvidenceError("Door collider refers to an unknown door: " + name)
            door_roles[(door_id, role)] += 1
        elif door_id is not None:
            raise EvidenceError("A non-door collider unexpectedly claims a door identity: " + name)
        role_counts[role] += 1
    if any(door_roles[(identity, role)] != 1 for identity in door_ids for role in ("door_blocker", "door_threshold")):
        raise EvidenceError("Every door requires exactly one declared blocker and one threshold.")
    summary = collider_table.get("counts")
    if (not isinstance(summary, dict) or any(type(count) is not int for count in summary.values()) or
            summary != dict(role_counts)):
        raise EvidenceError("Collider summary counts differ from the actual role rows.")
    for room in rooms:
        identity = _identity(room.get("room"), "room anchor")
        if identity in room_ids:
            raise EvidenceError("Duplicate room anchor identity: " + identity)
        room_ids.add(identity)
        _vector(room.get("translation"), 3, identity + " translation")
        _number(room.get("rotation_z_deg"), identity + " rotation")
    logical_rooms = manifest["logical_ids"]["rooms"]
    if not isinstance(logical_rooms, list) or len(logical_rooms) != len(room_ids) or set(logical_rooms) != room_ids:
        raise EvidenceError("Logical room catalogue differs from the room placements.")
    return {"doors": len(doors), "colliders": len(colliders), "room_anchors": len(rooms), "fbx_sha256": fbx_sha256,
            "role_counts": dict(role_counts), "export_provenance": provenance, "acceptance": "Unreviewed",
            "files": [{"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                      for relative, data in contents.items()]}


def validate_prepared(text: str, expected: dict, profile: dict) -> dict:
    validate_log(text)
    pattern = (r"^CS_COMBINED_MAP_PREPARED doors=(\d+) colliders=(\d+) room_anchors=(\d+) "
               r"source_sha256=([0-9a-fA-F]{64}) max_anchor_error_metres=(\S+) scene=(\S+)\r?$")
    matches = re.findall(pattern, text, re.M)
    if len(matches) != 1 or text.count("CS_COMBINED_MAP_PREPARED") != 1:
        raise EvidenceError("Expected exactly one complete combined-map preparation marker.")
    doors, colliders, rooms, source_hash, error, scene = matches[0]
    if (tuple(map(int, (doors, colliders, rooms))) != tuple(expected[key] for key in ("doors", "colliders", "room_anchors")) or
            source_hash.lower() != expected["fbx_sha256"] or scene != SCENE_PATH):
        raise EvidenceError("Native prepared inventory, source hash or scene differs from the declared combined-map inputs.")
    try:
        maximum = float(error)
    except ValueError as exception:
        raise EvidenceError("Native combined-map anchor measurement is malformed.") from exception
    if not math.isfinite(maximum) or maximum < 0 or maximum > 0.01:
        raise EvidenceError("Native combined-map anchors exceed the 0.01 metre alignment limit or have an invalid measurement.")
    if profile["editor"] not in text or profile["revision"] not in text:
        raise EvidenceError("Exact native Editor version and revision are missing from the preparation log.")
    return {"doors": int(doors), "colliders": int(colliders), "room_anchors": int(rooms), "source_sha256": source_hash.lower(),
            "max_anchor_error_metres": maximum, "scene": scene}


def run(unity: str | None, output_parent: Path, target: str = "Win64", map_source: Path = DEFAULT_MAP_SOURCE) -> tuple[int, Path]:
    output_parent, map_source = output_parent.resolve(), map_source.absolute()
    if ((output_parent.is_relative_to(RUNTIME.parent) and not output_parent.is_relative_to(RUNTIME / "out")) or
            output_parent.is_relative_to(map_source)):
        raise EvidenceError("Evidence must stay outside source/map directories, under runtime/out when inside the repository.")
    output_parent.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="combined-map-", dir=output_parent))
    phases = {name: {"status": "NotRun"} for name in ("source", "package-initialize", "prepare")}
    report = {"started_utc": utc(), "commit": checkout_revision(RUNTIME), "target": target, "status": "NotRun",
              "phases": phases, "independent_review": "NotRun", "limits": LIMITS}
    original_runtime, original_map = None, None
    work, expected_packages, native_attempted = None, None, False
    expected_code, copied_map = None, None
    current, code = "source", 1
    try:
        profile = json.loads((RUNTIME / "toolchain.json").read_text())
        report["profile"] = profile
        original_runtime = fingerprint(RUNTIME)
        original_map = map_fingerprint(map_source)
        report.update(source_sha256=original_runtime, map_inputs_sha256=original_map)
        expected = inspect_map_inputs(map_source)
        report["map_inputs"] = expected
        phases["source"] = check(RUNTIME)
        current = "prepare"
        editor = Path(unity).expanduser().resolve() if unity else None
        if editor is None or not editor.is_file():
            report["status"] = "Blocked"
            raise EvidenceError("An already activated pinned Unity Editor is required; pass --unity.")
        if target not in ("Win64", "Linux64"):
            raise EvidenceError("Unsupported combined-map preparation target.")
        report["editor_file_identity"] = inspect_editor(editor, profile)
        work, copied_map = output / "workspace/runtime", output / "workspace/map-source"
        report["copied_source_sha256"] = copy_inputs(RUNTIME, work)
        if report["copied_source_sha256"] != original_runtime:
            raise EvidenceError("Disposable Unity inputs differ from the recorded runtime fingerprint; Unity was not launched.")
        report["copied_code_sha256"] = expected_code = first_party_code_fingerprint(work / "unity")
        expected_packages = package_snapshot(work / "unity")
        if (expected_packages["packages"]["com.unity.test-framework"]["version"] != profile["testFramework"] or
                expected_packages["manifest_dependencies"].get("com.unity.test-framework") != profile["testFramework"]):
            raise EvidenceError("Copied Test Framework pins differ from the declared toolchain profile.")
        report["expected_package_pins"] = expected_packages
        for path in map_files(map_source):
            destination = copied_map / path.relative_to(map_source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        report["copied_map_inputs_sha256"] = map_fingerprint(copied_map)
        if report["copied_map_inputs_sha256"] != original_map:
            raise EvidenceError("Disposable map inputs differ from the recorded source fingerprint; Unity was not launched.")
        logs = output / "logs"
        logs.mkdir()
        current = "package-initialize"
        phases[current]["log"] = "logs/package-initialize.log"
        native_attempted = True
        initialize_packages(editor, work / "unity", target, profile, logs / "package-initialize.log", phases[current], execute,
                            report["editor_file_identity"])
        current = "prepare"
        log = logs / "prepare.log"
        phases["prepare"] = {"status": "NotRun", "started_utc": utc(), "log": "logs/prepare.log"}
        command = [str(editor), "-batchmode", "-nographics", "-quit", "-projectPath", str(work / "unity"),
                   "-buildTarget", target, "-forgetProjectPath", "-executeMethod",
                   "CriticalShift.Sandbox.Editor.CombinedMapSceneBuilder.PrepareBatch",
                   "-csCombinedMapSourceRoot", str(copied_map), "-logFile", str(log)]
        native_attempted = True
        rc, text = execute(command, log, 480)
        phases["prepare"].update(exit_code=rc, ended_utc=utc())
        if re.search(r"No valid Unity.*license|No valid license|Failed to activate|License is not active|No Unity Editor license", text, re.I):
            report["status"] = "Blocked"
            raise EvidenceError("The pinned Editor could not obtain a valid license.")
        if rc != 0 or not text:
            raise EvidenceError(f"Combined-map preparation returned {rc} or produced no native log.")
        audit_first_party_code(report, work / "unity", expected_code, "after_prepare")
        audit_copied_map(report, copied_map, original_map, "after_prepare")
        phases["prepare"].update(validate_prepared(text, expected, profile))
        scene = work / "unity" / SCENE_PATH
        if not scene.is_file() or scene.is_symlink() or not scene.resolve().is_relative_to((work / "unity").resolve()):
            raise EvidenceError("The declared prepared scene is missing or outside the disposable project.")
        audit_package_pins(report, work / "unity", expected_packages, "after_prepare")
        report["resolved_packages"] = report["package_pin_audits"]["after_prepare"]
        phases["prepare"]["status"] = report["status"] = "Passed"
        code = 0
    except Exception as exception:
        if phases[current]["status"] == "Blocked":
            report["status"] = "Blocked"
        if report["status"] != "Blocked":
            report["status"] = "Failed"
        phases[current]["status"] = report["status"]
        report.update(error_type=type(exception).__name__, reason=str(exception).replace(str(Path.home()), "<HOME>"))
        code = 2 if report["status"] == "Blocked" else 1
    finally:
        if native_attempted:
            pins_ok = audit_package_pins(report, work / "unity", expected_packages, "final", required=False)
            code_ok = audit_first_party_code(report, work / "unity", expected_code, "final", required=False)
            map_ok = audit_copied_map(report, copied_map, original_map, "final", required=False)
            if not pins_ok or not code_ok or not map_ok:
                report["status"], code = "Failed", 1
                report.setdefault("reason", "Final copied code/map or package audit failed; see copied input/package audits.")
        if native_attempted and "resolved_packages" not in report:
            report["resolved_packages"] = report["package_pin_audits"]["final"]
        if not audit_original(report, RUNTIME, original_runtime):
            code = 1
        report["runtime_source_unchanged"] = report["source_unchanged"]
        report["map_source_unchanged"] = None
        if original_map is not None:
            try:
                report["map_source_unchanged"] = map_fingerprint(map_source) == original_map
                if not report["map_source_unchanged"]:
                    report["map_audit_error"] = "Original combined-map inputs changed during preparation."
            except Exception as exception:
                report["map_audit_error"] = ("Final map source audit failed: " + str(exception)).replace(str(Path.home()), "<HOME>")
            if report["map_source_unchanged"] is not True:
                report["status"], code = "Failed", 1
                report.setdefault("reason", report["map_audit_error"])
        report["ended_utc"] = utc()
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        print("EVIDENCE_DIRECTORY=" + str(output))
    return code, output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unity")
    parser.add_argument("--out", type=Path, default=RUNTIME / "out")
    parser.add_argument("--target", choices=("Win64", "Linux64"), default="Win64")
    parser.add_argument("--map-source", type=Path, default=DEFAULT_MAP_SOURCE)
    arguments = parser.parse_args()
    sys.exit(run(arguments.unity, arguments.out, arguments.target, arguments.map_source)[0])
