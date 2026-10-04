# Independent pixel review — R37

**Reviewer:** GPT-6 Luna, independent critic B

**Evidence inspected:** all 21 mandatory R37 fixed views, both R37 details (D02/D03), every paired R31 fixed view and both R31 details, plus the specified Spawn and refinery R24 references. R37/R31 fixed poses and optics are matched.
**Decision:** **FAIL** the working target of at least 99/100 in every category. **No automatic visual veto.** The render set is complete and route/process readability is broadly strong, but several visible finish issues remain below the reference-level bar.

## Scores

| Category | Score / 100 | Weighted points | Finding |
|---|---:|---:|---|
| Layout, scale and route readability | 99 | 19.80 / 20 | The central spine, receiving/dispatch ends, cell approaches and service branches read clearly in C01/C03/C04 and W02/W03. No visible route blockage. |
| Art direction, architecture and silhouettes | 96 | 19.20 / 20 | Believable industrial construction and a coherent grounded palette; the broad storage-cell and vessel surfaces still read more generic and less art-directed than the Spawn/refinery finish references. |
| Waste-process hero equipment and functional clarity | 98 | 14.70 / 15 | Casks, transfer cart, four segregated cells, extraction and repair task all read as distinct functions across the fixed and detail views. Minor ambiguity remains in the wide views where broad repeated cell forms dominate over the staged loads. |
| Materials and anti-plastic quality | 95 | 14.25 / 15 | Metal, rubber, wood, glass and concrete are distinguishable, but some broad panels are nearly textureless and selected damage reads as applied dark blobs. |
| Fixture-only lighting and gloomy atmosphere | 97 | 9.70 / 10 | The low-key green-grey mood and localized practical pools fit the brief. Repeated bright ceiling diffusers flatten the central room values in the principal wide views. |
| Purposeful dressing and human storytelling | 97 | 9.70 / 10 | Inventory, workbench, quarantine and maintenance details are authored and task-specific. Several wide views have limited human-use evidence, though the clear negative space is appropriate and is not scored as a defect by itself. |
| Technical cleanliness, contacts and reproducibility | 99 | 9.90 / 10 | R37 authoring validation passes. The original-source cold rebuild matches all 3,051 object and 278 material fingerprints; all 21 fixed views and both details reproduce pixel-identically with matching settings. This is static Blender evidence within the validator's stated sampling limits. |
| **Weighted total** |  | **97.25 / 100** | **FAIL** — the six visual categories remain below 99; technical now meets the 99 target. |

## Highest-impact observed defects

1. **Paint/plaster damage reads as stamped dark blotches.** In C09_Inventory and W03_Dispatch, the low-wall damage clusters have hard, irregular edges and similar dark value, so they read as flat cutouts rather than moisture or contact wear integrated with the wall finish. This is a direct visible material-quality miss against the selective-wear target and is also present in paired R31 views.
2. **Large equipment fields lose object-specific surface character at gameplay distance.** In C02_Casks and W04_CellService, the main cask bodies and adjacent cell panels resolve as broad, nearly uniform grey-green areas beneath the bright collars and fasteners. The hardware gives the vessels useful silhouettes, but the main surfaces do not carry the same controlled tonal breakup and constructed specificity as the refinery R24 process/hero views; the casks consequently read closer to repeated industrial cylinders than individually authored shielded vessels.
3. **Bright fixture lenses draw too much attention in the wide views.** In C01_Entry, C03_Reverse and C04_Route, the diffuser faces are small, nearly white rectangles repeated across the ceiling. The surrounding ceiling stays near-black and the walls/floor are not broadly washed out; the room itself is not over-lit. The issue is the lens-to-room contrast and the repeated clean white bars, which pull attention upward and make the practicals feel newer/brighter than the neglected room. A lower or more varied lens luminance would preserve the existing localized pools and dark intervals without reducing general room readability.

These issues do not create a visual veto: the room remains legible, the dark areas do not erase the central route, and the exterior black beyond the isolated module boundary is excluded by the camera brief.

## Clarification for focused follow-up (scores unchanged)

