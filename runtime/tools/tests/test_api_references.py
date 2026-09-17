"""Path-selection tests only; fixture DLL bytes are never used as API stubs."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api_compile import modular_references


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


if __name__ == "__main__":
    unittest.main()
