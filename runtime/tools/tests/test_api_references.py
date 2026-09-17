"""Path-selection tests only; fixture DLL bytes are never used as API stubs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api_compile import compile_sources, modular_references, system_references


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


if __name__ == "__main__":
    unittest.main()
