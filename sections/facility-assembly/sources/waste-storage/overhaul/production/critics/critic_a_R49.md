# Independent visual review — Waste Storage R49

**Result: FAIL against the working 99-per-category gate.** I individually opened all 21 mandatory R49 views and both supplemental details beside their R45 counterparts. The paired comparison verifies all 21 image hashes and identical fixed-camera matrices, lenses and render settings. Main and detail manifests are complete and source-unchanged at SHA-256 `7f8d5aa91cb9d8131b7396bddb94327796d05fd484e64b6ed5984671e8ac1c6b`.

| Category | Score | Weight | Weighted points |
|---|---:|---:|---:|
| Layout, scale and route readability | 99 | 20% | 19.80 |
| Art direction, architecture and silhouettes | 99 | 20% | 19.80 |
| Waste-process hero equipment and functional clarity | 99 | 15% | 14.85 |
| Materials and anti-plastic quality | 98.5 | 15% | 14.775 |
| Fixture-only lighting and gloomy atmosphere | 99 | 10% | 9.90 |
| Purposeful dressing and human storytelling | 99 | 10% | 9.90 |
| Technical cleanliness, contacts and reproducibility | 99 | 10% | 9.90 |
| **Weighted total** |  | **100%** | **98.925 / 100** |

**Working gate:** FAIL. Materials are below 99. Technical now passes at 99 after inspection of R49's completed original-source state and 23-view pixel proof. **Critical visual veto:** none observed. **Highest-impact observed defect:** the broad lit faces of SC01/SC02 remain too uniform and smooth for the requested worn-down finish; the new chips do not break up those large uninterrupted shell areas at the fixed-camera crops. No score is raised for implementation effort or object count.

## Pixel findings

The R49 contact exposures are a clear improvement over rejected R46. In **C02_Casks** and **W04_CellService**, the small old-undercoat reveals are discrete and plausible around handling hardware, carrier edges and lower contact/nameplate zones. They are restrained at normal camera size, with no broad cloud, camouflage field, crisp repeated decal or new process cue. The previous W10 trunnion solution also remains legible as separate solid handling ends rather than a pipe joining adjacent vessels.

The remaining materials deduction comes from the large shell areas between those marks. In **C02_Casks**, the lit front of SC02 remains a mostly uninterrupted gray-green surface; in **W04_CellService**, most of SC01's broad visible face has the same smooth, even response. The few chips are too small and localized to change that overall read. This leaves the illuminated hero shells looking comparatively uniform beside the deliberately battered room and does not quite meet the reference-level wear/material response I expect for this brief. That is the only category I place below 99.

Across the other fixed views, routes, portals, storage-cell approaches and work clusters remain readable. The paint, concrete, steel, rubber, cloth, paper and wood retain distinct responses. Practical fixtures remain the only visible light sources; the result stays dark and gloomy while preserving local legibility. The actual Spawn polish images provide a clean hierarchy and prop-finish anchor, while refinery R24 provides the darker, more worn mood. R49 keeps that hierarchy and mood, but the broad cask coating still falls short of the latter's material wear.

My earlier paired reviews found no material regression from R31 to R37 and from R37 to R39. R39 to R45 likewise showed no material regression, with the W10 handling-end separation improved. R45 to R49 adds restrained, plausible contact wear and shows no material regression in the broader scene. It does not fully resolve the broad-shell surface-uniformity issue described above.

## Paired camera ledger

| Camera | R49 vs R45 observation |
|---|---|
| C01_Entry | Freight spine and receiving-to-rear sightline are unchanged in practical use; the new cask finish does not distract at this distance. |
| C02_Casks | Small contact chips are visible and not stamp-like; SC02's broad lit face remains smooth and uniform. |
| C03_Reverse | Reverse lane, storage rhythm and rear opening remain readable; no material regression. |
| C04_Route | Cell turns and lane markings remain legible; no route or lighting regression. |
| C05_Transfer | Staged incoming overpack remains supported on the cart; no material regression. |
| C06_Dry | Dry-store lids, bars and service clearance remain readable; no material regression. |
| C07_Quarantine | Open quarantine unit and retained filter remain understandable; no material regression. |
| C08_Extraction | Filter/fan and duct remain visible; no material regression. |
| C09_Inventory | Booth display, dose meter and shift log remain legible; no material regression. |
| C10_Workbench | Tool board and seal-repair dressing remain distinct; no material regression. |
| W01_Personnel | Personnel portal remains legible; no material regression. |
| W02_ReceivingReturn | Shutter edge has a slight brightness/inner-frame read difference from R45, but the opening, apron and route remain clear. The render-state audit confirms unchanged evaluated geometry, pose and settings. |
| W03_Dispatch | Portal contrast shifts slightly at the dark inner edge; the opening and adjacent route remain readable. Audit confirms no geometry or camera change. |
| W04_CellService | Contact chips are restrained and localized; the broad SC01 shell still reads smooth and even. Trunnion ends remain solid and separate. |
| W05_ReceivingExterior | Rear opening edge/value is slightly different, but receiving bay and freight spine remain clear; no material regression. |
| W06_PersonnelExterior | Slight edge/brightness difference at the foreground jamb; booth and center route remain visible. Audit confirms no wall or camera geometry shift. |
| W07_DispatchExterior | Dispatch axis and clear center route remain readable; no material regression. |
| W08_BoothDoor | Inventory station remains visible through the open doorway; no material regression. |
| W09_DrySouth | Dry-container closures and local access remain legible; no material regression. |
| W10_ResidueService | Filled trunnion end faces remain separate and do not imply a continuous connection; no material regression. |
| D01_SealRepair | Rejected seal, replacement ring, removal tool and repair tools remain distinct; no material regression. |
| D02_CaptureService | Capture mouths and supported header transition remain visible; no material regression. |
| D03_ExtractionRun | Room-air branches and filter/fan remain legible together; the path remains distinct from vessel contents. Small shell chips do not confuse the process read. |

The apparent doorway/frame changes I initially flagged in W02, W03, W05 and W06 are small pixel-level value/edge differences, not geometry or pose changes. `render_state_audit_R45_R49.json` reports identical evaluated mesh vertices and polygon-material indices, ray visibility, render/Cycles/color-management properties, view-layer exclusions/holdouts, and camera/light fingerprints. I therefore find no actual portal or wall shift and no material route-readability regression in those views.

## Technical evidence and limits

`validation_R49.json` reports PASS with zero issues: 247 protected poses unchanged; world strength 0; 26 fixture checks and 23 emissive checks passing; 335 new and 57 inherited support contacts passing; zero unregistered supports and sampled route obstructions; 50 freight-aperture checks passing; zero disabled material links; 26 projected-wear face checks passing; and 579,788 evaluated triangles. Closed-mesh normals and the authored process-path checks also pass. The supplied validation states that sampled route rays and fixture-seat/aperture tests do not certify exhaustive collision or full beam coverage.

The inspected `coldstart/comparison_R49.json` reports original-source state replay PASS with zero changed objects/materials and identical scene state; the fingerprints cover 3,065 objects and 290 material graphs. I inspected this shared-workspace evidence but did not run a separate rebuild myself. `coldstart/pixel_comparison_R49.json` and `coldstart/detail_comparison_R49.json` both report PASS: all 21 mandatory views plus D02/D03 are RGB-identical, with zero maximum channel delta, under equal render settings. `validation_R49_cold.json` also passes at 579,788 triangles. Separate blend file hashes reflect serialization differences and are not byte-for-byte equality. This evidence supports the final technical score of 99. This report does not certify Unity collision, navmesh, runtime lighting or performance.
