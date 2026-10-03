"""Compare original-source rebuild fingerprints and all fixed-view pixels.

Run with ordinary Python/Pillow after both render batches finish: ... R15.
This records reproducibility only; independent art acceptance is a separate gate.
"""
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

root=Path(__file__).resolve().parents[1]/'production'
revision=sys.argv[1]
assert revision.startswith('R') and revision[1:].isdigit(),revision
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
expected={'CAM_ENTRY','CAM_MAIN_ROUTE','CAM_PROCESS','CAM_REVERSE','CAM_PINCH','CAM_MATERIAL',
          'CAM_ASSEMBLY','CAM_DISPATCH','CAM_MINE_TO_CRUSHER','CAM_WORK_NOOK','CAM_HERO_DETAIL'}
assert all({v['camera'] for v in m['views']}==expected and len(m['views'])==11 for m in [ma,mb])
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
print(revision,'authoring',state['status'],'pixels',pixels['status'],'views',len(rows))
assert state['status']==pixels['status']=='PASS','Cold-start comparison failed'
