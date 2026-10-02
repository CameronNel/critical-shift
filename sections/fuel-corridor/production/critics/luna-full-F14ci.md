# Luna independent full-corridor review — F14ci

## Decision

**F14ci clears the strict visual threshold in the requested dark, eerie, rundown mood, and is materially stable against F13ci in the final two fixed-view cycles.** I independently score all seven categories and all nine areas at 99. The lower staging practical power and new staging/bench keys are visible in the fixed views as restrained lighting changes; they preserve the route, fabrication, material response and authored damage.

I opened all 19 published F14ci full views at 1280×853, the closed E03 freight-leaf diagnostic, all four actual spawn craft references, and all five manifest-verified PR54 reactor mood references. I rehashed the full and closed image sets against their render manifests; all 20 hashes and image dimensions match. The archived F14ci native SHA-256 is `650aec3f1e654e607de0442ae6f2fcf5544b99feb835ff1a709c2fb6b3641484`, matching the F14ci build and cold records; cold validation reports PASS with zero failures. The F13ci archived native SHA `c51f6f1fc397de024fa90cbb3acc3578501a8cb3ae660ea8b40a8a6f810ccf2a` and all 20 F13ci images also match their records.

The F13ci and F14ci render manifests use matching camera transforms, lenses and render settings. The stability record shows `fuel_atmosphere.py` as the only changed recipe input: F14 lowers the staging base from 109 W to 80 W and adds staged visible-light keys for the staging and bench practicals. The recipe and native hashes therefore differ. Across the 20 paired views, the largest mean absolute channel difference is 8.91/255 in `D02_WORKBENCH`; `C03_HERO` is 5.99, `D01_CARRIER_OPERATION` 6.07, `C01_ENTRY` 5.04, and all other paired full views are below 4.0. I inspected the changed views against F13ci; the changes read as local practical illumination and bounce, without a visible change to route, silhouette, construction or material identity. Closed E03 differs by 3.12/255 mean and retains the same seated-leaf appearance. I found no collateral art regression.

The actual reworked spawn remains the craftsmanship reference (100), not a palette target. F14ci matches its grounded fabrication, clear shape hierarchy, differentiated surfaces, selective detail and believable contacts while keeping the corridor's process/service palette and darker owner-requested mood. PR54 contributes atmosphere guidance only: dark green/amber values, sparse red alert accents and practical pools with usable silhouettes.

## Seven-category scores

| Category | F14ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` retain a legible freight path from cart-check and staging to the refinery/process areas under low light. `C05` separates reactor return and waste handoff; `C07/C08/E02` preserve the bypass and clean-zone routes. In the event samples, `C01` F28→29 visibly dims the rear work zone while the floor arrows and service opening remain readable; F31 restores the pool. |
| Modeling and fabrication detail | 99 | `C01/C03/C04` show bounded ceiling cavities with torn retained layers and hanging service leads, and fractured floor edges with recess depth and retained tile pieces. `C06/D04` resolve the reactor portal's layered leaves and operating hardware; `D05` shows the freight drive and rail; `D01–D03` give the carrier, bench and utility panel distinct construction. F14 changes no visible assembly silhouette. |
| Materials and surfacing | 99 | The views distinguish oxide and navy painted metal, pale formed panels, ceramic clean-zone tile, dark floor, timber, rubber, paper and metal fittings. Chips, stains, missing floor plates and ceiling damage remain localized; the surface response is not buried under generalized dirt. F14's lighting changes preserve those material families. |
| Lighting | 99 | `C02/C05` retain dark process margins and red alert points; `C01/C03` use localized task pools against damaged surfaces; `C08/E02` shift cooler in the clean passage; `D06` isolates its purge/check equipment. The final-native event samples show a visible staging source/pool dropout and recovery. In `C01`, the staging-bar crop mean falls from 13.25 to 4.35 (8-bit RGB mean) from frame 28 to 29 and returns to 13.1 by frame 31; the floor arrows and distant service opening stay legible. The bench phase is a quieter secondary fluctuation. |
| Environmental storytelling and asset diversity | 99 | `C01` combines check tools, transfer equipment and work traces; `D01` identifies the FC-017 carrier; `D02` shows an open service case and hung tools; `D03/D06` make air and purge/check tasks legible; `C05/E01` distinguish reactor return from waste receipt. The visible failures support the failing-facility story without substituting random debris for function. |
| Professional finish and contact appearance | 99 | The tagged cask rests in saddles on a wheeled chassis (`D01`), bench items sit on the top (`D02`), and the utility panel, valves and hose remain supported in their recesses (`D03/D06`). Missing tiles have fractured retained edges and visible backing depth; roof openings retain layered material and service leads. I found no visible floating prop, unsupported equipment or distracting intersection in the reviewed views. |
| Visual parity with spawn | 99 | Spawn's four actual references establish polished object contacts, layered fabrication, useful lighting and controlled detail. F14ci preserves those qualities in a much darker industrial scene: carrier, gate, valve, portal and workbench silhouettes remain readable, with damage applied as deliberate construction. The distinct fuel palette and service use fit the task. |

All seven categories strictly exceed 98.

## Nine-area scores

| Area | F14ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` show the refinery doors, cart-check station, transfer equipment and cask along a clear approach. Floor and roof damage flank the route; the staging practical's event samples do not erase its arrows or the distant opening. |
| Staging / bench / cask / utilities | 99 | `D01` shows the tagged FC-017 vessel secured on its carrier; `D02` shows the open tool case, tools and working surface; `D03` shows the air/utility panel, valves, hose and gauge. The main practical changes are visible without losing the work silhouettes. In C01 the bench phase is locally small: frame 32→33 workbench-crop RGB mean shifts 41.26→37.63, while the whole-view mean absolute channel delta is 1.68/255. It reads as subordinate to the staging dropout, which is an appropriate hierarchy for these frames. |
| Freight gate | 99 | `D05` resolves the motor housing, rail, mounts and drive; full `E03` shows the open passage with leaves parked, while the separate closed diagnostic shows the leaves seated at the threshold. The closed view is a static pose check only. F14 introduces no visible gate change. |
| East turn | 99 | `C05` distinguishes reactor return, red wall indicators, waste handoff and route arrows. Dark margins preserve the ominous framing while the central route remains visible. The paired F13/F14 image remains visually stable. |
| Delivery / waste | 99 | `E01/C05` show WASTE / S03, the B/017 container, arrival paperwork and seal/receipt point. The red practical is visibly wall-mounted and colors the nearby surface; the damaged flooring stays outside the handoff surface. |
| Reactor adapter | 99 | `C06/D04` make the REACTOR / 02 portal, layered leaves, inspection ports and hand wheels legible with restrained red spill. The large portal anchors the composition without blocking adjacent circulation. |
| Bypass / recess | 99 | `C07` marks the clean bypass route in the dim passage; `D06` shows the purge/check label, gauge, valves, hose and tray within the recess, illuminated as a usable task point. |
| Plant header | 99 | `C10` connects the PLANT / S01 doors, overhead water line and valve, hose reel, flow gauge and local practicals. Its warmer local light gives the plant end a distinct service identity within the darker scene. |
| North / clean corridor | 99 | `C08/E02` show the cooler clean passage, wipe/log and clean-zone cues, service cabinets and a clear aisle. The small damaged patch in `C08` and the cleaner repeated tiles elsewhere distinguish the clean route without undermining the wider rundown mood. |

