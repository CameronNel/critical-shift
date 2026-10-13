from pathlib import Path
import hashlib,json,subprocess,time,traceback,importlib.util,os,signal,re
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=Path('/tmp/cs-main342-graphics-cache-control-final15-r4');audit.mkdir()
state=audit/'receipt.json';log=audit/'unity.log';api=Path('/tmp/cs-main342-excluded-scope-api-final15-r8/player-api.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
report=json.loads(api.read_text());assert report['status']=='Passed' and report['source_sha256']=='fc9476fa0ae29986fcf325844346431b78f5a7baa04cd9faf3152072993a5199'
inputs=[Path(__file__),api,Path('/tmp/cs-main342-artifact-disk-relocation-final15-r3.json'),Path('/tmp/cs-main342-full-scene-recovered-final15-r3.json'),Path('/tmp/cs-main342-excluded-scope-roundtrip-clearance-independent-final15.json'),Path('/tmp/cs-main342-excluded-scope-backup-addendum-independent-final15.json')]
inputs += [Path('/tmp/cs-main342-excluded-animation-review-independent-final15.json')]
inputs += [project/'Assets/CriticalShift/Generated/Spawn'/p for p in ['map-bindings.json','rig-bindings.json','AssembledMap.unity']]
for d in ['Features/Player','Bootstrap/Player','Tests/Player']:
 inputs += [p for p in (project/'Assets/CriticalShift'/d).rglob('*') if p.suffix in {'.cs','.shader','.cginc','.asmdef'}]
inputs += [Path('/tmp/cs-main342-stage-alias-final15.py'),Path('/tmp/cs-main342-stage-alias-final15.json'),Path('/tmp/cs-main342-source-renders-final15-r2/provenance.json')]
pins={str(p):sha(p) for p in inputs}
spec=importlib.util.spec_from_file_location('aliases','/tmp/cs-main342-stage-alias-final15.py');aliases=importlib.util.module_from_spec(spec);spec.loader.exec_module(aliases)
args=['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.ExcludedRoomBakeScope.VerifyRoundTrip','-logFile',str(log)]
result={'status':'RunningBoundedGraphicsNoBakeNoSaveRoomRoundTrip','pins':pins,'command':args};state.write_text(json.dumps(result,indent=2)+'\n')
def verify():
 source=project/'Assets/CriticalShift';digest=hashlib.sha256(b''.join(p.read_bytes() for directory in [source/'Features/Player',source/'Bootstrap/Player',source/'Tests/Player'] for p in sorted(directory.rglob('*.cs')))).hexdigest();assert digest==report['source_sha256']
 recovered=json.loads(Path('/tmp/cs-main342-full-scene-recovered-final15-r3.json').read_text());assert recovered['status']=='RestoredExactAllActive14GroupDerivedScene_NativeLightingPending'
 assert sha(project/'Assets/CriticalShift/Generated/Spawn/AssembledMap.unity')==recovered['sceneSha256']==recovered['fullMapBackupSha256']
 for p,h in pins.items():assert sha(Path(p))==h,p
 aliases.validate(json.loads(aliases.receipt.read_text()))
 cache=json.loads(Path('/tmp/cs-main342-artifact-disk-relocation-final15-r3.json').read_text());assert cache['status']=='PreservedExactArtifactBucketsOnDisk_LogicalCachePathsAvailable'
 for item in cache['items']:
  link=Path('/dev/shm/critical-shift-spawn-library/Artifacts')/item['name'];target=Path('/home/agent/.local/share/critical-shift/toolchain/cache-archives/current-mine-artifacts-disk-final15-r3')/item['name'];assert link.is_symlink() and link.resolve()==target and target.is_dir()
process=None
try:
 aliases.idle();assert not (project/'Temp/UnityLockfile').exists();verify();process=subprocess.Popen(args,cwd=root,start_new_session=True)
 with (audit/'memory.jsonl').open('x') as observations:
  while process.poll() is None:
   stats=dict(x.split(' ',1) for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())
   observations.write(json.dumps({'utcEpoch':time.time(),'bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'anon':int(stats['anon']),'shmem':int(stats['shmem']),'events':Path('/sys/fs/cgroup/memory.events').read_text()})+'\n');observations.flush();time.sleep(2)
 result['exitCode']=process.wait();assert result['exitCode']==0
 text=log.read_text(errors='replace')
 for marker in ['CS_BAKE_EXCLUDED_ROOMS_UNLOADED','CS_BAKE_EXCLUDED_ROOMS_RESTORED','CS_BAKE_SCOPE_ROUND_TRIP_OK','CS_MINE_JOIN_RAYS_OK']:
  assert text.count(marker)==1,marker
 for marker in ['CS_BAKE_EXCLUDED_ROOMS_UNLOADED','CS_BAKE_EXCLUDED_ROOMS_RESTORED']:assert re.search(marker+r'; rooms=11;',text)
 assert re.search(r'CS_BAKE_SCOPE_ROUND_TRIP_OK; rooms=14; excluded=11;',text)
 assert 'CS_MINE_JOIN_RAYS_OK; sourceMatched=9; clearWalkingLanes=6' in text
 assert 'llvmpipe' in text and 'OpenGL' in text
 assert 'Shader error in' not in text and 'CS_SPAWN_LIGHTING_BAKE_START' not in text
 verify();result.update(status='PassedBoundedGraphicsRoomRoundTripAndCacheAliases_BakeUnverified',logSha256=sha(log));state.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
except BaseException as e:
 if process is not None:
  try:os.killpg(process.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:process.wait(timeout=10)
  except subprocess.TimeoutExpired:
   try:os.killpg(process.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   process.wait()
  # Remaining owned group members are terminated even if the wrapper exited first.
  try:os.killpg(process.pid,signal.SIGKILL)
  except ProcessLookupError:pass
 try:
  verify();result['postFailurePinsAndAliases']='VerifiedIntact'
 except BaseException as failure:
  result['postFailurePinsAndAliases']=repr(failure)
 result.update(status='FailedBoundedRoomRoundTrip',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
