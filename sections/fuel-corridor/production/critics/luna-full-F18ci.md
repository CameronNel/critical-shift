# Luna independent full-corridor review — F18ci

## Decision

**F18ci does not clear the requested strict greater-than-98 still-image threshold.** The authored lighting repair works: actual-map views no longer show the broad floor and service-wall wash, and visible practicals create bounded work pools while the central route remains readable. However, the closed double-door portals show a repeated bright center-line gap in the actual assembled-map views. The slit is most conspicuous in `E01_WASTE_APPROACH.png` and `E02_CLEAN_APPROACH.png`, and is subtler in `C10_PLANT_HEADER.png`. At normal view it reads as a light gap through closed leaves, rather than a dark meeting joint. This is a concrete fabrication/finish defect even if the adjoining-space light path is physically plausible.

The repair should close that visible path with a dark overlapping meeting stile/astragal or a compressible center seal, or adjust the leaves to meet it. Keep the adjoining-room light and local practical pools intact. Recheck the other closed boundary portals for the same finish. The open freight passage in `E03_FREIGHT_LEAF.png` and the separate closed freight-leaf diagnostic remain distinct, readable poses.

I independently opened all 19 F18ci actual-map views, all 19 native full views, the closed freight-leaf diagnostic and four native-lit detail views. All 19 assembled-map PNG hashes match the incremental `main-F18ci/RENDER_MANIFEST.json`. All 24 native/detail PNG hashes match their hosted group/detail manifests and pair to archived F18 native SHA-256 `e67b4c7e4fc6cbf1d989791040b88d9e515ba5abd0755853119401e8017c1fd4`. The F18 build manifest and cold record carry the same native and recipe hashes; cold is PASS with zero failures. The archived recipe fingerprint is `39f7ab0248c95e3d2bfd917ba72ff76311e0e898024c377de5123181d121bdec` across seven inputs. The assembled-map manifest uses that same native and recipe, records the corrected lighting installer `9e51c5a64220419197cddacd1d6bda900f880b5383da5acf152acbbc6f72b858`, and records 421 fuel receivers excluded from each of five retained map sun/bounce helpers. It adds no room ambient fill and retains the physical map world. These checks establish evidence pairing, not art points.

I reopened the four actual spawn craft references as the 100-point craft standard and the five current PR54 reactor references for atmosphere only. Spawn sets the bar for readable construction, material response, practical-light control and finished joins; its brighter palette and room functions are not targets. PR54 informs the low-key, worn mood only.

## Seven-category scores

| Category | F18ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` preserve the entry, primary route and refinery approach; `C05–C08` keep the east turn, reactor threshold, bypass and clean branch legible. The floor arrows remain visible in dark intervals, including `C02`, `C07` and `E01–E03`. The bright door seams do not block navigation. |
| Modeling and fabrication detail | 97 | The carrier, workbench, utility panel, gate and service equipment are well formed across `D01–D06` and `P01–P04`. The closed portal leaves at the waste and clean approaches, plus the plant header, lack a sufficiently dark, fitted center closure; the visible slit makes their meeting detail read unfinished. |
| Materials and surfacing | 99 | `C03/C04/C07` show layered ceiling and chipped floor damage; `C08/E02` retain a distinct clean-zone finish. Enamel, tile, rubber, steel, wood, paper and fittings stay differentiated under low practical light. The door seam is a closure-fit issue rather than a broad surfacing failure. |
| Lighting | 99 | In actual-map `C01/C03/C05/C08`, visible tubes and wall fixtures correspond to localized pools with falloff; the broad floor/service-wall wash is absent. The refinery sky glimpses stay within authored roof openings. C04’s bright vision pane and C06’s brighter portholes stay confined to glazing and create no room-wide spill, so I accept them as transmitted/reflected adjacent-space light in these views. |
| Environmental storytelling and asset diversity | 99 | `D01` identifies the FC-017 carrier; `D02` combines the retained work lead and tools; `D03/D06` show the AIR/07 and CHECK B assemblies; `E01` presents arrivals and seal/receipt work; `P03/P04` add a reactor call point and plant-side strainer. The fuel corridor keeps its own service/freight role. |
| Professional finish and contact appearance | 96 | Carrier wheels, cask saddles and support legs are grounded in actual-map `D01/C03/C09`; `P01–P04` show mounted, terminated and recessed details. The bright center slits in `E01/E02` and the subtler `C10` seam interrupt otherwise convincing closure/contact finish and recur across portals. |
| Visual parity with spawn | 97 | F18 matches the spawn references in authored detail, material control and practical task pools, while preserving the distinct industrial palette and rundown condition. Spawn’s closed joins read finished; F18’s bright closed-portal slits fall short of that fit-and-finish standard. |

## Nine-area scores

| Area | F18ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` show the cart-check station, refinery doors, route markings and damaged tile margins. C04’s glazing highlight remains localized; I found no confirmed center-gap defect there. |
| Staging / bench / cask / utilities | 99 | `D01–D03` show the cask carrier, tool bench, retained lead, AIR/07 manifold, pointer gauge and chained cap. `P01` confirms the fabricated lead connector and cradle; `P02` confirms the process junction box. |
| Freight gate | 99 | `D05` shows the drive/rail supports and contacts. Main `E03` shows the open passage; the separate closed diagnostic shows seated leaves with a readable center closure. |
| East turn | 99 | `C05` separates reactor return from waste handoff with arrows, local pools and red alerts; `P02` confirms the fastened process junction. |
| Delivery / waste | 96 | `E01` keeps the waste/S03 identity, arrivals board, container and seal/receipt station readable. The bright line through the closed double-door center seam is a visible fit/closure defect. |
| Reactor adapter | 99 | `C06/D04` retain the reactor threshold, warning spill, inspection hardware and readable door state; `P03` shows the mounted intercom. The porthole highlights remain local to the glass. |
| Bypass / recess | 99 | `C07/D06` distinguish the bypass from the CHECK B manifold; its tag, hose and purge/check tray remain readable under the local practical. |
| Plant header | 97 | `C10` keeps the plant doors, water line, reel and flow point legible. A subtler but visible bright center line on the closed plant portal repeats the same closure-fit issue. `P04` shows the flush open strainer. |
| North / clean corridor | 96 | `C08/E02` preserve the cooler clean-zone cues, cabinets and open aisle. E02’s bright center slit through the closed leaf pair is conspicuous at normal view and reads as an unfinished seal. |

The unaffected categories and areas exceed 98. Modeling/fabrication, professional finish, parity, delivery/waste, plant header and north/clean corridor do not. F18ci therefore fails the requested all-categories/all-areas strict threshold pending the visible portal-closure repair and a fresh full cycle.

## Evidence limits

The assembled-map review is limited to the 19 supplied fixed views at 960×640/32 samples; native full views are 1280×853/32 samples. The closed freight diagnostic establishes a static leaf pose only. I make no Unity, controller, performance or continuous-cadence claim. The C04/C06 glazing evidence supports only the visible bounded highlights and the supplied straight-ray exterior sightline; it does not prove the full refracted or reflected light path.
