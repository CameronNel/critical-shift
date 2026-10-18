"""Mocked package-initialization and three-runner failure fixtures; no native calls."""
import hashlib
import importlib
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_foundation  # Proposal entry adds canonical read-only helper imports.
import package_initialization as initialization
import test_combined_map_runner as map_fixtures
from evidence import EvidenceError, validate_log


PROFILE = {"editor": "6000.4.3f1", "revision": "39d1a88d4dd1", "testFramework": "1.6.0"}
IDENTITY = "Built from '6000.4/staging'; Version is '6000.4.3f1 (39d1a88d4dd1) revision 3789224'\n"
DIAGNOSTICS = (
    "Library\\PackageCache\\com.unity.shadergraph@fixture\\Editor\\Generation\\Targets\\BuiltIn\\Editor\\ShaderGraph\\Targets\\BuiltInCanvasSubTarget.cs(10,25): error CS0246: The type or namespace name 'GUID' could not be found (are you missing a using directive or an assembly reference?)\n"
    "Library\\PackageCache\\com.unity.shadergraph@fixture\\Editor\\Generation\\Contexts\\TargetSetupContext.cs(62,40): error CS0246: The type or namespace name 'GUID' could not be found (are you missing a using directive or an assembly reference?)\n"
    "[API Updater] Updated Files:\n"
    "Library/PackageCache/com.unity.shadergraph@fixture/Editor/Generation/Contexts/TargetSetupContext.cs\n"
    "Library/PackageCache/com.unity.shadergraph@fixture/Editor/Generation/Targets/BuiltIn/Editor/ShaderGraph/Targets/BuiltInCanvasSubTarget.cs\n"
    "Finished running ScriptUpdaters\n*** Tundra build success (fixture)\n"
)


def cache_descriptors(project):
    packages = json.loads((project / "Packages/packages-lock.json").read_text())["dependencies"]
    for name, row in packages.items():
        if row["source"] == "local":
            continue
        descriptor = project / "Library/PackageCache" / (name + "@fixture") / "package.json"
        descriptor.parent.mkdir(parents=True, exist_ok=True)
        descriptor.write_text(json.dumps({"name": name, "version": row["version"]}))
        if name == "com.unity.shadergraph":
            for relative in ("Editor/Generation/Contexts/TargetSetupContext.cs",
                             "Editor/Generation/Targets/BuiltIn/Editor/ShaderGraph/Targets/BuiltInCanvasSubTarget.cs"):
                source = descriptor.parent / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("// post-updater source hashing fixture; never compiled\n")


class PackageInitializationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name)
        self.project = self.output / "workspace/runtime/unity"
        self.log = self.output / "logs/package-initialize.log"
        self.log.parent.mkdir()
        for folder in (self.project / "Assets", self.project / "Packages", self.project.parent / "dotnet/src"):
            folder.mkdir(parents=True)
        (self.project / "Assets/Subject.cs").write_text("// original first-party code")
        (self.project.parent / "dotnet/src/package.json").write_text('{"name":"com.criticalshift.gameplay"}')
        manifest = {"dependencies": {"com.unity.test-framework": "1.6.0"}}
        lock = {"dependencies": {"com.unity.test-framework": {"version": "1.6.0", "source": "builtin"},
                                 "com.unity.ext.nunit": {"version": "2.0.5", "source": "builtin"},
                                 "com.unity.shadergraph": {"version": "17.4.0", "source": "builtin"}}}
        (self.project / "Packages/manifest.json").write_text(json.dumps(manifest))
        (self.project / "Packages/packages-lock.json").write_text(json.dumps(lock))
        self.editor = self.output / "Unity.exe"
        self.editor.write_bytes(b"not executable; native command is mocked")

    def invoke(self, text=IDENTITY + DIAGNOSTICS, code=0, artifact=True, mutate=None, identity=None):
        record = {}

        def execute(command, log, timeout):
            cache_descriptors(self.project)
            if mutate:
                mutate()
            if artifact:
                log.write_text(text)
            return code, text

        native = Mock(side_effect=execute)
        try:
            initialization.initialize_packages(self.editor, self.project, "Win64", PROFILE, self.log, record,
                                               native, {"status": "Verified"} if identity is None else identity)
        except EvidenceError:
            return record, native, True
        return record, native, False

    def test_diagnostics_are_retained_as_failed_strict_log_and_never_become_acceptance(self):
        record, native, failed = self.invoke()
        self.assertFalse(failed)
        self.assertEqual((record["status"], record["strict_log_status"], record["acceptance_status"]),
                         ("CompletedWithDiagnostics", "Failed", "NotRun"))
        self.assertIn("CS0246", record["first_diagnostic"])
        self.assertIn("Execution log contains", record["strict_log_reason"])
        self.assertEqual(record["native_log_sha256"], hashlib.sha256(self.log.read_bytes()).hexdigest())
        self.assertEqual(self.log.read_text(), IDENTITY + DIAGNOSTICS)
        self.assertTrue(record["first_party_code_unchanged"])
        self.assertEqual(record["known_sdk_update"]["status"], "ExpectedShaderGraphGuidApiUpdate")
        self.assertEqual(len(record["known_sdk_update"]["updated_sources"]), 2)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in record["known_sdk_update"]["updated_sources"]))
        with self.assertRaises(EvidenceError):
            validate_log(self.log.read_text())  # Original strict validator still rejects the retained log.
        command = native.call_args.args[0]
        for flag in ("-batchmode", "-nographics", "-quit", "-accept-apiupdate"):
            self.assertIn(flag, command)
        self.assertNotIn("-executeMethod", command)
        self.assertNotIn("-runTests", command)
        self.assertNotIn("-ignorecompilererrors", command)

    def test_clean_initialization_also_grants_no_validation_or_prepare_acceptance(self):
        record, _, failed = self.invoke(text=IDENTITY)
        self.assertFalse(failed)
        self.assertEqual((record["status"], record["strict_log_status"], record["acceptance_status"]), ("Completed", "Passed", "NotRun"))

    def test_unknown_vendor_compiler_error_is_fatal_even_with_the_known_updater_episode(self):
        record, _, failed = self.invoke(text=IDENTITY + DIAGNOSTICS +
                                       "Library/PackageCache/com.unity.shadergraph@fixture/Editor/Unrelated.cs(1,1): error CS0103: UnknownName does not exist\n")
        self.assertTrue(failed)
        self.assertEqual((record["status"], record["strict_log_status"]), ("Failed", "Failed"))
        self.assertIn("outside the two known", record["reason"])

    def test_first_party_warning_cannot_be_erased_by_a_later_clean_compile(self):
        record, _, failed = self.invoke(text=IDENTITY + DIAGNOSTICS + "Assets/CriticalShift/Worker.cs(1,1): warning CS0168: unused variable\n")
        self.assertTrue(failed)
        self.assertEqual(record["known_sdk_update"]["status"], "Rejected")
        self.assertIn("warning CS0168", record["known_sdk_update"]["unexpected_diagnostic"]["text"])

    def test_caught_null_reference_exception_remains_fatal_even_at_exit_zero(self):
        record, _, failed = self.invoke(text=IDENTITY + DIAGNOSTICS + "NullReferenceException: caught during SDK initialization\n")
        self.assertTrue(failed)
        self.assertEqual(record["status"], "Failed")
        self.assertIn("outside the two known", record["reason"])

    def test_other_managed_exception_headers_cannot_hide_in_the_known_sdk_update(self):
        for header in ("IndexOutOfRangeException: native initialization bounds failure\n",
                       "System.IO.IOException: native initialization file failure\n",
                       " ---> System.ArgumentOutOfRangeException: nested initialization failure\n",
                       "System.TypeInitializationException:\n"):
            with self.subTest(header=header):
                with self.assertRaises(EvidenceError):
                    validate_log(header)  # Strict phases now reject the same actual exception headers.
                record, _, failed = self.invoke(text=IDENTITY + DIAGNOSTICS + header)
                self.assertTrue(failed)
                self.assertEqual((record["status"], record["strict_log_status"]), ("Failed", "Failed"))
                self.assertEqual(record["known_sdk_update"]["status"], "Rejected")
                self.assertIn("managed exception header", record["reason"])
                self.assertEqual(record["managed_exception_headers"][0]["text"], header.rstrip("\n"))

    def test_managed_exception_without_known_sdk_diagnostics_also_fails_initialization(self):
        record, _, failed = self.invoke(text=IDENTITY + "System.IO.IOException: caught during initialization\n")
        self.assertTrue(failed)
        self.assertEqual((record["status"], record["strict_log_status"]), ("Failed", "Failed"))
        self.assertIn("managed exception header", record["reason"])

    def test_sdk_warning_stack_exception_reference_arguments_are_not_exception_headers(self):
        stack = ("Library/PackageCache/com.unity.shadergraph@fixture/Editor/Example.cs(1,1): warning CS0618: obsolete vendor API\n"
                 "UnityEditor.ShaderGraph.Drawing.MaterialGraphEditWindow:Open (System.Exception& exception, System.Boolean result)\n"
                 "UnityEditor.ShaderGraph.SomeHelper:TryLoad (System.String path, System.Exception& error)\n")
        record, _, failed = self.invoke(text=IDENTITY + DIAGNOSTICS + stack)
        self.assertFalse(failed)
        self.assertEqual(record["status"], "CompletedWithDiagnostics")
        self.assertEqual(record["managed_exception_headers"], [])

    def test_known_errors_without_an_updater_file_list_are_fatal(self):
        text = IDENTITY + DIAGNOSTICS.replace("[API Updater] Updated Files:\n", "")
        record, _, failed = self.invoke(text=text)
        self.assertTrue(failed)
        self.assertIn("updater file list is missing", record["reason"])

    def test_updater_must_list_both_exact_diagnostic_files(self):
        text = IDENTITY + DIAGNOSTICS.replace("Library/PackageCache/com.unity.shadergraph@fixture/Editor/Generation/Contexts/TargetSetupContext.cs\n", "")
        record, _, failed = self.invoke(text=text)
        self.assertTrue(failed)
        self.assertIn("must list both diagnostic files", record["reason"])

    def test_absent_or_only_pre_updater_rebuild_success_does_not_qualify(self):
        no_rebuild = DIAGNOSTICS.replace("*** Tundra build success (fixture)\n", "")
        for text in (IDENTITY + no_rebuild, IDENTITY + "*** Tundra build success (earlier unrelated build)\n" + no_rebuild):
            with self.subTest(text=text):
                record, _, failed = self.invoke(text=text)
                self.assertTrue(failed)
                self.assertIn("subsequent successful native Tundra rebuild", record["reason"])

    def test_same_diagnostics_with_another_selected_shadergraph_version_are_fatal(self):
        lock = self.project / "Packages/packages-lock.json"
        data = json.loads(lock.read_text())
        data["dependencies"]["com.unity.shadergraph"]["version"] = "17.3.0"
        lock.write_text(json.dumps(data))
        record, _, failed = self.invoke()
        self.assertTrue(failed)
        self.assertIn("selected builtin ShaderGraph 17.4.0", record["reason"])

    def test_unknown_guid_error_at_a_different_shadergraph_file_is_fatal(self):
        text = IDENTITY + DIAGNOSTICS.replace("BuiltInCanvasSubTarget.cs(10,25)", "DifferentCanvasSubTarget.cs(10,25)")
        record, _, failed = self.invoke(text=text)
        self.assertTrue(failed)
        self.assertIn("outside the two known", record["reason"])

    def test_nonzero_return_is_fatal_even_after_an_updater_success_message(self):
        record, native, failed = self.invoke(code=2)
        self.assertTrue(failed)
        self.assertEqual((record["status"], record["exit_code"], record["strict_log_status"]), ("Failed", 2, "Failed"))
        self.assertIn("returned 2", record["reason"])
        self.assertEqual(native.call_count, 1)

    def test_native_log_artifact_is_required_even_when_callback_returns_good_text(self):
        record, _, failed = self.invoke(text=IDENTITY, artifact=False)
        self.assertTrue(failed)
        self.assertEqual(record["status"], "Failed")
        self.assertIsNone(record["native_log_sha256"])

    def test_empty_native_log_never_completes_initialization(self):
        record, _, failed = self.invoke(text="")
        self.assertTrue(failed)
        self.assertEqual((record["status"], record["strict_log_status"]), ("Failed", "NotRun"))

    def test_wrong_or_absent_native_revision_blocks_initialization(self):
        for text in (IDENTITY.replace("39d1a88d4dd1", "000000000000"), "No engine identity\n"):
            with self.subTest(text=text):
                record, _, failed = self.invoke(text=text)
                self.assertTrue(failed)
                self.assertEqual(record["status"], "Blocked")
                self.assertIn("Exact native Editor", record["reason"])

    def test_license_unavailability_is_blocked_and_keeps_return_code(self):
        record, _, failed = self.invoke(text="No valid Unity Editor license\n", code=198)
        self.assertTrue(failed)
        self.assertEqual((record["status"], record["exit_code"]), ("Blocked", 198))

    def test_unverified_editor_metadata_cannot_launch_the_initialization_process(self):
        record, native, failed = self.invoke(identity={"status": "Unavailable"})
        self.assertTrue(failed)
        self.assertEqual(record["status"], "Blocked")
        native.assert_not_called()

    def test_package_pin_mutation_blocks_a_zero_exit_with_clean_log(self):
        path = self.project / "Packages/packages-lock.json"

        def mutate():
            data = json.loads(path.read_text())
            data["dependencies"]["com.unity.ext.nunit"]["version"] = "2.0.3"
            path.write_text(json.dumps(data))

        record, _, failed = self.invoke(text=IDENTITY, mutate=mutate)
        self.assertTrue(failed)
        self.assertEqual(record["status"], "Failed")
        self.assertIn("selected package versions or sources differ", record["reason"])

    def test_first_party_rewrite_cannot_become_a_healthy_initialized_input(self):
        record, _, failed = self.invoke(mutate=lambda: (self.project / "Assets/Subject.cs").write_text("// rewritten by initialization"))
        self.assertTrue(failed)
        self.assertEqual(record["status"], "Failed")
        self.assertFalse(record["first_party_code_unchanged"])

    def test_code_metadata_identity_rewrites_are_part_of_the_immutable_input_audit(self):
        for name in ("Subject.cs.meta", "Subject.asmdef.meta", "Subject.asmref.meta"):
            with self.subTest(metadata=name):
                path = self.project / "Assets" / name
                path.write_text("guid: original-serialized-code-identity\n")
                record, _, failed = self.invoke(mutate=lambda: path.write_text("guid: changed-serialized-code-identity\n"))
                self.assertTrue(failed)
                self.assertEqual(record["status"], "Failed")
                self.assertFalse(record["first_party_code_unchanged"])

    def test_generated_assets_settings_and_their_metadata_are_allowed_derivatives(self):
        def generate():
            for relative in ("Assets/Generated/URPGlobalSettings.asset", "Assets/Generated/URPGlobalSettings.asset.meta",
                             "ProjectSettings/GraphicsSettings.asset"):
                path = self.project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("initialization-created derivative fixture\n")

        record, _, failed = self.invoke(mutate=generate)
        self.assertFalse(failed)
        self.assertTrue(record["first_party_code_unchanged"])
        self.assertEqual(record["acceptance_status"], "NotRun")

    def test_initialization_cannot_accidentally_target_the_canonical_project(self):
        record, native = {}, Mock()
        with self.assertRaisesRegex(EvidenceError, "disposable project copy"):
            initialization.initialize_packages(self.editor, self.output / "runtime/unity", "Win64", PROFILE, self.log,
                                               record, native, {"status": "Verified"})
        native.assert_not_called()


