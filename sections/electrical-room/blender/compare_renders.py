"""Compare fixed-camera PNG pixels and camera/settings manifests; no image edits."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('--out',required=True);p.add_argument('--max-mean',type=float,default=.25);p.add_argument('--require-count',type=int,default=10)
a=p.parse_args();base=Path(a.baseline);cand=Path(a.candidate)
bm=json.loads((base/'render_manifest.json').read_text());cm=json.loads((cand/'render_manifest.json').read_text())
rows=[];names=[r['camera'] for r in bm['renders']];cnames=[r['camera'] for r in cm['renders']]
manifest_pass=names==cnames and len(names)==a.require_count and bm['settings']==cm['settings'] and bm['source_sha256']==cm['source_sha256']
for b in bm['renders']:
    name=b['camera'];other=next((r for r in cm['renders'] if r['camera']==name),None)
    if not other:rows.append({'camera':name,'pass':False,'error':'missing camera'});continue
    x=Image.open(base/(name+'.png')).convert('RGB');y=Image.open(cand/(name+'.png')).convert('RGB')
    samecamera=all(b[k]==other[k] for k in ['location','rotation_euler','lens_mm'])
    if x.size!=y.size:rows.append({'camera':name,'pass':False,'error':'resolution mismatch'});continue
    delta=ImageChops.difference(x,y);st=ImageStat.Stat(delta);mean=sum(st.mean)/3;maximum=max(v[1] for v in delta.getextrema())
    rows.append({'camera':name,'pass':samecamera and mean<=a.max_mean,'same_camera':samecamera,'exact_pixels':not delta.getbbox(),'mean_absolute_channel_difference_0_255':mean,'max_channel_difference_0_255':maximum,'baseline_sha256':hashlib.sha256((base/(name+'.png')).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((cand/(name+'.png')).read_bytes()).hexdigest()})
passed=manifest_pass and len(rows)==a.require_count and all(r['pass'] for r in rows)
report={'schema':'critical-shift.cold-render-comparison.v1','pass':passed,'manifest_pass':manifest_pass,'baseline':str(base),'candidate':str(cand),'mean_tolerance_0_255':a.max_mean,'required_camera_count':a.require_count,'comparisons':rows}
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(json.dumps({'pass':passed,'cameras':len(rows),'exact':sum(r.get('exact_pixels',False) for r in rows)}));raise SystemExit(0 if passed else 2)
