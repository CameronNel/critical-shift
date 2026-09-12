"""Hash-bound RGB comparison of two complete fixed-camera saved-file packs."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image
a,b,out=map(Path,sys.argv[1:4])
def read(folder):
    manifest=json.loads((folder/'cold_render_manifest.json').read_text())
    rows={r['camera']:r for r in manifest['renders']}
    assert len(rows)==16 and len(manifest['renders'])==16
    assert manifest['saved_file_unchanged'] and not manifest['preview']
    assert manifest['resolution']==[1440,960] and manifest['samples']==32
    for n,r in rows.items():assert hashlib.sha256((folder/(n+'.png')).read_bytes()).hexdigest()==r['sha256']
    return manifest,rows
ma,ra=read(a);mb,rb=read(b);assert ra.keys()==rb.keys()
assert ma['blend_sha256_before']==mb['blend_sha256_before']
rows=[]
for name in sorted(ra):
    x=np.array(Image.open(a/(name+'.png')).convert('RGB'),dtype=np.int16)
    y=np.array(Image.open(b/(name+'.png')).convert('RGB'),dtype=np.int16)
    assert x.shape==y.shape==(960,1440,3)
    d=np.abs(x-y)
    rows.append({'camera':name,'max_channel_difference_255':int(d.max()),'mean_channel_difference_255':float(d.mean()),'changed_pixels':int(np.any(d,axis=2).sum()),'pass':bool(d.max()<=2 and d.mean()<=.02)})
report={'source':str(a),'cold':str(b),'same_saved_blend_sha256':ma['blend_sha256_before'],'views':16,'threshold':'max <=2/255 and mean <=0.02/255 per camera; no averaging between cameras','rows':rows,'pass':all(r['pass'] for r in rows),'limits':'Pixel reproducibility does not replace independent visual quality review or engine validation.'}
out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
assert report['pass'],'Cold pixel regression'
