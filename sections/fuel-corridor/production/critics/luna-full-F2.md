# Luna independent full-corridor review — F2

## Decision

**F2 is a visible improvement over F1, but it is not accepted.** All seven visual categories and all nine areas remain far below the strict >98 target. The F1 black junction patch is no longer visible, and several specific construction and storytelling changes read well. The corridor still has very large, quiet upper-wall fields and a repeated cream/dark-blue panel system across most routes. In these views the new frames and access panels improve fabrication, but do not yet create enough architectural, material, light or human-use variety to approach the spawn reference.

I opened all 16 F2 fixed views and the matching `RENDER_MANIFEST.json`. The manifest binds them to `checkpoints/fuel_full_F2.blend`, SHA256 `39f2f8dc0b3b9d4ebe741290ba32032101a95eadbad68c0f0e27820a128bf3fd`, at 960×640, 32 samples. I reopened the spawn reference renders for the same calibration. F2COLD reports zero technical failures; that is separate from the pixel scores below and receives no visual points.

The S5 style slice passed its development gate. F2 demonstrates progress on the full asset set, but still reads as a clean modular corridor rather than an environment with the same material range and lived-in finish as spawn. No singular black patch remains to veto the review, but procedural cleanliness and architectural repetition continue to be major art-direction concerns.

## Seven-category scores

Scores use the unchanged rubric and spawn at 100. Parenthetical values show the F1 score for the same category.

| Category | F2 | F1 | Visible basis |
|---|---:|---:|---|
| Spatial composition and readability | 87 | 82 | Access-panel articulation and bumper placement improve the entry and junctions, and removal of the C07 black patch restores a continuous visual floor. Long routes still have weak destination hierarchy and broad blank wall fields. |
| Modeling and fabrication detail | 87 | 82 | C01/C03 roof and vent closure, recessed wall panels, guards and new leaf panels create visible authored construction. The same panel rhythm remains dominant; large doors still read as repeated symmetric assemblies. |
| Materials and surfacing | 82 | 79 | Cask, orange guards, utility hardware, door skins and painted wall families remain distinct. Most architectural surfaces are still clean, smooth and closely related in value; visible material range remains narrow next to spawn. |
| Lighting | 82 | 78 | The gate motor face in D05 is now visibly illuminated by the attached task light, and practical pools read in several corridors. Much of the route and staging set remains dim, while the broad fill does not consistently separate focal equipment from surrounding fields. |
| Environmental storytelling and asset diversity | 85 | 83 | Handover boards, racked case, bench kit, radio, tools and utility equipment improve human purpose. This evidence remains concentrated in the entry/staging cluster; several branches and header approaches are still empty and interchangeable. |
| Professional finish and support contacts | 86 | 76 | The C07 floor artifact is fixed visually, the case reads as supported on its shelf, and door/panel edges are more resolved. F2COLD's numerical results remain technical evidence; render views cannot establish every hidden support contact. |
| Visual parity with spawn | 82 | 78 | F2 is more fabricated and varied than F1. Spawn continues to show much greater variation in silhouette, material, color and human traces, especially fabric, rubber, wood, tile, paper, PPE and personal gear. |

Every category remains well below the owner's >98 requirement.

## Area scores

These scores use only the named views and the same spawn anchor. Areas with weak or ambiguous dedicated framing are marked in the evidence notes; new supplemental cameras below would improve assessment without moving the existing 16.

