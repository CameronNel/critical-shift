"""Package unchanged renders and compare the independently reopened delivery file."""
import json, shutil, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent.parent
warm=ROOT/'production/renders/review/inhabited-04'
cold=ROOT/'production/renders/review/inhabited-cold'
out=ROOT/'production/renders/final/inhabited';out.mkdir(parents=True,exist_ok=True)
checks=json.loads((cold/'checks.json').read_text());assert checks['status']=='PASS'
contacts=json.loads((cold/'contacts.json').read_text());assert contacts['status']=='PASS'
provenance=json.loads((cold/'provenance.json').read_text())
source=Path(provenance['output']);assert hashlib.sha256(source.read_bytes()).hexdigest()==provenance['sha256']
comparison=[]
for path in sorted(cold.glob('*.png')):
    a=np.asarray(Image.open(warm/path.name).convert('RGB'),dtype=np.float32)
    b=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)
    assert a.shape==b.shape
    delta=np.abs(a-b)
    comparison.append({'camera':path.stem,'mean_8bit_difference':float(delta.mean()),'maximum_8bit_difference':float(delta.max())})
    shutil.copy2(path,out/path.name)
assert len(comparison)==18
report={'status':'PASS' if max(v['mean_8bit_difference'] for v in comparison)<.25 else 'FAIL','images':comparison,'contact_checks':contacts['objects_checked'],'objective_checks':len(checks['checks']),'source_sha256':provenance['sha256']}
(out/'cold_comparison.json').write_text(json.dumps(report,indent=2))
for name in ['checks.json','contacts.json','provenance.json']:shutil.copy2(cold/name,out/name)
sheet=Image.new('RGB',(1500,math.ceil(len(comparison)/3)*350),(21,27,29));draw=ImageDraw.Draw(sheet)
for i,row in enumerate(comparison):
    tile=Image.open(out/(row['camera']+'.png')).convert('RGB');tile.thumbnail((500,320));x=(i%3)*500;y=(i//3)*350
    sheet.paste(tile,(x,y+26));draw.text((x+9,y+7),row['camera'],fill=(228,234,224))
sheet.save(out/'CONTACT_SHEET.jpg',quality=93)
print(json.dumps(report))
assert report['status']=='PASS'
