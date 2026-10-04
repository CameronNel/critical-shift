# Critic A — whole-room cycle R01a

## Scope and evidence

I inspected all 21 individual images named in the complete `renders/R01a/manifest.json`: C01–C10, W01–W10, and D01. I also read `production/validation_R01a.json`, which reports PASS for the same source hash as the saved R01a checkpoint and render manifest. These are first-cycle scores, not final acceptance. I score each category 0–100; the supplied rubric weights are applied only to the overall weighted total. The final requirement remains at least 99 in every category with zero vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 68 | 20% | The central aisle and side zones read in wide views, and sampled route evidence is clear. Numerous openings become featureless black voids; several close service views obscure usable equipment and boundaries. |
| Art direction, architecture and silhouettes | 64 | 20% | The casks, clamps, extraction assembly and repair bench have recognizable industrial forms. Repeated containment boxes and broad blank panels still dominate; the overall environment reads like a clean grey kit with minimal authored wear. |
| Waste-process hero equipment and functional clarity | 64 | 15% | Shielded casks, inventory station, quarantine box and seal repair task are identifiable. The extraction view does not make the extraction process clear, while key transfer equipment is nearly lost in darkness. Segregation reads partly through labels rather than process composition. |
| Materials and anti-plastic quality | 60 | 15% | Painted steel, bare hardware, plywood, paper and rubber separate in the better-lit views. Many areas collapse to similar green-grey values, large surfaces lack convincing use history, and the material story weakens in dark cameras. |
| Fixture-only lighting and gloomy atmosphere | 28 | 10% | The dark, oppressive mood is present, and some local practical pools work. C05, C06, W01, W02, W03 and W09 lose major forms; several door openings are pure black. This is unreadable darkness in key functional coverage. |
| Purposeful dressing and human storytelling | 44 | 10% | The overdue filter note, gloves, mug, shift paperwork and repair tools add a few useful human traces. Across the room, most zones remain sparse, orderly and unmarked; the waste-handling sequence and history of neglect are not yet strongly visible. |
| Technical cleanliness, contacts and reproducibility | 82 | 10% | The matching validation reports 247 protected transforms unchanged, world strength 0, 20 fixture checks passing, 195 new and 57 inherited contacts passing, zero unregistered supports/route obstructions/issues, and 141 closed-mesh checks passing. The manifest covers all 21 cameras and matches the saved blend hash. Cold-start validation is still pending, and the possible inventory-tube self-emission is not separately resolved in this report. |

**Weighted total: 60/100** (60.4 before rounding). No category is close to the 99-point acceptance bar. The scene is not visually accepted.

## Camera-by-camera pixel notes

