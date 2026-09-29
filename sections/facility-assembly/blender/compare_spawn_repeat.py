"""Compare actual decoded pixels from two independent saved-scene opens."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/spawn-finish'
a=np.asarray(Image.open(out/'01-front-yard.png').convert('RGBA')).astype(np.int16)
b=np.asarray(Image.open(out/'cold-01-front-yard.png').convert('RGBA')).astype(np.int16)
assert a.shape==b.shape
d=np.abs(a-b);m=json.loads((out/'manifest.json').read_text());cold=json.loads((out/'cold-render.json').read_text());assert m['source_sha256']==cold['source_sha256']
r=json.loads((out/'cold-open.json').read_text());assert r['sha256']==m['source_sha256']
r['pixel_comparison']=dict(shape=list(a.shape),max_channel_difference=int(d.max()),mean_channel_difference=float(d.mean()),changed_pixels=int(np.count_nonzero(np.any(d,axis=2))),identical=bool(not d.any()))
(out/'cold-open.json').write_text(json.dumps(r,indent=2));print(json.dumps(r['pixel_comparison']))
