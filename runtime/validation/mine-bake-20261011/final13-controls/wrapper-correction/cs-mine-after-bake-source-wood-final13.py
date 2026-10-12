import subprocess,time,json,hashlib
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('fresh_evidence','/tmp/cs-mine-evidence-final13.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';wrapper=audit/'native-bake-source-wood-final13-wrapper.log';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'
deadline=time.monotonic()+10800
while time.monotonic()<deadline:
 text=wrapper.read_text(errors='replace') if wrapper.exists() else ''
 if 'CS_BAKE_EDITOR_EXIT' in text:
  if 'CS_BAKE_EDITOR_EXIT 0' not in text:raise RuntimeError('Lighting bake failed; dependent checks not run')
  break
 time.sleep(2)
else:raise TimeoutError('Lighting bake did not finish within three hours')
folder=project/'Assets/CriticalShift/Generated/Spawn';proof=json.loads((folder/'prepared-scene.json').read_text());digest=hashlib.sha256()
for directory in ['Assets/CriticalShift/Features/Player','Assets/CriticalShift/Bootstrap/Player']:
 for p in sorted(p for p in (project/directory).rglob('*') if p.suffix in {'.cs','.shader','.cginc'}):digest.update(p.read_bytes())
if proof['sourceSha256']!=digest.hexdigest():raise RuntimeError('Source changed after bake; dependent capture rejected')
for key,file in [('mapBindingsSha256','map-bindings.json'),('rigBindingsSha256','rig-bindings.json'),('sceneSha256','AssembledMap.unity')]:
 if proof[key]!=hashlib.sha256((folder/file).read_bytes()).hexdigest():raise RuntimeError('Prepared artifact changed: '+file)
args=['xvfb-run','-a','-s','-screen 0 1440x810x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CriticalShift.Player.Editor.SpawnVisualReview.Render','-csCapturePath',str(audit/'unity-source-wood-final13'),'-csCameraFile',str(audit/'cameras.json'),'-csRoom','mine','-logFile',str(audit/'native-mine-render-source-wood-final13.log')]
evidence.require_absent(audit/'unity-source-wood-final13',audit/'native-mine-render-source-wood-final13.log',audit/'fresh-mine-receipt-final13.json',audit/'native-playmode-source-wood-final13.xml',audit/'native-playmode-source-wood-final13.log')
evidence.validate_spawn()
subprocess.run(args,cwd=root,check=True)
log=(audit/'native-mine-render-source-wood-final13.log').read_text(errors='replace')
if 'Shader error in' in log or log.count('CS_SPAWN_VISUAL_CAPTURE_OK')!=1:raise RuntimeError('Matched mine capture failed')
evidence.validate_mine()
print('CS_SOURCE_WOOD_FINAL13_MATCHED_CAPTURES_READY_FOR_REVIEW',flush=True)
subprocess.run([editor,'-batchmode','-nographics','-projectPath',str(project),'-runTests','-testPlatform','PlayMode','-assemblyNames','CriticalShift.Player.Tests.PlayMode','-testResults',str(audit/'native-playmode-source-wood-final13.xml'),'-logFile',str(audit/'native-playmode-source-wood-final13.log')],cwd=root,check=True)
import xml.etree.ElementTree as ET
result=ET.parse(audit/'native-playmode-source-wood-final13.xml').getroot();print('CS_SOURCE_WOOD_FINAL13_PLAYMODE_RESULT',result.attrib,flush=True)
import re
expected=set()
for source in (project/'Assets/CriticalShift/Tests/Player').glob('*.cs'):
 for name in re.findall(r'\[(?:UnityTest|Test)\]\s+public\s+(?:void|IEnumerator)\s+(\w+)\(',source.read_text()):
  expected.add('CriticalShift.Tests.Player.'+source.stem+'.'+name)
actual={case.attrib['fullname'] for case in result.iter('test-case')}
if actual!=expected or len(actual)!=18 or any(case.attrib.get('result')!='Passed' for case in result.iter('test-case')) or int(result.attrib.get('failed','0')) or int(result.attrib.get('skipped','0')) or result.attrib.get('result')!='Passed':raise RuntimeError('Native PlayMode checks failed or required test inventory differs: '+str({'missing':sorted(expected-actual),'unexpected':sorted(actual-expected)}))
print('CS_SOURCE_WOOD_FINAL13_TECHNICAL_CHECKS_OK; final visual review and Player build pending',flush=True)
evidence.complete();print('CS_FINAL13_COMPLETE_FRESH_TECHNICAL_RECEIPT_OK; independent visual review still pending',flush=True)
