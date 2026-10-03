# Independent visual review — R16

## Review scope

I opened and inspected all 11 current images in `production/renders/R16/` and compared matching views with R15, including `CAM_ENTRY`, `CAM_PROCESS`, `CAM_HERO_DETAIL`, `CAM_MATERIAL`, and `CAM_WORK_NOOK`. This review scores rendered pixels against the updated owner direction: “run down, dark, gloomy and hopeless.” The Spawn images set finish quality only; they are not a brightness or palette target.

## Scores

| Category | Score | Weight | Evidence |
|---|---:|---:|---|
| Route readability | 92 | 20% | The 2.8 m aisle reads across entry, route, reverse, and dispatch views; floor lane marks remain visible. Machinery edges and secondary controls disappear into black in the process, material, and dispatch views. |
| Art direction and silhouettes | 95 | 20% | Custom equipment silhouettes and the dirty grey-green / oxide palette convincingly replace R15's bright coral, cream, and mint treatment. Several large wall and floor planes still read as clean continuous surfaces. |
| Hero process equipment | 94 | 15% | PV vessel, clamp ring, gauges, couplings, and service fittings form a strong authored focal assembly. The detailed view shows some abrasion and dark staining, but the corrosion reads as isolated marks on otherwise broad, smooth panels. |
| Materials and anti-plastic quality | 85 | 15% | Oxidized machine colors and selective wear help, but walls and most of the central floor remain even and comparatively pristine. R16 needs larger, coherent signs of prolonged water, foot, and service wear. |
| Practical lighting and atmosphere | 96 | 10% | The mood shift is strong: the ceiling falls to near black, several fixtures fail, and weak cold pools separate the equipment. The bright white strips are conspicuous, while the darkest views suppress useful material and control detail. |
| Purposeful dressing and worker storytelling | 84 | 10% | The radio, cup, food, and shift board are readable and purposeful. The four neatly pinned sheets and orderly desk arrangement still suggest a maintained break station more than an interrupted, unwelcoming shift. |
| Technical cleanliness and reproducibility | 88 | 10% | The formal validator reports PASS, no protected-interface changes, world strength 0, no route obstructions, no missing dependencies, and all registered supports/normals passing. The independent technical audit still found reversed normals on all 16 north-wall stain sheets and PV corrosion strips 0.307–1.861 mm from their evaluated vessel surface against a 20 µm nominal offset. Fresh-process cold-start evidence was not available for this review. |

**Weighted score: 91.05/100.** R16 does not meet the required 99 in every category or the weighted 99 threshold. No automatic rubric veto was observed in the rendered views; the owner-requested neglect and decay remain the main visual gap.

## Findings for the next pass

1. **Keep the dark practical-light composition.** Compared with R15, the room now feels cold, depleted, and hostile. Preserve that palette and the failed-fixture rhythm while lifting only the task surfaces or controls that become unreadable in the material, dispatch, and process views.
2. **Make neglect read across the room, not only on the hero vessel.** In `CAM_ENTRY` and `CAM_MAIN_ROUTE`, the open floor lane and wall planes still look freshly finished. Use localized slab repairs, worn route paint, water trails, and service-area grime that follow plausible sources and traffic; keep the 2.8 m route readable.
3. **Give the worker nook one interrupted-shift cue.** `CAM_WORK_NOOK` has purposeful belongings, but the aligned papers and neat food stack feel orderly. A clearly abandoned or interrupted task state would better match the brief without adding arbitrary clutter.
4. **Repair the two technical findings before carrying those films forward.** Reverse the 16 north-wall stain-sheet faces to match the room-facing wall normal. Conform the three PV corrosion strips to the evaluated vessel surface at their intended offset. The formal PASS did not detect either issue.

## Technical evidence limits

`validation_R16.json` samples five rays at each practical aperture and reports no obstruction; 104 of 105 samples hit no object within the 0.15 m ray distance and only one sample is tagged as a task receiver. This supports clear apertures but does not establish task-plane illumination or control legibility. The validator itself limits its support and intersection checks and does not certify exhaustive self-intersection, buried volume, runtime collision, or fluid behavior. The independent technical findings above are from `production/critics/technical_R16.md`; no cold-start rebuild result was present at review time.
