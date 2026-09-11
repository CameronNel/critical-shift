"""Verify saved-artifact fingerprints, source bytes and decoded cold render pixels."""
import json,hashlib,re
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'production/validation/E05'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a,b=[read(V/f'snapshot-{q}.json') for q in ['A','B']]
sources=json.loads(a['data']['authoring_source_sha256'])
source_checks={n:sha(ROOT/'blender'/n)==h for n,h in sources.items()}
tech=read(V/'technical.json');types={o['name']:o['type'] for o in a['data']['objects']}
warnings=next(c['measurements'] for c in tech['checks'] if c['id']=='open_mesh_inventory')
classification=[]
for w in warnings:
 name=w['object'];kind=types[name];base=re.sub(r'\.\d{3}$','',name)
 reason=('Evaluated font tessellation; backed surface text, not architectural shell.' if kind=='FONT' else
         'Swept curve tessellation; source caps enabled, ends are supported in the associated assembly.' if kind=='CURVE' else
         'Intentional surface wear/decal sheet, separately support-tested.' if base in {'Localized chipped paint','Wear at repeatedly handled edge','Sparse floor handling scuff','Subtle repaired wall patch'} else None)
 classification.append({'object':name,'type':kind,'reason':reason,'nonmanifold_edges':w['nonmanifold_edges']})
warm=ROOT/'production/renders/review/E05';cold=ROOT/'production/renders/final'
wm,cm=[read(p/'render_manifest.json') for p in [warm,cold]];rows=[]
for wr in wm['renders']:
 name=wr['camera'];cr=next((q for q in cm['renders'] if q['camera']==name),None)
 i,j=[Image.open(p/(name+'.png')).convert('RGB') for p in [warm,cold]]
 difference=ImageChops.difference(i,j)
 rows.append({'camera':name,'decoded_pixels_equal':i.size==j.size and difference.getbbox() is None,'warm_sha256':sha(warm/(name+'.png')),'cold_sha256':sha(cold/(name+'.png')),'camera_equal':bool(cr) and all(wr[k]==cr[k] for k in ['location','rotation_euler','lens_mm'])})
r={'revision':'E05','blend_sha256':sha(ROOT/'blender/electrical_room.blend'),'fingerprint_A':a['artifact_fingerprint'],'fingerprint_B':b['artifact_fingerprint'],'saved_file_unchanged':a['blend_sha256']==b['blend_sha256']==sha(ROOT/'blender/electrical_room.blend'),'source_bytes_match':source_checks,'objects':a['objects'],'materials':a['materials'],'cameras':a['cameras'],'technical_pass':tech['pass'],'walkthrough_pass':read(V/'walkthrough.json')['pass'],'apertures_pass':read(V/'apertures.json')['pass'],'reviewed_open_mesh_warnings':classification,'renders':rows,'limits':'Local saved artifact only. Independent Luna visual approval is separate. No engine or assembled-facility validation.'}
r['pass']=r['saved_file_unchanged'] and a['artifact_fingerprint']==b['artifact_fingerprint'] and all(source_checks.values()) and len(rows)==14 and all(x['decoded_pixels_equal'] and x['camera_equal'] for x in rows) and tech['pass'] and r['walkthrough_pass'] and r['apertures_pass'] and all(x['reason'] and x['nonmanifold_edges']==0 for x in classification)
(V/'package-verification.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:r[k] for k in ['revision','pass','objects','materials','cameras','saved_file_unchanged']}))
if not r['pass']:raise SystemExit(2)
