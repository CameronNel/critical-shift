from pathlib import Path
import hashlib,json,tarfile,shutil
root=Path('/workspace/critical-shift-spawn-runtime');out=root/'runtime/out/inactive-controls-final13';out.mkdir(exist_ok=True)
names=['cs-mine-inactive-diagnostics-final10','cs-unity-asset-audit','cs-mine-wood-preview','cs-mine-cache-artifacts-final11-26','cs-mine-aov-final11-rejected-zero-aov-attempt2','cs-mine-aov-final11','cs-mine-aov-no-volume-final11']
files={};sources=[]
for name in names:
 source=Path('/tmp')/name;assert source.is_dir() and not source.is_symlink();sources.append(source)
 for p in source.rglob('*'):
  if p.is_symlink():raise RuntimeError('Unexpected inactive evidence symlink '+str(p))
  if p.is_file():
   with p.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
   files[str(p.relative_to('/tmp'))]={'sha256':digest,'bytes':p.stat().st_size}
archive=out/'evidence.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
 for p in sources:tar.add(p,arcname=p.name,recursive=True)
verified=set()
with tarfile.open(archive,'r:gz') as tar:
 for member in tar:
  if not member.isfile():continue
  if member.name not in files:raise RuntimeError('Unexpected archive member '+member.name)
  stream=tar.extractfile(member);digest=hashlib.file_digest(stream,'sha256').hexdigest();assert digest==files[member.name]['sha256'] and member.size==files[member.name]['bytes'];verified.add(member.name)
assert verified==set(files)
with archive.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
(out/'index.json').write_text(json.dumps({'status':'InactiveGeneratedEvidenceLosslesslyPreserved','archiveSha256':digest,'archiveBytes':archive.stat().st_size,'tmpBytesReleased':sum(r['bytes'] for r in files.values()),'limits':'Historical generated diagnostics and inactivecache only; no source, toolchain, Player or current reviewer inputs removed.','files':files},indent=2)+'\n')
for p in sources:shutil.rmtree(p)
print('CS_INACTIVE_EVIDENCE_PRESERVED',len(files),'files','released',sum(r['bytes'] for r in files.values()),'archive',archive.stat().st_size,flush=True)
