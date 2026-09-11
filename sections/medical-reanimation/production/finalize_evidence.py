"""Index verified outputs. Independent reviewer owns scores; this script cannot generate them."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
rev='M11';blend='blender/medical_integration.blend';h=sha(blend)
tech=read(f'production/validation/{rev}/technical.json')
assert tech['pass'] and tech['revision']==rev and tech['blend_sha256']==h
assert read(f'production/validation/{rev}/interaction.json')['pass']
assert read(f'production/validation/{rev}/signs.json')['pass']
assert not read(f'production/validation/{rev}/contact_candidates.json')['isolated']
comparison=read('production/validation/cold-comparison.json')
assert comparison['render_comparison_pass'] and comparison['state_comparison_pass']
for n in ['cold-A','cold-B']:
 assert read(f'production/validation/{n}.json')['blend_sha256']==h
for folder in ['final','cold']:
 m=read(f'production/renders/{folder}/render_manifest.json')
 assert m['revision']==rev and m['blend_sha256']==h and len(m['renders'])==14
 for row in m['renders']:assert row['sha256']==sha(f"production/renders/{folder}/{row['camera']}.png")
states=read(f'production/renders/states/{rev}/manifest.json');assert len(states)==6
for row in states:assert row['sha256']==sha(f"production/renders/states/{rev}/{row['camera']}.png")
review=read('production/critics/luna-scene-M11-scores.json')
assert review['revision']==rev and review['disposition']=='PASS'
assert review['blend_sha256']==h
assert len(review['categories'])>=8 and all(90<v<=100 for v in review['categories'].values())
assert len(review['views'])==20 and all(90<v<=100 for v in review['views'].values())
paths=[blend,'interface.json','architecture/floorplan.svg','architecture/floorplan.png','architecture/INTEGRATION.md','production/critics/luna-scene-M11.md','production/critics/luna-scene-M11-scores.json','production/validation/cold-comparison.json','production/validation/cold-A.json','production/validation/cold-B.json','production/validation/source-replay.json','production/validation/live-open.json','art/concepts/provenance.json']
paths += [p.relative_to(R).as_posix() for folder in ['final','cold',f'states/{rev}'] for p in sorted((R/'production/renders'/folder).glob('*')) if p.is_file()]
paths += [p.relative_to(R).as_posix() for p in sorted((R/f'production/validation/{rev}').glob('*.json'))]
paths += ['production/validation/gpu-batch-M11.log','production/checkpoints/M11/build_manifest.json']
evidence={'revision':rev,'disposition':'INDEPENDENTLY REVIEWED ART MODULE','blend_sha256':h,'state_sha256':read('production/validation/cold-A.json')['state_sha256'],'categories':review['categories'],'view_scores':review['views'],'fixed_views':14,'supplemental_state_views':6,'cold_fixed_views':14,'source_replay_matches':True,'original_grok_sha256':read('art/concepts/provenance.json')['source_layout_blend_sha256'],'files':{p:sha(p) for p in paths},'scope':'Owned Medical art module only. Neighbor transforms, game runtime, physics and whole-map assembly are unbound. See live-open.json for visible-window state separately from successful fresh-process M11 cold opens.'}
(R/'production/FINAL_EVIDENCE.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print('FINAL_EVIDENCE_VERIFIED',rev,h,min(review['categories'].values()),min(review['views'].values()))
