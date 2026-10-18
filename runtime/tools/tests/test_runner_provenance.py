"""Fault-injection source for disposable-runner provenance; native execution is always mocked."""
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import EvidenceError
from run_foundation import checkout_revision, execute, source_files


class RunnerProvenanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.editor = self.base / "Unity.exe"
        self.editor.write_bytes(b"not an executable; metadata inspection is mocked")

    def fixture(self, name):
        root = self.base / name / "runtime"
        for directory in ("unity/Assets", "unity/Packages", "unity/ProjectSettings", "dotnet/src", "validation"):
            (root / directory).mkdir(parents=True)
        (root / "toolchain.json").write_text(json.dumps({"editor": "6000.4.3f1", "revision": "39d1a88d4dd1"}))
        (root / "dotnet/src/package.json").write_text('{"name":"com.criticalshift.gameplay"}')
        (root / "unity/Assets/Subject.cs").write_text("// original source")
        for catalogue in ("expected-tests.json", "sandbox-expected-tests.json"):
            (root / "validation" / catalogue).write_text(json.dumps({"EditMode": ["Fixture.A"], "PlayMode": ["Fixture.B"]}))
        return root

    def invoke(self, module, root, stack):
        stack.enter_context(patch.object(module, "RUNTIME", root))
        stack.enter_context(patch.object(module, "checkout_revision", return_value="fixture-checkout-revision"))
        stack.enter_context(patch.object(module, "inspect_editor", return_value={"status": "Verified"}))
        if module.__name__ == "run_sandbox":
            stack.enter_context(patch.object(module, "check", return_value={"status": "Passed", "production_asmdefs": 1}))
        native = stack.enter_context(patch.object(module, "execute", side_effect=AssertionError("Native execution is forbidden in this fixture.")))
        return native

    def test_corrupted_disposable_copy_is_rejected_before_editor_launch(self):
        copy = shutil.copy2
        for name in ("run_foundation", "run_sandbox"):
            with self.subTest(runner=name), ExitStack() as stack:
                module, root = importlib.import_module(name), self.fixture(name)
                native = self.invoke(module, root, stack)

                def corrupt(source, destination):
                    result = copy(source, destination)
                    if source.name == "Subject.cs":
                        destination.write_text("// changed while the disposable copy was created")
                    return result

                stack.enter_context(patch("run_foundation.shutil.copy2", side_effect=corrupt))
                code, output = module.run(str(self.editor), self.base / (name + "-output"), "Win64")
                report = json.loads((output / "report.json").read_text())
                self.assertEqual((code, report["status"], report["source_unchanged"]), (1, "Failed", True))
                self.assertNotEqual(report["source_sha256"], report["copied_source_sha256"])
                self.assertIn("Disposable inputs differ", report["reason"])
                self.assertEqual(report["phases"]["PlayMode"]["status"], "NotRun")
                native.assert_not_called()

    def test_preflight_failure_survives_failed_final_source_audit(self):
        for name in ("run_foundation", "run_sandbox"):
            with self.subTest(runner=name), ExitStack() as stack:
                module, root = importlib.import_module(name), self.fixture(name)
                native = self.invoke(module, root, stack)

                def fail_inspection(*unused):
                    (root / "toolchain.json").unlink()
                    raise EvidenceError("First failure: Editor identity mismatch.")

                stack.enter_context(patch.object(module, "inspect_editor", side_effect=fail_inspection))
                code, output = module.run(str(self.editor), self.base / (name + "-output"), "Win64")
                report = json.loads((output / "report.json").read_text())
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertEqual(report["reason"], "First failure: Editor identity mismatch.")
                self.assertIsNone(report["source_unchanged"])
                self.assertIn("Final source audit failed", report["source_audit_error"])
                self.assertIn("ended_utc", report)
                native.assert_not_called()

    def test_unreadable_initial_source_still_writes_failed_report(self):
        for name in ("run_foundation", "run_sandbox"):
            with self.subTest(runner=name), ExitStack() as stack:
                module, root = importlib.import_module(name), self.fixture(name)
                native = self.invoke(module, root, stack)
                (root / "dotnet/src/package.json").unlink()
                code, output = module.run(str(self.editor), self.base / (name + "-output"), "Win64")
                report = json.loads((output / "report.json").read_text())
                self.assertEqual((code, report["status"]), (1, "Failed"))
                self.assertIsNone(report["source_unchanged"])
                self.assertNotIn("source_sha256", report)
                self.assertIn("source package is missing", report["reason"])
                native.assert_not_called()

    def test_malformed_profile_still_writes_failed_report(self):
        for name in ("run_foundation", "run_sandbox"):
            with self.subTest(runner=name), ExitStack() as stack:
                module, root = importlib.import_module(name), self.fixture(name)
                native = self.invoke(module, root, stack)
                (root / "toolchain.json").write_text("{broken")
                code, output = module.run(str(self.editor), self.base / (name + "-output"), "Win64")
                report = json.loads((output / "report.json").read_text())
                self.assertEqual((code, report["status"], report["error_type"]), (1, "Failed", "JSONDecodeError"))
                self.assertIsNone(report["source_unchanged"])
                native.assert_not_called()

    def test_missing_declared_input_root_is_rejected(self):
        root = self.fixture("source-root")
        (root / "unity/ProjectSettings").rmdir()
        with self.assertRaisesRegex(EvidenceError, "source directory is missing"):
            source_files(root)

    def test_checkout_revision_uses_checkout_instead_of_ci_environment(self):
        with patch.dict(os.environ, {"GITHUB_SHA": "stale-ci-revision"}), patch("run_foundation.subprocess.check_output", return_value="actual-checkout-revision\n") as git:
            self.assertEqual(checkout_revision(self.base), "actual-checkout-revision")
            self.assertEqual(git.call_args.kwargs["cwd"], self.base)


