# Spawn exterior + rescue courtyard R04 independent review

Revision: `R04`  
Build: `facility_spawn_concept02_R04.blend`  
Source hash: `b0846087369392fcf3289db9c9724a0e45a8cc3a8ebf51d55b9cfee67a860fc8`  
Views inspected: `renders-R04/01_COURTYARD.png`, `02_SOUTH.png`, `03_EAST.png`, `04_TOP.png`  
Concept: Concept02 approved; exterior-only scope preserved

## Decision

**REJECT — iteration review only.** The R04 geometry fixes are visible and the targeted technical report now passes; the route audit has zero findings. The built exterior still fails the strict `>93` requirement because the south view is substantially too dark, the background rock/horizon reads as crude faceted geometry, the top view is overexposed/low-information, and several surfaces remain broad and under-authored. No Unity runtime claim is made.

## Category scores

| # | Category | Result | Evidence / blocker |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **78/100 — REJECT** | Olive/ivory/orange Concept02 direction is present, with readable arrival/service additions. The warm stylized target is undercut by the cold/black south exposure, crude faceted background, and plain roof/ground fields. |
| 2 | Silhouette and massing | **82/100 — REJECT** | Stepped shell, entry, roof units and courtyard masses read across all four views. Large rectangular wall/roof planes still dominate, while the rock silhouette has visibly crude triangulated facets. |
| 3 | Scale and spatial layout | **84/100 — REJECT** | Doors, benches, rails, HVAC, planters, pipe/rack and courtyard footprint read at believable relative scale; fixed cameras and placements are consistent. No score can exceed the visible layout proof without a fuller dimensional audit. |
| 4 | Circulation, access, and rescue route | **86/100 — REJECT** | `TOP` keeps the central courtyard open; all listed route samples and spawn inner transition have zero findings. The south foreground rail consumes visual space and the lighting makes the route hard to read; runtime collision/navmesh is not certified. |
| 5 | Construction and load/support logic | **84/100 — REJECT** | R04 targeted ground contacts and wall anchors pass after the rack/bed correction; no missing used images. The report explicitly excludes blanket certification of every retained source object, so this is a scoped technical score. |
| 6 | Utility and service continuity | **83/100 — REJECT** | South/east service fixtures, wall anchors, and utility returns pass the targeted report, including the corrected south run. Full facility endpoint semantics and every retained utility are outside the report scope. |
| 7 | Exterior materials and surface response | **74/100 — REJECT** | Olive metal, ivory walls, orange accents, graphite trim, timber, paving and vegetation are distinct. Roof and paving remain smooth/low-detail, and the south view crushes the dark wall/material response into near-black. |
| 8 | Lighting, palette, and readability | **55/100 — REJECT** | `01_COURTYARD` and `03_EAST` have readable sun/contact shading, but `02_SOUTH` is severely underlit with black wall planes and an unreadable entry sign. `04_TOP` is washed out. The background/horizon has no controlled atmospheric finish. |
| 9 | Environmental storytelling and human use | **79/100 — REJECT** | Service cabinet, pipe run, hose/rack, benches, planted beds and entry identity explain a maintained campus. The service wall still has large quiet areas, and repeated plant strips feel procedural rather than authored. |
| 10 | Terrain, drainage, and ground transitions | **84/100 — REJECT** | Ground contacts pass for the corrected beds/rack and drains are visible; top view shows coherent paving. Terrain/background rock is visibly faceted and grade/transition behavior is only partly evidenced. |
| 11 | Roof and elevated detail | **78/100 — REJECT** | Roof heights, coping, HVAC units and seams remain coherent in `COURTYARD`, `SOUTH`, `EAST`, and `TOP`. Roof fields are broad and flat, with limited service/drain storytelling; top exposure weakens detail readability. |
| 12 | View-to-view consistency | **78/100 — REJECT** | Fixed camera manifest and object language are consistent; courtyard remains open and additions recur. Lighting differs sharply by view, with south near-black and top washed out, and the crude background dominates different views inconsistently. |
| 13 | Interface and reservation integrity | **UNVERIFIED** | Source preservation and placements pass in `TECHNICAL_R04.json`, and route audit is clean, but an explicit current portal/reservation/aperture audit is not included. |
| 14 | Runtime and delivery readiness | **UNVERIFIED** | Blender cold load passes and source hashes/placements are recorded. No R04 assembly performance benchmark, complete dependency/material visibility validation, or Unity runtime evidence is supplied. |
| 15 | Art-direction veto and professional finish | **62/100 — REJECT** | The pass avoids toy scale and generic low-poly construction in the spawn shell, but the south black crush, top washout, crude faceted background, broad blank planes and repetitive planted strips keep it below professional finish. |

## Concrete pixel blockers

1. Add directional skylight/fill and rebalance exposure so `02_SOUTH` retains readable olive walls, ivory entry, `SHIFT ENTRY`, service cabinet, hose, rail and route; the current near-black wall planes are a hard readability failure.
2. Bring `04_TOP` into the same readable value range; its overexposed paving/roof fields erase material grouping and route-edge information.
3. Replace or substantially refine the visible faceted background rock/horizon treatment; its large triangular planes read as crude unfinished geometry and dominate `01_COURTYARD`, `02_SOUTH`, and `03_EAST`.
4. Break the repeated straight grass strips into authored cluster groupings with varied spacing and height while preserving plant-bed positions and clear routes.
5. Add selective roof/paving/material variation and contact detail so large shell fields stop reading as blank smooth planes; keep detail density below clutter.

Technical note: R04 targeted checks pass and route samples report no findings, but categories 13 and 14 remain unverified for missing current reservation/aperture and assembly-performance/dependency evidence. Unity readiness remains separate and unverified.
