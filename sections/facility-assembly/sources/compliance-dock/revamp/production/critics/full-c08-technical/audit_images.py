import hashlib,json,struct
from pathlib import Path
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production';O=P/'critics/full-c08-technical'
H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35';RH='38d50f5ec2f64755c9f1f2fe35d4e46e98f74dc71c3df327c9d32a18012e28ce'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'module_overhaul_R1.blend')==H
assert sha(R/'render_dock.py')==RH
report={'source_sha256':H,'renderer_sha256':RH,'manifests':[],'images':[],'reference_provenance':None}
recipes={'overhaul_dock.py':'58b80133bf0b08779f58319db2f18301c791a1b33991a3f438d9d8de0dd02f32','full_detail.py':'57e5a98d95e11d5ed186132d6a8de12c0eb539f35d8cf7dacf106c24bae66388','full_repairs.py':'be8dc32a98d9aee43c64cd98ce60c626baca4baca8121332e77deece54001f36','render_dock.py':RH}
for name,digest in recipes.items():assert sha(R/name)==digest
report['frozen_recipes']=recipes
beauty={}
for folder,count,diag in [('full-cycle-08',27,None),('full-cycle-08-neutral',4,'neutral'),('full-cycle-08-uv-standard',4,'uv')]:
 d=P/'renders'/folder;m=json.loads((d/'manifest.json').read_text());assert m['complete'] is True;assert m['source_sha256']==H;assert m['renderer_sha256']==RH;assert m['resolution']==[1067,600];assert m['diagnostic']==diag;assert m['source_saved'] is False;assert len(m['shots'])==count;assert len(list(d.glob('*.png')))==count
 report['manifests'].append({'path':str(d/'manifest.json'),'sha256':sha(d/'manifest.json'),'complete':True,'count':count,'diagnostic':diag})
 for s in m['shots']:
  if diag is None:beauty[s['id']]=s
  else:
   for key in ['camera_matrix_world','actual_lens_mm','projection']:assert s[key]==beauty[s['id']][key]
  f=d/(s['id']+'.png');data=f.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';size=list(struct.unpack('>II',data[16:24]));assert size==[1067,600]
  digest=sha(f);assert digest==s['image_sha256']
  report['images'].append({'path':str(f),'id':s['id'],'group':folder,'sha256':digest,'dimensions':size,'original_opened':False,'finding':None})
d=P/'renders/spawn-reference';rp=d/'reference-provenance.json';m=json.loads(rp.read_text());assert len(m['images'])==4;assert sha(R.parent/'spawn-room/module.blend')==m['source_sha256'];assert len(list(d.glob('*.png')))==4
report['reference_provenance']={'path':str(rp),'sha256':sha(rp),'source_sha256':m['source_sha256']}
for s in m['images']:
 f=d/s['name'];assert sha(f)==s['sha256'];data=f.read_bytes();size=list(struct.unpack('>II',data[16:24]));report['images'].append({'path':str(f),'id':f.stem,'group':'spawn-reference','sha256':s['sha256'],'dimensions':size,'original_opened':False,'finding':None})
assert len(report['images'])==39
assert sha(R/'module_overhaul_R1.blend')==H and sha(R/'render_dock.py')==RH
(O/'imageaudit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'current':35,'reference':4,'manifests':report['manifests'],'all_hashes_verified':True},indent=2))
