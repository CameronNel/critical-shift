from pathlib import Path
import shutil,subprocess
root=Path('/workspace/critical-shift-spawn-runtime');p=root/'runtime/unity/Assets/CriticalShift/Bootstrap/Player/Editor/CsMineGiRadiusExtractionFinal12.cs';assert not p.exists();shutil.copy2('/tmp/cs-mine-gi-radius-extraction-final12.cs.txt',p)
try:subprocess.run(['/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-nographics','-quit','-projectPath',str(root/'runtime/unity'),'-executeMethod','CsMineGiRadiusExtractionFinal12.Run','-logFile',str(root/'runtime/out/mine-bake-audit/gi-radius-extraction-final12.native.log')],cwd=root,check=True)
finally:p.unlink(missing_ok=True);Path(str(p)+'.meta').unlink(missing_ok=True)
