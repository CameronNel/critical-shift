import json,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'production/connection-views'
data=json.loads((out/'manifest.json').read_text());assert len(data['views'])==12
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
groups=['Production connections','Service connections','Access and exterior']
for page,title in enumerate(groups):
 im=Image.new('RGB',(1600,1060),(24,28,33));d=ImageDraw.Draw(im)
 d.text((20,15),title,font=bold,fill='white')
 d.text((20,53),'Actual scene previews • dashed guides = unbuilt connection reservations',font=font,fill='#d2c39e')
 for i,v in enumerate(data['views'][page*4:page*4+4]):
  x=(i%2)*800;y=100+(i//2)*480
  frame=Image.open(out/(v['id']+'.png')).convert('RGB');frame.thumbnail((790,444))
  im.paste(frame,(x+5,y));d.text((x+12,y+449),v['caption'],font=font,fill='white')
 im.save(out/f'gallery-{page+1}.jpg',quality=93)
cards=''.join(f'<a href="{v["id"]}.png"><img src="{v["id"]}.png"><span>{html.escape(v["caption"])}</span></a>' for v in data['views'])
(out/'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>Facility connections and exterior</title><style>body{background:#181c21;color:#eee;font:18px Arial;margin:24px}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}a{color:inherit;text-decoration:none;background:#252b33}img{width:100%;display:block}span{display:block;padding:12px}p{color:#d2c39e}</style><h1>Connecting points and outside</h1><p>Actual master-scene solid-view previews. Dashed guides are unbuilt reservations. Click any image for full resolution. Source room geometry and master file are unchanged.</p><main>'+cards+'</main>',encoding='utf-8')
print('Three image boards and full-resolution gallery ready.')
