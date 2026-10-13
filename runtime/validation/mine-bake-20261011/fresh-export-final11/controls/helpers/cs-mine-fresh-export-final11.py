from pathlib import Path
import subprocess
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit'
with (audit/'prepare-source-wood-final11.log').open('w') as log:
 subprocess.run(['/home/agent/.local/share/critical-shift/venv/bin/python','runtime/tools/prepare_mine.py','--blender','/home/agent/.local/bin/blender','--size','4096','--batched'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
print('CS_FINAL11_FRESH_SOURCE_EXPORT_DONE',flush=True)
