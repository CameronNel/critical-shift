from pathlib import Path
import subprocess,time,json,hashlib,os
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';state=audit/'full-native-final13-state.json';python='/home/agent/.local/share/critical-shift/venv/bin/python'
def record(status,**extra):state.write_text(json.dumps({'state':status,'pid':os.getpid(),**extra},indent=2)+'\n')
record('WaitingForFreshSource')
script_names=['cs-mine-complete-native-final13.py','cs-mine-full-native-final13.py','cs-mine-bake-source-wood-final13.py','cs-mine-after-bake-source-wood-final13.py','cs-mine-evidence-final13.py']
def script_hashes():return {name:hashlib.sha256((Path('/tmp')/name).read_bytes()).hexdigest() for name in script_names}
scripts=script_hashes();(audit/'native-launch-recipe-final13.json').write_text(json.dumps({'externalHelpers':scripts,'status':'Queued; not native execution proof'},indent=2)+'\n')
try:
 malformed=0
 while True:
  try:source=json.loads((audit/'fresh-export-final13-state.json').read_text());malformed=0
  except json.JSONDecodeError:
   malformed+=1
   if malformed>=3:raise RuntimeError('Fresh source state remains malformed; no bake launched')
   time.sleep(2);continue
  if source['state']=='Failed':raise RuntimeError('Fresh source13 export failed; no native bake launched')
  if source['state']=='Finished':break
  time.sleep(2)
 report=json.loads((audit/'api-final13/player-api.json').read_text());assert report['status']=='Passed'
 base=root/'runtime/unity/Assets/CriticalShift';digest=hashlib.sha256(b''.join(p.read_bytes() for directory in [base/'Features/Player',base/'Bootstrap/Player',base/'Tests/Player'] for p in sorted(directory.rglob('*.cs')))).hexdigest();assert digest==report['source_sha256'],'Code changed since pinned API check'
 false={x['name'] for x in json.loads(Path('/tmp/cs-mine-source-stable-board-final12/context-shadow-exclusions.json').read_text())};m=json.loads((base/'Generated/Spawn/map-bindings.json').read_text());context=next(p for p in m['materials'] if p['room']=='mine')['contextObjects'];fixed=[b for b in context if b['source'] in false];assert len(fixed)==30 and all(b['sourceShadowExcluded'] for b in fixed),'Context source shadow flags incomplete'
 assert json.loads(Path('/tmp/cs-mine-production-scope-final13.json').read_text())['status']=='Passed'
 assert script_hashes()==scripts,'External helper changed while waiting; queue requires fresh review'
 record('RunningFullNativeBakeAndValidation',contextShadowExclusions=30)
 print('CS_FINAL13_SOURCE_FLAGS_API_SCOPE_PREFLIGHT_OK',flush=True)
 subprocess.run([python,'/tmp/cs-mine-full-native-final13.py'],cwd=root,check=True)
 receipt=json.loads((audit/'fresh-technical-receipt-final13.json').read_text());assert receipt['status']=='PassedTechnicalChecksAwaitingIndependentVisualReview'
 assert script_hashes()==scripts,'External helper changed during native run'
 record('FinishedTechnicalChecksAwaitingStrictVisualReview')
 print('CS_FINAL13_FULL_NATIVE_READY_FOR_STRICT_VISUAL_REVIEW; no visual score or Player pass implied',flush=True)
except Exception as error:
 record('Failed',reason=str(error));raise
