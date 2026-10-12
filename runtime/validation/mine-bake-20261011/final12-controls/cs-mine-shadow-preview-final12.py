from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');p=root/'runtime/unity/Assets/CriticalShift/Bootstrap/Player/Editor/CsMineShadowPreviewFinal12.cs';assert not p.exists();shutil.copy2('/tmp/cs-mine-shadow-preview-final12.cs.txt',p)
try:subprocess.run(['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(root/'runtime/unity'),'-executeMethod','CsMineShadowPreviewFinal12.Render','-logFile',str(root/'runtime/out/mine-bake-audit/shadow-preview-final12.native.log')],cwd=root,check=True)
finally:p.unlink(missing_ok=True);Path(str(p)+'.meta').unlink(missing_ok=True)
