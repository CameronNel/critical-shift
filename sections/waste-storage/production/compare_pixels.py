"""Compare independently cold-rendered images using decoded pixels."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
left=R/'production/renders/review/W22';right=R/'production/renders/cold/W22'
a=json.loads((left/'render_manifest.json').read_text());b=json.loads((right/'render_manifest.json').read_text())
assert len(a['renders'])==len(b['renders'])==20
assert a['settings']==b['settings']
rows=[]
for entry in a['renders']:
    name=entry['camera'];x=np.asarray(Image.open(left/(name+'.png')).convert('RGB'),dtype=np.int16);y=np.asarray(Image.open(right/(name+'.png')).convert('RGB'),dtype=np.int16)
    assert x.shape==y.shape
    d=np.abs(x-y)
    rows.append({'camera':name,'pixel_identical':bool(np.array_equal(x,y)),'mean_absolute_8bit_difference':float(d.mean()),'maximum_8bit_difference':int(d.max()),'changed_pixels':int(np.any(d,axis=2).sum())})
result={'revision':'W22','same_settings':True,'settings':a['settings'],'images':rows,'all_pixel_identical':all(r['pixel_identical'] for r in rows),'artifact_sha256':hashlib.sha256((R/'blender/waste_storage_integration.blend').read_bytes()).hexdigest(),'scope':'Two separate fresh-process opens of the same saved artifact. Not neighboring assembly or game runtime validation.'}
first=json.loads((R/'production/validation/W22/fingerprint-first-open.json').read_text())
result['artifact_unchanged_since_first_open']=result['artifact_sha256']==first['file_sha256']
assert result['artifact_unchanged_since_first_open'], 'Saved artifact changed during review; preserve and reverify before delivery.'
(R/'production/validation/W22/cold-pixel-comparison.json').write_text(json.dumps(result,indent=2));print('PIXEL_COMPARISON',result['all_pixel_identical'],max(r['mean_absolute_8bit_difference'] for r in rows))
