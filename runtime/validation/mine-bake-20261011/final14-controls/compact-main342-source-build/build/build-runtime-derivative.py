from pathlib import Path
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
(root/'map-config.json').write_text(json.dumps(config,indent=2)+'\n')
(root/'build-receipt.json').write_text(json.dumps({'status':'CurrentCompact13SourceDerivativeBuilt_NotUnityAccepted','mapCommit':sources['mainCommit'],'sourceSha256':sha(root/'combined-runtime-source.blend'),'configSha256':sha(root/'map-config.json'),'sourceRecords':sources['records'],'rooms':[r[0] for r in rooms],'localAssemblyObjects':[{'name':o.name,'type':o.type} for o in local],'missingExternalImages':missing,'limits':['Build/source preservation only, not geometry/render/Unity/playability acceptance','Local halls/concourse/placeholders must be delivered too; old exporter room-only loop would omit them']},indent=2)+'\n');print('CS_CURRENT_COMPACT_SOURCE_BUILT',len(rooms),len(local),flush=True)
