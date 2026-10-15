"""Arrange real evidence pixels. Crops are lossless, unscaled and unretouched.

Contact sheets and the owner comparison are navigation aids. Canonical full-size
renders and their hashes remain the review authority.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def pack(label):
    main = HERE/'renders-A2'/label
    supplemental = HERE/'renders-A2'/(label+'-supplemental')
    dest = HERE/'renders-A2'/(label+'-review');dest.mkdir(exist_ok=True)
    frames = sorted(main.glob('*.png')) + sorted(supplemental.glob('*.png'))
    assert len(frames) == 29, 'Full 22+7 evidence required'
    sheet=Image.new('RGB',(1920,((len(frames)+3)//4)*300),(24,26,28))
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(frames):
        im=Image.open(p).convert('RGB');assert im.size == (1920,1080)
        x=(i%4)*480;y=(i//4)*300
        sheet.paste(im.resize((480,270)),(x,y));draw.text((x+8,y+278),p.stem,fill=(240,230,215))
    sheet.save(dest/'contact-sheet.jpg',quality=95)
    # Camera layouts are fixed by the original room/evidence scripts.
    crops = {
        'EXHAUST_FLANGE':(main/'C04_EXHAUST.png',(250,250,1650,940)),
        'CONDENSATE_CONTROLS':(main/'C05_RETURN.png',(420,80,1320,1020)),
        'COOLING_ISOLATORS':(supplemental/'S02_LOCAL_CW.png',(0,120,1920,1080)),
        'OPERATOR_LABELS':(main/'C07_OPERATOR.png',(465,170,1460,955)),
        'GLASS_EDGES':(supplemental/'S04_GLASS.png',(160,80,1760,1000)),
        'FLOOR_SUPPORT_CONTACTS':(supplemental/'S05_FEET.png',(100,190,1820,1060)),
        'DOOR_ACCESS_REVEAL':(main/'C01_ENTRY.png',(0,0,1920,1080)),
    }
    receipt={'label':label,'policy':'Lossless original-pixel crops, no scaling, sharpening, recolouring or image generation. Sheet thumbnails are navigation only.','crops':[]}
    for name,(source,rect) in crops.items():
        output=dest/(name+'.png');Image.open(source).crop(rect).save(output)
        receipt['crops'].append({'name':name,'source':str(source.relative_to(HERE)),'source_sha256':digest(source),'pixel_box':rect,'output_sha256':digest(output)})
    (dest/'crop-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return dest

def owner(label='owner-map'):
    paths=[HERE/'renders-A2/baseline-map/OWNER_A1.png',HERE/'renders-A2'/label/'OWNER_A2.png']
    canvas=Image.new('RGB',(3840,1124),(24,26,28));draw=ImageDraw.Draw(canvas)
    rows=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB');assert im.size==(1920,1080)
        canvas.paste(im,(1920*i,44));draw.text((1920*i+20,14),'A1 / BEFORE' if i==0 else 'A2 / AFTER',fill=(240,230,215))
        rows.append({'file':str(p.relative_to(HERE)),'sha256':digest(p)})
    dest=HERE/'renders-A2'/label;canvas.save(dest/'OWNER_A1_A2.png')
    (dest/'comparison.json').write_text(json.dumps({'policy':'Original pixels side by side; same eye, target, 16mm lens, resolution, samples and original map renderer. Header only; no retouching.','eye':[1.6,3.9,-4.4],'target':[6,10.3,-4.8],'lens_mm':16,'samples':32,'images':rows},indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('labels',nargs='*');ap.add_argument('--owner',action='store_true');ap.add_argument('--owner-label',default='owner-map');a=ap.parse_args()
    for label in a.labels:pack(label)
    if a.owner:owner(a.owner_label)
