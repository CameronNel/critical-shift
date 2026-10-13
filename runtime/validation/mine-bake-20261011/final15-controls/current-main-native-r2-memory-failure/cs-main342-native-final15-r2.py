from pathlib import Path
import subprocess,json,traceback,hashlib,importlib.util
state=Path('/tmp/cs-main342-native-pipeline-final15-r2.json');assert not state.exists()
python='/home/agent/.local/share/critical-shift/venv/bin/python'
result={'status':'StartingNativeCurrentMainBake_NotArtAccepted','mapCommit':'342af0003fec9dbe80b5acb40d1477c23b5a3169','limits':['Draft delivery only, independent visual and Player acceptance remain required']}
state.write_text(json.dumps(result,indent=2)+'\n')
root=Path('/workspace/critical-shift-spawn-runtime')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
helpers=[Path('/tmp')/n for n in ['cs-main342-native-final15-r2.py','cs-main342-native-bake-final15-r2.py','cs-main342-native-after-bake-final15-r2.py','cs-main342-native-evidence-final15-r2.py','cs-main342-native-memory-final15-r2.py']]
alias_spec=importlib.util.spec_from_file_location('stage_alias','/tmp/cs-main342-stage-alias-final15.py');alias_module=importlib.util.module_from_spec(alias_spec);alias_spec.loader.exec_module(alias_module)
helpers += [Path('/tmp/cs-main342-stage-alias-final15.py'),Path('/tmp/cs-main342-stage-restore-final15.py')]
inputs=helpers+[Path('/tmp/cs-main342-excluded-scope-api-final15-r7/player-api.json'),Path('/tmp/cs-main342-excluded-roundtrip-r2-independent-final15.json'),Path('/tmp/cs-unity65-released-final15-r2.json'),Path('/tmp/cs-main342-memory-relocation-final15-r2.json')]+[Path('/tmp')/n for n in ['cs-main342-adoption-final15.json','cs-main342-adoption-plan-final15.json','cs-current-main-surface-preparation-final15-r6.json','cs-main342-source-renders-native-final15-r2.json','cs-mine-library-artifacts-restored-final15.json']]+[Path('/tmp/cs-main342-source-renders-final15-r2/provenance.json'),root/'runtime/out/mine-bake-audit/cameras.json']
for directory in ['Features/Player','Bootstrap/Player','Tests/Player']:
 inputs += [p for p in (root/'runtime/unity/Assets/CriticalShift'/directory).rglob('*') if p.suffix in {'.cs','.shader','.cginc','.asmdef'}]
inputs += [Path('/tmp/cs-compact-main342-final14')/n for n in ['map-config.json','combined-runtime-source.blend','build-receipt.json']]
inputs += [Path('/tmp/cs-main342-stage-alias-final15.json')]
pins={str(p):sha(p) for p in inputs};result['launchRecipe']=pins;state.write_text(json.dumps(result,indent=2)+'\n')
def validate_recipe():
 for p,digest in pins.items():assert sha(Path(p))==digest,p
 api=json.loads(Path('/tmp/cs-main342-excluded-scope-api-final15-r7/player-api.json').read_text());assert api['status']=='Passed' and api['source_sha256']=='6687a450e6dde01be063fa31d9a1167b5c5ec262132d87e6f34b295589d68748'
 aliases=json.loads(alias_module.receipt.read_text());assert aliases['status']=='PreservedExactImmutableStageBytesViaVerifiedRootAliases';alias_module.validate(aliases)
try:
 alias_module.idle()
 assert json.loads(Path('/tmp/cs-unity65-released-final15-r2.json').read_text())['status']=='ArchivedInactiveUnity65OnDisk_ProjectPinnedEditorUnchanged'
 assert json.loads(Path('/tmp/cs-main342-memory-relocation-final15-r2.json').read_text())['status']=='PreservedInactiveArtifactsOnDisk_LogicalPathsExact'
 stats=dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines());assert int(stats['shmem'])<5*1024**3
 import os
 v=os.statvfs(root);assert v.f_bavail*v.f_frsize>1024**3
 result['capacityBaseline']={'shmemBytes':int(stats['shmem']),'rootAvailableBytes':v.f_bavail*v.f_frsize,'memoryEvents':Path('/sys/fs/cgroup/memory.events').read_text(),'limits':'Measured prelaunch capacity, not peak-bake guarantee'}
 state.write_text(json.dumps(result,indent=2)+'\n')
 steps=[('/tmp/cs-main342-native-bake-final15-r2.py','/tmp/cs-main342-native-bake-wrapper-final15-r2.log'),('/tmp/cs-main342-native-after-bake-final15-r2.py','/tmp/cs-main342-native-after-bake-wrapper-final15-r2.log')]
 for helper,log in steps:
  validate_recipe()
  assert not Path(log).exists();result['activeStep']=helper;state.write_text(json.dumps(result,indent=2)+'\n')
  with Path(log).open('x') as f:subprocess.run([python,helper],stdout=f,stderr=subprocess.STDOUT,check=True)
  result.setdefault('completedSteps',[]).append({'helper':helper,'helperSha256':hashlib.sha256(Path(helper).read_bytes()).hexdigest(),'log':log,'logSha256':hashlib.sha256(Path(log).read_bytes()).hexdigest()})
 validate_recipe()
 spec=importlib.util.spec_from_file_location('current_evidence','/tmp/cs-main342-native-evidence-final15-r2.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
 technical=Path('/tmp/cs-main342-native-final15-r2/fresh-technical-receipt-final15-r2-main342.json')
 complete=json.loads(technical.read_text());assert complete['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview'
 assert complete['spawn']==evidence.validate_spawn() and complete['mine']==evidence.validate_mine() and complete['tests']==evidence.validate_tests()
 result['completeTechnicalReceiptSha256']=sha(technical)
 result['status']='CompletedCurrentMainBakeCaptureAnd18PlayModeChecks_NotVisualOrPlayerAccepted';state.write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 result.update(status='FailedCurrentMainNativePipeline',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
