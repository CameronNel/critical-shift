from pathlib import Path
import hashlib,json,shutil
root=Path('/workspace/critical-shift-spawn-runtime');dest=root/'runtime/validation/mine-bake-20261011/final14-controls/production-spot-first-native-failure';assert not dest.exists();dest.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
def copy(p,tag):
 t=dest/tag;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t);assert sha(t)==sha(p);records.append({'file':tag,'sha256':sha(t),'bytes':t.stat().st_size})
for folder,tag in [('/tmp/cs-mine-production-spot-native-control-final14','partial-native'),('/tmp/cs-mine-production-spot-failed-cookie-final14','failed-cookie')]:
 for p in Path(folder).iterdir():copy(p,tag+'/'+p.name)
for n in ['cs-mine-production-spot-control-final14.cs.txt','cs-mine-production-spot-native-final14.py','cs-mine-production-spot-native-final14.json','cs-mine-production-spot-api-final14-r3.json','cs-mine-production-spot-api-final14-r3.log','cs-mine-production-spot-baseline-final14.shader.txt','cs-mine-production-spot-source-final14.json','cs-mine-production-spot-source-control-input-final14.json','cs-mine-spot-production-prelaunch-independent-final14.json','cs-mine-preserve-production-spot-failure-final14.py']:copy(Path('/tmp')/n,n)
for n in ['production-spot-control-final14.native.log','production-spot-control-final14.wrapper.log']:copy(root/'runtime/out/mine-bake-audit'/n,n)
state=json.loads(Path('/tmp/cs-mine-production-spot-native-final14.json').read_text())
for p,h in state['pins'].items():
 p=Path(p);assert sha(p)==h
 if '/Assets/CriticalShift/Bootstrap/Player/Editor/' in str(p) or p.name in {'BlenderPointLighting.cginc','BlenderSurface.shader','mine_context_lights.py'}:copy(p,'exact-production/'+p.name)
resources={'memoryEvents':Path('/sys/fs/cgroup/memory.events').read_text(),'disk':shutil.disk_usage(root)._asdict()};(dest/'resources.json').write_text(json.dumps(resources,indent=2)+'\n');(dest/'provenance.json').write_text(json.dumps({'state':'FailedNativeLightBakerExit11At60Degree_NotPassing20Control','files':records,'originalStateSha256':sha(Path('/tmp/cs-mine-production-spot-native-final14.json')),'limits':['Nativeguards passed and partialframespreserved; no completepixel/shadow/fallbackacceptance','Not an OOM or interpreted Source/material/transport failure; exactcodeunchanged retry remainsseparate','No currentMain/Generatedscene files modified']},indent=2)+'\n');print(len(records),sum(r['bytes'] for r in records),resources['memoryEvents'])
