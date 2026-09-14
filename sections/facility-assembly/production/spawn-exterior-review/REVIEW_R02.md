# Spawn exterior + rescue courtyard R02 independent review

Revision: `R02`  
Build: `facility_spawn_concept02_R02.blend`  
Source hash: `03e931f2b24dd68349e2b337668efa327e24e99d8e5b7094a1a167758dc10c7a`  
Views: `renders-R02/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved (`CONCEPT_APPROVAL.md`)

## Decision

**REJECT — iteration review only.** All four locked actual renders were inspected at native resolution. The R02 build clearly adds the approved olive/ivory/orange identity, arrival accents, service cabinet/pipe/hose dressing, planted beds, and richer timber. It remains below the strict `>93` threshold, with cold/flat lighting, regular grass rows, unfinished-looking rear/service value grouping, and absent current technical evidence. No polish or final acceptance is implied.

## View observations

- `01_COURTYARD`: orange `STAFF / ARRIVAL` fascia reads strongly; olive wing, planters, benches and broad courtyard route are clear. The sunlight is cool/flat and the grass strips read as repeated spikes. Large pale paving dominates.
- `02_SOUTH`: `SHIFT ENTRY`, local-service cabinet, orange hose and utility run are visible and grounded. The camera remains tight; the rail cuts across the entire foreground and the building/route beyond is compressed. Wall wear appears as conspicuous pale blotches rather than designed variation.
- `03_EAST`: service cabinet, low pipe run, rack/bench and planting are visible. The service wall remains a large dark-green plane with sparse authored detail; the regular planted strip and light stands repeat mechanically.
- `04_TOP`: footprint and central courtyard remain open; benches, pergolas, plant beds, routes and roof equipment align across the plan. The nearly white ground and roof fields flatten boundaries and make fine route/grade claims impossible from pixels alone.

## Category scores

| # | Category | Result | Evidence / blocker |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **72/100 — REJECT** | Approved Concept02 palette and service additions are recognizable in all applicable views. Lighting remains colder/flatter than the target, grass rows are too regular, and the approved painterly/value hierarchy is only partly realized. |
| 2 | Silhouette and massing | **78/100 — REJECT** | Stepped roof blocks, olive wings, entry frame and courtyard remain legible. Large shell planes and repeated vertical panel rhythm still dominate; secondary forms are sparse outside the entry/service additions. |
| 3 | Scale and spatial layout | **81/100 — REJECT** | Door, rail, bench, cabinet, planters and roof unit read at believable relative scale; top footprint remains consistent. Exact dimension/layout audit is pending. |
| 4 | Circulation, access, and rescue route | **80/100 — REJECT** | Central courtyard stays open in `TOP`; approach and entry read in `COURTYARD`/`SOUTH`; service apron is visible in `EAST`. Current route/threshold/clearance audit is absent, and foreground rail dominance weakens gameplay readability in `SOUTH`. |
| 5 | Construction and load/support logic | **UNVERIFIED** | BUILD_R02 fixture ledger names supports and anchors, but current evaluated support/penetration evidence was not supplied. Pixels alone cannot certify the cabinet, pipes, hose, rack, planters or roof fixtures. |
| 6 | Utility and service continuity | **UNVERIFIED** | South/east cabinet, hose, pipe runs and glands are visible, but the requested technical R02 connectivity report is still pending. |
| 7 | Exterior materials and surface response | **68/100 — REJECT** | Olive sheet metal, ivory walls, graphite trims, orange accents, timber and paving separate. Roof/paving/walls remain low-contrast and mostly smooth; pale blotches look like artifacts or un-authored wear. |
| 8 | Lighting, palette, and readability | **58/100 — REJECT** | Palette direction is materially closer to Concept02, but all four views remain cold and flat with weak warm sun/contact hierarchy. The central courtyard and roof planes are over-bright; entry practicals do not establish enough depth. |
| 9 | Environmental storytelling and human use | **74/100 — REJECT** | Service cabinet, hose, low utility run, spare rack, benches and planted margins establish staff maintenance use. The repeated grass rows, sparse service wall and empty large paving still feel placed for coverage rather than authored use. |
| 10 | Terrain, drainage, and ground transitions | **UNVERIFIED** | Drains and paving joints are visible, but current grade/transition/terrain evidence is absent. Bright ground prevents reliable pixel-only judgment of subtle transitions. |
| 11 | Roof and elevated detail | **72/100 — REJECT** | Roof units, trims, stepped heights and top plan remain coherent. Broad roof planes have limited material/edge variation and the lighting leaves roof construction visually flat; support/drain checks are pending. |
| 12 | View-to-view consistency | **79/100 — REJECT** | Same locked cameras and new olive/orange/plant/service language carry through all four views; top view preserves the open center. Lighting/value response and storytelling density differ by face, with the rear still under-authored. |
| 13 | Interface and reservation integrity | **UNVERIFIED** | BUILD_R02 states unchanged source room libraries and scoped exterior, but current portal/reservation/source-preservation audit is absent. |
| 14 | Runtime and delivery readiness | **UNVERIFIED** | EEVEE manifest, build hash and object ledger establish a review artifact. Blender cold-load/dependency/geometry/route/performance evidence is absent; Unity runtime remains separately unverified. |
| 15 | Art-direction veto and professional finish | **60/100 — REJECT** | No dominant generic-low-poly or toy-scale veto. Cold flat lighting, repeated grass rows, large low-information planes, and visible pale blotch artifacts keep the pass below professional finish. |

## Top concrete pixel blockers

1. Correct the global lighting/exposure toward warm readable sun and cool-neutral shade with stronger contact and door-reveal depth; preserve the approved olive/ivory/orange palette without a cyan wash.
2. Replace the repeated straight grass strips with designed clusters and varied density/height consistent with Concept02; retain clear routes and plant-bed positions.
3. Resolve or redesign the pale irregular wall blotches visible on `02_SOUTH` and `03_EAST`; they currently read as accidental artifacts rather than authored wear.
4. Give the east/service wall a clearer focal composition around the cabinet, pipe/hose and rack, with deliberate value grouping and support visibility; keep the route clear.
5. Keep `02_SOUTH` readable despite the foreground rail and tight framing; the door, both wings, service dressing and approach must remain legible in the fixed camera.

Technical_R02 and route audit were not present at review time, so categories 5, 6, 10, 13 and 14 remain `UNVERIFIED` regardless of the BUILD_R02 ledger.
