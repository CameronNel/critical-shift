# Luna independent full-corridor review — F22ci

## Decision

**F22ci clears the requested still-image gate in the dark, eerie, rundown fuel-corridor mood.** I independently score all seven categories and all nine areas at 99 against the actual reworked spawn craft references (100). I found no substantiated remaining art defect in the reviewed fixed views. The formerly visible bright slot around the inset waste jamb is closed by the fitted return, and the other closed boundary portals show seated center and perimeter joints.

I opened all 19 F22ci full native views, the closed freight-leaf diagnostic and all four native-lit P01–P04 details; I also opened all 19 actual assembled-map views. Every native/detail PNG hash matches its hosted group/detail manifest and all 24 pair to native SHA-256 `2cd961279e0a357029ea9be70af38dd602eda61297055ed9971729e179ffb2cc`. Every actual-map PNG hash matches the incremental `main-F22ci/RENDER_MANIFEST.json`; its 19 rows carry that same native SHA and recipe `2af15cd9f6915334ed42bad8c53e73b49a18ef7ea043597b49d59c2041e31e19`. The archived F22 native, F22 build manifest and F22 cold record also carry that native and recipe; cold is PASS with zero failures. Native fixed views are 1280×853/32 samples; assembled-map views are 960×640/32 samples. The selected module had advanced to F23 by the time I completed the map review, so I used the archived F22 pair and did not treat the F23 source/native as F22 evidence.

I reopened the four actual spawn reference images for the craft bar and the five latest PR54 reactor references for mood only. Spawn sets the bar for readable construction, attached hardware, material response, practical lighting and clean contacts; its brighter palette and room functions are not targets. PR54 guides the low-key, distressed atmosphere only. The fuel corridor retains its own freight/service identity and protected outer boundary.

## Seven-category scores

| Category | F22ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` connect entry, staging and refinery with visible direction marks; `C05–C08` distinguish the east turn, reactor threshold, bypass and clean branch. `C02`, `C07` and `E01–E03` keep the floor route readable through dark intervals. The C02 main-map view shows a dark process jamb, not the narrow bright strip suggested by its standalone native view. |
| Modeling and fabrication detail | 99 | `D01` grounds the cask on its carrier; `D02/P01` show the bench, hung tools, retained power lead, fabricated connector and cradle; `D03/D06` show the valve assemblies; D03’s gauge face is subdued at map scale, though its ticks and pointer resolve in the native closeup. `D05` retains the motor feet and rail supports, while `P04` shows a flush, fastened strainer. The folded return around the waste jamb closes the prior exterior sightline. |
| Materials and surfacing | 99 | `C03/C04` show chipped tile margins and layered roof damage; `C05/C07` distinguish oxide and navy service finishes, and `C08/E02` retain a cooler clean-zone identity. Enamel, metal, rubber, tile, timber, paper and hardware respond differently under the practical pools. The brighter edge around the carrier's rear wall panel in `C09` reads as a fitted access-panel boundary, not a gap. |
| Lighting | 99 | Actual-map `C01/C03/C05/C08` show task pools tied to visible fixtures with darker intervals retained. The broad unmotivated wash is absent; red alarm spill stays localized. `C04`'s bright door-pane highlight and `C06/C10`'s bright portal panes are bounded by their glazing frames, while the blue glimpse in `D04` is confined to the authored roof opening. Critical routes and controls remain readable. |
| Environmental storytelling and asset diversity | 99 | `D01` identifies the FC-017 cask; `D02` carries tools, gloves, notes and connected bench power; `D03` labels the AIR/07 manifold; `D06` pairs the CHECK B controls with the purge tray. `E01` presents arrivals and seal/receipt work, `P03` adds the reactor call point, and `P04` adds the plant strainer without changing the corridor's service role. |
| Professional finish and contact appearance | 99 | `D01/C09` show cask saddles, deck, legs and wheels in contact; `D05` shows the motor feet seated on the rail. `P01–P03` show retained or mounted connections, and `P04` sits within its recessed frame. Main-map `C05` no longer exposes the exterior beside the inset waste leaf; `E01/E02/C10` show fitted center overlaps without bright slits. |
| Visual parity with spawn | 99 | Across the reviewed views, the construction reads with the spawn references' clarity and attachment quality: controls remain legible, supports touch their bases, materials separate under low light, and practicals shape rather than flatten the scene. The corridor keeps its own palette, damage and freight/service function. |

## Nine-area scores

| Area | F22ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` show cart-check, transfer and refinery identities, ceiling damage, tile wear and forward arrows. The door-pane highlight in `C04` stays confined to its window. |
| Staging / bench / cask / utilities | 99 | `D01–D03` show the labeled cask and trolley, working bench, connected lead and AIR/07 manifold. The D03 dial is low-contrast in the map proxy, but its markings and pointer resolve in the full native closeup; the AIR/07 label and valve handles remain legible. `P01` confirms the retained connector/cradle; tool and tabletop items stay grounded. |
| Freight gate | 99 | `D05` shows the supported drive and rail; full `E03` shows the open passage with the leaves parked, while the separate closed diagnostic shows a static closed pose. Both preserve the threshold and route. |
| East turn | 99 | `C05` separates the reactor return from the waste handoff, with red warnings local to the turn. The repaired folded jamb return blocks the former bright exterior slot without obscuring the route or controls. |
| Delivery / waste | 99 | `E01` keeps WASTE/S03, the arrivals board, container and seal/receipt station identifiable. The closed waste pair has an unbroken center overlap in this actual-map view. |
| Reactor adapter | 99 | `C06/D04` show the labeled reactor threshold, paired leaves, inspection windows, red alert and arrival/check station; `P03` shows a mounted, connected call point. The pane highlights remain within the glazing. |
| Bypass / recess | 99 | `C07/D06` distinguish the clean bypass from the CHECK B manifold and purge tray; valves, tag and attached lines remain readable within the local task pool. |
| Plant header | 99 | `C10` shows the WATER header, hose reel, FLOW/S01 panel and closed paired portal; `P04` shows the recessed open strainer and its fasteners. |
| North / clean corridor | 99 | `C08/E02` retain the cooler clean-zone tiles, cabinets and signage. The closed E02 portal has a continuous center stile and a legible CLEAN/S02 identity. |

No category or area depends on cold, geometry-budget or ray-check points. I found no reason to score below the strict threshold in this F22 still set.

## Evidence limits

This review covers only the supplied fixed views, closed-leaf diagnostic and detail views. The E03 full view shows an open freight passage; its separate diagnostic is a static closed pose check. The D03 gauge face is a bounded readability limitation: its ticks and pointer require closer inspection at map scale, but resolve in the native detail; the surrounding manifold remains readily identifiable. I do not find that limitation actionable or severe enough to lower the staging/utilities scores. The evidence does not establish Unity integration, runtime performance or continuous flicker cadence. The F23 actual-map review is still pending, so this report makes no F22/F23 material-stability or final-pair claim.
