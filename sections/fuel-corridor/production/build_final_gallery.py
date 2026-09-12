"""Local fixed-camera review gallery with preserved inherited comparison."""
import json,html,sys
from pathlib import Path
root=Path(__file__).resolve().parent
revision=sys.argv[1] if len(sys.argv)>1 else 'final-F09'
manifest=json.loads((root/f'renders/review/{revision}/cold_render_manifest.json').read_text())
cards=[]
for row in sorted(manifest['renders'],key=lambda r:r['camera']):
    name=row['camera'];title=name.replace('_',' ')
    cards.append(f'<figure><a href="renders/review/final-F05/{name}.png"><img loading="lazy" data-camera="{name}" src="renders/review/final-F05/{name}.png" alt="{title}"></a><figcaption>{title}</figcaption></figure>')
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fuel Corridor — fixed-camera review</title><style>
body{margin:0;background:#202226;color:#eee9df;font:16px system-ui,sans-serif}header{padding:32px 4vw;border-bottom:3px solid #db782c}h1{margin:0 0 10px;font-size:32px}p{max-width:900px;line-height:1.5;color:#c5c4bf}button,a{color:inherit}button{border:1px solid #db782c;background:#303237;padding:10px 16px;margin:5px;cursor:pointer}button.active{background:#a95017}main{padding:22px 3vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}figure{margin:0;background:#292c30}img{display:block;width:100%}figcaption{padding:12px}footer{padding:25px 4vw;color:#c5c4bf}@media(max-width:500px){main{grid-template-columns:1fr}}
</style><header><h1>Fuel Corridor</h1><p>Ten fixed room views and six machinery/detail views. Click an image for full resolution. The inherited pack retains the rejected condition; the corrected pack shows F05. This gallery covers the authored corridor, not an assembled or running facility.</p><button class="active" data-pack="final-F05">Corrected F05</button><button data-pack="final-F00-inherited">Inherited / rejected</button></header><main>'''+''.join(cards)+'''</main><footer>Dimensioned plan: <a href="../architecture/A101-plan-preview.png">A101</a> · <a href="../architecture/INTEGRATION_HANDOFF.md">Integration handoff</a> · Independent evidence: production/critics/final-pass</footer><script>
for(const b of document.querySelectorAll('button'))b.onclick=()=>{document.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));for(const image of document.querySelectorAll('img')){const url='renders/review/'+b.dataset.pack+'/'+image.dataset.camera+'.png';image.src=url;image.parentElement.href=url;}};
</script></html>'''
doc=doc.replace('final-F05',revision).replace('Corrected F05','Corrected '+revision.replace('final-','')).replace('shows F05','shows '+revision.replace('final-',''))
walk=root/f'renders/review/{revision}-walkthrough/manifest.json'
if walk.exists():
    w=json.loads(walk.read_text());assert w['complete']
    extra='<section style="padding:24px 4vw"><h2>Player-eye approaches</h2><p>All twelve views are at1.70m eye height. These are authored-scene observations, not an engine playtest.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px">'
    for row in w['renders']:
        n=row['view'];url=f'renders/review/{revision}-walkthrough/{n}.png'
        extra+=f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{n}"></a><figcaption>{n.replace("_"," ")}</figcaption></figure>'
    doc=doc.replace('</main>','</main>'+extra+'</div></section>')
    doc=doc.replace("document.querySelectorAll('img')","document.querySelectorAll('img[data-camera]')")
(root/'FINAL_GALLERY.html').write_text(doc,encoding='utf-8');print('Gallery:',len(cards),'fixed views; walkthrough',walk.exists())
