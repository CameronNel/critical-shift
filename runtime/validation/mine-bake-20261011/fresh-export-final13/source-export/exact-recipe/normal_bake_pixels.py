"""Keep uncovered baked normal texels neutral, including at mip/chart edges."""
import numpy as np


def neutralize_empty(pixels):
    """Modify only invalid, exactly black RGB normals; retain alpha and all others."""
    empty = np.all(pixels[:, :3] == 0, axis=1)
    pixels[empty, :3] = (.5, .5, 1)
    return int(np.count_nonzero(empty))
