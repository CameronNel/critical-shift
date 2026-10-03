"""Validate and package the labelled render survey as a gallery and ZIP."""
import html
import base64
import json
from pathlib import Path
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revamp-review/room-survey'
manifest = json.loads((OUT/'manifest.json').read_text())
assert len(manifest['shots']) == 18
for shot in manifest['shots']:
    path = OUT/(shot['id']+'.png')
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    assert struct.unpack('>II', data[16:24]) == (1600,900), path
parts = ['''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reanimation room — labelled render survey</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:32px;background:#10171b;color:#e8eef1;font:16px system-ui,sans-serif}
main{max-width:1500px;margin:auto}h1{font-size:28px;margin:0}p{color:#aebfc8}nav{display:flex;gap:22px;margin:24px 0}a{color:#b9d9e7}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}figure{margin:0;background:#192329;border:1px solid #35444c;border-radius:8px;overflow:hidden}
img{width:100%;display:block}figcaption{padding:10px 14px;font-size:13px}h2{margin-top:40px;font-size:21px}
dialog{background:#0c1114;border:1px solid #536772;padding:12px;max-width:96vw;max-height:96vh;color:white}dialog::backdrop{background:#000c}
dialog img{max-height:85vh;width:auto;max-width:91vw}button{background:#283a44;color:white;border:1px solid #617782;border-radius:4px;padding:8px 16px;cursor:pointer}
@media(max-width:800px){body{padding:18px}.grid{grid-template-columns:1fr}}
</style><main><h1>Reanimation room</h1>
<p>18 labelled views · 1600 × 900 · Blender 5.2.2 LTS</p>
<p>Front is the entry side. Left/right refer to looking into the room from the entry. Click any image to enlarge.</p>
<p>Corner views are elevated cutaways: the ceiling and two near wall planes are hidden for inspection. Wall and asset views retain the full room geometry.</p>
<p>Room materials and practical lighting are retained. The cart close-up adds a temporary soft fill to reveal its lifting mechanism in the dark parking bay.</p>
<nav><a href="#corners">Four corners</a><a href="#walls">Four walls</a><a href="#assets">Significant assets</a></nav>''']
for group,title in [('corners','Four room corners'),('walls','Each wall'),('assets','Significant assets')]:
    parts.append(f'<h2 id="{group}">{title}</h2><div class="grid">')
    for shot in manifest['shots']:
        if shot['group'] != group: continue
        label = html.escape(shot['label'])
        name = shot['id']+'.png'
        parts.append(f'<figure><a href="{name}" class="shot"><img loading="lazy" src="{name}" alt="{label}"></a><figcaption>{label}</figcaption></figure>')
    parts.append('</div>')
parts.append('''</main><dialog><button autofocus>Close</button><p></p><img alt=""></dialog>
<script>const d=document.querySelector('dialog');document.querySelectorAll('.shot').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();d.querySelector('img').src=a.querySelector('img').src;d.querySelector('img').alt=a.querySelector('img').alt;d.querySelector('p').textContent=a.querySelector('img').alt;d.showModal()}));d.querySelector('button').onclick=()=>d.close();d.onclick=e=>{if(e.target===d)d.close()};</script></html>''')
(OUT/'index.html').write_text('\n'.join(parts))
delivery_root = Path('/workspace/shared')
delivery = delivery_root / 'reanimation-room-survey'
delivery.parent.mkdir(exist_ok=True)
shutil.copytree(OUT, delivery, dirs_exist_ok=True)
standalone = (OUT/'index.html').read_text()
for shot in manifest['shots']:
    name = shot['id']+'.png'
    encoded = 'data:image/png;base64,'+base64.b64encode((OUT/name).read_bytes()).decode()
    standalone = standalone.replace('href="'+name+'"', 'href="#"')
    standalone = standalone.replace('src="'+name+'"', 'src="'+encoded+'"')
(delivery_root/'reanimation-room-gallery.html').write_text(standalone)
with zipfile.ZipFile(delivery_root/'reanimation-room-survey.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for file in sorted(delivery.iterdir()):
        bundle.write(file, arcname='reanimation-room-survey/'+file.name)
print('PACKAGED', len(manifest['shots']), 'labelled renders')
