# Critic A — whole-room cycle R20

## Scope and evidence

I inspected each of the 21 R20 fixed-camera images individually and paired it with the matching R13 view. I also inspected `details/R20/D02_CaptureService.png` as supplemental evidence only; it does not substitute for player-camera coverage. R20's manifest is complete and its SHA matches `validation_R20.json`. I reopened the actual Spawn `VALIDATE_Hero_A.png` and `VALIDATE_Spawn.png` and refinery R24 `CAM_ENTRY.png`, `CAM_PROCESS.png`, `CAM_MATERIAL.png`, `CAM_HERO_DETAIL.png` and `CAM_WORK_NOOK.png` references. Black beyond the module portals is expected and was not scored as a defect. Layout is scored against the preserved fixed cell/pose contract; repetition is judged under art direction. Cold-pixel proof is still rendering, so technical acceptance remains pending. No Unity runtime, collision or navmesh claim is made.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 99 | 20% | The visible freight spine, turns, cell approaches, receiving, booth and personnel access remain clear and plausible in all fixed views. The four-cell plan and protected poses are fulfilled requirements, not layout penalties. |
| Art direction, architecture and silhouettes | 76 | 20% | Flared capture mouths, cask-service hardware, distinct SC01/SC02 details and the quarantine form improve construction specificity. The overall room still repeats the same vessel, bin and bay silhouettes; C08/C02 do not visually connect the capture system to its destination. |
| Waste-process hero equipment and functional clarity | 84 | 15% | Split/replacement seals and the removal pick now clearly communicate an uninstalled repair task; C02/W04 show a guarded SC01 gauge and repaired SC02 jacket. Receiving/inspection/stored state reads better. C08 still does not show a clear hood/header-to-fan path, and several small cues disappear at wide-view scale. |
| Materials and anti-plastic quality | 74 | 15% | The rejected seal reads as matte rubber, straps are distinct, upper cask paint is quieter and spalls are more irregular/deep than R13. Broad lower cask mottling persists in W04, lid faces remain pale, and wall spalls retain conspicuous angular cutout edges in wide shots. |
| Fixture-only lighting and gloomy atmosphere | 74 | 10% | Dark intervals and the existing fixture pools remain readable and moody. C08's internal process contents are still dark and the new work does not create a stronger inspection pool there. Many broad surfaces remain similarly lit/value-matched rather than separating the principal functional stations. |
| Purposeful dressing and human storytelling | 72 | 10% | D01 now shows a split rejected seal, a matching uninstalled replacement and removal pick; C09's clipped “NO RELIEF / SHIFT 06” note reads at camera scale. C05 ratchets appear, though the working handles remain small; the wider room still carries few interruption cues. |
| Technical cleanliness, contacts and reproducibility | 91 | 10% | Complete manifest hash matches validation. PASS reports 489,766 evaluated triangles, 247 protected poses unchanged, 26 fixture pairs, 23 active emissive surfaces, 256 new plus 57 inherited contacts, no sampled route obstruction, six extractor cavity and six capture-air-path checks, and no listed issues. Independent cold-pixel proof is pending, so 99 is not supported yet. |

**Weighted total: 82/100** (82.4 before rounding). R20 improves the functional details, especially the seal-service story, but the visual categories remain materially below 99. No explicit critical visual veto is observed in this review; the candidate is still not accepted. The remaining functional weakness is significant but is reported as a deduction rather than treating a partially readable process as a hidden-camera or blocked-route veto.

## Camera-by-camera comparison

| Camera | R13 → R20 pixel result |
|---|---|
| `C01_Entry` | Capture assembly now appears as flared, segmented intake faces and is more visibly tied to the left station than the plain header in R13. It remains small/high on the wall at this wide view, and its connection onward to the plenum/fan cannot be followed. Route stays open. |
| `C02_Casks` | Flared twin capture mouths and header form a more purposeful silhouette. SC01's opened protective gauge guard is visible, and SC02's bolted jacket patch gives the two fronts distinct service states. The two vessels still dominate as near-identical forms; most individual fasteners/labels remain small compared with the refinery hero-detail reference. |
| `C03_Reverse` | No meaningful change from R13; the bay rhythm and open central spine remain clear. Repetition remains an art-direction issue across the room, not a layout defect. |
| `C04_Route` | No meaningful change. Route and turns stay legible. The capture mechanism is not visible from this camera, so this view does not communicate its relation to the aisle or process. |
| `C05_Transfer` | The brown web straps from R13 remain visible and two outward-facing dark ratchet/tensioner blocks now appear at the near load-plate edges beside the canister base. Their form reads as tie-down hardware in the close image, though the handles/anchors are still low contrast and small. The load is visibly secured better than R13. |
| `C06_Dry` | No meaningful change; broad lid planes and the repeated bin profile remain. The fixed view still emphasizes large pale tops and edge staining rather than distinctive dry-storage contents/state. |
| `C07_Quarantine` | No meaningful change from R13. Pleated filter remains legible through the gasketed viewport; the scene still shows only a partial body above/behind the bin lip. |
| `C08_Extraction` | No meaningful visual improvement. Inspection slits and internal pleats remain small bright elements, but the shot does not reveal a continuous air path from capture/header to plenum/fan. As a result, its extraction function is not fully communicated in the player view. |
| `C09_Inventory` | A larger clipped shift note reading “NO RELIEF / SHIFT 06” is now legible beside the monitor, strengthening the human/task story. It covers part of the monitor's right edge and does not clarify a specific held item or event in the inventory list. |
| `C10_Workbench` | No meaningful change: repair tools remain neatly hung and tabletop surfaces arranged. The active work sequence is better told in D01, but this view still feels more like a prepared display than a recently interrupted job. |
| `W01_Personnel` | No meaningful change. Jamb, threshold and approach remain legible; black past the opening is expected. |
| `W02_ReceivingReturn` | No meaningful change. Opening and approach remain clear; note that the scan/booth and portal are readable from this fixed view. |
| `W03_Dispatch` | No meaningful change. Authored frame and threshold remain visible; black beyond is expected. |
| `W04_CellService` | The opened SC01 gauge guard is now clearly swung aside around the gauge; SC02 shows the rectangular bolted jacket patch. These are useful functional distinctions. SC01 body still has diffuse lower-face discoloration rather than only contact/rim wear. |
| `W05_ReceivingExterior` | No meaningful change. The cart is visible but ratchets are too small to identify at this range; there is no route blockage. |
| `W06_PersonnelExterior` | No meaningful change. The cart and booth remain legible; load-restraint hardware is not readable at this distance. |
| `W07_DispatchExterior` | No meaningful change. This still reads as repeated bays and containers. Route remains clear, but major forms do not gain much cell-to-cell identity. |
| `W08_BoothDoor` | The “NO RELIEF / SHIFT 06” paper note appears beside the monitor and is readable, but overlaps the monitor edge. It adds a human circumstance; it still does not say which operation is held or what condition caused it. |
| `W09_DrySouth` | No meaningful change. Container fronts and pale broad lids remain dominant. Rim wear still extends conspicuously along edge bands; surface wear could be more tightly localized. |
| `W10_ResidueService` | No meaningful change. The residue cask fronts remain visually repeated and the wide view does not show a distinct stored-state difference. |
| `D01_SealRepair` | Strong improvement: a split rejected seal with a removal pick now sits beside a grooved replacement seal. Their adjacent placement communicates a service/replacement state without implying an installed closure. Both still sit very neatly on an otherwise clean bench; the reference work nook uses a few objects plus task evidence, and this close view could carry a small contact/handling trace. |

