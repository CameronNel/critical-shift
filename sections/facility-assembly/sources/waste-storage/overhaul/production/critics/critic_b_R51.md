# Independent visual review — R51

## Verdict

R51’s larger localized coating exposures break up the cask shells in normal fixed views without reading as a decal border or broad camouflage stain. The native light-tree sampling change restores the modeled portal and work-surface pools lost in incomplete R50. I found no visual veto and no consequential regression against the last complete cycle, R49. All six visual categories meet the working 99-per-category bar. Overall remains **provisional** until R51’s own 23-view cold pixel comparison completes.

| Category | Score | Weight | Evidence |
|---|---:|---:|---|
| Layout, scale and route readability | 99.5 | 20% | All wide views retain the central freight spine, cell approaches and receiving/dispatch openings. No fixture or handling gear blocks the protected route. |
| Art direction, architecture and silhouettes | 99.0 | 20% | Folded, cast and pressed forms read as a coherent neglected industrial facility; segregated cells and cask hardware retain distinct silhouettes. The dark intervals and cool exhausted palette match the brief. |
| Waste-process hero equipment and functional clarity | 99.0 | 15% | Cask collars, carrier hardware, gauges, quarantine chest, dry cells and room-air extraction remain legible as separate functions. D03 reads as room-air extraction; no vessel-content piping is implied. |
| Materials and anti-plastic quality | 99.0 | 15% | The exposed substrate now appears at useful camera scale on SC01/SC02 in C02, W04 and D03. Irregular losses sit at handling/collar zones and have no continuous outer primer edge. The broad shell retains unchipped areas, but the prior smooth, uniformly coated read is sufficiently interrupted; I found no remaining material defect with a visible consequence that warrants a below-gate score. |
| Fixture-only lighting and gloomy atmosphere | 99.0 | 10% | The W02/W03 receiving and dispatch pools, C01/C03 wall pools, and C09/W08 work surfaces are readable again in R51. Lighting remains dark and localized, with no evidence of unmodeled fill. |
| Purposeful dressing and human storytelling | 99.0 | 10% | The seal-repair bench, inventory station, transfer cart and service details support the interrupted-maintenance story. The route remains clear; replacement seals read as service stock rather than installed vessel components. |
| Technical cleanliness, contacts and reproducibility | 99.0 | 10% | Original-source checkpoint/rebuild fingerprints match across all 3,065 objects, 290 materials and scene digest. Hot and cold expanded validation pass at 589,943 evaluated triangles, with 335 new and 57 inherited supports, zero disabled material links and zero issues. All 21 main plus D02/D03 warm/cold renders independently match every RGB pixel. |

Weighted total: **99.1**. All seven categories meet the working threshold. Verdict: **PASS, no critical veto**. R51’s own selected original-source cold proof is complete; no prior revision’s pixel result is transferred.

## R49 → R51 paired evidence

I individually opened all 21 actual R51 main views and D01–D03, each beside its actual R49 counterpart, and re-opened the actual Spawn and refinery references. R51 main and detail manifests are complete and source-unchanged at checkpoint SHA-256 `4165b2ce869cc581e247c6110a91b8f7f4c6a97b5370f6744fb0f372fd5c669f`. `comparison_R49_R51.json` verifies the 21 main-view file hashes, fixed camera matrices and lenses, and all settings other than the explicitly recorded `use_light_tree: true → false` change. Both detail manifests are complete; their fixed camera matrices/lenses match R49, and the actual D02/D03 images were opened as pairs. R49’s historical missing sampling field is recorded as the enabled default, not treated as a hidden matching setting.

The sampling method differs, so I do not claim an entirely matched-sampling comparison or attribute the restoration to a specific material. The paired images show a real and consequential default-R50 regression at portal pools and nearby wall/jamb readability. The packaged actual diagnostic `production/diagnostics/R50_W02_no_lighttree.png`, with its settings and hash in `production/sampling_diagnostic_R50.json`, restores that W02 pool at the same 24 samples when only the light-tree flag is changed. R51 saves the disabled setting natively and the actual R51 W02, W03 and W05 views restore those modeled-light pools. No new fixture, power or material change is involved in this repair.

