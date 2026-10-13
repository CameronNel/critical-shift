from pathlib import Path
import hashlib,json,os,stat,subprocess,tarfile,shutil
root=Path('/workspace/critical-shift-spawn-runtime');alias=root/'runtime/unity/Library'
library=Path('/dev/shm/critical-shift-spawn-library');cache=library/'Artifacts'
archive=Path('/tmp/cs-mine-library-artifacts-preserved-final15.tar.zst');receipt=Path('/tmp/cs-mine-library-artifacts-preserved-final15.json')
assert alias.is_symlink() and alias.resolve()==library and cache.is_dir() and not cache.is_symlink()
assert not archive.exists() and not receipt.exists()
processes=subprocess.check_output(['ps','-eo','pid,stat,args'],text=True)
assert not any(' Z' not in line and any(name in line for name in ['Editor/Unity','LightBaker','UnityShaderCompiler']) for line in processes.splitlines()),'Native process still active'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
records={}
for p in [cache,*sorted(cache.rglob('*'))]:
 mode=p.lstat().st_mode;relative=str(p.relative_to(library));r={'mode':stat.S_IMODE(mode)}
 if stat.S_ISLNK(mode):r.update(type='symlink',link=os.readlink(p))
 elif stat.S_ISREG(mode):r.update(type='file',bytes=p.stat().st_size,sha256=sha(p))
 elif stat.S_ISDIR(mode):r.update(type='directory')
 else:raise RuntimeError('Unexpected cache entry '+str(p))
 records[relative]=r
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  for fd in (proc/'fd').iterdir():
   try:link=os.readlink(fd)
   except OSError:continue
   assert not link.startswith(str(cache)+'/'),(proc.name,link)
 except (FileNotFoundError,PermissionError):continue
baseline={'memoryCurrent':int(Path('/sys/fs/cgroup/memory.current').read_text()),'memoryStat':Path('/sys/fs/cgroup/memory.stat').read_text(),'memoryEvents':Path('/sys/fs/cgroup/memory.events').read_text()}
receipt.write_text(json.dumps({'status':'InventoriedOwnedInactiveCache_BeforeArchive','entries':records,'baseline':baseline},indent=2)+'\n')
subprocess.run(['tar','--zstd','-cf',str(archive),'-C',str(library),'Artifacts'],check=True)
pipe=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE)
seen=set()
with tarfile.open(fileobj=pipe.stdout,mode='r|') as stream:
 for member in stream:
  name=member.name.rstrip('/');assert name in records and name not in seen,name;seen.add(name);r=records[name];assert member.mode==r['mode']
  if r['type']=='file':
   assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();f=stream.extractfile(member)
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   assert h.hexdigest()==r['sha256'],name
  elif r['type']=='symlink':assert member.issym() and member.linkname==r['link'],name
  else:assert member.isdir(),name
assert pipe.wait()==0 and seen==set(records)
assert all(sha(library/n)==r['sha256'] for n,r in records.items() if r['type']=='file')
result={'status':'ArchiveExactEntriesAndBytesVerifiedBeforeRelease','archive':str(archive),'archiveSha256':sha(archive),'archiveBytes':archive.stat().st_size,'cacheBytes':sum(r.get('bytes',0) for r in records.values()),'entries':records,'baseline':baseline,'limits':['Owned inactive Unity import cache only; Source and runtime assets untouched','Restore exact archive before Unity/native work; failed mine bake remains failed']}
receipt.write_text(json.dumps(result,indent=2)+'\n')
shutil.rmtree(cache);cache.mkdir(mode=records['Artifacts']['mode'])
result.update(status='ReleasedVerifiedInactiveCache_ExactArchivePreserved',after={'memoryCurrent':int(Path('/sys/fs/cgroup/memory.current').read_text()),'memoryStat':Path('/sys/fs/cgroup/memory.stat').read_text(),'memoryEvents':Path('/sys/fs/cgroup/memory.events').read_text()})
receipt.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['cacheBytes'],result['archiveBytes'],flush=True)
