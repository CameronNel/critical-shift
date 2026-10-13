import hashlib,json,subprocess,time,shutil,uuid
from pathlib import Path
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=Path('/tmp/cs-main342-native-final15');editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';output=Path('/tmp/cs-main342-player-final15');binary=output/'CriticalShift'
# Explicit launch after independent image review. Require fresh output/log/report identities.
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert not output.exists()
report_path=audit/'native-player-source-wood-final15-main342.json'
map_report=audit/'native-player-map-inventory-final15-main342.json'
for p in [report_path,map_report,audit/'native-player-build-source-wood-final15-main342.log',audit/'native-player-smoke-source-wood-final15-main342.log',audit/'native-player-scratch-final15-main342.json']:assert not p.exists(),p
review_path=Path('/tmp/cs-main342-independent-visual-review-final15.json');review=json.loads(review_path.read_text())
assert review['status']=='ApprovedForCurrentMainPlayerVerification'
prepared=project/'Assets/CriticalShift/Generated/Spawn/prepared-scene.json'
assert sha(prepared)==review['preparedSceneSha256']
native=Path('/tmp/cs-main342-native-final15');source=Path('/tmp/cs-main342-source-renders-final15-r2')
expected_artifacts={str(source/(name+ext)) for name in ['R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'] for ext in ['.png','-linear.exr']}|{str(native/'unity-source-wood-final15-main342'/(name+ext)) for name in ['R39_01_PORTAL_APPROACH','R39_02_TUNNEL','R39_04_SHED_FRONT'] for ext in ['.png','-linear.exr','-linear.json']}
expected_artifacts|={str(native/'unity-spawn-source-wood-final15-main342'/(name+'.png')) for name in ['VALIDATE_Spawn','VALIDATE_BriefingDoor','VALIDATE_LockerDoor']}
assert {r['path'] for r in review['artifacts']}==expected_artifacts
for r in review['artifacts']:assert sha(Path(r['path']))==r['sha256'],r['path']
technical_path=native/'fresh-technical-receipt-final15-main342.json';technical=json.loads(technical_path.read_text());assert technical['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview'
assert sha(technical_path)==review['completeTechnicalReceiptSha256']
mapping=json.loads((prepared.parent/'map-bindings.json').read_text());assert mapping['mapCommit']=='342af0003fec9dbe80b5acb40d1477c23b5a3169'
source_proof=json.loads((source/'provenance.json').read_text());assert mapping['mapCommit']==source_proof['mapCommit'] and mapping['sources']==source_proof['sourceRecords']
inputs=[Path(__file__),prepared,prepared.parent/'map-bindings.json',prepared.parent/'rig-bindings.json',prepared.parent/'AssembledMap.unity',review_path,technical_path,source/'provenance.json',Path('/tmp/cs-main342-source-renders-native-final15-r2.json'),root/'runtime/out/mine-bake-audit/cameras.json']+[Path(r['path']) for r in review['artifacts']]
for directory in ['Features/Player','Bootstrap/Player','Tests/Player']:
 inputs += [p for p in (project/'Assets/CriticalShift'/directory).rglob('*') if p.suffix in {'.cs','.shader','.cginc','.asmdef'}]
pins={str(p):sha(p) for p in inputs}
def validate_recipe():
 for p,h in pins.items():assert sha(Path(p))==h,p
assert not (project/'Temp/UnityLockfile').exists()
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  comm=(proc/'comm').read_text().strip();process_state=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
  assert process_state=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'}),(proc.name,comm)
 except (FileNotFoundError,PermissionError):continue
validate_recipe()
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
smoke_args=['xvfb-run','-a','-s','-screen 0 1280x720x24',str(binary),'-force-glcore','-screen-width','1280','-screen-height','720','--cs-player-smoke','--cs-map-smoke-report',str(map_report),'--cs-expected-map-commit',mapping['mapCommit'],'--cs-expected-map-bindings-sha256',sha(prepared.parent/'map-bindings.json'),'-logFile',str(audit/'native-player-smoke-source-wood-final15-main342.log')]
validate_recipe()
smoke=subprocess.run(smoke_args,cwd=output,timeout=600)
smoke_log=(audit/'native-player-smoke-source-wood-final15-main342.log').read_text(errors='replace')
if smoke.returncode or smoke_log.count('CS_PLAYER_ROOM_SMOKE_OK')!=1 or smoke_log.count('CS_PLAYER_MAP_INVENTORY_OK')!=1:raise RuntimeError('Current native Player smoke failed')
validate_recipe()
loaded=json.loads(map_report.read_text());assert loaded['mapCommit']==mapping['mapCommit'] and loaded['mapBindingsSha256']==sha(prepared.parent/'map-bindings.json') and loaded['frames']==120
assert len(loaded['rooms'])==len(mapping['rooms'])==14
assert {r['key']:r['triangles'] for r in loaded['rooms']}=={r['key']:r['collisionTriangles'] for r in mapping['rooms']}
assert len({r['key'] for r in loaded['rooms']})==14
manifest={relative:sha(prepared.parent/relative) for relative in ['prepared-scene.json','map-bindings.json','rig-bindings.json','AssembledMap.unity']}
assert binary.is_file() and (output/'CriticalShift_Data').is_dir() and binary.stat().st_mode & 0o111
for p in [output/'CriticalShift_Data/data.unity3d',output/'CriticalShift_Data/Managed/CriticalShift.Features.Player.Unity.dll',output/'CriticalShift_Data/Managed/CriticalShift.Player.Bootstrap.dll']:assert p.is_file() and p.stat().st_size>0,p
artifacts=[{'path':str(p.relative_to(output)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.rglob('*')) if p.is_file()]
report={'launchRecipe':pins,'result':'Passed','buildCommand':args,'smokeCommand':smoke_args,'buildExitCode':build_code,'smokeExitCode':smoke.returncode,'elapsedSeconds':time.time()-start,'binary':str(binary),'preparedArtifactHashes':manifest,'smokeFrames':120,'mapInventoryReportSha256':sha(map_report),'mapInventory':loaded,'buildArtifacts':artifacts,'performanceClaim':'None; loaded room/collision inventory and session lifecycle only; target-hardware performance and continuous navigation outside the tested Spawn→cafeteria route remain unassessed'}
(audit/'native-player-source-wood-final15-main342.json').write_text(json.dumps(report,indent=2)+'\n');print('CS_CURRENT_MINE_PLAYER_BUILD_AND_SMOKE_OK',flush=True)