| Camera | R49 → R51 actual-view observation |
|---|---|
| C01_Entry | Restored receiving/portal wall pool and clear central spine; bay labels and cell fronts remain legible. |
| C02_Casks | Stronger irregular SC01/SC02 shell exposure is visible at normal size. Contact wear reads as chipped coating, not a graphic outline or broad cloud. |
| C03_Reverse | Portal wall pools return; extraction context and aisle remain clear. |
| C04_Route | Protected route remains open with localized practical pools; no regression. |
| C05_Transfer | Transfer cart, carried cask and route clearance remain readable. |
| C06_Dry | Folded lid, restraints and dry-cell edges remain clear; no collateral material change. |
| C07_Quarantine | Open inspection state and containment framing remain legible; no regression. |
| C08_Extraction | Filter/extraction service face and duct remain readable under the restored modeled pool. |
| C09_Inventory | Inventory display, dose dial and log surface retain their task pool; no regression. |
| C10_Workbench | Actual seal-service tools remain clearly lit; no new reflection or finish defect. |
| W01_Personnel | The portal pool and jamb separation return; the approach remains open. |
| W02_ReceivingReturn | The diagnostic-confirmed left-wall pool and receiving-frame depth return. |
| W03_Dispatch | Right-wall pool and opening-frame separation return; opening stays clear. |
| W04_CellService | Contact losses at cask collar/carrier zones are visible without a perimeter decal read. |
| W05_ReceivingExterior | Left receiving-enclosure highlight and interior pools return; transfer context remains clear. |
| W06_PersonnelExterior | The large left partition recovers most of its R49 value; a small residual value difference remains but does not impair the approach or make its surface unreadable. |
| W07_DispatchExterior | Clear route and dispatch context remain stable. |
| W08_BoothDoor | Inventory display and work surface are more readable under the restored pool. |
| W09_DrySouth | Dry-cell faces and restraints remain stable; no collateral finish change. |
| W10_ResidueService | Residue-cell array and controls remain stable; the R51 light method does not obscure labels or seams. |
| D01_SealRepair | Replacement rings, tools, gloves and paperwork retain their service-stock read; no regression. |
| D02_CaptureService | Capture header and cask tops remain readable; no regression. |
| D03_ExtractionRun | The extraction system and casks remain distinct; shell contact wear is visible without implying internal vessel pipework. |

There is no material regression in R49→R51. R39→R45 and R45→R49 previously had no material regressions in my independent comparisons. This R49→R51 judgment respects the recorded sampling-method change and is based on actual pixels, not on geometry or code evidence.

## Technical scope and pending proof

The selected R51 checkpoint and original-source rebuild fingerprints each contain 3,065 objects and 290 materials; the changed-object and changed-material sets are empty and the scene-state digests match. Hot and cold validations both pass at 589,943 evaluated triangles, with 335 new and 57 inherited supports, zero disabled shader links and zero issues. Both R51 warm manifests are complete, source-unchanged and record `use_light_tree: false`.

R51 cold state, validation, and pixel evidence independently pass. The selected checkpoint and cold rebuild fingerprints contain 3,065 objects and 290 materials, with zero changed objects/materials and identical scene-state digests. `validation_R51.json` and `validation_R51_cold.json` both pass at 589,943 evaluated triangles, 335 new and 57 inherited supports, zero disabled shader links and zero issues. I checked both complete source-unchanged manifest pairs: all camera matrices and lenses match their cold partners, each warm/cold PNG SHA-256 matches its manifest, main and detail settings match exactly including `use_light_tree: false`, all 21 main RGB comparisons have max channel delta zero, and both supplemental details also match RGB exactly. The checkpoint SHA-256 is `4165b2ce869cc581e247c6110a91b8f7f4c6a97b5370f6744fb0f372fd5c669f`; the cold rebuild SHA differs by serialization, so I do not claim byte-identical blend files. These checks establish selected-revision reproducibility, not Unity integration, exhaustive collision/navmesh validation, or runtime performance.