All nine areas strictly exceed 98.

## Assembled-map and temporal evidence

I opened the actual assembled-map `F14ci_complete_main_C03_HERO.png`. Its SHA-256 `febc4abee56db2c6c4d8f8160520fa5ff1c3c0a4411d2a6fa248448f371fda0f` matches the F14ci main dependency record, paired to the reviewed native SHA. The validation record reports the canonical map and frozen dependencies byte-exact. The assembled-map world lifts the overall exposure compared with the standalone fixed view, but the dark intervals, broken floor and open roof panels remain visible and the cask/route remain readable. A narrow vertical fringe at the extreme right is outside the fuel interior in this camera framing; the pixels do not support calling it a new fuel-roof opening or leak.

The native preview MP4 SHA-256 is `c6e626570e04be731028da245e08d71ec3b8e4b3bde7b74da311a733c8eb04bc`. Its manifest and `ffprobe` agree on 320×212, 24 fps, 240 frames and 10 seconds; the manifest ties it to the reviewed F14ci native and records 112 distinct rendered states with exact reuse of held source-PNG bytes and no fallback. I opened the native frame-1 and frame-240 stills and the event frames 28/29/31 and 32/33/38. The staging bar and its surrounding pool clearly dim and recover in the sampled stills while route cues persist. The bench variation is smaller and remains a secondary event. The loop-boundary stills appear close, but sampled images and metadata do not establish perceived rhythm or continuous playback.

**Real-time playback review: NOT_RUN_CAPABILITY_UNAVAILABLE.** No target-speed playback tool was available. Evaluated light keys, exact frame count and preview encoding do not substitute for that review. This report makes no runtime cadence claim and no Unity, controller, performance or whole-map claim.

## Findings and evidence limits

I found no substantiated remaining art defect in the 19 full views, closed diagnostic, actual assembled-map render or sampled event stills. The bench dropout is a subtle secondary fluctuation at the whole-view scale, with a visible local worklight/pool change on comparison. It does not compete with or weaken the plainly perceptible staging before/dropout/recovery cue. Neither the fixed images nor the still-only sequence establishes continuous playback appearance.

F13ci and F14ci are materially stable full visual cycles: the 20 paired fixed views share camera transforms, lenses and settings; their visible differences track the single bounded atmosphere-input change; no collateral art regression was found. This does not claim byte-identical recipes or pixels. The closed-leaf image and build/cold validation add no art points.

**F14ci still-image decision: PASS, with F13ci/F14ci materially stable as the final two fixed-view cycles.** Every category and area is independently above 98. Temporal cadence remains unreviewed at target speed.
