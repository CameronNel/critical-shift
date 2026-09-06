"""Index the fifty actual PNG renders without changing the originals."""
from pathlib import Path
import argparse,json,hashlib,html
from PIL import Image,ImageDraw,ImageFont,ImageStat

def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,required=True);p.add_argument('--renders',type=Path,required=True);a=p.parse_args()
    rows=json.loads((a.scene/'camera_manifest.json').read_text());records=[]
    if len(rows)!=50:raise RuntimeError('Fifty camera records required')
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    except OSError:font=ImageFont.load_default()
    for row in rows:
        path=a.renders/(row['id']+'.png')
        if not path.is_file():raise FileNotFoundError(path)
        im=Image.open(path);im.load();gray=im.convert('L');hist=gray.histogram();pixels=im.width*im.height
        records.append({**row,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':im.size,'mean_luma':round(ImageStat.Stat(gray).mean[0],2),'black_fraction':round(sum(hist[:6])/pixels,4)})
    for page in range(10):
        sheet=Image.new('RGB',(1600,1644),(24,25,26));d=ImageDraw.Draw(sheet)
        for j,row in enumerate(records[page*5:page*5+5]):
            x=(j%2)*800;y=(j//2)*548
            im=Image.open(a.renders/row['file']).convert('RGB');im.thumbnail((800,501));sheet.paste(im,(x,y+42))
            d.text((x+10,y+9),row['id']+'  '+row['title'],font=font,fill=(235,230,219))
        sheet.save(a.renders/f'contact_{page+1:02}.jpg',quality=94)
    (a.renders/'gallery_manifest.json').write_text(json.dumps(records,indent=2))
    body=''.join(f'<figure id="{r["id"]}"><figcaption><b>{r["id"]}</b> {html.escape(r["title"])}'+(f' | Sector {r["sector"]}, state {r["state"]}' if r['sector'] else '')+f'</figcaption><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}"></a></figure>' for r in records)
    (a.renders/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Gullet: fifty Blender camera views</title><style>body{background:#151617;color:#ddd;font:17px system-ui;margin:28px}figure{margin:20px 0 45px}img{width:100%;max-width:1100px}figcaption{margin-bottom:12px}a{color:#c4ad80}</style><h1>Gullet / fifty actual Blender camera views</h1><p>Rendered scene images, not concept illustrations. Each view records its excavation state. Click for the original PNG.</p>'+body)
    print('GALLERY_VERIFIED',len(records))
if __name__=='__main__':main()
