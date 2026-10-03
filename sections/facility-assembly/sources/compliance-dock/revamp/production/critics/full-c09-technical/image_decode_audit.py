from pathlib import Path
import json,hashlib,datetime
from PIL import Image
P=Path(__file__).resolve().parent;PROD=P.parents[1];R=PROD/'renders';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
native='6838d604ac4586da057a652e98e9c694f754a84e9f38ba70b83f1046e9ae6e9a';recipe='38d50f5ec2f64755c9f1f2fe35d4e46e98f74dc71c3df327c9d32a18012e28ce'
rows=[];groups=[]
for folder,count in [('full-cycle-09',27),('full-cycle-09-neutral',4),('full-cycle-09-uv-standard',4)]:
 D=R/folder;M=json.loads((D/'manifest.json').read_text());assert M['complete'] and len(M['shots'])==count and len(list(D.glob('*.png')))==count
 assert M['source_sha256']==native and M['renderer_sha256']==recipe and M['resolution']==[1067,600] and not M['source_saved']
 for S in M['shots']:
  F=D/(S['id']+'.png');I=Image.open(F);I.load();assert I.size==(1067,600);assert sha(F)==S['image_sha256']
  rows.append({'path':str(F),'sha256':sha(F),'decoded_size':list(I.size),'bytes':F.stat().st_size,'vision_opened':False,'kind':folder,'view_id':S['id']})
 groups.append({'folder':folder,'actual_png_count':count,'manifest_sha256':sha(D/'manifest.json'),'source_sha256':M['source_sha256'],'renderer_sha256':M['renderer_sha256'],'complete':True})
ref=json.loads((R/'spawn-reference/reference-provenance.json').read_text());assert ref['source_sha256']=='9635f41aec585768285317399af9d6a3943411a66e20e2e3d96b05ad86dcfa40'
for S in ref['images']:
 F=R/'spawn-reference'/S['name'];I=Image.open(F);I.load();assert sha(F)==S['sha256']
 rows.append({'path':str(F),'sha256':sha(F),'decoded_size':list(I.size),'bytes':F.stat().st_size,'vision_opened':False,'kind':'approved-spawn-original','view_id':S['name'],'reference_original_path':S['original_path']})
result={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_sha256':native,'renderer_sha256':recipe,'manifest_groups':groups,'current_decoded':35,'reference_decoded':4,'actual_vision_opens':0,'images':rows,'reference_provenance_sha256':sha(R/'spawn-reference/reference-provenance.json'),'decode_and_hash_checks_pass':True,'vision_checks_complete':False}
(P/'imageaudit.json').write_text(json.dumps(result,indent=2));print('39_DECODE_HASH_VERIFIED',flush=True)
