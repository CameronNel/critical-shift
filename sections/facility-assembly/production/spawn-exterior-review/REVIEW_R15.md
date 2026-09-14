# Spawn exterior + rescue courtyard R15 independent review

Revision: `R15`  
Build hash: `72c71cb39a04243e9e514a6766177e7e15e78434f0c2793ad77ec0a7c2e0b3a8`  
Views inspected: `renders-R15/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** R15 has complete native pixels and strong revision-matched offline evidence. Source geometry/boundary preservation, contacts, anchors/returns, dependencies, reservations, route samples, and four-frame render stability are documented. The strict `>93` gate remains unmet by multiple visual categories: large roof/wall/paving fields are still quiet, vegetation/bench repetition remains obvious, the foreground rail crowds the south view, and the rock/background remains a visibly faceted contextual treatment. The benchmark establishes offline assembly rendering only; no Unity or interactive-FPS claim is made.

## Category scores

| # | Category | Result | Specific deduction/evidence |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **89/100 — REJECT** | Approved palette, footprint, service dressing and warm timber remain. Rock is more planar but still visibly faceted and unlike Concept02’s painted directional surface; broad quiet fields and sparse wear remain. |
| 2 | Silhouette and massing | **90/100 — REJECT** | Spawn stepped mass, entry, roofs and courtyard edges read consistently. Remaining deduction is the coarse faceted background silhouette and low-information rectangular shell fields, not a footprint or doorway error. |
| 3 | Scale and spatial layout | **92/100 — REJECT** | BUILD_R15 reports 2,444 protected boundary/lower-interface vertices unchanged with 0 m error; doors, benches, beds, HVAC and route layout are coherent. The fixed south rail crowds the entry read in `02_SOUTH`; no dimension defect is inferred. |
| 4 | Circulation, access, and rescue route | **95/100 — PASS (scoped)** | R15 route audit has zero findings, actual floor/support samples, and max adjacent sample floor change 0.015 m; `04_TOP` shows open central circulation. This does not claim Unity traversal, collision, navmesh, or controller behavior. |
| 5 | Construction and load/support logic | **95/100 — PASS (scoped)** | Fresh R15 report passes 67 roof/base contacts plus anchors/returns and preserves source hashes. BUILD_R15 also records supported hose axle/back-flange connection and exact protected-boundary preservation. Report scope remains targeted, not blanket certification of every retained source object. |
| 6 | Utility and service continuity | **94/100 — PASS (scoped)** | Hose is now connected through a supported axle/back flange; fresh anchors/returns pass and visible south/east utilities remain grounded. Full semantic continuity of every retained facility utility is outside the targeted report. |
| 7 | Exterior materials and surface response | **86/100 — REJECT** | Olive/ivory/graphite/orange/timber families separate. Roof/paving/wall surfaces remain smooth and low-frequency; rock is still faceted and the visible wear/storytelling is sparse relative to Concept02. |
| 8 | Lighting, palette, and readability | **86/100 — REJECT** | Exposure -0.25 improves exterior balance and entry readability. `04_TOP` still compresses pale value groups, while `02_SOUTH` remains rail-heavy and the background has weak atmospheric separation. |
| 9 | Environmental storytelling and human use | **88/100 — REJECT** | Cabinet, hose, pipe/rack, benches, beds, pergolas and signs communicate an operating campus. Repeated benches/planting and large quiet walls/roofs remain visibly arranged rather than fully authored. |
| 10 | Terrain, drainage, and ground transitions | **95/100 — PASS (scoped)** | R15 route audit provides floor/support samples, zero findings, and 0.015 m max adjacent floor change; targeted contacts pass. This supports assembly transitions but does not establish Unity navigation behavior. |
| 11 | Roof and elevated detail | **90/100 — REJECT** | Added membrane fields, HVAC and coping read across all views, and contacts pass. Roof planes remain broad with limited drain/service/wear variation; `04_TOP` suppresses subtle separation. |
| 12 | View-to-view consistency | **89/100 — REJECT** | Locked cameras, protected footprint, plants, utilities, roof fields and palette persist. The same broad quiet planes and repeated planting/bench rhythm are obvious in `TOP` and both obliques; background faceting changes prominence by view. |
| 13 | Interface and reservation integrity | **95/100 — PASS (scoped)** | DELIVERY_R15 reports reservations/dependencies/source unchanged; BUILD_R15 records all protected boundary/lower-interface vertices unchanged at 0 m error. This is a strong scoped pass; Unity traversal is separate. |
| 14 | Runtime and delivery readiness | **95/100 — PASS (offline assembly scope)** | Fresh delivery cold load/dependencies/visibility plus four-frame native-render stability benchmark pass. This is offline Blender assembly evidence only; interactive FPS and Unity remain unmeasured/unverified. |
| 15 | Art-direction veto and professional finish | **80/100 — REJECT** | Spawn shell avoids toy-scale/generic-box dominance. Faceted contextual rock, repetitive furnishings/planting, quiet roof/paving planes and weak top-view value hierarchy keep professional finish below threshold. |

## Strongest remaining pixel blockers

1. Refine visible rock face shading/materials into deliberate broad directional planes with controlled painted variation; preserve the R15 source vertices/topology and silhouette contract.
2. Rebalance `04_TOP` so roof membranes, paving, olive fields, plant beds, drains and route edges retain distinct values at native resolution.
3. Add selective authored variation to the broad roof, ivory wall and courtyard paving fields, with localized wear tied to use rather than uniform noise.
4. Break repeated planting and bench rhythm into a few varied authored groupings while preserving exact bed/furniture positions and route clearances.
5. Keep `02_SOUTH` entry and route legible around the fixed foreground rail; any local additive adjustment must preserve the protected boundary and rerun the R15 route check.

R15 technical and delivery passes are requirement-specific scoped passes and were not penalized for unrelated art defects. Native render timing is offline assembly evidence, not interactive FPS or Unity readiness. No final acceptance is implied.
