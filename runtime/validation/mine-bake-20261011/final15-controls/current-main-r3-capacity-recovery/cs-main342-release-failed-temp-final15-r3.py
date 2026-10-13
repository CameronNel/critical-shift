"""Release only verified failed tmp data; discard a duplicate archive, retain Root originals."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil
state_path=Path('/tmp/cs-main342-failed-data-archives-final15-r3.json');state=json.loads(state_path.read_text());assert state['status']=='VerifiedBothFailedDataArchives_OriginalsRetained'
assert [i['archive'] for i in state['items']]==['/tmp/cs-main342-native-r2-failed-temp-preserved-final15-r3.tar.zst',str(source.parent/'cache-archives/cs-mine-final13-failed-native-data-preserved-final15-r3.tar.zst')]
assert [i['source'] for i in state['items']]==['/tmp/cs-mine-unity-temp-f641ef18fa1748dc8e311fa133c01ef7','/workspace/critical-shift-spawn-runtime/runtime/out/mine-bake-audit/final13-failed-native-oom']
proof_path=Path('/tmp/cs-main342-failed-archives-independent-final15-r3.json');proof=json.loads(proof_path.read_text());assert proof['status']=='PassedExactTwoFailedDataArchivesAndOriginalTrees' and proof['archivePreparationReceiptSha256']==sha(state_path)
receipt=Path('/tmp/cs-main342-failed-temp-released-final15-r3.json');result=json.loads(receipt.read_text()) if receipt.exists() else None
project_temp=Path('/workspace/critical-shift-spawn-runtime/runtime/unity/Temp')
def verify_tree(item,subset=False):
 p=Path(item['source']);assert not p.is_symlink();records=item['inventory'];actual=[p,*p.rglob('*')] if p.exists() else []
 names=set()
 for x in actual:
  name=str(x.relative_to(p.parent));assert name in records and not x.is_symlink();names.add(name);r=records[name];s=x.lstat();assert stat.S_IMODE(s.st_mode)==r['mode'] and s.st_uid==r['uid'] and s.st_gid==r['gid']
  if r['type']=='file':assert x.is_file() and s.st_size==r['bytes'] and sha(x)==r['sha256']
  else:assert r['type']=='dir' and x.is_dir()
 if not subset:assert names==set(records)
def idle_scoped():
 idle();roots=[i['source'] for i in state['items']]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   for fd in (proc/'fd').iterdir():
    try:
     target=os.readlink(fd);assert not any(target==r or target.startswith(r+'/') for r in roots),(proc.name,target)
    except (FileNotFoundError,PermissionError):continue
  except (FileNotFoundError,PermissionError):continue
idle_scoped();temp,old=state['items'];encoded=Path(temp['archive']);assert encoded.is_file() and not encoded.is_symlink() and sha(encoded)==temp['archiveSha256'] and encoded.stat().st_size==temp['archiveBytes']
verify_tree(old)
if not result:
 verify_tree(temp);result={'status':'ReleasingVerifiedFailureData','phase':'discard_duplicate','preparationReceiptSha256':sha(state_path),'independentReceiptSha256':sha(proof_path),'limits':['OldRoot failed data stays exact and installed; only redundant new archive discarded; restore index1 unavailable until archive regenerated from original','NewR2 failed Temp retained in exact validated archive and restore recipe','No canonical source or current immutable derivative changed']};write_json(receipt,result)
else:assert result['preparationReceiptSha256']==sha(state_path) and result['phase'] in {'discard_duplicate','remove_temp','done'}
try:
 duplicate=Path(old['archive'])
 if duplicate.exists():
  assert result['phase']=='discard_duplicate' and not duplicate.is_symlink() and sha(duplicate)==old['archiveSha256'];verify_tree(old)
  duplicate.unlink();fsync_dir(duplicate.parent)
 result.update(status='OriginalRootFailureIntact_DuplicateArchiveDiscarded',phase='remove_temp');write_json(receipt,result)
 if project_temp.is_symlink():
  assert os.readlink(project_temp)==temp['source'];project_temp.unlink();fsync_dir(project_temp.parent)
 else:assert not project_temp.exists()
 idle_scoped();verify_tree(temp,subset=True)
 if Path(temp['source']).exists():shutil.rmtree(temp['source']);fsync_dir(Path(temp['source']).parent)
 verify_tree(old);assert sha(encoded)==temp['archiveSha256']
 result.update(status='FailedTmpArchived_RootHistoricalOriginalRetained',phase='done',tempArchiveAvailable=True,rootDuplicateArchiveAvailable=False,rootOriginalAvailable=True,rootAvailableBytes=free(source.parent),tmpAvailableBytes=free(Path('/tmp')),shmemBytes=int(dict(x.split() for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())['shmem']));write_json(receipt,result);print(result['status'],flush=True)
except BaseException as e:
 result.update(status='FailedRelease_ExactArchiveOrOriginalRetained',error=repr(e));write_json(receipt,result);raise
