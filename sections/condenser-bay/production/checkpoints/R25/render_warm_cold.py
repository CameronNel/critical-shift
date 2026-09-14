"""Legacy repeat-render helper, NOT a cold reopen. Use astra_review.ps1 instead."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from render import render_set

rev = "R14"
if "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1 :]
    if args:
        rev = args[0]
render_set(ROOT, rev, "all", 32, 1920, 1080)
render_set(ROOT, "repeat-" + rev, "all", 32, 1920, 1080)
print("REPEAT_RENDER_ONLY_NOT_COLD", rev, flush=True)
