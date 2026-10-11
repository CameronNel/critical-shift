"""Guard numeric texture channels and asset identity before native mine import."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_mine import texture_metadata


class MineTextureMetadataTests(unittest.TestCase):
    def test_new_import_keeps_guid_and_numeric_smoothness_alpha(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            atlas = {}
            for channel in ("albedo", "normal", "metallicSmoothness"):
                path = output / (channel + ".png")
                path.write_bytes(b"metadata fixture")
                Path(str(path)+".meta").write_text("fileFormatVersion: 2\nguid: " + "a"*32 + "\nDefaultImporter: {}\n")
                atlas[channel] = {"file": path.name, "size": 4096}
            texture_metadata(output, {"atlases": [atlas]})
            for channel,record in atlas.items():
                actual = Path(str(output/record["file"])+".meta").read_text()
                self.assertIn("guid: " + "a"*32, actual)
                self.assertIn("alphaUsage: 1", actual)
                self.assertIn("textureFormat: " + ("26" if channel == "normal" else "25"), actual)
                self.assertIn("sRGBTexture: " + ("1" if channel == "albedo" else "0"), actual)

    def test_existing_native_settings_are_not_reset(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            original = "fileFormatVersion: 2\nguid: " + "b"*32 + "\nTextureImporter:\n  userData: retained-native-settings\n"
            atlas = {}
            for channel in ("albedo", "normal", "metallicSmoothness"):
                path = output / (channel + ".png")
                Path(str(path)+".meta").write_text(original)
                atlas[channel] = {"file": path.name, "size": 4096}
            texture_metadata(output, {"atlases": [atlas]})
            for record in atlas.values():
                self.assertEqual(Path(str(output/record["file"])+".meta").read_text(), original)
