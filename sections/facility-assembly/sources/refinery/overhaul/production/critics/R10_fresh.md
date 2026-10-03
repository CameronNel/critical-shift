# Independent visual review — refinery R10

**Review basis:** All eleven completed R10 fixed-view PNGs, the two requested Spawn-room polish references, the refinery owner brief and rubric, and the bounded R10 validation plus technical audit. This is a review of the current candidate, not a runtime-readiness certification.

## Scores

| Category | Score / 100 | Weighted contribution |
|---|---:|---:|
| Route readability | 97 | 19.40 / 20 |
| Art direction and silhouettes | 92 | 18.40 / 20 |
| Hero process equipment | 96 | 14.40 / 15 |
| Materials and anti-plastic quality | 89 | 13.35 / 15 |
| Practical lighting and atmosphere | 94 | 9.40 / 10 |
| Purposeful dressing and worker storytelling | 90 | 9.00 / 10 |
| Technical cleanliness and reproducibility | 98 | 9.80 / 10 |
| **Weighted total** |  | **93.75 / 100** |

The owner’s threshold is not met: no category reaches 99, and the weighted score is below 99. The visible pass is coherent and professionally art-directed, but the current images still show finish and construction details that matter at this threshold.

## Vetoes

**No automatic visual or objective veto observed in the reviewed evidence.** The route reads as open, forms are not dominated by primitive blockout construction, and practical fixtures are visible. Validation reports world strength 0, 21 AREA lights, no route obstructions, no issues, and no changed protected interfaces. Both dark ports are treated as preserved open module connections and are not scored as missing room geometry.

## Highest-impact visible defects

1. **The hero painted finishes still share a smooth, broad highlight response.** In `CAM_HERO_DETAIL` and `CAM_PROCESS`, the orange pressure vessel, its side vessel, and the green horizontal dryer/motor have broad soft highlights with limited visible roughness separation. The inspection press in `CAM_MATERIAL` has a similarly smooth orange base, green control cover, and grey table. This makes the objects feel more uniformly coated than their different manufactured materials suggest. Give painted enamel, dark structural steel, bare fittings, rubber and glass more distinct response; add restrained wear only around the vessel hatch clamps/handwheels, machine access points and press work surface.

2. **Several focal transitions remain rounded where the fabrication should read as folded, joined or guarded.** `CAM_MATERIAL` shows the inspection press as a stack of broad slabs: orange pedestal, grey work deck and yellow safety frame. `CAM_PINCH` shows the crusher/sorter interface with a large pale housing over the orange belt and dark support plates. Their edge radii and panel breaks are soft and similar, so the equipment reads more as smooth assembled forms than specific fabricated assemblies. Sharpen the sheet-metal returns, add a few clear panel reveals or folded lips, and differentiate cast/rolled corners from bent guards. Keep the current silhouettes and route clearance.

3. **Small control faces and machine labels lose clarity in the broad gameplay views.** In `CAM_ENTRY`, `CAM_MAIN_ROUTE` and `CAM_MINE_TO_CRUSHER`, the crusher and sorter panels are small pale/black plates dotted with controls; their text is not legible at that distance. `CAM_PROCESS` brings the belt control panel forward, but its labels remain crowded and the individual function groups do not read immediately. Strengthen the hierarchy of two or three primary controls per face with size, spacing and value grouping, and simplify subordinate marks. This is a legibility refinement, not a request for more labels or screens.

4. **The dark ceiling support and utility lines compete with equipment outlines in the entry and process compositions.** In `CAM_ENTRY`, the repeated black beam rhythm crosses above the crusher, vessel and dryer, while orange and grey runs occupy the same narrow band. In `CAM_PROCESS`, the overhead lines sit close to the vessel necks and rear ducts. Preserve the physical utility routing, but clarify which members are primary structure and which are services through spacing, mounting brackets and a quieter secondary line value. This should restore separation around machine tops without removing necessary infrastructure.