class NativeProcessCleanupTests(unittest.TestCase):
    def test_timeout_cleanup_and_reap_both_have_limits(self):
        process = Mock(pid=4321)
        process.wait.side_effect = [subprocess.TimeoutExpired("fake-editor", 1), 0]
        with tempfile.TemporaryDirectory() as temporary, patch("run_foundation.subprocess.Popen", return_value=process), patch("run_foundation.subprocess.run") as terminate, patch("run_foundation.os.killpg", create=True) as kill_group:
            code, _ = execute(["fake-editor"], Path(temporary) / "timeout.log", 1)
            self.assertEqual(code, 124)
            self.assertEqual([call.kwargs["timeout"] for call in process.wait.call_args_list], [1, 10])
            if os.name == "nt":
                self.assertEqual(terminate.call_args.kwargs["timeout"], 10)
            else:
                kill_group.assert_called_once()

    def test_failed_cleanup_preserves_redacted_log_and_never_returns_success(self):
        process = Mock(pid=4321)
        process.wait.side_effect = [subprocess.TimeoutExpired("fake-editor", 1), subprocess.TimeoutExpired("fake-editor", 10)]
        with tempfile.TemporaryDirectory() as temporary, patch("run_foundation.subprocess.Popen", return_value=process), patch("run_foundation.subprocess.run"), patch("run_foundation.os.killpg", create=True):
            log = Path(temporary) / "failed-cleanup.log"
            log.write_text("private source location: " + str(Path.home()))
            with self.assertRaisesRegex(EvidenceError, "cleanup failed"):
                execute(["fake-editor"], log, 1)
            self.assertNotIn(str(Path.home()), log.read_text())
            self.assertIn("<HOME>", log.read_text())

    def test_interruption_stops_the_process_before_propagating(self):
        process = Mock(pid=4321)
        process.wait.side_effect = [KeyboardInterrupt(), 0]
        with tempfile.TemporaryDirectory() as temporary, patch("run_foundation.subprocess.Popen", return_value=process), patch("run_foundation.subprocess.run"), patch("run_foundation.os.killpg", create=True):
            with self.assertRaises(KeyboardInterrupt):
                execute(["fake-editor"], Path(temporary) / "interrupted.log", 1)
            self.assertEqual([call.kwargs["timeout"] for call in process.wait.call_args_list], [1, 10])


if __name__ == "__main__":
    unittest.main()
