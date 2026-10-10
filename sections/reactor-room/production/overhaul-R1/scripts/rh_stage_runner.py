"""Execute an existing bpy stage and exit after its save (headless audio workaround)."""
import os, runpy, sys, traceback
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:]
stage=Path(args[0]).resolve()
sys.path.insert(0,str(stage.parent))
sys.argv=[str(stage),'--',*args[1:]]
try:
    runpy.run_path(str(stage),run_name='__main__')
except SystemExit as e:
    sys.stdout.flush(); sys.stderr.flush(); os._exit(e.code or 0)
except BaseException:
    traceback.print_exc()
    sys.stdout.flush(); sys.stderr.flush(); os._exit(1)
sys.stdout.flush(); sys.stderr.flush(); os._exit(0)
