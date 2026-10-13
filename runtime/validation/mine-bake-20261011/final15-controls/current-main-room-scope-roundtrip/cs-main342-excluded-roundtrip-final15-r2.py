from pathlib import Path
import hashlib,json,subprocess,time,traceback,importlib.util
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=Path('/tmp/cs-main342-excluded-roundtrip-final15-r2');audit.mkdir()
state=audit/'receipt.json';log=audit/'unity.log';api=Path('/tmp/cs-main342-excluded-scope-api-final15-r7/player-api.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
report=json.loads(api.read_text());assert report['status']=='Passed' and report['source_sha256']=='6687a450e6dde01be063fa31d9a1167b5c5ec262132d87e6f34b295589d68748'
inputs=[Path(__file__),api,Path('/tmp/cs-main342-excluded-scope-roundtrip-clearance-independent-final15.json'),Path('/tmp/cs-main342-excluded-scope-backup-addendum-independent-final15.json')]
inputs += [Path('/tmp/cs-main342-excluded-animation-review-independent-final15.json')]
inputs += [project/'Assets/CriticalShift/Generated/Spawn'/p for p in ['map-bindings.json','rig-bindings.json','AssembledMap.unity']]
for d in ['Features/Player','Bootstrap/Player','Tests/Player']:
 inputs += [p for p in (project/'Assets/CriticalShift'/d).rglob('*') if p.suffix in {'.cs','.shader','.cginc','.asmdef'}]
inputs += [Path('/tmp/cs-main342-stage-alias-final15.py'),Path('/tmp/cs-main342-stage-alias-final15.json'),Path('/tmp/cs-main342-source-renders-final15-r2/provenance.json')]
pins={str(p):sha(p) for p in inputs}
spec=importlib.util.spec_from_file_location('aliases','/tmp/cs-main342-stage-alias-final15.py');aliases=importlib.util.module_from_spec(spec);spec.loader.exec_module(aliases)
args=['/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-nographics','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.ExcludedRoomBakeScope.VerifyRoundTrip','-logFile',str(log)]
result={'status':'RunningBoundedNoBakeNoSaveRoomRoundTrip','pins':pins,'command':args};state.write_text(json.dumps(result,indent=2)+'\n')
def verify():
 for p,h in pins.items():assert sha(Path(p))==h,p
 aliases.validate(json.loads(aliases.receipt.read_text()))
try:
 aliases.idle();assert not (project/'Temp/UnityLockfile').exists();verify();process=subprocess.Popen(args,cwd=root)
 with (audit/'memory.jsonl').open('x') as observations:
  while process.poll() is None:
   stats=dict(x.split(' ',1) for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())
   observations.write(json.dumps({'utcEpoch':time.time(),'bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'anon':int(stats['anon']),'shmem':int(stats['shmem']),'events':Path('/sys/fs/cgroup/memory.events').read_text()})+'\n');observations.flush();time.sleep(2)
 result['exitCode']=process.wait();assert result['exitCode']==0
 text=log.read_text(errors='replace')
 for marker in ['CS_BAKE_EXCLUDED_ROOMS_UNLOADED','CS_BAKE_EXCLUDED_ROOMS_RESTORED','CS_BAKE_SCOPE_ROUND_TRIP_OK','CS_MINE_JOIN_RAYS_OK']:
  assert text.count(marker)==1,marker
 assert 'Shader error in' not in text and 'CS_SPAWN_LIGHTING_BAKE_START' not in text
 verify();result.update(status='PassedActualNoBakeNoSave14RoomRoundTrip_BakePeakAndFailurePathsUnverified',logSha256=sha(log));state.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
except BaseException as e:
 try:
  verify();result['postFailurePinsAndAliases']='VerifiedIntact'
 except BaseException as failure:
  result['postFailurePinsAndAliases']=repr(failure)
 result.update(status='FailedBoundedRoomRoundTrip',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
