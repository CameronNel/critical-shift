"""Write a reviewable handoff only when current revision renders/hashes are complete."""
import json,hashlib,re,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];C=json.loads((ROOT/'exteriors/CURRENT.json').read_text())
cold=json.loads((ROOT/'production/COLD_EXTERIOR_MASTER_CHECK.json').read_text());assert cold['status']=='PASS'
master=json.loads((ROOT/'production/EXTERIOR_MASTER_MANIFEST.json').read_text());rows=[]
assembled=json.loads((ROOT/'production/material-views-A05/manifest.json').read_text())
assert assembled['source_sha256']==master['master_sha256']
assert {v['id'] for v in assembled['views']}=={'E03_COMPLETE_EXTERIOR','E02_FACILITY_EXTERIOR'}
for v in assembled['views']:
 assert hashlib.sha256((ROOT/'production/material-views-A05'/(v['id']+'.png')).read_bytes()).hexdigest()==v['sha256']
for sid,rev in C.items():
 p=ROOT/'exteriors'/sid;asset=p/f'exterior-{rev}.blend';digest=hashlib.sha256(asset.read_bytes()).hexdigest()
 assert next(r for r in master['exteriors'] if r['section']==sid)['sha256']==digest,sid
 m=json.loads((p/f'review-{rev}/manifest.json').read_text());assert m['source_sha256']==digest,sid
 for v in m['views']:assert hashlib.sha256((p/f'review-{rev}'/(v['camera']+'.png')).read_bytes()).hexdigest()==v['sha256']
 assert len(m['views'])==4
 critics=sorted(p.glob('critic-R*.md'));critic=critics[-1] if critics else None
 score=re.search(r'(\d+)\s*/\s*90',critic.read_text()) if critic else None
 rows.append({'section':sid,'revision':rev,'render_count':4,'asset_sha256':digest,'latest_art_review':str(critic.relative_to(ROOT)) if critic else None,'visual_score_out_of_90':int(score[1]) if score else None})
runpy.run_path(str(ROOT/'blender/make_exterior_gallery.py'))
table='\n'.join(f"| {r['section']} | {r['revision']} | 4 | {r['visual_score_out_of_90'] if r['visual_score_out_of_90'] is not None else 'pending'} / 90 |" for r in rows)
doc=f'''# A05 exterior integration handoff

All twelve sections have generated concept previews and editable additive exterior builds. The master retains A04 placement, original source room geometry and the 21 unbuilt connection reservations. Four actual Cycles HIP views per section (48 total) are hash-bound to their current saved revision. Generated concepts are clearly separated from scene renders in the [local gallery](../exteriors/gallery.html).

## Open

- [Assembled A05 master](../blender/facility_master_A05_exteriors.blend)
- [Concept/render comparison gallery](../exteriors/gallery.html)
- [Actual assembled exterior](material-views-A05/E03_COMPLETE_EXTERIOR.png)
- [Actual power-wing exterior](material-views-A05/E02_FACILITY_EXTERIOR.png)
- [Current revision map](../exteriors/CURRENT.json)
- [Concept prompt set](../exteriors/CONCEPT_PROMPTS.md)
- [Cold integration check](COLD_EXTERIOR_MASTER_CHECK.json)
- [Exterior placement/route screen](EXTERIOR_LAYOUT_AUDIT.json)

## Verification and limits

Fresh-process integration checks pass for all twelve linked rooms and exterior collections, unit scale, exact A04 poses, frozen source hashes, image dependencies, per-section portal/reservation audits, and added-mesh support/connectivity broadphase. No new foreign-room or reserved-route candidates remain in the conservative layout screen. Turbine/condenser U04 centers remain within {cold['U04_centres_delta_m']:.9f} m. The screen excludes four-metre endpoint transition zones; explicit aperture checks cover named local interfaces. This is not runtime collision/navmesh certification.

Art acceptance is **not claimed**. The latest independent visual scores below are out of the visual portion's 90 points; technical scoring is separate. Some reviews precede small current-revision corrections: use each section's critic files for exact scope. Exterior finish, wear/storytelling and some labels remain below the full protocol threshold. No two stable accepted exterior rounds are claimed. Existing accepted interiors are not rescored by these outside views.

| Section | Built revision | Actual views | Latest independent visual score |
|---|---|---:|---:|
{table}

## Integration details

Original A04 `facility_master.blend` remains preserved. A05 links `EXTERIOR_<section>` collections from `exteriors/<section>/exterior-<revision>.blend` at the same unit-scale transform as its room. Keep the whole `sections/facility-assembly` folder together so relative libraries resolve.

Source practical lights with demonstrated exterior leakage are copied locally: spawn, turbine, cooling, mine and reactor emitter dimensions are reduced to fit their shells. Source shadow-disabled lights are enabled in local copies where applicable. Original source files are never rewritten. Reactor/cooling/mine wrappers retain source collection hierarchy and visibility; spawn/turbine/refinery legacy wrappers were independently checked for inherited flag changes. Reactor's hidden QA annotation transforms are not acceptance geometry; non-QA physical source geometry/transforms match at the common review frame.

No connecting corridors, stairs/lifts, facility cooling loop, terrain infill or new utility continuations were fabricated. Source-owned closed caps/doors remain, including the mine/condenser stubs and turbine return cap. Compliance exterior gate dressing still requires attachment to its corresponding moving leaf during engine import. No merge to main or engine integration is included.

## Replay

Use Blender 5.2 LTS headlessly. Set `EXTERIOR_SECTION` and a new `EXTERIOR_REVISION`, then run `blender/build_exteriors.py`; validate with `audit_exterior.py` and `audit_exterior_support.py`. Update `exteriors/CURRENT.json` only to the intended candidate. `render_exterior.py` resolves CURRENT by default; set `EXTERIOR_USE_CURRENT=0` for historical revisions. All GPU renders use the facility GPU gate, owner `astra-facility-assembly`. Render settings are Cycles HIP/HIPRT, GPU denoising, 32 samples, 1600x900; persistent render data is disabled after severe successive-frame slowdown was observed.

Run `audit_exterior_layout.py`, `integrate_exteriors.py`, and a fresh `check_exterior_master.py` before handing off another assembly. Reviews, failed intermediate revisions and original concept/source evidence remain preserved.
'''
(ROOT/'production/EXTERIOR_HANDOFF.md').write_text(doc,encoding='utf-8')
(ROOT/'production/EXTERIOR_DELIVERY_MANIFEST.json').write_text(json.dumps({'revision':'A05','sections':rows,'actual_render_count':48,'cold_integration':'PASS','art_acceptance':'NOT CLAIMED','connectors':'21 reserved, unbuilt'},indent=2))
with (ROOT/'exteriors/TASK_STATE.md').open('a',encoding='utf-8') as f:f.write('\n\n## A05 integrated exterior build — 2026-09-12\nAll twelve concept/build packages and 48 current actual renders are complete. Cold integration PASS; gaps remain unbuilt. Full art acceptance is not claimed. See ../production/EXTERIOR_HANDOFF.md and CURRENT.json for exact state.\n')
print('EXTERIOR_HANDOFF_WRITTEN',len(rows),'sections, 48 current renders')
