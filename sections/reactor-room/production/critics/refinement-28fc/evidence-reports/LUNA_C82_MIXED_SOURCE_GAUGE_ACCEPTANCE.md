# C82 mixed-source gauge acceptance

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`  
**Current source SHA-256:** `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`  
**Disposition:** Accept #16 (gauge information readability) and #30 (gauge housing depth) against C82 through explicitly mixed historical full-quality evidence. No C82 image is claimed for these two rows.

The reviewed panel sources are **C79 SHA-256 `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b`** (panels01–06 and09–16) and **C80 SHA-256 `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`** (panels07/08). These are distinct from the current C82 SHA above; each image keeps its matching original manifest and source lineage.

## Pixel review

I independently inspected all sixteen native 640×360, Cycles CPU, 96-maximum/32-minimum-sample panels. The set comprises the fourteen C79 panels listed in the manifest at `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/render_manifest.json` and C80 panels07/08 in `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/gauge-sheet/render_manifest.json`. Both manifests report identical render settings, and every used file's SHA-256 matches its manifest entry. The sixteen hashes and per-panel observations are recorded in [the panel review](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C79_GAUGE_PANELS_REVIEW.md).

For #16, every panel shows its 0/5/10 range, `bar` unit, divisions and retained pointer. Panels01 and13 have the weakest face illumination but their information remains legible at native size without zoom. I count those as marginal passes, not reasons to alter shared ink or room exposure. The set does not claim that every dial is perfectly lit.

For #30, each dial has a raised rim, retainer or casing edge that visibly separates the face from its host. Some bezels are faceted, but the requested face-to-housing depth is present across the panels. I do not infer unsupported gauge internals from these stills.

## Exact C82 lineage

The exact C79→C82 comparator at `/workspace/scratch/reactor-refinement-cycle82/cumulative-c79-scene-delta.json` passes. It records only the crane-identity font and six door-hardware `STEEL` meshes as changed, three crane nameplate/fixing objects added, and 1,910 objects unchanged; no object was removed or unexpected. Its declared comparison includes mesh arrays/material indices, object transforms and parents, material node graphs, lights, and cameras. None of the sixteen gauges, their ink/retainers, relevant materials/lights, or camera objects is changed.

The C80→C82 comparator at `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json` separately confirms that the C80 07/08 panels are outside the only changes between those source saves: the six door-hardware meshes. It passes with 1,914 unchanged objects and no added, removed, or unexpected objects. Together the two comparisons bound the mixed-source set to the exact C82 gauge state.

This is an explicit historical-image carry. The C79/C80 image files, manifests, and source hashes remain their original lineage; neither #16 nor #30 is counted as a fresh C82 render. Ten fresh C82 main views remain required for final acceptance. The overall score and all nine area scores remain unset.
