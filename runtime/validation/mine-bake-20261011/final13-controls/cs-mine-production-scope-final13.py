from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';file=folder/'CsMineProductionScopeFinal13.cs'
if (project/'Temp/UnityLockfile').exists() or file.exists():raise RuntimeError('Editor busy')
try:
 shutil.copyfile('/tmp/cs-mine-production-scope-final13.cs.txt',file)
 with (audit/'cs-mine-production-scope-final13.wrapper.log').open('w') as log:subprocess.run(['/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-nographics','-quit','-projectPath',str(project),'-executeMethod','CsMineProductionScopeFinal13.Render','-logFile',str(audit/'cs-mine-production-scope-final13.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
finally:
 file.unlink(missing_ok=True);file.with_suffix('.cs.meta').unlink(missing_ok=True)
