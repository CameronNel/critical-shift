"""Reconstruct staging files, including interrupted alias/restore operations."""
from pathlib import Path
import importlib.util,json,os,stat,uuid,traceback
spec=importlib.util.spec_from_file_location('stage_alias','/tmp/cs-main342-stage-alias-final15.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
receipt=Path('/tmp/cs-main342-stage-restored-final15.json');a.idle()
if receipt.exists():
 old=json.loads(receipt.read_text());assert old['status'] in {'RestoringExactPlainStageFiles','FailedPlainStageRestoration_MixedStateRecoverable'}
 history=old.get('attemptHistory',[])+[old]
else:history=[]
prior=json.loads(a.receipt.read_text());assert prior['status'] in {'PreservedExactImmutableStageBytesViaVerifiedRootAliases','VerifiedImmutableStageDuplicatesBeforeRelinking','FailedStageAliasing_ExactRootCopiesPreserved_MixedStateRecoverable'}
assert not a.stage.is_symlink() and not a.target.is_symlink()
pending=[];temporary_aliases=[]
# Freeze and verify the entire mixed state before changing any path.
for r in prior['files']:
 rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix in {'.fbx','.png','.exr'}
 p=a.stage/rel;t=a.target/rel;assert r['aliasTarget']==str(t)
 assert t.is_file() and not t.is_symlink() and t.resolve()==t and t.stat().st_size==r['bytes'] and a.sha(t)==r['sha256']
 if p.is_symlink():
  assert os.readlink(p)==str(t) and p.resolve()==t;pending.append(r)
 else:
  assert p.is_file() and p.resolve()==p and p.stat().st_size==r['bytes'] and a.sha(p)==r['sha256'] and stat.S_IMODE(p.stat().st_mode)==r['stageMode']
 temporary=p.with_name(p.name+'.root-alias-final15')
 if temporary.exists() or temporary.is_symlink():
  assert temporary.is_symlink() and os.readlink(temporary)==str(t) and temporary.resolve()==t
  temporary_aliases.append((temporary,t))
free=lambda p:os.statvfs(p).f_bavail*os.statvfs(p).f_frsize
remaining=sum(r['bytes'] for r in pending)
assert free(a.stage)>remaining+128*1024*1024
assert int(Path('/sys/fs/cgroup/memory.current').read_text())+remaining+512*1024*1024<int(Path('/sys/fs/cgroup/memory.max').read_text())
result={'status':'RestoringExactPlainStageFiles','priorAliasReceiptSha256':a.sha(a.receipt),'pendingPaths':[r['path'] for r in pending],'remainingBytes':remaining,'restoredPaths':[],'attemptHistory':history}
a.write_json(receipt,result)
try:
 for temporary,t in temporary_aliases:
  assert temporary.is_symlink() and os.readlink(temporary)==str(t) and temporary.resolve()==t;temporary.unlink()
 for r in pending:
  p=a.stage/r['path'];t=Path(r['aliasTarget']);temporary=p.with_name(p.name+'.plain-restore-final15-'+uuid.uuid4().hex)
  assert not temporary.exists() and not temporary.is_symlink() and a.sha(t)==r['sha256'] and p.is_symlink() and os.readlink(p)==str(t) and p.resolve()==t
  result['activeTemporaryPath']=str(temporary);a.write_json(receipt,result)
  with t.open('rb') as source,temporary.open('xb') as output:
   for b in iter(lambda:source.read(1024*1024),b''):output.write(b)
   output.flush();os.fsync(output.fileno())
  os.chmod(temporary,r['stageMode'])
  assert temporary.stat().st_size==r['bytes'] and a.sha(temporary)==r['sha256'];os.replace(temporary,p)
  assert not p.is_symlink() and p.stat().st_size==r['bytes'] and a.sha(p)==r['sha256'] and stat.S_IMODE(p.stat().st_mode)==r['stageMode']
  result['restoredPaths'].append(r['path']);result.pop('activeTemporaryPath');a.write_json(receipt,result)
 for r in prior['files']:
  p=a.stage/r['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'] and a.sha(p)==r['sha256'] and stat.S_IMODE(p.stat().st_mode)==r['stageMode']
 result.update(status='ReconstructedExactPlainStageFiles',files=len(prior['files']),bytes=prior['rawDuplicateBytes']);a.write_json(receipt,result);print(result['status'],flush=True)
except BaseException as error:
 result.update(status='FailedPlainStageRestoration_MixedStateRecoverable',error=repr(error),traceback=traceback.format_exc());a.write_json(receipt,result);raise
