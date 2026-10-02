# Luna independent full-corridor review — F23ci

## Decision

**F23ci independently clears the strict still-image threshold in the gloomy, eerie, rundown fuel-corridor mood.** I score every requested category and area at 99 against the actual reworked spawn craft references (100). I found no substantiated visible defect that lowers a category or area to 98 or below. The closed-portal repair remains seated in all supplied angles, and the confirmed F20 exterior slot does not return in F22 or F23 actual-map views.

I opened all 19 F23ci full native views, the closed freight-leaf diagnostic, all four native-lit P01–P04 details, all 19 actual assembled-map views, all four actual spawn craft references, and all five PR54 reactor mood references. All 24 native/detail images hash-match their hosted group/detail manifests and pair to F23 native SHA-256 `def288245d8356802f972c45b4f389df5effabf249bb0e76601eaf7dd78cf3fe`. All 19 actual-map image hashes match the incremental `main-F23ci/RENDER_MANIFEST.json` and carry that native SHA and recipe `2af15cd9f6915334ed42bad8c53e73b49a18ef7ea043597b49d59c2041e31e19`. The selected module, archived F23 native, build manifest and cold record agree on the same native and recipe; cold is PASS with zero failures. Native views are 1280×853/32 samples; actual-map views are 960×640/32 samples.

The actual spawn images set the craft standard for readable construction, material response, practical lighting and finished contacts. The five PR54 references inform mood only; they are not a craft score target. F23 preserves the fuel corridor's distinct freight/service role, protected boundary and industrial palette while carrying the authored dark, worn look.

## Seven-category scores

| Category | F23ci | Pixel basis |
|---|---:|---|
| Spatial composition and readability | 99 | `C01–C04` show the entry, primary route and refinery approach; `C05–C08` separate the east turn, reactor threshold, bypass and clean branch. `C02`, `C07` and `E01–E03` keep chevrons and aisles readable across dark intervals. The actual-map C02 process jamb remains dark, without an exterior slit. |
| Modeling and fabrication detail | 99 | `D01` shows the cask saddles, trolley base, wheels and supports; `D02/P01` show the hung tools, connected lead, fabricated plug and wall cradle; `D03/D06` show the AIR/07 and CHECK B assemblies; `D05` shows a supported rail motor; `P04` shows the recessed strainer. Full-depth jamb returns and door overlaps close the previously visible edge gaps. |
| Materials and surfacing | 99 | `C03/C04` show layered ceiling damage and chipped tile margins; `C05/C07` retain the worn oxide/navy service character while `C08/E02` remain cooler and cleaner. Tile, painted steel, enamel, rubber, timber, paper and fittings remain differentiated under the practical pools. The framed wall panel behind the carrier in `C09` is more outlined in F23 than F22 but reads as a closed panel, not an aperture. |
| Lighting | 99 | Actual-map `C01/C03/C05/C08` show bounded fixture pools and dark intervals without a broad helper-light wash. Red alarm color remains local. `C04`'s bright refinery-pane patch and `C06/C10`'s pane reflections stay inside glazing; `D04`'s blue sky glimpse is bounded by the authored roof opening. The D03 gauge face is low-contrast in the 960×640 main-map view; its markings and pointer resolve in the native detail, while the AIR/07 label, valves and hose remain readable. This is a minor dial-readability limitation, not a room-lighting failure.
| Environmental storytelling and asset diversity | 99 | `D01` identifies the FC-017 cask; `D02/P01` support hands-on bench use; `D03` identifies AIR/07 and its chained bleed; `D06` pairs CHECK B with the purge tray. `E01` shows arrivals and sealing work, `P03` adds the reactor call point, and `P04` the plant-side strainer without borrowing spawn-room functions. |
| Professional finish and contact appearance | 99 | `D01/C09` show a grounded cask, saddles, deck, legs and wheels; `D05` seats the motor feet on its rail. `P01–P03` show retained or mounted connections, and `P04` sits flush within its frame. The closed `E01/E02/C10` portals show continuous overlap joints; `C05` no longer has the bright exterior slit beside the inset waste jamb. |
| Visual parity with spawn | 99 | Relative to spawn's actual construction references, the reviewed views retain comparable attachment clarity, support/contact definition, controlled material response and practical shaping. The corridor does not need spawn's brighter palette or briefing/locker functions to meet that craft bar. |

## Nine-area scores

