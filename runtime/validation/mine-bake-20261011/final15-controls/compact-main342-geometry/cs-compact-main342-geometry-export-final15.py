from pathlib import Path
import os,json,hashlib,subprocess,traceback
root=Path('/workspace/critical-shift-spawn-runtime');source=Path('/tmp/cs-compact-main342-final14');out=Path('/tmp/cs-compact-main342-geometry-final15')
state=Path('/tmp/cs-compact-main342-geometry-export-final15.json');log=Path('/tmp/cs-compact-main342-geometry-export-final15.log')
assert not out.exists() and not state.exists() and not log.exists()
import sys
sys.path.insert(0,str(root/'runtime/tools'))
from map_source_snapshot import verified_snapshot
_,config=verified_snapshot(source,'342af0003fec9dbe80b5acb40d1477c23b5a3169')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[source/'map-config.json',source/'combined-runtime-source.blend']+list((root/'runtime/tools').glob('export_*.py'))+[root/'runtime/tools/mine_join_rays.py',root/'runtime/tools/map_source_snapshot.py']
pins={str(p):sha(p) for p in inputs};out.mkdir()
args=['/home/agent/.local/bin/blender','-b',str(source/'combined-runtime-source.blend'),'-t','4','--disable-autoexec','--python-exit-code','1','--python',str(root/'runtime/tools/export_spawn_map.py'),'--',str(source/'map-config.json'),str(out)]
result={'status':'RunningIsolatedCurrent13GeometryExport','pins':pins,'command':args,'limits':['No main Generated scene replacement','Surface baking and native Unity acceptance not included']};state.write_text(json.dumps(result,indent=2)+'\n')
try:
 env=dict(os.environ,CS_SKIP_SURFACES='1',OMP_NUM_THREADS='4')
 with log.open('x') as f:subprocess.run(args,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 for p,h in pins.items():assert sha(Path(p))==h,p
 _,after=verified_snapshot(source,config['map_commit']);assert after==config
 manifest=json.loads((out/'map-bindings.json').read_text());roundtrip=json.loads((out/'map-roundtrip.json').read_text())
 assert manifest['mapCommit']==config['map_commit'] and len(manifest['rooms'])==14 and len(manifest['assemblyObjects'])==202
 assert [r['key'] for r in manifest['rooms']]==[r[0] for r in config['rooms']]+['assembly-context']
 assert roundtrip['status']=='Passed' and roundtrip['rooms']==14
 for r in manifest['rooms']:
  for field,digest in [('mesh','meshSha256'),('collision','collisionSha256')]:assert sha(out/r[field])==r[digest]
 result.update(status='PassedIsolatedCurrent13GeometryAndCollisionRoundtrip_NotUnityAccepted',files=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file()])
except BaseException as e:
 result.update(status='FailedIsolatedCurrent13GeometryExport',error=repr(e),traceback=traceback.format_exc());raise
finally:state.write_text(json.dumps(result,indent=2)+'\n')
