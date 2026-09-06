"""Copy inspected PNG evidence without altering pixels; record exact delivered source hashes."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
HERE=Path(__file__).resolve().parent;PROD=HERE.parent/'production';REVIEW=PROD/'renders/review';FINAL=PROD/'renders/final/tactile'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={};records=[]
for name in ['spawnroom_tactile.blend','spawnroom_tactile_walk.blend','spawnroom_tactile_slice.blend']:
    p=HERE/name;sources[name]={'sha256':digest(p),'bytes':p.stat().st_size}
for folder,destination,pattern in [('tactile-cold-01',FINAL,'*.png'),('tactile-walk-cold-final',FINAL/'walk','VALIDATE_*.png'),('tactile-walk-03',FINAL/'walk','DETAIL_*.png'),('tactile-slice-02',FINAL/'slice','SLICE_*.png')]:
    destination.mkdir(parents=True,exist_ok=True)
    for p in sorted((REVIEW/folder).glob(pattern)):
        target=destination/p.name;shutil.copyfile(p,target)
        with Image.open(target) as im:im.verify()
        records.append({'output':str(target.relative_to(FINAL)),'rendered_in':'renders/review/'+folder,'sha256':digest(target)})
for folder,destination in [('tactile-cold-01',FINAL),('tactile-walk-cold-final',FINAL/'walk')]:
    for name in ['contact_validation.json','objective_validation.json','dependency_validation.json','cameras.json']:
        shutil.copyfile(REVIEW/folder/name,destination/name)
    checks=json.loads((destination/'dependency_validation.json').read_text());assert checks['pass']
    file='spawnroom_tactile_walk.blend' if destination.name=='walk' else 'spawnroom_tactile.blend'
    assert checks['source_sha256']==sources[file]['sha256'],file
    assert len(list(destination.glob('VALIDATE_*.png')))==11
shutil.copyfile(REVIEW/'tactile-room-02/source_inventory.json',FINAL/'source_inventory.json')
shutil.copyfile(PROD/'tactile_walk_cold_comparison.json',FINAL/'walk/cold_comparison.json')
report={'sources':sources,'renders':records,'render_contract':{'blender':'5.2.0 LTS','resolution':[1440,900],'view_transform':'AgX','look':'AgX - Medium High Contrast','exposure':.3,'cycles':'32 samples, HIP on Radeon RX 9070 XT, denoising','walking':'EEVEE 64 samples; Material Preview startup using scene lights/world; four baked volumes and four unshadowed floor-bounce approximations','slice':'Cycles CPU 24 samples, denoising'},'note':'The final walking copy differs from walk-03 only in saved viewport startup mode. All eleven fresh-open images pass comparison. Its two DETAIL frames retain the inspected walk-03 pixels. Warm walk-03 camera manifest is inherited from the verified source build, whose cameras prepare_lit_walk does not modify.'}
(FINAL/'render_provenance.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'sources':sources,'images':len(records),'output':str(FINAL)},indent=2))
