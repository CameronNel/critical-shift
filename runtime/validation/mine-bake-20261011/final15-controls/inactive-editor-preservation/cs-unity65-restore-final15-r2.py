"""Restore a complete or known partial editor from preserved exact archive."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import subprocess,tarfile
receipt=Path('/tmp/cs-unity65-restored-final15-r2.json')
scratch=source.parent/'cs-unity65-restoration-scratch-final15-r2'
idle();entries=archive_check();existing=tree_check(entries)
result=json.loads(receipt.read_text()) if receipt.exists() else None
if result:assert result['archiveSha256']==prior['archiveSha256'] and result['scratch']==str(scratch)
else:assert not scratch.exists() and not scratch.is_symlink()
assert not scratch.is_symlink()
missing=sum(r.get('bytes',0) for name,r in entries.items() if name not in existing)
assert free(source.parent)>missing+256*1024*1024
result={'status':'RestoringExactArchivedUnity65','archiveSha256':prior['archiveSha256'],'inventorySha256':prior['inventorySha256'],'scratch':str(scratch),'missingBytes':missing,'limits':['Original hardlink sharing becomes independent byte-identical files','Pinned4.3 and standaloneSDK launcher remain untouched','Owned interrupted file scratch is retained outside the editor tree']};write_json(receipt,result)
scratch.mkdir(exist_ok=True);fsync_dir(scratch.parent)
pipe=None
try:
 pipe=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE);seen=set()
 with tarfile.open(fileobj=pipe.stdout,mode='r|') as stream:
  for member in stream:
   name=member.name.rstrip('/');assert name in entries and name not in seen;seen.add(name);r=entries[name];p=source.parent/name
   assert member.mode==r['mode'] and member.uid==r['uid'] and member.gid==r['gid']
   if r['type']=='dir':
    assert member.isdir();p.mkdir(exist_ok=True);os.chmod(p,r['mode'])
   elif r['type']=='symlink':
    assert member.issym() and member.linkname==r['link']
    if name not in existing:p.symlink_to(r['link'])
   else:
    assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();f=stream.extractfile(member)
    if name in existing:
     for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    else:
     temporary=scratch/uuid.uuid4().hex
     with temporary.open('xb') as output:
      for b in iter(lambda:f.read(1024*1024),b''):h.update(b);output.write(b)
      output.flush();os.fsync(output.fileno())
     assert h.hexdigest()==r['sha256'];os.chmod(temporary,r['mode'])
     os.chown(temporary,r['uid'],r['gid'])
     with temporary.open('rb') as saved:os.fsync(saved.fileno())
     os.replace(temporary,p);fsync_dir(p.parent)
    assert h.hexdigest()==r['sha256']
   if p.lstat().st_uid!=r['uid'] or p.lstat().st_gid!=r['gid']:os.chown(p,r['uid'],r['gid'],follow_symlinks=False)
   fsync_dir(p.parent)
 assert pipe.wait()==0 and seen==set(entries)
 tree_check(entries,complete=True);idle()
 result.update(status='RestoredExactUnity65BytesModesOwnershipAndLinks');write_json(receipt,result);print(result['status'],flush=True)
except BaseException as error:
 if pipe and pipe.poll() is None:pipe.terminate()
 if pipe:
  try:pipe.wait(timeout=10)
  except subprocess.TimeoutExpired:pipe.kill();pipe.wait()
 result.update(status='FailedUnity65Restoration_ArchiveAndKnownPartialTreeRetained',error=repr(error));write_json(receipt,result);raise
