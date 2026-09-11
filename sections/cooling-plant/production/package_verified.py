"""Package only independently approved, measured, cold-verified scene evidence."""
from pathlib import Path
import json,hashlib,shutil,sys,html

r=Path(__file__).resolve().parents[1];rev=sys.argv[1]
read=lambda p:json.loads((r/p).read_text(encoding='utf-8'))
write=lambda p,s:(r/p).write_text(s.strip()+'\n',encoding='utf-8')
audit=read(f'production/technical/{rev}-validation.json')
walk=read(f'production/technical/{rev}-walkthrough.json')
cold=read(f'production/technical/{rev}-cold-survival.json')
review=read(f'production/critics/luna-{rev}-scores.json')
manifest=read(f'production/renders/review/{rev}/render_manifest.json')
assert audit['objective_status']=='PASS' and audit['failure_count']==0
assert walk['status']=='PASS' and len(walk['routes'])==8
assert cold['status']=='PASS' and cold['artifact_unchanged']
assert review['approved'] and len(review['scores'])==8 and min(review['scores'].values())>=90
assert len(manifest['cameras'])==18 and manifest['revision']==rev
scene=r/'blender/cooling_plant.blend'
assert hashlib.sha256(scene.read_bytes()).hexdigest()==cold['blend_sha256']==audit['checks']['source']['blend_sha256']
dest=r/'production/renders/final';dest.mkdir(exist_ok=True)
for c in sorted(manifest['cameras'],key=lambda item:item['camera']):
    source=r/f'production/renders/review/{rev}'/(c['camera']+'.png')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==c['sha256']
    shutil.copy2(source,dest/source.name)
shutil.copy2(r/f'production/renders/review/{rev}/render_manifest.json',dest/'render_manifest.json')
checkpoint=r/f'production/checkpoints/{rev}';checkpoint.mkdir(parents=True,exist_ok=True)
for name in ('build_scene.py','kit.py','develop_room.py','cooling_plant.blend'):
    shutil.copy2(r/'blender'/name,checkpoint/name)
shutil.copy2(r/'interface.json',checkpoint/'interface.json')
write('production/renders/final/README.md',f'''# Verified {rev} images

Ten fixed cameras C01–C10 and eight supplementary W01–W08 views, all1440×960 at48samples. Exact copies of the independently reviewed {rev} batch; SHA256 values are in render_manifest.json. Ten primary cameras were rendered again after a fresh saved-file open and compared numerically and independently inspected; tiny numerical differences are retained honestly. See ../../technical/{rev}-cold-survival.md and ../../critics/luna-{rev}-full-review.md.

The neutral gray reactor boundary is intentionally unassembled. Images do not imply a built remote corridor or runtime gameplay verification.
''')
cards=[]
for c in sorted(manifest['cameras'],key=lambda item:item['camera']):
    n=c['camera'];cards.append(f'<figure><a href="{n}.png"><img loading="lazy" src="{n}.png" alt="{html.escape(n)}"></a><figcaption>{html.escape(n.replace("_"," "))}</figcaption></figure>')
