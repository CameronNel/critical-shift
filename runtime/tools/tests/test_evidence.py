import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import EvidenceError, validate_log, validate_player, validate_results
from run_foundation import execute, fingerprint, run


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


class RunnerSafetyTests(unittest.TestCase):
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
            try:
                (assets / "escaped.cs").symlink_to(root / "toolchain.json")
            except OSError:
                self.skipTest("OS does not grant symlink creation for this test user.")
            with self.assertRaises(EvidenceError):
                fingerprint(root)


if __name__ == "__main__":
    unittest.main()
