"""A staged room must keep its runtime references when adopted into Unity."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import prepare_player
import prepare_spawn


class DerivativeMetadataTests(unittest.TestCase):
    def test_external_staging_keeps_canonical_file_and_folder_guids(self):
        with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as staging:
            root=Path(repo)
            canonical=root/"runtime/unity/Assets/CriticalShift/Generated/Spawn"
            staged=Path(staging)/"delivery"
            for output in [canonical,staged]:
                (output/"Surfaces").mkdir(parents=True)
                (output/"Surfaces/albedo.png").write_bytes(b"metadata identity fixture")
            with patch.object(prepare_player,"ROOT",root/"runtime"),patch.object(prepare_spawn,"ROOT",root):
                for relative in ["Surfaces","Surfaces/albedo.png"]:
                    prepare_player.meta(canonical/relative)
                    prepare_spawn.derivative_meta(staged/relative,staged)
                    self.assertEqual(Path(str(canonical/relative)+".meta").read_bytes(),
                                     Path(str(staged/relative)+".meta").read_bytes())
