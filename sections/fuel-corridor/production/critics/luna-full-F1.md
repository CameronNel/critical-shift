# Luna independent full-corridor review — F1

## Decision

**F1 is not accepted.** All seven visual categories and all nine requested areas are far below the strict >98 target. One image has a critical visible defect: `C07_BYPASS.png` contains a solid black, hole-like floor patch at the left side of the junction. The technical report may establish floor surfaces at that location, but the render still presents a conspicuous black cutout. Treat it as a visual failure until the finish overlap is resolved and the fixed view is rerendered.

The repeated broad wall-panel and door language also leaves much of the full corridor visually sterile and under-authored. I do not call the panels themselves an automatic veto in every view, but their repetition across the pack, combined with plain large doors and limited storytelling, keeps the full-scene quality far below the spawn reference. The spawn-room renders remain the 100-point quality anchor.

I inspected all 16 images in `production/renders/review/full-F1/` and the matching `RENDER_MANIFEST.json`. The manifest binds the render set to `checkpoints/fuel_full_F1.blend` hash `752c3e932969d5b001117c1042c73456e095c8185b4c4844b7fa10c8020d2f86`, at 960×640, 24 samples. Reduced resolution/sample count limits fine surface inspection, but does not obscure the large structural, lighting, composition or route defects below. F1COLD contact issues are separate technical evidence and receive no visual credit here.

## Seven-category scores

Scores compare rendered evidence with the spawn reference at 100. They are independent and not averaged up from area scores.

| Category | Score | Evidence |
|---|---:|---|
| Spatial composition and readability | 82 | The main route and ports can be followed, and the floor arrows provide some guidance. Long corridors and service branches often terminate in quiet blank fields; `C07` has a visually broken floor, while `C02` has an isolated floor case near the foreground. |
| Modeling and fabrication detail | 82 | The cask, cart and bench props in `C03`, `C09`, `D01` and `D02` have authored forms. In contrast, large door leaves in `C06`/`D04` and `C10` read as broad simple slabs with a few generic bars/handles, and most wall bays repeat the same panel rhythm. |
| Materials and surfacing | 79 | Painted upper/lower wall families are distinct, and the cart/cask hardware has several useful material groups. Across most views the same pale upper panels, dark blue lower panels and gray floor repeat with very little visible localized wear or surface variation. The cask barrel remains smooth and nearly uniform. |
| Lighting | 78 | Practical fixtures are present, but many views are dim and evenly filled, with dark foreground mechanisms and weakly differentiated focal areas (`D01`, `D02`, `D03`, `D05`, `D06`). Small bright fixtures do not create a consistent hierarchy through the routes. |
| Environmental storytelling and asset diversity | 83 | The bench, radio, tools, utility panel and cask tell a credible local maintenance story. Most entry, bypass, east-turn and connector views lack comparable human-use cues; repeated doors, panels and lights dominate the corridor. |
| Professional finish and support contacts | 76 | The black junction floor patch in `C07` is a clear visual defect. The orange case on the floor in `C02` reads as a loose object in the route. Other rendered assemblies mostly appear attached, but screenshots cannot establish hidden contacts; the separately reported F1COLD contact defects remain open technical concerns. |
| Visual parity with spawn | 78 | The corridor is coherent as a restrained industrial space, but spawn shows far more silhouette, material, color and human-use variety. Fuel frequently reads as a repeated clean modular hallway, particularly in the wide route views. |

## Area scores

Every area remains below >98. These area scores reflect the named views only; where an area lacks a clear identifying focal asset in its supplied camera, the low score includes that weak visual evidence.

| Area | Score | Visible evidence and defects |
|---|---:|---|
| Entry / refinery | 83 | `C01_ENTRY` has a legible approach, wall-mounted extinguisher and distant bench/cask. Large neutral wall fields and ceiling grid dominate; route markers are sparse and the service zone reads as a small cluster at the end of a long plain run. |
| Staging / bench / cask / utilities | 87 | `C03_HERO`, `C09_MATERIALS`, `D01_CARRIER_OPERATION`, `D02_WORKBENCH`, `D03_UTILITY` show the most authored and narratively specific content. The assembly is still small in `C03`; close views reveal clean, smooth cask surfaces, sparse wear and dim lighting. This is the strongest area, not near the reference. |
| Freight gate | 80 | `C03_HERO` and `D05_GATE_MECHANISM` show portal structure and powered drive. The fixed mechanism image is dark, while the portal remains dominated by large dark horizontal/vertical members; the complete opening and operation do not make a compelling hero composition. |
| East turn | 80 | `C05_EAST_TURN` communicates the turn and adjacent doors. The near wall is a large uninterrupted field; orange floor arrows are small and door faces are simple, repeated panels. |
| Delivery / waste | 77 | `C05_EAST_TURN`/`C08_SERVICE_JUNCTION` provide only general connector views; no strong waste-transfer identity or distinctive delivery staging is visible. If this pack intends those views to cover the area, its function is under-communicated. |
| Reactor adapter | 77 | `C06_REACTOR_THRESHOLD` and `D04_REACTOR_WIDE` show a large transfer door and clear approach, but the leaves are oversized dark slabs with minimal construction beyond a few pull bars, horizontal strips and rings. The wide image makes their scale clear while also making the lack of panel hierarchy more obvious. |
| Bypass / recess | 72 | `C07_BYPASS` contains the critical black floor patch at the left side of the junction, next to the structural frame. The route otherwise reads as a narrow, unremarkable corridor; `D06_SERVICE_RECESS` isolates a functional panel but is dark and sparse. |
| Plant header | 78 | `C10_PLANT_HEADER` gives the S01 header and double door a clear centered silhouette. The large leaves remain mostly flat and symmetrical, with two small windows, bars and simple handles; surrounding walls repeat the same panel kit. |
| North / clean corridor | 77 | `C08_SERVICE_JUNCTION` shows the branch and through-route but offers little visual hierarchy or human/service function beyond wall panels, cable tray and a small cabinet. The junction is dim, and the destination remains visually generic. |

