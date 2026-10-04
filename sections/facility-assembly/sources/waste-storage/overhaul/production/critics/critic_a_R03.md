# Critic A — whole-room cycle R03

## Scope and evidence

I inspected all 21 R03 fixed-camera images individually and compared each against its R02b counterpart. I read `production/validation_R03.json` and the complete `renders/R03/manifest.json`; their blend hashes match. Portal views are judged under the isolated-module contract: black beyond an opening is expected, so the visual assessment covers its authored jambs, threshold, frame and approach. Scores are normalized 0–100 per category; rubric weights apply to the weighted total. The final requirement remains at least 99 in every category with no vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 78 | 20% | The aisle, bay boundaries and portal approaches remain readable, and the transfer cart is visible. R03 does not materially change the layout. Several camera views still show repetitive bay geometry and the cart has no seated load to explain its intended use. |
| Art direction, architecture and silhouettes | 63 | 20% | Formed cover edges and localized wear improve the storage silhouettes over R02b. The repeated plain box bays still lack a distinct folded/frame construction language, and much of the large room remains visually generic. |
| Waste-process hero equipment and functional clarity | 65 | 15% | Shielded casks, formed covers, inventory station and quarantine container read more clearly. The spent filter is not visible in C07, the transfer cart remains empty in C05, and C08 still does not explain the extraction path. |
| Materials and anti-plastic quality | 65 | 15% | The broad orange-white speckling has been substantially reduced; wear now generally follows edges and contact zones. Painted steel, bare metal, rubber, wood and paper separate in better-lit views. The remaining broad fields are smooth and repetitive, with a few edges still carrying visibly mottled wear. |
| Fixture-only lighting and gloomy atmosphere | 75 | 10% | The R02 local-light improvements persist, with a bleak palette and useful pools on major work areas. Several lower-value service corners remain hard to read, while the 21 pixels do not show the actual source pairing/provenance on their own. |
| Purposeful dressing and human storytelling | 48 | 10% | The repair bench and inventory station contribute useful traces. The quarantine container has no clearly visible payload, the cart is unloaded, and the remaining bay views have little evidence of people or repeated work beyond labels and localized wear. The gloves still look flat at close range. |
| Technical cleanliness, contacts and reproducibility | 86 | 10% | The matching validation reports world 0, 247 protected transforms unchanged, 24 passing fixture/lens pairs, 278 new and 57 inherited contacts passing, zero unregistered supports/route obstructions/issues, and 165 passing closed-mesh checks. The manifest is complete for all 21 views and matches the validated blend hash. Cold-start behavior remains unverified. |

**Weighted total: 69/100** (68.6 before rounding). The wear/material category improved over R02b, but no category approaches 99. This is not visual acceptance.

## Camera-by-camera comparison

