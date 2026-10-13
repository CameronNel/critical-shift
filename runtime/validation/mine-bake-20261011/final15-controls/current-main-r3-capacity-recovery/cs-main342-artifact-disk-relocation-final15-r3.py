"""Relocate a bounded set of exact active-cache buckets while Unity is stopped."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil,re
artifacts=Path('/dev/shm/critical-shift-spawn-library/Artifacts');base=source.parent/'cache-archives/current-mine-artifacts-disk-final15-r3';receipt=Path('/tmp/cs-main342-artifact-disk-relocation-final15-r3.json')
assert artifacts.resolve()==artifacts and base.parent.resolve()==base.parent and not base.is_symlink()
def collect(p):
 result={}
 for x in [p,*p.rglob('*')]:
  s=x.lstat();assert not x.is_symlink();r={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  if x.is_file():r.update(type='file',bytes=s.st_size,sha256=sha(x))
  else:assert x.is_dir();r['type']='dir'
  result[str(x.relative_to(p.parent))]=r
 return result

def check(p,records,subset=False):
 if not p.exists():assert subset;return
 actual=collect(p);assert set(actual)<=set(records) and (subset or set(actual)==set(records))
 assert all(r==records[n] for n,r in actual.items())
def idle_buckets(names):
 idle()
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   for fd in (proc/'fd').iterdir():
    try:
     target=os.readlink(fd);assert not any(target==str(artifacts/n) or target.startswith(str(artifacts/n)+'/') for n in names),(proc.name,target)
    except (FileNotFoundError,PermissionError):continue
  except (FileNotFoundError,PermissionError):continue
idle();result=json.loads(receipt.read_text()) if receipt.exists() else None
if not result:
 assert not base.exists();candidates=[]
 for p in artifacts.iterdir():
  if not p.is_dir() or p.is_symlink() or not re.fullmatch('[0-9a-f]{2}',p.name) or any(x.is_symlink() for x in p.rglob('*')):continue
  records=collect(p);candidates.append((sum(r.get('bytes',0) for r in records.values()),p.name,records))
 chosen=[];total=0
 for size,name,records in sorted(candidates,reverse=True):
  if total+size>820_000_000:continue
  chosen.append({'name':name,'bytes':size,'inventory':records,'phase':'copy'});total+=size
  if total>=780_000_000:break
 assert 780_000_000<=total<=820_000_000 and free(base.parent)>total+384*1024**2
 result={'status':'RelocatingExactCacheBytes','items':chosen,'bytes':total,'rootAvailableBefore':free(base.parent),'shmemBefore':int(dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())['shmem']),'limits':['Generated Library cache only; current immutable assets/canonical Source untouched','Unity may subsequently update/evict cache entries; this is byte preservation at relocation, not cache-health or immutability certification','384MiB minimum Rootreserve; next-bake peak not guaranteed']};write_json(receipt,result)
assert all(re.fullmatch('[0-9a-f]{2}',i['name']) for i in result['items']);idle_buckets([i['name'] for i in result['items']]);base.mkdir(exist_ok=True);fsync_dir(base.parent)
try:
 for item in result['items']:
  p=artifacts/item['name'];dest=base/p.name;records=item['inventory'];assert item['phase'] in {'copy','release','done'}
  if item['phase']=='copy':
   check(p,records);assert not dest.is_symlink()
   if dest.exists():
    for x in [dest,*dest.rglob('*')]:
     n=str(x.relative_to(base));assert n in records and not x.is_symlink();assert x.is_dir() if records[n]['type']=='dir' else x.is_file()
   for name,r in sorted(records.items(),key=lambda v:len(Path(v[0]).parts)):
    src=artifacts/name;target=base/name;assert not target.is_symlink() and target.parent.resolve()==target.parent and target.is_relative_to(base)
    if r['type']=='dir':target.mkdir(exist_ok=True);os.chmod(target,r['mode']);os.chown(target,r['uid'],r['gid']);continue
    offset=target.stat().st_size if target.exists() else 0;assert offset<=r['bytes'] and free(base)>r['bytes']-offset+384*1024**2
    if offset:
     with src.open('rb') as a,target.open('rb') as b:
      remaining=offset
      while remaining:
       n=min(1024*1024,remaining);v=b.read(n);assert len(v)==n and v==a.read(n);remaining-=n
    with src.open('rb') as a,target.open('ab' if target.exists() else 'xb') as b:
     a.seek(offset)
     for block in iter(lambda:a.read(1024*1024),b''):b.write(block)
     b.flush();os.fsync(b.fileno())
    os.chmod(target,r['mode']);os.chown(target,r['uid'],r['gid'])
    with target.open('rb') as f:os.fsync(f.fileno())
    fsync_dir(target.parent)
   for name,r in sorted(records.items(),key=lambda v:-len(Path(v[0]).parts)):
    if r['type']=='dir':fsync_dir(base/name)
   fsync_dir(base);check(dest,records);check(p,records);item['phase']='release';write_json(receipt,result)
  check(dest,records)
  if not p.is_symlink():
   assert item['phase']=='release';idle_buckets([p.name]);check(p,records,subset=True)
   if p.exists():shutil.rmtree(p)
   fsync_dir(artifacts);temporary=p.with_name(p.name+'.disk-alias-'+uuid.uuid4().hex);temporary.symlink_to(dest,target_is_directory=True);os.replace(temporary,p);fsync_dir(artifacts)
  assert os.readlink(p)==str(dest);check(p.resolve(),records);item['phase']='done';write_json(receipt,result)
 result.update(status='PreservedExactArtifactBucketsOnDisk_LogicalCachePathsAvailable',rootAvailableAfter=free(base),shmemAfter=int(dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())['shmem']));write_json(receipt,result);print(result['status'],result['bytes'],flush=True)
except BaseException as e:
 result.update(status='FailedCacheRelocation_VerifiedOriginalOrDiskCopyRetained',error=repr(e));write_json(receipt,result);raise
