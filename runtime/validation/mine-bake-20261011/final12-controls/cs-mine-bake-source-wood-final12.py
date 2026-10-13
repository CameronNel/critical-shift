import json,subprocess,time,shutil,uuid
from pathlib import Path
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';log=audit/'native-bake-source-wood-final12.log';scratch=Path('/tmp')/('cs-mine-unity-temp-'+uuid.uuid4().hex)
args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.SpawnVisualReview.BakeAndRender','-csCapturePath',str(audit/'unity-spawn-source-wood-final12'),'-logFile',str(log)]
log.unlink(missing_ok=True)
process=subprocess.Popen(args,cwd=root);moved=False
while process.poll() is None and not moved:
 if log.exists() and 'CS_SPAWN_LIGHTING_BAKE_START' in log.read_text(errors='replace'):
  temp=project/'Temp';assert temp.is_dir() and not temp.is_symlink() and not scratch.exists();shutil.move(temp,scratch);temp.symlink_to(scratch,target_is_directory=True);moved=True
  (audit/'native-scratch.json').write_text(json.dumps({'scratch':str(scratch),'projectTemp':str(temp),'relocatedBeforeLightBakerInput':True,'command':args},indent=2)+'\n');print('CS_BAKE_SCRATCH_RELOCATED',scratch,flush=True)
 time.sleep(.2)
code=process.wait();print('CS_BAKE_EDITOR_EXIT',code,flush=True);raise SystemExit(code)
