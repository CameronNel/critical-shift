"""Prepare verified lossless inactive-editor archive. No tree deletion in this phase."""
from pathlib import Path
import os,stat,json,hashlib,subprocess,tarfile,time,uuid,traceback
source=Path('/home/agent/.local/share/critical-shift/toolchain/unity-6000.6.5f1')
archive=Path('/tmp/cs-unity6000.6.5f1-preserved-final15.tar.zst');state=Path('/tmp/cs-unity65-preserved-final15.json');inventory=Path('/tmp/cs-unity65-inventory-final15.json')
assert not archive.exists() and not state.exists() and not inventory.exists() and source.is_dir() and not source.is_symlink()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write_json(path,value):
 temporary=path.with_name(path.name+'.atomic-'+uuid.uuid4().hex)
 with temporary.open('x') as output:
  output.write(json.dumps(value,indent=2)+'\n');output.flush();os.fsync(output.fileno())
 os.replace(temporary,path)
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  comm=(proc/'comm').read_text().strip();s=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
  assert s=='Z' or (not comm.startswith('Unity Main') and comm not in {'Unity','blender','LightBaker','UnityShaderComp'})
 except (FileNotFoundError,PermissionError):continue
pinned=[Path('/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'),Path('/home/agent/.local/share/critical-shift/toolchain/dotnet/dotnet')]
pins={str(p):sha(p) for p in pinned};result={'status':'InventoryingInactiveUnity65_StillInstalled','source':str(source),'archive':str(archive),'pinnedToolHashes':pins,'pinScope':'Required4.3 Editor binary and standalone dotnet launcher only; not wholeSDK tree','tmpAvailableBytes':os.statvfs('/tmp').f_bavail*os.statvfs('/tmp').f_frsize,'baselineMemoryBytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'baselineMemoryEvents':Path('/sys/fs/cgroup/memory.events').read_text()};write_json(state,result)
tarProcess=None;zstdProcess=None;decompressProcess=None
try:
 entries={}
 for p in [source,*sorted(source.rglob('*'))]:
  s=p.lstat();rel=p.relative_to(source.parent);r={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  if stat.S_ISREG(s.st_mode):r.update(type='file',bytes=s.st_size,sha256=sha(p),originalHardlinkCount=s.st_nlink)
  elif stat.S_ISDIR(s.st_mode):r.update(type='dir')
  elif stat.S_ISLNK(s.st_mode):r.update(type='symlink',link=os.readlink(p))
  else:raise RuntimeError('Unexpected tool entry type: '+str(p))
  entries[str(rel)]=r
 raw=sum(r.get('bytes',0) for r in entries.values());write_json(inventory,{'entries':entries,'rawBytes':raw})
 result.update(status='CompressingInactiveUnity65_StillInstalled',rawBytes=raw,inventorySha256=sha(inventory));write_json(state,result);print('Inventory complete',len(entries),raw,flush=True)
 # Store regular bytes independently even for the nine hardlinked files; restoration
 # preserves bytes/modes, not original internal/external inode sharing.
 tarProcess=subprocess.Popen(['tar','--hard-dereference','-cf','-','-C',str(source.parent),source.name],stdout=subprocess.PIPE)
 with archive.open('xb') as output:zstdProcess=subprocess.Popen(['zstd','-T2','-5','-c'],stdin=tarProcess.stdout,stdout=output)
 tarProcess.stdout.close();assert zstdProcess.wait()==0 and tarProcess.wait()==0
 with archive.open('rb') as f:os.fsync(f.fileno())
 seen=set();decompressProcess=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE)
 with tarfile.open(fileobj=decompressProcess.stdout,mode='r|') as stream:
  for member in stream:
   name=member.name.rstrip('/');assert name in entries and name not in seen;seen.add(name);r=entries[name]
   assert member.mode==r['mode'] and member.uid==r['uid'] and member.gid==r['gid']
   if r['type']=='file':
    assert member.isfile() and member.size==r['bytes'];h=hashlib.sha256();f=stream.extractfile(member)
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    assert h.hexdigest()==r['sha256'],name
   elif r['type']=='dir':assert member.isdir()
   else:assert member.issym() and member.linkname==r['link']
 assert decompressProcess.wait()==0 and seen==set(entries)
 for p,d in pins.items():assert sha(Path(p))==d
 result.update(status='VerifiedInactiveUnity65Archive_OriginalTreeStillInstalled',archiveBytes=archive.stat().st_size,archiveSha256=sha(archive),entries=len(entries),limits=['Required6000.4.3 editor and SDK untouched','No tree deletion in archive phase','Restore preserves all file bytes/modes/uid/gid/link text; original file inode sharing is not required or recreated'])
 write_json(state,result);print(result['status'],result['archiveBytes'],flush=True)
except BaseException as error:
 for child in [tarProcess,zstdProcess,decompressProcess]:
  if child is not None:
   if child.poll() is None:child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
 result.update(status='FailedArchivePreparation_OriginalTreeRetained',error=repr(error),traceback=traceback.format_exc())
 write_json(state,result);raise