## Highest-impact remaining pixel repairs

1. **Make the capture route legible in the fixed player views.** The new flared mouths improve C01/C02 silhouettes, and supplemental D02 shows their construction, but C08 does not visually connect them through the header/plenum to the fan. Carry a readable continuous duct/plenum silhouette into the existing extraction interface in the actual room views, while preserving all protected poses and routes.
2. **Differentiate major equipment/state without moving the required cells.** C02/W04 now distinguish SC01's open gauge guard from SC02's jacket patch, a good direction, but the casks remain near-clones and C01/C03/W07 repeat similar bay fronts. Add a small number of durable mid-scale state cues to the repeated primary forms that survive 960x540 views, avoiding extra tiny labels.
3. **Improve deterioration material quality in `W04`, `W01`–`W03` and C01/C03.** R20's spalls are more irregular than R13 but still read as angular dark/gold cutout islands from wide cameras; lower SC01 staining remains broad. Show believable exposed undercoat/substrate depth with varied edge scale and direction around plausible seams/leaks, and confine cask corrosion to rims/contact zones.
4. **Give the C05 restraint readable hardware where the cart is seen at distance.** In C05 the outward-facing ratchet blocks are visible at the near plate edges; in W05/W06 they disappear. Add a simple higher-contrast handle/web path at camera-visible faces without enlarging it into visual clutter.
5. **Make the operator state more actionable.** C09/W08's shift note is a good scale improvement but clips the screen and names only the staffing event. Tie it to a visible inventory hold/control indicator and retain unobstructed monitor content; add a single worn handling cue to D01 so the split-seal operation feels performed rather than laid out for display.

## Bounded technical evidence

R20's complete manifest covers all 21 cameras and its source SHA matches `validation_R20.json`. The validation PASS reports 489,766 evaluated triangles; protected count 247 with zero changes; 26 fixture pairs; 23 emissive surfaces; 256 new and 57 inherited contacts; no route obstructions; six extractor-cavity checks and six capture-air-path checks; and no listed issues. These are source-side measurements, not exhaustive proof beyond their stated samples. Independent cold source/pixel proof is pending, and no Unity runtime, collision, navmesh or performance result is claimed.

## Technical-count correction

Direct re-read of `validation_R20.json` confirms **268 new contacts**, not 256. The report above preserves the original entry as review history; the correct measured total is 268 new plus 57 inherited contacts. This factual correction does not change the technical score or visual verdict.

## Cold-source reproducibility update

I independently inspected `coldstart/comparison_R20.json`, `pixel_comparison_R20.json`, `detail_comparison_R20.json`, both checkpoint/rebuild fingerprints, `validation_R20_cold.json`, and the complete `R20`, `R20_cold`, `details/R20`, and `details/R20_cold` manifests. The hot and cold fixed-view manifests cover the same 21 cameras, each detail manifest covers D02, and the source hashes match their respective validation records. The cold comparison reports no changed objects or materials and identical scene state. Both fingerprints contain 2,784 objects and 266 materials, with identical hashes. All 21 paired camera renders have exact pixel identity (maximum channel delta 0); D02 also has exact pixel identity and equal settings. Cold validation is PASS with 489,766 triangles, 247 protected poses unchanged, 268 new plus 57 inherited contacts, 26 fixture pairs, 23 emissive surfaces, six cavity rays, six capture-air-path checks, zero sampled route obstructions, zero unregistered supports and no listed issues.

This new evidence supersedes the earlier pending-cold-state rationale and warrants **99/100 for Technical cleanliness, contacts and reproducibility**. The score reflects complete measured authoring and cold-source/pixel repeatability for this scope; it does not include Unity runtime, performance, collision or navmesh claims. Other category scores and the visual non-acceptance verdict remain unchanged. The revised weighted total is **83/100** (83.2 before rounding).
