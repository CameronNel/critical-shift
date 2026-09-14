# R04 bounded fixes for categories 2, 3, 4, 5, 6, and 10

This is a corrective-action list for the R04 deductions. It does not change the rubric threshold, approve R06, authorize interior edits, or authorize a footprint/doorway/camera change. Each action must be rechecked in the same four locked views and the applicable technical report.

## Category 2 — silhouette and massing

**Observed defect — `01_COURTYARD`, `02_SOUTH`, `03_EAST`, upper background:** the large background rock/horizon is a dominant angular silhouette made of coarse triangular planes. It reads as unfinished environment geometry and competes with the spawn roofline. This is a visible presentation defect, although the rock is neighboring context rather than spawn shell geometry.

**Bounded correction:** preserve the existing rock silhouette and neighboring placement, but replace the crude visible background treatment with the approved quiet sky/haze or an authored broad-plane treatment that keeps the same silhouette. Do not add buildings, change the spawn roof heights, or redraw the mine geometry under the spawn task.

**Evidence gap:** no spawn-shell silhouette defect remains proven beyond the background competition. Recheck roof/entry/olive-wing silhouette in all four R06 views after the background correction.

## Category 3 — scale and spatial layout

**Observed defect — `02_SOUTH`, lower third:** the foreground guardrail spans the full image and compresses the perceived entry apron, door, and wall-service scale. The door and fixtures remain plausibly scaled; this is a readability/composition deduction, not evidence of wrong dimensions.

**Bounded correction:** keep the guardrail footprint and route reservation, but verify its height and camera-side relationship against the fixed layout. If it is additive, lower or locally step the rail only within the existing reserved edge so the entry threshold and service fixtures remain visible from the locked camera. Do not widen/move the door or shift the camera. Attach a dimension/transform check showing door, rail, bench, planter, and cabinet relationships.

**Evidence gap:** R04 placement evidence covers section transforms, not every prop dimension. Add an evaluated scale/clearance table for the entry apron and courtyard furniture in R06.

## Category 4 — circulation, access, and rescue route

**Observed defect — `02_SOUTH`, lower edge:** the rail visually masks the approach and threshold. `01_COURTYARD` and `04_TOP` show the central courtyard remains open; no route obstruction is established by the zero-finding R04 route audit.

**Bounded correction:** preserve the route centerline, doorway width, courtyard opening, and rail reservation. Adjust only additive edge dressing/rail height or local spacing if the fixed route audit confirms the same width and threshold clearances. Re-run the R04 route sample set on R06, including `SPAWN_INNER_TRANSITION`, R10, and R22, and add a locked-camera route overlay proving the entry approach is visually legible.

**Evidence gap:** route samples prove no findings in R04 but do not certify Unity collision/navmesh or player/controller traversal. Keep those statuses separate and unverified.

## Category 5 — construction and load/support logic

**Observed defect:** no unresolved R04 support gap is visible in the four renders after the rack/bed correction. The technical report's targeted contacts and anchors pass.

**Evidence gap:** `TECHNICAL_R04.json` explicitly scopes itself to new bed/rack bases, wall anchors/returns, and targeted intersections; it is not blanket certification of retained source geometry, roof equipment, light poles, benches, or pergolas.

**Bounded correction/evidence action:** do not add geometry merely to create apparent support. Run an evaluated support/contact audit for every R06 exterior-added object visible in the locked views, with object name, supporting surface, signed gap/penetration, tolerance, and pass/fail. Include roof HVAC feet, coping/roof service additions, lamps, benches, pergola posts, cabinets, pipe/rack, hose, and planted beds. Any actual exception gets a local support fix that preserves the footprint and route.

## Category 6 — utility and service continuity

**Observed defect — `03_EAST`, lower-left service wall:** cabinet, low pipe run, hose/rack and planted edge read as a cluster, but the run terminus and destination are not visually obvious at gameplay distance. This is a continuity/readability deduction, not proof of detachment; R04 targeted wall returns pass.

**Bounded correction:** retain the cabinet and pipe positions and the corrected south downpipe clearance. Add only a visibly grounded terminal detail at the existing run ends (for example, a compact gland/isolator or capped maintenance endpoint) and ensure both ends terminate into an existing wall/service surface. Do not extend utilities into uncontracted corridors or fabricate a facility-wide loop. Re-run endpoint, wall-return, and clearance checks for the south and east runs.

**Evidence gap:** R04 proves targeted returns, not semantic destination or every retained utility. Supply an endpoint ledger with start/end object, supporting surface, clearance, and purpose for each visible new run.

## Category 10 — terrain, drainage, and ground transitions

**Observed defect — `01_COURTYARD`, `03_EAST`, `04_TOP`: paving and linear drains are visible and mostly coherent; no specific spawn slab float or route gap is proven by pixels. The crude faceted rock is a background silhouette issue under category 2, not evidence of a spawn ground-transition failure.

**Evidence gap:** R04 support contacts do not prove grade continuity, drain fall, threshold height, or terrain cutout transitions. The top view's bright exposure also hides small level changes.

**Bounded correction/evidence action:** preserve existing paving footprint, route widths, drains, and courtyard opening. Run downward/upward transition probes at the spawn entry, courtyard apron, service apron, drain crossings, planter edges, pergola edges, and the rescue-courtyard connection. Report maximum step, gap/overlap, drain continuity, and route clearance. Apply only local additive edging/transition correction where a probe fails; do not fill reserved future connector space or alter the fixed plan.

## R06 verification minimum

R06 can only improve these categories when the same fixed cameras show: a readable spawn silhouette against a corrected background, entry/rail scale and access legibility, unchanged open rescue circulation, complete evaluated support coverage, explicit utility endpoints, and measured ground/threshold/drain transitions. Technical evidence must be revision-matched to R06; R04 pass reports cannot be silently reused as R06 proof.
