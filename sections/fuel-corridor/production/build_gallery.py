"""Create an offline gallery from a complete, named Blender render batch."""
import argparse
import html
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('render_folder', help='Folder relative to production, e.g. renders/review/full04')
p.add_argument('--accepted', action='store_true')
a = p.parse_args()
here = Path(__file__).resolve().parent
batch = (here / a.render_folder).resolve()
assert batch.is_relative_to(here), 'Gallery images must remain inside production'
views = [
    ('C01_ENTRY', 'Entry and route choice'),
    ('C02_PRIMARY_ROUTE', 'Freight route'),
    ('C03_HERO', 'Staging bay and freight gate'),
    ('C04_REVERSE', 'Return toward the refinery'),
    ('C05_EAST_TURN', 'Eastern freight turn'),
    ('C06_REACTOR_THRESHOLD', 'Reactor threshold'),
    ('C07_BYPASS', 'Service bypass'),
    ('C08_SERVICE_JUNCTION', 'Clean service junction'),
    ('C09_MATERIALS', 'Loaded carrier'),
    ('C10_PLANT_HEADER', 'Plant service header'),
    ('D01_CARRIER_OPERATION', 'Carrier restraints and brakes'),
    ('D02_WORKBENCH', 'Maintenance workbench'),
    ('D03_UTILITY', 'Staging utility station'),
    ('D04_REACTOR_WIDE', 'Complete reactor approach'),
    ('D05_GATE_MECHANISM', 'Gate drive and service light'),
    ('D06_SERVICE_RECESS', 'Recessed service station'),
]
images = []
for stem, title in views:
    path = batch / (stem + '.png')
    assert path.is_file(), f'Missing required render: {path}'
    images.append({'src': path.relative_to(here).as_posix(), 'title': title})
status = 'Verified scene' if a.accepted else 'Review candidate — acceptance pending'
cards = ''.join(f'<button class="card" data-index="{i}" aria-label="Open {html.escape(v["title"])}"><img loading="lazy" src="{html.escape(v["src"])}" alt="{html.escape(v["title"])}"><span><b>{i+1:02d}</b>{html.escape(v["title"])}</span></button>' for i,v in enumerate(images))
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fuel Corridor · Critical Shift</title><style>
*{box-sizing:border-box}body{margin:0;background:#e9e8e2;color:#20292c;font:16px/1.5 system-ui,sans-serif}header,main,footer{max-width:1320px;margin:auto;padding:32px}header{padding-top:54px;border-bottom:1px solid #b7b8b3}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:700;color:#5f6b70}h1{font-size:clamp(34px,6vw,64px);line-height:1.04;letter-spacing:-.04em;margin:12px 0 16px}p{max-width:750px;margin:12px 0}.status{display:inline-block;padding:6px 12px;border-left:4px solid #c96935;background:#deded6;font-size:13px;font-weight:600}.links{display:flex;gap:24px;margin-top:20px}a{color:#324e57;text-underline-offset:4px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px}.card{appearance:none;border:0;background:#f5f4ee;box-shadow:0 1px 2px #0002;padding:0;cursor:pointer;text-align:left;color:inherit;font:inherit}.card:hover{box-shadow:0 0 0 2px #b66637}.card:focus-visible{outline:3px solid #bd612b;outline-offset:4px}.card img{display:block;width:100%;aspect-ratio:3/2;object-fit:contain;background:#1d2327}.card span{display:flex;gap:18px;padding:14px 18px}.card b{color:#a4532d;font-size:13px;letter-spacing:.08em}footer{font-size:13px;color:#57666a;padding-top:0}dialog{width:min(98vw,1700px);max-width:none;padding:0;background:#141a1e;border:1px solid #687176;color:#f5f4ec}dialog::backdrop{background:#080d10ed}dialog img{display:block;width:100%;height:calc(90vh - 68px);object-fit:contain}.viewerbar{display:flex;align-items:center;gap:12px;padding:12px 18px}.viewerbar strong{flex:1;font-size:15px}.viewerbar button{border:1px solid #788184;background:#222e33;color:#f6f4ed;padding:9px 14px;cursor:pointer}.viewerbar button:hover{background:#41525a}@media(max-width:700px){header,main,footer{padding:22px}.grid{grid-template-columns:1fr;gap:20px}.links{flex-wrap:wrap;gap:14px}dialog img{height:75vh}.viewerbar{padding:8px;gap:8px}.viewerbar strong{font-size:12px}.viewerbar button{padding:9px}}
</style><header><div class="eyebrow">CRITICAL SHIFT / FACILITY CONNECTIONS</div><h1>Fuel Corridor</h1><div class="status">STATUS</div><p>An original freight route, staging bay and service bypass. Ten room angles and six close inspections show the complete authored section.</p><nav class="links"><a href="../architecture/A101-plan.svg">Dimensioned plan</a><a href="../architecture/SPEC_CONTENTS.md">Room contents</a><a href="../blender/Fuel_Corridor.blend">Blender scene</a></nav></header><main><div class="grid">CARDS</div></main><footer>Actual Blender renders. Select an image to inspect it; use the arrow keys to move between views. Concept images are kept separately in the art folder.</footer><dialog id="viewer"><img id="large" alt=""><div class="viewerbar"><button id="prev" aria-label="Previous view">←</button><strong id="caption"></strong><button id="next" aria-label="Next view">→</button><button id="close">Close</button></div></dialog><script>
const views=IMAGES;let current=0;const viewer=document.querySelector('#viewer'),large=document.querySelector('#large'),caption=document.querySelector('#caption');function show(i){current=(i+views.length)%views.length;large.src=views[current].src;large.alt=views[current].title;caption.textContent=`${String(current+1).padStart(2,'0')} / ${views.length} · ${views[current].title}`;if(!viewer.open)viewer.showModal()}document.querySelectorAll('[data-index]').forEach(el=>el.addEventListener('click',()=>show(Number(el.dataset.index))));document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#close').onclick=()=>viewer.close();document.addEventListener('keydown',e=>{if(!viewer.open)return;if(e.key==='ArrowLeft')show(current-1);if(e.key==='ArrowRight')show(current+1)});
</script></html>'''
page = page.replace('STATUS', html.escape(status)).replace('CARDS', cards).replace('IMAGES', json.dumps(images))
output = here / 'SCENE_GALLERY.html'
output.write_text(page, encoding='utf-8')
print(json.dumps({'gallery': str(output), 'views': len(images), 'status': status}))
