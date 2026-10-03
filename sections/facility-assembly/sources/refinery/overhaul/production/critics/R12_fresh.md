# Independent fresh review — R12

**Reviewer:** GPT-6 Luna, fresh-context visual critic

**Evidence reviewed:** Current R12 fixed renders (11/11; each inspected individually and in a 3-column, 4-row contact sheet), current refinery brief/rubric/camera specification, Critical Shift art direction, the two specified Spawn-room validation renders, R12 manifest, `validation_R12.json`, and `technical_R12.md`. No prior scores or visual reviews were used.

**Render setup:** Blender 5.2.0 LTS, CPU Cycles, 24 samples, 960×540, seed 73, world strength 0.

**Decision:** **Does not meet the 99/100-per-category threshold.** The weighted score is **96.85/100**. No automatic visual or technical veto was observed in the reviewed evidence. The full acceptance gate remains unmet.

| Category | Weight | Score | Weighted points |
|---|---:|---:|---:|
| Route readability | 20% | 98 | 19.60 |
| Art direction and silhouettes | 20% | 97 | 19.40 |
| Hero process equipment | 15% | 97 | 14.55 |
| Materials and anti-plastic quality | 15% | 96 | 14.40 |
| Practical lighting and atmosphere | 10% | 98 | 9.80 |
| Purposeful dressing and worker storytelling | 10% | 96 | 9.60 |
| Technical cleanliness and reproducibility | 10% | 95 | 9.50 |
| **Weighted overall** | **100%** |  | **96.85** |

## Assessment

The R12 overhaul reads as a working refinery from the entry and route cameras. The warm concrete, muted green protection, charcoal frames and oxide-orange machines make a consistent hierarchy. Machine roles distinguish through silhouettes and process fittings, and the broad clear aisle remains easy to parse. `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_REVERSE` and `CAM_MINE_TO_CRUSHER` establish circulation and the receiving-to-crusher handoff. I did not count the large dark module openings in `CAM_REVERSE` or `CAM_DISPATCH` as missing set dressing: they read as adjacent-map connections. The intentionally clear aisle is also doing its job.

The refinement is a meaningful step toward the stated stylized semi-real target. The processor vessel has a recognisable pressure body, domed cap, band, gauges, clamped access hatch, valves and connected machinery; the crusher and sorting/press stations have more specific construction than a blockout. `CAM_PINCH` and `CAM_MATERIAL` show folded-panel edges, fasteners, guarded controls and differentiated painted metal, glass and steel. These broad forms carry the scene at gameplay distance. Some large machine masses still resolve as simple panels on boxes or cylinders, and several close transitions need another fabrication pass before they match the Spawn reference's finish. The Spawn renders have more convincing prop contact and a denser, more naturally used preparation area; R12's industrial palette and form language are coherent, but its worker evidence is concentrated in one nook.

Materials stay restrained and generally matte-to-semi-matte. Orange enamel and green painted steel remain legible as separate families, the clear guard reads as glass, and bright metal is reserved for the hatch, rails, shafts and fittings. Highlights remain controlled overall; this is not a generic glossy or noisy treatment. In `CAM_HERO_DETAIL` and `CAM_PROCESS`, however, the small left riser shows a conspicuous pale angular wedge/transition, and the larger vessel has abrupt patches along its curved body. These read as construction or shading defects rather than authored wear. At close range, the local surface continuity reduces confidence in the otherwise successful material separation.

The practical-light setup is a strong part of the candidate. The current validation records world strength zero, 21 in-room AREA lights bound near visible fixture lenses, and no route obstructions. The renders show their warm pools and falloff, especially on the rear wall and work surfaces; the dark secondary corners keep useful depth. The lighting is bright enough to read machine controls and aisle markings without a broad ambient wash. The checked technical evidence found no light ray blocked except the documented intended inspection-practical sample.

