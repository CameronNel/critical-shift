"""Local review gallery: original, generated concept, actual Blender exterior."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exteriors';current=json.loads((OUT/'CURRENT.json').read_text())
cards=[]
for sid,rev in current.items():
 title=sid.replace('-',' ').title()
 images=[]
 for label,path in [('Original scene',f'{sid}/baseline/OBLIQUE.png'),('Generated concept',f'{sid}/art/concept-R01.png'),('Built scene — '+rev,f'{sid}/review-{rev}/OBLIQUE.png')]:
  if not (OUT/path).exists() and label=='Original scene':path=f'{sid}/baseline/FRONT.png'
  images.append(f'<figure><a href="{path}"><img loading="lazy" src="{path}" alt="{html.escape(title+": "+label)}"></a><figcaption>{label}</figcaption></figure>')
 views=' '.join(f'<a href="{sid}/review-{rev}/{v}.png">{v.title()}</a>' for v in ['FRONT','OBLIQUE','REVERSE','DETAIL'])
 cards.append(f'<section id="{sid}"><h2>{title} <small>{rev}</small></h2><div class="compare">'+''.join(images)+f'</div><p>{views} · <a href="{sid}/exterior-{rev}.blend">Editable Blender package</a> · <a href="{sid}/audit-{rev}.json">Clearance audit</a></p></section>')
nav=' '.join(f'<a href="#{sid}">{sid.replace("-"," ")}</a>' for sid in current)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Critical Shift exterior build review</title><style>
*{box-sizing:border-box}body{margin:0;background:#181e23;color:#e7e2d7;font:16px/1.5 system-ui,sans-serif}header,main{max-width:1560px;margin:auto;padding:28px}h1{font-size:32px;margin:0 0 12px}h2{font-size:24px}small{color:#cbb17a;font-size:15px}nav{display:flex;flex-wrap:wrap;gap:8px 18px}a{color:#d8bc80;text-underline-offset:4px}section{padding:20px 0 36px;border-top:1px solid #46505a;scroll-margin:16px}.compare{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}figure{margin:0;background:#252d34}img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}figcaption{padding:8px 12px;color:#ddd7c9}p{max-width:1080px}section p a{margin-right:10px}@media(max-width:850px){.compare{grid-template-columns:1fr}header,main{padding:18px}}
</style><header><h1>Critical Shift — exterior build review</h1><p>Twelve additive exterior packages. Compare the original scene, generated design preview and actual Cycles render. Connecting structures remain reserved gaps. Images and models are local files.</p><p><a href="../blender/facility_master_A05_exteriors.blend">A05 assembled master</a> · <a href="../production/COLD_EXTERIOR_MASTER_CHECK.json">Cold integration check</a> · <a href="CONCEPT_PROMPTS.md">Concept prompts</a></p><nav>'''+nav+'</nav></header><main>'+''.join(cards)+'</main></html>'
assembled=''.join(f'<figure><a href="../production/material-views-A05/{name}.png"><img src="../production/material-views-A05/{name}.png" alt="Actual assembled exterior render"></a><figcaption>Actual assembled scene</figcaption></figure>' for name in ['E03_COMPLETE_EXTERIOR','E02_FACILITY_EXTERIOR'] if (ROOT/'production/material-views-A05'/(name+'.png')).exists())
page=page.replace('<main>','<main>'+assembled)
(OUT/'gallery.html').write_text(page,encoding='utf-8');print(OUT/'gallery.html')
