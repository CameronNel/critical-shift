from pathlib import Path
import subprocess,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not (root/'runtime/unity/Temp/UnityLockfile').exists()
records=json.loads((audit/'preservation.json').read_text())['sourceRecords'];pins={str(root/'runtime/out/spawn-export-source/map'/r['path']):r['sha256'] for r in records};snapshot=root/'runtime/out/spawn-export-source/combined-runtime-source.blend';pins[str(snapshot)]='255fe337aacd602e81bd2940be7bf2a1da2541954f6c8446c8a06f5aae413b72';helper=Path('/tmp/cs-mine-source-closure-inspect-final13.py');pins[str(helper)]=sha(helper)
for p,h in pins.items():assert sha(Path(p))==h,p
log=audit/'cs-mine-source-closure-inspect-final13.log';assert not log.exists() and not Path('/tmp/cs-mine-source-closure-inspect-final13.json').exists();args=['/home/agent/.local/bin/blender','--background',str(snapshot),'--python-exit-code','1','--python',str(helper)]
with log.open('x') as f:subprocess.run(args,cwd=root,stdout=f,stderr=subprocess.STDOUT,check=True)
assert 'CS_SOURCE_CLOSURE_INSPECTION_OK' in log.read_text(errors='replace')
for p,h in pins.items():assert sha(Path(p))==h,p
output=Path('/tmp/cs-mine-source-closure-inspect-final13.json');report=json.loads(output.read_text());assert report['snapshotSha256']==sha(snapshot) and report['helperSha256']==sha(helper)
Path('/tmp/cs-mine-source-closure-inspect-final13-preservation.json').write_text(json.dumps({'status':'PassedReadOnlySourceInspectionPreservation','pins':pins,'outputSha256':sha(output),'logSha256':sha(log),'command':args,'limits':['Numeric socket/visibility/geometry inventory, no render or grade']},indent=2)+'\n');print('Read-only closure inspection and source hashes passed',flush=True)
