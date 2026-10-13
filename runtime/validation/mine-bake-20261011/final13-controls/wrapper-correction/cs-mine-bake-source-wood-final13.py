import json,subprocess,time,shutil,uuid
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('fresh_evidence','/tmp/cs-mine-evidence-final13.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';log=audit/'native-bake-source-wood-final13.log';scratch=Path('/tmp')/('cs-mine-unity-temp-'+uuid.uuid4().hex)
args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.SpawnVisualReview.BakeAndRender','-csCapturePath',str(audit/'unity-spawn-source-wood-final13'),'-logFile',str(log)]
evidence.require_absent(log,audit/'unity-spawn-source-wood-final13',audit/'fresh-spawn-receipt-final13.json')
preserved=audit/'final13-pre-bake-generated-receipts';preserved.mkdir(exist_ok=False)
for name in ['prepared-scene.json','mine-point-bake-output.json']:
 path=evidence.GENERATED/name
 if path.exists():shutil.move(path,preserved/name)
process=subprocess.Popen(args,cwd=root);moved=False
while process.poll() is None and not moved:
 if log.exists() and 'CS_SPAWN_LIGHTING_BAKE_START' in log.read_text(errors='replace'):
  temp=project/'Temp';assert temp.is_dir() and not temp.is_symlink() and not scratch.exists();shutil.move(temp,scratch);temp.symlink_to(scratch,target_is_directory=True);moved=True
  (audit/'native-scratch.json').write_text(json.dumps({'scratch':str(scratch),'projectTemp':str(temp),'relocatedBeforeLightBakerInput':True,'command':args},indent=2)+'\n');print('CS_BAKE_SCRATCH_RELOCATED',scratch,flush=True)
 time.sleep(.2)
code=process.wait();print('CS_BAKE_EDITOR_EXIT',code,flush=True)
if code:raise SystemExit(code)
text=log.read_text(errors='replace')
for marker in ['CS_SPAWN_LIGHTING_BAKE_START','CS_SPAWN_LIGHTING_BAKE_OK','CS_MINE_ACTUAL_POINT_BAKE_OUTPUT','CS_SPAWN_VISUAL_CAPTURE_OK']:
 if text.count(marker)!=1:raise RuntimeError('Missing or duplicate fresh bake marker: '+marker)
if not moved or 'Shader error in' in text:raise RuntimeError('Native bake failed scratch/shader check')
evidence.validate_spawn();print('CS_FINAL13_FRESH_BAKE_AND_COMPLETE_SPAWN_RECEIPT_OK',flush=True)
