from pathlib import Path
import shutil,hashlib,json
root=Path('/workspace/critical-shift-spawn-runtime');dest=root/'runtime/validation/mine-bake-20261011/final13-controls/timber-measurement';assert not dest.exists();dest.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
def copy(p,relative):
 t=dest/relative;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t);assert sha(p)==sha(t);records.append({'file':relative,'bytes':t.stat().st_size,'sha256':sha(t)})
for folder,tag in [('/tmp/cs-mine-timber-source-final13','source'),('/tmp/cs-mine-timber-native-final13','native')]:
 for p in Path(folder).iterdir():copy(p,tag+'/'+p.name)
for name in ['cs-mine-timber-independent-review-final13.json','cs-mine-timber-r2-prelaunch-independent-final13.json','cs-mine-timber-diagnostics-final13-r2.json','cs-mine-timber-diagnostics-final13-r2.py','cs-mine-timber-source-final13.py','cs-mine-timber-native-final13.cs.txt','cs-mine-timber-native-final13.shader.txt','cs-mine-timber-object-id-final13.shader.txt','cs-mine-timber-native-api-final13-r2.json','cs-mine-timber-native-api-final13-r2.log','cs-mine-front-end-spot-independent-final13.json','cs-mine-front-spots-source-final13.json','cs-mine-freeze-timber-final13.py']:
 p=Path('/tmp')/name
 if p.exists():copy(p,name)
for name in ['timber-split-final13-r2.native.log','timber-split-final13-r2.wrapper.log','timber-split-final13-r2-stale-lock.json','preserved-player-relocation-final14.json']:
 p=root/'runtime/out/mine-bake-audit'/name
 if p.exists():copy(p,name)
(dest/'provenance.json').write_text(json.dumps({'status':'BoundedCurrentTimberDiagnosticComplete_NotVisualAcceptance','files':records,'limits':['Source32samples multiAOV raw; Native5finiteHDR actual selectedsource shaders with original casts/lights','Shared eroded interiors establish excess totaldiffuse; Native baked/probe includesbaked direct','NativeBaseColor broadlyagrees; no globalalbedo/roughness/GIscale correction','Six actual authoredfrontspots importedPoint is verifieddefect; fixture/native correction remains separate','No canonical/main/Generated scene modification, freshPlayer or98 claim']},indent=2)+'\n');print(len(records),sum(r['bytes'] for r in records))
