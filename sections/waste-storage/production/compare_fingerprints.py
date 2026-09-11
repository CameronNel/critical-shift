"""Compare actual saved-artifact receipts without modifying the artifacts."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('second');p.add_argument('--out',required=True);a=p.parse_args()
x=json.loads(Path(a.first).read_text());y=json.loads(Path(a.second).read_text())
r={'first':a.first,'second':a.second,'objects_match':x['object_hash']==y['object_hash'],'materials_match':x['material_hash']==y['material_hash'],'contract_match':x['contract_sha256']==y['contract_sha256']}
for key in ['objects','materials']:
    left={q['name']:q for q in x[key]};right={q['name']:q for q in y[key]}
    r[key+'_differences']=[{'name':n,'first':left.get(n),'second':right.get(n)} for n in sorted(left.keys()|right.keys()) if left.get(n)!=right.get(n)]
r['pass']=r['objects_match'] and r['materials_match'] and r['contract_match']
Path(a.out).write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if not k.endswith('_differences')});print('difference counts',len(r['objects_differences']),len(r['materials_differences']))
