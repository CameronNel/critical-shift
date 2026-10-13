"""A changed assembly must fail before any Blender invocation or delivery mutation."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_mine


class MineRefreshGuardTests(unittest.TestCase):
    def test_changed_uv_exporter_rejects_source_identical_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "runtime/tools"
            tools.mkdir(parents=True)
            for name in prepare_mine.RECIPE_FILES:
                (tools/name).write_text("original conversion recipe")
            config = {"sources":[{"path":"unchanged.blend","sha256":"a"*64}]}
            recipe = prepare_mine.export_recipe(root,"Blender 5.2.2 LTS",True)
            cached = {"method":"source-recipe-v2","size":4096,"sources":config["sources"],"exportRecipe":recipe}
            prepare_mine.validate_cache(cached,config,4096,recipe)
            (tools/"mine_delivery_uv.py").write_text("changed UV packing")
            changed = prepare_mine.export_recipe(root,"Blender 5.2.2 LTS",True)
            with self.assertRaisesRegex(ValueError,"exporter/UV recipe changed"):
                prepare_mine.validate_cache(cached,config,4096,changed)

    def test_cache_cannot_change_batching_or_blender_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "runtime/tools"
            tools.mkdir(parents=True)
            for name in prepare_mine.RECIPE_FILES:
                (tools/name).write_text("original conversion recipe")
            config = {"sources":[]}
            recipe = prepare_mine.export_recipe(root,"Blender 5.2.2 LTS",True)
            cached = {"method":"source-recipe-v2","size":4096,"sources":[],"exportRecipe":recipe}
            for version,batched in (("Blender other version",True),("Blender 5.2.2 LTS",False)):
                with self.assertRaisesRegex(ValueError,"exporter/UV recipe changed"):
                    prepare_mine.validate_cache(cached,config,4096,prepare_mine.export_recipe(root,version,batched))

    def test_cache_cannot_replace_generated_source_with_same_room_pins(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "runtime/tools"
            tools.mkdir(parents=True)
            for name in prepare_mine.RECIPE_FILES:
                (tools/name).write_text("unchanged conversion recipe")
            config = {"sources":[]}
            original = prepare_mine.export_recipe(root,"Blender 5.2.2 LTS",True,"a"*64)
            cached = {"method":"source-recipe-v2","size":4096,"sources":[],"exportRecipe":original}
            changed = prepare_mine.export_recipe(root,"Blender 5.2.2 LTS",True,"b"*64)
            with self.assertRaisesRegex(ValueError,"exporter/UV recipe changed"):
                prepare_mine.validate_cache(cached,config,4096,changed)

    def reject_changed_source(self, changed_builder):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            builder_path = "sections/facility-assembly/combined/build_combined_map.py"
            other_path = "sections/facility-assembly/sources/front-end-area/front_end_area.blend"
            builder = b"pinned assembly builder"
            config = {"map_commit": "pin", "sources": [
                {"path": builder_path, "sha256": hashlib.sha256(builder).hexdigest()},
                {"path": other_path, "sha256": "a" * 64},
            ]}
            scratch = root / "runtime/out/spawn-export-source"
            scratch.mkdir(parents=True)
            (scratch / "map-config.json").write_text(json.dumps(config))
            output = root / "runtime/unity/Assets/CriticalShift/Generated/Spawn"
            output.mkdir(parents=True)
            manifest = output / "map-bindings.json"
            manifest.write_text(json.dumps({"mapCommit": "pin"}))
            before = manifest.read_bytes()

            def git_show(command, **kwargs):
                if command[-1].endswith(builder_path):
                    return b"changed assembly" if changed_builder else builder
                return ("version https://git-lfs.github.com/spec/v1\n"
                        "oid sha256:" + "b" * 64 + "\nsize 100\n").encode()

            args = SimpleNamespace(map_ref="main", blender="must-not-run", size=4096)
            with patch.object(prepare_mine, "ROOT", root), patch.object(prepare_mine, "sha", return_value="current"), \
                    patch.object(prepare_mine.subprocess, "check_output", side_effect=git_show), \
                    patch.object(prepare_mine.subprocess, "run") as blender_run:
                expected = "Assembly builder changed" if changed_builder else "Source changed"
                with self.assertRaisesRegex(ValueError, expected):
                    prepare_mine.prepare(args)
                blender_run.assert_not_called()
            self.assertEqual(before, manifest.read_bytes())
            self.assertFalse((root / "runtime/out/mine-bake-audit").exists())

    def test_changed_builder_cannot_modify_the_prepared_map(self):
        self.reject_changed_source(True)

    def test_changed_neighbor_room_cannot_modify_the_prepared_map(self):
        self.reject_changed_source(False)
