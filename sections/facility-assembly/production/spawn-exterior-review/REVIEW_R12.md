# Spawn exterior + rescue courtyard R12 independent review

Revision: `R12`  
Build hash: `215a425377c54d325e8bb8b224e51e172d916b5db8623b09a68c2a4481218bd3`  
Views inspected: `renders-R12/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** R12 has complete four-view pixels and materially stronger offline evidence. Roof membrane fields, broad bed foliage, warm paving, softened fill, contacts, route samples, dependencies, reservations, and render stability are all represented. The scene still misses the strict `>93` threshold: the rock/background now reads clay-like and over-soft, the top view remains overexposed, the spawn shell and roof fields are broad/quiet, and planting repetition persists. The material preview artifact is separate and receives no R12 score credit. The render benchmark proves offline native-render timing/stability only; it does not prove interactive FPS or Unity readiness.

## Category scores

| # | Category | Result | Evidence / blocker |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **88/100 — REJECT** | Olive/ivory/orange palette, warm timber, roof membranes, service dressing and planted margins track Concept02. The softened clay-like rock, washed top, sparse wear and repeated planting rhythm remain visibly off-target. |
| 2 | Silhouette and massing | **87/100 — REJECT** | Stepped shell, roof units, entry and courtyard edges remain readable in all views. The spawn is still mostly broad rectangular masses, while the rock silhouette has lost directional planar definition. |
| 3 | Scale and spatial layout | **89/100 — REJECT** | Four locked views and R12 placement/source records keep doors, benches, HVAC, planters, service fixtures, roof fields and open courtyard coherent. No pixel defect indicates a wrong footprint; detailed dimensions remain limited to report coverage. |
| 4 | Circulation, access, and rescue route | **89/100 — REJECT** | R12 route samples include floor heights/support objects, zero findings, and a maximum adjacent floor change of 0.015000 m; top view keeps the centre open. South rail still competes with entry approach at gameplay scale; Unity traversal remains outside this evidence. |
| 5 | Construction and load/support logic | **89/100 — REJECT** | Expanded R12 contacts cover the new roof membrane fields and prior rack/bed/wall fixtures; targeted checks pass. The report still disclaims blanket certification of every retained source object and does not make Unity collision claims. |
| 6 | Utility and service continuity | **88/100 — REJECT** | South/east cabinet, hose, pipe runs, roof equipment and supports remain visible; R12 delivery/material inventory is fresh. Semantic continuity of every retained utility beyond the audited additions is not proven. |
| 7 | Exterior materials and surface response | **84/100 — REJECT** | Warm ivory, olive metal, graphite trims, orange accents, timber, paving and planting separate well. Roof/paving fields remain smooth and low-frequency; rock shading is clay-like rather than the approved sculpted painted planes. |
| 8 | Lighting, palette, and readability | **82/100 — REJECT** | Fill is warmer and contact shadows are clearer in exterior views. `04_TOP` is still washed out, broad roof/paving values compress, and the background does not establish a convincing atmospheric hierarchy. |
| 9 | Environmental storytelling and human use | **86/100 — REJECT** | Entry signs, benches, planters, service cabinet, hose/rack and utility runs communicate active maintenance and rescue-campus use. Large quiet walls/roofs and repeated plant groupings still reduce authored specificity. |
| 10 | Terrain, drainage, and ground transitions | **89/100 — REJECT** | R12 route audit has actual floor/support samples, zero findings and max adjacent floor change 0.015 m; targeted contacts pass. Bright top view hides small paving/threshold distinctions, and no Unity navigation evidence is implied. |
| 11 | Roof and elevated detail | **86/100 — REJECT** | Added membrane fields improve roof continuity and HVAC/coping forms remain coherent. Roof planes still read as large quiet slabs in `SOUTH`, `EAST`, and `TOP`; drainage/service detail is sparse at review distance. |
| 12 | View-to-view consistency | **87/100 — REJECT** | Same locked cameras, footprint, roof fields, planting, service dressing and palette persist across all four images. Top exposure and clay-like background vary in impact by view, while repeated bed layouts remain obvious in top view. |
| 13 | Interface and reservation integrity | **90/100 — REJECT** | R12 delivery reports unchanged source/dependencies and zero named reservation intersections; route audit is clean. This supports the scoped interface claim, but does not certify every portal/aperture or future connector behavior. |
| 14 | Runtime and delivery readiness | **90/100 — REJECT** | Blender cold load, dependency existence, visibility/material/bounds inventory, source hash and four-frame native-render timing/stability are documented. The benchmark explicitly excludes viewport FPS and Unity; interactive collision/navmesh/controller/performance remain unverified. |
| 15 | Art-direction veto and professional finish | **75/100 — REJECT** | The spawn shell avoids toy scale and obvious bevel-box construction. Clay-like background rock, washed top, broad low-information surfaces, repeated planting, and still-muted wear prevent professional finish. |

## Strongest remaining pixel blockers

1. Rework only the visible rock/background face shading in the fixed views so the existing silhouette reads as broad directional planes with controlled painterly variation rather than soft clay; preserve source vertices/topology and neighboring placement.
2. Correct `04_TOP` exposure/value grouping so roof membranes, warm paving, olive fields, plant beds, drains and rescue-route edges remain distinct.
3. Add selective broad value/wear variation to roof membranes, ivory wall fields and courtyard paving at the existing focal zones; avoid noisy microdetail or footprint changes.
4. Break repeated bed strips and bench-adjacent planting into authored cluster patterns with varied height/density while preserving all bed positions and route clearances.
5. Maintain south entry legibility around the fixed foreground rail after lighting changes; the sign, door recess, service cabinet, hose and approach should remain readable together.

R12 technical and delivery artifacts support scoped offline Blender assembly readiness. The native render benchmark is not an interactive FPS result, and Unity readiness remains separate and unverified. No final acceptance is implied.