- **Wall-damage location:** In C09_Inventory, the hard-edged dark marks are on the visible lower wall to the left of the inventory desk/monitor: approximately image x=15–165, y=325–455 in the 960×540 render. The upper/right part of that cluster is partly occluded by the monitor and desk. In W03_Dispatch, the smaller cluster sits on the low west wall immediately left of the dispatch opening/jamb, approximately x=181–210, y=420–456. Repair should make those existing wall areas read as worn paint/plaster with integrated, contact- or moisture-shaped edges; the surrounding surfaces and routes do not need additional dressing.
- **Process deduction (C01_Entry and C03_Reverse):** Both wide views show a readable open freight spine and repeated cage-front bays. At this distance the four functions rely heavily on small, low-contrast wall words (“RESIDUE,” “SHIELDED,” “DRY STORE,” “QUARANTINE”); cage silhouettes and values are similar enough that the difference between sealed residue, shielded hot waste, dry stock and quarantine is less immediate than in C02/C06/C07/W10. Making the existing zone identifiers or a small existing functional color/value cue readable at wide-view scale would improve process sorting without adding objects to the route.
- **Dressing/story deduction (C01_Entry, C03_Reverse and C04_Route):** The wide views communicate storage and a controlled facility, while the overdue maintenance and human interruption story is concentrated in C09_Inventory and C10_Workbench. From the freight spine the evidence is mostly too small/low contrast to read, so the room feels more orderly and anonymous than the close-ups suggest. The material improvement is better wide-view legibility of existing task/maintenance cues at the cell edges or walls; the central route should remain empty.
- **Lighting distinction:** The lighting deduction concerns luminous diffuser faces, not the amount of light spilling into the room. C01/C03/C04 retain dark ceilings, dark intervals and isolated wall pools, so I do not observe broad fill or a flat/flooded lighting veto. Reducing or varying the repeated lens-face brightness would strengthen the gloomy read while preserving the authored practical sources and current local contrast.

## Camera-by-camera comparison

The paired-image comparison record reports the same pose and optics for all 21 fixed cameras. Mean absolute RGB channel delta is shown as R/G/B on the 0–255 scale; deltas describe the observed iteration change, not quality by themselves.

| Camera | R31 → R37 comparison |
|---|---|
| C01_Entry | 3.1 / 3.4 / 3.2; same clear central spine and cell rhythm. Ceiling-panel brightness and broad low-value floor remain. |
| C02_Casks | 3.6 / 3.5 / 3.2; cask pair and extraction bridge remain legible. Broad vessel faces remain visually quiet against detailed collars. |
| C03_Reverse | 2.8 / 3.0 / 2.8; reverse route and rear dispatch read as before; no new occlusion or material regression. |
| C04_Route | 2.2 / 2.4 / 2.2; spine edges and lane markings remain legible. Repeated bright ceiling panels persist. |
| C05_Transfer | 6.4 / 6.8 / 6.4; cart and loaded overpack remain clear; no visible route obstruction or meaningful regression. |
| C06_Dry | 6.2 / 6.3 / 6.2; dry contaminated-equipment zone remains readable; surfaces and storage hardware remain broadly uniform at this view. |
| C07_Quarantine | 2.9 / 3.0 / 2.9; open QH01 state, lid and contained item remain legible; no material regression. |
| C08_Extraction | 4.1 / 4.3 / 4.1; extraction equipment remains a distinct rear-service cluster; no route or lighting regression observed. |
| C09_Inventory | 5.3 / 5.5 / 5.0; booth, inventory screen and dose instrument remain visible. Wall damage still reads as hard-edged blotches. |
| C10_Workbench | 3.7 / 3.6 / 3.2; repair bench, hand tools, gloves and replacement seal remain clear as an uninstalled repair set; no regression. |
| D01_SealRepair | 1.9 / 1.8 / 1.5; close view keeps the split failed seal and separate replacement ring readable; the complete ring is correctly treated as bench stock. |
| W01_Personnel | 8.3 / 8.8 / 8.4; personnel access remains identifiable, but the doorway interior falls to near-black and contributes little view-through context. This is a lesser readability weakness, not a veto. |
| W02_ReceivingReturn | 5.6 / 6.1 / 5.7; receiving apron and central route remain open and readable; no regression. |
| W03_Dispatch | 3.3 / 3.3 / 3.2; dispatch portal and approach remain legible. The low-wall dark damage patches remain conspicuous and decal-like. |
| W04_CellService | 1.7 / 1.9 / 1.7; cask/cell service face remains clear and accessible; broad equipment panels retain the uniform read noted above. |
| W05_ReceivingExterior | 3.0 / 3.3 / 3.0; receiving frame, parked shutter hardware and threshold remain visible. Black adjoining space is outside the authored-room judgment. |
| W06_PersonnelExterior | 2.3 / 2.5 / 2.4; exterior personnel opening and frame remain visible; black beyond the isolated module is excluded. |
| W07_DispatchExterior | 2.4 / 2.6 / 2.4; dispatch frame, tracks and threshold remain visible; black adjoining space is excluded. |
| W08_BoothDoor | 3.1 / 3.5 / 3.1; open glazed booth leaf, aperture and receiving-side approach remain readable; no regression. |
| W09_DrySouth | 7.0 / 7.2 / 7.0; dry-zone pair remains clearly separated with its service access intact; no visible regression. |
| W10_ResidueService | 3.4 / 3.6 / 3.4; sealed residue overpacks and their service clearance remain clear; no route regression. |
| D02_CaptureService | Opened both R31 and R37. Capture mouths, supported header transition and upper clearances remain legible; no visible regression. |
| D03_ExtractionRun | Opened both R31 and R37. The two room-air branches, filter plenum and fan remain connected and distinguishable; no visible regression. |