write('production/renders/final/gallery.html','<!doctype html><meta charset="utf-8"><title>Critical Shift — Cooling Plant</title><style>body{margin:36px;background:#202020;color:#eee;font:16px system-ui}h1{color:#d5905b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:22px}figure{margin:0}img{width:100%;border-radius:4px}figcaption{padding:8px 0}a{color:inherit}</style><h1>Cooling Plant · '+rev+'</h1><p>Ten fixed views and eight player-height views. Click an image for full resolution. Local section only; reactor boundary and remote utility connections remain unassembled.</p><main>'+''.join(cards)+'</main>')
score_table='\n'.join(f'| {k} | {v} |' for k,v in review['scores'].items())
write('production/FINAL_HANDOFF.md',f'''# Cooling Plant — verified local integration package {rev}

Complete original Blender room:11×13m clear footprint,5.8m ceiling plane, paired pump trains, heat exchanger, extraction hoist, maintenance workshop, reserve restart, backup-water services, drains, lighting and navigation. Ivory/charcoal/oxide-orange/yellow Valorant direction; no teal. All machinery, supports and procedural materials are authored from scratch.

## Review and saved-file evidence

Independent Luna actual-pixel review: all eight categories meet90. Full report: [Luna {rev}](critics/luna-{rev}-full-review.md).

| Category | Score /100 |
|---|---:|
{score_table}

Saved-scene evaluated geometry audit: PASS, zero failures/review items, matching source hash. Eight conservative player/cart sweeps: PASS, zero collision samples. Ten primary cameras rendered again in a fresh Blender process: unchanged saved artifact and independently verified visual stability; tiny numerical differences remain, so bit-exact output is not claimed. Materials, geometry, native text, cameras and interfaces survive reopening; no missing linked/external textures are required. Evidence: [geometry](technical/{rev}-validation.json), [routes](technical/{rev}-walkthrough.json), [cold-start comparison](technical/{rev}-cold-survival.md).

Saved Blender SHA256: `{cold['blend_sha256']}`. Reproducible source SHA256: `{manifest['source_sha256']}`. Exact source/scene checkpoint: checkpoints/{rev}/.

Live Blender inspection is recorded in technical/{rev}-live-inspection.json and its viewport screenshot. The dependency tool reports Blender's native Bfont `<builtin>` sentinel as a missing literal filesystem path; the raw flag is retained, while the native text is visibly verified in fresh-process renders. This is not an external font file. The live scene was not resaved, and its control lease was released.

## Inspection and assembly

Open ../blender/cooling_plant.blend. All10 C cameras and8 W cameras are saved. [Image gallery](renders/final/gallery.html) and [dimensioned plan](../architecture/floorplan.png) provide review coverage. [Requirements](REQUIREMENTS.md), [concept provenance](../art/concepts/PROVENANCE.md), [correction history](CORRECTION_HISTORY.md) and [camera transforms](CAMERAS.md) retain the full evidence chain.

Local origin is CP-P01 at(0,0,0),+Y inward,+Z up, metres. Main opening5×5m; internal CP-D02 at(-4.1,9.9,0),1.2×2.2m. Permanent center lane2.2m; exchanger withdrawal2.6×3.5m; bench standing strip0.9m. Full machine/service envelopes, normals, elevations and eight utility socket coordinates are in [interface.json](../interface.json) and [connection contracts](../architecture/CONNECTIONS.md). Do not scale the scene.

Proposed Cooling→reactor placement is Rz(-135°), translation(11.0162950904,-11.0162950904,0), at the OUTER end of the existing reactor-owned3.7m stub. This transform is documented, not applied. Topology is refinery→Fuel Corridor→reactor→Cooling. No neighbouring section was moved, rebuilt or imported.

## Remaining integration uncertainties

The reactor's existing static closed cooling door blocks assembled traversal; its owner/integrator must resolve it. Remote coolant/secondary-water, reserve-power and drainage endpoints remain unassigned. Fuel Corridor S01_PLANT is a reserved header, not an installed Cooling link. Reconcile final global module placement and turbine fit when assembling the facility. Read-only neighbour measurements preserve before/after hashes; recheck contracts if neighbours change.

This is integration-ready Blender scenery and interface evidence, not final whole-map polish, pressure-vessel certification, game-engine collision or interaction validation. Pumps, valve hold, repair, reserve sharing, battery/water attachment and hydraulic values still need host-authoritative gameplay integration. The conservative saved-scene route sweeps do not replace engine physics.

Commit/push receipt and live inspection evidence are recorded separately after packaging. No merge to main is authorized by this package.
''')
write('README.md',f'''# Cooling Plant

Complete verified local Blender support room for Critical Shift, revision **{rev}**. Paired pumps, exchanger and hoist, maintenance workshop, reserve restart, backup water, drains, lighting and routes. Valorant direction in ivory, charcoal, oxide orange and yellow; no teal.

Independent Luna review: all eight categories90+. Saved geometry and all eight conservative routes pass. Ten fixed-camera cold-start renders preserve the scene and pass independent visual-stability review; small numerical differences are documented. This certifies the local artifact; the facility remains unassembled.

- [Saved scene](blender/cooling_plant.blend)
- [Final handoff and scores](production/FINAL_HANDOFF.md)
- [18-view image gallery](production/renders/final/gallery.html)
- [Dimensioned plan](architecture/floorplan.png)
- [Exact connections and ownership](architecture/CONNECTIONS.md)
- [Equipment checklist](production/REQUIREMENTS.md)
- [Approved concepts and rejected history](art/concepts/PROVENANCE.md)

Other sections were preserved. The reactor's closed door, remote utilities and global placement require assembly work by their owners/integrator.
''')
write('production/CHECKLIST.md',f'''# {rev} delivery checklist

- [x] Dimensioned architecture and exact measured neighbour/interface contracts
- [x] Complete original room, all required machinery/functions represented
- [x] Approved no-teal Valorant concepts and honest rejected history
- [x] Detailed couplings, casings, flanges, guards, supports and service connections
- [x] Traceable local coolant, secondary water, reserve service and drains
- [x] Ten fixed and eight supplementary actual rendered views
- [x] Independent Luna score90+ in every category, no averaging
- [x] Saved-scene evaluated geometry/support/clearance/dependency checks
- [x] Eight conservative player/cart route sweeps
- [x] Fresh-process cold-open, honest ten-camera numerical comparison and independent visual-stability review
- [x] Verified source/scene checkpoint and integration handoff
- [ ] Separate live Blender inspection receipt
- [ ] Section-only commit/push receipt

The last two delivery actions are recorded after packaging. Historical slice/fixed-cycle rules were superseded by the user's full-room integration-readiness workflow. Whole-map and engine validation are explicitly not claimed.
''')
write('CONTINUE.md',f'''# Cooling Plant — verified local package {rev}

Read production/FINAL_HANDOFF.md and production/DELIVERY_RECEIPT.md (once written) for current acceptance and commit/push state. This supersedes September8 paused slice instructions. Preserve historical failures and rejected images.

Own only sections/cooling-plant and assigned original-checkout status/cooling-plant.md. Use the shared GPU gate for GPU renders and private resources for background work. Do not edit or claim another worker's Blender. Further geometry changes invalidate current final render/review/cold evidence until reverified.

Latest user palette forbids teal. Approved concepts are R05 overall, R06 machinery/prop panels1–5 and R07 interior reverse composition. Luna is the independent reviewer. No fixed number of cosmetic cycles is required. Neighbour doors/utilities and global assembly remain unresolved as documented.
''')
write('production/TASK_STATE.md',f'# {rev} verified local artifact\n\nAll eight independent categories90+, geometry and route audits PASS, ten-camera saved-artifact cold survival PASS; small numerical differences retained. See FINAL_HANDOFF.md; live inspection and commit/push receipt are the remaining delivery actions until DELIVERY_RECEIPT.md is written.')
print('VERIFIED_PACKAGE_READY',rev,cold['blend_sha256'])
