"""Release only exact, immutable staged delivery duplicates after adoption."""
from pathlib import Path
import hashlib,json,os,uuid
stage=Path('/tmp/cs-compact-main342-geometry-final15')
target=Path('/workspace/critical-shift-spawn-runtime/runtime/unity/Assets/CriticalShift/Generated/Spawn')
receipt=Path('/tmp/cs-main342-stage-alias-final15.json')
adoption=Path('/tmp/cs-main342-adoption-final15.json')
def write_json(path,value):
 temporary=path.with_name(path.name+'.atomic-'+uuid.uuid4().hex)
 with temporary.open('x') as f:
  f.write(json.dumps(value,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 os.replace(temporary,path)
 directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(directory)
 finally:os.close(directory)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def idle():
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   comm=(proc/'comm').read_text().strip();state=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
   assert state=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'}),(proc.name,comm)
  except (FileNotFoundError,PermissionError):continue
def records(value):
 if isinstance(value,dict):
  if 'file' in value and 'sha256' in value:yield value
  for v in value.values():yield from records(v)
 elif isinstance(value,list):
  for v in value:yield from records(v)
def validate(result):
 for r in result['files']:
  p=stage/r['path'];t=target/r['path']
  assert p.is_symlink() and os.readlink(p)==str(t) and p.resolve()==t
  assert t.is_file() and not t.is_symlink() and t.stat().st_size==r['bytes'] and sha(t)==r['sha256'],r['path']
 return result
if __name__=='__main__':
 import sys
 if '--validate-only' in sys.argv:
  result=json.loads(receipt.read_text());assert result['status']=='PreservedExactImmutableStageBytesViaVerifiedRootAliases';validate(result);print('Verified immutable stage aliases and target bytes',flush=True);raise SystemExit(0)
 assert not receipt.exists();idle()
 assert json.loads(adoption.read_text())['status']=='AdoptedVerifiedCurrent13Derivatives_AwaitingNativeRebuild'
 assert not stage.is_symlink() and not target.is_symlink()
 m=json.loads((stage/'map-bindings.json').read_text());rig=json.loads((stage/'rig-bindings.json').read_text())
 assert sha(stage/'map-bindings.json')==sha(target/'map-bindings.json') and sha(stage/'rig-bindings.json')==sha(target/'rig-bindings.json')
 expected={}
 for r in list(records(m))+list(records(rig)):
  if Path(r['file']).suffix in {'.fbx','.png','.exr'}:
   assert r['file'] not in expected or expected[r['file']]==r['sha256'];expected[r['file']]=r['sha256']
 for r in m['rooms']:
  for k,d in [('mesh','meshSha256'),('collision','collisionSha256')]:expected[r[k]]=r[d]
 expected['CrewWorker.fbx']=rig['fbx_sha256'];expected[rig['animationFile']]=rig['animationSha256']
 files=[]
 for relative,digest in sorted(expected.items()):
  rel=Path(relative);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix in {'.fbx','.png','.exr'}
  p=stage/rel;t=target/rel;temporary=p.with_name(p.name+'.root-alias-final15')
  assert p.is_file() and not p.is_symlink() and t.is_file() and not t.is_symlink()
  assert p.resolve()==p and t.resolve()==t
  assert not temporary.exists() and not temporary.is_symlink()
  assert sha(p)==digest==sha(t) and p.stat().st_size==t.stat().st_size,relative
  files.append({'path':relative,'sha256':digest,'bytes':p.stat().st_size,'stageMode':p.stat().st_mode&0o7777,'aliasTarget':str(t)})
 result={'status':'VerifiedImmutableStageDuplicatesBeforeRelinking','files':files,'rawDuplicateBytes':sum(r['bytes'] for r in files),'adoptionReceiptSha256':sha(adoption),'stagedManifestSha256':sha(stage/'map-bindings.json'),'stagedRigManifestSha256':sha(stage/'rig-bindings.json'),'before':{n:Path('/sys/fs/cgroup/'+n).read_text() for n in ['memory.current','memory.stat','memory.events']},'limits':['Only declared immutable FBX/PNG/EXR source delivery files are aliased; metadata/scene/material/cache receipts remain plain','Unity reads root source assets and never references this staging directory','Future source re-export/adoption must reconstruct staged plain files before editing; retained hashes permit verification','Any native rewrite of an alias target rejects post-run validation']}
 write_json(receipt,result)
 try:
  for r in files:
   p=stage/r['path'];t=target/r['path'];temporary=p.with_name(p.name+'.root-alias-final15')
   assert sha(p)==r['sha256']==sha(t) and not p.is_symlink() and not t.is_symlink()
   temporary.symlink_to(t);os.replace(temporary,p)
   result.setdefault('relinkedPaths',[]).append(r['path']);write_json(receipt,result)
  validate(result)
  result.update(status='PreservedExactImmutableStageBytesViaVerifiedRootAliases',after={n:Path('/sys/fs/cgroup/'+n).read_text() for n in ['memory.current','memory.stat','memory.events']})
  write_json(receipt,result);print(result['status'],result['rawDuplicateBytes'],flush=True)
 except BaseException as error:
  result.update(status='FailedStageAliasing_ExactRootCopiesPreserved_MixedStateRecoverable',error=repr(error));write_json(receipt,result);raise
