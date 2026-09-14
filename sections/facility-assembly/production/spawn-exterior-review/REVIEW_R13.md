# Spawn exterior + rescue courtyard R13 independent review

Revision: `R13`  
Build hash: `6ca5d8d890d102a5d06e3def09dd1a0a1a33fd76d43219e11704793cbce1019c`  
Views inspected: `renders-R13/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** R13 keeps the fixed geometry and improves rock face definition through normals-only shading. Fresh R13 technical, delivery, route, and offline render-benchmark evidence supports the corresponding assembly claims. Source/reservation and route requirements pass their stated checks; they are not discounted for the scene’s remaining art issues. Visual acceptance still fails the strict `>93` rule because the rock shading reads as banded clay rather than sculpted painted stone, `04_TOP` is washed out, large roof/paving fields are quiet, and repeated planting/rail patterns remain visible.

## Category scores

| # | Category | Result | Specific deduction/evidence |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **88/100 — REJECT** | Approved palette and footprint are retained, but rock treatment, top-view exposure, and sparse wear do not yet match Concept02’s painted directional treatment. |
| 2 | Silhouette and massing | **88/100 — REJECT** | Spawn mass and stepped roofs read consistently. No unresolved spawn silhouette/placement defect is proven; the visible rock keeps a coarse banded shading read that weakens the context silhouette. |
| 3 | Scale and spatial layout | **92/100 — REJECT** | Fixed camera/footprint, doors, benches, beds, service fixtures and roof equipment remain coherent. Remaining deduction is limited to gameplay readability in `02_SOUTH` where the foreground rail crowds the entry approach; no wrong dimension is inferred. |
| 4 | Circulation, access, and rescue route | **95/100 — PASS (scoped)** | R13 route audit reports zero findings, floor/support samples, and max adjacent floor change 0.015 m; `04_TOP` shows the central courtyard open. This does not claim Unity traversal/collision/navmesh. |
| 5 | Construction and load/support logic | **94/100 — PASS (scoped)** | R13 expanded targeted contacts pass, including roof membrane fields and prior bed/rack/wall fixtures. Remaining scope limitation is explicit: retained source objects are not blanket-certified. |
| 6 | Utility and service continuity | **94/100 — PASS (scoped)** | Fresh targeted wall anchors/returns pass and south/east fixtures remain visibly coherent. Full semantic continuity of every retained facility utility is outside the report scope. |
| 7 | Exterior materials and surface response | **86/100 — REJECT** | Olive/ivory/graphite/orange/timber families separate. Rock has visibly banded clay-like response; roof, paving and wall fields remain smooth with sparse authored wear. |
| 8 | Lighting, palette, and readability | **84/100 — REJECT** | Exterior views have readable warm/cool shading and the approved palette. `04_TOP` still washes out roof/paving/route values, reducing material and circulation readability. |
| 9 | Environmental storytelling and human use | **88/100 — REJECT** | Entry identity, benches, beds, service cabinet, hose, rack and utilities communicate a maintained campus. Repeated planting rhythm and large quiet wall/roof spans keep the setting below authored finish. |
| 10 | Terrain, drainage, and ground transitions | **94/100 — PASS (scoped)** | R13 route audit includes actual floor/support samples, zero findings, and 0.015 m maximum adjacent sample change; targeted contacts pass. This does not claim Unity navigation. |
| 11 | Roof and elevated detail | **89/100 — REJECT** | Membranes, coping, seams and HVAC read coherently. Roof surfaces remain broad and low-information in `SOUTH`/`EAST`; top exposure suppresses detail. |
| 12 | View-to-view consistency | **89/100 — REJECT** | Fixed camera/geometry/material language is stable across all four views. Top exposure and rock shading vary in impact, and repeated beds/rails are obvious from `TOP`. |
| 13 | Interface and reservation integrity | **95/100 — PASS (scoped)** | DELIVERY_R13 reports unchanged source/dependencies and zero named reservation intersections; route audit is clean. Existing apertures/traversal behavior remains outside this named-reservation check. |
| 14 | Runtime and delivery readiness | **95/100 — PASS (offline assembly scope)** | R13 cold load, dependencies, source hash, visibility/material/bounds inventory, and four-frame native render timing/stability are documented. Benchmark is offline only; interactive FPS and Unity remain unmeasured/unverified. |
| 15 | Art-direction veto and professional finish | **78/100 — REJECT** | No generic toy-scale veto dominates the spawn shell. Banded clay rock, washed top view, quiet roof/paving fields and repeated planting prevent professional finish. |

## Strongest remaining pixel blockers

1. Replace the normals-only rock result with face shading that reveals broad directional planes without horizontal banding or clay-like softness; preserve source vertices/topology and neighboring silhouette.
2. Rebalance `04_TOP` exposure/value grouping so roof membranes, paving, olive fields, beds, drains and rescue-route edges remain distinct.
3. Add controlled broad wear/value variation to existing roof, ivory wall and paving materials; keep the footprint, route, and detail density unchanged.
4. Break the repeated narrow bed planting into authored clusters with varied height/density while preserving all approved bed positions and clearances.
5. Keep `02_SOUTH` entry/route legible around the fixed foreground rail after lighting changes; do not move the doorway or camera.

R13 route, reservation, source, support, dependency, and offline assembly checks pass within their explicit scopes. Unity runtime and interactive FPS remain separate and unverified. No final acceptance is implied.
