import hashlib,json,subprocess,time,shutil,uuid
from pathlib import Path
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=Path('/tmp/cs-main342-native-final15');editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';output=Path('/tmp/cs-main342-player-final15');binary=output/'CriticalShift'
# Explicit invocation only after visual review. This script does not wait or launch itself.
assert not output.exists(), 'Do not overwrite a previous Player evidence build'
review=json.loads(Path('/tmp/cs-main342-independent-visual-review-final15.json').read_text())
assert review['status']=='ApprovedForCurrentMainPlayerVerification'
prepared=project/'Assets/CriticalShift/Generated/Spawn/prepared-scene.json'
assert hashlib.sha256(prepared.read_bytes()).hexdigest()==review['preparedSceneSha256']
pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),prepared,project/'Assets/CriticalShift/Generated/Spawn/map-bindings.json',project/'Assets/CriticalShift/Generated/Spawn/rig-bindings.json',project/'Assets/CriticalShift/Generated/Spawn/AssembledMap.unity']}
for directory in ['Features/Player','Bootstrap/Player','Tests/Player']:
 for source in (project/'Assets/CriticalShift'/directory).rglob('*'):
  if source.suffix in {'.cs','.shader','.cginc','.asmdef'}:pins[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()

assert not (project/'Temp/UnityLockfile').exists(), 'Unity must be closed before Player build'
args=['xvfb-run','-a','-s','-screen 0 1440x810x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.SpawnMapBuild.Build','-csBuildPath',str(binary),'-csCompressedBuild','-logFile',str(audit/'native-player-build-source-wood-final15-main342.log')]
start=time.time();build_process=subprocess.Popen(args,cwd=root);scratch=Path('/tmp')/('cs-mine-player-temp-'+uuid.uuid4().hex);temp=project/'Temp';relocated=False
while build_process.poll() is None:
 if temp.is_dir() and not temp.is_symlink() and not relocated:
  shutil.move(temp,scratch);temp.symlink_to(scratch,target_is_directory=True);relocated=True
  (audit/'native-player-scratch-final15-main342.json').write_text(json.dumps({'scratch':str(scratch),'projectTemp':str(temp)},indent=2)+'\n')
 time.sleep(.2)
build_code=build_process.wait()
log=(audit/'native-player-build-source-wood-final15-main342.log').read_text(errors='replace')
if build_code or 'CS_SPAWN_MAP_BUILD_OK' not in log or 'Shader error in' in log:raise RuntimeError('Native Player build failed')
smoke_args=['xvfb-run','-a','-s','-screen 0 1280x720x24',str(binary),'-force-glcore','-screen-width','1280','-screen-height','720','--cs-player-smoke','-logFile',str(audit/'native-player-smoke-source-wood-final15-main342.log')]
smoke=subprocess.run(smoke_args,cwd=output,timeout=600)
smoke_log=(audit/'native-player-smoke-source-wood-final15-main342.log').read_text(errors='replace')
if smoke.returncode or 'CS_PLAYER_ROOM_SMOKE_OK' not in smoke_log:raise RuntimeError('Current native Player smoke failed')
manifest={}
for relative in ['prepared-scene.json','map-bindings.json','rig-bindings.json','AssembledMap.unity']:
 p=project/'Assets/CriticalShift/Generated/Spawn'/relative;manifest[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
assert binary.is_file() and (output/'CriticalShift_Data').is_dir()
report={'launchRecipe':pins,'result':'Passed' ,'buildCommand':args,'smokeCommand':smoke_args,'buildExitCode':build_code,'smokeExitCode':smoke.returncode,'elapsedSeconds':time.time()-start,'binary':str(binary),'preparedArtifactHashes':manifest,'smokeFrames':120,'performanceClaim':'None; software graphics in this container are not representative target hardware'}
(audit/'native-player-source-wood-final15-main342.json').write_text(json.dumps(report,indent=2)+'\n');print('CS_CURRENT_MINE_PLAYER_BUILD_AND_SMOKE_OK',flush=True)
