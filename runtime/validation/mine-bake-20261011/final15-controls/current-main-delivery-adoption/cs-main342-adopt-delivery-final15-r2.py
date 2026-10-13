"""Adopt only a completed, reviewed derivative; preserve every replaced byte."""
from pathlib import Path
import hashlib,json,shutil,os,sys
root=Path('/workspace/critical-shift-spawn-runtime');stage=Path('/tmp/cs-compact-main342-geometry-final15')
target=root/'runtime/unity/Assets/CriticalShift/Generated/Spawn';backup=Path('/tmp/cs-main342-prior-delivery-final15')
receipt=Path('/tmp/cs-main342-adoption-final15.json')
plan_only='--plan-only' in sys.argv
assert not backup.exists() and not receipt.exists()
assert not (root/'runtime/unity/Temp/UnityLockfile').exists()
prep=json.loads(Path('/tmp/cs-current-main-surface-preparation-final15-r6.json').read_text())
assert prep['status']=='CompletedFreshCurrentMainSurfaces_NotNativeUnityAccepted'
source=json.loads(Path('/tmp/cs-main342-source-renders-native-final15-r2.json').read_text())
assert source['status']=='PassedCurrentSourceRenderTechnicalChecks_IndependentComparisonPending'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
mapping=json.loads((stage/'map-bindings.json').read_text())
assert prep['manifestSha256']==sha(stage/'map-bindings.json')
source_proof_path=Path('/tmp/cs-main342-source-renders-final15-r2/provenance.json')
assert source['provenanceSha256']==sha(source_proof_path)
source_proof=json.loads(source_proof_path.read_text())
snapshot=Path('/tmp/cs-compact-main342-final14')
assert source_proof['mapCommit']==mapping['mapCommit']
assert source_proof['sourceRecords']==mapping['sources']
assert source_proof['sourceSha256']==sha(snapshot/'combined-runtime-source.blend')
assert source_proof['configSha256']==sha(snapshot/'map-config.json')
assert not stage.is_symlink() and not target.is_symlink()
assert not any(p.is_symlink() for p in stage.rglob('*'))
assert not any(p.is_symlink() for p in target.rglob('*'))
assert mapping['mapCommit']=='342af0003fec9dbe80b5acb40d1477c23b5a3169' and len(mapping['rooms'])==14
def records(value):
 if isinstance(value,dict):
  if 'file' in value and 'sha256' in value:yield value
  for v in value.values():yield from records(v)
 elif isinstance(value,list):
  for v in value:yield from records(v)
rig=json.loads((stage/'rig-bindings.json').read_text())
for r in list(records(mapping))+list(records(rig)):
 assert not Path(r['file']).is_absolute() and '..' not in Path(r['file']).parts
 assert sha(stage/r['file'])==r['sha256'],r['file']
for r in mapping['rooms']:
 for key,digest in [('mesh','meshSha256'),('collision','collisionSha256')]:assert sha(stage/r[key])==r[digest]
assert sha(stage/'CrewWorker.fbx')==rig['fbx_sha256'] and sha(stage/rig['animationFile'])==rig['animationSha256']
package=next(p for p in mapping['materials'] if p['room']=='mine');spots=package['contextSpotLights']
assert len(spots)==6 and {s['name'] for s in spots}=={s['name'] for s in next(r for r in mapping['rooms'] if r['key']=='front-end-area')['lights'] if s['type']=='SPOT'}
changes=[]
for p in sorted(stage.rglob('*')):
 relative=p.relative_to(stage);current=target/relative
 if p.is_dir():
  assert not current.exists() or current.is_dir(),str(current)
  continue
 if not p.is_file():continue
 assert not current.exists() or current.is_file(),str(current)
 digest=sha(p)
 if current.is_file() and sha(current)==digest:continue
 changes.append({'path':str(relative),'newSha256':digest,'oldSha256':sha(current) if current.is_file() else None,
  'newBytes':p.stat().st_size,'oldBytes':current.stat().st_size if current.is_file() else 0})
backup_bytes=sum(r['oldBytes'] for r in changes)
delta=0;peak=0
for r in changes:
 # Conservative file-replacement estimate: new content may coexist with old.
 peak=max(peak,delta+r['newBytes']);delta+=r['newBytes']-r['oldBytes'];peak=max(peak,delta)
free=lambda p:os.statvfs(p).f_bavail*os.statvfs(p).f_frsize
capacity={'backupBytes':backup_bytes,'rootPeakAdditionalBytes':peak,'rootFinalDeltaBytes':delta,
 'tmpAvailableBytes':free(Path('/tmp')),'rootAvailableBytes':free(root),'marginBytes':128*1024*1024}
assert capacity['tmpAvailableBytes']>backup_bytes+capacity['marginBytes'],capacity
assert capacity['rootAvailableBytes']>peak+capacity['marginBytes'],capacity
plan_path=Path('/tmp/cs-main342-adoption-plan-final15.json')
plan={'status':'CompleteValidatedChangePlanBeforeMutation','changes':changes,'capacity':capacity,
 'stagedManifestSha256':sha(stage/'map-bindings.json'),'sourceProvenanceSha256':sha(source_proof_path)}
if plan_only:
 assert not plan_path.exists();plan_path.write_text(json.dumps(plan,indent=2)+'\n');print('Validated plan only; no asset mutation',flush=True);raise SystemExit(0)
assert plan_path.exists()
reviewed_plan=json.loads(plan_path.read_text())
# Capacity may vary, but every changed file, source and manifest must remain identical.
assert reviewed_plan['changes']==plan['changes'] and reviewed_plan['stagedManifestSha256']==plan['stagedManifestSha256'] and reviewed_plan['sourceProvenanceSha256']==plan['sourceProvenanceSha256']
assert json.loads(Path('/tmp/cs-mine-library-artifacts-restored-final15.json').read_text())['status']=='RestoredExactCacheBytesModesAndLinks_CacheHealthNotCertified'
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  comm=(proc/'comm').read_text().strip();process_state=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
  assert process_state=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'}),(proc.name,comm)
 except (FileNotFoundError,PermissionError):continue
backup.mkdir()
for r in changes:
 p=target/r['path']
 if r['oldSha256'] is not None:
  b=backup/r['path'];b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,b);assert sha(b)==r['oldSha256']
result={'status':'PreservedPriorBytesBeforeAdoption','mapCommit':mapping['mapCommit'],'changes':changes,
 'capacity':capacity,'changePlanSha256':sha(plan_path),
 'preparationStateSha256':sha(Path('/tmp/cs-current-main-surface-preparation-final15-r6.json')),
 'limits':['Canonical Blender/Claude assembly untouched','Unity scene must be rebuilt/baked and reviewed; copied derivatives are not acceptance']}
receipt.write_text(json.dumps(result,indent=2)+'\n')
try:
 for r in changes:
  p=target/r['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(stage/r['path'],p);assert sha(p)==r['newSha256']
 result['status']='AdoptedVerifiedCurrent13Derivatives_AwaitingNativeRebuild';receipt.write_text(json.dumps(result,indent=2)+'\n')
except BaseException:
 for r in changes:
  p=target/r['path']
  if r['oldSha256'] is None:p.unlink(missing_ok=True)
  else:shutil.copyfile(backup/r['path'],p);assert sha(p)==r['oldSha256']
 result['status']='AdoptionFailed_RestoredPriorBytes';receipt.write_text(json.dumps(result,indent=2)+'\n');raise
