"""Compare completed saved-scene render batches; never edit image pixels."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent
warm = root / 'renders/review/R07'
cold = root / 'renders/review/cold-R07'
out = root / 'validation/R07'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = json.loads((out / 'snapshot-a.json').read_text(encoding='utf-8'))
b = json.loads((out / 'snapshot-b.json').read_text(encoding='utf-8'))
assert a['artifact_fingerprint'] == b['artifact_fingerprint']
assert a['blend_sha256'] == b['blend_sha256'] == sha(root.parent / 'blender/turbine-room.blend')
rows = []
for p in sorted(warm.glob('*.png')):
    q = cold / p.name
    x = np.array(Image.open(p).convert('RGBA')).astype(np.int16)
    y = np.array(Image.open(q).convert('RGBA')).astype(np.int16)
    assert x.shape == y.shape
    d = np.abs(x-y)
    rows.append({'camera':p.stem, 'warm_sha256':sha(p), 'cold_sha256':sha(q),
                 'dimensions':[x.shape[1],x.shape[0]], 'max_channel_difference_255':int(d.max()),
                 'mean_channel_difference_255':float(d.mean()),
                 'changed_pixel_fraction':float(np.any(d,axis=2).mean())})
assert len(rows) == 16
report = {'revision':'R07', 'blend_sha256':a['blend_sha256'],
          'semantic_fingerprints_identical':True, 'artifact_fingerprint':a['artifact_fingerprint'],
          'all_pixels_identical':all(r['max_channel_difference_255']==0 for r in rows),
          'method':'Two independent reopened Blender render processes through shared GPU gate; RGBA byte comparison with Pillow/NumPy. Numeric differences are evidence, not a substitute for independent visual review.',
          'views':rows}
(out / 'cold-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='views'}))
print('Largest channel difference:',max(r['max_channel_difference_255'] for r in rows))
