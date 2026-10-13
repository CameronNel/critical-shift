import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normal_bake_pixels import neutralize_empty


class NormalBakePixelsTests(unittest.TestCase):
    def test_only_invalid_black_rgb_changes_and_alpha_is_retained(self):
        pixels = np.array([[0, 0, 0, 1], [.5, .5, 1, .7], [0, .5, .5, 1],
                           [1e-7, 0, 0, .3], [0, 0, 0, 0]], dtype=np.float32)
        before = pixels.copy()
        self.assertEqual(neutralize_empty(pixels), 2)
        np.testing.assert_array_equal(pixels[[1, 2, 3]], before[[1, 2, 3]])
        np.testing.assert_array_equal(pixels[:, 3], before[:, 3])
        np.testing.assert_array_equal(pixels[[0, 4], :3], [[.5, .5, 1], [.5, .5, 1]])
        self.assertEqual(neutralize_empty(pixels), 0)
