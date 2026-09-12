"""Publish acceptance notes only after the full saved-artifact gate passes."""
import json,sys,subprocess,shutil
from pathlib import Path
r=Path(__file__).resolve().parent.parent;rev=sys.argv[1];review=Path(sys.argv[2]).resolve();prefix=rev.replace('final-','')
subprocess.run([sys.executable,str(r/'production/verify_delivery.py'),rev,str(review)],check=True)
luna=json.loads(review.read_text());receipt=json.loads((r/'production/evidence/final-pass/delivery-receipt.json').read_text());cold=json.loads((r/f'production/evidence/final-pass/{prefix}-cold-comparison.json').read_text())
sha=receipt['blend_sha256'];lo=min(x['score'] for x in luna['categories']);hi=max(x['score'] for x in luna['categories'])
def put(path,text):(r/path).write_text(text.strip()+'\n',encoding='utf-8')
score_table='\n'.join('| '+x['name']+' | '+str(x['score'])+' |' for x in luna['categories'])
put('production/FINAL_ACCEPTANCE.md',f'''# Fuel Corridor final acceptance — {prefix}

**PASS: all 17 independently reviewed categories are strictly above 90 ({lo}–{hi}).** All 16 fixed views and all 12 player-eye views also exceed 90. Independent reviewer: {luna.get('reviewer','independent critic')}. Builder: Astra. These scores cover the authored corridor's integration readiness, not whole-map polish or engine runtime validation.

Saved artifact: `blender/Fuel_Corridor.blend` · SHA256 `{sha}`.
The canonical file is byte-identical to the reviewed candidate and survives fresh-process reopening. It contains {receipt["object_count"]:,} objects, 34 materials, 16 saved cameras and 3 packed images, with no linked libraries. Original scene authoring is reproducible from the section-local source.

| Category | Independent score |
|---|---:|
{score_table}

## Evidence

- Complete 16-view final pack: `renders/review/{rev}`; 1440 × 960, 32 samples, frozen camera poses.
- Complete 16-view canonical cold repeat: `renders/review/{rev}-cold`; every view separately passes max ≤2/255 and mean ≤0.02/255. Largest observed channel difference: {max(x['max_channel_difference_255'] for x in cold['rows'])}/255. Each primary and repeat image uses its own fresh Blender process; the original per-view manifests are retained with the complete aggregate manifests. PNGs are not claimed byte-identical.
- Twelve player-eye observations: `renders/review/{rev}-walkthrough`; 1200 × 800, 32 samples, eye height 1.70 m. All approaches have grounded positions and clear near-camera space.
- Fresh CPU geometry/support/routes: `evidence/final-pass/{prefix}-technical.json`.
- Factory-empty object/world-geometry replay and separate material/UV/packed-texture replay: `{prefix}-source-replay.json` and `{prefix}-material-replay.json`.
- Exact branch/handoff and 39 sampled gate positions: `{prefix}-branch-handoff.json` and `{prefix}-engineering-motion.json`. Zero-depth roller tangencies are intentional contacts; no penetrating mechanical obstruction is accepted.
- Independent final scores: `{review.relative_to(r/'production').as_posix()}`. Final hash-bound receipt: `evidence/final-pass/delivery-receipt.json`.
- Interactive image gallery: `FINAL_GALLERY.html`; dimensioned plan and exact interfaces are in `../architecture`.

## Corrections and preserved failures

F00 was rejected for a black overlapping floor patch, competing/hidden wayfinding, mounting/source mismatches, weak reactor-header contrast and insufficient door construction. F01–F04 repaired geometry and presentation but retained their failed or partial status. F05's broad visual pack passed, then its canonical C08 repeat exposed a real narrow coplanar flange/lining strip; Luna correctly revised reproducibility to 90/fail.

F06–F08 were rejected engineering candidates. F09 separates the rear steel flange from the lining by 4 mm, fits waste-sign feet to the exposed upright face, and separates the service grille and corner lamp from sign mounts. No required machinery, portal, route or fixed camera was added, removed or relocated. Exact geometry delta is retained in `F05-F09-delta.json`. The rejected images, scores and technical failures remain available; none were averaged away.

F09's complete cold pack exposed the intersecting first-aid cross bars (C07 max31/255) and four tiny beam-edge outliers (C04 max4/255). F10 replaces only the two coplanar cross bars with one continuous stamped cross; `F09-F10-delta.json` confirms no other object changed. Its paired fresh-process rendering catches each view's repeatability immediately. The invalid pre-promotion F09 attempt is explicitly excluded from all F10 evidence.

## Integration limits

Five external connections and one internal freight gate are authored. F01/F02 retain their exact local refinery/reactor mating equations; S01/S02/S03 are reserved destinations. Neighbors were not moved or rebuilt. Their closed doors, shared-world placement, destination adapters and refinery-unit/reactor-cartridge conversion remain unresolved external work. The handoff supplies authored collision sources, routes, carriages, spawn/incident markers, audio volumes and network cells. Collider cooking, navmesh, controllers, runtime physics, audio/network behavior and full facility travel timing are not certified by Blender renders.

Repository delivery is section-only on `codex/fuel-corridor-final-20260911`; the final shared status/user response supplies the verified commit and remote result.
''')
put('README.md',f'''# Fuel Corridor

Verified {prefix} delivery: **17 independent categories score {lo}–{hi}, all strictly above 90**, with 16 fixed views, a complete cold repeat and 12 player-eye views. Grounded Valorant direction uses ivory mineral panels, charcoal steel, tactile materials and orange safety markings. Reviewer: {luna.get('reviewer','independent critic')}.

- [Finished image gallery](production/FINAL_GALLERY.html)
- [Final acceptance and scores](production/FINAL_ACCEPTANCE.md)
- [Saved Blender scene](blender/Fuel_Corridor.blend)
- [Dimensioned plan](architecture/A101-plan-preview.png) and [editable SVG](architecture/A101-plan.svg)
- [Exact connection contracts](architecture/CONNECTION_CONTRACTS.md)
- [Integration handoff](architecture/INTEGRATION_HANDOFF.md)
- [Required equipment and scope](architecture/SPEC_CONTENTS.md)
- [Approved concept provenance](art/REFERENCE_PROVENANCE.md)

Canonical SHA256: `{sha}`. Original authoring is in `blender/build.py`, `valorant_details.py` and `wayfinding.py`. Use `blender/run.ps1` for a new named candidate; use the shared GPU gate for every GPU render. Preserve the verified artifact and its frozen checkpoint before further work.

This is an authored, integration-ready connector. Neighbor assembly, destination adapters, packing conversion and engine runtime systems remain explicit handoff work. No neighboring section was modified.
''')
put('production/CHECKLIST.md','''# Final asset acceptance checklist

- [x] Isolated branch; only Fuel Corridor section and assigned status owned.
- [x] Brief/specification, approved art references and current neighboring interface sources reviewed.
- [x] Dimensioned plan, equipment scope and exact five external connection contracts.
- [x] Complete freight route, gate, carrier staging, service bypass and three headers.
- [x] Strict grounded Valorant direction, no teal, independently reviewed actual pixels.
- [x] More than four actual full correction/review cycles after the full01 baseline; failed/partial candidates receive no false credit.
- [x] All 17 final categories, 16 fixed views and 12 player-eye views strictly above 90.
- [x] Geometry, physical support, maintenance/route clearances, branch approaches and typed handoff checked.
- [x] Final16 and canonical cold16 are stable, with each view independently inside the numeric thresholds.
- [x] Saved-file reopen and factory-empty source/material/UV/texture replay verified.
- [x] Scene, source, scores, render hashes and limitations bound by delivery-receipt.json.
- [x] No assembled-map, runtime-controller or continuous-physics claim.

Owned-only commit/push is reported separately in the shared status and final response after remote verification. See FINAL_ACCEPTANCE.md for the actual artifact receipt and FULL_CYCLES.md for honest review accounting.
''')
put('CONTINUE.md',f'''# Verified Fuel Corridor handoff

The authored section is verified at {prefix}; do not resume an older failed candidate. Read production/FINAL_ACCEPTANCE.md, production/evidence/final-pass/delivery-receipt.json and architecture/INTEGRATION_HANDOFF.md first.

Canonical SHA256: {sha}. Isolated branch: codex/fuel-corridor-final-20260911. Own only this section. Preserve neighboring files and live Blender windows. Any further change requires a new candidate and affected rechecks; the final evidence applies only to the exact saved artifact.
''')
put('production/TASK_STATE.md',f'''# Fuel Corridor — asset verification complete

Revision {rev}, canonical SHA256 {sha}. All 17 independent categories {lo}–{hi}; all 16 fixed and 12 player views above 90. Reviewer: {luna.get('reviewer','independent critic')}. Full 16/cold16, source replay, materials/UV/textures, geometry/support/routes and final delivery gate PASS.

Authority: FINAL_ACCEPTANCE.md and evidence/final-pass/delivery-receipt.json. Historical failures remain in FINAL_PASS.md and critics/final-pass. Branch codex/fuel-corridor-final-20260911 owns only sections/fuel-corridor. Remote delivery is verified separately in the shared status/final response; no historical process IDs are active instructions.
''')
p=r/'production/FINAL_PASS.md';p.write_text('# Historical correction journal\n\nFinal authority: [FINAL_ACCEPTANCE.md](FINAL_ACCEPTANCE.md). Pending statements below describe the state when each candidate was examined; they are superseded by the final receipt.\n\n---\n\n'+p.read_text(),encoding='utf-8')
p=r/'production/technical_audit.md';p.write_text(f'# Final technical state — {prefix} PASS\n\nSee FINAL_ACCEPTANCE.md and evidence/final-pass/delivery-receipt.json for the current verified artifact. Geometry/support/routes, source and material replay, cold16 and player-eye evidence are complete. Historical reports below retain their original failure state.\n\n---\n\n'+p.read_text(),encoding='utf-8')
p=r/'architecture/INTEGRATION_HANDOFF.md';s=p.read_text();start=s.index('Current canonical candidate');end=s.index('\n',start)
s=s[:start]+f'Final {prefix} passes all 17 independent categories above 90; the exact saved-artifact receipt is production/evidence/final-pass/delivery-receipt.json. See production/FINAL_ACCEPTANCE.md for scores, cold stability and scope.'+s[end:];p.write_text(s,encoding='utf-8')
put('production/FULL_CYCLES.md','''# Full-scene correction and stability ledger

Current authority requires every relevant category strictly above 90, independently reviewed. Engineering-only builds, preview subsets and interrupted renders are never counted as completed full cycles.

| Revision | Actual evidence/result | Credit after baseline |
|---|---|---|
| full01 | Complete original baseline; rejected sparse detail, mounting, gate/pipe conflicts and seams | Baseline only |
| full02 | Complete10+6 views; rejected flow/art/hierarchy/light/story and construction failures | Cycle1 |
| full03 | Complete10+6 views; rejected art/equipment/story; D05 black near-camera obstruction | Cycle2 |
| interrupted full04 | Partial inherited images | None |
| final-F00-inherited | Fresh full16 of saved eng12/walk02 corrections; Luna rejected floor overlap, hierarchy, support and source mismatch | Cycle3 |
| final-F01/F02 | CPU candidates; F01 rejected, F02 PASS | None |
| final-F03 | Two images then stopped for known corrections; explicit PARTIAL | None |
| final-F04 | Eight targeted previews; reactor-header contrast rejected | None |
| final-F05 | Full16; broad visual scores above90, but canonical C08 numeric failure revised reproducibility to90/fail | Cycle4; not final acceptance |
| final-F05-cold | Full16 repeat exposed real coincident flange/lining faces | Failed stability check; no new correction credit |
| final-F06 | CPU support FAIL; owned renderer stopped; PARTIAL retained | None |
| final-F07/F08 | CPU support failures retained; no full renders claimed | None |
| final-F09 | Corrected full16, independent visual review, source and geometry PASS; final cold condition failed | Cycle5 |
| final-F09-cold | Full16; C07 first-aid cross overlap and C04 four-pixel beam-edge exception exceed strict numeric threshold | Failed stability; no new correction credit |
| final-F10 | Single-piece first-aid cross; full16, independently above90, source and geometry PASS | Cycle6 |
| final-F10-cold | Full16 fresh-process pairs, each numeric threshold passes; independent stable approval | Stability verification, no invented correction revision |
| final-F10-walkthrough | Twelve1.70m player-eye approaches, independently above90 | Supplementary navigation evidence |

The final two complete visual passes are F10 and its canonical cold repeat. They establish stability of the same corrected artifact, not two fictional geometry revisions. All rejected technical and visual reports remain in their original evidence folders. The invalid pre-promotion image is excluded; aggregation requires sixteen real hash-bound per-view manifests in each pack.
''')
print('Final documents reconciled from passed evidence; no pending asset approval claims.')
