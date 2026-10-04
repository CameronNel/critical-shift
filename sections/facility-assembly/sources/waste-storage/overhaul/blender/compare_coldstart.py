"""Compare original-source rebuild fingerprints and all fixed-view pixels.

Run with ordinary Python/Pillow after both render batches finish: ... R15.
This records reproducibility only; independent art acceptance is a separate gate.
"""
import hashlib,json,sys,re
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

root=Path(__file__).resolve().parents[1]/'production'
revision=sys.argv[1]
assert re.fullmatch(r'R\d+[a-z]?',revision), 'Revision must be a full-revision basename such as R50 or R50a'
cold=root/'coldstart'
read=lambda p:json.loads(p.read_text())
a=read(cold/f'fingerprint_{revision}_checkpoint.json')
b=read(cold/f'fingerprint_{revision}_rebuild.json')
assert a['source_unchanged'] and b['source_unchanged']
changed=lambda key:sorted(n for n in a[key].keys()|b[key].keys() if a[key].get(n)!=b[key].get(n))
objects=changed('objects');materials=changed('materials')
same_scene=a['scene_state_sha256']==b['scene_state_sha256']
state=dict(checkpoint_source_sha256=a['source_sha256'],rebuild_source_sha256=b['source_sha256'],
           changed_objects=objects,changed_materials=materials,scene_state_identical=same_scene,
           status='PASS' if not objects and not materials and same_scene else 'FAIL',
           scope='Original-source rebuild reproducibility; visual acceptance is separate.')
(cold/f'comparison_{revision}.json').write_text(json.dumps(state,indent=2))

ma=read(root/f'renders/{revision}/manifest.json')
mb=read(root/f'renders/{revision}_cold/manifest.json')
assert all(m['complete'] and m['source_unchanged'] for m in [ma,mb]),'Render batches incomplete'
expected=set(ma['required_cameras'])
assert expected==set(mb['required_cameras']) and len(expected)==21
assert all({v['camera'] for v in m['views']}==expected and len(m['views'])==21 for m in [ma,mb])
assert ma['source_sha256']==a['source_sha256'] and mb['source_sha256']==b['source_sha256']
other={v['camera']:v for v in mb['views']};rows=[]
for view in ma['views']:
 name=view['camera'];v=other[name]
 assert view['matrix']==v['matrix'] and view['lens']==v['lens'],name+' camera mismatch'
 pa=root/f'renders/{revision}/{name}.png';pb=root/f'renders/{revision}_cold/{name}.png'
 assert hashlib.sha256(pa.read_bytes()).hexdigest()==view['sha256']
 assert hashlib.sha256(pb.read_bytes()).hexdigest()==v['sha256']
 ia=Image.open(pa).convert('RGB');ib=Image.open(pb).convert('RGB');assert ia.size==ib.size
 diff=ImageChops.difference(ia,ib)
 rows.append(dict(camera=name,pixels_identical=diff.getbbox() is None,
                  max_channel_delta=max(hi for lo,hi in diff.getextrema()),
                  mean_channel_delta=ImageStat.Stat(diff).mean))
settings_equal=ma['settings']==mb['settings']
pixels=dict(status='PASS' if settings_equal and all(v['pixels_identical'] for v in rows) else 'FAIL',
            checkpoint=a['source_sha256'],cold_rebuild=b['source_sha256'],cameras=rows,
            settings_equal=settings_equal,scope='Cold-start reproducibility; no visual acceptance inference.')
(cold/f'pixel_comparison_{revision}.json').write_text(json.dumps(pixels,indent=2))
detail=None
required_details={'D02_CaptureService','D03_ExtractionRun'}
assert required_details.issubset(a['objects']) and required_details.issubset(b['objects']), 'Both fixed detail cameras are mandatory'
if required_details:
 da=read(root/f'details/{revision}/manifest.json');db=read(root/f'details/{revision}_cold/manifest.json')
 assert da['complete'] and db['complete'] and da['source_unchanged'] and db['source_unchanged']
 assert da['source_sha256']==a['source_sha256'] and db['source_sha256']==b['source_sha256']
 assert set(da['required_cameras'])==set(db['required_cameras'])==required_details
 assert len(da['views'])==len(db['views'])==len(required_details)
 assert {v['camera'] for v in da['views']}=={v['camera'] for v in db['views']}==required_details
 other_details={v['camera']:v for v in db['views']};detail_rows=[]
 for va in da['views']:
  name=va['camera'];vb=other_details[name];assert va['matrix']==vb['matrix'] and va['lens']==vb['lens']
  pa=root/f'details/{revision}/{name}.png';pb=root/f'details/{revision}_cold/{name}.png'
  assert hashlib.sha256(pa.read_bytes()).hexdigest()==va['sha256'] and hashlib.sha256(pb.read_bytes()).hexdigest()==vb['sha256']
  ia=Image.open(pa).convert('RGB');ib=Image.open(pb).convert('RGB');assert ia.size==ib.size
  diff=ImageChops.difference(ia,ib);detail_rows.append(dict(camera=name,pixels_identical=diff.getbbox() is None,max_channel_delta=max(hi for lo,hi in diff.getextrema())))
 same_settings=da['settings']==db['settings']==ma['settings'];identical=all(v['pixels_identical'] for v in detail_rows)
 detail=dict(cameras=detail_rows,settings_equal=same_settings,
             status='PASS' if identical and same_settings else 'FAIL',scope='All authored supplemental process details independently reproduced.')
 (cold/f'detail_comparison_{revision}.json').write_text(json.dumps(detail,indent=2))
 assert detail['status']=='PASS','Cold supplemental detail comparison failed'
print(revision,'authoring',state['status'],'pixels',pixels['status'],'views',len(rows))
assert state['status']==pixels['status']=='PASS','Cold-start comparison failed'
