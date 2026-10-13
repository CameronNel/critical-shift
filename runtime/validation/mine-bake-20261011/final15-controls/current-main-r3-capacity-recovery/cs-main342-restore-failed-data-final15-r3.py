"""Restore complete archived failure directory or an exact known partial tree."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import subprocess,tarfile,sys
state=json.loads(Path('/tmp/cs-main342-failed-data-archives-final15-r3.json').read_text());assert state['status']=='VerifiedBothFailedDataArchives_OriginalsRetained'
allowed={'/tmp/cs-mine-unity-temp-f641ef18fa1748dc8e311fa133c01ef7','/workspace/critical-shift-spawn-runtime/runtime/out/mine-bake-audit/final13-failed-native-oom'}
assert len(sys.argv)==2 and sys.argv[1] in {'0','1'};item=state['items'][int(sys.argv[1])];src=Path(item['source']);encoded=Path(item['archive']);records=item['inventory'];assert str(src) in allowed
receipt=Path('/tmp')/('cs-main342-failed-data-restored-final15-r3-'+sys.argv[1]+'.json');scratch=src.parent/('cs-failed-data-restore-scratch-r3-'+sys.argv[1]);idle()
assert src.parent.resolve()==src.parent and encoded.parent.resolve()==encoded.parent and encoded.is_file() and not encoded.is_symlink()
assert encoded.stat().st_size==item['archiveBytes'] and sha(encoded)==item['archiveSha256']
for name in records:
 rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]==src.name
assert not src.is_symlink()
existing=set()
for p in [src,*src.rglob('*')] if src.exists() else []:
 name=str(p.relative_to(src.parent));assert name in records and not p.is_symlink();r=records[name];s=p.lstat();existing.add(name)
 assert stat.S_IMODE(s.st_mode)==r['mode'] and s.st_uid==r['uid'] and s.st_gid==r['gid']
 if r['type']=='file':assert p.is_file() and s.st_size==r['bytes'] and sha(p)==r['sha256']
 else:assert r['type']=='dir' and p.is_dir()
# These scoped failure directories contain no links; reject unsupported future inputs.
assert all(r['type'] in {'file','dir'} for r in records.values())
old=json.loads(receipt.read_text()) if receipt.exists() else None
if old:assert old['scratch']==str(scratch) and old['archiveSha256']==item['archiveSha256']
else:assert not scratch.exists() and not scratch.is_symlink()
assert not scratch.is_symlink()
missing=sum(r.get('bytes',0) for name,r in records.items() if name not in existing);assert free(src.parent)>missing+256*1024*1024
result={'status':'RestoringExactFailureData','scratch':str(scratch),'source':str(src),'archiveSha256':item['archiveSha256'],'missingBytes':missing};write_json(receipt,result);scratch.mkdir(exist_ok=True);fsync_dir(scratch.parent);decoder=None
try:
 decoder=subprocess.Popen(['zstd','-dc',str(encoded)],stdout=subprocess.PIPE);seen=set()
 with tarfile.open(fileobj=decoder.stdout,mode='r|') as stream:
  for member in stream:
   name=member.name.rstrip('/');assert name in records and name not in seen;seen.add(name);r=records[name];p=src.parent/name
   assert member.mode==r['mode'] and member.uid==r['uid'] and member.gid==r['gid'] and p.parent.resolve()==p.parent
   if r['type']=='dir':
    assert member.isdir();p.mkdir(exist_ok=True);os.chmod(p,r['mode']);os.chown(p,r['uid'],r['gid'])
   else:
    assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();data=stream.extractfile(member)
    if name in existing:
     for block in iter(lambda:data.read(1024*1024),b''):h.update(block)
    else:
     t=scratch/uuid.uuid4().hex
     with t.open('xb') as f:
      for block in iter(lambda:data.read(1024*1024),b''):h.update(block);f.write(block)
      f.flush();os.fsync(f.fileno())
     assert h.hexdigest()==r['sha256'];os.chmod(t,r['mode']);os.chown(t,r['uid'],r['gid'])
     with t.open('rb') as f:os.fsync(f.fileno())
     os.replace(t,p)
    assert h.hexdigest()==r['sha256']
   fsync_dir(p.parent)
 assert decoder.wait()==0 and seen==set(records)
 for name,r in records.items():
  p=src.parent/name;s=p.lstat();assert stat.S_IMODE(s.st_mode)==r['mode'] and s.st_uid==r['uid'] and s.st_gid==r['gid']
  if r['type']=='file':assert p.is_file() and s.st_size==r['bytes'] and sha(p)==r['sha256']
 assert {str(p.relative_to(src.parent)) for p in [src,*src.rglob('*')]}==set(records)
 idle();result['status']='RestoredExactFailureBytesModesAndOwnership';write_json(receipt,result);print(result['status'],flush=True)
except BaseException as e:
 if decoder and decoder.poll() is None:decoder.terminate()
 if decoder:
  try:decoder.wait(timeout=10)
  except subprocess.TimeoutExpired:decoder.kill();decoder.wait()
 result.update(status='FailedRestoration_ArchiveAndKnownPartialTreeRetained',error=repr(e));write_json(receipt,result);raise