| Area | F2 | F1 | Visible evidence and remaining issues |
|---|---:|---:|---|
| Entry / refinery | 87 | 83 | `C01_ENTRY` now includes a handover board, louvered upper closure, outlined access panel and paired yellow guards. It is still a long, nearly symmetrical approach with the same large smooth wall panels and small route marks. The handover board is partly clipped at the left image edge. |
| Staging / bench / cask / utilities | 89 | 87 | `C03_HERO`, `C09_MATERIALS`, `D01_CARRIER_OPERATION`, `D02_WORKBENCH`, `D03_UTILITY` remain the strongest cluster. The cask has stronger panel/seam detail; the workbench is human-useful. From `C03` these assets are still modest against broad walls, and D01/D02/D03 retain a dark presentation. |
| Freight gate | 85 | 80 | `C03_HERO` and `D05_GATE_MECHANISM` show the portal and powered system. The motor-face task light is a clear improvement. The large black running channel still dominates D05's lower frame, while wide views do not make the freight opening a strong visual focal point. The open-state leaves are intentionally concealed in pockets. |
| East turn | 85 | 80 | `C05_EAST_TURN` now gives the doors more layered construction, a clearer frame and visible safety bumpers. The corner's open wall fields remain empty; destination/function lettering is too small to establish zone identity from the wide view. |
| Delivery / waste | 81 | 77 | The C05/C08 views show connector geometry but do not give the waste/delivery branch a distinct visual identity. The area is weakly framed for assessment; a player-height view directed at the S03 approach is needed to score its function and construction confidently. |
| Reactor adapter | 85 | 77 | `C06_REACTOR_THRESHOLD` and `D04_REACTOR_WIDE` show materially improved raised door panels, rails and reinforced surfaces. The glazed circular inspection apertures now read as apertures with metal surrounds, not pull rings. The leaves still occupy most of the composition as repeated, dark-gray industrial forms; the wide view gives little supporting process context. |
| Bypass / recess | 85 | 72 | `C07_BYPASS` no longer has the black floor patch. The bypass is readable and now has more framed access panels. `D06_SERVICE_RECESS` shows the connected utility and parked hose, but the alcove remains dim and visually isolated from surrounding functions. |
| Plant header | 84 | 78 | `C10_PLANT_HEADER` now shows more differentiated leaf panels and better framed geometry. Large symmetric leaves and quiet surrounding walls still dominate; the small S01 identification has weak distance readability. |
| North / clean corridor | 82 | 77 | `C08_SERVICE_JUNCTION` has added access framing and yellow guards and reads as an open route. It remains a long generic passage with no strong clean-header destination cue or human-use cluster. The S02 port is not directly showcased in this composition. |

All nine area scores remain below 98.

## F1 repair targets: result in F2

| F1 target | Result | Evidence |
|---|---|---|
| Floor/ceiling finish overlap at the bypass junction | **Improved** | `C07_BYPASS` now shows a continuous floor where F1 displayed a black, hole-like patch. This is a visible correction; F2COLD is separate evidence. |
| Panel, guard and roof-closure construction | **Improved, incomplete** | `C01_ENTRY` and `C03_HERO` show the louvered closure and better framed access/threshold parts; C01/C04/C05/C07/C08/C10 show more access outlines and safety guards. Large upper fields and repeated panel rhythm remain. |
| Major leaves and human-height handles | **Improved, incomplete** | `C06`/`D04` show reworked reactor leaves and framed glazed inspection apertures; `C04`, `C05` and `C10` show stronger door panels. Handles are more coherent but remain thin/dark against broad leaves in wide views. Existing gasket, folded edge and hardware geometry is not denied; the remaining critique is about how much of that construction reads in the pixels. |
| Practical-light hierarchy | **Improved locally; unresolved globally** | `D05_GATE_MECHANISM` now lights the motor face and mounting area. C01/C03/C08 and D01–D06 still have dim corridors or mechanisms without consistent focal separation. |
| Handover, interlock and racked kit | **Improved** | C01/C04 handover boards and the case on a wall-side rack in C02 make human use more credible. This storytelling still clusters near entry/staging, while downstream route sections remain sparse. |

No clear F1 repair target regressed in the inspected views. New access-panel outlines help fabrication but risk becoming another repeated graphic if not tied to distinct functions.

## Highest-impact remaining changes

