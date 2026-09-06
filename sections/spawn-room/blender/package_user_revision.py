"""Package unmodified review renders and compare a fresh-process reopen."""
import json, shutil, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
warm=ROOT/'production/renders/review/user-corrections-03'
cold=ROOT/'production/renders/review/user-corrections-cold'
out=ROOT/'production/renders/final/user-corrections';out.mkdir(parents=True,exist_ok=True)
checks=json.loads((cold/'checks.json').read_text());assert checks['status']=='PASS'
contact=json.loads((cold/'contacts.json').read_text());assert contact['status']=='PASS'
provenance=json.loads((cold/'provenance.json').read_text())
source=Path(provenance['output']);assert hashlib.sha256(source.read_bytes()).hexdigest()==provenance['output_sha256']
comparison=[]
for path in sorted(cold.glob('*.png')):
    a=np.asarray(Image.open(warm/path.name).convert('RGB'),dtype=np.float32)
    b=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)
    assert a.shape==b.shape
    delta=np.abs(a-b);comparison.append({'camera':path.stem,'mean_8bit_difference':float(delta.mean()),'maximum_8bit_difference':float(delta.max())})
    shutil.copy2(path,out/path.name)
assert len(comparison)==14
report={'status':'PASS' if max(v['mean_8bit_difference'] for v in comparison)<.25 else 'FAIL','images':comparison,'contact_checks':contact['objects_checked'],'objective_checks':len(checks['checks']),'source_sha256':provenance['output_sha256']}
(out/'cold_comparison.json').write_text(json.dumps(report,indent=2))
for name in ['checks.json','contacts.json','clearance_and_states.json','provenance.json']:shutil.copy2(cold/name,out/name)
names=[v['camera'] for v in comparison];sheet=Image.new('RGB',(1500,5*350),(21,27,29));draw=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
    tile=Image.open(out/(name+'.png')).convert('RGB');tile.thumbnail((500,320));x=(i%3)*500;y=(i//3)*350
    sheet.paste(tile,(x,y+26));draw.text((x+9,y+7),name,fill=(228,234,224))
sheet.save(out/'CONTACT_SHEET.jpg',quality=93)
print(json.dumps(report))
assert report['status']=='PASS'