## Technical evidence scope

R37 checkpoint source SHA-256 is `3c52dd3c926cf2bb7a1c148181b404a7d6a7776d15294ee4d394e49b6569e019`; the independent original-source rebuild blend SHA-256 is `cdeae0a992620227f9d46ee5c45c86c0cd5f357644e41eabb618b61bc2c1422f`. The differing blend-file hashes are serialization differences and are not treated as byte equality. `comparison_R37.json` reports no changed object or material fingerprints and `scene_state_identical: true`; the matched fingerprints cover 3,051 objects and 278 materials. `pixel_comparison_R37.json` reports PASS for all 21 required views, every image pixel-identical with zero channel delta and equal settings. `detail_comparison_R37.json` reports PASS for both D02_CaptureService and D03_ExtractionRun, also pixel-identical with zero maximum channel delta and equal settings. The cold build record confirms the original module hash (`8912b5c3b3d2525abb64e838d1fe83a1ea90aa12fea0c9b5a730d4449caecedf`) and 3,051 output objects. `validation_R37.json` reports PASS, 247 protected items with no changes, 26/26 practical fixture checks PASS, zero world strength, and no issues. This supports reproducible static Blender authoring/contact/process evidence within the validator's recorded sampling limits. It does not certify runtime collision/navmesh, Unity lighting or performance.

## Diagnostic follow-up correction — R38 wall patches

I re-opened the four actual R37/R38 source PNGs individually and verified their hashes. R37 C09_Inventory: `97e73b3c850d94ca372186f79879f24371232ca6e8bce1d9f1eb3dc633c771d3`; R38 C09_Inventory: `0666d4ec819b1c41a9afc05ad0b02d6a0df0ed004cc8ebcbafa1e69aab27b7e8`; R37 W03_Dispatch: `118df6b210dc616be976b713fd421409c2cb0cd9c80ce227e1251bbb4770d700`; R38 W03_Dispatch: `986373fbb0a9bef5a16ca3fb214d367594fd5b1f4f173cf08d3a52eb9ecab09a`. My earlier R38 note that the wall marks looked unchanged was inaccurate. In C09, the lower-left wall variation at approximately x=15–165, y=325–455 is visibly much fainter and more graded in R38; the hard dark cutout read is substantially reduced. W03's small lower-west-wall variation left of the dispatch jamb is also subdued, though faint marks remain. This is an R38 diagnostic observation only; it does not alter the R37 full-cycle scores or acceptance decision.
