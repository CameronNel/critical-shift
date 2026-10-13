from pathlib import Path
import hashlib,json
root=Path('/tmp/cs-compact-main342-final14');f=root/'staged-sources.json';s=json.loads(f.read_text());known={'build_combined_map.py':'9c249aea2159287157074bb03152d3cd9eaa5b4d','build_compact_map.py':'fc4ff05be675fcfdcf98355682d620f281f98b2b','reactor_links.py':'b253f54782c828af9ae1f9d464ccc7939b653ea4','AGENT_READ_FIRST.md':'6e7dc275da2bc59107b5af96a4317e8115a165c7','COMPACT_MAP.md':'acbc6fea046832cdb0006bdb3c39c855f3cd1c81'}
for r in s['records']:
 if Path(r['path']).name not in known:continue
 p=root/'map'/r['path'];b=p.read_bytes();h=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert h==known[p.name],(p.name,h);r['gitBlobSha']=h
assert all(hashlib.sha256((root/'map'/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in s['records'])
f.write_text(json.dumps(s,indent=2)+'\n');print('22 sources exact hash+git blob pins verified')
