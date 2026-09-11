"""Compare actual independent render and saved-state outputs; no approval generation."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];rows=[]
for p in sorted((R/'production/renders/final').glob('*.png')):
 q=R/'production/renders/cold'/p.name
 if not q.exists():rows.append({'camera':p.stem,'pass':False,'missing_cold':True});continue
 a=np.asarray(Image.open(p).convert('RGB')).astype(np.int16);b=np.asarray(Image.open(q).convert('RGB')).astype(np.int16);dif=np.abs(a-b)
 rows.append({'camera':p.stem,'pass':a.shape==b.shape and int(dif.max())<=1,'max_channel_difference':int(dif.max()),'changed_pixels':int(np.count_nonzero(np.any(dif,axis=2))),'mean_absolute_difference':float(dif.mean()),'final_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cold_sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
states={}
for n in ['cold-A','cold-B','source-replay']:
 p=R/'production/validation'/f'{n}.json'
 if p.exists():states[n]=json.loads(p.read_text())['state_sha256']
report={'render_comparison_pass':len(rows)==14 and all(r['pass'] for r in rows),'renders':rows,'state_fingerprints':states,'state_comparison_pass':len(states)==3 and len(set(states.values()))==1,'note':'At most one 8-bit code difference allows documented GPU rounding, not perceptual changes. Independent reviewer decides visual acceptance.'}
(R/'production/validation/cold-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='renders'},indent=2))
