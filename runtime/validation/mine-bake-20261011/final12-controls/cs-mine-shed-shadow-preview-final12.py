from pathlib import Path
import subprocess,shutil,time
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';helper=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineShadowPreviewFinal12.cs';deadline=time.monotonic()+1800
while True:
 active=[]
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    if (p/'exe').resolve().name in ['Unity','blender','LightBaker']:active.append(p.name)
   except (OSError,RuntimeError):pass
 if not active and not (project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineTransportSplitFinal12.cs').exists():break
 if time.monotonic()>deadline:raise TimeoutError('Another heavy process remains; no concurrent launch')
 time.sleep(1)
code=Path('/tmp/cs-mine-shadow-preview-final12.cs.txt').read_text().replace('/tmp/cs-mine-shadow-preview-final12/','/tmp/cs-mine-shed-shadow-preview-final12/').replace('R39_02_TUNNEL','R39_04_SHED_FRONT');Path('/tmp/cs-mine-shed-shadow-preview-final12.cs.txt').write_text(code);assert not helper.exists();helper.write_text(code)
try:subprocess.run(['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineShadowPreviewFinal12.Render','-logFile',str(root/'runtime/out/mine-bake-audit/shed-shadow-preview-final12.native.log')],cwd=root,check=True)
finally:helper.unlink(missing_ok=True);Path(str(helper)+'.meta').unlink(missing_ok=True)
