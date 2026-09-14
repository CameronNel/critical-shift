"""Cold reopen renderer. Invoke with the saved .blend already opened by Blender."""
import argparse
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
ap = argparse.ArgumentParser()
ap.add_argument("--revision", required=True)
ap.add_argument("--render", default="all")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--width", type=int, default=1920)
ap.add_argument("--height", type=int, default=1080)
p = ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])
from render import render_set

render_set(ROOT, p.revision, p.render, p.samples, p.width, p.height)
