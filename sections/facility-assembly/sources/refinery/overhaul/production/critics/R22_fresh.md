# R22 fresh acceptance review

I opened all 11 R22 renders and compared them against the matching R21 views. I also inspected the Spawn hero and full-room references for construction and finish quality; they guide form separation and material control, not refinery brightness or mood. R22 and its independently rebuilt cold candidate both have complete 11-view manifests.

## Visual finding

R22 reads dark, gloomy and neglected while keeping the continuous floor route visible. The broader indoor residue and dulled floor lanes make the service path less orderly than R21. The existing task and threshold fixtures give the main work clusters useful separation; the six failed fixtures remain off. Pressure-vessel construction stays crisp in HERO_DETAIL, with its flange, gauge, fasteners, tags, valves and service pipework. The work nook still reads as an interrupted night shift through its leak sheet, gloves, cup, radio and tools.

The remaining high-impact visual weakness is separation of secondary equipment in the receiving/crusher and remote process areas. In MINE_TO_CRUSHER, the receiving hopper interior and adjacent controls still merge into deep shadow; in REVERSE and PROCESS, some support machinery reads mainly by silhouette. The floor route and visible portal frames remain clear. I did not treat black space beyond the open portals as a defect because the standalone room has no adjoining geometry there. The Spawn images retain stronger shape separation across secondary forms; R22 is close in modeled construction quality but loses some of that separation in these dark views.

Across R21→R22, fixed composition and camera framing stay intact. Pixel measurements show small but real changes in every view: mean absolute RGB differences range from 1.593 to 5.545 levels on a 0–255 scale. Average per-pixel RGB means rise in all views by 1.238–5.383 levels. The R22 floor wear and softer lane markings are visible causes of some of that change; the image mean is a descriptive measure, not a quality score or a claim about every local area.

| View | Mean RGB, R21 → R22 | Mean absolute RGB difference |
|---|---:|---:|
| CAM_ASSEMBLY | 13.019 → 16.012 | 3.269 |
| CAM_DISPATCH | 15.027 → 20.023 | 5.131 |
| CAM_ENTRY | 18.548 → 20.421 | 2.439 |
| CAM_HERO_DETAIL | 32.392 → 37.775 | 5.545 |
| CAM_MAIN_ROUTE | 24.788 → 27.925 | 3.582 |
| CAM_MATERIAL | 15.946 → 20.714 | 4.813 |
| CAM_MINE_TO_CRUSHER | 16.089 → 17.938 | 2.332 |
| CAM_PINCH | 23.412 → 24.650 | 1.593 |
| CAM_PROCESS | 28.430 → 32.114 | 3.916 |
| CAM_REVERSE | 16.287 → 18.349 | 2.388 |
| CAM_WORK_NOOK | 24.884 → 26.771 | 2.148 |

## Scores

| Category | Weight | Score | Basis |
|---|---:|---:|---|
| Route readability | 20% | 98 | The aisle and lane path remain visible and open; receiving/crusher support equipment is still difficult to distinguish in the dark views. |
| Art direction and silhouettes | 20% | 98 | The neglected, cold industrial direction is clear, with authored equipment silhouettes; some secondary forms lose separation in shadow. |
| Hero process equipment | 15% | 99 | Strong fabricated vessel, closure, pipe, valve and gauge detail, with visible wear and service tags. |
| Materials and anti-plastic quality | 15% | 98 | R22 adds restrained indoor residue and floor wear while retaining varied concrete, enamel, oxide and metal response; a few broad views still hide surface distinctions. |
| Practical lighting and atmosphere | 10% | 99 | Isolated practical pools support the requested gloom. Current numerical and technical evidence confirms zero world strength, 15 live sources attached to physical fixtures and six failed sources at zero. |
| Purposeful dressing and worker story | 10% | 99 | The dedicated WORK_NOOK view shows a purposeful interrupted-shift cluster: leak and night-shift records, gloves, cup, radio and tools. |
| Technical cleanliness and reproducibility | 10% | 100 | Validation and cold validation PASS; 418,610 evaluated triangles, 29 protected interfaces unchanged, zero world strength and no route obstructions. Independent technical audit and full cold fingerprints/render comparison agree. |

Weighted score: **98.55/100**. No critical veto observed. R22 is below the required 99 in three categories and below 99 weighted overall, so it is not accepted.

## Technical and cold evidence

`validation_R22.json` and `validation_R22_cold.json` both report PASS, with 418,610 visible evaluated triangles, world strength 0 and no issues. The independent audit in `technical_R22.md` verifies eight joined glove-finger roots, all 108 schematic mark vertices seated 20.027 μm above the paper face, indoor-only residue assignments, unchanged camera/light matrices, and 15 working fixture-bound sources plus six zero-energy failed fixtures. It reports no runtime certification.

The cold checkpoint and rebuild fingerprints have equal object maps, equal material maps and equal scene-state hashes; both report their source unchanged. Formal `comparison_R22.json` and `pixel_comparison_R22.json` report PASS, no changed objects or materials, identical scene state, equal render settings, and pixel-identical results for all 11 views with zero maximum channel delta. This closes the current cold visual reproduction check.

R21→R22 is a substantive mood/readability revision, so it does not establish the required final two stable correction cycles. No runtime certification was performed.
