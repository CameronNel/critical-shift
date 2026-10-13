"""Resume durable release of independently preserved unused Unity6.5 only."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil
receipt=Path('/tmp/cs-unity65-released-final15-r2.json')
result=json.loads(receipt.read_text()) if receipt.exists() else None
idle();entries=archive_check()
if result:
 assert result['source']==str(source) and result['archiveSha256']==prior['archiveSha256']
 assert result['phase'] in {'remove','copy','alias','done'},result
 tree_check(entries)
 if result['phase']=='remove':assert not disk.exists() and not disk.is_symlink()
else:
 assert not disk.exists() and not disk.is_symlink()
 tree_check(entries,complete=True)
 result={'status':'ReleaseInProgress','phase':'remove','source':str(source),'logicalArchive':str(archive),'diskArchive':str(disk),'archiveSha256':prior['archiveSha256'],'inventorySha256':prior['inventorySha256'],'rootAvailableBefore':free(source.parent),'limits':['Only unused6.5 editor becomes archived/restorable; pinned4.3 remains runnable','All optional component archives remain preserved','Restore needs adequate capacity and recreates byte-identical independent files rather than hardlinks']}
 write_json(receipt,result)
try:
 if source.exists():
  assert result['phase']=='remove';shutil.rmtree(source);fsync_dir(source.parent)
 result.update(status='RawTreeReleased_ArchiveRetained',phase='copy',rootAvailableAfterRelease=free(source.parent));write_json(receipt,result)
 if not archive.is_symlink():
  # A partial destination is accepted only after a durable owned copy phase.
  assert not disk.is_symlink()
  offset=disk.stat().st_size if disk.exists() else 0
  assert offset<=prior['archiveBytes']
  assert free(disk.parent)>prior['archiveBytes']-offset+256*1024*1024
  if offset:
   with archive.open('rb') as a,disk.open('rb') as b:
    remaining=offset
    while remaining:
     n=min(1024*1024,remaining);x=b.read(n);assert len(x)==n and x==a.read(n);remaining-=n
  with archive.open('rb') as a,disk.open('ab' if disk.exists() else 'xb') as output:
   a.seek(offset)
   for b in iter(lambda:a.read(1024*1024),b''):output.write(b)
   output.flush();os.fsync(output.fileno())
  fsync_dir(disk.parent)
 assert disk.stat().st_size==prior['archiveBytes'] and sha(disk)==prior['archiveSha256']
 result.update(status='DiskArchiveVerified',phase='alias');write_json(receipt,result)
 if not archive.is_symlink():
  temporary=archive.with_name(archive.name+'.disk-link-'+uuid.uuid4().hex)
  temporary.symlink_to(disk);os.replace(temporary,archive);fsync_dir(archive.parent)
 archive_check();idle()
 result.update(status='ArchivedInactiveUnity65OnDisk_ProjectPinnedEditorUnchanged',phase='done',rootAvailableAfter=free(disk.parent),tmpAvailableAfter=free(Path('/tmp')));write_json(receipt,result);print(result['status'],flush=True)
except BaseException as error:
 result.update(status='FailedRelease_VerifiedArchiveRetained',error=repr(error));write_json(receipt,result);raise
