"""Disposable package drift fixtures; compiler, Editor, tests and Player are mocked."""
import importlib
import json
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_combined_map_runner as map_fixtures
from test_package_initialization import IDENTITY, cache_descriptors


class NativeRunnerPackagePinTests(unittest.TestCase):
    runners = ("run_foundation", "run_sandbox")
    build_guid = "a" * 32
    epoch = "b" * 32

    def fixture(self):
        fixture = map_fixtures.CombinedMapRunnerTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.runtime / "validation").mkdir()
        for name in ("expected-tests.json", "sandbox-expected-tests.json"):
            (fixture.runtime / "validation" / name).write_text(json.dumps({"EditMode": ["Fixture.A"], "PlayMode": ["Fixture.B"]}))
        return fixture

    def mutate(self, project, kind):
        if kind in ("code", "code_meta", "package_code", "removed_code"):
            path = project / "Assets/Subject.cs"
            if kind == "removed_code":
                path.unlink()
            else:
                if kind == "code_meta": path = path.with_suffix(".cs.meta")
                if kind == "package_code": path = project.parent / "dotnet/src/Changed.cs"
                path.write_text("// native phase rewrote an executable input or its identity")
            return
        if kind == "manifest":
            path = project / "Packages/manifest.json"
            data = json.loads(path.read_text())
            data["dependencies"]["com.unity.test-framework"] = "1.7.0"
        elif kind in ("lock_version", "lock_source"):
            path = project / "Packages/packages-lock.json"
            data = json.loads(path.read_text())
            data["dependencies"]["com.unity.test-framework"]["version" if kind == "lock_version" else "source"] = (
                "1.7.0" if kind == "lock_version" else "registry")
        else:
            path = project / "Library/PackageCache/com.unity.ext.nunit@fixture/package.json"
            data = json.loads(path.read_text())
            if kind == "descriptor_content":
                data["dependencies"] = {"com.unity.unexpected": "9.9.9"}
            else:
                data["version"] = "2.0.3"
        path.write_text(json.dumps(data))

    def invoke(self, name, drift_phase=None, kind="manifest", fail_build=False, final_window_drift=False):
        fixture, project_seen = self.fixture(), []
        module = importlib.import_module(name)
        target = "Win64" if sys.platform == "win32" else "Linux64"
        with ExitStack() as stack:
            stack.enter_context(patch.object(module, "RUNTIME", fixture.runtime))
            stack.enter_context(patch.object(module, "checkout_revision", return_value="fixture-checkout"))
            stack.enter_context(patch.object(module, "inspect_editor", return_value={"status": "Verified"}))
            if name == "run_sandbox":
                stack.enter_context(patch.object(module, "check", return_value={"status": "Passed", "production_asmdefs": 1}))

            def execute(command, log, timeout):
                code = 0
                if "-projectPath" not in command:
                    project = project_seen[0]
                    phase = "player"
                    if name == "run_sandbox":
                        text = (f"CS_SANDBOX_PLAYER_READY unity=6000.4.3f1 build={self.build_guid} epoch={self.epoch} bindings=11 bodies=31 meshes=1\n"
                                f"CS_SANDBOX_PLAYER_STOPPED epoch={self.epoch} frames=120 milliseconds=2400 errors=0 bindings=0 bodies=0 objects=0 claims=0 timers=0 connections=0\n")
                    else:
                        text = (f"CS_FOUNDATION_READY unity=6000.4.3f1 build={self.build_guid}\n"
                                "CS_FOUNDATION_STOPPED frames=12 errors=0\n")
                else:
                    project = Path(command[command.index("-projectPath") + 1])
                    if not project_seen:
                        project_seen.append(project)
                    if "-accept-apiupdate" in command:
                        phase, text = "initialize", IDENTITY
                        cache_descriptors(project)
                    elif "-runTests" in command:
                        suite = command[command.index("-testPlatform") + 1]
                        phase, text = suite, IDENTITY
                        result = Path(command[command.index("-testResults") + 1])
                        root = ET.Element("test-run", result="Passed", total="1", passed="1", failed="0", skipped="0", inconclusive="0")
                        ET.SubElement(root, "test-case", fullname="Fixture.A" if suite == "EditMode" else "Fixture.B", result="Passed")
                        ET.ElementTree(root).write(result, encoding="utf-8")
                    else:
                        method = command[command.index("-executeMethod") + 1]
                        if method.endswith(".Prepare"):
                            phase = "import"
                            text = IDENTITY + ("CS_SANDBOX_PREPARED\nCS_SANDBOX_ASSEMBLIES count=1\n" if name == "run_sandbox" else "CS_FOUNDATION_PREPARED\n")
                        else:
                            self.assertTrue(method.endswith(".Build"))
                            phase = "build"
                            argument = "-csSandboxBuildPath" if name == "run_sandbox" else "-csBuildPath"
                            binary = Path(command[command.index(argument) + 1])
                            binary.parent.mkdir(parents=True, exist_ok=True)
                            binary.write_bytes(b"not executable; Player execution is also mocked")
                            prefix = "CS_SANDBOX_BUILD_OK" if name == "run_sandbox" else "CS_FOUNDATION_BUILD_OK"
                            text = IDENTITY + prefix + " guid=" + self.build_guid + "\n"
                            if fail_build:
                                code = 7
                if phase == drift_phase:
                    self.mutate(project, kind)
                log.write_text(text)
                return code, text

            if final_window_drift:
                original_audit = module.audit_package_pins

                def interleave(report, project, expected, checkpoint, required=True):
                    result = original_audit(report, project, expected, checkpoint, required)
                    if checkpoint == "before_success":
                        self.mutate(project, kind)
                    return result

                stack.enter_context(patch.object(module, "audit_package_pins", side_effect=interleave))
            native = stack.enter_context(patch.object(module, "execute", side_effect=execute))
            arguments = [str(fixture.editor), fixture.base / "evidence", target]
            if name == "run_sandbox":
                code, output = module.run(*arguments, build_player=True, run_player=True)
            else:
                code, output = module.run(*arguments)
            return code, output, json.loads((output / "report.json").read_text()), native

    def test_unchanged_native_pins_complete_both_runner_lifecycles(self):
        for name in self.runners:
            with self.subTest(runner=name):
                code, _, report, _ = self.invoke(name)
                self.assertEqual((code, report["status"]), (0, "Passed"))
                self.assertEqual(report["phases"]["player"]["status"], "Passed")
                self.assertEqual(report["package_pin_audits"]["after_import"]["status"], "Passed")
                self.assertEqual(report["package_pin_audits"]["after_build"]["status"], "Passed")
                self.assertEqual(report["package_pin_audits"]["before_success"]["status"], "Passed")
                self.assertEqual(report["package_pin_audits"]["final"]["status"], "Passed")
                self.assertEqual(report["copied_code_audits"]["final"]["status"], "Passed")

    def test_native_phases_cannot_rewrite_copied_code_or_metadata(self):
        for name in self.runners:
            for phase in ("import", "PlayMode", "build", "player"):
                for kind in ("code", "code_meta", "package_code", "removed_code"):
                    with self.subTest(runner=name, phase=phase, kind=kind):
                        code, _, report, _ = self.invoke(name, phase, kind)
                        self.assertEqual((code, report["status"]), (1, "Failed"))
                        self.assertEqual(report["copied_code_audits"]["final"]["status"], "Failed")
                        self.assertTrue(report["source_unchanged"], "Canonical inputs did not change.")
                        self.assertIn("Copied code audit", report["reason"])

    def test_final_code_audit_preserves_the_original_native_failure(self):
        for name in self.runners:
            with self.subTest(runner=name):
                code, _, report, _ = self.invoke(name, "build", "code", fail_build=True)
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertIn("build returned 7", report["reason"])
                self.assertEqual(report["copied_code_audits"]["final"]["status"], "Failed")

    def test_prepare_manifest_or_selected_source_drift_stops_before_tests(self):
        for name in self.runners:
            for kind in ("manifest", "lock_source"):
                with self.subTest(runner=name, kind=kind):
                    code, _, report, native = self.invoke(name, "import", kind)
                    self.assertEqual((code, report["status"], native.call_count), (1, "Failed", 2))
                    self.assertEqual(report["phases"]["PlayMode"]["status"], "NotRun")
                    self.assertEqual(report["phases"]["build"]["status"], "NotRun")
                    self.assertEqual(report["package_pin_audits"]["after_import"]["status"], "Failed")
                    self.assertEqual(report["package_pin_audits"]["final"]["status"], "Failed")
                    self.assertIn("after_import", report["reason"])
                    self.assertTrue(report["source_unchanged"], "Only the disposable package state was changed.")

    def test_good_build_markers_cannot_hide_selected_version_or_descriptor_drift(self):
        for name in self.runners:
            for kind in ("lock_version", "descriptor", "descriptor_content"):
                with self.subTest(runner=name, kind=kind):
                    code, output, report, native = self.invoke(name, "build", kind)
                    self.assertEqual((code, report["status"]), (1, "Failed"))
                    self.assertIn("_BUILD_OK guid=" + self.build_guid, (output / "logs/build.log").read_text())
                    self.assertEqual(report["package_pin_audits"]["after_build"]["status"], "Failed")
                    self.assertEqual(report["phases"]["player"]["status"], "NotRun")
                    self.assertTrue(all("-projectPath" in call.args[0] for call in native.call_args_list))
                    if kind == "descriptor_content":
                        self.assertFalse(report["package_pin_audits"]["after_build"]["descriptor_hashes_match_initialization"])

    def test_pin_drift_during_an_otherwise_valid_player_is_rejected_before_success(self):
        for name in self.runners:
            with self.subTest(runner=name):
                code, _, report, _ = self.invoke(name, "player", "lock_source")
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertEqual(report["package_pin_audits"]["before_success"]["status"], "Failed")
                self.assertEqual(report["package_pin_audits"]["final"]["status"], "Failed")

    def test_final_pin_audit_cannot_erase_an_earlier_native_exit_failure(self):
        for name in self.runners:
            with self.subTest(runner=name):
                code, _, report, _ = self.invoke(name, "build", "lock_version", fail_build=True)
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertIn("build returned 7", report["reason"])
                self.assertEqual(report["phases"]["build"]["exit_code"], 7)
                self.assertEqual(report["package_pin_audits"]["final"]["status"], "Failed")
                self.assertNotIn("after_build", report["package_pin_audits"])

    def test_final_audit_closes_the_window_after_the_pre_success_pin_check(self):
        for name in self.runners:
            with self.subTest(runner=name):
                code, _, report, _ = self.invoke(name, kind="manifest", final_window_drift=True)
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertEqual(report["package_pin_audits"]["before_success"]["status"], "Passed")
                self.assertEqual(report["package_pin_audits"]["final"]["status"], "Failed")
                self.assertIn("Final native package pin audit failed", report["reason"])


if __name__ == "__main__":
    unittest.main()
