# Luna independent full-corridor review — F12ci

## Decision

**F12ci clears the full-cycle visual threshold and is materially stable against F11ci.** The new render set shows the bounded waste upper closure reading continuously into its jamb and lining. The change is visible around the waste-side structure; the rest of the corridor retains its route clarity, service identity and finish. It remains a purpose-built freight and service corridor with the fixed outer shell and five closed external ports. Its palette and task use appropriately differ from spawn.

I opened all 19 published F12ci fixed views at 1280×853, the closed E03 freight-leaf diagnostic, and all four actual frozen spawn references at 1280×720. I rehashed the selected native and F12 checkpoint (`0a13ff2fe1eadc8608223bd40810285a375a02edacfdfac615263cffe5196f87`), current and archived build/cold records, all five recipe inputs, and full and closed image manifests. Current and archived records agree on the native and recipe (`88857cf4e2d345469647886034c77b0de3fd35ac56f1c95296acd8569b569093`); cold validation reports PASS with zero failures. Every F12 image hash matches its manifest. The 12 hosted group images opened earlier are byte-identical to their final published files. The F11 full and closed manifests also match their PNGs.

I compared decoded F11ci and F12ci pixels in all 19 corresponding fixed views and the closed diagnostic, with the same 1280×853 framing and matching camera transforms. F12 differs most visibly in `C05_EAST_TURN`, `C09_MATERIALS` and `E01_WASTE_APPROACH` around the corrected waste closure, with nearby background/shadow changes also visible in `D01_CARRIER_OPERATION`. The other views show little or no visible change. These differences are localized to the intended construction update and its light/shadow response; I found no collateral art regression. F12 uses a new recipe and native hash, so this is a visual stability comparison rather than an identical-build claim.

## Seven-category scores

| Category | F12ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` establish a clear route through the PROCESS / 02 extraction bay; `C05` distinguishes reactor return from waste handoff at the east turn; `C07`, `C08` and `E02` make the bypass and clean task legible. The updated waste closure joins the portal composition without consuming the route or obscuring the handoff. |
| Modeling and fabrication detail | 99 | `C06/D04` show layered reactor leaves, ports, handles and frame hardware; `D05` resolves the freight drive and track; `D01–D03` show the carrier, bench and utility fittings as assembled equipment. `C05/C09/E01` show the waste upper closure meeting the jamb/lining while retaining the framed door and handoff assembly. |
| Materials and surfacing | 99 | The set separates oxide and navy painted metal, pale formed panels, clean-zone ceramic, timber impact protection and worktops, rubber, paper, floor finishes and metal fittings. The closure repair maintains the existing painted-metal response and does not introduce a conspicuous material break. |
| Lighting | 99 | `C01–C03` use warm refinery practicals; `C07–C08/E02` shift the clean zone cooler; `C10` gives plant equipment warm task light; `D05–D06` preserve depth around mechanisms and recesses. The localized F12 shadow changes around the waste closure read as ordinary occlusion and do not flatten or obscure the task. |
| Environmental storytelling and asset diversity | 99 | `C01/C04` connect cart checks, paperwork and repair tools; `D01` stages the FC-017 carrier; `D02` shows an open service case and hung tools; `C05/E01` distinguish reactor return from waste receipt; `C08/E02` pair clean stock with linen work; `D06` identifies purge/check. The task cues fit this working corridor without copying spawn's preparation-room occupancy. |
| Professional finish and contact appearance | 99 | The frames meet wall and floor transitions, machinery sits in formed bays, the carrier rests on its chassis, and bench equipment sits on the work surface. In `C05/C09/E01`, the revised upper closure reads as a continuous junction with the portal lining. I found no visible unsupported prop, distracting intersection or unfinished edge. |
| Visual parity with spawn | 99 | The frozen spawn references establish the comparison through readable silhouettes, layered fabrication, distinct materials, practical warm/cool lighting, contact shadows and purposeful use. F12 reaches comparable care through industrial portals, process bays, service fixtures and task cues while keeping its own functional palette. |

All seven categories strictly exceed 98.

## Nine-area scores

| Area | F12ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01–C04` carry the freight route through the extraction enclosure to the refinery doors. The cart-check board, tools, fire station and service headers define the approach while leaving the central floor readable. |
| Staging / bench / cask / utilities | 99 | `D01` shows the FC-017 vessel held in saddles on a mobile chassis; `D02` gives the bench an open case, tools and work items; `D03` presents a readable gauge/valve/hose panel. The change produces no visible loss in these task assemblies. |
| Freight gate | 99 | `D05` resolves the motor, rail, mounts and drive housing; full `E03` shows the open passage with the leaves parked, and closed `E03` shows those leaves shut across the threshold. The closed diagnostic is a static pose check only. |
| East turn | 99 | `C05` keeps the reactor-return equipment and waste/handoff station distinct at the turn. The closure now spans the visible upper portal junction without obscuring either destination. |
| Delivery / waste | 99 | `E01/C05` show the WASTE / S03 portal, tagged B/017 container, arrival paperwork and seal/receipt point as a coherent receipt sequence. The corrected upper closure reads continuously around the waste opening. |
| Reactor adapter | 99 | `C06/D04` give the REACTOR / 02 portal paired leaves, layered panels, ports and operating hardware. `D04` includes the arrival/check point and impact protection while keeping portal scale clear. |
| Bypass / recess | 99 | `C07` marks CLEAN > at the turn; `D06` shows the PURGE / CHECK B gauge, valves, hose and tray within the bounded recess. The passage remains clear and task cues remain visible. |
| Plant header | 99 | `C10` combines PLANT / S01 doors, connected water line and valve, hose reel, FLOW / S01 gauge, wall protection and local practical in a plant-specific composition. |
| North / clean corridor | 99 | `C08/E02` establish the clean zone through washable surfaces, cool local light, stock storage, linen handling, WIPE / LOG cues and a clear aisle. The ceiling spine links the opposing task points. |

All nine areas strictly exceed 98.

## Findings and evidence limits

I found no substantiated visual defect in the F12ci corridor views. Broad quiet fields, repeated floor panels, natural contact shadows and harmless framing crops do not impair readability or finish; the spawn references also use quiet fields and repeated flooring. No extra wall dressing, additional room, or spawn-specific prop is required by the evidence.

I also opened the actual published assembled-map C03 render and compared it with F11ci and the earlier F12c candidate. The F11 bright slit at the far-right edge beside the waste upper closure is absent in F12ci; the closure now reads continuously against the adjacent jamb/lining. In the affected 12×53-pixel crop at x=945–956, y=225–277, F11 contains 203 pixels with all RGB channels above 200, while F12ci and F12c contain none. The remainder of the view appears materially unchanged. The F12ci render SHA256 (`7c2645794d3792d416147c517a32d416fcd525112f2183b9803a41a11a5f93f2`) matches `MAIN_LINK_VALIDATION.json`, which pairs it with the reviewed native SHA; the separate edge-ray record reports 30/30 hits in this former slit. This confirms the bounded integration sightline correction in the inspected view. With F11ci, F12ci forms the final two materially stable full visual cycles, with no collateral regression identified.

This review covers the corridor fixed views and one actual assembled-map C03 view. Validation records and the closed-leaf image add no art points; the closed freight diagnostic does not establish motion, collision or controller behavior. This report makes no whole-map, Unity or performance claim.

**Formal visual decision: PASS for the final two stable full visual cycles.** All seven categories and all nine areas exceed 98; the bounded waste-closure correction is visible in the fixed views and confirmed in the actual C03 integration render, with no art regression identified.
