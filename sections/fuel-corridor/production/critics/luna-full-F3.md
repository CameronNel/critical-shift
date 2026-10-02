# Luna independent full-corridor review — F3

## Decision

**F3 is a substantial visible improvement over F2, but it is not accepted.** All seven visual categories and all nine areas remain below the owner's strict >98 target. The strongest improvement is localized: F3 adds visibly authored service assemblies, a more useful bench and carrier cluster, more legible door construction, and a separate waste/clean approach. However, most corridor views still share broad cream wall fields, dark blue lower panels, a pale tiled floor, and a regular ceiling grid. Against the spawn reference, the full route still lacks enough architectural variation, material range, strong branch identity, and human-scale storytelling.

I opened all 19 images and the matching `RENDER_MANIFEST.json` in `production/renders/review/full-F3`, plus `E03_FREIGHT_LEAF.png` and its manifest in `production/renders/review/closed-F3`. The full manifest binds the 1280×853, 32-sample images to `checkpoints/fuel_full_F3.blend`, SHA256 `8d6af812aee50cfabe9d9dc5ceb12d64e3dbc5d9503134b8fecb0ad99c71140d`; all 19 image hashes match. The closed-pose diagnostic is also bound to that native file and its image hash matches. Spawn remains the fixed reference at 100.

F3 improves every named F2 repair target to some degree, but the results are uneven. The new equipment and detail often read well in close views, while wide-route images still expose large unarticulated fields. F2's dark/quiet presentation also persists in several close views, even though the gate motor task light is functioning visibly. The small closed-pose view demonstrates the freight leaf faces and their layered panels; open-state pocket concealment is intentional and is not counted as missing geometry.

## Seven-category scores

Scores use the same rubric and spawn=100 as F1/F2. These are pixel judgments only.

| Category | F3 | F2 | Visible basis and remaining gap |
|---|---:|---:|---|
| Spatial composition and readability | 90 | 87 | Door destinations, route arrows, and branch-specific fixtures improve orientation. C01/C03/C08 still read as long repetitions of the same corridor bay; large wall/floor fields dominate focal equipment. In C03, the pale broken parking-berth outline beneath the carrier is visible but low-contrast against the floor, so its function does not read strongly at route scale. |
| Modeling and fabrication detail | 91 | 87 | D01/D02/D03 and the freight/reactor doors show real layered construction, fitted supports, tools, rails, handles, windows, and utility hardware. The architectural shell remains repetitive; some large doors and service units still read as simple assemblies against flat fields in wide views. |
| Materials and surfacing | 86 | 82 | Carrier, painted steel, orange guards/doors, dark lower wall, and floor are differentiated. Most surfaces remain clean painted metal or tile in a narrow value range. Spawn has much stronger material and color variety, including fabric, rubber, wood, paper, PPE, and contrasting tile. |
| Lighting | 86 | 82 | The D05 task light clearly illuminates the drive; C01/C03 have usable broad fill. D01/D02/D03 and the wide routes still have dark shadow areas around important hardware, without the warm/cool pools and focal hierarchy visible in spawn. |
| Environmental storytelling and asset diversity | 89 | 85 | F3 adds a convincing handover/work cluster, carrier, radio/tools, utility hardware, clean/waste approaches, and a waste bin. Most traces remain concentrated around entry/staging; E01/E02/C07/C08 still lack the density and distinctive human use of spawn's lockers, PPE, seating, notes, and personal gear. |
| Professional finish and support contacts | 90 | 86 | The carrier wheels and cradle, cask restraints, bench supports, door hardware, utility panel and freight running assembly read as mounted objects. The pale broken floor marks beneath the C03 carrier read plausibly as its parking berth, though their low contrast weakens that reading. Rendered pixels cannot establish hidden contacts or runtime behavior; no technical-validation points are added. |
| Visual parity with spawn | 86 | 82 | F3 is more authored and functionally varied than F2, especially in close-up assets. Spawn still has bolder silhouette variation, richer material/color changes, more strongly composed thresholds, and more human-use detail across the whole frame. |

No category is near the required >98.

## Nine area scores

