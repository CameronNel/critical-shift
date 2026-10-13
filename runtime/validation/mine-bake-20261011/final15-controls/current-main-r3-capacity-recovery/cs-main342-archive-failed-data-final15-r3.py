"""Create exact, independently checkable archives; original failed data retained."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import subprocess,tarfile
receipt=Path('/tmp/cs-main342-failed-data-archives-final15-r3.json');assert not receipt.exists()
items=[(Path('/tmp/cs-mine-unity-temp-f641ef18fa1748dc8e311fa133c01ef7'),Path('/tmp/cs-main342-native-r2-failed-temp-preserved-final15-r3.tar.zst')),(Path('/workspace/critical-shift-spawn-runtime/runtime/out/mine-bake-audit/final13-failed-native-oom'),source.parent/'cache-archives/cs-mine-final13-failed-native-data-preserved-final15-r3.tar.zst')]
def inventory_for(src):
 assert src.is_dir() and not src.is_symlink() and src.parent.resolve()==src.parent
 records={}
 for p in [src,*src.rglob('*')]:
  info=p.lstat();r={'mode':stat.S_IMODE(info.st_mode),'uid':info.st_uid,'gid':info.st_gid}
  if stat.S_ISREG(info.st_mode):r.update(type='file',bytes=info.st_size,sha256=sha(p))
  elif stat.S_ISDIR(info.st_mode):r['type']='dir'
  else:assert stat.S_ISLNK(info.st_mode);r.update(type='symlink',link=os.readlink(p))
  records[str(p.relative_to(src.parent))]=r
 return records
result={'status':'ArchivingFailedData_OriginalsRetained','items':[],'limits':['Only two specifically scoped inactive failure directories','Exact bytes/modes/ownership/linktext retained; original hardlink inode sharing not reconstructed','Archive preparation does not release any original or certify native lighting']};write_json(receipt,result)
try:
 for src,output in items:
  idle();records=inventory_for(src);raw=sum(r.get('bytes',0) for r in records.values());assert not output.exists() and not output.is_symlink();assert free(output.parent)>raw+256*1024*1024
  record={'source':str(src),'archive':str(output),'rawBytes':raw,'inventory':records,'status':'Preparing'};result['items'].append(record);write_json(receipt,result)
  tar_process=None;compress_process=None;decompress_process=None
  try:
   with output.open('xb') as encoded:
    tar_process=subprocess.Popen(['tar','--hard-dereference','-cf','-','-C',str(src.parent),src.name],stdout=subprocess.PIPE)
    compress_process=subprocess.Popen(['zstd','-5','-T2','-q'],stdin=tar_process.stdout,stdout=encoded);tar_process.stdout.close()
    assert compress_process.wait()==0 and tar_process.wait()==0;encoded.flush();os.fsync(encoded.fileno())
   fsync_dir(output.parent);decompress_process=subprocess.Popen(['zstd','-dc',str(output)],stdout=subprocess.PIPE);seen=set()
   with tarfile.open(fileobj=decompress_process.stdout,mode='r|') as archive_stream:
    for member in archive_stream:
     name=member.name.rstrip('/');assert name in records and name not in seen;seen.add(name);r=records[name]
     assert member.mode==r['mode'] and member.uid==r['uid'] and member.gid==r['gid']
     if r['type']=='dir':assert member.isdir()
     elif r['type']=='symlink':assert member.issym() and member.linkname==r['link']
     else:
      assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();file=archive_stream.extractfile(member)
      for block in iter(lambda:file.read(1024*1024),b''):h.update(block)
      assert h.hexdigest()==r['sha256']
   assert decompress_process.wait()==0 and seen==set(records);assert inventory_for(src)==records
   record.update(status='VerifiedCompleteArchive_OriginalRetained',archiveBytes=output.stat().st_size,archiveSha256=sha(output));write_json(receipt,result)
  except BaseException:
   for proc in [tar_process,compress_process,decompress_process]:
    if proc and proc.poll() is None:proc.terminate()
   for proc in [tar_process,compress_process,decompress_process]:
    if proc:
     try:proc.wait(timeout=10)
     except subprocess.TimeoutExpired:proc.kill();proc.wait()
   raise
 idle();result['status']='VerifiedBothFailedDataArchives_OriginalsRetained';write_json(receipt,result);print(result['status'],flush=True)
except BaseException as error:
 result.update(status='FailedArchivePreparation_OriginalsRetained',error=repr(error));write_json(receipt,result);raise
