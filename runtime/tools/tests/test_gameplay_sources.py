"""Source-package safety fixtures; no Editor, compiler or asset import is launched."""
import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_source import RUNTIME, gameplay_sources
from evidence import EvidenceError
from run_foundation import fingerprint, source_files


class GameplaySourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "dotnet/src"
        shutil.copytree(RUNTIME / "dotnet/src", self.package)
        manifest = self.root / "unity/Packages/manifest.json"
        manifest.parent.mkdir(parents=True)
        shutil.copy2(RUNTIME / "unity/Packages/manifest.json", manifest)
        shutil.copy2(RUNTIME / "toolchain.json", self.root / "toolchain.json")

    def change_definition(self, name, mutate):
        path = self.package / name / (name + ".asmdef")
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data))

    def test_canonical_package_has_matching_assembly_graph(self):
        self.assertEqual(gameplay_sources(self.root), self.package)

    def test_peer_domain_reference_is_rejected(self):
        self.change_definition("CriticalShift.Features.Workers.Domain",
                               lambda data: data["references"].append("CriticalShift.Features.Session.Domain"))
        with self.assertRaises(ValueError):
            gameplay_sources(self.root)

    def test_unity_engine_reference_is_rejected(self):
        self.change_definition("CriticalShift.Application",
                               lambda data: data.update(noEngineReferences=False))
        with self.assertRaises(ValueError):
            gameplay_sources(self.root)

    def test_precompiled_plugin_escape_is_rejected(self):
        self.change_definition("CriticalShift.Application",
                               lambda data: data["precompiledReferences"].append("DuplicateGameplay.dll"))
        with self.assertRaises(ValueError):
            gameplay_sources(self.root)

    def test_generated_output_cannot_enter_source_package(self):
        output = self.package / "CriticalShift.Application/obj"
        output.mkdir()
        (output / "Generated.cs").write_text("// must not be imported")
        with self.assertRaises(ValueError):
            gameplay_sources(self.root)
        with self.assertRaises(EvidenceError):
            source_files(self.root)

    def test_output_configuration_cannot_write_binaries_into_unity_package(self):
        path = self.package / "Directory.Build.props"
        tree = ET.parse(path)
        tree.find(".//BaseOutputPath").text = "bin/"
        tree.write(path)
        with self.assertRaises(ValueError):
            gameplay_sources(self.root)

    def test_canonical_sources_are_included_in_disposable_evidence(self):
        path = self.package / "CriticalShift.Application/WorldSession.cs"
        self.assertIn(path, source_files(self.root))
        original = fingerprint(self.root)
        path.write_text(path.read_text() + "\n// fixture source mutation\n")
        self.assertNotEqual(original, fingerprint(self.root))

    def test_missing_package_cannot_appear_as_clean_import_input(self):
        (self.package / "package.json").unlink()
        with self.assertRaises(EvidenceError):
            source_files(self.root)


if __name__ == "__main__":
    unittest.main()
