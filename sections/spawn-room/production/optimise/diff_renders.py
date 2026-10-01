"""python diff_renders.py <before_dir> <after_dir> <out_dir>  - per-camera pixel difference and a before|after|diff montage"""
import os
import sys

import numpy as np
from PIL import Image

b, a, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
rows = []
for name in sorted(os.listdir(b)):
    if not name.endswith(".png") or not os.path.exists(os.path.join(a, name)):
        continue
    x = np.asarray(Image.open(os.path.join(b, name)).convert("RGB"), dtype=np.float32) / 255
    y = np.asarray(Image.open(os.path.join(a, name)).convert("RGB"), dtype=np.float32) / 255
    d = np.abs(x - y).max(axis=2)
    mean, p99, frac = float(d.mean()), float(np.percentile(d, 99)), float((d > 0.08).mean())
    print("%-24s mean %.4f  p99 %.3f  pixels differing by more than 8%%: %.3f%%" % (name[:-4], mean, p99, frac * 100))
    heat = np.clip(d * 6, 0, 1)
    im = np.concatenate([x, y, np.stack([heat] * 3, axis=2)], axis=1)
    Image.fromarray((im * 255).astype(np.uint8)).save(os.path.join(out, name))
