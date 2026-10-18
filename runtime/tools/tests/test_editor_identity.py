import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from editor_identity import inspect_editor, validate_windows_identity
from evidence import EvidenceError


class EditorIdentityTests(unittest.TestCase):
    profile = {"editor": "6000.4.3f1", "revision": "39d1a88d4dd1"}
    metadata = {"ProductName": "Unity", "ProductVersion": "6000.4.3f1_39d1a88d4dd1", "FileVersion": "6000.4.3.3789224"}

    def test_exact_version_and_revision_are_required(self):
        result = validate_windows_identity(self.metadata, self.profile)
        self.assertEqual(result["status"], "Verified")
        self.assertEqual(result["product_version"], self.metadata["ProductVersion"])

    def test_wrong_version_revision_vendor_or_shape_is_rejected(self):
        values = [None, [], {}, dict(self.metadata, ProductName="Other"),
                  dict(self.metadata, ProductVersion="6000.6.2f1_other"),
                  dict(self.metadata, ProductVersion="6000.4.3f1_wrongrevision")]
        for value in values:
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                validate_windows_identity(value, self.profile)

    def test_inspection_reads_a_literal_path_without_executing_the_editor(self):
        editor = Path("Editor with spaces ' and $ characters/Unity.exe").resolve()
        with patch("editor_identity.sys.platform", "win32"), patch("editor_identity.subprocess.run") as execute:
            execute.return_value = subprocess.CompletedProcess([], 0, json.dumps(self.metadata), "")
            self.assertEqual(inspect_editor(editor, self.profile)["status"], "Verified")
            arguments, options = execute.call_args
            self.assertEqual(arguments[0][0], "powershell.exe")
            self.assertNotIn(str(editor), arguments[0])
            self.assertIn("-LiteralPath $env:CS_UNITY_EDITOR_FILE", arguments[0][-1])
            self.assertEqual(options["env"]["CS_UNITY_EDITOR_FILE"], str(editor))

    def test_unsupported_host_does_not_claim_a_file_identity_pass(self):
        with patch("editor_identity.sys.platform", "linux"), patch("editor_identity.subprocess.run") as execute:
            result = inspect_editor(Path("Unity"), self.profile)
            self.assertEqual(result["status"], "NativeLogRequired")
            execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