| Area | F3 | F2 | Visible evidence and remaining gap |
|---|---:|---:|---|
| Entry / refinery | 89 | 87 | `C01_ENTRY`, `C02_PRIMARY_ROUTE`, `C03_HERO`, `C04_REVERSE`: new service equipment and work assets help, but C01's handover board is clipped by the left edge and the repeated cream/blue wall system leaves the approach visually broad and quiet. C02's new wall unit has no visible branch of service runs connecting it to a larger process. |
| Staging / bench / cask / utilities | 92 | 89 | `C03`, `C09`, `D01`, `D02`, `D03`: strongest area. Cask saddle/restraints and wheeled carrier read as usable; workbench tools, radio, containers, and utility panel add human purpose. The pale broken parking-berth lines beneath the carrier are real floor markings, but are subtle in C03's wider view. The left workbench is also clipped by that view's frame; D02 provides the dedicated bench evidence. This cluster still lacks spawn's material range and warm focal color. |
| Freight gate | 91 | 85 | `C03`, `D05`, `E03`, closed-pose `E03`: running rail, motor, bellows, attached task light, and closed leaf detailing are visible. D05 still devotes much of its lower frame to a heavy dark channel, and the bright motor housing is surrounded by large near-black structure. The closed diagnostic shows layered faces but does not verify an engine controller or continuous sweep. |
| East turn | 87 | 85 | `C05_EAST_TURN`: the orange gate and offset corridor make the turn readable; blue header and wall-mounted box add some articulation. The broad left wall and small electrical box still leave the turn generic, with no large, high-contrast destination feature to pull the eye into the branch. |
| Delivery / waste | 89 | 81 | `E01_WASTE_APPROACH`: the S03 header, orange waste leaves, service panel, and wheeled bin give this branch a real identity, an improvement over F2's weak framing. The bin is small against the gate, labels are difficult to read from the approach, and there is little evidence of active handover or waste handling beyond the single bin. |
| Reactor adapter | 90 | 85 | `C06_REACTOR_THRESHOLD`, `D04_REACTOR_WIDE`: the paired leaves now show raised panels, bars, edge framing, central separation, and circular glazed apertures. Their monumental repeated slabs still dominate a fairly bare threshold; nearby process context is limited, and the wide view does not give the aperture/glazing much visual emphasis. |
| Bypass / recess | 89 | 85 | `C07_BYPASS`, `D06_SERVICE_RECESS`: the floor is continuous, bypass access is clear, and the recessed utility panel/hose/fixture reads as installed. C07's two long walls and floor remain bare transit surfaces; D06 is a dark, isolated fixture without surrounding service purpose or maintenance evidence. |
| Plant header | 89 | 84 | `C10_PLANT_HEADER`: substantial frame, paired leaves, inset viewing windows, wall service panel and overhead cable route make the plant endpoint identifiable. The header label is small at corridor scale, and the similar door palette/panel rhythm makes this destination feel like another portal rather than a distinct plant station. |
| North / clean corridor | 85 | 82 | `C08_SERVICE_JUNCTION`, `E02_CLEAN_APPROACH`: E02 finally frames the clean port and its vent, doors, and approach; it is clearer evidence than F2. The `CLEAN / S02` header is white on a dark ink plate, but is weakly legible in E02 because it is shadowed and cropped by the top edge; C08 remains a dim, long generic corridor with little human-use evidence. |

All nine areas remain below 98. Staging is strongest; north/clean, east turn, and entry still lag because authored close objects do not yet carry through to route-scale composition.

## F2 repair targets: F3 result

| F2 target | Result | Pixel evidence |
|---|---|---|
| Substantial functional service assemblies | **Improved, localized** | `C02` now has a central grille/control assembly with a rising duct; `D03` shows a detailed wall utility panel and connecting hose; `D06` places related equipment in a recess. These are meaningful additions, but C02's new unit still looks isolated on a large wall and C08's route remains mostly empty. |
| Branch wayfinding | **Improved, incomplete** | `C03` has readable service/fuel-transfer signs at close range; `E01` shows `WASTE / S03`, `C10` identifies `PLANT / S01`, and E02 identifies `CLEAN / S02`. At player-route scale the text remains small; the white-on-cream `CLEAN TRANSFER` direction plate in `C07_BYPASS` has especially weak contrast. E02's header uses white on a dark ink plate, but is shadowed and partly cropped by the framing. |
| Light/material separation | **Improved locally; broad gap remains** | `D05`'s mounted fixture lights the motor face and bellows, and `C03` has a clear work zone. `D01`/`D02` still fall dark around support structure and tabletop details; wide corridor lighting stays neutral and the large wall planes have little material response. |
| Door/cast-object detail | **Improved** | `C06`/`D04` show layered reactor leaves with real glazed inspection apertures; `C10`'s plant doors and the closed diagnostic show fabricated panel faces, rails, and hardware. Open freight leaf faces remain properly hidden in pockets. The wide scenes still make many large doors feel like repeated, similar panels. |
| Downstream human-use evidence | **Improved, still sparse** | `D02`'s bench, pegboard, tools, radio and containers are credible; `D01` carrier and `E01` waste bin extend use beyond entry. Clean, bypass, and north corridor views still lack comparable signs of routine occupancy or maintenance. |

No F2 target visibly regressed in this evidence. The main remaining issue is that the new localized detail is not yet supported by a similarly authored route shell and area-to-area hierarchy.

## Highest-impact remaining corrections