class SeparateStrictPrepareTests(unittest.TestCase):
    def fixture(self):
        fixture = map_fixtures.CombinedMapRunnerTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.runtime / "validation").mkdir()
        for name in ("expected-tests.json", "sandbox-expected-tests.json"):
            (fixture.runtime / "validation" / name).write_text(json.dumps({"EditMode": ["Fixture.A"], "PlayMode": ["Fixture.B"]}))
        lock = fixture.runtime / "unity/Packages/packages-lock.json"
        data = json.loads(lock.read_text())
        data["dependencies"]["com.unity.shadergraph"] = {"version": "17.4.0", "source": "builtin"}
        lock.write_text(json.dumps(data))
        return fixture

    def invoke(self, module_name, prepare_text=None, prepare_code=0, initialization_code=0):
        fixture = self.fixture()
        module = importlib.import_module(module_name)
        with ExitStack() as stack:
            stack.enter_context(patch.object(module, "RUNTIME", fixture.runtime))
            stack.enter_context(patch.object(module, "checkout_revision", return_value="fixture-checkout"))
            stack.enter_context(patch.object(module, "inspect_editor", return_value={"status": "Verified"}))
            if module_name != "run_foundation":
                stack.enter_context(patch.object(module, "check", return_value={"status": "Passed", "production_asmdefs": 1}))

            def execute(command, log, timeout):
                project = Path(command[command.index("-projectPath") + 1])
                cache_descriptors(project)
                if "-executeMethod" not in command:
                    text, code = IDENTITY + DIAGNOSTICS, initialization_code
                else:
                    text, code = prepare_text if prepare_text is not None else IDENTITY, prepare_code
                log.write_text(text)
                return code, text

            native = stack.enter_context(patch.object(module, "execute", side_effect=execute))
            arguments = [str(fixture.editor), fixture.base / "evidence", "Win64"]
            if module_name == "run_combined_map":
                arguments.append(fixture.map)
            code, output = module.run(*arguments)
            return code, output, json.loads((output / "report.json").read_text()), native

    def test_all_three_runners_reject_diagnostics_in_the_separate_prepare_log(self):
        for name in ("run_foundation", "run_sandbox", "run_combined_map"):
            with self.subTest(runner=name):
                code, output, report, native = self.invoke(name, IDENTITY + "InvalidOperationException: second process failed\n")
                prepare = "prepare" if name == "run_combined_map" else "import"
                self.assertEqual((code, report["status"], native.call_count), (1, "Failed", 2))
                self.assertEqual(report["phases"]["package-initialize"]["status"], "CompletedWithDiagnostics")
                self.assertEqual(report["phases"]["package-initialize"]["strict_log_status"], "Failed")
                self.assertEqual(report["phases"][prepare]["status"], "Failed")
                first, second = [call.args[0] for call in native.call_args_list]
                self.assertNotIn("-executeMethod", first)
                self.assertIn("-executeMethod", second)
                self.assertNotEqual(first[first.index("-logFile") + 1], second[second.index("-logFile") + 1])
                self.assertIn("CS0246", (output / "logs/package-initialize.log").read_text())
                self.assertIn("second process failed", (output / "logs" / (prepare + ".log")).read_text())

    def test_no_runner_reports_pass_when_initialization_is_the_only_completed_operation(self):
        for name in ("run_foundation", "run_sandbox", "run_combined_map"):
            with self.subTest(runner=name):
                code, _, report, native = self.invoke(name)  # Clean second log, but no prepare marker.
                self.assertEqual((code, report["status"], native.call_count), (1, "Failed", 2))
                self.assertEqual(report["phases"]["package-initialize"]["acceptance_status"], "NotRun")
                self.assertTrue(all(record["status"] == "NotRun" for key, record in report["phases"].items()
                                    if key in ("EditMode", "PlayMode", "build", "player")))

    def test_nonzero_initialization_never_reaches_any_prepare_process(self):
        for name in ("run_foundation", "run_sandbox", "run_combined_map"):
            with self.subTest(runner=name):
                code, _, report, native = self.invoke(name, initialization_code=2)
                self.assertEqual((code, report["status"], native.call_count), (1, "Failed", 1))
                self.assertEqual(report["phases"]["package-initialize"]["exit_code"], 2)
                prepare = "prepare" if name == "run_combined_map" else "import"
                self.assertEqual(report["phases"][prepare]["status"], "NotRun")


if __name__ == "__main__":
    unittest.main()
