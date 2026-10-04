# Independent visual review — Waste Storage R37

**Verdict: FAIL against the working gate.** I opened all 21 mandatory R37 views, both supplemental detail views, and every paired R31 view. R37's render manifest records all 21 required cameras, the protected camera poses/optics, world strength 0, and checkpoint SHA-256 `3c52dd3c926cf2bb7a1c148181b404a7d6a7776d15294ee4d394e49b6569e019`. R31/R37 comparisons and detail manifests identify the paired images as source-matched. The visual work is strong and the mood fits the dark, neglected brief. I find one material process-readability defect; the cold evidence confirms exact reproduction but does not change the visual score.

| Category | Score | Weight | Weighted points |
|---|---:|---:|---:|
| Layout, scale and route readability | 99 | 20% | 19.80 |
| Art direction, architecture and silhouettes | 99 | 20% | 19.80 |
| Waste-process hero equipment and functional clarity | 98 | 15% | 14.70 |
| Materials and anti-plastic quality | 99 | 15% | 14.85 |
| Fixture-only lighting and gloomy atmosphere | 99 | 10% | 9.90 |
| Purposeful dressing and human storytelling | 99 | 10% | 9.90 |
| Technical cleanliness, contacts and reproducibility | 99 | 10% | 9.90 |
| **Weighted total** |  | **100%** | **98.85 / 100** |

**Working gate:** FAIL. The process category is below 99. **Critical visual veto:** none observed. The cask-side bridge below is a specific image-readability defect, not an observed connected fluid path or broken runtime state.

## Pixel findings

In **C02_Casks** and **W04_CellService**, the opposed black, flanged side fittings line up across the narrow gap between the shielded casks. In these standing crops they read as one dark vessel-to-vessel transfer bridge. That weakens the intended reading that the casks are sealed and that the room-air capture hood/header is the separate extraction system. **D03_ExtractionRun** helps by showing the overhead capture/header and filter/fan arrangement together, but it does not clarify the cask-side bridge in the tighter views. This is the only material process-readability defect I found.

The R37 finish otherwise holds together: the casks have recognizable lifting lugs, bolted closures, gauges and distinct jackets; the cells and dry/quarantine containers retain useful silhouettes; visible wear is localized; wood, rubber, bare/painted metal, concrete and paper separate under the modeled practical lights. Dark intervals remain readable in the standing shots, and the freight spine is visibly open. The repeated storage forms read as functional repetition, not a defect by themselves. The replacement ring and split rejected seal on the bench read as uninstalled stock and failed stock; I do not count the unused replacement as an error.

## Paired camera review

R37 was compared directly with the same-pose R31 image in every row. Most changes are subtle surface, fixture or hardware refinements. I found no material regression beyond the close cask-connector ambiguity described above.

| Camera | R37 vs R31 observation |
|---|---|
| C01_Entry | Freight spine and receiving-to-rear sightline remain clear; no material regression. |
| C02_Casks | Cask hardware and labels remain readable; opposed flanged fittings retain the transfer-bridge ambiguity. |
| C03_Reverse | Reverse route and four-cell rhythm remain legible; no material regression. |
| C04_Route | Central cart lane reads clearly between storage cells; no material regression. |
| C05_Transfer | Incoming overpack remains staged on the cart; visible supports and cart silhouette read clearly. |
| C06_Dry | Dry-storage containers remain legible as separate repeated units; no new occlusion. |
| C07_Quarantine | Open quarantine container and retained filter read clearly; no material regression. |
| C08_Extraction | Filter/fan and duct remain visible; no new defect relative to R31. |
| C09_Inventory | Booth equipment and inventory display remain locally readable; no material regression. |
| C10_Workbench | Tool board and repair bench remain readable; no material regression. |
| W01_Personnel | Personnel portal and nearby circulation remain open; no material regression. |
| W02_ReceivingReturn | Shutter opening and apron remain unobstructed; added upper frame details do not block the opening. |
| W03_Dispatch | Dispatch aperture remains clear; no material regression. |
| W04_CellService | Service access and cask faces remain readable; the opposed black fittings contribute to the bridge ambiguity. |
| W05_ReceivingExterior | Receiving threshold and interior route remain readable; no material regression. |
| W06_PersonnelExterior | Personnel threshold remains legible; cart and route remain clear. |
| W07_DispatchExterior | Dispatch approach and room axis remain readable; no material regression. |
| W08_BoothDoor | Booth opening and equipment remain visible through the doorway; no material regression. |
| W09_DrySouth | Dry containers remain visually distinct and access space remains open. |
| W10_ResidueService | Residue overpacks remain identifiable; close crop communicates storage and service fittings without a new regression. |
| D01_SealRepair | Failed seal, replacement ring, removal tool and repair tools remain distinct; R37 replacement rubber reads as a clean uninstalled part. |
| D02_CaptureService | Both capture mouths and their header transition remain visible; no material regression. |
| D03_ExtractionRun | Room-air collection and the filter/fan are visible together; this improves process context but does not resolve C02/W04. |

## Technical evidence and limits

The supplied `validation_R37.json` reports PASS, with zero protected-pose changes, world strength 0, 26 fixture checks and 23 emissive checks passing, 321 new and 57 inherited support contacts passing, zero unregistered supports, zero sampled route obstructions, 50 freight-aperture checks passing, and zero reported issues. `material_contract_R37.json` is a material/dependency inventory, not a visual material pass. The checkpoint fingerprint is source-unchanged.

The original-source cold rebuild reports PASS. `comparison_R37.json` records zero changed objects and materials and an identical scene-state digest. The checkpoint and rebuilt blend have different file SHA-256 values because the rebuild is a separately serialized file; this is not a byte-for-byte comparison. Their fingerprints cover the same 3,051 objects and 278 materials, both report source unchanged, and the R37 build record reports 562,759 triangles.

`pixel_comparison_R37.json` records identical settings and exact pixel matches (`max_channel_delta: 0`) for all 21 mandatory cameras. `detail_comparison_R37.json` records the same for D02 and D03. These cold results complete the required image/state reproducibility evidence and support a **99 technical score**. The score is bounded to the supplied authoring, contact, support, fixture, route-sampling, mesh-integrity, dependency/fingerprint and cold-pixel evidence; it does not certify Unity collision, navmesh, runtime lighting or performance.

**Geometry clarification for the visual finding:** a later read-only geometry probe identifies the opposed C02/W04 components as solid trunnion retaining flanges and lifting spindles, with their ends physically separated. I did not inspect or score that source geometry. My 98 process score is specifically about their image read in the opened standing views, where the dark opposing parts visually suggest a bridge; it is not a claim that the modeled vessels are connected. This clarification does not change the R37 visual scores or finding.