1. **Break the repeated bay language with a few substantial area-specific architectural changes.** In `C01_ENTRY`, `C03_HERO`, `C05_EAST_TURN`, and `C08_SERVICE_JUNCTION`, broad cream fields and the continuous dark-blue lower band dominate. Use existing wall/ceiling bays for materially and spatially distinct process architecture: a deep service recess or backed equipment bay at C02, a clear threshold/turn treatment at C05, and differentiated clean/bypass wall or floor treatment at C07/C08. Keep the route width and outer footprint, and let each assembly connect visibly to its service function instead of adding isolated small props.

2. **Clarify actual floor markings and strengthen route-scale signs.** The pale broken lines directly beneath the carrier in `C03_HERO` are its parking berth, not a floor defect; their low contrast makes that purpose easy to miss in the wide view. Raise their separation slightly from the surrounding tile if a player should read the berth. Improve the distance read of the `CLEAN TRANSFER` direction plate in `C07_BYPASS` with a higher-contrast face; improve the `CLEAN / S02` header's visibility in `E02_CLEAN_APPROACH` through lighting/placement so it is not lost to shadow and top-edge cropping. Improve the entry/refinery and east-turn destination read in `C01`/`C05` without adding competing labels.

3. **Carry the useful human story into the downstream branches.** `D02_WORKBENCH` is the strongest use case, and `E01` now has a bin. Add one or two functional, area-specific fixtures to `C07_BYPASS`/`D06_SERVICE_RECESS`, `C08_SERVICE_JUNCTION`, and `E02_CLEAN_APPROACH`—for example, a readable maintenance/handover point at the bypass, an actual clean-entry preparation feature, and a supported service/transfer point at the junction. Tie them to the architecture and preserve open travel space.

4. **Refine light and material grouping around close equipment.** `D05_GATE_MECHANISM` is an actual improvement: keep its attached task light, but expose more of the rail/mount support without the broad dark channel swallowing the lower view. In `D01_CARRIER_OPERATION` and `D02_WORKBENCH`, lift local fill or adjust value/material separation so the cradle, wheels, lower bench storage and tools remain readable in shadow. Wider shots need distinct color/material zones; local brightness alone will not close the spawn parity gap.

5. **Give the plant/reactor thresholds more distinct hierarchy.** The doors in `C06`, `D04`, and `C10` are better fabricated, and their apertures are properly understood as glazing. Keep that construction; distinguish the plant and reactor functions with stronger portal silhouette, useful adjacent process fixtures, and clearer label placement rather than another layer of generic bars or panel graphics. Ensure the glazed apertures catch enough controlled light to read as windows in the wide threshold views.

## Concrete remaining gap by rubric category

- **Spatial composition/readability (90):** break up the same broad wall/floor rhythm in `C01/C03/C05/C08`; connect C02 equipment to visible service paths; make the C03 carrier berth markings read as purposeful at route scale; make the `C07` direction plate readable and keep the `E02` clean header visible from the approach.
- **Modeling/fabrication (91):** invest in large wall/ceiling/service silhouettes that can hold their own in `C01/C05/C08`, not just close-up fixtures. D03 and door construction are strengths to retain; make their supports and the adjacent architecture read together in the wide views.
- **Materials/surfacing (86):** add clearly different tactile/material families across major surfaces and props in `C03/C07/C08/E02`; the current tile/painted panel set does not approach spawn's wood, fabric, rubber, paper, PPE, and bold color blocking.
- **Lighting (86):** maintain D05's motor task light while clarifying its shadowed mounting rail; use purposeful warm/cool pools in `D01/D02/D06` and `C08`, and separate branch focal areas from overhead ambient fill.
- **Storytelling/diversity (89):** extend D02's believable maintenance story to `C07/D06`, `C08`, and `E02`; the large branches should show who uses them and why, not only their door label.
- **Professional finish/support contacts (90):** keep the C03 carrier and pale berth markings visually integrated, and maintain the visible support quality around the cart/cask and wall-mounted assemblies. Hidden contacts still require separate native/engine evidence.
- **Parity with spawn (86):** raise the overall route's material and silhouette variation, contrast and human detail. The existing close-up quality is not yet distributed across the route, while spawn sustains its richer visual language over every large surface and threshold.

## Evidence and limits

The 19 native-state renders and matching manifest are the visual basis. F3's archived `F3_COLD_VALIDATION.json` and `F3_BUILD_MANIFEST.json` are intentionally not used to award art points. The separate `closed-F3/E03_FREIGHT_LEAF.png` is a rigid-carriage diagnostic: it confirms that closed leaf surfaces can be inspected and shows layered panel faces, handles, and circular glazed apertures. The native scene remains open; that diagnostic does not establish the engine controller, collision, or continuous gate sweep. Concealed open-state leaf faces are not treated as missing geometry.

The wide views establish route-scale composition; `D01`–`D06` establish close object detail; `E01`/`E02` establish the downstream waste and clean approaches; `E03` establishes the open freight approach. These views still cannot prove all in-engine lighting, gameplay traversal, hidden support contacts, or the appearance of views not covered by the 19 cameras. Those limits do not change the visible score findings above.
