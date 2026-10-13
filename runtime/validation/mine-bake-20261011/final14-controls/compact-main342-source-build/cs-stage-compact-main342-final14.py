from pathlib import Path
import hashlib,json,subprocess,os,shutil
root=Path('/workspace/critical-shift-spawn-runtime');dest=Path('/tmp/cs-compact-main342-final14');assert not dest.exists();dest.mkdir();cfg=json.loads(Path('/tmp/cs-compact-main342-source-metadata-final14.json').read_text());records=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gsha=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
for r in cfg['files']:
 path=r['path'];p=dest/'map'/path;p.parent.mkdir(parents=True,exist_ok=True);pointer=r['content'];old=root/'runtime/out/spawn-export-source/map'/path
 if pointer:
  b=pointer.encode();assert gsha(b)==r['gitBlobSha'];kv=dict(l.split(' ',1) for l in pointer.splitlines());expected=kv['oid'].removeprefix('sha256:');size=int(kv['size'])
  if old.exists() and sha(old)==expected:p.symlink_to(old);method='VerifiedExistingSourceBytes'
  else:
   with p.open('xb') as f:subprocess.run(['git','lfs','smudge'],input=b,stdout=f,cwd=root,check=True)
   method='SinglePinnedLFSPointerHydration'
  assert p.stat().st_size==size and sha(p)==expected
 else:
  # The exact Git blob already exists locally; no bulk commit fetch is needed.
  b=subprocess.check_output(['git','cat-file','blob',r['gitBlobSha']],cwd=root);assert gsha(b)==r['gitBlobSha'];expected=hashlib.sha256(b).hexdigest();size=len(b)
  if old.exists() and sha(old)==expected:p.symlink_to(old);method='VerifiedExistingPlainGitSourceBytes'
  else:p.write_bytes(b);method='SinglePinnedExistingGitBlob'
 records.append({'path':path,'source_commit':r['sourceCommit'],'gitBlobSha':r['gitBlobSha'],'sha256':expected,'bytes':size,'stagingMethod':method});print(path,size,method,flush=True)
for name in ['build_compact_map.py','build_combined_map.py','reactor_links.py','AGENT_READ_FIRST.md','COMPACT_MAP.md']:
 p=dest/'map/sections/facility-assembly/combined'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path('/tmp/cs-main342-review')/name,p);records.append({'path':str(p.relative_to(dest/'map')),'source_commit':cfg['mainCommit'],'sha256':sha(p),'bytes':p.stat().st_size})
(dest/'staged-sources.json').write_text(json.dumps({'state':'PinnedCurrentMainSourcesStaged_NoBuildYet','mainCommit':cfg['mainCommit'],'turbineCommit':'e12c8e2a9c35a6888960ce08185cd3ad10898f59','records':records,'limits':['Read-only canonical source staging; old6mesh/bake proof doesnotcertify current13main','No main or Claude branch changes; compact builder authority preserved']},indent=2)+'\n')
