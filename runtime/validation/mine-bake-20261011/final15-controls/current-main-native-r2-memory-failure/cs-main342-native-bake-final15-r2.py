import json,subprocess,time,shutil,uuid,re,hashlib
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('fresh_evidence','/tmp/cs-main342-native-evidence-final15-r2.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=Path('/tmp/cs-main342-native-final15-r2');log=audit/'native-bake-source-wood-final15-r2-main342.log';scratch=Path('/tmp')/('cs-mine-unity-temp-'+uuid.uuid4().hex)
audit.mkdir(exist_ok=False)
assert json.loads(Path('/tmp/cs-main342-adoption-final15.json').read_text())['status']=='AdoptedVerifiedCurrent13Derivatives_AwaitingNativeRebuild'
assert json.loads(Path('/tmp/cs-mine-library-artifacts-restored-final15.json').read_text())['status']=='RestoredExactCacheBytesModesAndLinks_CacheHealthNotCertified'
args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.SpawnVisualReview.BakeAndRender','-csCapturePath',str(audit/'unity-spawn-source-wood-final15-r2-main342'),'-logFile',str(log)]
evidence.require_absent(log,audit/'unity-spawn-source-wood-final15-r2-main342',audit/'fresh-spawn-receipt-final15-r2-main342.json')
preserved=audit/'final15-r2-main342-pre-bake-generated-receipts';preserved.mkdir(exist_ok=False)
for name in ['prepared-scene.json','mine-point-bake-output.json','mine-spot-bake-output.json']:
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
for marker in ['CS_BAKE_FULL_SCENE_BACKUP','CS_BAKE_EXCLUDED_ROOMS_UNLOADED','CS_BAKE_EXCLUDED_ROOMS_RESTORED','CS_SPAWN_LIGHTING_BAKE_START','CS_SPAWN_LIGHTING_BAKE_OK','CS_MINE_ACTUAL_POINT_BAKE_OUTPUT','CS_MINE_ACTUAL_SPOT_BAKE_OUTPUT','CS_SPAWN_VISUAL_CAPTURE_OK']:
 if text.count(marker)!=1:raise RuntimeError('Missing or duplicate fresh bake marker: '+marker)
if not moved or 'Shader error in' in text:raise RuntimeError('Native bake failed scratch/shader check')
evidence.validate_spawn();print('CS_FINAL13_FRESH_BAKE_AND_COMPLETE_SPAWN_RECEIPT_OK',flush=True)

match=re.search(r'CS_BAKE_FULL_SCENE_BACKUP; path=(.+)',text);assert match
backup=Path(match.group(1).strip());assert backup.is_file() and not backup.is_symlink() and backup.parent==Path('/tmp') and backup.name.startswith('cs-bake-full-map-before-exclusion-')
for marker in ['CS_BAKE_EXCLUDED_ROOMS_UNLOADED','CS_BAKE_EXCLUDED_ROOMS_RESTORED']:
 assert re.search(marker+r'; rooms=11;',text),marker
assert not list(evidence.GENERATED.glob('BakeRoomStash-*'))
(audit/'room-scope-recovery-proof.json').write_text(json.dumps({'fullSceneBackup':str(backup),'backupSha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'excludedRooms':11,'ownedStashAbsent':True,'limits':'Actual bake successful restoration, not injected failure-path certification'},indent=2)+'\n')
