from pathlib import Path
import subprocess,json,traceback,hashlib,importlib.util
state=Path('/tmp/cs-main342-native-pipeline-final15.json');assert not state.exists()
python='/home/agent/.local/share/critical-shift/venv/bin/python'
result={'status':'StartingNativeCurrentMainBake_NotArtAccepted','mapCommit':'342af0003fec9dbe80b5acb40d1477c23b5a3169','limits':['Draft delivery only, independent visual and Player acceptance remain required']}
state.write_text(json.dumps(result,indent=2)+'\n')
root=Path('/workspace/critical-shift-spawn-runtime')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
helpers=[Path('/tmp')/n for n in ['cs-main342-native-final15.py','cs-main342-native-bake-final15.py','cs-main342-native-after-bake-final15.py','cs-main342-native-evidence-final15.py']]
inputs=helpers+[Path('/tmp')/n for n in ['cs-main342-adoption-final15.json','cs-main342-adoption-plan-final15.json','cs-current-main-surface-preparation-final15-r6.json','cs-main342-source-renders-native-final15-r2.json','cs-mine-library-artifacts-restored-final15.json']]+[Path('/tmp/cs-main342-source-renders-final15-r2/provenance.json'),root/'runtime/out/mine-bake-audit/cameras.json']
for directory in ['Features/Player','Bootstrap/Player','Tests/Player']:
 inputs += [p for p in (root/'runtime/unity/Assets/CriticalShift'/directory).rglob('*') if p.suffix in {'.cs','.shader','.cginc','.asmdef'}]
inputs += [Path('/tmp/cs-compact-main342-final14')/n for n in ['map-config.json','combined-runtime-source.blend','build-receipt.json']]
pins={str(p):sha(p) for p in inputs};result['launchRecipe']=pins;state.write_text(json.dumps(result,indent=2)+'\n')
def validate_recipe():
 for p,digest in pins.items():assert sha(Path(p))==digest,p
try:
 steps=[('/tmp/cs-main342-native-bake-final15.py','/tmp/cs-main342-native-bake-wrapper-final15.log'),('/tmp/cs-main342-native-after-bake-final15.py','/tmp/cs-main342-native-after-bake-wrapper-final15.log')]
 for helper,log in steps:
  validate_recipe()
  assert not Path(log).exists();result['activeStep']=helper;state.write_text(json.dumps(result,indent=2)+'\n')
  with Path(log).open('x') as f:subprocess.run([python,helper],stdout=f,stderr=subprocess.STDOUT,check=True)
  result.setdefault('completedSteps',[]).append({'helper':helper,'helperSha256':hashlib.sha256(Path(helper).read_bytes()).hexdigest(),'log':log,'logSha256':hashlib.sha256(Path(log).read_bytes()).hexdigest()})
 validate_recipe()
 spec=importlib.util.spec_from_file_location('current_evidence','/tmp/cs-main342-native-evidence-final15.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
 technical=Path('/tmp/cs-main342-native-final15/fresh-technical-receipt-final15-main342.json')
 complete=json.loads(technical.read_text());assert complete['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview'
 assert complete['spawn']==evidence.validate_spawn() and complete['mine']==evidence.validate_mine() and complete['tests']==evidence.validate_tests()
 result['completeTechnicalReceiptSha256']=sha(technical)
 result['status']='CompletedCurrentMainBakeCaptureAnd18PlayModeChecks_NotVisualOrPlayerAccepted';state.write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 result.update(status='FailedCurrentMainNativePipeline',error=repr(e),traceback=traceback.format_exc());state.write_text(json.dumps(result,indent=2)+'\n');raise