## Highest-impact causal corrections

1. **Resolve the visible junction floor overlap first — `C07_BYPASS.png`.** The black patch at the left edge of the junction looks like a missing slab or unrendered hole, regardless of the underlying surface-ray result. Give the overlapping floor finish one visible owner, preserve the contract bounds, and rerender the unchanged camera. Do not mask it with a prop or dark decal.

2. **Break the repeated panel-and-door rhythm with authored architectural variation — `C01`, `C02`, `C04`, `C05`, `C08`, `C10`.** Across these views, the same large pale upper fields, blue lower panels, continuous rail and ceiling grid repeat with little functional differentiation. Preserve the footprint and passage widths, but add selected structural transitions, deeper access/reveal geometry, distinct service bays and appropriate wall-protection details. Do not distribute random small props across every wall.

3. **Redesign the major transfer leaves as constructed industrial doors — `C06_REACTOR_THRESHOLD`, `D04_REACTOR_WIDE`, `C10_PLANT_HEADER`, and the orange leaves at `C04_REVERSE`/`C05_EAST_TURN`.** The reactor adapter is the clearest case: two huge dark planes with sparse generic bars and circular pulls dominate both views. Establish actual leaf depth, folded perimeter, seals, stiffeners, track/hinge/lock logic and differentiated service panels; use hardware sized and placed for the door's function. Use the same object-specific reasoning for the plant header and orange connector doors.

4. **Rebuild the lighting hierarchy across the long routes — especially `D01`, `D02`, `D03`, `D05`, `D06`, `C07`, `C08`.** Add shape to the staging focal area and branch intersections with better localized practical falloff and controlled fill; lift dark mechanism details enough to read. Preserve shadows and avoid making the whole corridor flat bright. The current small lights produce isolated spots while nearby panels and authored objects remain murky.

5. **Extend the staging area's human-use language to the rest of the corridor — `C01` through `C10`.** The bench, case, radio, note, cup, tools, extinguisher and cask establish a useful start. Most other areas have little evidence of routine work, handover, storage or route-specific function. Add a few purposeful clusters or architecture-integrated service features where they help identify each zone; keep negative space and reserve dense detail for the staging/interaction points.

## Specific visible notes

- `C02_PRIMARY_ROUTE.png`: small orange case sits alone at the lower-left edge of the route view. It reads as an uncontextualized dropped/stored object and draws attention from the otherwise empty corridor; connect it clearly to a work area or remove it from this approach.
- `C06_REACTOR_THRESHOLD.png` and `D04_REACTOR_WIDE.png`: reactor leaves are the largest authored forms in this area but lack construction depth and distinct subassemblies. Their scale magnifies the flatness.
- `D05_GATE_MECHANISM.png`: mechanism is readable as a motor/rail assembly but remains very dark and fills the crop with black hardware. Improve local light/value separation and keep the rail, motor support and header distinguishable at the fixed camera.
- `D03_UTILITY.png`/`D06_SERVICE_RECESS.png`: pipe branches, control panel and hose are legible in close view, but the broader recess is dim and the same metal/panel finish dominates. Preserve the functional pipe route while improving local contrast and tying the installation into a more distinctive architectural bay.
- `C09_MATERIALS.png`: carrier build is the strongest asset-level construction evidence. However, the cream barrel occupies most of the focal mass and still reads as a clean smooth tube even at close range; use restrained broad surfacing changes and construction breaks that remain visible at player distance.

## Evidence and scope

All 16 fixed views opened: `C01_ENTRY`, `C02_PRIMARY_ROUTE`, `C03_HERO`, `C04_REVERSE`, `C05_EAST_TURN`, `C06_REACTOR_THRESHOLD`, `C07_BYPASS`, `C08_SERVICE_JUNCTION`, `C09_MATERIALS`, `C10_PLANT_HEADER`, `D01_CARRIER_OPERATION`, `D02_WORKBENCH`, `D03_UTILITY`, `D04_REACTOR_WIDE`, `D05_GATE_MECHANISM`, and `D06_SERVICE_RECESS`.

Reference images opened: `production/renders/reference/VALIDATE_Spawn.png` and `VALIDATE_Material_A.png`. The reference shows noticeably richer material and storytelling variety, including wood, tile, painted locker metal, fabric, rubber, paper, PPE and personal equipment. Fuel's industrial subject is not a fidelity bonus.

The render pack supports visual review only. It does not prove assembled adjacent-room passage, gameplay timing, engine collision/controller behavior or runtime integration. The reported four contact issues remain independent blockers until corrected and verified; they do not replace or explain the visible C07 black patch.
