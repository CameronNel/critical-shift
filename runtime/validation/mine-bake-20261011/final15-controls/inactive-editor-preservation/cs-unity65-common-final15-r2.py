from pathlib import Path
import hashlib,json,os,stat,uuid
prior_path=Path('/tmp/cs-unity65-preserved-final15.json')
prior=json.loads(prior_path.read_text())
source=Path('/home/agent/.local/share/critical-shift/toolchain/unity-6000.6.5f1')
archive=Path('/tmp/cs-unity6000.6.5f1-preserved-final15.tar.zst')
disk=source.parent/'cache-archives/cs-unity6000.6.5f1-preserved-final15.tar.zst'
inventory=Path('/tmp/cs-unity65-inventory-final15.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def fsync_dir(p):
 fd=os.open(p,os.O_DIRECTORY|os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def write_json(path,value):
 t=path.with_name(path.name+'.atomic-'+uuid.uuid4().hex)
 with t.open('x') as f:f.write(json.dumps(value,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 os.replace(t,path);fsync_dir(path.parent)
def idle():
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   comm=(proc/'comm').read_text().strip();s=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
   assert s=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'}),comm
   for fd in (proc/'fd').iterdir():
    try:assert not os.readlink(fd).startswith(str(source)+'/'),(proc.name,str(fd))
    except (FileNotFoundError,PermissionError):continue
  except (FileNotFoundError,PermissionError):continue
 for p,d in prior['pinnedToolHashes'].items():assert sha(Path(p))==d,p
def archive_check():
 assert prior['status']=='VerifiedInactiveUnity65Archive_OriginalTreeStillInstalled' and prior['source']==str(source) and prior['archive']==str(archive)
 assert source.parent.resolve()==source.parent and disk.parent.resolve()==disk.parent
 assert sha(inventory)==prior['inventorySha256']
 if archive.is_symlink():assert os.readlink(archive)==str(disk) and disk.is_file() and not disk.is_symlink()
 else:assert archive.is_file()
 assert archive.stat().st_size==prior['archiveBytes'] and sha(archive)==prior['archiveSha256']
 independent=json.loads(Path('/tmp/cs-unity65-archive-independent-final15.json').read_text())
 assert independent['status']=='PassedExactInactiveUnity65ArchiveAndOriginalTree' and independent['archiveSha256']==prior['archiveSha256'] and independent['inventorySha256']==prior['inventorySha256']
 entries=json.loads(inventory.read_text())['entries']
 for name in entries:
  rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]==source.name
 return entries

def tree_check(entries,complete=False):
 assert not source.is_symlink()
 actual=[source,*source.rglob('*')] if source.exists() else []
 names=set()
 for p in actual:
  name=str(p.relative_to(source.parent));assert name in entries,name;names.add(name);r=entries[name];s=p.lstat()
  assert stat.S_IMODE(s.st_mode)==r['mode'] and s.st_uid==r['uid'] and s.st_gid==r['gid'],name
  if r['type']=='file':assert stat.S_ISREG(s.st_mode) and s.st_size==r['bytes'] and sha(p)==r['sha256'],name
  elif r['type']=='dir':assert stat.S_ISDIR(s.st_mode),name
  else:assert stat.S_ISLNK(s.st_mode) and os.readlink(p)==r['link'],name
 if complete:assert names==set(entries)
 return names

def free(p):return os.statvfs(p).f_bavail*os.statvfs(p).f_frsize