| Camera | Visible result and defect |
|---|---|
| `C01_Entry` | The center route and flanking storage zones are easy to parse. The dispatch opening at the far end is a featureless black rectangle; much of the ceiling and the side bins fall into darkness. |
| `C02_Casks` | The sealed casks have the strongest large-scale silhouette and useful clamp/gauge detail. The left cask is crowded by a cropped foreground column; the two vessels are very similar, and small identifiers disappear at this distance. |
| `C03_Reverse` | The aisle and yellow floor guides remain legible. Side storage loses detail in shadow and the far opening is black, with no readable threshold or destination. |
| `C04_Route` | The route is visibly clear and flanked by equipment. The crane hardware is strongly silhouetted, but the central dispatch opening again reads as an unlit void and several side assets have weak separation from their bays. |
| `C05_Transfer` | The transfer cart is almost swallowed by darkness: its cradle and contents have low contrast and the lower frame/wheels are difficult to read. This view fails to communicate a safe, usable transfer action. |
| `C06_Dry` | The dry-storage containers can be recognized by their lids and rail edges, but the close view is too dark to read their front hardware or distinguish the container group cleanly. Repeated rectangular lids dominate. |
| `C07_Quarantine` | The open quarantine unit reads as a separate container and the front label is visible. The rear QUARANTINE lettering is cropped at the top and partly hidden; most interior details are dark. |
| `C08_Extraction` | The heavy vertical and rotary equipment feels industrial, but the actual extraction operation is not clear from this framing. Large foreground structure crowds the mechanism, while controls and process connections are dim. |
| `C09_Inventory` | The workstation, dose meter, list screen and shift log read as an inventory station. Screen and paper text are too small/dim to use beyond broad category; the view is materially cleaner than the requested neglected mood. |
| `C10_Workbench` | The seal-service board, tools, vise and local lamp are clear. Compared with the rest of the room this is the most convincing authored work cluster, though tools and surfaces still appear orderly and relatively clean. |
| `W01_Personnel` | Almost the entire personnel opening and its surround disappear into near-black. The cropped sign is not legible and the view gives no useful threshold or access cue. |
| `W02_ReceivingReturn` | The central receiving aperture takes most of the image as a pure black void. The side inventory scanner is visible, but the opening and adjacent route edges are not. |
| `W03_Dispatch` | The dispatch aperture is an enormous black rectangle with little visible door leaf, interior or destination. The view reads as missing scene content rather than a dark but legible facility interface. |
| `W04_CellService` | Close views of the pressure hardware and cell gauges are useful, but vessels fill the frame and some lower identifiers are clipped. It shows construction more than service access or process. |
| `W05_ReceivingExterior` | The near receiving/scanner frame and central lane are clear; the far dispatch aperture remains black. The overall material grouping is coherent but still quite uniform. |
| `W06_PersonnelExterior` | The personnel booth and nearby vessels are visible, but dark foreground structure dominates the left and a table/cart silhouette intrudes at lower right. The doorway hierarchy is weak. |
| `W07_DispatchExterior` | The wide route and cask banks are readable, with clear floor guides. The distant destination is again a black rectangle, preventing the route from having a believable endpoint. |
| `W08_BoothDoor` | The inventory desk and dose monitor are visible through the framed glass, communicating the booth's function. The upper wall is mostly empty, and the glass/door framing is more graphic than materially detailed. |
| `W09_DrySouth` | The dry storage containers occupy the frame, but shadow hides their front surfaces and details. Their repeated box silhouettes flatten together rather than reading as distinct authored units. |
| `W10_ResidueService` | Residue vessels are well enough lit to read their bands, lugs and tags. The repeated trio makes the zone clear, though the crop emphasizes repetition and hardware over any residue-specific handling story. |
| `D01_SealRepair` | The repair task is immediately legible at close range: ring, tray parts, gloves, mug and overdue note. The close crop exposes the gloves as flat, stiff silhouettes and the plywood surface as clean, regular grain; the human-use details feel staged rather than long-used. |

## Highest-impact corrections for R02

1. **Restore functional local contrast in the dark cameras.** Start with C05 Transfer, C06 Dry, W01 Personnel, W02 ReceivingReturn, W03 Dispatch and W09 DrySouth. Keep world strength at zero and use only registered, visible fixtures or actual instrument lenses. Strengthen useful falloff and bounce from those existing practicals, improve surface value grouping, and retain dark intervals between pools. The cart, bin closures, personnel threshold and aperture edges must remain readable.
2. **Resolve black openings as interfaces.** The repeated featureless void in C01/C03/C04/W02/W03/W05/W07 reads as missing environment, not an intentional gloomy destination. Preserve reserved openings and host hooks, but show readable frame, threshold, door/shutter surface, hardware, and a controlled amount of adjoining-space or spill detail appropriate to this module.
3. **Make the process legible through equipment and arrangement.** C02 casks and C09 inventory are the clearest process cues. C08 extraction and C05 transfer need more visible connections, control points and material movement, with silhouettes that explain what passes from receiving to segregation, quarantine and extraction. Clarify at a glance without relying on tiny labels.
4. **Give storage and contact surfaces authored wear.** The current broad panels and repeated bins lack the selective damp, handling, repair and long-term neglect visible in the brief. Add localized, plausible damage and residue around access points, cask bases and service interactions while keeping large quiet regions and material families distinct.
5. **Add a few purposeful human traces beyond the repair bench.** Inventory paperwork is a start, but the remaining zones feel empty and showroom-orderly. Place a small number of specific, supported work traces at receiving, quarantine or dispatch to explain the daily routine and breakdown history; do not fill the room with random debris or labels.

## Technical evidence and limits

The render manifest is complete for all 21 required cameras, and its source hash matches the saved R01a checkpoint and validation report. The validation reports PASS for the listed transform, world, fixture, support, route and mesh checks. Those results support the bounded technical score above. They do not establish cold-start behavior or exhaustive collision certification; the report expressly limits its anchor and lane rays to samples. The supplied note that an inventory tube may self-emit remains unresolved as an actual-instrument-lens source or other emission, so lighting provenance should be explicitly checked before final acceptance.
