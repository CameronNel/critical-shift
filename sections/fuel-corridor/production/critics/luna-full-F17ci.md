# Luna independent full-corridor review — F17ci

## Decision

**F17ci clears the strict still-image threshold in the requested dark, eerie, rundown mood.** All seven categories and all nine areas score 99 against the actual reworked spawn reference (100). I found no substantiated new art defect. The F16 bench-lead repair remains finished in the F17 pixels, and the authored route, practical light pools, damage and service hardware continue to read clearly.

I independently opened all 19 F17ci full views at 1280×853, the closed freight-leaf diagnostic, all four native-lit P01–P04 closeups, all four actual spawn craft references and all five manifest-listed PR54 atmosphere references. All 24 F17ci PNG hashes match their per-view manifests at 1280×853 and 32 samples. The selected module, archived native, build manifest, cold record and render manifests agree on native SHA-256 `027ab74f9a3928204d7d3e5f2c1af736982aa41063b37078a6fd9db2efec8deb`; cold validation is PASS with zero failures. All seven current recipe inputs match the archived build manifest; the construction fingerprint is `4907d580baa67d66a12c02d8ce7598a07ef903de9ded16e8208f0c32a90f087b`.

The spawn views set the craft standard for readable construction, material response, practical lighting and finished contacts; their palette and room functions are not targets. PR54 guides atmosphere only. F17 keeps the protected fuel/service corridor distinct, with dark intervals and sparse red warnings supporting the same authored rundown mood.

## Seven-category scores

| Category | F17ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` preserve the marked path from entry through staging and process. `C05–C08` distinguish the east turn, reactor threshold, bypass and clean branch; `E01–E03` identify waste, clean and freight approaches. Damaged floor margins remain bounded around the route. |
| Modeling and fabrication detail | 99 | `D01–D06` show the carrier, workbench, utility panel, gate and recess equipment with distinct supports. `P01` resolves the stepped lead connector, recessed contacts, strain boot and wall cradle; `P02–P04` show the attached junction, intercom and recessed strainer. |
| Materials and surfacing | 99 | `C03/C04/C07` retain localized chipped tiles, backing depth and layered ceiling damage; `C08/E02` preserve the cooler clean-zone identity. Painted metal, enamel, rubber, tile, timber, paper and fittings stay visually distinct under the low light. |
| Lighting | 99 | `C01/C03/C05` use work pools and restrained red alert spill against deliberate dark intervals. `C08/E02` remain cooler, and `D03/D06` isolate service tasks. The shadows preserve object silhouettes and do not hide the P01–P04 hardware in their close views. |
| Environmental storytelling and asset diversity | 99 | `D01` identifies the FC-017 carrier; `D02` combines retained power, tools and bench use; `D03` shows the AIR/07 manifold and chained bleed cap; `D06/C07` show the CHECK B tag and tamper seal. `P03` adds a reactor call point and `P04` a plant-side strainer without introducing unrelated room functions. |
| Professional finish and contact appearance | 99 | `P01` shows the connector retained in a bolted wall cradle and the cable routed along the wall. `P02` shows glands entering a fastened enclosure; `P03` shows a mounted intercom with a routed cable; `P04` shows a flush open grate. Carrier and gate hardware remain supported in `D01/D05`. |
| Visual parity with spawn | 99 | F17 matches the spawn reference’s level of attached hardware, functional clarity, controlled material response and finished contacts while retaining the corridor’s industrial palette and deliberately worn condition. |

All seven categories strictly exceed 98.

## Nine-area scores

| Area | F17ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` show the cart-check station, refinery approach, transfer equipment and route markings. Damaged floor and roof frame the travel path. |
| Staging / bench / cask / utilities | 99 | `D01` shows the tagged cask on its carrier; `D02` shows the bench, tools and routed lead; `D03` shows the AIR/07 panel, pointer gauge and chained cap. `P01` confirms the formed connector and its retaining cradle at full detail scale. |
| Freight gate | 99 | `D05` shows the drive/rail assembly and supports. Full `E03` shows the open passage with leaves parked; the separate closed diagnostic shows the leaves seated. That diagnostic is a static pose check. |
| East turn | 99 | `C05` separates reactor return from waste handoff with route markings and red alerts. `P02` confirms the local junction is a fastened, terminated enclosure. |
| Delivery / waste | 99 | `E01/C05` show the waste approach, container, arrival paperwork and seal/receipt station as a coherent handoff. |
| Reactor adapter | 99 | `C06/D04` preserve the reactor portal, inspection ports, hand wheels and warning spill. `P03` confirms the call point is mounted between the jamb and interlock console. |
| Bypass / recess | 99 | `C07/D06` distinguish the bypass path from the CHECK B manifold; the attached inspection tag remains part of the valve assembly. |
| Plant header | 99 | `C10/P04` connect the plant doors, water line, hose reel, flow point and recessed open strainer. |
| North / clean corridor | 99 | `C08/E02` keep the cooler clean-zone cues, service cabinets and open aisle legible. The dark floor patch in C08 is bounded and does not obstruct the route. |

All nine areas strictly exceed 98.

## F16–F17 material stability

F16ci and F17ci build manifests contain the same seven recipe input hashes. I compared all 19 paired full views and the paired closed-leaf diagnostic, with matching camera transforms, lenses and render settings. The maximum paired mean absolute channel difference is `0.0037069/255`; the largest per-pixel change is 15/255 in E01 and is confined to sparse pixels. I inspected the pairs directly and found no material visual change or regression. P01 in both views retains the same resolved connector and cradle. The different native SHA values do not imply byte-identical native files; the reviewed evidence supports a materially stable final pair.

## Evidence limits

The reviewed evidence establishes static authored appearance. The closed freight diagnostic establishes a static leaf pose only. Cold checks and image comparisons add no art points.

## Assembled-map and preview still check

I opened the actual assembled-map image `F17ci_complete_main_C03_HERO.png` and checked its SHA-256 (`ef3aab7247501468c0c8e0497b9ca98df098f7522a23fc18df92e81591bee7d7`) against the main-link record. Its launcher, dependency and main-link records identify the same F17 native SHA above; the dependency record reports exact frozen canonical main/R17/spawn/exterior inputs and zero missing fuel IDs. In this brighter assembled-map lighting, the corridor’s route, staging equipment, carrier, floor wear and service openings remain legible. I saw no new visible integration regression in this view. This check does not establish whole-map acceptance.

I also opened preview frames 1, 28, 29, 31, 32, 33, 38 and 240. The preview manifest pairs to native SHA `027ab74f9a3928204d7d3e5f2c1af736982aa41063b37078a6fd9db2efec8deb`; each inspected PNG hash matches its frame-map record. It records 240 frames at 24 fps over 10 seconds, with 112 actually rendered distinct states and exact held-state image reuse. The staging practical’s frame-29 drop is visibly distinct from frame 28 and recovers by frame 31 while the foreground route arrows and task lighting remain readable. The bench change around frames 32–33 is subtler in this wide view. These stills support the intended lighting variation and route readability at sampled states, but do not establish target-speed continuous cadence. No Unity, controller or performance claim is made.

**F17ci still-image decision: PASS.** Every category and area independently exceeds 98, and F16ci/F17ci are materially stable as the final two full fixed-view cycles.
