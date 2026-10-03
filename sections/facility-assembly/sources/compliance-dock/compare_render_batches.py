"""Verify two actual render batches; Pillow reads pixels without editing images.

Used for cold-start reproducibility and fixed-camera regression inventories.
Pixel differences are evidence, never an invented visual acceptance score.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p=argparse.ArgumentParser()
p.add_argument('before',type=Path)
p.add_argument('after',type=Path)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--cold',action='store_true',help='Require unchanged source/settings and identical decoded pixels')
a=p.parse_args()
before=json.loads((a.before/'manifest.json').read_text())
after=json.loads((a.after/'manifest.json').read_text())
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
keys=['renderer_sha256','resolution','samples','engine','device','seed','adaptive_threshold','adaptive_min_samples','max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','view_transform','look','exposure','diagnostic','label_method','requested_view_count']
same_settings=all(before.get(k)==after.get(k) for k in keys)
left={x['id']:x for x in before['shots']};right={x['id']:x for x in after['shots']}
records=[]
for name in sorted(set(left)&set(right)):
    l,r=left[name],right[name]
    lp,rp=a.before/(name+'.png'),a.after/(name+'.png')
    li,ri=Image.open(lp).convert('RGBA'),Image.open(rp).convert('RGBA')
    if li.size!=ri.size:raise RuntimeError('Changed image dimensions: '+name)
    delta=ImageChops.difference(li,ri);extrema=delta.getextrema()
    same_camera=all(l.get(k)==r.get(k) for k in ['camera_matrix_world','actual_lens_mm','projection','ortho_scale_m','temporary_hidden_geometry','label'])
    records.append(dict(id=name,before_sha256=sha(lp),after_sha256=sha(rp),hashes_match_manifests=sha(lp)==l['image_sha256'] and sha(rp)==r['image_sha256'],same_camera=same_camera,identical_pixels=all(high==0 for low,high in extrema),max_channel_difference=max(high for low,high in extrema),mean_channel_difference=ImageStat.Stat(delta).mean))
report=dict(before_source_sha256=before['source_sha256'],after_source_sha256=after['source_sha256'],same_source=before['source_sha256']==after['source_sha256'],same_settings=same_settings,complete=before['complete'] and after['complete'],same_view_set=set(left)==set(right),views=records,cold_comparison=a.cold,visual_acceptance=False)
report['pass']=report['complete'] and report['same_view_set'] and same_settings and all(x['hashes_match_manifests'] and x['same_camera'] for x in records) and (not a.cold or report['same_source'] and all(x['identical_pixels'] for x in records))
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(report,indent=2)+'\n')
print('RENDER_COMPARISON',report['pass'],len(records),'views','identical',sum(x['identical_pixels'] for x in records))
if not report['pass']:raise SystemExit(1)
