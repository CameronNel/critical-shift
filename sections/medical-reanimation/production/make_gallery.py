"""Build a portable gallery of actual final renders, separate from generated concepts."""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'production/renders/final/render_manifest.json').read_text())
cards=[]
for folder in ['final','states/M11']:
 for p in sorted((R/'production/renders'/folder).glob('*.png')):
  rel=p.relative_to(R).as_posix()
  cards.append(f'<figure><a href="{rel}"><img loading="lazy" src="{rel}" alt="{html.escape(p.stem)}"></a><figcaption>{html.escape(p.stem)} — actual Blender render</figcaption></figure>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Medical / Reanimation — actual scene</title><style>body{margin:0;background:#222320;color:#ece9df;font:17px/1.55 system-ui}main{max-width:1440px;margin:auto;padding:36px}h1{font-size:36px;margin-bottom:8px}p{max-width:900px}a{color:#e9bb80}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:24px}figure{margin:0;background:#30312d}img{display:block;width:100%;height:auto}figcaption{padding:12px 16px}@media(max-width:520px){section{grid-template-columns:1fr}main{padding:16px}}</style><main><h1>Medical / Reanimation</h1><p>Actual M11 saved-scene renders: ten fixed cameras, four additional player approaches and six demonstrated interaction poses. Grok's original layout is preserved; this is the separate original art rebuild. These are not generated concepts.</p><p><a href="blender/medical_integration.blend">Blender scene</a> · <a href="architecture/floorplan.png">Dimensioned plan</a> · <a href="architecture/INTEGRATION.md">Integration contract</a> · <a href="production/critics/luna-scene-M11.md">Independent review</a></p><section>'''+''.join(cards)+'''</section><p>The transfer proxy is validation dressing. Runtime game behavior and the unbound neighboring junction remain host integration work.</p></main></html>'''
(R/'gallery.html').write_text(page,encoding='utf-8')
print('GALLERY',len(cards))
