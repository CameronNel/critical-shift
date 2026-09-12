"""Render bounded fixed-view pairs under an already-held shared GPU gate.

Every image opens the canonical artifact in its own fresh Blender process.
Original per-view manifests are retained; aggregate manifests are emitted only
after all16 real views exist. No geometry, settings or source scene is saved.
"""
import argparse,subprocess,sys,json,hashlib,shutil,os,datetime
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--cameras',required=True);a=p.parse_args()
r=Path(__file__).resolve().parent.parent;blend=r/'blender/Fuel_Corridor.blend';h=hashlib.sha256(blend.read_bytes()).hexdigest()
build=json.loads((r/f'production/checkpoints/{a.revision}/blender/build_manifest.json').read_text())
assert build['revision']==a.revision and build['blend_sha256']==h,'Canonical promotion must finish before queuing this revision'
gate=Path('C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_owner.json')
owner=json.loads(gate.read_text());assert owner['status']=='running' and owner['owner']=='fuel-corridor','Shared gate must be held by the calling wrapper'
assert os.getppid()==owner['pid'],'Pair runner must be the direct child of its gate wrapper'
all_names=['C01_ENTRY','C02_PRIMARY_ROUTE','C03_HERO','C04_REVERSE','C05_EAST_TURN','C06_REACTOR_THRESHOLD','C07_BYPASS','C08_SERVICE_JUNCTION','C09_MATERIALS','C10_PLANT_HEADER','D01_CARRIER_OPERATION','D02_WORKBENCH','D03_UTILITY','D04_REACTOR_WIDE','D05_GATE_MECHANISM','D06_SERVICE_RECESS']
names=a.cameras.split(',');assert all(x in all_names for x in names)
os.environ['FUEL_CORRIDOR_ROOT']=str(r)
for name in names:
 for suffix in ['', '-cold']:
  folder=r/'production/renders/review'/(a.revision+suffix);part=folder/'parts'/name
  assert not (part/'cold_render_manifest.json').exists(),'Do not overwrite existing pair evidence'
  subprocess.run(['C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','--background',str(blend),'--python-exit-code','1','--python',str(r/'blender/render_saved.py'),'--','--out',str(part),'--cameras',name,'--require-full'],check=True)
  held=json.loads(gate.read_text());assert held.get('status')=='running' and held.get('pid')==owner['pid'] and held.get('owner')=='fuel-corridor','Gate ownership changed during render; no acceptance credit'
  m=json.loads((part/'cold_render_manifest.json').read_text());assert m['revision']==a.revision and m['blend_sha256_before']==m['blend_sha256_after']==h and m['saved_file_unchanged']
  assert len(m['renders'])==1 and m['renders'][0]['camera']==name
  shutil.copy2(part/(name+'.png'),folder/(name+'.png'))
 first=r/'production/renders/review'/a.revision/(name+'.png');second=r/'production/renders/review'/(a.revision+'-cold')/(name+'.png')
 x=np.array(Image.open(first).convert('RGB'),dtype=np.int16);y=np.array(Image.open(second).convert('RGB'),dtype=np.int16);d=np.abs(x-y)
 report={'camera':name,'blend_sha256':h,'max_channel_difference_255':int(d.max()),'mean_channel_difference_255':float(d.mean()),'pass':bool(d.max()<=2 and d.mean()<=.02),'method':'Two independent fresh Blender processes reading the same canonical file'}
 (r/f'production/renders/review/{a.revision}-cold/parts/{name}/pair-comparison.json').write_text(json.dumps(report,indent=2));print('PAIR_CHECK',json.dumps(report),flush=True)
 assert report['pass'],'Pair numeric threshold failed; preserve evidence and inspect before continuing'
assert hashlib.sha256(blend.read_bytes()).hexdigest()==h
for suffix in ['', '-cold']:
 folder=r/'production/renders/review'/(a.revision+suffix)
 manifests=[folder/'parts'/name/'cold_render_manifest.json' for name in all_names]
 if not all(q.exists() for q in manifests):continue
 parts=[json.loads(q.read_text()) for q in manifests]
 assert all(m['blend_sha256_before']==m['blend_sha256_after']==h and m['saved_file_unchanged'] for m in parts)
 result=dict(parts[0]);result['renders']=[m['renders'][0] for m in parts]
 result['utc_started']=min(m['utc_started'] for m in parts);result['utc_completed']=max(m['utc_completed'] for m in parts)
 result['execution_model']='One independent fresh Blender process per fixed view; no cross-camera persistent cache'
 result['per_view_manifests']=[str(q.relative_to(folder)) for q in manifests];result['complete']=True
 (folder/'cold_render_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print('COMPLETE_AGGREGATE',suffix or 'primary',len(parts),flush=True)
