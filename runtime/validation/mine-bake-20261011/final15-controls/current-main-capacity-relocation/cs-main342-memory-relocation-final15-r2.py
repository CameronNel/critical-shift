"""Preserve scoped inactive artifacts on root disk, retaining exact logical paths."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil
receipt=Path('/tmp/cs-main342-memory-relocation-final15-r2.json')
base=source.parent/'cache-archives/mine-capacity-preserved-final15-r2'
paths=[Path('/tmp')/n for n in ['cs-mine-library-artifacts-preserved-final15.tar.zst','cs-mine-inactive-bake-scratch-preserved-final15.tar.zst','cs-mine-inactive-controls-final13-evidence.tar.gz','cs-mine-preserved-player-data-final11.unity3d','cs-main342-prior-delivery-final15','cs-mine-preserved-cache-final13-final15']]
idle();assert base.parent.resolve()==base.parent and not base.is_symlink()
def inventory_for(p):
 items=[p,*p.rglob('*')] if p.is_dir() else [p];out={}
 for x in items:
  s=x.lstat();r={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  assert not x.is_symlink(),x
  if x.is_file():r.update(type='file',bytes=s.st_size,sha256=sha(x))
  else:assert x.is_dir();r['type']='dir'
  out[str(x.relative_to(p.parent))]=r
 return out

def validate(p,records,subset=False):
 if not p.exists():assert subset;return
 actual=inventory_for(p)
 assert set(actual)<=set(records) and (subset or set(actual)==set(records))
 for n,r in actual.items():assert r==records[n],n

result=json.loads(receipt.read_text()) if receipt.exists() else None
if not result:
 assert not base.exists();records=[]
 for p in paths:
  assert p.exists() and not p.is_symlink();records.append({'source':str(p),'destination':str(base/p.name),'inventory':inventory_for(p),'phase':'copy'})
 required=sum(r.get('bytes',0) for item in records for r in item['inventory'].values())
 assert free(base.parent)>required+512*1024*1024
 result={'status':'RelocatingInactiveExactBytes','items':records,'bytes':required,'rootAvailableBefore':free(base.parent),'shmemBefore':int(dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())['shmem']),'limits':['Inactive historical archives and previous delivery backup only','Canonical sources/current Unity assets/active cache remain unchanged','Logical paths stay usable as exact verified disk aliases']};write_json(receipt,result)
assert [i['source'] for i in result['items']]==[str(p) for p in paths]
base.mkdir(exist_ok=True);fsync_dir(base.parent)
try:
 for item in result['items']:
  p=Path(item['source']);dest=base/p.name;assert item['destination']==str(dest);records=item['inventory'];assert item['phase'] in {'copy','release','done'}
  if item['phase']=='copy':
   validate(p,records);assert not dest.is_symlink()
   if dest.exists():
    actual=[dest,*dest.rglob('*')] if dest.is_dir() else [dest]
    for known in actual:
     name=str(known.relative_to(base));assert name in records and not known.is_symlink(),name
     assert known.is_dir() if records[name]['type']=='dir' else known.is_file(),name
   # Partial copied files are never accepted without checking their prefix.
   for name,r in sorted(records.items(),key=lambda v:len(Path(v[0]).parts)):
    src=p.parent/name;target=base/name
    assert not target.is_symlink() and target.parent.resolve()==target.parent and target.is_relative_to(base),target
    if r['type']=='dir':target.mkdir(exist_ok=True);os.chmod(target,r['mode']);os.chown(target,r['uid'],r['gid']);continue
    offset=target.stat().st_size if target.exists() else 0
    assert not target.is_symlink() and offset<=r['bytes']
    assert free(base)>r['bytes']-offset+512*1024*1024
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
    with target.open('rb') as b:os.fsync(b.fileno())
    fsync_dir(target.parent)
   for name,r in sorted(records.items(),key=lambda v:-len(Path(v[0]).parts)):
    if r['type']=='dir':fsync_dir(base/name)
   fsync_dir(base);validate(dest,records);validate(p,records)
   item['phase']='release';write_json(receipt,result)
  validate(dest,records)
  if not p.is_symlink():
   assert item['phase']=='release';validate(p,records,subset=True)
   if p.is_dir():shutil.rmtree(p)
   elif p.exists():p.unlink()
   fsync_dir(p.parent)
   temporary=p.with_name(p.name+'.disk-alias-'+uuid.uuid4().hex);temporary.symlink_to(dest,target_is_directory=dest.is_dir());os.replace(temporary,p);fsync_dir(p.parent)
  assert os.readlink(p)==str(dest);validate(p.resolve(),records)
  item['phase']='done';write_json(receipt,result)
 idle();result.update(status='PreservedInactiveArtifactsOnDisk_LogicalPathsExact',rootAvailableAfter=free(base),tmpAvailableAfter=free(Path('/tmp')),shmemAfter=int(dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())['shmem']));write_json(receipt,result);print(result['status'],result['bytes'],flush=True)
except BaseException as e:
 result.update(status='FailedRelocation_VerifiedOriginalOrDiskCopyRetained',error=repr(e));write_json(receipt,result);raise
