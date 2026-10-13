from pathlib import Path
import subprocess,json,os
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit'
(audit/'fresh-export-final13-state.json').write_text(json.dumps({'state':'Running','pid':os.getpid()}))
with (audit/'prepare-source-shadow-air-final13.log').open('w') as log:
 result=subprocess.run(['/home/agent/.local/share/critical-shift/venv/bin/python','runtime/tools/prepare_mine.py','--blender','/home/agent/.local/bin/blender','--size','4096','--batched'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
(audit/'fresh-export-final13-state.json').write_text(json.dumps({'state':'Finished' if result.returncode==0 else 'Failed','exitCode':result.returncode}))
print('CS_FINAL13_FRESH_SOURCE_EXPORT_EXIT',result.returncode,flush=True)
raise SystemExit(result.returncode)
