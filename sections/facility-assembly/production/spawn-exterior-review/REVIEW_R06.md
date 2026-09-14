# Spawn exterior + rescue courtyard R06 independent review

Revision: `R06`  
Build hash: `c5cc6171f8f1b2b62609e0438d712749fe3d68c67fe15f84fde39acb75d3cb6b`  
Views inspected: `renders-R06/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** R06 improves the south exposure and reduces the earlier black crush. The four views show the approved olive/ivory/orange identity, corrected support contacts, fresh cold-load/dependency evidence, and a more readable entry. The scene still fails the strict `>93` rule: the top view remains washed out, the background terrain is still a crude faceted band, the central paving/roof masses are under-articulated, and R06 has no current route audit. R04 route evidence is historical and is not claimed for R06.

## Category scores

| # | Category | Result | Evidence / blocker |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **82/100 — REJECT** | Approved palette, orange arrival identity, service fixtures, benches and planted margins are visible. The target’s warm stylized environmental hierarchy is only partly realized; top exposure and faceted background remain off-target. |
| 2 | Silhouette and massing | **84/100 — REJECT** | Spawn shell, stepped roofs, entry and courtyard masses read consistently. The broad shell remains rectangular and the background terrain’s repeating triangular facets dominate the skyline. |
| 3 | Scale and spatial layout | **85/100 — REJECT** | Doors, planters, benches, rail, HVAC, service objects and courtyard footprint read at believable scale; fixed camera/footprint consistency is strong. Detailed layout dimensions remain outside the supplied pixel evidence. |
| 4 | Circulation, access, and rescue route | **UNVERIFIED** | R06 pixels show an open central courtyard and readable entry approach, but no R06 route audit exists. The zero-finding R04 route audit is historical and cannot certify this revision. |
| 5 | Construction and load/support logic | **86/100 — REJECT** | R06 targeted ground contacts and wall anchors pass in `TECHNICAL_R06.json`; delivery inventory supplies bounds/materials/visibility. The technical report remains scoped and is not blanket certification of every retained source object. |
| 6 | Utility and service continuity | **85/100 — REJECT** | South/east service cabinet, hose, pipe runs and wall returns remain visible and supported; fresh object inventory exists. Full semantic endpoints and route interaction are not established for every retained utility. |
| 7 | Exterior materials and surface response | **76/100 — REJECT** | Olive metal, ivory walls, graphite trims, orange accents, timber and paving separate. Large roof/paving/ground fields remain nearly uniform; top exposure flattens material boundaries and foreground grass/rock still reads procedural. |
| 8 | Lighting, palette, and readability | **68/100 — REJECT** | South is materially more readable and courtyard contact shadows are present. `04_TOP` remains overexposed, the distant band is low-contrast, and the overall fill is still cool/flat relative to Concept02’s warm sun and shaped shade. |
| 9 | Environmental storytelling and human use | **81/100 — REJECT** | Cabinet, hose, pipe/rack, benches, planters, pergolas and entry signs explain active campus use. Service and roof surfaces still have quiet spans, with repeated thin bed foliage and limited localized wear. |
| 10 | Terrain, drainage, and ground transitions | **UNVERIFIED** | Ground-contact checks pass for targeted new beds/rack and drains are visible, but no R06 grade/threshold/drain-transition probe or route audit is supplied. Background faceting is a presentation defect, not proof of a spawn slab transition failure. |
| 11 | Roof and elevated detail | **80/100 — REJECT** | Roof units, coping, seams and stepped heights read across the four views. Top view washes out roof value groups; elevated surfaces have sparse service/drain variation and broad blank planes. |
| 12 | View-to-view consistency | **80/100 — REJECT** | Fixed views retain the same footprint, additions, open courtyard and palette. South/courtyard readability is stronger than top, and the faceted background changes prominence by angle. |
| 13 | Interface and reservation integrity | **86/100 — REJECT** | `DELIVERY_R06.json` reports zero named reservation intersections; source/dependency inventory is present. This is strong scoped evidence, but it does not replace a full portal/aperture/reservation audit for every interface. |
| 14 | Runtime and delivery readiness | **UNVERIFIED** | Blender cold load is recorded at 52.04 seconds, all listed libraries exist, and new-object materials/bounds/visibility are inventoried. No assembly performance benchmark or Unity runtime evidence is supplied. |
| 15 | Art-direction veto and professional finish | **68/100 — REJECT** | No toy-scale or generic-low-poly veto dominates the spawn shell. The washed top view, faceted background, repeated thin grass rows, cool fill and broad under-authored surfaces keep the iteration below professional finish. |

## Concrete pixel blockers

1. Reduce `04_TOP` exposure or rebalance the top-view lighting so paving, roofs, planted margins, route edges and olive/ivory blocks retain readable value grouping.
2. Replace the visible faceted background band with the approved quiet sky/haze or a controlled broad-plane treatment while preserving the neighboring silhouette and placement.
3. Warm and shape the directional fill so the scene matches Concept02’s sun/shade hierarchy without returning to R04’s south black crush.
4. Replace repeated thin grass rows with broader authored plant clusters and varied spacing while preserving bed positions and all route clearances.
5. Add selective roof/paving wear and material variation at the existing focal zones; avoid adding undirected clutter or changing the fixed footprint.

Technical note: R06 support/contact, cold-load, dependency, bounds/material, visibility, source-hash, and named-reservation evidence is fresh. Route and grade-transition claims remain unverified until R06-matched audits arrive. Unity readiness remains separate and unverified.
