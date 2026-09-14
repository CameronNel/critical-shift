# Spawn exterior + rescue courtyard R16 independent review

Revision: `R16`  
Build hash: `bc87737a25bea91f1a276570ccb33358d40d982f39ac756005caaf4375317dcf`  
Views inspected: `renders-R16/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** R16 native pixels show stronger baked contact shadows and a coherent warm olive/ivory/orange palette. Fresh R16 support, delivery, route, validation, and offline-render evidence pass their stated scopes. The art pass remains below the strict `>93` threshold: the new lighting is too contrasty in the courtyard/east views and leaves the south wall/entry dark; the top view has hard shadow blocks and low material separation; background rock still reads as coarse faceted geometry; roof/wall/paving fields and repeated planting remain under-authored. No Unity or interactive-FPS claim is made.

## Category scores

| # | Category | Result | Specific deduction/evidence |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **88/100 — REJECT** | Approved footprint, palette, furniture, service dressing and roof fields persist. Contrast/shadow treatment, coarse rock, sparse wear and low-information surfaces remain below Concept02’s stylized target. |
| 2 | Silhouette and massing | **90/100 — REJECT** | Spawn stepped shell, entry and roofs remain legible. The large faceted rock/background still competes with the shell, while most spawn masses remain rectangular and minimally articulated. |
| 3 | Scale and spatial layout | **92/100 — REJECT** | BUILD_R16 retains the protected boundaries/lower interfaces and fixed footprint; doors, benches, beds, HVAC, routes and service objects read plausibly. `02_SOUTH` remains rail-heavy, crowding the perceived entry apron; no wrong dimensions are inferred. |
| 4 | Circulation, access, and rescue route | **95/100 — PASS (scoped)** | R16 route audit reports zero findings with floor samples/support objects and max adjacent floor change 0.015 m; `04_TOP` keeps central circulation open. Unity traversal/collision/navmesh/controller remain unmeasured. |
| 5 | Construction and load/support logic | **95/100 — PASS (scoped)** | Fresh R16 expanded roof/base contacts plus anchors/returns pass; source-preservation hashes and protected interface geometry remain unchanged. The report is targeted and does not blanket-certify every retained source object. |
| 6 | Utility and service continuity | **94/100 — PASS (scoped)** | South/east cabinets, hose, pipe runs, roof units and supports remain visibly coherent; technical anchors/returns pass. Full semantics of every retained facility utility remain outside the targeted audit. |
| 7 | Exterior materials and surface response | **84/100 — REJECT** | Olive/ivory/graphite/orange/timber families separate. Hard shadowing darkens materials into near-black in `02_SOUTH` and `03_EAST`; roof/paving/rock surfaces remain smooth or coarse-faceted with limited authored wear. |
| 8 | Lighting, palette, and readability | **70/100 — REJECT** | Baked GI/contact shadows add grounding, but courtyard/east shadows are very hard, south entry/walls are too dark, and top view shadow blocks compress paving/roof/route values. The 4x12 shadow-map setting is not itself visual proof. |
| 9 | Environmental storytelling and human use | **87/100 — REJECT** | Entry, service cabinet, hose/rack, benches, planters and pergolas communicate an operating campus. Repeated planting/furniture rhythm and quiet roof/wall stretches remain visible. |
| 10 | Terrain, drainage, and ground transitions | **95/100 — PASS (scoped)** | R16 route floor/support samples report zero findings and 0.015 m max adjacent change; targeted contacts pass. This supports assembly transitions only and does not prove Unity navigation. |
| 11 | Roof and elevated detail | **90/100 — REJECT** | Membrane fields, HVAC, coping and seams remain coherent. Hard shadows obscure roof/paving value groups in `TOP` and `SOUTH`, and elevated service/drain variation is still sparse. |
| 12 | View-to-view consistency | **84/100 — REJECT** | Fixed cameras, footprint, palette and object placement persist. Lighting impact changes sharply by view: near-black south wall/entry, heavy east/courtyard shadow blocks, and top-view shadow geometry reduce consistent readability. |
| 13 | Interface and reservation integrity | **95/100 — PASS (scoped)** | DELIVERY_R16 reservations/dependencies/source and visibility checks pass; route audit is clean. The named checks do not claim Unity traversal behavior. |
| 14 | Runtime and delivery readiness | **95/100 — PASS (offline assembly scope)** | R16 cold load/dependencies/inventory/visibility and four-frame native render stability evidence pass; PREVIEW_VALIDATION_R16 records baked GI and 256-sample render context. Interactive FPS and Unity remain unmeasured. |
| 15 | Art-direction veto and professional finish | **74/100 — REJECT** | No toy-scale or generic low-poly veto dominates the spawn shell. Severe contrast blocks, faceted background, broad quiet surfaces, repetitive planting and limited wear keep professional finish below threshold. |

## Strongest remaining pixel blockers

1. Lift and soften the hard shadow blocks while retaining baked contact grounding; `02_SOUTH` must keep the SHIFT ENTRY, service cabinet, hose, wall material and foreground route readable, and `01_COURTYARD`/`03_EAST` must not collapse into dark façade bands.
2. Bring `04_TOP` into a usable value range where roof membranes, paving, drains, olive fields, beds and rescue-route edges remain distinct under the new GI/shadow setup.
3. Refine the visible rock/background face treatment into deliberate broad planes with controlled painterly variation; preserve source geometry, topology, silhouette and placement.
4. Add selective authored material/wear variation to existing roof, ivory wall and courtyard paving fields, avoiding generic noise and footprint changes.
5. Break repeated planting and bench rhythms into varied clusters while preserving exact approved positions and route clearances.

R16 technical, route, reservation, source, delivery and offline assembly checks are requirement-specific scoped passes and were not globally art-penalized. The render benchmark is offline only; Unity readiness and interactive FPS remain unverified. No final acceptance is implied.
