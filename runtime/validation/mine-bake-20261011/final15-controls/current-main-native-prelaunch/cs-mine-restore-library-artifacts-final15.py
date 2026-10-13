from pathlib import Path
import hashlib,json,os,stat,subprocess,tarfile
root=Path('/workspace/critical-shift-spawn-runtime');library=Path('/dev/shm/critical-shift-spawn-library');cache=library/'Artifacts'
prior_path=Path('/tmp/cs-mine-library-artifacts-preserved-final15.json');receipt=Path('/tmp/cs-mine-library-artifacts-restored-final15.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert not receipt.exists();prior=json.loads(prior_path.read_text());assert prior['status']=='ReleasedVerifiedInactiveCache_ExactArchivePreserved'
archive=Path(prior['archive']);assert sha(archive)==prior['archiveSha256'];records=prior['entries']
assert (root/'runtime/unity/Library').is_symlink() and (root/'runtime/unity/Library').resolve()==library
assert cache.is_dir() and not cache.is_symlink() and not any(cache.iterdir())
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  comm=(proc/'comm').read_text().strip();state=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
  assert state=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'}),(proc.name,comm)
 except (FileNotFoundError,PermissionError):continue
# Verify exact archive bytes/types/modes before extraction; never follow cached symlinks.
pipe=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE);seen=set()
with tarfile.open(fileobj=pipe.stdout,mode='r|') as stream:
 for member in stream:
  name=member.name.rstrip('/');assert name in records and name not in seen;seen.add(name);r=records[name]
  relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts and relative.parts[0]=='Artifacts'
  assert member.mode==r['mode']
  if r['type']=='file':
   assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();f=stream.extractfile(member)
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   assert h.hexdigest()==r['sha256'],name
  elif r['type']=='symlink':assert member.issym() and member.linkname==r['link'],name
  else:assert member.isdir(),name
assert pipe.wait()==0 and seen==set(records)
baseline={n:Path('/sys/fs/cgroup/'+n).read_text() for n in ['memory.current','memory.stat','memory.events']}
result={'status':'ExactArchiveVerifiedBeforeRestore','preservationReceiptSha256':sha(prior_path),'archiveSha256':sha(archive),'baseline':baseline};receipt.write_text(json.dumps(result,indent=2)+'\n')
subprocess.run(['tar','--zstd','-xf',str(archive),'-C',str(library)],check=True)
assert {str(p.relative_to(library)) for p in [cache,*cache.rglob('*')]}==set(records)
external=[]
for name,r in records.items():
 p=library/name;mode=p.lstat().st_mode;assert stat.S_IMODE(mode)==r['mode'],name
 if r['type']=='file':assert stat.S_ISREG(mode) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],name
 elif r['type']=='symlink':
  assert stat.S_ISLNK(mode) and os.readlink(p)==r['link'],name
  external.append({'path':name,'link':r['link'],'targetExists':p.exists()})
 else:assert stat.S_ISDIR(mode),name
assert (root/'runtime/unity/Library').resolve()==library
result.update(status='RestoredExactCacheBytesModesAndLinks_CacheHealthNotCertified',entries=len(records),externalSymlinkTargets=external,after={n:Path('/sys/fs/cgroup/'+n).read_text() for n in ['memory.current','memory.stat','memory.events']},limits=['One external target was already missing before preservation; restoration verifies link text, not missing target bytes','Unity may regenerate stale import cache; Source and runtime asset provenance remains independently checked'])
receipt.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
