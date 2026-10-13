from pathlib import Path
import hashlib,json,subprocess,runpy,os
root=Path('/workspace/critical-shift-spawn-runtime');dest=Path('/tmp/cs-compact-main342-final14');f=dest/'staged-sources.json';s=json.loads(f.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gsha=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
# Twelve exact main screen assets; avoid the builder's blank-image fallback.
for r in json.loads(Path('/tmp/cs-compact-main342-screen-metadata-final14.json').read_text())['files']:
 b=r['content'].encode();assert gsha(b)==r['gitBlobSha'];kv=dict(l.split(' ',1) for l in r['content'].splitlines());p=dest/'map'/r['path'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
 with p.open('xb') as h:subprocess.run(['git','lfs','smudge'],input=b,stdout=h,cwd=root,check=True)
 expected=kv['oid'].removeprefix('sha256:');assert sha(p)==expected and p.stat().st_size==int(kv['size']);s['records'].append({'path':r['path'],'source_commit':r['sourceCommit'],'gitBlobSha':r['gitBlobSha'],'sha256':expected,'bytes':p.stat().st_size})
f.write_text(json.dumps(s,indent=2)+'\n')
helper=dest/'build-runtime-derivative.py';assert not helper.exists();helper.write_text('''from pathlib import Path
import bpy,json,hashlib,runpy
root=Path('/tmp/cs-compact-main342-final14');sources=json.loads((root/'staged-sources.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(root/'map'/r['path'])==r['sha256'] for r in sources['records'])
layout=runpy.run_path(str(root/'map/sections/facility-assembly/combined/build_compact_map.py'),run_name='cs_runtime_layout');bm=layout['BM'];rooms=bm.ROOMS
assert len(rooms)==13 and len({r[0] for r in rooms})==13
assert next(r for r in rooms if r[0]=='mine')[3]==(-14.4,-41.0,0.0)
config={'map_commit':sources['mainCommit'],'assembly_builder':'sections/facility-assembly/combined/build_compact_map.py','assembly_dependencies':['sections/facility-assembly/combined/build_combined_map.py','sections/facility-assembly/combined/reactor_links.py'],'rooms':rooms,'sources':sources['records'],'spawn_omitted':bm.OMIT.get('spawn-room',[]),'exterior_skins':bm.EXTERIOR_SKINS,'turbine_commit':sources['turbineCommit']}
assert all((root/'map/sections/facility-assembly/sources'/r[1]).resolve().is_file() for r in rooms)
bm.build('compliance-dock',str(root/'combined-runtime-source.blend'))
assert all(bpy.data.objects.get('ROOM_'+r[0]) is not None for r in rooms)
local=[o for o in bpy.data.collections['COMBINED_MAP'].all_objects if o.library is None and not o.name.startswith('ROOM_')]
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()]
if missing:raise ValueError('Current map has missing external images: '+repr(missing))
assert all(sha(root/'map'/r['path'])==r['sha256'] for r in sources['records'])
(root/'map-config.json').write_text(json.dumps(config,indent=2)+'\\n')
(root/'build-receipt.json').write_text(json.dumps({'status':'CurrentCompact13SourceDerivativeBuilt_NotUnityAccepted','mapCommit':sources['mainCommit'],'sourceSha256':sha(root/'combined-runtime-source.blend'),'configSha256':sha(root/'map-config.json'),'sourceRecords':sources['records'],'rooms':[r[0] for r in rooms],'localAssemblyObjects':[{'name':o.name,'type':o.type} for o in local],'missingExternalImages':missing,'limits':['Build/source preservation only, not geometry/render/Unity/playability acceptance','Local halls/concourse/placeholders must be delivered too; old exporter room-only loop would omit them']},indent=2)+'\\n');print('CS_CURRENT_COMPACT_SOURCE_BUILT',len(rooms),len(local),flush=True)
''')
command=['/home/agent/.local/bin/blender','-b','--disable-autoexec','--python-exit-code','1','-t','4','--python',str(helper)]
with (dest/'build.log').open('x') as h:r=subprocess.run(command,cwd=root,stdout=h,stderr=subprocess.STDOUT)
(dest/'build-wrapper.json').write_text(json.dumps({'returncode':r.returncode,'command':command,'helperSha256':sha(helper),'limits':['No canonical/Claude files changed; Source construction is not Unity validation']},indent=2)+'\n');assert r.returncode==0
