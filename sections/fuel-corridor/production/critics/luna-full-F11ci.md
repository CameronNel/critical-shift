# Luna independent full-corridor review — F11ci

## Decision

**F11ci clears the second materially stable full-cycle visual threshold.** The fuel corridor reads as a purpose-built freight and service workplace: the route stays legible, the separate process tasks have specific visual identities, and the passage keeps the fixed outer shell and closed external leaves. The art reaches the grounded stylized standard of the actual frozen spawn references through its own industrial palette and use. It does not need spawn's briefing or locker functions, additional rooms, or a different palette.

I opened all 19 published F11ci fixed views at 1280×853, the closed E03 freight-leaf diagnostic, and all four actual frozen spawn references at 1280×720. I rehashed the selected native and F11 checkpoint (`4de5ea95e03bd21d10e1771b926bbc63c3405dae6cd58d88a3d156bb9bdc2b65`), the current and archived build/cold records, the five recipe inputs, all full and closed image manifests, and the PNGs. The current and checkpoint build/cold records agree on the native and recipe (`1dbefb4c1d5dc85b33d2cc34f4619bb904b3e6c7f85264858503e2cb11af6311`); cold validation reports PASS with zero failures. Each image manifest matches the opened file. The 12 hosted images opened before publication are byte-identical to their final published counterparts.

As a stability check, I compared decoded F10ci and F11ci RGB pixels in all 19 matching full views and the closed diagnostic. The differences are visually negligible render variation: the largest mean absolute channel difference among the full views is 0.014 on an 8-bit scale, with fewer than 0.016% of pixels in any full view differing by more than 2 channel values. The two renders show no material or composition change. This comparison supports visual stability; the scores below come from my inspection of the actual F11ci pixels.

## Seven-category scores

| Category | F11ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` establish a long, unobstructed freight route into the formed extraction task; `C05` separates reactor return from waste handoff at the east turn; `C07`, `C08` and `E02` make the bypass and clean task legible. Quiet wall and floor fields leave space around the focal assemblies. |
| Modeling and fabrication detail | 99 | `C06` and `D04` show layered reactor leaves, pressure ports, handles and frame hardware; `D05` shows the freight drive, track and mounts; `D01–D03` resolve the carrier, bench and utility fittings as assembled work equipment. `C10` has a distinct plant baffle and connected header. |
| Materials and surfacing | 99 | The views distinguish navy and oxide painted metal, pale formed panels, ceramic clean-zone surfaces, timber impact protection and worktops, rubber, paper, floor finishes and metal fittings. Surface variation and wear remain selective. The fuel palette is restrained and functional, with separate warm refinery/plant and cooler clean-zone treatments. |
| Lighting | 99 | `C01–C03` use warm local refinery practicals; `C07–C08` and `E02` shift the clean zone cooler; `C10` gives the plant header warm task light; `D05–D06` retain readable recess depth and contact shadow. Light hierarchy is visible without making every field equally bright. |
| Environmental storytelling and asset diversity | 99 | `C01/C04` connect cart checks, paperwork and repair tools; `D01` stages the restrained FC-017 carrier; `D02` shows an open service case and hung tools; `C05/E01` give reactor return and waste receipt separate stations; `C08/E02` pair clean stock with linen wipe/log work; `D06` identifies the purge/check task. These cues suit corridor work rather than copying spawn occupancy. |
| Professional finish and contact appearance | 99 | Across the complete set, frames meet wall and floor transitions, machines sit in formed bays, the carrier is supported by its wheeled chassis, and bench equipment is placed on its work surface. `D04` shows the arrival/check assembly within the reactor approach; `D05` shows the drive mounted to its track structure. I found no visible unsupported prop, distracting intersection, or unfinished edge that warrants a deduction. |
| Visual parity with spawn | 99 | The frozen spawn images show readable silhouettes, layered construction, distinct material response, warm/cool practical lighting, contact shadows and purposeful human use. F11ci demonstrates comparable care through service bays, portals, equipment, material zoning and task cues. The palette and work functions appropriately differ. |

All seven categories strictly exceed 98.

## Nine-area scores

| Area | F11ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01–C04` carry the route through the PROCESS / 02 extraction enclosure to the refinery doors. The cart-check board, tools, fire station and service headers define the approach while preserving a clear central floor. |
| Staging / bench / cask / utilities | 99 | `D01` shows the FC-017 vessel held in saddles on a mobile chassis; `D02` gives the bench an open case, tools, small work items and lower storage; `D03` presents a readable gauge/valve/hose utility panel. The close views retain distinct fabrication and material identity. |
| Freight gate | 99 | `D05` resolves the motor, rail, mounts and drive housing; full `E03` shows the open passage with the leaves parked, while closed `E03` shows those leaves shut across the threshold. The diagnostic is a static pose check only. |
| East turn | 99 | `C05` turns cleanly between the reactor-return assembly and the separate waste/handoff station. Their distinct destinations remain readable at the junction without additional wall openings or filler. |
| Delivery / waste | 99 | `E01` and `C05` show the WASTE / S03 portal, tagged B/017 container, arrival paperwork, seal/receipt point and separate handoff surface as one task sequence. The framed view keeps the approach readable. |
| Reactor adapter | 99 | `C06` gives the REACTOR / 02 portal a specific paired-leaf profile, layered panels, ports and operating hardware. `D04` places the arrival/check point and impact protection beside it, in a view that keeps portal scale clear. |
| Bypass / recess | 99 | `C07` marks CLEAN > at the turn; `D06` shows the PURGE / CHECK B gauge, valves, hose and service tray within the bounded recess. The cues are visible and the passage remains clear. |
| Plant header | 99 | `C10` combines PLANT / S01 doors, a connected water line and valve, hose reel, FLOW / S01 gauge, wall protection and a local practical in a plant-specific composition. |
| North / clean corridor | 99 | `C08` and `E02` establish the clean zone with tiled/washable surfaces, a clear aisle, stock storage, linen handling and WIPE / LOG work. The ceiling spine and matching practicals link the opposing task points. |

All nine areas strictly exceed 98.

## Findings and evidence limits

I found no substantiated visual defect in the inspected views. Broad quiet fields, repeated floor panels, natural contact shadows and harmless framing crops are present but do not impair readability or finish; the spawn references also use quiet fields and repeated flooring. I have not inferred requirements for extra wall dressing, additional rooms, or spawn-specific props from those qualities.

In the actual assembled-map C03 render (`F11ci_complete_main_C03_HERO.png`), a narrow bright vertical sliver appears at the extreme right edge beside dark frame members near the upper process/waste wall. At this crop and resolution it reads more like an overbright seam/opening than a clearly designed optic or viewport; no glazing or optic surround is legible. The image alone cannot establish whether it is a wall/roof light leak, a lit adjacent surface, or another construction detail. This integration-only appearance does not alter the fixed-view corridor score; source-ray or construction evidence is needed to attribute it.

The opened images support visual art review only. Cold clearances and contact sampling add no art points. The closed freight diagnostic does not establish motion, collision or controller behavior. This review makes no Unity, gameplay, or performance claim.

**Formal visual decision: PASS for the second stable full-cycle threshold.** All seven categories and all nine areas exceed 98, and the F11ci pixels are materially stable against F10ci.
