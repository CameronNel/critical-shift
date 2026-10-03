# Refinery overhaul R08 — fresh review

**Result: not accepted.** R08 has clearer process cues, a clean central circulation lane, a stronger set of machine bases and enclosures, and a convincing work nook. The vessel's visible shell distortion, repeated operator-console construction, uneven stage readability, limited use evidence outside the nook, and unresolved connected-map presentation keep it below the owner's requirement of at least 99 in every category and overall.

## Evidence reviewed

- The completed R08 manifest and all eleven fixed-camera renders: `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_PROCESS`, `CAM_REVERSE`, `CAM_PINCH`, `CAM_MATERIAL`, `CAM_ASSEMBLY`, `CAM_DISPATCH`, `CAM_MINE_TO_CRUSHER`, `CAM_WORK_NOOK`, and `CAM_HERO_DETAIL`.
- The actual Spawn reference pixels `VALIDATE_Hero_A.png` and `VALIDATE_Spawn.png`.
- `validation_R08.json` for bounded technical evidence.
- The read-only checkpoint audit in `technical_R08.md` for measured support gaps, disconnected dressing details, and the source modifier-order warning.

All scores and findings apply to R08 as rendered and audited. Any planned R09 repairs are not credited here.
- The connected-context `.blend`/manifest are present, but no rendered connected-context camera pixels were present in the evidence reviewed. I do not credit those incomplete views or use them to claim the port backgrounds are resolved.

## Scores

| Category | Score | Weight | Weighted points | Pixel/evidence basis |
|---|---:|---:|---:|---|
| Route readability | 94 | 20% | 18.80 | The central aisle and keep-clear marks read clearly in `CAM_ENTRY` and `CAM_MAIN_ROUTE`; the receiving conveyor and later belt arrows help establish travel direction in `CAM_MINE_TO_CRUSHER` and `CAM_PINCH`. The reverse and dispatch views still terminate in black openings because this module is shown without adjacent map space. |
| Art direction and silhouettes | 89 | 20% | 17.80 | The orange/green/charcoal process palette, overhead service rhythm, and broad machinery silhouettes feel intentionally art-directed. `CAM_ENTRY`, `CAM_ASSEMBLY`, and `CAM_MATERIAL` still show repeated flat-faced panels, square supports, and box-built station bodies. The large process vessels also read less cleanly than the Spawn room's distinct locker, chamber, and doorway construction. |
| Hero process equipment | 86 | 15% | 12.90 | `CAM_PROCESS` and `CAM_HERO_DETAIL` show useful gauges, hatch construction, pipe connections, a task indicator, and a service card. The orange vessel shell has broad irregular dents/creases that read as an unintended form/shading problem, while the full line remains only partly legible from broad views. |
| Materials and anti-plastic quality | 90 | 15% | 13.50 | Concrete, painted machine colors, glass, dark steel, and metal piping separate well in `CAM_MATERIAL` and `CAM_ASSEMBLY`. Large orange shells remain unusually smooth and slightly molded in close views; the maintained room has little localized surface variation or contact wear to reinforce its industrial material response. |
| Practical lighting and atmosphere | 91 | 10% | 9.10 | Ceiling pendants now visibly hang from structure and produce contact shadows in `CAM_ENTRY` and `CAM_MAIN_ROUTE`; service areas retain darker undersides. The room remains broadly warm and evenly bright, with modest separation among stages. Validator evidence supports the physical-light constraint, but the pixels do not yet reach Spawn's stronger contrast and focal hierarchy. |
| Purposeful dressing and worker storytelling | 88 | 10% | 8.80 | `CAM_WORK_NOOK` has a purposeful cluster of shift notes, radio, mug, and food; `CAM_HERO_DETAIL` adds a service card at the vessel. Outside those focal areas, the room is clean equipment presentation with few visible traces of sampling, adjustment, or repair. Fine captions on several controls remain hard to read at the review resolution. |
| Technical cleanliness and reproducibility | 90 | 10% | 9.00 | The validator's counts are strong, but `technical_R08.md` measured a 1 mm worktop-to-rib gap, a 1 mm cabinet-sheet stand-off, a 1 mm unsecured diffuser gap with an incomplete stay/support record, a tag wire disconnected by 0.13/0.63 mm, and tag text 1.5–2.3 mm off the paper. The support registry can pass without measuring the actual worktop/source face. The Boolean is applied after bevel/weighted-normal setup and emits a modifier-order warning, though the baked cut geometry is sound. These are localized, real defects that the automated PASS does not certify away. |
| **Weighted total** |  | **100%** | **89.90 / 100** | **Below the required 99.00.** |