5. **The work nook’s human cues are purposeful but still read as a simple prop arrangement.** `CAM_WORK_NOOK` shows a radio, mug and food on a plain table beneath a mounted shift board, which gives a believable pause point. The tabletop objects have little contact shadow or interaction grouping, and the board’s papers are pale and generic at this distance. Tighten the grouping around the radio/mug, show more convincing contact and wear at the table’s front working edge, and make one existing notice visibly specific to the PV-05 maintenance or current shift. Retain the quiet wall around it.

## Camera findings

- **CAM_ENTRY:** Process stages are immediately differentiated by the receiving/conveyor equipment at left, orange vessel at center and green dryer at right. The foreground KEEP CLEAR aisle has generous negative space. Small panel text and the tight ceiling service band are the visible opportunities.
- **CAM_MAIN_ROUTE:** The route remains open in the foreground and the central vessel is an effective focal point. The right side has breathing room. Vessel/dryer finishes and the crusher-side control faces still need material and control hierarchy refinement.
- **CAM_PROCESS:** The pressure-vessel hatch, clamps, gauge, handwheels and connected process equipment form the strongest close operational read. The painted shell and connected green machine remain too smooth in their highlight response; the left control panel is harder to parse than the hero hatch.
- **CAM_REVERSE:** The empty central floor clearly communicates circulation. The worker utility cluster and receiving hopper are readable secondary masses. This composition supports the intentional negative space.
- **CAM_PINCH:** Conveyor/support relationships and sorter station are visible, but the crusher enclosure, belt side plates and sorter head are close together in silhouette. Clarify fabricated edge breaks and control hierarchy while retaining the specified clear passage.
- **CAM_MATERIAL:** The safety frame, press deck, cylinder and operator panel are readable as a work machine; the object still appears assembled from broad, smoothly edged layers. This is the clearest view for the finish and fabrication refinements above.
- **CAM_ASSEMBLY:** The inspection machine, line benches and dryer create a clear downstream work sequence. The pale console hanging over the orange bench is visually prominent but its function is not immediately clear; use its existing controls and panel shape to separate it from the neighboring work surface.
- **CAM_DISPATCH:** The trolley and sample cylinders add a convincing dispatch task. Their contact shadows are readable. Keep the bright cylinder tops and cabinet from competing with the more important inspection outputs through restrained value emphasis.
- **CAM_MINE_TO_CRUSHER:** Receiving material, feed conveyor and crusher read as a clear upstream sequence. The conveyor’s supports and black controls are legible but would benefit from stronger separation of primary controls and structural supports.
- **CAM_HERO_DETAIL:** Strong authored hatch vocabulary and scale cues. The broad orange body and adjacent side vessel show the smoothest material response; the hatch hardware has the best construction specificity and is a useful finish target for nearby components.
- **CAM_WORK_NOOK:** The board, radio, mug and food make a specific worker pause point while preserving wall negative space. Improve their contact and make one current notice readable as PV-05/shift-specific.

## Reference comparison and evidence limits

The requested Spawn polish images use strong value grouping, clear practical-light pools, and purpose-specific object clusters. R10 reaches a comparable level of composition and production clarity, especially in its process sequence and open route. Spawn’s Hero_A has a more immediately differentiated focal enclosure and stronger local light/material contrast; Spawn’s corridor has crisp doorway and wall-protection breaks. Refinery should carry those principles into its process equipment without copying Spawn assets or layout.

R10 manifest is complete and records 11 views at 960×540, Cycles CPU, 24 samples, seed 73 and world strength 0. The numerical validator reports 29 protected interfaces unchanged, 146/146 new contacts, 133/133 inherited support entries, 927/927 closed-mesh normals, 21 practical AREA lights, 105 aperture samples with only the documented inspection receiver hit, and no route obstructions. The read-only technical audit independently confirms the source/checkpoint/build/validation hash match and confirms the recorded hatch marks, ear defenders, reader support, crusher mouth, diffuser suspensions and process link. I therefore score technical cleanliness highly.

The validation explicitly does not certify exhaustive self-intersection, buried geometry or runtime collision. The folded crusher roof’s side/back seating is observed but has no explicit support registry entry. The aperture sampling covers five rays per fixture over 150 mm, not a complete beam volume. Runtime collision, performance and game-engine behavior were not part of this visual review.
