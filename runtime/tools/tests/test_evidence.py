import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import EvidenceError, read_result_evidence, validate_log, validate_player, validate_results, validate_sandbox_player
from run_foundation import RUNTIME, execute, fingerprint, run
from run_sandbox import run as run_sandbox
import run_sandbox as sandbox_runner


class ResultEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "results.xml"
        self.expected = {"Fixture.A", "Fixture.B"}
        self.root = ET.Element("test-run", result="Passed", total="2", passed="2", failed="0", skipped="0", inconclusive="0")
        for name in sorted(self.expected):
            ET.SubElement(self.root, "test-case", fullname=name, result="Passed")

    def save(self):
        ET.ElementTree(self.root).write(self.path)

    def reject(self):
        self.save()
        with self.assertRaises(EvidenceError):
            validate_results(self.path, self.expected, 0)

    def test_valid_results_report_exact_counts(self):
        self.save()
        self.assertEqual(validate_results(self.path, self.expected, 0)["executed"], 2)

    def test_missing_xml_cannot_pass_with_zero_exit(self):
        with self.assertRaises(EvidenceError):
            validate_results(self.path, self.expected, 0)

    def test_malformed_xml_rejected(self):
        self.path.write_text("<broken")
        with self.assertRaises(EvidenceError):
            validate_results(self.path, self.expected, 0)

    def test_zero_tests_rejected(self):
        self.root.clear()
        self.root.attrib.update(result="Passed", total="0", passed="0", failed="0", skipped="0", inconclusive="0")
        self.reject()

    def test_failed_case_rejected_even_with_green_summary(self):
        self.root[0].set("result", "Failed")
        self.reject()

    def test_skipped_case_rejected(self):
        self.root[0].set("result", "Skipped")
        self.reject()

    def test_wrong_test_identity_rejected(self):
        self.root[0].set("fullname", "Unrelated.Test")
        self.reject()

    def test_duplicate_identity_rejected(self):
        self.root[0].set("fullname", self.root[1].get("fullname"))
        self.reject()

    def test_summary_count_mismatch_rejected(self):
        self.root.set("passed", "3")
        self.reject()

    def test_missing_summary_count_rejected(self):
        self.root.attrib.pop("inconclusive")
        self.reject()

    def test_malformed_summary_count_rejected(self):
        self.root.set("total", "two")
        self.reject()

    def test_failed_parent_suite_rejected(self):
        ET.SubElement(self.root, "test-suite", result="Failed")
        self.reject()

    def test_nonzero_process_rejected_with_passing_xml(self):
        self.save()
        with self.assertRaises(EvidenceError):
            validate_results(self.path, self.expected, 17)

    def test_empty_expected_catalogue_rejected(self):
        self.save()
        with self.assertRaises(EvidenceError):
            validate_results(self.path, set(), 0)

    def test_failed_xml_observations_retain_counts_and_diagnostics_without_acceptance(self):
        self.root.set("result", "Failed(Child)")
        self.root.set("passed", "1")
        self.root.set("failed", "1")
        self.root[1].set("result", "Failed")
        failure = ET.SubElement(self.root[1], "failure")
        ET.SubElement(failure, "message").text = "The actual physics assertion failed."
        ET.SubElement(failure, "stack-trace").text = str(Path.home()) + "/Fixture.cs:10"
        self.save()
        observed = read_result_evidence(self.path, self.expected)
        self.assertEqual(observed["reported_counts"], {"total": 2, "passed": 1, "failed": 1, "skipped": 0, "inconclusive": 0})
        self.assertEqual(observed["test_identities"], sorted(self.expected))
        self.assertEqual(observed["failed_test_identities"], ["Fixture.B"])
        self.assertEqual(observed["failed_cases"][0]["message"], "The actual physics assertion failed.")
        self.assertIn("<HOME>", observed["failed_cases"][0]["stack_trace"])
        for code in (0, 2):
            with self.subTest(exit_code=code), self.assertRaises(EvidenceError):
                validate_results(self.path, self.expected, code)

    def test_missing_or_malformed_xml_observations_do_not_invent_counts(self):
        missing = read_result_evidence(self.path, self.expected)
        self.assertFalse(missing["artifact_present"])
        self.assertNotIn("reported_counts", missing)
        self.path.write_text("<test-run broken")
        malformed = read_result_evidence(self.path, self.expected)
        self.assertTrue(malformed["artifact_present"])
        self.assertIn("read_error", malformed)
        self.assertNotIn("reported_counts", malformed)
        self.assertNotIn("xml_test_cases", malformed)

    def test_observed_inventory_mismatch_remains_visible_with_a_green_xml_summary(self):
        self.root[1].set("fullname", "Fixture.Unexpected")
        self.root.set("failed", "invalid")
        self.save()
        observed = read_result_evidence(self.path, self.expected)
        self.assertEqual(observed["missing_expected_tests"], ["Fixture.B"])
        self.assertEqual(observed["unexpected_tests"], ["Fixture.Unexpected"])
        self.assertEqual(observed["invalid_summary_fields"], ["failed"])
        self.assertNotIn("failed", observed["reported_counts"])


