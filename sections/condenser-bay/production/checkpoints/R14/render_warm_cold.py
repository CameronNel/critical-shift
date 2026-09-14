"""One GPU hold: warm then cold of the already-open blend."""
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
render_set(ROOT, "cold-" + rev, "all", 32, 1920, 1080)
print("WARM_COLD_OK", rev, flush=True)
