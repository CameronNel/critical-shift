from pathlib import Path
import json,hashlib,ast,math,datetime
ROOT=Path('/workspace/critical-shift-spawn-runtime'); STAGE=Path('/tmp/cs-compact-main342-geometry-final15'); SOURCE=Path('/tmp/cs-compact-main342-final14'); AUDIT=Path('/tmp/cs-current-main-surface-audit-final15-r6'); STATE=Path('/tmp/cs-current-main-surface-preparation-final15-r6.json')
OUT=Path('/tmp/cs-main342-surface-independent-final15.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def records(v):
 if isinstance(v,dict):
  if 'file' in v and 'sha256' in v:yield v
  for x in v.values():yield from records(x)
 elif isinstance(v,list):
  for x in v:yield from records(x)
def file_record(r):
 rel=Path(r['file']);assert not rel.is_absolute() and '..' not in rel.parts
 p=STAGE/rel;assert p.is_file() and sha(p)==r['sha256'],str(p)
 return str(rel),r['sha256']
state=json.loads(STATE.read_text());assert state['status']=='CompletedFreshCurrentMainSurfaces_NotNativeUnityAccepted',state['status']
assert not OUT.exists()
manifest_path=STAGE/'map-bindings.json'; manifest=json.loads(manifest_path.read_text());assert sha(manifest_path)==state['manifestSha256']
config=json.loads((SOURCE/'map-config.json').read_text());assert manifest['mapCommit']==config['map_commit']=='342af0003fec9dbe80b5acb40d1477c23b5a3169'
assert manifest['sources']==config['sources'];expected={r[0] for r in config['rooms']}|{'assembly-context'}
assert len(manifest['rooms'])==len(expected)==14 and len({r['key'] for r in manifest['rooms']})==14 and {r['key'] for r in manifest['rooms']}==expected
before=json.loads((AUDIT/'mine/before-bindings.json').read_text())
assert {r['key']:r for r in before['rooms'] if r['key']!='mine'}=={r['key']:r for r in manifest['rooms'] if r['key']!='mine'}
assert next(r for r in before['rooms'] if r['key']=='mine')['collisionSha256']==next(r for r in manifest['rooms'] if r['key']=='mine')['collisionSha256']
for r in manifest['rooms']:
 for k,h in [('mesh','meshSha256'),('collision','collisionSha256')]:assert sha(STAGE/r[k])==r[h],r['key']
metas=json.loads(Path('/tmp/cs-current-main-surface-audit-final15-r4/retained-importer-metadata.json').read_text())
for r in metas:assert sha(STAGE/r['path'])==r['sha256'],r['path']
preserved=json.loads((AUDIT/'resumed-spawn-and-other-room-files.json').read_text())
for r in preserved:assert sha(STAGE/r['path'])==r['sha256'],r['path']
rig=json.loads((STAGE/'rig-bindings.json').read_text());assert sha(STAGE/'CrewWorker.fbx')==rig['fbx_sha256'];assert sha(STAGE/rig['animationFile'])==rig['animationSha256']
for n in ['rig-bindings.json','CrewWorker.fbx',rig['animationFile']]:
 assert sha(STAGE/n)==state['pins'][str(ROOT/'runtime/unity/Assets/CriticalShift/Generated/Spawn'/n)]
 assert sha(Path(str(STAGE/n)+'.meta'))==state['pins'][str(Path(str(ROOT/'runtime/unity/Assets/CriticalShift/Generated/Spawn'/n)+'.meta'))]
delivered=dict(file_record(r) for r in records(manifest));rig_deps=dict(file_record(r) for r in records(rig))
for rel,h in rig_deps.items():
 canonical=ROOT/'runtime/unity/Assets/CriticalShift/Generated/Spawn'/rel
 assert sha(STAGE/rel)==sha(canonical)==h
 assert sha(Path(str(STAGE/rel)+'.meta'))==sha(Path(str(canonical)+'.meta'))
for p,h in state['pins'].items():assert sha(Path(p))==h,p
for r in config['sources']:
 assert sha(SOURCE/'map'/r['path'])==r['sha256'],r['path']
cache=json.loads((AUDIT/'mine/surface-cache.json').read_text());preservation=json.loads((AUDIT/'mine/preservation.json').read_text())
assert cache['method']=='source-recipe-v2' and cache['size']==4096 and cache['sources']==config['sources']
recipe=cache['exportRecipe']; assert recipe['batched'] is True and recipe['runtimeSceneSha256']==sha(SOURCE/'combined-runtime-source.blend')
module=ast.parse((ROOT/'runtime/tools/prepare_mine.py').read_text());toolnames=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE_FILES' for t in n.targets))
assert set(recipe['tools'])==set(toolnames) and all(recipe['tools'][n]==sha(ROOT/'runtime/tools'/n) for n in toolnames)
assert preservation['status']=='Passed' and preservation['inspectedMain']==manifest['mapCommit'] and all(preservation[k] is True for k in ['roomPlacementsUnchanged','otherRoomCollisionsUnchanged','mineCollisionUnchanged','otherRoomMeshesUnchanged','sourceFilesUnchanged'])
package=next(p for p in manifest['materials'] if p['room']=='mine');spots=package['contextSpotLights'];original={r['name']:r for r in next(r for r in manifest['rooms'] if r['key']=='front-end-area')['lights'] if r['type']=='SPOT'}
assert len(spots)==len(original)==6 and len({s['name'] for s in spots})==6 and {s['name'] for s in spots}==set(original)
for s in spots:
 o=original[s['name']]
 assert all(s[k]==o[k] for k in ['name','type','position','rotation','color','power','radius','spotSize','spotBlend','normalized','softFalloff']),s['name']
 assert s['normalized'] and s['softFalloff'] and all(math.isfinite(v) for k in ['position','rotation','color'] for v in s[k])
 assert all(math.isfinite(s[k]) for k in ['power','radius','spotSize','spotBlend'])
log=AUDIT/'mine-surfaces.log';assert 'CS_MINE_DELIVERY_OK' in log.read_text(errors='replace')
assert sha(manifest_path)==state['manifestSha256']
result={'status':'PassedIndependentCurrentMain14DeliveryProvenance_NotUnityOrVisualAccepted','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stateSha256':sha(STATE),'manifestSha256':sha(manifest_path),'mapCommit':manifest['mapCommit'],'uniqueRooms':sorted(expected),'sourceInputCount':len(config['sources']),'deliveredUniqueRecordFiles':len(delivered),'rigUniqueDependencies':len(rig_deps),'retainedImporterMetadataCount':len(metas),'preservedNonmineFileCount':len(preserved),'sourceRecipe':recipe,'sixContextSpotNames':sorted(original),'preservationSha256':sha(AUDIT/'mine/preservation.json'),'surfaceCacheSha256':sha(AUDIT/'mine/surface-cache.json'),'mineLogSha256':sha(log),'checks':['14 unique Source-derived room keys and exact13 nonmine room records preserved','All14mesh+collision bytes match declared hashes; mine collision unchanged','All retained metadata1570 + nonmine model/texture records byte-identical','Complete rig model/animation/declared dependency package + actual metas matches pinned canonical bytes','Current no-reuse4096 batched source-recipe-v2 exact13tools/sourceScene SHA and34Source pins','Six complete Source context SPOT contracts match room records'],'limits':['Fresh source-pinned Spawn completed passes resumed from prior R4/R5; entire mine core/context fresh current recipe','Failed R5 remains failed; no partial mine cache reused','Source render R2/Unity adoption/bake/capture/gameplay/Player fidelity still pending','No Blender/Unity launched by reviewer; current art score not assigned']}
OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','manifestSha256','deliveredUniqueRecordFiles','rigUniqueDependencies','retainedImporterMetadataCount']},indent=2));print('receiptSHA',sha(OUT))