## Veto review

**Automatic visual vetoes: none observed in the complete R08 fixed views.** The room is not dominated by primitives, glossy materials, flat light, random clutter, or route blockage. Technical validation reports no light/interface/route veto: all lights are in-room and bound to physical fixtures, world strength is zero, protected changes are empty, and the measured route has no obstruction.

The separate technical audit does expose localized support/contact defects in small items and one work surface. They do not dominate the evaluated pixels, so I do not call them a scene-wide floating-dressing veto; they remain unresolved technical acceptance defects and must be repaired. In particular, the diffuser has no complete support record, and the tag's wire does not connect to either endpoint.

The two large black areas in `CAM_REVERSE` and `CAM_DISPATCH` are open module ports. Because the candidate is intentionally a standalone additive module whose ports must connect to the map, these black fields are best classified as an **isolated-module context limitation**, not altered or defective room geometry. They remain a real presentation gap in the available pixels: without rendered neighboring map space, the views cannot establish how the opening reads in final context. The connected-context camera preview is incomplete and receives no credit here.

## Highest-impact defects to address

1. **The main vessel shell still looks dented or melted** — `CAM_HERO_DETAIL`, `CAM_PROCESS`. Irregular broad depressions cross otherwise smooth painted areas without corresponding seams or access features. Restore a controlled vessel profile; reserve shape changes for intentional welds, formed panels, and service hardware.
2. **Machine silhouettes still share a repeated console-and-post kit** — `CAM_ENTRY`, `CAM_MATERIAL`, `CAM_ASSEMBLY`, `CAM_PINCH`. Several mint panels use nearly identical faces and square supports on otherwise different stages. Design distinct, weight-bearing control housings and mounts tied to each station's operation.
3. **The complete material path is still hard to follow** — `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_DISPATCH`. The receiving-to-crusher belt and the `04 SORT` arrow help, but later process handoffs blend into a side-by-side equipment row. Give each stage an unmistakable input/output direction and silhouette that remains readable from the route cameras.
4. **Connected-map port presentation is unverified** — `CAM_REVERSE`, `CAM_DISPATCH`. These views show featureless black beyond the preserved openings. This is an isolated-module context limitation, not permission to close or move an interface. Render the actual adjoining map in these same views and assess the real threshold transition before deciding whether any room-side reveal or practical lighting still needs adjustment.
5. **Worker use is still concentrated in a single nook** — `CAM_WORK_NOOK`, `CAM_HERO_DETAIL`, `CAM_ASSEMBLY`. The nook reads well and the service card helps, but equipment elsewhere has few visible human-use cues and small panel labels blur at this distance. Add only a few relevant traces at work points—such as a sample jar/tag or a tool staged at maintenance—and strengthen essential caption size/value while preserving the open route and quiet wall areas.

## Technical evidence limits

`validation_R08.json` records 2,460 visible meshes and 279,870 evaluated triangles. All 130 new support contacts, 133 inherited support checks, and 905 closed-mesh winding/volume checks pass; `technical_R08.md` independently measured zero negative volumes across 908 closed authored meshes. Missing images and libraries are empty. The measured 1 mm support gaps and disconnected dressing details show why these are bounded checks rather than proof of every actual target contact, intersection, buried overlap, connected-map appearance, or runtime collision behavior. No source or scene files were changed for this review.
