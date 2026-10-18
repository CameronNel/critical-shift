"""Path-selection tests only; fixture DLL bytes are never used as API stubs."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import api_compile
from api_compile import bundled_test_references, compile_sources, discover_assemblies, modular_references, system_references, topological_order
from acquire_toolchain import bundled_nunit


class ModularReferenceTests(unittest.TestCase):
    def test_combined_reference_is_excluded_when_modules_exist(self):
        with tempfile.TemporaryDirectory() as temporary:
            managed = Path(temporary)
            for family in ("UnityEngine", "UnityEditor"):
                folder = managed / family
                folder.mkdir()
                for path in (managed / (family + ".dll"), folder / (family + ".dll"),
                             folder / (family + ".CoreModule.dll")):
                    path.write_bytes(b"path-selection fixture, not a loadable DLL")
                self.assertEqual([p.name for p in modular_references(managed, family)],
                                 [family + ".CoreModule.dll"])

    def test_missing_core_module_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                modular_references(Path(temporary), "UnityEngine")

    def test_conflicting_same_named_modules_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            managed = Path(temporary)
            (managed / "UnityEngine").mkdir()
            (managed / "UnityEngine/UnityEngine.CoreModule.dll").write_bytes(b"first")
            (managed / "UnityEngine.CoreModule.dll").write_bytes(b"different")
            with self.assertRaises(ValueError):
                modular_references(managed, "UnityEngine")


    def test_editor_modules_in_shared_engine_directory_are_found(self):
        with tempfile.TemporaryDirectory() as temporary:
            managed = Path(temporary)
            shared = managed / "UnityEngine"
            shared.mkdir()
            for name in ("UnityEngine.CoreModule.dll", "UnityEditor.CoreModule.dll",
                         "UnityEditor.BuildPipelineModule.dll"):
                (shared / name).write_bytes(b"path fixture, not a loadable DLL")
            self.assertEqual([p.name for p in modular_references(managed, "UnityEngine")],
                             ["UnityEngine.CoreModule.dll"])
            self.assertEqual([p.name for p in modular_references(managed, "UnityEditor")],
                             ["UnityEditor.BuildPipelineModule.dll", "UnityEditor.CoreModule.dll"])

    def test_identical_reference_copies_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as temporary:
            managed = Path(temporary)
            (managed / "UnityEngine").mkdir()
            for path in (managed / "UnityEngine.CoreModule.dll",
                         managed / "UnityEngine/UnityEngine.CoreModule.dll"):
                path.write_bytes(b"identical path fixture")
            self.assertEqual(len(modular_references(managed, "UnityEngine")), 1)

    def test_precondition_failure_preserves_a_failed_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                compile_sources(root / "missing-editor", root / "missing-nunit.dll", root / "evidence")
            report = json.loads((root / "evidence/api-compile.json").read_text())
            self.assertEqual(report["status"], "Failed")
            self.assertEqual(report["checks"], [])
            self.assertFalse(report["native_unity_execution"])


class SystemReferenceTests(unittest.TestCase):
    def test_real_standard_and_framework_facade_paths_are_selected(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary)
            standard = data / "NetStandard/ref/2.1.0/netstandard.dll"
            facade = data / "NetStandard/compat/2.1.0/shims/netfx/mscorlib.dll"
            for path in (standard, facade):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"path-selection fixture, not a loadable DLL")
            self.assertEqual({p.name for p in system_references(data)},
                             {"netstandard.dll", "mscorlib.dll"})

    def test_missing_framework_facade_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary)
            path = data / "NetStandard/ref/2.1.0/netstandard.dll"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"path fixture")
            with self.assertRaisesRegex(ValueError, "facade"):
                system_references(data)

    def test_missing_standard_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "Standard 2.1"):
                system_references(Path(temporary))


class _AssemblyFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "unity/Assets").mkdir(parents=True)
        (self.root / "dotnet/src").mkdir(parents=True)

    def assembly(self, relative, name, references=(), test=False, pure=False, editor=False):
        directory = self.root / relative
        directory.mkdir(parents=True, exist_ok=True)
        data = {"name": name, "references": list(references), "noEngineReferences": pure,
                "includePlatforms": ["Editor"] if editor else [], "precompiledReferences": ["nunit.framework.dll"] if test else [],
                "optionalUnityReferences": ["TestAssemblies"] if test else []}
        (directory / (name + ".asmdef")).write_text(json.dumps(data))
        source = directory / (name.split(".")[-1] + ".cs")
        source.write_text("// source-ownership fixture; never compiled")
        return directory, source


class AssemblyGraphTests(_AssemblyFixture):
    def test_nested_editor_and_tests_have_their_own_sources(self):
        outer, source = self.assembly("unity/Assets/Feature", "CriticalShift.Feature")
        _, editor = self.assembly("unity/Assets/Feature/Editor", "CriticalShift.Feature.Editor", ["CriticalShift.Feature"], editor=True)
        _, tests = self.assembly("unity/Assets/Feature/Tests", "CriticalShift.Feature.Tests", ["CriticalShift.Feature"], test=True)
        groups = discover_assemblies(self.root)
        self.assertEqual(groups["CriticalShift.Feature"]["sources"], [source])
        self.assertEqual(groups["CriticalShift.Feature.Editor"]["sources"], [editor])
        self.assertEqual(groups["CriticalShift.Feature.Tests"]["sources"], [tests])

    def test_unowned_sources_cannot_disappear_from_the_compile_plan(self):
        self.assembly("dotnet/src/Rules", "CriticalShift.Rules", pure=True)
        (self.root / "unity/Assets/Unowned.cs").write_text("// must not escape")
        with self.assertRaisesRegex(ValueError, "Unowned"):
            discover_assemblies(self.root)

    def test_duplicate_names_and_conditional_boundaries_are_rejected(self):
        self.assembly("unity/Assets/A", "CriticalShift.Duplicate")
        directory, _ = self.assembly("unity/Assets/B", "CriticalShift.Duplicate")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            discover_assemblies(self.root)
        path = directory / "CriticalShift.Duplicate.asmdef"
        data = json.loads(path.read_text())
        data.update(name="CriticalShift.Conditional", defineConstraints=["UNVERIFIED_DEFINE"])
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "conditional"):
            discover_assemblies(self.root)

    def test_declared_graph_orders_dependencies_before_consumers_and_tests_last(self):
        self.assembly("dotnet/src/ZRules", "CriticalShift.ZRules", pure=True)
        self.assembly("dotnet/src/AApplication", "CriticalShift.AApplication", ["CriticalShift.ZRules"], pure=True)
        self.assembly("unity/Assets/Adapter", "CriticalShift.Adapter", ["CriticalShift.AApplication"])
        self.assembly("unity/Assets/Editor", "CriticalShift.Editor", ["CriticalShift.Adapter"], editor=True)
        self.assembly("unity/Assets/Tests", "CriticalShift.Tests", ["CriticalShift.Adapter"], test=True)
        self.assertEqual(topological_order(discover_assemblies(self.root)),
                         ["CriticalShift.ZRules", "CriticalShift.AApplication", "CriticalShift.Adapter", "CriticalShift.Editor", "CriticalShift.Tests"])

    def test_test_assemblies_flag_rejects_an_explicit_duplicate_runner(self):
        for reference in ("UnityEngine.TestRunner", "UnityEditor.TestRunner"):
            with self.subTest(reference=reference):
                self.assembly("unity/Assets/Tests", "CriticalShift.Tests", [reference], test=True)
                with self.assertRaisesRegex(ValueError, "duplicates the implicit TestAssemblies reference"):
                    discover_assemblies(self.root)

    def test_editor_platform_rejects_an_explicit_duplicate_runner_without_test_flags(self):
        for reference in ("UnityEngine.TestRunner", "UnityEditor.TestRunner"):
            with self.subTest(reference=reference):
                self.assembly("unity/Assets/Editor", "CriticalShift.Editor", [reference], editor=True)
                with self.assertRaisesRegex(ValueError, "duplicates the implicit Editor platform reference"):
                    discover_assemblies(self.root)

    def test_missing_dependencies_and_cycles_block_before_compilation(self):
        directory, _ = self.assembly("unity/Assets/A", "CriticalShift.A", ["CriticalShift.Missing"])
        with self.assertRaisesRegex(ValueError, "Unknown"):
            topological_order(discover_assemblies(self.root))
        path = directory / "CriticalShift.A.asmdef"
        data = json.loads(path.read_text())
        data["references"] = ["CriticalShift.B"]
        path.write_text(json.dumps(data))
        self.assembly("unity/Assets/B", "CriticalShift.B", ["CriticalShift.A"])
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            topological_order(discover_assemblies(self.root))

    def test_production_cannot_gain_test_dependencies(self):
        self.assembly("unity/Assets/Production", "CriticalShift.Production", ["CriticalShift.Tests"])
        self.assembly("unity/Assets/Tests", "CriticalShift.Tests", test=True)
        with self.assertRaisesRegex(ValueError, "production assembly"):
            topological_order(discover_assemblies(self.root))

    def test_missing_and_conflicting_test_runner_caches_remain_explicit(self):
        selected, missing = bundled_test_references(self.root)
        self.assertFalse(selected)
        self.assertIn("UnityEngine.TestRunner", missing)
        for template, content in (("A", b"first binary path fixture"), ("B", b"different binary path fixture")):
            path = self.root / "Resources/PackageManager/ProjectTemplates/libcache" / template / "ScriptAssemblies/UnityEngine.TestRunner.dll"
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
        selected, missing = bundled_test_references(self.root)
        self.assertNotIn("UnityEngine.TestRunner", selected)
        self.assertIn("conflicting", missing["UnityEngine.TestRunner"])

    def test_identical_test_runner_copies_are_selected_without_leaking_into_engine_references(self):
        managed = self.root / "Managed"
        managed.mkdir()
        (managed / "UnityEngine.CoreModule.dll").write_bytes(b"path selection only")
        path = managed / "UnityEngine.TestRunner.dll"
        path.write_bytes(b"identical runner path fixture")
        second = self.root / "Resources/PackageManager/ProjectTemplates/libcache/A/ScriptAssemblies/UnityEngine.TestRunner.dll"
        second.parent.mkdir(parents=True)
        second.write_bytes(path.read_bytes())
        selected, _ = bundled_test_references(self.root)
        self.assertEqual(selected["UnityEngine.TestRunner"], path)
        self.assertEqual([item.name for item in modular_references(managed, "UnityEngine")], ["UnityEngine.CoreModule.dll"])


class SupplementaryCompileEvidenceTests(_AssemblyFixture):
    """Compiler orchestration fixtures: every compiler/identity call is mocked, no fixture DLL is loaded."""
    def prepare(self, stack, missing_runner=False, fail=False):
        runtime = self.root
        self.assembly("dotnet/src/Rules", "CriticalShift.Rules", pure=True)
        self.assembly("unity/Assets/Adapter", "CriticalShift.Adapter", ["CriticalShift.Rules"])
        self.assembly("unity/Assets/Editor", "CriticalShift.Adapter.Editor", ["CriticalShift.Adapter"], editor=True)
        self.assembly("unity/Assets/Tests", "CriticalShift.Tests", ["CriticalShift.Adapter"], test=True)
        profile = {"editor": "6000.4.3f1", "revision": "39d1a88d4dd1", "supplementaryDotnetSdk": "8.0.423"}
        (runtime / "toolchain.json").write_text(json.dumps(profile))
        editor = self.root / "fake-editor"
        data = editor / "Editor/Data"
        for relative in ("NetStandard/ref/2.1.0/netstandard.dll", "NetStandard/compat/2.1.0/shims/netfx/mscorlib.dll",
                         "Managed/UnityEngine.CoreModule.dll", "Managed/UnityEditor.CoreModule.dll"):
            path = data / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"path-selection fixture; compiler is mocked")
        for executable in ("Unity.exe", "Unity"):
            (editor / "Editor" / executable).write_bytes(b"not an executable")
        if not missing_runner:
            (data / "Managed/UnityEngine.TestRunner.dll").write_bytes(b"path selection fixture")
            (data / "Managed/UnityEditor.TestRunner.dll").write_bytes(b"path selection fixture")
        nunit = self.root / "nunit.framework.dll"
        nunit.write_bytes(b"path-selection fixture")
        sdk = self.root / "sdk"
        compiler = sdk / "8.0.423/Roslyn/bincore/csc.dll"
        compiler.parent.mkdir(parents=True)
        compiler.write_bytes(b"not executable; compiler calls are mocked")
        stack.enter_context(patch.object(api_compile, "ROOT", runtime))
        stack.enter_context(patch.object(api_compile, "checkout_revision", return_value="fixture-checkout"))
        identity = stack.enter_context(patch.object(api_compile, "inspect_editor", return_value={"status": "Verified"}))
        stack.enter_context(patch.object(api_compile, "check", return_value={"status": "Passed", "check": "mocked-source"}))
        stack.enter_context(patch.object(api_compile.subprocess, "check_output", return_value=f"8.0.423 [{sdk}]\n"))

        def build(command, **unused):
            self.assertIn("-noconfig", command)
            response = Path(command[-1][1:]).read_text()
            self.assertNotIn("-noconfig", response)
            destination = Path(re.search(r'^"-out:(.+)"$', response, re.M)[1])
            if not fail:
                destination.write_bytes(b"mock compiler output, not a usable assembly")
            return subprocess.CompletedProcess(command, 1 if fail else 0, "deliberate compile failure" if fail else "", "")

        execution = stack.enter_context(patch.object(api_compile.subprocess, "run", side_effect=build))
        return editor, nunit, runtime / "out/api-check", execution, identity

    def test_all_owned_production_and_test_groups_reach_the_compiler_in_graph_order(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, identity = self.prepare(stack)
            report = compile_sources(editor, nunit, output, "pinned-dotnet-host")
        self.assertEqual((report["status"], report["production_status"], execution.call_count), ("Passed", "Passed", 4))
        self.assertEqual([item["assembly"] for item in report["checks"]],
                         ["CriticalShift.Rules", "CriticalShift.Adapter", "CriticalShift.Adapter.Editor", "CriticalShift.Tests"])
        identity.assert_called_once()
        self.assertFalse(report["native_unity_execution"])
        self.assertTrue(report["source_unchanged"])
        self.assertTrue(all(item["output_sha256"] for item in report["checks"]))

    def test_missing_real_test_runner_blocks_affected_editor_and_test_compilation(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, _ = self.prepare(stack, missing_runner=True)
            report = compile_sources(editor, nunit, output)
        self.assertEqual((report["status"], report["production_status"], execution.call_count), ("Blocked", "Blocked", 2))
        self.assertEqual(report["checks"][-2]["status"], "Blocked")
        self.assertEqual(report["checks"][-1]["status"], "Blocked")
        self.assertIn("No real test-runner binary", report["checks"][-1]["reason"])

    def test_implicit_runner_is_recorded_and_passed_to_the_compiler_once(self):
        with ExitStack() as stack:
            editor, nunit, output, _, _ = self.prepare(stack)
            report = compile_sources(editor, nunit, output)
        record = report["checks"][-1]
        self.assertNotIn("UnityEngine.TestRunner", record["declared_references"])
        self.assertEqual(record["implicit_references"], ["UnityEngine.TestRunner", "UnityEditor.TestRunner"])
        response = (output / record["compiler_response"]).read_text()
        for provenance in record["implicit_reference_provenance"]:
            self.assertEqual(provenance["source"], "optionalUnityReferences:TestAssemblies")
            self.assertEqual(len(provenance["sha256"]), 64)
            self.assertEqual(response.count(provenance["assembly"] + ".dll"), 1)
            self.assertIn(provenance["binary"], record["references"])

    def test_missing_implicit_editor_runner_blocks_editor_and_test_compilation(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, _ = self.prepare(stack)
            (editor / "Editor/Data/Managed/UnityEditor.TestRunner.dll").unlink()
            report = compile_sources(editor, nunit, output)
        self.assertEqual((report["status"], report["production_status"], execution.call_count), ("Blocked", "Blocked", 2))
        self.assertEqual(report["checks"][-2]["status"], "Blocked")
        self.assertEqual(report["checks"][-1]["status"], "Blocked")
        self.assertIn("UnityEditor.TestRunner", report["unavailable_test_references"])

    def test_editor_platform_alone_supplies_both_real_runner_references(self):
        with ExitStack() as stack:
            editor, nunit, output, _, _ = self.prepare(stack)
            report = compile_sources(editor, nunit, output)
        record = next(item for item in report["checks"] if item["assembly"] == "CriticalShift.Adapter.Editor")
        self.assertEqual(record["kind"], "production")
        self.assertEqual(record["implicit_references"], ["UnityEngine.TestRunner", "UnityEditor.TestRunner"])
        response = (output / record["compiler_response"]).read_text()
        for provenance in record["implicit_reference_provenance"]:
            self.assertEqual(provenance["source"], "includePlatforms:Editor")
            self.assertEqual(response.count(provenance["assembly"] + ".dll"), 1)

    def test_a_real_compile_failure_retains_first_failure_and_unexecuted_groups(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, _ = self.prepare(stack, fail=True)
            with self.assertRaisesRegex(RuntimeError, "CriticalShift.Rules"):
                compile_sources(editor, nunit, output)
        report = json.loads((output / "api-compile.json").read_text())
        self.assertEqual((report["status"], report["production_status"], execution.call_count), ("Failed", "Failed", 1))
        self.assertEqual([item["status"] for item in report["checks"]], ["Failed", "NotRun", "NotRun", "NotRun"])
        self.assertIn("deliberate compile failure", (output / report["checks"][0]["log"]).read_text())

    def test_unverified_editor_identity_stops_before_any_compiler_invocation(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, identity = self.prepare(stack)
            identity.return_value = {"status": "NativeLogRequired"}
            with self.assertRaisesRegex(ValueError, "verified Editor file identity"):
                compile_sources(editor, nunit, output)
        report = json.loads((output / "api-compile.json").read_text())
        self.assertEqual((report["status"], report["checks"]), ("Blocked", []))
        execution.assert_not_called()

    def test_compiler_timeout_is_a_recorded_failure_with_response_and_log(self):
        with ExitStack() as stack:
            editor, nunit, output, execution, _ = self.prepare(stack)
            execution.side_effect = subprocess.TimeoutExpired("pinned-dotnet-host", 120)
            with self.assertRaises(subprocess.TimeoutExpired):
                compile_sources(editor, nunit, output)
        report = json.loads((output / "api-compile.json").read_text())
        self.assertEqual(report["checks"][0]["status"], "Failed")
        self.assertTrue((output / report["checks"][0]["compiler_response"]).is_file())
        self.assertTrue((output / report["checks"][0]["log"]).is_file())
        self.assertTrue(all(item["status"] == "NotRun" for item in report["checks"][1:]))


class BundledNUnitSelectionTests(unittest.TestCase):
    def test_matching_editor_bundle_records_exact_reference_and_provenance_without_network(self):
        with tempfile.TemporaryDirectory() as temporary, patch("acquire_toolchain.urllib.request.urlopen") as network:
            root = Path(temporary)
            package = root / "Editor/Data/Resources/PackageManager/BuiltInPackages/com.unity.ext.nunit"
            package.mkdir(parents=True)
            (package / "package.json").write_text(json.dumps({"name": "com.unity.ext.nunit", "version": "2.0.5"}))
            binary = package / "net40/unity-custom/nunit.framework.dll"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"reference-selection fixture only; never loaded")
            lock = root / "packages-lock.json"
            lock.write_text(json.dumps({"dependencies": {"com.unity.ext.nunit": {"version": "2.0.5", "source": "builtin"}}}))
            selected, evidence = bundled_nunit(root, lock)
            self.assertEqual(selected, binary)
            self.assertEqual((evidence["version"], evidence["source"]), ("2.0.5", "pinned-editor-builtin"))
            self.assertEqual(len(evidence["dll_sha256"]), 64)
            self.assertEqual(len(evidence["descriptor_sha256"]), 64)
            network.assert_not_called()

    def test_obsolete_bundle_or_missing_dll_cannot_fall_back_to_a_registry_download(self):
        with tempfile.TemporaryDirectory() as temporary, patch("acquire_toolchain.urllib.request.urlopen") as network:
            root = Path(temporary)
            package = root / "Editor/Data/Resources/PackageManager/BuiltInPackages/com.unity.ext.nunit"
            package.mkdir(parents=True)
            descriptor = package / "package.json"
            descriptor.write_text(json.dumps({"name": "com.unity.ext.nunit", "version": "2.0.3"}))
            lock = root / "packages-lock.json"
            lock.write_text(json.dumps({"dependencies": {"com.unity.ext.nunit": {"version": "2.0.5", "source": "builtin"}}}))
            with self.assertRaisesRegex(ValueError, "differs from the selected project lock"):
                bundled_nunit(root, lock)
            descriptor.write_text(json.dumps({"name": "com.unity.ext.nunit", "version": "2.0.5"}))
            with self.assertRaisesRegex(ValueError, "exactly one real NUnit"):
                bundled_nunit(root, lock)
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