| Camera | R02b → R03 pixel result |
|---|---|
| `C01_Entry` | The central aisle remains clear. Broad rust speckle on side lids is reduced to a much quieter edge/contact pattern; the far opening's black interior is expected under the isolated-module scope. |
| `C02_Casks` | This is a strong improvement: collar bands and most of each cask body are clean, with wear gathered nearer lower seams and support contact. Cask silhouettes and gauges read more clearly without the mottling taking over. |
| `C03_Reverse` | Lighting and route readability are stable. The dark intervals and bay rhythm still read; this view offers little evidence of the east-bay construction quality because the bins are mostly seen at a distance. |
| `C04_Route` | The open route and turning area remain clear. Open cover edges are more controlled than R02b; the surrounding bay faces still repeat the same broad box-and-panel language. |
| `C05_Transfer` | The cart remains legible and the work area is adequately exposed, but it is still empty. The flat load platform has no seated cask/container to communicate how a transfer is secured. |
| `C06_Dry` | The broad speckle field is largely gone and the covers have a more formed, returned edge. Remaining wear is mostly along the rim; some lid surfaces still appear very broad and smooth, and repeated bins dominate. |
| `C07_Quarantine` | The lid now has a thicker formed edge and restrained edge wear, a clear improvement. A payload is not actually readable in the open container from this camera; the interior still reads as an empty dark cavity. |
| `C08_Extraction` | Housing and surrounding material marks are cleaner, but the camera remains visually close to R02b. The transfer/extraction path and the function of the central mechanism are still ambiguous. |
| `C09_Inventory` | The screen, inventory rows, dose gauge and shift log remain legible. No material R03 change is visible here. The small text remains supporting detail rather than a readable gameplay cue. |
| `C10_Workbench` | The repair bench retains its useful local light and clear seal-service setup. It is effectively unchanged; the arrangement still feels carefully staged and the board/tools show little localized use from this view. |
| `W01_Personnel` | The doorway frame and approach remain visible; black beyond the contract opening is expected. This camera is effectively unchanged and does not establish detail inside the adjoining module. |
| `W02_ReceivingReturn` | The portal jambs, lintel, floor marks and nearby scan booth remain readable. The isolated black beyond the aperture is not scored as a defect; there is no material R03 change. |
| `W03_Dispatch` | The authored frame and approach remain clear under the local practical. The black region beyond is expected at the module boundary. No meaningful R03 change. |
| `W04_CellService` | Wear is now concentrated near the lower vessel seam/support contact instead of blanketing the full body and collar. The service gauge and fittings remain identifiable. |
| `W05_ReceivingExterior` | The approach and scanner stay readable. Open lid wear is much more restrained, though the east-bay storage forms still look like repeated plain containers. |
| `W06_PersonnelExterior` | The corridor/booth composition and practical pools are stable; no major R03 change. The cart at lower right still appears as an empty staged object rather than a loaded transfer. |
| `W07_DispatchExterior` | The route and portal approach remain readable, with black beyond the isolated opening. The open lid on the left is less visually noisy than R02b; repeated bay shapes remain. |
| `W08_BoothDoor` | Inventory equipment and glass framing remain clear. There is no significant R03 visual change; the booth stays sparse, with a bright practical visible at upper right. |
| `W09_DrySouth` | Formed lid returns are more apparent, and rust is limited to much smaller edge patches. The broad storage faces remain repetitive and could use clearer folded skins/channel framing to avoid the box look. |
| `W10_ResidueService` | The earlier body/collar/support speckle is substantially reduced and concentrated near lower seams and exposed contact edges. Cask construction is easier to assess, but the group remains repetitive. |
| `D01_SealRepair` | Ring-stain shadows are softer than R02b and the gloves appear slightly fuller, but the glove silhouettes still look like flat cut shapes without convincing finger/palm volume. The bench props remain arranged rather than actively used. |

## Highest-impact corrections for R04

1. **Make the quarantined spent filter visible in C07.** It must remain below the formed lid's closure envelope, but from the fixed view it should read unmistakably as a held filter/material item rather than an empty cavity. Preserve the lid clearance and quarantine silhouette.
2. **Replace the east-bay box rhythm with specific architecture.** In C01/C04/C06/W05/W09 the repeated plain sides and broad covers still flatten the storage bays. Use folded or corrugated skins, real channel frames and formed cover geometry so the architecture and container silhouettes are authored even before labels or wear are seen.
3. **Show a secured closed load on the receiving cart in C05.** The cart is now visible, but an empty platform does not explain its relation to the storage cells. Add a closed, seated load with clear support/retention, visible at the existing fixed camera and consistent with the clear lane.
4. **Resolve C08's functional hierarchy.** The extraction setup still reads as equipment without a clear sequence. Clarify the source, controls, connection and receiving/containment path in silhouette and value, and make the critical junctions legible from this camera.
5. **Finish the close-view glove and repair story.** D01's gloves remain flat and the tool board looks neat. Give the glove a credible palm/finger volume and broad fabric folds, then add only a few task-specific handling marks or displaced tools. Keep the strong local task light and restrained wear language.

## Bounded technical evidence

The R03 manifest is complete for all 21 fixed views and its source SHA matches `validation_R03.json`. The validation reports PASS with 247 protected transforms unchanged, world strength 0, 24 fixture/lens checks, 278 new and 57 inherited contacts, zero unregistered new supports, route obstructions or issues, and 165 closed-mesh checks. These results support the registered checkpoint checks only. The report states that its anchors and lane rays are sampled, not exhaustive collision certification, and no cold-start proof is included here.
