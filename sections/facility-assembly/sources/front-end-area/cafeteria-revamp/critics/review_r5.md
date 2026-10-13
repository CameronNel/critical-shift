# Cafeteria R5 independent follow-up review

Reviewed 2026-10-13. This is a factual snapshot of **`checkpoints/full_r5.blend` and all thirteen `renders/review_r5/*.png`**, before the later R6 dart-bull repair. Images were initially inspected in `renders/rebuild_review/` and subsequently retained under `review_r5`. Models/scripts were not edited, images were not generated, and no other critic's scores were consulted. The governing art/specification and 20/20/15/15/10/10/10 rubric are unchanged from the independent R4 review.

## Result and scores

**91.55/100. R5 passes the score, category-floor, individual-camera and currently measured authoring checks. Full protocol completion remains PENDING a second final full review/render cycle and its comparison.** No critical visible scene defect was found. The R4 support-coverage blocker is repaired. A small coplanar dart-bull defect still exists in this R5 snapshot; it is not a critical room-scale failure and must not be described as fixed merely because the script calls the green shape an annulus.

| Category | /100 | Weight | Earned |
|---|---:|---:|---:|
| Layout / route readability | 95 | 20 | 19.00 |
| Art direction / silhouettes | 91 | 20 | 18.20 |
| Heroes / focal clarity | 92 | 15 | 13.80 |
| Materials / anti-plastic | 89 | 15 | 13.35 |
| Lighting / atmosphere | 91 | 10 | 9.10 |
| Dressing / worldbuilding | 89 | 10 | 8.90 |
| Technical cleanliness / reproducibility | 92 | 10 | 9.20 |

The visual scores remain largely stable because the macro composition and material read are largely stable. The technical increase is earned by actual registration coverage, a strict failing gate, contact repairs, source consolidation and the completed fresh rebuild/render evidence. It is not an award for implementation effort.

The cafeteria still reads as a coherent warm institutional room, with clear travel routes, specific dining-chair silhouettes, a full lounge and convincing game equipment. The coffee warming cups now have visibly hollow interiors. The coffee machine remains the weakest detailed focal asset: its spare control face and dark handle/cup overlap are less carefully resolved than the foosball and basketball machines. Sofa upholstery remains unusually uniform, and repeated neatly aligned serving stock reduces the sense of everyday use. These are polish limitations, not dominant low-poly, plastic or random-clutter vetoes.

## Per-camera visual assessment and R4 comparison

Every supplied PNG was opened individually at its native **960 × 540** resolution. All thirteen visually PASS; no material regression was found in route clarity, major silhouettes, exposure or material identity. Minor support translations and extended suspension endpoints are consistent with the intended repairs. Low-sample noise differences are not interpreted as modeled surface defects.

| Camera | Result | R4 → R5 assessment |
|---|---|---|
| `CAF_01_ENTRY_NORTH` | PASS | Stable central route and destination hierarchy. Distant red hall opening remains conspicuously bright. |
| `CAF_02_DINING` | PASS | Stable table/serving/medical composition and chair material separation. No new obstruction. |
| `CAF_03_SERVING` | PASS | Stable counter, kiosk and queue read. Small contact repairs do not damage the composition. |
| `CAF_04_LOUNGE` | PASS | Stable full lounge, negative space and warm local lighting. Upholstery uniformity remains. |
| `CAF_05_GAME_CORNER` | PASS | Stable clear equipment silhouettes and play-area read; minor placement/mounting corrections are unobtrusive. |
| `CAF_X1_AIRLOCK_DOOR` | PASS | Stable door construction, booth scale and clear approach. |
| `CAF_X2_YARD_DOOR` | PASS | Stable visible connection beyond the room, threshold and clear door approach. |
| `CAF_X3_MEDICAL_DOOR` | PASS | Stable framed doorway and drinks cluster. No gross new contact or clipping fault. |
| `FE_05_CAFE_REVERSE_NORTH_TO_SOUTH` | PASS | Stable reverse-axis readability and furniture separation. |
| `R8_GAMES_HERO` | PASS | Specific rods, players, bearings, returns, machine frames, nets and balls retain their quality. |
| `R8_LOUNGE_HERO` | PASS | Stable furniture forms and table contents; slightly corrected table-lamp support. Rigid/uniform sofa surfaces remain. |
| `R8_COFFEE_DETAIL` | PASS | Improved warming-cup rims/interiors. Machine/portafilter/cup readability remains the principal local weakness. |
| `R8_DINING_HERO` | PASS | Stable authored chair shells and bent frames. Suspended-sign glare and neat repeated stock remain. |

