"""Restore currently preserved cache bytes to SHM while idle, with capacity guard."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil,re
move=json.loads(Path('/tmp/cs-main342-artifact-disk-relocation-final15-r3.json').read_text());assert move['status']=='PreservedExactArtifactBucketsOnDisk_LogicalCachePathsAvailable'
artifacts=Path('/dev/shm/critical-shift-spawn-library/Artifacts');base=source.parent/'cache-archives/current-mine-artifacts-disk-final15-r3';scratch=Path('/dev/shm/cs-mine-artifact-restore-final15-r3');receipt=Path('/tmp/cs-main342-artifact-disk-restored-final15-r3.json')
def collect(p):
 records={}
 for x in [p,*p.rglob('*')]:
  s=x.lstat();assert not x.is_symlink();r={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  if x.is_file():r.update(type='file',bytes=s.st_size,sha256=sha(x))
  else:assert x.is_dir();r['type']='dir'
  records[str(x.relative_to(p.parent))]=r
 return records
def idle_scoped():
 idle();roots=[artifacts/i['name'] for i in move['items']]+[base/i['name'] for i in move['items']]+[scratch]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   for fd in (proc/'fd').iterdir():
    try:
     target=os.readlink(fd);assert not any(target==str(r) or target.startswith(str(r)+'/') for r in roots),(proc.name,target)
    except (FileNotFoundError,PermissionError):continue
  except (FileNotFoundError,PermissionError):continue
idle_scoped();assert artifacts.resolve()==artifacts and base.resolve()==base and not scratch.is_symlink();result=json.loads(receipt.read_text()) if receipt.exists() else None
if not result:
 assert not scratch.exists();items=[]
 for item in move['items']:
  name=item['name'];assert re.fullmatch('[0-9a-f]{2}',name);p=artifacts/name;disk=base/name
  assert p.is_symlink() and os.readlink(p)==str(disk);items.append({'name':name,'inventory':collect(disk),'phase':'copy'})
 total=sum(r.get('bytes',0) for item in items for r in item['inventory'].values());assert free(artifacts)>total+256*1024**2
 result={'status':'RestoringCurrentExactCacheBytes','items':items,'limits':['Current disk-cache bytes, which may have changed since original relocation','Unknown/conflicting cache tree fails without overwriting','No Source/current immutable derivative changes']};write_json(receipt,result)
scratch.mkdir(exist_ok=True);fsync_dir(scratch.parent)
try:
 for item in result['items']:
  name=item['name'];assert re.fullmatch('[0-9a-f]{2}',name);p=artifacts/name;disk=base/name;stage=scratch/name;records=item['inventory']
  assert collect(disk)==records
  if item['phase']=='copy':
   assert p.is_symlink() and os.readlink(p)==str(disk) and not stage.is_symlink()
   # A retained partial staging tree must contain only byte-identical known files.
   if stage.exists():
    partial=collect(stage);assert set(partial)<=set(records) and all(r==records[n] for n,r in partial.items())
   pending=sum(r.get('bytes',0) for n,r in records.items() if not (scratch/n).exists());assert free(artifacts)>pending+256*1024**2
   for n,r in sorted(records.items(),key=lambda v:len(Path(v[0]).parts)):
    target=scratch/n;src=base/n;assert target.parent.resolve()==target.parent and not target.is_symlink()
    if r['type']=='dir':target.mkdir(exist_ok=True);os.chmod(target,r['mode']);os.chown(target,r['uid'],r['gid'])
    elif not target.exists():
     t=scratch/(uuid.uuid4().hex+'.partial')
     with src.open('rb') as a,t.open('xb') as b:shutil.copyfileobj(a,b);b.flush();os.fsync(b.fileno())
     assert sha(t)==r['sha256'];os.chmod(t,r['mode']);os.chown(t,r['uid'],r['gid'])
     with t.open('rb') as f:os.fsync(f.fileno())
     os.replace(t,target)
    fsync_dir(target.parent)
   assert collect(stage)==records;item['phase']='replace';write_json(receipt,result)
  if item['phase']=='replace':
   idle_scoped()
   if p.is_symlink():assert os.readlink(p)==str(disk);p.unlink();fsync_dir(artifacts)
   if not p.exists():assert collect(stage)==records;os.rename(stage,p);fsync_dir(artifacts)
   assert not p.is_symlink() and collect(p)==records;item['phase']='done';write_json(receipt,result)
  assert item['phase']=='done' and collect(p)==records
 idle_scoped();result['status']='RestoredCurrentExactCacheBucketsToShm_DiskDuplicatesRetained';write_json(receipt,result);print(result['status'],flush=True)
except BaseException as e:
 result.update(status='FailedCacheRestore_ExactDiskAndKnownStagingRetained',error=repr(e));write_json(receipt,result);raise
