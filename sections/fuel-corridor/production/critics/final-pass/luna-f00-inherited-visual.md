# Luna F00 inherited visual review — Fuel Corridor

**Reviewer:** Luna, independent final-pass review  
**Artifact:** `blender/Fuel_Corridor.blend`  
**Decision:** **REJECT / HOLD** for the F00 inherited artifact

This is a fresh pixel review of the exact F00 saved artifact. I opened all sixteen PNGs directly and compared them with the current reactor-Valorant direction and approved C07/C09/C10 concept family. This is Fuel Corridor scope only; it is not runtime, assembled-facility or whole-map approval.

## Provenance

`cold_render_manifest.json` records a fresh background render of revision `full04`, stage `full`, with the same SHA-256 before and after:

`7d25367ddbc5d1fb3463e00026c2ba1438afda0d4704afdfad78ff096477c3f5`

All ten mandatory and six diagnostic views are present. `scene_saved: false` and `saved_file_unchanged: true` are preserved in the manifest. This is valid fresh pixel evidence for that exact inherited file, while the source/save reproducibility issue and F00 technical failures remain separate blockers.

## Category scores

Scores are independent; a strong close-up does not conceal a weak route view. The requested strict-above-90 bar is not met by this artifact. The seventeen categories below are the categories specified by `production/FINAL_PASS.md`.

| Category | F00 score | Direct evidence and unresolved issue |
|---|---:|---|
| Specification coverage | 90 | All ten mandatory and six diagnostic views exist, and the named freight, service, reactor, plant, clean and waste subjects are visible. F00 technical failures and unverified engine/runtime requirements prevent a complete specification pass. |
| Facility / process logic | 89 | Carrier, bench, service-air station, gate and route cues imply a working transfer corridor, but refinery-to-reactor payload conversion/ownership and the closed reactor fuel passage remain unresolved. |
| Human scale | 92 | Doors, rails, cart, carrier and service hardware read at believable industrial scale. Character-scale traversal and assembled clearances remain unverified by the interface audit. |
| Player circulation | 90 | The route is visually readable, but C07/C08 contain a hard-edged black floor artifact and the F01/F02 sampled clearances are not runtime proof. |
| Freight / cart handling | 90 | C09 and D01 show a convincing loaded carrier and restraint logic, but cart sweep, F01 bollard clearance and end-to-end loaded handling are unverified. |
| Maintenance access | 91 | D02, D03 and D06 show reachable tools, fittings, gauge and service-air hardware; D05's lower drive is dark and the full maintenance route is not runtime-tested. |
| Interface consistency | 89 | Local F01/F02 headings and normals match P07 source contracts, but the current refinery save changed identity, F02 doors remain closed, and assembled sill/stub plus S01/S02/S03 fit are unverified. |
| Machinery construction | 91 | Carrier, workbench, service-air and gate components read as built assemblies, while D04 wide reactor construction is sparse and D05 is softer than the approved mechanism reference. |
| Physical support / contact | 84 | F00 technical audit records six zero-area lower trims and unregistered wayfinding support members. Pixel-visible hardware cannot establish valid support chains. |
| Valorant shape language | 89 | Warm off-white, charcoal and restrained orange are grounded in the approved industrial language, but broad route and reactor leaves carry less authored panel/wear density than the approved reference family. |
| Material separation / anti-plastic | 91 | C09, D01, D02, D03 and D06 show convincing metal, rubber, paint, glass, tools, fittings and wear; broad doors and D05 remain softer and less differentiated. |
| Lighting / readability | 89 | Practical pools and warm/cool value separation work in close views, but C07/C08 show the black floor overlap, D04 washes the reactor header, and D05's task lamp dominates the drive. |
| No-teal color discipline | 93 | F00 pixels use controlled concrete/off-white, charcoal steel and orange safety accents with no teal drift. |
| Signage / numbering | 89 | Freight and destination labels are legible overall, but C02's foreground REACTOR cue competes, C03 CLEAN is cropped, C05 WASTE is occluded and D04 REACTOR loses contrast. |
| Environmental storytelling | 90 | Carrier operation, bench tools, grease/flask case, service-air fittings, destination boards and gate hardware imply an active facility; the long route and reactor threshold have lower maintenance-story density than the reference set. |
| Camera coverage | 92 | All sixteen designated cameras render successfully and each intended subject is present, with the noted crop/occlusion and wide-scale hierarchy defects. |
| Saved-artifact / source / dependency reproducibility | 84 | Fresh F00 provenance is hash-bound and packed, but `scene_saved:false`, F00 source SHA mismatch, support failure and degenerate geometry prevent reproducible final acceptance. |