class SandboxFailedResultReportingTests(unittest.TestCase):
    """Real XML parsing with all native execution mocked; no Editor or compiler is launched."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.runtime = self.base / "repository/runtime"
        for directory in ("unity/Assets", "unity/Packages", "unity/ProjectSettings", "dotnet/src", "validation"):
            (self.runtime / directory).mkdir(parents=True)
        (self.runtime / "toolchain.json").write_text(json.dumps({"editor": "6000.4.3f1", "revision": "39d1a88d4dd1"}))
        (self.runtime / "dotnet/src/package.json").write_text("{}")
        (self.runtime / "unity/Assets/Subject.cs").write_text("// source fixture")
        (self.runtime / "unity/Packages/manifest.json").write_text(json.dumps({
            "dependencies": {"com.unity.test-framework": "1.6.0"}}))
        (self.runtime / "unity/Packages/packages-lock.json").write_text(json.dumps({"dependencies": {
            "com.unity.test-framework": {"version": "1.6.0", "source": "builtin"},
            "com.unity.ext.nunit": {"version": "2.0.5", "source": "builtin"}}}))
        (self.runtime / "validation/sandbox-expected-tests.json").write_text(json.dumps({"PlayMode": ["Fixture.A", "Fixture.B"]}))
        self.editor = self.base / "Unity.exe"
        self.editor.write_bytes(b"not executable")
        self.exit_code, self.change_source = 2, False

    def native(self, command, log, timeout):
        if "-accept-apiupdate" in command:
            self.assertNotIn("-executeMethod", command)
            self.assertNotIn("-runTests", command)
            project = Path(command[command.index("-projectPath") + 1])
            for name, version in (("com.unity.test-framework", "1.6.0"), ("com.unity.ext.nunit", "2.0.5")):
                descriptor = project / "Library/PackageCache" / (name + "@fixture") / "package.json"
                descriptor.parent.mkdir(parents=True, exist_ok=True)
                descriptor.write_text(json.dumps({"name": name, "version": version}))
            text = "Built from 'fixture'; Version is '6000.4.3f1 (39d1a88d4dd1)'\n"
            log.write_text(text)
            return 0, text
        if "-runTests" not in command:
            self.assertEqual(command[command.index("-executeMethod") + 1],
                             "CriticalShift.Sandbox.Editor.SandboxSceneBuilder.Prepare")
            text = "Initialize engine version: 6000.4.3f1 (39d1a88d4dd1)\nCS_SANDBOX_PREPARED\nCS_SANDBOX_ASSEMBLIES count=1\n"
            log.write_text(text)
            return 0, text
        result = Path(command[command.index("-testResults") + 1])
        root = ET.Element("test-run", result="Failed(Child)", total="2", passed="1", failed="1", skipped="0", inconclusive="0")
        ET.SubElement(root, "test-case", fullname="Fixture.A", result="Passed")
        failed = ET.SubElement(root, "test-case", fullname="Fixture.B", result="Failed")
        ET.SubElement(ET.SubElement(failed, "failure"), "message").text = "Native assertion diagnostic retained."
        ET.ElementTree(root).write(result, encoding="utf-8")
        if self.change_source:
            (self.runtime / "unity/Assets/Subject.cs").write_text("// changed during native execution")
        log.write_text("Native test results are in PlayMode.xml\n")
        return self.exit_code, log.read_text()

    def invoke(self):
        with ExitStack() as stack:
            stack.enter_context(patch.object(sandbox_runner, "RUNTIME", self.runtime))
            stack.enter_context(patch.object(sandbox_runner, "checkout_revision", return_value="fixture-checkout"))
            stack.enter_context(patch.object(sandbox_runner, "inspect_editor", return_value={"status": "Verified"}))
            stack.enter_context(patch.object(sandbox_runner, "check", return_value={"status": "Passed", "production_asmdefs": 1}))
            native = stack.enter_context(patch.object(sandbox_runner, "execute", side_effect=self.native))
            code, output = sandbox_runner.run(str(self.editor), self.base / "evidence", "Win64", build_player=True, run_player=True)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["phases"]["package-initialize"]["status"], "Completed")
            self.assertEqual(report["phases"]["import"]["status"], "Passed")
            return code, report, native

    def test_native_exit_two_retains_real_failed_xml_and_stops_before_build(self):
        code, report, native = self.invoke()
        self.assertEqual((code, report["status"], report["phases"]["PlayMode"]["exit_code"]), (1, "Failed", 2))
        observed = report["phases"]["PlayMode"]["result_evidence"]
        self.assertEqual(observed["reported_counts"]["failed"], 1)
        self.assertEqual(observed["reported_counts"]["passed"], 1)
        self.assertEqual(observed["xml_test_cases"], 2)
        self.assertEqual(observed["test_identities"], ["Fixture.A", "Fixture.B"])
        self.assertEqual(observed["failed_test_identities"], ["Fixture.B"])
        self.assertEqual(observed["failed_cases"][0]["message"], "Native assertion diagnostic retained.")
        self.assertIn("PlayMode returned 2", report["reason"])
        self.assertEqual(report["phases"]["build"]["status"], "NotRun")
        self.assertEqual(report["phases"]["player"]["status"], "NotRun")
        self.assertEqual(native.call_count, 3)
        commands = [call.args[0] for call in native.call_args_list]
        self.assertIn("-accept-apiupdate", commands[0])
        self.assertIn("-executeMethod", commands[1])
        self.assertIn("-runTests", commands[2])

    def test_xml_validation_failure_also_retains_native_counts_at_zero_exit(self):
        self.exit_code = 0
        code, report, _ = self.invoke()
        self.assertEqual((code, report["status"]), (1, "Failed"))
        self.assertEqual(report["phases"]["PlayMode"]["result_evidence"]["failed_test_identities"], ["Fixture.B"])
        self.assertIn("NUnit run did not pass", report["reason"])

    def test_source_audit_cannot_erase_the_first_native_failure_or_its_counts(self):
        self.change_source = True
        code, report, _ = self.invoke()
        self.assertEqual((code, report["status"], report["source_unchanged"]), (1, "Failed", False))
        self.assertIn("PlayMode returned 2", report["reason"])
        self.assertEqual(report["phases"]["PlayMode"]["result_evidence"]["reported_counts"]["failed"], 1)


class PlayerEvidenceTests(unittest.TestCase):
    guid = "a" * 32
    version = "6000.4.3f1"

    def valid(self):
        return f"CS_FOUNDATION_READY unity={self.version} build={self.guid}\nCS_FOUNDATION_STOPPED frames=12 errors=0\n"

    def check(self, text, code=0):
        return validate_player(text, code, self.version, self.guid)

    def test_valid_player_evidence(self):
        self.assertEqual(self.check(self.valid())["frames"], 12)

    def test_no_readiness_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check("CS_FOUNDATION_STOPPED frames=12 errors=0\n")

    def test_wrong_build_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid().replace(self.guid, "b" * 32))

    def test_wrong_editor_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid().replace(self.version, "6000.0.1f1"))

    def test_duplicate_ready_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid() + self.valid().splitlines()[0] + "\n")

    def test_out_of_order_lifecycle_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check("\n".join(reversed(self.valid().splitlines())))

    def test_insufficient_frames_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid().replace("frames=12", "frames=1"))

    def test_error_counter_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid().replace("errors=0", "errors=1"))

    def test_nonzero_exit_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid(), 20)

    def test_unhandled_exception_rejected(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid() + "NullReferenceException: broken binding\n")

    def test_first_party_warning_rejected(self):
        with self.assertRaises(EvidenceError):
            validate_log("Assets/CriticalShift/Bootstrap/X.cs(1,2): warning CS0168: unused\n")

    def test_canonical_package_warning_rejected(self):
        for separator in ("/", "\\"):
            with self.subTest(separator=separator), self.assertRaises(EvidenceError):
                path = separator.join(("Packages", "com.criticalshift.gameplay", "CriticalShift.Application", "WorldSession.cs"))
                validate_log(path + "(1,2): warning CS0168: unused\n")

    def test_physical_canonical_source_warning_rejected(self):
        for separator in ("/", "\\"):
            with self.subTest(separator=separator), self.assertRaises(EvidenceError):
                path = separator.join(("runtime", "dotnet", "src", "CriticalShift.Application", "WorldSession.cs"))
                validate_log(path + "(1,2): warning CS0168: unused\n")

    def test_third_party_warning_remains_separate(self):
        validate_log("Packages/com.unity.example/Example.cs(1,2): warning CS0168: tracked separately\n")
        validate_log("Packages/com.criticalshift.gameplay.vendor/Example.cs(1,2): warning CS0168: separate package\n")


class SandboxPlayerEvidenceTests(unittest.TestCase):
    guid = "c" * 32
    epoch = "d" * 32
    version = "6000.4.3f1"

    def valid(self):
        return (f"CS_SANDBOX_PLAYER_READY unity={self.version} build={self.guid} epoch={self.epoch} bindings=10 bodies=31 meshes=256\n"
                f"CS_SANDBOX_PLAYER_STOPPED epoch={self.epoch} frames=120 milliseconds=2400 errors=0 bindings=0 bodies=0 objects=0 claims=0 timers=0 connections=0\n")

    def check(self, text, code=0):
        return validate_sandbox_player(text, code, self.version, self.guid)

    def test_valid_sandbox_player_evidence(self):
        result = self.check(self.valid())
        self.assertEqual((result["frames"], result["initial_bodies"], result["remaining_objects"]), (120, 31, 0))

    def test_wrong_build_version_or_empty_epoch_is_rejected(self):
        for old, new in ((self.guid, "b" * 32), (self.version, "6000.6.2f1"), (self.epoch, "0" * 32)):
            with self.subTest(value=old), self.assertRaises(EvidenceError):
                self.check(self.valid().replace(old, new))

    def test_missing_duplicate_and_malformed_markers_are_rejected(self):
        ready, stopped = self.valid().splitlines()
        for text in (ready, stopped, self.valid() + ready, self.valid() + stopped,
                     self.valid() + "CS_SANDBOX_PLAYER_READY malformed\n"):
            with self.subTest(text=text), self.assertRaises(EvidenceError):
                self.check(text)

    def test_mismatched_world_and_reversed_lifetime_are_rejected(self):
        wrong = self.valid().replace("STOPPED epoch=" + self.epoch, "STOPPED epoch=" + "e" * 32)
        for text in (wrong, "\n".join(reversed(self.valid().splitlines()))):
            with self.subTest(text=text), self.assertRaises(EvidenceError):
                self.check(text)

    def test_incomplete_lifetime_or_runtime_inventory_is_rejected(self):
        for old, new in (("frames=120", "frames=119"), ("milliseconds=2400", "milliseconds=1999"),
                         ("bindings=10", "bindings=9"), ("bodies=31", "bodies=30"), ("meshes=256", "meshes=0")):
            with self.subTest(value=old), self.assertRaises(EvidenceError):
                self.check(self.valid().replace(old, new))

    def test_every_error_or_remaining_teardown_counter_is_rejected(self):
        for counter in ("errors", "bindings", "bodies", "objects", "claims", "timers", "connections"):
            with self.subTest(counter=counter), self.assertRaises(EvidenceError):
                self.check(self.valid().replace(counter + "=0", counter + "=1"))

    def test_nonzero_exit_or_critical_log_cannot_pass_with_good_markers(self):
        with self.assertRaises(EvidenceError):
            self.check(self.valid(), 20)
        with self.assertRaises(EvidenceError):
            self.check(self.valid() + "InvalidOperationException: lost body\n")

    def test_player_execution_requires_a_new_build_in_the_same_run(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out = run_sandbox(None, Path(temp), "Win64", run_player=True)
            report = json.loads((out / "report.json").read_text())
            self.assertEqual(code, 1)
            self.assertIn("explicit --build-player", report["reason"])
            self.assertEqual(report["phases"]["player"]["status"], "NotRun")


class RunnerSafetyTests(unittest.TestCase):
    def test_output_inside_source_is_rejected_before_creation(self):
        forbidden = RUNTIME / "unity/Assets/forbidden-output"
        self.assertFalse(forbidden.exists())
        with self.assertRaises(EvidenceError):
            run(None, forbidden, "Linux64")
        self.assertFalse(forbidden.exists())

    def test_output_inside_art_is_rejected_before_creation(self):
        forbidden = RUNTIME.parent / "sections/forbidden-wp01-output"
        self.assertFalse(forbidden.exists())
        with self.assertRaises(EvidenceError):
            run(None, forbidden, "Linux64")
        self.assertFalse(forbidden.exists())

    def test_timed_out_process_cannot_return_success(self):
        with tempfile.TemporaryDirectory() as temp:
            code, _ = execute([sys.executable, "-c", "import time; time.sleep(30)"],
                              Path(temp) / "timeout.log", 1)
            self.assertEqual(code, 124)

    def test_missing_editor_is_blocked_and_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out = run(None, Path(temp), "Linux64")
            data = json.loads((out / "report.json").read_text())
            self.assertEqual(code, 2)
            self.assertEqual(data["status"], "Blocked")
            self.assertTrue(data["source_unchanged"])
            self.assertEqual(data["phases"]["player"]["status"], "NotRun")

    def test_repeated_runs_use_fresh_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            _, first = run(None, Path(temp), "Linux64")
            _, second = run(None, Path(temp), "Linux64")
            self.assertNotEqual(first, second)

    def test_input_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "toolchain.json").write_text("{}")
            assets = root / "unity/Assets"
            assets.mkdir(parents=True)
            (root / "unity/Packages").mkdir()
            (root / "unity/ProjectSettings").mkdir()
            package = root / "dotnet/src"
            package.mkdir(parents=True)
            (package / "package.json").write_text("{}")
            try:
                (assets / "escaped.cs").symlink_to(root / "toolchain.json")
            except OSError:
                self.skipTest("OS does not grant symlink creation for this test user.")
            with self.assertRaisesRegex(EvidenceError, "Symlinks"):
                fingerprint(root)


if __name__ == "__main__":
    unittest.main()
