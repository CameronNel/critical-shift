"""Preserve failed stash, restore exact all-active generated map before retry."""
from pathlib import Path
exec(compile(Path('/tmp/cs-unity65-common-final15-r2.py').read_text(),'/tmp/cs-unity65-common-final15-r2.py','exec'))
import shutil
root=Path('/workspace/critical-shift-spawn-runtime');generated=root/'runtime/unity/Assets/CriticalShift/Generated/Spawn';scene=generated/'AssembledMap.unity';backup=Path('/tmp/cs-bake-full-map-before-exclusion-1f9d65f228db4123ae4378d20d520cad.unity');stash=generated/'BakeRoomStash-9ee722c22cba479a8ba6dee05fa25df0';preserved=Path('/tmp/cs-main342-failed-room-stash-preserved-final15-r3');receipt=Path('/tmp/cs-main342-full-scene-recovered-final15-r3.json')
idle();assert not receipt.exists() and not preserved.exists() and generated.resolve()==generated
assert sha(backup)=='5d9718be84fc6f9c2219a14323cbfe972e4ce63d6fdf6404bb00b6126ecca9fe'
assert not (generated/'prepared-scene.json').exists();assert stash.is_dir() and not stash.is_symlink() and scene.is_file()
files=[p for p in stash.rglob('*') if p.is_file()]+[Path(str(stash)+'.meta'),scene];assert not any(p.is_symlink() for p in stash.rglob('*'))
assert {p.name for p in stash.iterdir()}=={'ExcludedRooms.unity','ExcludedRooms.unity.meta'}
preserved.mkdir();records=[]
for p in files:
 t=preserved/p.name;shutil.copy2(p,t)
 with t.open('rb') as f:os.fsync(f.fileno())
 h=sha(p);assert sha(t)==h;records.append({'original':str(p),'copy':str(t),'sha256':h,'bytes':p.stat().st_size})
fsync_dir(preserved)
result={'status':'FailedSceneAndStashPreservedBeforeRecovery','copies':records,'fullMapBackup':str(backup),'fullMapBackupSha256':sha(backup),'limits':['Generated derivative only, no canonical room/builder edits','Restores the all-active14-group scene from before Bake; no current native lighting or Player acceptance','No prepared-scene proof fabricated']};write_json(receipt,result)
try:
 temporary=scene.with_name(scene.name+'.recovery-'+uuid.uuid4().hex);shutil.copy2(backup,temporary)
 with temporary.open('rb') as f:os.fsync(f.fileno())
 assert sha(temporary)==sha(backup);os.replace(temporary,scene);fsync_dir(scene.parent)
 for record in records:assert sha(Path(record['copy']))==record['sha256']
 for p in files:
  if p!=scene:assert sha(p)==next(r['sha256'] for r in records if r['original']==str(p))
 shutil.rmtree(stash);Path(str(stash)+'.meta').unlink();fsync_dir(generated)
 assert sha(scene)==sha(backup) and not stash.exists() and not (generated/'prepared-scene.json').exists()
 result.update(status='RestoredExactAllActive14GroupDerivedScene_NativeLightingPending',sceneSha256=sha(scene));write_json(receipt,result);print(result['status'],flush=True)
except BaseException as e:
 result.update(status='FailedSceneRecovery_ExactBackupAndStashCopiesRetained',error=repr(e));write_json(receipt,result);raise