`CAM_WORK_NOOK` gives the clearest human story: a shift board, radio, mug and food on a small timber table beside the work area. The objects have plausible roles and make a useful pause in the otherwise process-heavy room. In the wider cameras, most other stations remain very orderly, with limited signs of active maintenance or individual use. This restraint is preferable to arbitrary clutter, but the brief specifically asks for small worker details distributed as purposeful clusters. The vignette currently carries nearly all of that requirement by itself.

Technical evidence is unusually concrete and supports a high, but not passing, score: the candidate hash matches the build and validation records; all 29 protected interfaces are unchanged; world strength is 0; all 21 checked lights are in-room; route obstruction and issue lists are empty; stored winding checks pass for 935 closed meshes; and 157 new contact entries plus 133 inherited support entries pass. The audit also found two material qualifications that prevent a 99-level score: both hose compression bands have 4 mm radial interference with the hose (60 hose vertices inside each band and 142/144 overlap pairs), and the transition from the 110 mm capped incoming line to the new 68.5 mm coupling bore does not demonstrate an open continuous path. The external fittings are clear for the hose and align to their supports, but that does not settle the separate reducer transition. The review evidence is bounded: it does not certify runtime collision, performance, exhaustive intersections or fluid behavior. The requested four correction cycles, final two stable cycles and fresh-process acceptance sequence are also not established by the reviewed render/audit packet.

## Most consequential remaining corrections

1. **Close the visible vessel/riser surface defects.** In `CAM_PROCESS` and `CAM_HERO_DETAIL`, repair the pale triangular patch and abrupt tonal/surface transitions on the small left riser and the curved hero vessel. Recheck silhouette and normals/material continuity in the fixed detail and process cameras under the final practical lights. Removing the wedge and making the vessel body read as continuous fabricated metal would close the clearest visible polish gap.
2. **Resolve the hose-band fit.** `technical_R12.md` measures a 63 mm band bore against a 67 mm hose, producing 4 mm radial interference and 142/144 surface-overlap pairs. Increase the band inner radius to the documented close-fit range (approximately 66.5 mm for 0.5 mm squeeze at a 72.5 mm major radius with the same section), keep the band seated on the spline, and rerun the evaluated-geometry check. Confirm in `CAM_HERO_DETAIL` that bands look like external compression hardware rather than buried rings.
3. **Show a continuous processor reducer transition.** The audit measures the inherited capped line at 110 mm radius and the new coupling bore at 68.5 mm; the line stops at the coupling face. If this connection is meant to carry the process through, model a visible reducer and annular line end so the opening reads continuously. Update a bounded check to cover the line-to-coupling transition, then inspect it in `CAM_HERO_DETAIL` and `CAM_PROCESS`.
4. **Distribute worker use evidence in a few more station clusters.** `CAM_WORK_NOOK` is a readable human vignette, while `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_ASSEMBLY` and `CAM_DISPATCH` mostly show clean equipment and controls. Add only a few role-specific, supported maintenance/work items where they explain an operation (for example a service record/tool at the crusher or a sample-handling aid at inspection), leaving the route and equipment silhouettes clear. The Spawn comparison provides the target for lived-in prop grouping and believable contact.
5. **Finish the close fabrication pass on prominent folded parts.** The audit confirms checked sheet edges use a sharp 1 mm single-segment bevel. In `CAM_MATERIAL` and `CAM_PINCH`, some panel-to-frame transitions still look like simplified slabs, and small controls/labels compete with the underlying panel geometry. Refine folds, returns and transitions on the most visible press/reader panels while preserving the sharp edge treatment, then check that the machine silhouette remains the first read at gameplay distance.

## Veto and gate record

No automatic veto is supported by these pixels and technical checks: there is no dominant blockout primitive language, generic glossy response, photoreal surface noise, arbitrary clutter, floating visible dressing, blocked aisle, changed protected interface, unmotivated illumination or nonzero world illumination. The interface openings and clear route were treated according to the brief. This is a sub-threshold review, not acceptance. The score gate fails in all categories because none reaches 99; the weighted gate fails at 96.85. Correction-cycle stability and the complete fresh-process acceptance requirement remain unverified by this bounded review.
