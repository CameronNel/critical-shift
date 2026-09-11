"""Compare independent saved-file GPU render batches without tolerance inflation."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parents[1];rev=sys.argv[1]
reference=root/f'production/renders/review/{rev}'
cold=root/f'production/renders/cold/{rev}'
baseline=json.loads((reference/'render_manifest.json').read_text(encoding='utf-8'))
fresh=json.loads((cold/'render_manifest.json').read_text(encoding='utf-8'))
audit=json.loads((root/f'production/technical/{rev}-validation.json').read_text(encoding='utf-8'))
blend=root/'blender/cooling_plant.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for c in fresh['cameras']:
    name=c['camera'];p=reference/(name+'.png');q=cold/(name+'.png')
    a=np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
    b=np.asarray(Image.open(q).convert('RGB'),dtype=np.int16)
    if a.shape!=b.shape:raise RuntimeError('Image dimensions changed')
    delta=np.abs(a-b)
    rows.append(dict(camera=name,reference_sha256=sha(p),cold_sha256=sha(q),
        decoded_pixels_equal=bool(np.array_equal(a,b)),changed_channels=int(np.count_nonzero(delta)),
        max_channel_difference=int(delta.max()),mean_absolute_difference=float(delta.mean()),
        rms_difference=float(np.sqrt(np.mean(delta.astype(np.float64)**2))),
        dimensions=list(a.shape)))
actual=sha(blend);expected=audit['checks']['source']['blend_sha256']
settings_equal=all(baseline[k]==fresh[k] for k in ('revision','source_sha256','backend','samples','resolution'))
primary={c['camera'] for c in baseline['cameras'] if c['camera'].startswith('C')}
all_primary={r['camera'] for r in rows}==primary and len(primary)==10
passed=actual==expected and settings_equal and all_primary and all(r['decoded_pixels_equal'] for r in rows)
report=dict(revision=rev,status='PASS' if passed else 'REVIEW',method='Two independent Blender processes cold-open the same saved artifact. Ten primary cameras rendered through shared GPU gate. Exact decoded RGB equality; no numerical tolerance used.',
    blend_sha256=actual,baseline_blend_sha256=expected,artifact_unchanged=actual==expected,
    settings_equal=settings_equal,all_ten_primary_cameras=all_primary,cameras=rows,
    limitations='Saved Blender artifact survival and render repeatability only; not whole-map or game-engine verification.')
(root/f'production/technical/{rev}-cold-start.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=[f'# {rev} cold-start evidence','',f'**{report["status"]}** — fresh saved-file render comparison; artifact unchanged: {report["artifact_unchanged"]}.','',report['method'],'',f'Blender file SHA256: `{actual}`','',
'| Camera | Equal decoded pixels | Changed channels | Maximum difference /255 |','|---|---|---:|---:|']
lines += [f'| {r["camera"]} | {r["decoded_pixels_equal"]} | {r["changed_channels"]} | {r["max_channel_difference"]} |' for r in rows]
lines+=['',report['limitations']]
(root/f'production/technical/{rev}-cold-start.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='cameras'}))
if not passed:sys.exit(2)
