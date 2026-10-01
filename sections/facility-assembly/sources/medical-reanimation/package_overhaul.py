"""Package the complete labelled review and local authoring source, without promotion.

System Python: package_overhaul.py --cycle cycle-17 [--portable-map]
PNG files remain the exact Blender outputs. The single-file HTML embeds them.
"""
import argparse,base64,hashlib,html,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=ROOT/'revamp-review/production'
a=argparse.ArgumentParser();a.add_argument('--cycle',required=True);a.add_argument('--portable-map',action='store_true');a.add_argument('--dest',default='/workspace/shared');args=a.parse_args()
SHARE=Path(args.dest);SHARE.mkdir(parents=True,exist_ok=True)
source=ROOT/'module_overhaul_R2.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest()
render=P/'renders'/args.cycle
manifest=json.loads((render/'manifest.json').read_text())
if manifest.get('source_sha256')!=sha:raise RuntimeError('Gallery source differs from rendered source')
if manifest.get('complete') is not True:raise RuntimeError('A completed full render manifest is required')
shots=manifest['shots']
if len(shots)!=24:raise RuntimeError('A complete 24-view set is required')
final=[]
for shot in shots:
 path=render/(shot['id']+'.png')
 if not path.exists():raise RuntimeError(path)
 final.append((shot.get('label',shot['id']),path,shot.get('group','assets')))
