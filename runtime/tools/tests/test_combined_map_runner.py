"""Combined-map input and native-runner fault fixtures. Native execution is always mocked."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_combined_map as runner
from evidence import EvidenceError


class CombinedMapRunnerTests(unittest.TestCase):
    profile = {"editor": "6000.4.3f1", "revision": "39d1a88d4dd1", "testFramework": "1.6.0"}

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.runtime = self.base / "repository/runtime"
        self.map = self.base / "map-source"
        for directory in ("unity/Assets", "unity/Packages", "unity/ProjectSettings", "dotnet/src"):
            (self.runtime / directory).mkdir(parents=True)
        (self.runtime / "toolchain.json").write_text(json.dumps(self.profile))
        (self.runtime / "dotnet/src/package.json").write_text('{"name":"com.criticalshift.gameplay"}')
        (self.runtime / "unity/Assets/Subject.cs").write_text("// source fixture")
        manifest = {"dependencies": {"com.unity.test-framework": "1.6.0", "com.criticalshift.gameplay": "file:../../dotnet/src"}}
        lock = {"dependencies": {"com.unity.test-framework": {"version": "1.6.0", "source": "builtin"},
                                  "com.unity.ext.nunit": {"version": "2.0.5", "source": "builtin"},
                                  "com.criticalshift.gameplay": {"version": "file:../../dotnet/src", "source": "local"}}}
        (self.runtime / "unity/Packages/manifest.json").write_text(json.dumps(manifest))
        (self.runtime / "unity/Packages/packages-lock.json").write_text(json.dumps(lock))
        self.editor = self.base / "Unity.exe"
        self.editor.write_bytes(b"not executable; native invocation is mocked")
        for directory in ("export", "validation"):
            (self.map / directory).mkdir(parents=True)
        self.fbx = b"FBX identity fixture, not an importable model"
        (self.map / runner.MAP_INPUTS[0]).write_bytes(self.fbx)
        self.manifest = {
            "source": {"scene": "sections/facility-assembly/combined/combined_map.blend", "builder": "build_compact_map.py",
                       "git_revision_at_export": "a" * 40, "worktree_dirty_at_export": True},
            "export": {"format": "FBX", "file": "compact_map_colliders_anchors.fbx", "sha256": hashlib.sha256(self.fbx).hexdigest()},
            "room_placements": [{"room": "test-room", "translation": [1, 2, 0], "rotation_z_deg": 90}],
            "logical_ids": {"rooms": ["test-room"]},
        }
        self.doors = {"doors": [{"id": "TEST_DOOR", "state": "closed", "evac_state": "open", "plan": [0, 0, 0],
                                  "outward": [0, 1], "clear_w": 1.4, "clear_h": 2.4}]}
        self.colliders = {"counts": {"door_blocker": 1, "door_threshold": 1}, "colliders": [
            {"name": "COL TEST_DOOR blocker", "role": "door_blocker", "door_id": "TEST_DOOR", "trigger": False,
             "bounds": [[-1, -0.1, 0], [1, 0.1, 2.4]]},
            {"name": "COL TEST_DOOR threshold", "role": "door_threshold", "door_id": "TEST_DOOR", "trigger": True,
             "bounds": [[-1, -0.3, 0], [1, 0.3, 2.4]]},
        ]}
        self.save()

    def save(self):
        for relative, data in zip(runner.MAP_INPUTS[1:], (self.manifest, self.doors, self.colliders)):
            (self.map / relative).write_text(json.dumps(data))

    def marker(self, **changes):
        values = {"doors": 1, "colliders": 2, "room_anchors": 1, "source_sha256": self.manifest["export"]["sha256"],
                  "max_anchor_error_metres": "0.001", "scene": runner.SCENE_PATH}
        values.update(changes)
        return ("Initialize engine version: 6000.4.3f1 (39d1a88d4dd1)\nCS_COMBINED_MAP_PREPARED " +
                " ".join(key + "=" + str(value) for key, value in values.items()) + "\n")

    def invoke(self, native=None, editor=None):
        with ExitStack() as stack:
            stack.enter_context(patch.object(runner, "RUNTIME", self.runtime))
            stack.enter_context(patch.object(runner, "checkout_revision", return_value="b" * 40))
            stack.enter_context(patch.object(runner, "inspect_editor", return_value={"status": "Verified"}))
            stack.enter_context(patch.object(runner, "check", return_value={"status": "Passed", "check": "mocked-source"}))
            def execute(command, log, timeout):
                if "-executeMethod" not in command:
                    project = Path(command[command.index("-projectPath") + 1])
                    for name, version in (("com.unity.test-framework", "1.6.0"), ("com.unity.ext.nunit", "2.0.5")):
                        descriptor = project / "Library/PackageCache" / (name + "@fixture") / "package.json"
                        descriptor.parent.mkdir(parents=True, exist_ok=True)
                        data = {"name": name, "version": version}
                        if name == "com.unity.test-framework":
                            data["dependencies"] = {"com.unity.ext.nunit": "2.0.3"}
                        descriptor.write_text(json.dumps(data))
                    text = "Built from 'fixture'; Version is '6000.4.3f1 (39d1a88d4dd1)'\n"
                    log.write_text(text)
                    return 0, text
                return (native or self.prepare)(command, log, timeout)

            execution = stack.enter_context(patch.object(runner, "execute", side_effect=execute))
            code, output = runner.run(str(self.editor) if editor is None else editor, self.base / "evidence", "Win64", self.map)
            return code, output, json.loads((output / "report.json").read_text()), execution

    def prepare(self, command, log, timeout):
        project = Path(command[command.index("-projectPath") + 1])
        scene = project / runner.SCENE_PATH
        scene.parent.mkdir(parents=True)
        scene.write_text("%YAML mocked generated scene")
        for name, version in (("com.unity.test-framework", "1.6.0"), ("com.unity.ext.nunit", "2.0.5")):
            descriptor = project / "Library/PackageCache" / (name + "@fixture") / "package.json"
            descriptor.parent.mkdir(parents=True, exist_ok=True)
            data = {"name": name, "version": version}
            if name == "com.unity.test-framework":
                data["dependencies"] = {"com.unity.ext.nunit": "2.0.3"}  # Vendor requirement differs from selected bundled pin.
            descriptor.write_text(json.dumps(data))
        text = self.marker()
        log.write_text(text)
        return 0, text

    def test_native_prepare_cannot_rewrite_initialized_package_descriptor_content(self):
        def mutate(command, log, timeout):
            result = self.prepare(command, log, timeout)
            project = Path(command[command.index("-projectPath") + 1])
            path = project / "Library/PackageCache/com.unity.ext.nunit@fixture/package.json"
            data = json.loads(path.read_text()); data["dependencies"] = {"com.unity.unexpected": "9.9.9"}
            path.write_text(json.dumps(data))
            return result
        code, _, report, _ = self.invoke(native=mutate)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertFalse(report["package_pin_audits"]["after_prepare"]["descriptor_hashes_match_initialization"])
        self.assertEqual(report["package_pin_audits"]["final"]["status"], "Failed")

    def test_native_prepare_cannot_rewrite_copied_runtime_or_map_inputs(self):
        for relative in ("code", *runner.MAP_INPUTS):
            with self.subTest(input=relative):
                def mutate(command, log, timeout):
                    result = self.prepare(command, log, timeout)
                    project = Path(command[command.index("-projectPath") + 1])
                    copied_map = Path(command[command.index("-csCombinedMapSourceRoot") + 1])
                    path = project / "Assets/Subject.cs" if relative == "code" else copied_map / relative
                    path.write_bytes(path.read_bytes() + b"\nchanged after copy")
                    return result
                code, _, report, _ = self.invoke(native=mutate)
                self.assertEqual((code, report["status"]), (1, "Failed"))
                audit = "copied_code_audits" if relative == "code" else "copied_map_audits"
                self.assertEqual(report[audit]["final"]["status"], "Failed")
                self.assertTrue(report["map_source_unchanged"])
                self.assertTrue(report["runtime_source_unchanged"])

    def test_preparation_copies_only_declared_inputs_and_derives_its_inventory(self):
        (self.map / "combined_map.blend").write_bytes(b"must not be copied")
        (self.map / "export/extra-art.fbx").write_bytes(b"must not be copied")
        code, output, report, execution = self.invoke()
        self.assertEqual((code, report["status"]), (0, "Passed"))
        self.assertEqual((report["map_inputs"]["doors"], report["map_inputs"]["colliders"], report["map_inputs"]["room_anchors"]), (1, 2, 1))
        copied = output / "workspace/map-source"
        self.assertEqual({path.relative_to(copied).as_posix() for path in copied.rglob("*") if path.is_file()}, set(runner.MAP_INPUTS))
        self.assertEqual(report["map_inputs_sha256"], report["copied_map_inputs_sha256"])
        self.assertEqual(report["source_sha256"], report["copied_source_sha256"])
        self.assertTrue(report["runtime_source_unchanged"])
        self.assertTrue(report["map_source_unchanged"])
        self.assertTrue(report["map_inputs"]["export_provenance"]["worktree_dirty_at_export"])
        self.assertEqual(report["map_inputs"]["acceptance"], "Unreviewed")
        command = execution.call_args.args[0]
        self.assertEqual(command[command.index("-csCombinedMapSourceRoot") + 1], str(copied))
        for flag in ("-batchmode", "-nographics", "-quit"):
            self.assertIn(flag, command)
        self.assertNotIn("-runTests", command)
        self.assertEqual(execution.call_count, 2)
        self.assertEqual(report["resolved_packages"]["status"], "Passed")
        self.assertEqual(report["resolved_packages"]["packages"]["com.unity.ext.nunit"]["version"], "2.0.5")

    def test_mismatched_fbx_hash_cannot_reach_native_execution(self):
        (self.map / runner.MAP_INPUTS[0]).write_bytes(b"changed model")
        code, _, report, execution = self.invoke()
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertIn("SHA256", report["reason"])
        execution.assert_not_called()

    def test_duplicate_door_and_missing_threshold_are_rejected(self):
        self.doors["doors"].append(copy.deepcopy(self.doors["doors"][0]))
        self.save()
        with self.assertRaisesRegex(EvidenceError, "Duplicate.*door"):
            runner.inspect_map_inputs(self.map)
        self.doors["doors"].pop()
        self.colliders["colliders"].pop()
        self.colliders["counts"].pop("door_threshold")
        self.save()
        with self.assertRaisesRegex(EvidenceError, "exactly one"):
            runner.inspect_map_inputs(self.map)

    def test_invalid_door_state_and_nonfinite_coordinates_are_rejected(self):
        door = self.doors["doors"][0]
        for key, invalid in (("state", "unlocked"), ("evac_state", "unknown"), ("plan", [0, float("nan"), 0]),
                             ("clear_h", 0), ("clear_w", True), ("outward", [0, 0])):
            with self.subTest(field=key):
                valid = door[key]
                door[key] = invalid
                self.save()
                with self.assertRaises(EvidenceError):
                    runner.inspect_map_inputs(self.map)
                door[key] = valid

    def test_duplicate_unknown_and_degenerate_collider_rows_are_rejected(self):
        baseline = copy.deepcopy(self.colliders)
        for change in (lambda rows: rows.append(copy.deepcopy(rows[0])),
                       lambda rows: rows[0].update(door_id="OTHER_DOOR"),
                       lambda rows: rows[0].update(trigger=True),
                       lambda rows: rows[0].update(bounds=[[0, 0, 0], [0, 1, 1]])):
            self.colliders = copy.deepcopy(baseline)
            change(self.colliders["colliders"])
            self.save()
            with self.assertRaises(EvidenceError):
                runner.inspect_map_inputs(self.map)

    def test_summary_counts_and_room_catalogue_cannot_replace_actual_rows(self):
        self.colliders["counts"]["door_blocker"] = True
        self.save()
        with self.assertRaisesRegex(EvidenceError, "summary counts"):
            runner.inspect_map_inputs(self.map)
        self.colliders["counts"]["door_blocker"] = 1
        self.manifest["logical_ids"]["rooms"] = ["other-room"]
        self.save()
        with self.assertRaisesRegex(EvidenceError, "room catalogue"):
            runner.inspect_map_inputs(self.map)

    def test_retiring_map_provenance_and_duplicate_room_anchors_are_rejected(self):
        self.manifest["source"]["scene"] = "sections/facility-assembly/blender/facility_environment.blend"
        self.save()
        with self.assertRaisesRegex(EvidenceError, "compact combined map"):
            runner.inspect_map_inputs(self.map)
        self.manifest["source"]["scene"] = "sections/facility-assembly/combined/combined_map.blend"
        self.manifest["room_placements"].append(copy.deepcopy(self.manifest["room_placements"][0]))
        self.save()
        with self.assertRaisesRegex(EvidenceError, "Duplicate room"):
            runner.inspect_map_inputs(self.map)

    def test_linked_input_and_junction_directories_are_rejected_without_os_privileges(self):
        manifest = self.map / runner.MAP_INPUTS[1]
        with patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == manifest):
            with self.assertRaisesRegex(EvidenceError, "symlinks or junctions"):
                runner.map_files(self.map)
        with patch.object(Path, "is_junction", create=True, side_effect=lambda: True):
            with self.assertRaisesRegex(EvidenceError, "symlinks or junctions"):
                runner.map_files(self.map)

    def test_good_marker_cannot_pass_without_the_generated_scene(self):
        def without_scene(command, log, timeout):
            text = self.marker()
            log.write_text(text)
            return 0, text

        code, output, report, _ = self.invoke(without_scene)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertIn("scene is missing", report["reason"])
        self.assertTrue((output / "logs/prepare.log").is_file())

    def test_wrong_inventory_hash_path_and_anchor_error_markers_are_rejected(self):
        expected = runner.inspect_map_inputs(self.map)
        for changes in ({"doors": 2}, {"colliders": 1}, {"room_anchors": 0}, {"source_sha256": "0" * 64},
                        {"scene": "../outside.unity"}, {"max_anchor_error_metres": "0.0101"},
                        {"max_anchor_error_metres": "nan"}, {"max_anchor_error_metres": "inf"},
                        {"max_anchor_error_metres": "-0.1"}, {"max_anchor_error_metres": "missing"}):
            with self.subTest(changes=changes), self.assertRaises(EvidenceError):
                runner.validate_prepared(self.marker(**changes), expected, self.profile)
        self.assertEqual(runner.validate_prepared(self.marker(max_anchor_error_metres="0.01"), expected, self.profile)["max_anchor_error_metres"], 0.01)

    def test_duplicate_or_malformed_markers_and_wrong_editor_are_rejected(self):
        expected = runner.inspect_map_inputs(self.map)
        for text in (self.marker() + self.marker(), self.marker() + "CS_COMBINED_MAP_PREPARED malformed\n",
                     self.marker().replace("39d1a88d4dd1", "wrong-revision")):
            with self.assertRaises(EvidenceError):
                runner.validate_prepared(text, expected, self.profile)

    def test_changed_disposable_map_copy_cannot_launch_unity(self):
        original_copy = shutil.copy2

        def changed_copy(source, destination):
            result = original_copy(source, destination)
            if source == self.map / runner.MAP_INPUTS[0]:
                destination.write_bytes(b"changed disposable FBX")
            return result

        with patch.object(runner.shutil, "copy2", side_effect=changed_copy):
            code, _, report, execution = self.invoke()
        self.assertEqual((code, report["status"], report["map_source_unchanged"]), (1, "Failed", True))
        self.assertIn("Disposable map inputs differ", report["reason"])
        execution.assert_not_called()

    def test_map_mutation_during_native_preparation_invalidates_its_good_marker(self):
        def mutate(command, log, timeout):
            result = self.prepare(command, log, timeout)
            (self.map / runner.MAP_INPUTS[0]).write_bytes(b"concurrent source change")
            return result

        code, _, report, _ = self.invoke(mutate)
        self.assertEqual((code, report["status"], report["map_source_unchanged"]), (1, "Failed", False))
        self.assertEqual(report["phases"]["prepare"]["status"], "Passed")

    def test_native_failure_is_preserved_when_final_map_audit_also_fails(self):
        def fail(command, log, timeout):
            (self.map / runner.MAP_INPUTS[0]).unlink()
            log.write_text("First native failure retained")
            return 7, "First native failure retained"

        code, output, report, _ = self.invoke(fail)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertIn("returned 7", report["reason"])
        self.assertIn("Final map source audit failed", report["map_audit_error"])
        self.assertIsNone(report["map_source_unchanged"])
        self.assertEqual((output / "logs/prepare.log").read_text(), "First native failure retained")

    def test_prepare_license_failure_stops_after_the_completed_initialization(self):
        def blocked(command, log, timeout):
            log.write_text("No valid Unity Editor license")
            return 1, "No valid Unity Editor license"

        code, _, report, execution = self.invoke(blocked)
        self.assertEqual((code, report["status"]), (2, "Blocked"))
        self.assertEqual(execution.call_count, 2)
        self.assertEqual(set(report["phases"]), {"source", "package-initialize", "prepare"})
        self.assertEqual(report["phases"]["package-initialize"]["status"], "Completed")

    def test_missing_input_still_produces_a_failed_report_without_native_execution(self):
        (self.map / runner.MAP_INPUTS[2]).unlink()
        code, _, report, execution = self.invoke()
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertIsNone(report["map_source_unchanged"])
        execution.assert_not_called()

    def test_native_package_override_blocks_an_otherwise_valid_preparation(self):
        def override(command, log, timeout):
            result = self.prepare(command, log, timeout)
            project = Path(command[command.index("-projectPath") + 1])
            path = project / "Packages/packages-lock.json"
            data = json.loads(path.read_text())
            data["dependencies"]["com.unity.test-framework"]["version"] = "1.7.0"
            path.write_text(json.dumps(data))
            return result

        code, output, report, _ = self.invoke(override)
        self.assertEqual((code, report["status"], report["runtime_source_unchanged"]), (1, "Failed", True))
        self.assertEqual(report["resolved_packages"]["status"], "Failed")
        self.assertEqual(report["resolved_packages"]["packages"]["com.unity.test-framework"]["version"], "1.7.0")
        self.assertIn("versions or sources differ", report["reason"])
        self.assertTrue((output / "logs/prepare.log").is_file())

    def test_resolved_package_evidence_is_retained_after_native_failure(self):
        def failed(command, log, timeout):
            self.prepare(command, log, timeout)
            project = Path(command[command.index("-projectPath") + 1])
            descriptor = project / "Library/PackageCache/com.unity.test-framework@fixture/package.json"
            descriptor.write_text(json.dumps({"name": "com.unity.test-framework", "version": "1.4.6"}))
            log.write_text("Original preparation failure")
            return 1, "Original preparation failure"

        code, _, report, _ = self.invoke(failed)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertIn("returned 1", report["reason"])
        evidence = report["resolved_packages"]
        self.assertEqual(evidence["status"], "Failed")
        self.assertEqual(evidence["cached_descriptors"]["com.unity.test-framework"][0]["version"], "1.4.6")

    def test_missing_native_package_cache_cannot_appear_as_verified_resolution(self):
        def missing(command, log, timeout):
            result = self.prepare(command, log, timeout)
            project = Path(command[command.index("-projectPath") + 1])
            for descriptor in (project / "Library/PackageCache").glob("*/package.json"):
                descriptor.unlink()
            return result

        code, _, report, _ = self.invoke(missing)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertEqual(report["resolved_packages"]["status"], "NotRun")
        self.assertIn("no cached descriptor evidence", report["reason"])

    def test_package_source_drift_is_rejected_even_when_its_version_matches(self):
        def source_drift(command, log, timeout):
            result = self.prepare(command, log, timeout)
            project = Path(command[command.index("-projectPath") + 1])
            path = project / "Packages/packages-lock.json"
            data = json.loads(path.read_text())
            data["dependencies"]["com.unity.ext.nunit"]["source"] = "registry"
            path.write_text(json.dumps(data))
            return result

        code, _, report, _ = self.invoke(source_drift)
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertEqual(report["resolved_packages"]["packages"]["com.unity.ext.nunit"], {"version": "2.0.5", "source": "registry"})


if __name__ == "__main__":
    unittest.main()