| Area | F23ci | Pixel basis |
|---|---:|---|
| Entry / refinery | 99 | `C01/C03/C04` identify cart-check, refinery and fuel-transfer stations, with damaged floor margins and route arrows. The small vision-pane highlight in `C04` stays within the glazed opening. |
| Staging / bench / cask / utilities | 99 | `D01–D03` show the labeled cask carrier, connected bench lead and AIR/07 valve panel. `P01` verifies the captive connector/cradle. The D03 gauge is subdued at map scale, but its ticks and pointer resolve in the full native close-up; label, handles and hose remain legible. This bounded limitation does not prevent identifying or reading the utility assembly. |
| Freight gate | 99 | `D05` shows the drive, feet and rail; open `E03` preserves the passage, and the separate closed diagnostic shows the freight leaves seated. This diagnostic is a static pose check. |
| East turn | 99 | `C05` separates reactor return from waste handoff with clear arrows, local fixtures and red indicators; the repaired full-depth waste jamb return blocks the former outside view. |
| Delivery / waste | 99 | `E01/C05` show WASTE/S03, the arrivals board, container and seal/receipt station. The closed waste pair has a continuous center overlay and no bright line through it. |
| Reactor adapter | 99 | `C06/D04` preserve the reactor identity, paired leaves, inspection windows, alarm spill and arrival/check station; `P03` shows a mounted and connected intercom. Pane brightness remains contained by the window frames. |
| Bypass / recess | 99 | `C07/D06` keep the cooler bypass distinct from the CHECK B manifold. The attached tag, hose, valve handles and purge/check tray remain discernible in the work pool. |
| Plant header | 99 | `C10/P04` show the WATER header, hose reel, FLOW/S01 point, fitted portal and flush open strainer. |
| North / clean corridor | 99 | `C08/E02` preserve clean-zone cues, cabinets and open aisle. The closed CLEAN/S02 portal has a continuous center stile and readable sign. |

All 16 scores strictly exceed 98. The D03 dial's low contrast is explicitly recorded; at the supplied full native detail its scale and needle can be read, so it does not merit a sub-threshold score or an added room light.

## F22ci–F23ci material stability

I separately opened and compared the corresponding F22 and F23 views; this is not inherited approval. Both cycles use the same seven recipe inputs (`2af15cd9f6915334ed42bad8c53e73b49a18ef7ea043597b49d59c2041e31e19`) with matching camera transforms, lenses and render settings. All 24 paired native/detail views and all 19 paired actual-map views were compared. The largest mean absolute channel differences are `0.16236/255` in native `C09_MATERIALS` and `0.18708/255` in actual-map `C09_MATERIALS`; those bounded changes cluster at the background access-panel edge behind the cask. I inspected both C09 pairs: the line reads as the perimeter of the same closed wall panel, with the carrier, wall and supports otherwise materially stable. I found no material regression across the other views. F22 and F23 are materially stable cycles, not byte-identical renders.

## Actual assembled-map hero

I opened `F23ci_complete_main_C03_HERO.png` and matched its SHA-256 `69dde89245f06d653ec4fb3f1ea2745e78e32b4e3897103327b0d4524585b8e0` to `MAIN_LINK_VALIDATION.json`. That record and the launcher/dependency records pair to F23 native SHA `def288245d8356802f972c45b4f389df5effabf249bb0e76601eaf7dd78cf3fe` and the recipe above. In this assembled-map view the task pools remain bounded, arrows and floor wear read, and the workbench, carrier and side route remain identifiable. I saw no new integration regression. This is one hero view; it does not establish whole-map or Unity acceptance.

## Actual-map dim-state stills

I opened the four sampled assembled-map dim-state PNGs and checked their hashes against `production/renders/temporal/F23ci-main-dim/RENDER_MANIFEST.json`. The manifest pairs them to the same F23 native SHA and recipe, with 960×640/32-sample settings. `C01_ENTRY_F0110` retains the foreground chevron, center aisle, doorway silhouette and entry equipment. `C03_HERO_F0029` darkens the staging bay but leaves the central route, floor arrow, bench edge and transfer cart readable. `C05_EAST_TURN_F0001` has broad shadowed wall and ceiling areas, while the center turn, arrow and local process/waste fixtures remain legible. `C08_SERVICE_JUNCTION_F0001` keeps the clean branch and its wall controls readable. Across these samples, dark intervals remain without losing route or task identities; I saw no broad unmotivated fill or newly obscured contact. These are sampled stills, not evidence of perceived flicker cadence.

## Evidence limits

The still review is limited to the supplied 19 fixed actual-map views, 19 native full views, four details, one closed-leaf diagnostic, one assembled-map hero, four assembled-map dim states and eight preview samples. The E03 full view shows an open freight passage; the separate image is a static closed pose. The F23 entry preview pairs to native SHA `def288245d8356802f972c45b4f389df5effabf249bb0e76601eaf7dd78cf3fe`; I checked frames 1, 28, 29, 31, 32, 33, 38 and 240 against its final manifest. Its 240-frame encoding is 24 fps over 10 seconds at 320×212, with 112 rendered distinct states. The sampled dim states preserve route cues and task silhouettes, but neither these proxy stills nor the encoding establishes perceived continuous cadence. No Unity, controller or performance claim is made.
