# R23 fresh comparison and acceptance review

I inspected all 11 R23 fixed views, all 11 paired R22 and R21 views, the three R23 actual-map context views, and the Spawn hero and room references. The Spawn images provide the construction and finish benchmark; their brightness and mood do not set the refinery target.

## Visual result

R23 keeps the requested dark, cold, neglected direction. The aisle and visible approaches remain open and readable, with floor marking wear and service residue established in R22. R23 then redistributes power among existing practical fixtures. In MINE_TO_CRUSHER, the receiving hopper, feed conveyor and nearby controls have stronger separation. REVERSE also shows a more legible approach and machine silhouette. The PROCESS hero vessel remains the clearest focal point; its flange, gauges, fasteners, valves, tags and pipework read cleanly at the detail view.

One remaining visual defect keeps the art-direction/silhouette score below 99: in CAM_PROCESS, the far-right support machinery still compresses into a dark group, so the equipment after the hero vessel has weaker form separation than the receiving and assembly views. This is a local hierarchy target for a next pass: improve separation around those forms with existing practical sources and localized finish control, while preserving the dark room. Do not brighten the room broadly. I saw no route blockage or interface change. In the actual-map context, the portal frames and approaches connect to nearby geometry; I did not penalize black beyond open portals in the standalone room.

The interrupted night-shift cluster remains purposeful in WORK_NOOK: the leak and shift papers, gloves, cup, radio and tools tell the story at their intended detail distance. R23 makes no dressing or geometry change from R22. Materials retain varied dirty concrete, worn enamel, oxide and metal response; the new lighting keeps the work pools restrained rather than glossy or cheerful.

## Paired stability: R21 → R22 → R23

The measured pixel changes are nonzero, but they track the intended local revisions. R21→R22 adds broader indoor floor residue, dulled lane paint and lens/material refinements. R22→R23 changes existing fixture-source powers and matching lens emission properties only. The technical audit confirms no geometry, fixed-camera, light-pose or base-surface-palette changes in R23. Overall composition, route and mood stay stable through both transitions. Per-view RGB means and mean absolute RGB differences are descriptive image measurements, not perceptual scores.

| View | Mean RGB R21 → R22 → R23 | Mean absolute RGB difference R21→R22 | Mean absolute RGB difference R22→R23 |
|---|---:|---:|---:|
| CAM_ASSEMBLY | 13.019 → 16.012 → 16.714 | 3.269 | 0.861 |
| CAM_DISPATCH | 15.027 → 20.023 → 20.669 | 5.131 | 0.807 |
| CAM_ENTRY | 18.548 → 20.421 → 21.618 | 2.439 | 1.882 |
| CAM_HERO_DETAIL | 32.392 → 37.775 → 38.146 | 5.545 | 0.835 |
| CAM_MAIN_ROUTE | 24.788 → 27.925 → 27.883 | 3.582 | 1.701 |
| CAM_MATERIAL | 15.946 → 20.714 → 23.705 | 4.813 | 3.015 |
| CAM_MINE_TO_CRUSHER | 16.089 → 17.938 → 21.894 | 2.332 | 4.713 |
| CAM_PINCH | 23.412 → 24.650 → 23.455 | 1.593 | 2.419 |
| CAM_PROCESS | 28.430 → 32.114 → 30.528 | 3.916 | 2.651 |
| CAM_REVERSE | 16.287 → 18.349 → 21.938 | 2.388 | 3.623 |
| CAM_WORK_NOOK | 24.884 → 26.771 → 28.269 | 2.148 | 1.552 |

R21→R22 mean RGB rises in every view. R22→R23 mean RGB changes are mixed: the increases are strongest in MINE_TO_CRUSHER and REVERSE, while MAIN_ROUTE, PINCH and PROCESS decrease slightly. This supports local illumination changes rather than a broad brightness shift. Mean absolute RGB differences are 1.593–5.545/255 for R21→R22 and 0.807–4.713/255 for R22→R23; the across-view averages are 3.378 and 2.187, respectively. The later transition changes only local practical-light response, while camera composition and base-surface palette remain stable.

## Scores

| Category | Weight | Score | Evidence |
|---|---:|---:|---|
| Route readability | 20% | 99 | The clear aisle and floor route read through the fixed views; actual-map context confirms usable approaches at the open portals. |
| Art direction and silhouettes | 20% | 98 | The cold, run-down style is coherent, but far-right PROCESS support machinery still loses separation. |
| Hero process equipment | 15% | 99 | The pressure vessel and attached mechanical details remain strong at both broad and hero-detail distances. |
| Materials and anti-plastic quality | 15% | 99 | Grime, worn lane paint, oxide, enamel and metal have controlled varied response, without a glossy or noisy-material failure. |
| Practical lighting and atmosphere | 10% | 99 | Restrained pools support the gloomy mood. Technical evidence confirms 15 live fixture-bound sources, six failed sources at zero, and world strength zero. |
| Purposeful dressing and worker story | 10% | 99 | WORK_NOOK clearly shows a purposeful interrupted-shift cluster at its intended camera distance. |
| Technical cleanliness and reproducibility | 10% | 100 | Candidate and cold validations pass; independent lighting audit passes; all 11 cold renders are pixel-identical and fingerprints match. |

Weighted score: **98.9/100**. No critical veto observed. R23 remains below 99 in art direction/silhouettes and below 99 weighted overall, so it is not accepted.

## Technical, cold and context evidence

`validation_R23.json` and `validation_R23_cold.json` pass with 418,610 visible evaluated triangles, 29 protected interfaces unchanged, world strength zero and no reported issues. `technical_R23.md` verifies 21 distinct physical fixture lenses, 15 active sources paired to those lenses, six failed sources with both source energy and lens emission at zero, and unchanged camera/light poses. R23 modifies only existing fixture powers; no external source or fill light was added.

Formal `comparison_R23.json` and `pixel_comparison_R23.json` pass: checkpoint and rebuild object/material state is identical, all 11 cold images match with maximum channel delta zero, and render settings match. The context validation passes for 3,029 visible poses and 21 candidate light sources at world strength zero; it reports no transform errors and leaves the source unchanged. These checks do not certify runtime behavior or exhaustive map dependency health.