A separate read-only same-camera calculation against R4 found matching dimensions in every view and mean absolute RGB differences of **0.375–1.034 /255**. These images are **not byte-identical**. The higher local differences agree with the support/cup changes; visual inspection found no material regression. The earlier unchanged-state `cold_r4` comparison spans approximately 0.253–0.660 /255 and supplies useful context for low-sample variation. Its JSON contains an old `current` path label; that label is not treated as evidence that it compares this repaired R5 state.

## Repaired technical state

The reviewed R5 validation reports **799,998 evaluated module triangles**, including **453,824 cafeteria triangles**, leaving **two triangles** under the 800,000 cap. This is the actual R5 count after the warming-cup change, superseding the earlier 799,742 figure. The cafeteria's 400k flag and the lack of meaningful authoring reserve remain material handoff notes; no runtime performance was measured.

`support_coverage.py` now classifies supported cafeteria objects and accepts either a direct registration or a registered ancestor. An independent fresh-process read-only probe confirmed **431 required objects, 227 directly registered objects/assemblies, 850 anchors and zero missing registrations** in the saved state. Remaining unregistered/unclassified source entries were shell/floor construction, architectural finishes and surface decals, rather than the formerly omitted signs, tableware and game stools. The final numerical report records all 850 anchors passing, with gaps from **−0.0005 to 0.005 m** and maximum reported angle **0.02°**.

`../validate_front_end.py` now raises on missing support coverage or failed contact, instead of merely reporting a selected set of successful anchors. `verify_support_gate.py`, `negative_support_gate.json` and its log demonstrate that removing `rules_game`'s registration gives exactly that missing entry and a rejected validation result. The negative check modifies only the in-memory scene and restores the field without saving the model. The negative-test artifact predates the final warming-cup geometry change but tests the same registration/failure logic.

`support_repairs.json` records **28** inherited contact/suspension repairs, including wall placements, tabletop contacts and roof ends of suspension rods. R5's numerical evidence retains passing lanes, seven unchanged interfaces, zero reimport bounds error and unchanged unrelated yard/hall/shared geometry signatures. Images and external fonts are packed, with no missing dependencies or linked libraries. The fresh read-only open confirms metric units with scale length 1 and no negative world determinants.

The material-consolidation function restricts sharing to the reimported palette, excludes image shaders and compares node input values, relevant operations, ramps and links before remapping. Its record contains **49** merges. The probe finds **113 polygon/curve-used material datablocks**, with no remaining numbered reimported palette copies. This is a real consolidation improvement; it does not prove the separate per-view material-family cap or engine batching behavior.

The completed `logs/cold_rebuild_final.log` runs graphics, three standalone builds/previews, room rebuild, numerical validation and the thirteen-camera render batch in fresh processes. `logs/rebuild_review.log` lists all thirteen saves and a normal Blender exit. Thus R5 has cold build/open/render evidence. A second final cycle's visual-stability evidence was still pending when this R5 snapshot was closed.

## Remaining R5 mesh defect

The native bull repair uses `p_lathe(..., close=True)`. In the actual helper, `close=True` fills the first and last radial rings with n-gons; it does not create the inner cylindrical wall. The saved bull therefore has **40 green front annular quads plus one filled inner-radius cap**, still overlapping the separate red plug at the same depth.

The green front-facing area is **0.000781046 m²**, approximately the whole outer disk, rather than the intended annulus area **0.000657590 m²**. The red plug's front area is **0.000126157 m²**. The standalone preview still shows a dark center. This is a small verified source/pixel defect. It remains in R5 even though later source code may repair it; R6 must be judged separately.

## Highest-impact remaining work

1. Complete the second final full review/render comparison; keep full protocol completion pending until that evidence is inspected.
2. Resolve the coffee machine's group-head/handle/cup separation and specific control/drip-tray construction, which remain weak in the detailed camera.
3. Add selective cushion compression, contact wear and small asymmetries to lounge/dining use patterns, preserving clear routes and restrained material frequency.

Repair the small dart-bull overlap and preserve budget compliance while doing so. No Unity import, collider, interaction, animation, networking, gameplay or measured performance acceptance is implied by this authoring review.