## Per-view scores

These are visual view scores only, with the reason each view is below the requested strict-above-90 bar called out where applicable.

| View | Score | Finding |
|---|---:|---|
| C01 ENTRY | 90 | Service header dominates the first read; freight is carried mainly by the floor route and carrier. |
| C02 PRIMARY ROUTE | 89 | Foreground F02 / REACTOR board is oversized in the frame and competes with the central destination cue. |
| C03 HERO | 90 | Carrier and FREIGHT header are strong, but the far CLEAN cue is partly cropped at the left edge. |
| C04 REVERSE | 93 | F01 / REFINERY doorway and route read cleanly with coherent proportions and lighting. |
| C05 EAST TURN | 89 | WASTE advance board is partly occluded by the nearby frame/door assembly. |
| C06 REACTOR THRESHOLD | 89 | REACTOR threshold is legible, but broad leaves and wall fields have less local hardware/wear density than the approved reactor reference. |
| C07 BYPASS | 87 | S01/S02 and branch arrow read, but the black rectangular floor artifact is a conspicuous current-scene defect and S01 is partly occluded. |
| C08 SERVICE JUNCTION | 88 | CLEAN/WASTE cues read, but a second hard-edged near-black floor region appears under/behind the left orange protection post; junction dressing is sparse. |
| C09 MATERIALS | 94 | Strong carrier close-up: cask, restraints, eyes, brakes and material separation are clear and tactile. |
| C10 PLANT HEADER | 92 | PLANT doorway and header are grounded and readable; minor lower-door shadow line does not obscure the subject. |
| D01 CARRIER OPERATION | 94 | Convincing operational hardware, restraint logic and material variation. |
| D02 WORKBENCH | 92 | Tools, gloves, grease, flask and case tell a clear maintenance story; the upper RETURN AFTER USE text is cropped. |
| D03 UTILITY | 94 | Gauge, valve, hose, pipe, fittings and labels have excellent separation and authored detail. |
| D04 REACTOR WIDE | 88 | Full doorway is present, but bright REACTOR lettering loses contrast and the leaf fields are visually sparse at wide scale. |
| D05 GATE MECHANISM | 90 | Motor, fins, terminal, cable and brackets are inspectable, but the bright task lamp and dark lower drive reduce material/hardware hierarchy versus the approved drive reference. |
| D06 SERVICE RECESS | 94 | Service-air panel, gauge, wheel, regulator, pipework, hose and mounting hardware form a clear, tactile industrial close-up. |

## Required follow-up evidence

F00 remains rejected even though D05 is now inspectable in this fresh pack; the historical full03 D05 black/unusable failure remains part of the record and is not silently replaced. The F00 technical report must also remain attached: six degenerate lower trims, unregistered wayfinding supports and source/save hash mismatch are evidence failures for this exact inherited artifact.

The next candidate needs a fresh saved-scene pack after its technical corrections, with all sixteen direct PNGs and a matching manifest. The visual review should specifically recheck the C07/C08 floor artifact, route-board hierarchy and occlusion, D04 header contrast, reactor-threshold density and D05 material hierarchy. A passing candidate must separately demonstrate the required technical replay, source match, support contacts, saved-file reopen and route/integration limits documented by the architecture handoff.

**Luna F00 status: REJECT / HOLD. No complete-scene or runtime approval.**
