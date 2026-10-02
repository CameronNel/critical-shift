# Luna independent full-corridor review — F15ci

## Decision

**F15ci does not clear the strict visual threshold.** The newly added bench lead ends in a smooth pale sphere that reads as a placeholder bead rather than a fabricated electrical connector. This is a localized defect, but it is plainly visible in the dedicated P01 closeup and falls short of the spawn craftsmanship reference. Modeling/fabrication, professional finish/contact, spawn parity and the staging/bench/cask/utilities area score 98; the strict bar is greater than 98 in every row.

I opened all 19 F15ci full views at 1280×853, the separate closed freight-leaf diagnostic, all four actual spawn craft references, all five manifest-listed PR54 atmosphere references, and the four native-lit detail closeups P01–P04. I independently checked all 24 F15ci PNG hashes against their render manifests; dimensions and render settings agree at 1280×853, 32 samples. The archived native SHA-256 `07dbbfd9153b0e732a31ce22a0342eff9dce33111f04b4af091ff55bc2a8b61b` matches the selected module, archived native, build manifest, cold record and all render manifests. Cold validation is PASS with zero failures. I verified all seven frozen recipe input hashes against source commit `0ad9008f316c3f1f52ac8a2ead2cded5842afa14` and the F15 build manifest. The current working copy of `fuel_details.py` has since advanced for F16; it is not used as evidence for F15.

The actual reworked spawn is the craftsmanship reference (100), not a palette target. It establishes attached, fully formed hardware, clear use, controlled practical light and finished contacts. PR54 is atmosphere guidance only: its dark green/amber pools, red alerts and worn workspaces inform mood, not the corridor's construction bar. F15 retains the protected fuel/service-corridor use and its dark, eerie look.

## Seven-category scores

| Category | F15ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` preserve the marked central travel path and staging-to-process sequence beneath dark intervals. `C05–C08` separate the east service turn, reactor threshold, bypass and clean branch. `E01–E03` keep waste, clean and freight thresholds recognizable. Floor damage stays visibly bounded around the route. |
| Modeling and fabrication detail | 98 | `D01–D06` show a supported cask carrier, bench, gauges, gate hardware and recess equipment. `P02` resolves a gasketed, fastened junction enclosure with glands; `P03` resolves the backed intercom and cable; `P04` shows a framed recessed grate. In `P01`, however, the loose lead's terminal is only a smooth pale sphere with no visible connector shell, grip, contacts or strain sleeve. |
| Materials and surfacing | 99 | `C03/C04` and `C07` show localized chipped floor edges, retained fragments and roof wear; `C08/E02` maintain the cooler, cleaner tile identity. Painted steel, enamel, tile, rubber, paper, timber and metal fittings remain distinct under the authored low light. The lead-end defect is a missing fabricated form, not a broader material-response failure. |
| Lighting | 99 | `C01/C03/C05` use localized work pools and restrained red warnings against intentional dark intervals. `C08/E02` remain cooler; `D03/D06` isolate practical utility tasks. Shadows preserve silhouettes and do not hide the new intercom or drain in their dedicated proofs. |
| Environmental storytelling and asset diversity | 99 | `C01/C03` show transfer and bench work; `D01` identifies the FC-017 carrier; `D03` distinguishes the AIR/07 manifold and chained bleed cap; `D06/C07` show the CHECK B tag/tamper seal; `P03` adds a usable reactor call point; `P04` gives the plant-side floor a functional strainer. |
| Professional finish and contact appearance | 98 | Most additions appear attached and supported: the bench cable is retained along the wall, junction glands enter the enclosure, the intercom sits between jamb and interlock console, and the strainer is recessed flush with its tile border. The exposed pale bead at the free end in `P01` interrupts that finish and reads as unfinished hardware. |
| Visual parity with spawn | 98 | Overall composition, practical lighting and industrial fabrication approach the spawn reference while retaining the fuel corridor's distinct service palette and rundown mood. The unformed terminal in `P01` is a visible departure from spawn's fully resolved small-object contacts and keeps parity below the strict bar. |

Modeling/fabrication, professional finish/contact and visual parity do not exceed 98.

## Nine-area scores

| Area | F15ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` show the cart-check station, refinery approach, transfer equipment and marked route. Worn roof and floor areas remain at the edges of the central travel path. |
| Staging / bench / cask / utilities | 98 | `D01` shows the tagged vessel on its wheeled carrier; `D02` shows the bench and tool storage; `D03` shows the AIR/07 panel, pointer gauge and chained bleed cap. `P01` makes the flaw explicit: the retained wall lead ends in a smooth pale spherical cap without recognizable connector construction. The outlet and wall route are otherwise legible. |
| Freight gate | 99 | `D05` resolves the freight mechanism and leaf construction. Full `E03` shows the open passage with its leaves parked; the separate closed diagnostic shows the freight leaves seated. The closed diagnostic is a static pose check. |
| East turn | 99 | `C05` keeps the reactor return and waste handoff distinct with route markings and red alerts. `P02` provides a clearer view of the new process junction than the deliberately dark full-view wall. |
| Delivery / waste | 99 | `E01/C05` show the waste approach, container, arrival/receipt station and handoff fixtures in a recognizable sequence. |
| Reactor adapter | 99 | `C06/D04` preserve the reactor portal, leaf hardware and warning spill. `P03` confirms the intercom is visible in its final position between the jamb and interlock console. |
| Bypass / recess | 99 | `C07/D06` keep the bypass route and CHECK B manifold distinct. The inspection tag is attached at the recess valve rather than becoming an independent notice cluster. |
| Plant header | 99 | `C10/P04` connect the plant doors, water service, hose reel and flow point; the floor strainer reads as a real open grate set into a recessed receiver. |
| North / clean corridor | 99 | `C08/E02` retain the cooler clean-zone identity, service cabinets and open aisle. The dark floor patch in `C08` is also present in F14ci's matching view, so it is not a new F15 collateral change. |

The staging/bench/cask/utilities area does not exceed 98.

## Findings and evidence limits

The actionable defect is confined to the loose end of the retained work lead: in `P01_BENCH_POWER.png`, at the right end of the cable loop, a pale smooth ball terminates the cable. It lacks a visible molded connector shell or grip, contacts and strain sleeve. At this dedicated close scale it reads as a placeholder rather than an intentionally capped electrical fitting. A connector shell with a grip/strain sleeve and a real retaining cradle would resolve the visible mismatch. This review does not waive the issue because it affects only one small detail.

The other inspected new details are supported by the pixels: `P02_PROCESS_JUNCTION.png` shows the fastened enclosure and gland entries; `P03_REACTOR_INTERCOM.png` shows a visible backed housing, perforated speaker, guarded call button and cable; `P04_FLOOR_STRAINER.png` shows an open grate in a flush recessed frame. The AIR/07 chained cap and CHECK B tag are visible in `D03` and `D06`; I found no additional substantiated defect requiring a separate finding. No claim is made about Unity, whole-map integration, runtime performance or continuous animation.

**F15ci still-image decision: FAIL.** The new details improve the corridor, but the P01 terminal flaw leaves four scored rows at 98. The report scores this frozen F15ci evidence only; a later repair and render cycle must be judged on its own pixels.