1. **Give the large upper fields an authored functional hierarchy — `C01_ENTRY`, `C02_PRIMARY_ROUTE`, `C03_HERO`, `C05_EAST_TURN`, `C08_SERVICE_JUNCTION`, `C10_PLANT_HEADER`.** The new access-panel frames improve the silhouette, but large uninterrupted cream fields still dominate. Use the existing structural bays for a few differentiated architectural/service assemblies (deep equipment recess, exposed-but-supported utility run, maintenance access bay, or substantial route-specific wall feature) so the zones gain distinct purpose. Preserve the outer footprint and route width; do not fill every wall with small props.

2. **Make destination and freight/service hierarchy readable at player distance — especially `C02`, `C05`, `C08`, `C10`.** The orange arrows are understated and the port labels are tiny in these wides. Keep the restrained palette but strengthen the scale, placement and contrast of the one sign or route mark that identifies the branch in each view. Distinguish freight, bypass, plant, clean and waste destinations without multiplying labels.

3. **Improve broad light and material separation without erasing the practical-light improvement — `C01`, `C03`, `C07`, `C08`, `D01`, `D02`, `D03`, `D05`, `D06`.** D05's illuminated motor face is improved; extend that local clarity to nearby rail/supports and the staging equipment. General corridors remain gray and low-contrast, while the close details are dark. Use localized value/roughness changes and controlled fill to expose the authored forms; avoid a uniformly bright result.

4. **Give the reactor and plant doors a stronger object-specific read — `C06`, `D04`, `C10`.** F2's panel redesign is a real improvement. From the fixed wide views, however, the massive paired leaves still read as broad repeated slabs with similar linear bars and recessed panels. Let the existing folded perimeter, gasket, ribs/dogs and inspection-window construction show through silhouette, edge shadow and material response. Keep the glazed circular apertures recognizable as windows; do not treat them as handles or add redundant surface graphics.

5. **Extend the human-use evidence beyond the entry cluster — `C04`, `C05`, `C07`, `C08`, `C10`.** The boards, staged case and bench kit work. The downstream spaces still have no comparable sign of maintenance, handover or process activity. Use a small number of function-specific items or architectural fixtures tied to each area's job, leaving the transit lane and blank surfaces open.

## Additional coverage without moving the existing 16 cameras

- **Delivery/waste:** add a player-height camera at `(14.2, 16.0, 1.70)` looking east (`+X`) toward the S03 waste-transfer approach. The current C05/C08 views do not establish the branch's destination or hero construction.
- **North/clean:** add a player-height camera at `(6.6, 18.0, 1.70)` looking north (`+Y`) toward the S02 clean header. C08 frames the north corridor obliquely and does not show the destination clearly.
- **Freight leaf fabrication (optional diagnostic):** if a closed leaf face needs its own geometry/material assessment, add a player-height camera near `(4.5, 10.0, 1.70)` looking east (`+X`) with the gate in the relevant closed pose. This supplements the current open-state portal/mechanism views and does not imply the hidden pocket internals should be exposed during open gameplay.

Do not move any of the existing fixed cameras; these positions are additional evidence only.

## Evidence and limits

All 16 F2 images were opened: `C01_ENTRY`, `C02_PRIMARY_ROUTE`, `C03_HERO`, `C04_REVERSE`, `C05_EAST_TURN`, `C06_REACTOR_THRESHOLD`, `C07_BYPASS`, `C08_SERVICE_JUNCTION`, `C09_MATERIALS`, `C10_PLANT_HEADER`, `D01_CARRIER_OPERATION`, `D02_WORKBENCH`, `D03_UTILITY`, `D04_REACTOR_WIDE`, `D05_GATE_MECHANISM`, and `D06_SERVICE_RECESS`. The matching manifest was reviewed. Spawn references reopened: `VALIDATE_Spawn.png` and `VALIDATE_Material_A.png`.

Renders do not establish assembled adjacent-room passage, runtime controllers, engine collision behavior or hidden contact geometry. F2COLD reports zero technical failures but is not a visual score. Keep the visual findings, technical contact evidence and runtime validation separate in the next review cycle.
