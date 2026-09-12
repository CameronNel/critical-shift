# Luna F09 fixed-view review

Revision `final-F09` was reviewed from the complete 1440x960/32-sample image set in `production/renders/review/final-F09`. I inspected all ten mandatory views and all six diagnostic views directly as local pixels. This is an independent image review; the CPU technical, source replay, material replay, branch/handoff, and motion files are builder evidence and are not treated as a second Luna engineering signoff.

## Result

The F09 pixel pack clears the requested strict `>90` bar for every reviewed category and fixed view. The concrete F05 C08 cold failure remains preserved: its coplanar rear flange/washable-lower strip was a real construction defect, and F09's proud rear-flange/support-contact repair removes the visible failure in the reviewed C08 image. No new broad visual defect is visible in F09.

The fixed-view result is currently **CONDITIONALLY ACCEPTED**. The saved-artifact/reproducibility category and overall disposition remain held until the canonical F09 cold rerender and twelve player-eye approaches are complete and compared against the strict evidence thresholds. `scene_saved:false` in a render manifest means the renderer opened an already-saved file read-only; it does not mean the `.blend` was unsaved.

## Category scores

| Category | Score | Evidence and bounded limitation |
|---|---:|---|
| Specification coverage | 94 | Required doors, service station, staging, freight, workbench, carrier, and route identity are represented. Neighboring unassembled room fit remains out of scope. |
| Facility/process logic | 93 | F02/F01/S03 identity, service-air operation, waste/plant/clean sequencing, and staging workflow read coherently. Runtime controls are out of scope. |
| Human scale | 94 | Door, rail, workbench, carrier, valve, and service hardware read at believable worker scale. |
| Player circulation | 93 | Floor lines and arrows keep the route readable through the corridor and turns; final player-eye evidence is pending. |
| Freight/cart handling | 94 | The parked FC-07 carrier, marked bay, restraint hardware, and turn/approach framing support the intended handling story. |
| Maintenance access | 94 | Workbench, tools, grease, gloves, service-air regulator/gauge/hose, and access panels provide a complete maintenance read. |
| Interface consistency | 93 | Current refinery/reactor source and payload checks remain P07-consistent; exact neighboring assembly fit is not claimed. |
| Machinery construction | 95 | Carrier, straps, feet, rollers, motor, gate, air regulator, pipe joints, access panels, and fasteners read as assembled mechanisms. |
| Physical support/contact | 94 | F09 support audit passes all owned panels; motion replay reports only zero-depth contact/tangency events. This is bounded finite evidence, not a continuous engine collision proof. |
| Valorant shape language | 94 | Strong dark structural frame, ivory panels, orange safety accents, bevels, readable silhouettes, and restrained industrial props match the grounded Valorant direction. |
| Material separation/anti-plastic | 94 | Painted panel, dark steel, rubber, cloth, brushed metal, and carrier surfaces separate clearly in the direct images. |
| Lighting/readability | 93 | F05's washed-out reactor header is corrected in F09; D04 is legible, with practical fixtures producing useful contrast. |
| No-teal color discipline | 95 | Palette stays in ivory, charcoal, steel, orange, and restrained warm utility tones; no teal wash is visible. |
| Signage/numbering | 94 | Door labels, advance cues, floor arrows, bay marking, and service labels are readable. The wayfinding audit's transparent FIRST AID lid obstruction remains a bounded minor caveat. |
| Environmental storytelling | 93 | Tool wall, consumables, check tags, carrier restraint, service-air hardware, warning placards, and access wear support the working facility story. |
| Camera coverage | 94 | All ten mandatory and six diagnostic purposes are covered with useful entry, route, reverse, thresholds, material, machinery, utility, and recess views. |
| Saved-artifact/source/dependency reproducibility | 92 (conditional) | F09 SHA, source replay, material/UV/packed-texture replay, and branch/handoff evidence agree. Canonical cold16 and twelve player-eye comparisons are still required for unconditional approval. |

## Fixed views

| View | Score | Direct pixel finding |
|---|---:|---|
| C01_ENTRY | 94 | Clear service/bypass and F02/reactor identity, freight arrow, trolley bay, and readable route depth. |
| C02_PRIMARY_ROUTE | 94 | S03 waste and F02 reactor boards, floor turn arrow, and passage margins read cleanly. |
| C03_HERO | 92 | Strong staging/workbench/carrier/service composition; the incidental FG01/freight header is cropped by the camera frame but the intended staging content remains readable. |
| C04_REVERSE | 94 | Refinery doors and sign are clear, centered, and approached through a believable corridor. |
| C05_EAST_TURN | 94 | Waste turn, advance sign, panel construction, and floor line are legible without the earlier black floor artifact. |
| C06_REACTOR_THRESHOLD | 95 | Close threshold view clearly shows F02/reactor identity, bolted access panels, contact wear, handles, and lower protection. |
| C07_BYPASS | 94 | S01/plant overhead cue, S02/clean board, arrow, and service electrical panel read at the turn. |
| C08_SERVICE_JUNCTION | 94 | S02/clean cue, orange floor line, support bays, and corrected rear-wall construction read cleanly. |
| C09_MATERIALS | 95 | Carrier shell, orange straps, rings, clamps, feet, rails, wheels, bay border, and labels provide strong material/mechanical evidence. |
| C10_PLANT_HEADER | 95 | S01/plant header and paired doors are centered, highly legible, and supported by a quiet approach. |
| D01_CARRIER_OPERATION | 95 | Detailed carrier supports, brakes, wheels, straps, rings, and restraint labels read as a coherent working assembly. |
| D02_WORKBENCH | 93 | Tools, gloves, grease, case, shelf, and bench construction are clear; the upper housekeeping text is incidentally cropped by the diagnostic framing. |
| D03_UTILITY | 95 | Service-air regulator, gauge, valve, hose, pipe elbows, supports, and labels are all legible. |
| D04_REACTOR_WIDE | 95 | Corrected near-black header is legible and the complete reactor threshold composition is readable. |
| D05_GATE_MECHANISM | 93 | Motor, bracket, warning plate, transmission housing, and lower track read sharply; the large lower sign is intentionally incidental and clipped by the close mechanism framing. |
| D06_SERVICE_RECESS | 95 | Service-air recess is centered with readable title, complete pipe/regulator/gauge/hose assembly, and convincing wall framing. |

## Historical and pending evidence

F00 was rejected for the black floor overlap, foreground competition, missing/hidden route cues, weak reactor header, sparse door leaves, and motor-light dominance. F04 was rejected for the washed-out reactor header. F05 was held after canonical cold C08 exceeded the hard pixel threshold; source rays located a real coplanar rear-flange/washable-lower construction condition. F06, F07, and F08 remain recorded as failed/partial engineering candidates. F09 is the first current candidate with the corrected support placements and a complete direct fixed-view image pack.

The in-progress F09 canonical cold pack has now exposed a second hard numeric exception in C07: 148 pixels over the max2/255 threshold (max31) at the tiny orange FIRST AID cross on the right wall. Direct F09/cold inspection shows the cross remains visually identical at scene scale, but source/ray diagnosis identifies coplanar `cross_v` and `cross_h` surfaces. This is retained as a real reproducibility/construction evidence failure, not waived as generic renderer noise; F10 is the builder's bounded correction candidate.

Unconditional approval requires a corrected canonical cold16 comparison and all twelve player-eye approach images. Runtime behavior, engine controller operation, and assembled neighboring scenes remain outside this section review.