references=[]
for path in sorted((ROOT/'revamp-review/room-survey').glob('*.png')):references.append(('Original | '+path.stem,path,'original'))
for path in sorted((ROOT/'revamp-review/spawn-reference').glob('*.png')):references.append(('Approved spawn | '+path.stem,path,'spawn'))
for name,label in [('concept-R3.png','Generated room direction'),('clinical-propaganda.png','Authored corporate clinical print')]:references.append((label,ROOT/'revamp-review/concepts'/name,'concept'))
all_images=final+references
cards=[]
for title,path,group in all_images:
 enc=base64.b64encode(path.read_bytes()).decode()
 cards.append('<figure data-group="'+group+'"><a href="#" onclick="openFull(this.firstElementChild);return false"><img loading="lazy" src="data:image/png;base64,'+enc+'" alt="'+html.escape(title)+'"></a><figcaption>'+html.escape(title)+'</figcaption></figure>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Critical Shift — Reanimation room</title><style>
:root{color-scheme:dark}body{background:#151924;color:#dcd8cf;font:16px system-ui;margin:0}header,nav,main,footer{max-width:1500px;margin:auto;padding:24px}header{padding-bottom:8px}h1{font-size:30px;margin:0 0 12px;color:#eee6d2}p{line-height:1.55;max-width:1000px}small{color:#929eb5}nav{display:flex;gap:8px;flex-wrap:wrap;position:sticky;top:0;background:#151924ed;z-index:2}button{border:1px solid #56668c;color:#dcd8cf;background:#29324c;border-radius:3px;padding:9px 14px;cursor:pointer}button[aria-pressed=true]{background:#92574a;border-color:#bb7967}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,540px),1fr));gap:22px}figure{margin:0;background:#202635;border:1px solid #343e55}figure img{width:100%;display:block}figcaption{padding:12px;font-size:13px;letter-spacing:.03em}figure[hidden]{display:none}a{color:#d4b879}footer{font-size:12px;color:#929eb5}code{overflow-wrap:anywhere}
</style><header><small>CRITICAL SHIFT / ISOLATED ART BRANCH</small><h1>Reanimation / medical room</h1><p>One red berth light, a dim warm workbench lamp and two directional accents. Established clinical machinery, expired stock, interrupted work and corporate pressure to return to the shift. The original layout and room boundaries are preserved.</p><p>24 labelled 1067 × 600 Blender renders: four corner cutaways, each wall, ten asset heroes, three player-height views, two material details and one concealed-bag inspection. The inspection alone uses a temporary 2 W fill, which is not saved in the scene.</p><p>OCRU revives incapacitated or biologically offline workers following the retrieval and restart procedure. The bed at the opposite wall is the recovery cot.</p><small>Evidence cycle: CYCLE · Scene SHA-256: <code>__SOURCE_HASH__</code></small></header><nav>
<button data-filter="all" aria-pressed="true">Final views</button><button data-filter="corners">Four corners</button><button data-filter="walls">Each wall</button><button data-filter="assets">Asset heroes</button><button data-filter="mandatory">Player height</button><button data-filter="details">Details</button><button data-filter="inspection">Hidden bag</button><button data-filter="original">Original survey</button><button data-filter="spawn">Spawn fidelity reference</button><button data-filter="concept">Generated direction / print</button><button data-filter="every">All useful images</button></nav><main>CARDS</main><footer>Branch: codex/reanimation-room-revamp-20260930. Editable scene: REANIMATION_EDIT_LOCAL. Assembled map remains a read-only linked reference and is unchanged. Review scores and technical evidence are included with the source package; images are direct Blender outputs with small camera labels.</footer><script>
function openFull(img){const w=window.open();if(w){const el=w.document.createElement('img');el.src=img.src;el.style.maxWidth='100%';w.document.body.style.background='#151924';w.document.body.appendChild(el);}}const finalGroups=new Set(['corners','walls','assets','mandatory','details','inspection']);function filter(value){document.querySelectorAll('figure').forEach(x=>x.hidden=!(value==='every'||(value==='all'&&finalGroups.has(x.dataset.group))||x.dataset.group===value));document.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x.dataset.filter===value));}document.querySelectorAll('button').forEach(x=>x.onclick=()=>filter(x.dataset.filter));filter('all');
</script></html>'''.replace('CYCLE',html.escape(args.cycle)).replace('__SOURCE_HASH__',sha).replace('CARDS','\n'.join(cards))
(SHARE/'reanimation-overhaul-gallery.html').write_text(page)
with zipfile.ZipFile(SHARE/'reanimation-overhaul-images.zip','w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for title,path,group in all_images:z.write(path,group+'/'+path.name)
 z.writestr('manifest.json',json.dumps({'source_sha256':sha,'cycle':args.cycle,'shots':shots,'reference_count':len(references)},indent=2))
# Review archive preserves useful prior renders and the documented failures.
with zipfile.ZipFile(SHARE/'reanimation-overhaul-review.zip','w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for path in sorted((ROOT/'revamp-review').rglob('*')):
  if path.is_file() and path.suffix in {'.png','.jpg','.jpeg','.json','.md','.txt','.py','.log'}:z.write(path,str(path.relative_to(ROOT)))
shutil.copy2(source,SHARE/'reanimation-room-overhaul.blend')
# Preserve repository paths so the linked main-map library resolves unchanged.
repo=ROOT.parents[3]
files=[source,ROOT/'module_overhaul_R1.blend',ROOT/'revamp-review/baseline.json',ROOT/'revamp-review/workspace.json']
files+=list(ROOT.glob('*.py'))
files+=list((ROOT/'revamp-review/concepts').glob('*'))
files+=[p for p in (P/'critics').rglob('*') if p.is_file() and p.suffix in {'.json','.md','.txt','.py','.log','.jpg','.jpeg'}]+list(P.glob('*.json'))+list(P.glob('*.md'))
files+=list((ROOT/'revamp-review/textures').glob('*'))
files+=list((P/'fonts').glob('*'))
files+=list((ROOT/'contracts').rglob('*'))
for rel in json.loads((ROOT/'revamp-review/baseline.json').read_text())['protected_sha256']:files.append(ROOT.parents[1]/rel)
files += [repo/'AGENTS.md',repo/'MAP.md',repo/'MAP.json',repo/'design/GAME_SPEC.md',repo/'design/ART_DIRECTION.md',repo/'design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md']
files += [repo/'sections/facility-assembly/README.md',repo/'sections/facility-assembly/production/SOURCES.json']
for skill in ('blender-headless','blender-uv-texturing'):
 files+=list((repo/'.agents/skills'/skill).rglob('*'))
files += [repo/'design/ART_REFERENCE_INDEX.md',repo/'design/blender-headless/README.md']
if args.portable_map:
 dependency_manifest=json.loads((P/'dependency-manifest.json').read_text())
 if dependency_manifest['source_sha256']!=sha:raise RuntimeError('Portable dependencies must be validated for this source')
 files+=[Path(x['absolute_path']) for x in dependency_manifest['linked_libraries']]
 for item in dependency_manifest.get('unpacked_files',[]):
  path=Path(item['absolute_path'] if isinstance(item,dict) else item)
  if path.is_relative_to(repo):files.append(path)
  elif isinstance(item,dict) and (item.get('required_for_cold_open') or item.get('required_for_rebuild')):
   raise RuntimeError('Required external file needs an explicit portable destination: '+str(path))
with zipfile.ZipFile(SHARE/'reanimation-overhaul-source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for path in sorted(set(files)):
  if path.is_file():z.write(path,str(path.relative_to(repo)))
 z.writestr('OPEN_ME.txt','Open sections/facility-assembly/sources/medical-reanimation/module_overhaul_R2.blend in Blender 5.2.2 LTS or newer. Editable scene REANIMATION_EDIT_LOCAL. Original main map is a read-only linked reference. Source scripts reproduce from the included R1 baseline, original medical module and approved spawn module. Source hashes, review scores, cold-open and render comparison evidence are in revamp-review/production. No main-map edits or source promotion.\n')
print(json.dumps({'scene_sha256':sha,'cycle':args.cycle,'images':len(all_images),'artifacts':{p.name:p.stat().st_size for p in SHARE.glob('reanimation-overhaul-*') if p.is_file()}},indent=2))
