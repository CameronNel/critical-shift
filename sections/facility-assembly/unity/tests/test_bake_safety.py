"""Exercise bake lifecycle and complete geometry checks without running Blender.

Run: python -m unittest discover -s sections/facility-assembly/unity/tests -v
These use the real script functions with controlled Blender/mesh boundaries;
they do not establish native baking, FBX import or visual acceptance.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def function_source(file, name, namespace):
    tree = ast.parse((ROOT / file).read_text())
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), file, "exec"), namespace)
    return namespace[name]


class BakeSafetyTests(unittest.TestCase):
    def bounds(self, coordinates, matrix=None):
        problems = []
        namespace = {"np": np, "fail": problems.append}
        bounds = function_source("bake_check.py", "bounds", namespace)

        class Vertices:
            def __len__(self): return len(coordinates)
            def foreach_get(self, attribute, destination):
                if attribute != "co": raise AssertionError(attribute)
                destination[:] = np.asarray(coordinates).ravel()

        obj = SimpleNamespace(name="round-trip mesh", data=SimpleNamespace(vertices=Vertices()),
                              matrix_world=np.eye(4) if matrix is None else matrix)
        return bounds([obj]), problems

    def test_late_nan_and_infinity_cannot_hide_after_the_first_thousand_vertices(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.subTest(value=value):
                coordinates = np.zeros((1001, 3)); coordinates[-1, 2] = value
                _, problems = self.bounds(coordinates)
                self.assertEqual(len(problems), 1)
                self.assertIn("non-finite vertex positions", problems[0])

    def test_nonfinite_object_transform_cannot_produce_accepted_world_bounds(self):
        matrix = np.eye(4); matrix[0, 3] = np.inf
        _, problems = self.bounds([[0, 0, 0], [1, 1, 1]], matrix)
        self.assertEqual(len(problems), 1)
        self.assertIn("non-finite world positions", problems[0])

    def test_valid_complete_geometry_keeps_its_transformed_bounds(self):
        matrix = np.eye(4); matrix[:3, 3] = [2, 3, 4]
        (low, high), problems = self.bounds([[0, -1, 0], [1, 2, 3]], matrix)
        np.testing.assert_allclose(low, [2, 2, 4]); np.testing.assert_allclose(high, [3, 5, 7])
        self.assertEqual(problems, [])

    def test_all_stage_reopens_prepared_objects_after_destructive_bake_join(self):
        class ObjectHandle:
            def __init__(self, name): self.label, self.removed = name, False
            @property
            def name(self):
                if self.removed: raise ReferenceError("StructRNA has been removed")
                return self.label

        original = [ObjectHandle("part A"), ObjectHandle("part B")]
        original[1].removed = True  # Joining during bake deletes the non-active object.
        restored = [ObjectHandle("part A"), ObjectHandle("part B")]
        context = SimpleNamespace(scene="old scene", view_layer="old layer")
        calls = []

        def reopen(filepath):
            self.assertEqual(filepath, "_work.blend")
            calls.append("open"); context.scene, context.view_layer = "prepared scene", "prepared layer"

        def collect():
            self.assertEqual(namespace["vl"], "prepared layer")
            calls.append("collect"); return restored, ["prepared material"]

        namespace = {"bpy": SimpleNamespace(ops=SimpleNamespace(wm=SimpleNamespace(open_mainfile=reopen)), context=context),
                     "WORK": "_work.blend", "assert_isolated": lambda stage: calls.append(stage), "collect": collect,
                     "STAGE": "all", "objs": original, "step": lambda *args, **kwargs: None}
        function_source("bake_room.py", "restore_prepared_geometry", namespace)
        # Execute the real all-stage handoff, including its call ordering.
        tree = ast.parse((ROOT / "bake_room.py").read_text())
        handoff = next(node for node in ast.walk(tree) if isinstance(node, ast.If) and
                       isinstance(node.test, ast.Compare) and ast.unparse(node.test) == "STAGE == 'all'" and
                       any(isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and
                           call.func.id == "restore_prepared_geometry" for call in ast.walk(node)))
        exec(compile(ast.Module(body=[handoff], type_ignores=[]), "bake_room.py", "exec"), namespace)
        self.assertEqual([obj.name for obj in namespace["objs"]], ["part A", "part B"])
        self.assertEqual(namespace["mats"], ["prepared material"])
        self.assertEqual(calls, ["open", "finish", "collect"])


if __name__ == "__main__":
    unittest.main()
