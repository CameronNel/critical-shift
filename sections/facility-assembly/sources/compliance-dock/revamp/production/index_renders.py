"""Index every actual render without changing image pixels or source scenes."""
from pathlib import Path
import html,json
p=Path(__file__).resolve().parent
rows=[];count=0
for directory in sorted((p/'renders').iterdir()):
 if not directory.is_dir():continue
 manifest=directory/'manifest.json'
 if not manifest.is_file():continue
 data=json.loads(manifest.read_text());shots=data.get('shots',[])
 phase='COMPLETE EVIDENCE' if data.get('complete') else 'INTERRUPTED EVIDENCE'
 if directory.name in {'full-cycle-01-uv','full-cycle-01-neutral'}:phase='INCLUDES FAILED BLACK DIAGNOSTIC — RETAINED'
 if directory.name.endswith('-repair'):phase='OVER-BRIGHT DIAGNOSTIC ATTEMPT — RETAINED'
 cards=[]
 for shot in shots:
  png=directory/(shot['id']+'.png')
  if not png.is_file():continue
  rel=str(png.relative_to(p));label=shot.get('label',shot['id']);count+=1
  cards.append(f'<figure><a href="{html.escape(rel)}"><img loading="lazy" src="{html.escape(rel)}" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>')
 if cards:rows.append(f'<section><h2>{html.escape(directory.name)}</h2><p>{phase} · {len(cards)} images · source {html.escape(data.get("source_sha256",""))[:12]}</p><div class="grid">{"".join(cards)}</div></section>')
page='<!doctype html><meta charset="utf-8"><title>Compliance dock render evidence</title><style>body{background:#171e26;color:#e2ded4;font:15px system-ui;max-width:1440px;margin:30px auto;padding:0 24px}h1,h2{font-weight:600}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px}figure{margin:0;background:#222c37}img{display:block;width:100%;height:auto}figcaption{padding:8px 12px}p{color:#b4bcc3}section{margin:32px 0}a{color:#c5d7ee}</style>'
page+=f'<h1>Compliance dock · actual render evidence</h1><p>{count} images. Completion of a batch is not art acceptance. Read <a href="TASK_STATE.md">production state</a> and <a href="HANDOFF.md">agent handoff</a>. Cutaways and diagnostics are explicitly labelled; original failures remain reviewable. Open this HTML from a checkout; GitHub shows the source file.</p>'+''.join(rows)
(p/'render-gallery.html').write_text(page+'\n');print('INDEXED_IMAGES',count)
