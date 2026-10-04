# Independent visual review — Waste Storage R39

**Verdict: FAIL against the 99-per-category working gate; technical remains provisional.** I opened all 21 mandatory R39 images and both supplemental details, each against the same R37 fixed view. The R39 manifest covers all 21 required cameras and both detail cameras, with `source_unchanged: true` and checkpoint SHA-256 `b628dc5deaad05c64ced81c9e80b9e3099b53ebf234b4ee23c083f84853e1877`. The R37/R39 comparison reports matching poses and optics for all 21 paired main views. I found no material R37-to-R39 regression. R31-to-R37 had likewise shown no material regression in the earlier paired review.

| Category | Score | Weight | Weighted points |
|---|---:|---:|---:|
| Layout, scale and route readability | 99 | 20% | 19.80 |
| Art direction, architecture and silhouettes | 99 | 20% | 19.80 |
| Waste-process hero equipment and functional clarity | 98 | 15% | 14.70 |
| Materials and anti-plastic quality | 99 | 15% | 14.85 |
| Fixture-only lighting and gloomy atmosphere | 99 | 10% | 9.90 |
| Purposeful dressing and human storytelling | 99 | 10% | 9.90 |
| Technical cleanliness, contacts and reproducibility | 96 provisional | 10% | 9.60 |
| **Weighted total** |  | **100%** | **98.55 / 100** |

**Working gate:** FAIL. Process clarity is below 99, and technical is provisional pending R39's own 23-view cold pixel proof. **Critical visual veto:** none observed.

## Pixel findings

The R38-to-R39 end-face treatment resolves the earlier C02/W04 ambiguity in the actual R39 images. The exposed, non-emissive steel faces read as solid capped trunnion ends, and visible negative space separates the opposed parts. W04 remains a tight, nearly aligned crop, but the pipe-like connection is no longer the dominant read. D03 also shows the overhead room-air extraction path separately from the casks.

The remaining process clarity defect is **W10_ResidueService**: at the standing close crop, the horizontal dark flange/spindle forms between the three residue overpacks line up into pipe-like bridges across adjacent vessels. That image still suggests inter-vessel transfer and makes the sealed-storage/room-air-extraction distinction less immediate. This is an image-reading observation only; it does not assert a connected fluid path in the model. The two targeted hot-cask views were improved, but W10 keeps the process category below 99.

The rest of the scene holds the requested dark, worn mood while preserving local readability. Strong cask silhouettes, folded extraction mouths and specific maintenance hardware carry the main visual hierarchy. The route remains legible between purposeful repeated storage units. Concrete, painted steel, bare/oxidized metal, rubber, cloth, paper, glass and wood remain distinguishable under the visible modeled practicals. The fixtures create useful pools without turning the room into a showroom. Task dressing stays contained around work points, and the bench seal cluster reads as failed stock beside an uninstalled replacement.

Compared with the Spawn polish images, R39 has the same level of clean silhouette control and finished prop construction, expressed in the requested colder, more neglected palette. Compared with the refinery R24 views, its low-key fixture lighting and material separation sit comfortably in the intended darker family. I observed no visual veto such as flat/flooded lighting, uniformly plastic surfaces, unreadable darkness, blocked routes, excessive signage or generic box-only hero construction.

## Paired camera ledger

Each R39 image was opened beside its R37 counterpart. The earlier R31-to-R37 review had found no material regressions; the R37-to-R39 comparison likewise shows no regressions. Changes to the trunnion end faces are improvements in C02 and W04; other small value changes do not reduce route or equipment readability.

| Camera | R39 vs R37 observation |
|---|---|
| C01_Entry | Receiving-to-rear sightline and central freight lane remain clear; trunnion end-face treatment is a subtle improvement in the left storage cluster. |
| C02_Casks | Solid steel end faces and separated dark gap now read as opposed handling trunnions, not a continuous dark tube. Clear improvement. |
| C03_Reverse | Reverse lane, storage rhythm and rear opening remain readable; no material regression. |
| C04_Route | Freight route remains legible between the cells; the slightly darker value read does not obscure lane markings or turns. |
| C05_Transfer | Incoming sealed overpack remains staged and supported on the cart; no material regression. |
| C06_Dry | Repeated dry-storage containers remain distinct and the service clearance remains visible. |
| C07_Quarantine | Open quarantine unit and retained filter remain readable; no material regression. |
| C08_Extraction | Filter/fan face and duct remain visible; no material regression. |
| C09_Inventory | Booth display, dose instrument and paper log remain locally readable; no material regression. |
| C10_Workbench | Tool board and seal-repair work surface remain legible; replacement and failed components remain distinct. |
| W01_Personnel | Personnel doorway and route remain clear; no material regression. |
| W02_ReceivingReturn | Shutter and receiving apron remain unobstructed; no material regression. |
| W03_Dispatch | Dispatch opening and adjacent route remain clear; no material regression. |
| W04_CellService | R39's separate steel trunnion faces reduce the former joined-pipe read in this close view. Clear improvement, with tight-crop alignment still visible. |
| W05_ReceivingExterior | Threshold, receiving bay and freight spine remain readable; no material regression. |
| W06_PersonnelExterior | Personnel approach remains clear; no material regression. |
| W07_DispatchExterior | Dispatch approach and room axis remain visible; no material regression. |
| W08_BoothDoor | Inventory booth remains visible through the open door; no material regression. |
| W09_DrySouth | Dry storage closures and local access space remain readable; no material regression. |
| W10_ResidueService | Three overpacks remain legible as storage, but opposed dark side fittings align as pipe-like bridges and weaken sealed-storage clarity. |
| D01_SealRepair | Split rejected seal, replacement ring, removal tool and repair tools remain distinct; no material regression. |
| D02_CaptureService | Both capture mouths and header transition remain visible; no material regression. |
| D03_ExtractionRun | Room-air branches and the filter/fan are visible together; the separate extraction path is clear. |

## Technical evidence and limits

`validation_R39.json` reports PASS: zero protected-pose changes, world strength 0, 26 fixture checks and 23 emissive checks passing, 321 new and 57 inherited support contacts passing, zero unregistered supports, zero sampled route obstructions, 50 freight-aperture checks passing, 575 closed-mesh-normal checks passing, and zero reported issues. The report notes the limits of sampled route rays and lens checks; these do not certify runtime collision or beam-aperture coverage.

`coldstart/comparison_R39.json` reports PASS with zero changed objects/materials and identical scene-state digest. Checkpoint and rebuilt file hashes differ due separate serialization; this is not byte equality. Their fingerprints match across 3,051 objects, 281 materials and the same scene-state digest, and R39 remains source-unchanged. Cold validation also reports PASS at 562,759 triangles. This evidence supports the current provisional technical assessment.

The independent cold pixel comparison for R39 is still running. No exact cold image reproducibility or final technical score is inferred from R37's completed proof. This review does not certify Unity collision, navmesh, runtime lighting or performance.
