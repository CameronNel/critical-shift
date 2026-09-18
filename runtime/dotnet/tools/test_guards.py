"""Negative controls for the actual file/graph/result checkers; uses only Python's standard library."""
from pathlib import Path
import copy
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from check_boundaries import validate as check, DOMAIN, SESSION, WORKERS, APPLICATION, MATERIALS, PRODUCTION, REACTOR, POWER, PROCESS, TESTS
from verify_results import validate as results

ROOT = Path(__file__).resolve().parents[1]


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "dotnet"
        self.root.mkdir()
        for relative in ("Application/ProcessLifetime.cs", "Tests/EditMode/ProcessLifetimeTests.cs"):
            source = ROOT.parent / "unity/Assets/CriticalShift" / relative
            target = self.root.parent / "unity/Assets/CriticalShift" / relative
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
        shutil.copytree(ROOT / "src", self.root / "src", ignore=shutil.ignore_patterns("bin", "obj"))
        shutil.copytree(ROOT / "tools" / "CriticalShift.Scenarios", self.root / "tools" / "CriticalShift.Scenarios", ignore=shutil.ignore_patterns("bin", "obj"))
        shutil.copytree(ROOT / "tests", self.root / "tests", ignore=shutil.ignore_patterns("bin", "obj"))

    def test_production_cannot_reference_materials_domain(self):
        path = self.root / PRODUCTION; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Materials.Domain/CriticalShift.Features.Materials.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_materials_cannot_reference_production_domain(self):
        path = self.root / MATERIALS; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Production.Domain/CriticalShift.Features.Production.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_reactor_cannot_reference_power_peer(self):
        path = self.root / REACTOR; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Power.Domain/CriticalShift.Features.Power.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_power_cannot_reference_reactor_peer(self):
        path = self.root / POWER; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Reactor.Domain/CriticalShift.Features.Reactor.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_external_link_cannot_be_changed_or_duplicated(self):
        for mode in ("replace", "duplicate", "conditional"):
            with self.subTest(mode=mode):
                path = self.root / PROCESS; original = path.read_bytes(); tree = ET.parse(path)
                item = tree.find(".//Compile")
                if mode == "replace": item.set("Include", "../../../arbitrary.cs")
                elif mode == "conditional": item.set("Condition", "'$(Configuration)' == 'Release'")
                else: tree.find("ItemGroup").append(copy.deepcopy(item))
                tree.write(path)
                self.assertTrue(any("Compile" in x for x in check(self.root)))
                path.write_bytes(original)

    def test_external_source_must_exist(self):
        (self.root.parent / "unity/Assets/CriticalShift/Application/ProcessLifetime.cs").unlink()
        self.assertTrue(any("canonical linked source" in x for x in check(self.root)))

    def test_process_project_cannot_discover_duplicate_sources(self):
        path = self.root / PROCESS; tree = ET.parse(path)
        tree.find(".//EnableDefaultCompileItems").text = "true"; tree.write(path)
        self.assertTrue(any("source discovery" in x for x in check(self.root)))

    def test_tests_cannot_link_second_process_copy(self):
        path = self.root / TESTS; tree = ET.parse(path)
        ET.SubElement(tree.find("ItemGroup"), "Compile", Include="../../copy.cs")
        tree.write(path)
        self.assertTrue(any("Compile" in x for x in check(self.root)))

    def test_clean_graph(self):
        self.assertEqual(check(self.root), [])

    def test_forbidden_actual_project_reference(self):
        path = self.root / DOMAIN
        tree = ET.parse(path)
        group = ET.SubElement(tree.getroot(), "ItemGroup")
        ET.SubElement(group, "ProjectReference", Include="../CriticalShift.Application/CriticalShift.Application.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_session_domain_cannot_reference_interaction_domain(self):
        path = self.root / SESSION; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Interaction.Domain/CriticalShift.Features.Interaction.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_domain_cannot_read_hidden_clock(self):
        (self.root / SESSION).parent.joinpath("ClockLeak.cs").write_text("class ClockLeak { object Now => System.DateTime.UtcNow; }")
        self.assertTrue(any("Hidden clock" in x for x in check(self.root)))

    def test_worker_domain_cannot_depend_on_session(self):
        path = self.root / WORKERS; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Session.Domain/CriticalShift.Features.Session.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_production_cannot_reference_scenario_runner(self):
        path = self.root / APPLICATION; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../../tools/CriticalShift.Scenarios/CriticalShift.Scenarios.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_package_leak(self):
        path = self.root / APPLICATION; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "PackageReference", Include="Unapproved.Sdk", Version="1.0")
        tree.write(path)
        self.assertTrue(any("package" in x for x in check(self.root)))

    def test_source_escape(self):
        (self.root / "Loose.cs").write_text("class Loose {}")
        self.assertTrue(any("unique project" in x for x in check(self.root)))

    def test_engine_leak(self):
        (self.root / DOMAIN).parent.joinpath("Leak.cs").write_text("using UnityEngine; class Leak {}")
        self.assertTrue(any("Forbidden engine" in x for x in check(self.root)))

    def fixture(self):
        xml = ET.Element("TestRun")
        entries = ET.SubElement(xml, "Results")
        ET.SubElement(entries, "UnitTestResult", testName="Example", testId="one", outcome="Passed")
        summary = ET.SubElement(xml, "ResultSummary", outcome="Completed")
        ET.SubElement(summary, "Counters", total="1", executed="1", passed="1", failed="0", notExecuted="0")
        return xml

    def run_result(self, xml, expected=None):
        path = self.root / "result.trx"; ET.ElementTree(xml).write(path)
        return results(path, {"Example": 1} if expected is None else expected)

    def test_positive_result(self):
        self.assertEqual(self.run_result(self.fixture())["passed"], 1)

    def test_zero_discovery(self):
        xml = self.fixture(); xml.find("Results").clear()
        with self.assertRaises(ValueError): self.run_result(xml)

    def test_failure_skip_and_timeout(self):
        for outcome in ("Failed", "NotExecuted", "Timeout"):
            with self.subTest(outcome=outcome):
                xml = self.fixture(); xml.find("Results/UnitTestResult").set("outcome", outcome)
                with self.assertRaises(ValueError): self.run_result(xml)

    def test_missing_expected_test(self):
        with self.assertRaises(ValueError): self.run_result(self.fixture(), {"Example": 1, "Missing": 1})

    def test_duplicate_result(self):
        xml = self.fixture(); xml.find("Results").append(copy.deepcopy(xml.find("Results/UnitTestResult")))
        with self.assertRaises(ValueError): self.run_result(xml)

    def test_counters_do_not_override_real_results(self):
        xml = self.fixture(); xml.find("ResultSummary/Counters").set("executed", "0")
        with self.assertRaises(ValueError): self.run_result(xml)

    def test_missing_and_malformed_results(self):
        path = self.root / "missing.trx"
        with self.assertRaises(FileNotFoundError): results(path, {"Example": 1})
        path.write_text("not xml")
        with self.assertRaises(ET.ParseError): results(path, {"Example": 1})

    def test_overall_error_cannot_hide_behind_passing_rows(self):
        xml = self.fixture(); xml.find("ResultSummary").set("outcome", "Failed")
        with self.assertRaises(ValueError): self.run_result(xml)

    def test_missing_overall_result(self):
        xml = self.fixture(); xml.remove(xml.find("ResultSummary"))
        with self.assertRaises(ValueError): self.run_result(xml)

    def test_empty_expected_manifest(self):
        with self.assertRaises(ValueError): self.run_result(self.fixture(), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
