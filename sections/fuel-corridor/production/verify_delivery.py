"""Fail-closed delivery gate binding saved scene, renders and Luna's scores."""
import json,hashlib,sys
from pathlib import Path
r=Path(__file__).resolve().parent.parent
revision=sys.argv[1];review=Path(sys.argv[2]);prefix=revision.replace('final-','')
def read(p):return json.loads((r/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
blend_sha=sha(r/'blender/Fuel_Corridor.blend')
assert sha(r/f'production/checkpoints/{revision}/blender/Fuel_Corridor.blend')==blend_sha
evidence=Path('production/evidence/final-pass')
technical=read(evidence/f'{prefix}-technical.json');assert technical['status']=='PASS' and not technical['failed_gates']
assert technical['revision']==revision and technical['fresh_background_process'] and not technical['scene_modified']
assert technical['saved_source_sha256']==sha(r/'blender/build.py')
assert technical['saved_detail_source_sha256']==sha(r/'blender/valorant_details.py')
assert technical['saved_interface_sha256']==sha(r/'interface.json')
replay=read(evidence/f'{prefix}-source-replay.json')
assert not any(replay[k] for k in ['missing','added','changed','matrix_differences'])
materials=read(evidence/f'{prefix}-material-replay.json')['differences']
for kind in ['materials','uv','textures']:
 assert not any(materials[kind][k] for k in ['changed','missing','added'])
comparison=read(evidence/f'{prefix}-cold-comparison.json');assert comparison['pass'] and comparison['views']==16 and comparison['same_saved_blend_sha256']==blend_sha
survey=read(evidence/f'{prefix}-delivery-survey.json');assert survey['sha256']==blend_sha and len(survey['cameras'])==16 and not survey['libraries']
assert len(survey['images'])==3 and all(x['packed'] for x in survey['images'])
for pack in [revision,revision+'-cold']:
 folder=r/'production/renders/review'/pack
 m=json.loads((folder/'cold_render_manifest.json').read_text())
 assert len(m['renders'])==16 and m['saved_file_unchanged'] and not m['preview']
 assert m['blend_sha256_before']==m['blend_sha256_after']==blend_sha
 assert m['resolution']==[1440,960] and m['samples']==32
 for row in m['renders']:assert sha(folder/(row['camera']+'.png'))==row['sha256']
walk=r/'production/renders/review'/(revision+'-walkthrough')
m=json.loads((walk/'manifest.json').read_text());assert m['complete'] and len(m['renders'])==12
assert m['blend_sha256_before']==m['blend_sha256_after']==blend_sha and m['eye_height_m']==1.7
for row in m['renders']:assert sha(walk/(row['view']+'.png'))==row['sha256']
positions=read(evidence/'walkthrough-positions.json');assert positions['pass'] and positions['blend_sha256']==blend_sha
branch=read(evidence/f'{prefix}-branch-handoff.json');assert branch['blend_sha256']==blend_sha and not branch['handoff']['errors']
for row in branch['full_branch_approaches']:assert row['blocked']==0 and not row['floor_failures']
luna=json.loads(review.read_text(encoding='utf-8'));assert luna['disposition']=='PASS' and luna['blend_sha256']==blend_sha and luna['revision']==revision
for key,count in [('categories',17),('fixed_views',16),('player_views',12)]:
 assert len(luna[key])==count and len({x['name'] for x in luna[key]})==count
 assert all(90<x['score']<=100 for x in luna[key]),key+' has a failing score'
snapshot=r/f'production/checkpoints/{revision}/blender'
for name in ['build.py','valorant_details.py','wayfinding.py']:
 assert sha(r/'blender'/name)==sha(snapshot/name),'Source changed after verification: '+name
assert sha(r/'interface.json')==sha(snapshot/'interface.json')
assert read('scenery/handoff.json')==json.loads((snapshot/'handoff.json').read_text())
paths=[r/'blender/Fuel_Corridor.blend',r/'interface.json',r/'scenery/handoff.json',review]
paths+=list((r/evidence).glob(prefix+'-*.json'))
receipt={'status':'PASS','revision':revision,'blend_sha256':blend_sha,'object_count':survey['objects'],'categories':len(luna['categories']),'minimum_category_score':min(x['score'] for x in luna['categories']),'fixed_views':16,'cold_views':16,'player_views':12,'review':str(review.relative_to(r)),'verified_files':{str(p.relative_to(r)):sha(p) for p in paths},'scope':'Authored Fuel Corridor integration readiness. Neighbor assembly and engine runtime behavior remain unverified.'}
(r/evidence/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_files'},indent=2))
