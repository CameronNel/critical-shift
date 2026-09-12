# Luna F05 final visual review — Fuel Corridor

**Reviewer:** Luna, independent reviewer  
**Decision:** **HOLD — local visual/technical gates pass; canonical cold reproducibility remains unresolved**

I inspected all sixteen F05 PNGs directly at 1440 × 960 and compared them with the current reactor-Valorant direction and approved concept family. This is Fuel Corridor scope only. Runtime, assembled neighboring geometry and gameplay approval remain outside this review.

## Evidence identity

`production/renders/review/final-F05/cold_render_manifest.json` contains all ten mandatory and six diagnostic views from a fresh background process. The exact candidate hash is unchanged through rendering:

`f11dc1c5210f0d7c0552db0aafc1148724b54ef6beb0ce6abc6e9d0e42c85c6b`

F05 technical status is PASS. The source replay reports 7,979 baseline and reproduction objects with no missing, added or changed transforms/base meshes/fonts/lights/cameras/bevels. The material replay reports no changed, missing or added materials, UV sets or packed textures. These are strong candidate checks; they are builder-run replay evidence rather than a new independent engineering signoff.

The F05 engineering-motion replay samples 39 authored gate states. Its eight reported moving/fixed pairs are contact-only zero-depth events: four roller/rail contacts across the sampled motion and four one-state rivet/track tangent contacts. It reports no crown/tray, external-door/ceiling, service-station or architecture collisions, plus zero service-air loop/endpoint gap. This supports the modeled-contact score while remaining bounded: the replay is a retained builder replay, finite samples are not a continuous sweep, and it does not prove engine physics, structural load or runtime door control.

The manifest records `scene_saved: false` and `saved_file_unchanged: true`; this is the expected read-only render behavior for an already saved checkpoint, not evidence of an unsaved artifact. The candidate is therefore visually and technically reviewed as the exact rendered checkpoint. The canonical second cold all-camera render completed against the same hash, but its pre-established pixel threshold fails on C08; twelve player-eye approaches and a repeatability resolution remain required before the saved-artifact/reproducibility category can be treated as unconditional.

The cold comparison passes 15 views at max channel difference 1–2/255. C08 has 332 pixels above 2/255 in a narrow 5-pixel-wide vertical right-wall support edge (`x1052–1056`, `y537–716`), with maximum channel difference 7/255 and mean 0.00210865/255. Direct inspection shows the F05 and cold C08 images visually identical at scene scale, but CPU/source tracing identifies a real coplanar construction between the rear upright flange and `washable_lower`, rather than generic renderer noise. The threshold is a hard evidence gate and is not waived. F06 is correcting that bounded construction issue; F05 remains a reproducibility failure.

## Independent 17-category scores

Every category clears 90 for the F05 candidate. Conditional evidence is marked explicitly; no runtime or unassembled-neighbor claim is hidden in a visual score.

| Category | F05 score | Evidence and limits |
|---|---:|---|
| Specification coverage | 93 | All sixteen designated views render, all named freight/service/destination subjects are present, and F05 technical gates pass. Runtime interaction, engine collision/navmesh, audio and networking remain outside this slice. |
| Facility / process logic | 92 | Carrier, route markings, destination doors, bench, service-air station and gate now read as one operating corridor. Refinery-to-reactor payload conversion/ownership remains an integration contract gap. |
| Human scale | 94 | Door leaves, guard rails, carrier, handles, tools and service hardware maintain believable industrial scale. Character traversal and assembled clearance are not runtime proof. |
| Player circulation | 93 | C01–C08 show clear route lines and turns with no F00 black floor artifact; C07/C08 branch reads are strong. Runtime navigation and the neighboring door states remain unverified. |
| Freight / cart handling | 93 | C09/D01 visibly prove a supported single-cartridge carrier with wheels, restraints, lifting eyes and parking bounds. F05 motion replay reports contact-only zero-depth events, but this is not engine carriage approval. |
| Maintenance access | 93 | D02, D03 and D06 show reachable tool, utility and service-air stations; D05 shows readable drive access. Full player interaction is outside the slice. |
| Interface consistency | 92 | F01/F02/S01/S02/S03 labels and local mappings agree with P07, with unchanged interface hash in F05. F01/F02 assembled fit, closed reactor fuel doors and S01/S02/S03 destination fit remain unverified. |
| Machinery construction | 94 | Carrier, gate motor, reactor leaves, service-air assembly and bench read as layered, fastened built assemblies with appropriate operational labels. |
| Physical support / contact | 92 | F05 CPU technical audit passes geometry, support chains and routes; source/material replays are identical. The independent engineering evidence is builder replay and still bounded to modeled contacts, not structural load or engine physics. |
| Valorant shape language | 93 | Controlled off-white, charcoal, orange safety language, bold panels, restrained bevels and readable industrial forms match the grounded direction. No teal drift is visible. |
| Material separation / anti-plastic | 94 | Metal, rubber, painted panels, concrete, glass, tools, straps and cartridge surfaces separate strongly in C09/D01–D06 and remain coherent in the route views. |
| Lighting / readability | 93 | Practical pools explain the corridor, all destination labels remain readable, D04 header contrast is corrected, and no F00 floor artifact is visible. |
| No-teal color discipline | 94 | Direct inspection shows warm ivory/off-white, charcoal/gunmetal and orange safety accents without visible teal or cyan drift. |
| Signage / numbering | 93 | C01–C08 and C10 clearly carry F01/F02/S01/S02/S03 identities, arrows, transfer roles and stand-clear labels. C03's incidental FG01 header is frame-cropped only; the dedicated gate views carry its full proof. |
| Environmental storytelling | 92 | Carrier handling, checked labels, workbench tools, service-air controls, gate drive, plant/waste/clean doors and route markings create a believable active facility. Quiet circulation margins remain intentional. |
| Camera coverage | 93 | All sixteen fixed cameras are present in the manifest and serve their designated purposes. C03's incidental FG01 frame crop and D02's top-line crop do not prevent their intended composition reads. |
| Saved-artifact / source / dependency reproducibility | 90 **FAIL / conditional** | F05 hash-bound manifest, source replay and material/UV/texture replay are clean, but canonical cold comparison fails the hard max-2/255 rule on C08's narrow right-wall support edge. CPU/source tracing identifies a real coplanar rear-flange/`washable_lower` construction. `scene_saved:false` is expected read-only behavior; F06 must correct and re-audit this issue, followed by twelve player-eye approaches. |

## Per-view scores

| View | Score | Direct result |
|---|---:|---|
| C01 ENTRY | 93 | Freight arrow/label, carrier, F02/REACTOR cue and SERVICE/BYPASS branch read together; quiet foreground is usable circulation margin. |
| C02 PRIMARY ROUTE | 94 | Foreground board competition is removed; S03/WASTE and F02/REACTOR are separated with clear arrows and subtitles. |
| C03 HERO | 93 | Strong service, F02, S02, carrier and route composition; incidental FG01 header crop does not block navigation proof. |
| C04 REVERSE | 94 | F01/REFINERY overhead and side board, door labels, orange edge treatment and reverse approach are clear. |
| C05 EAST TURN | 93 | S03/WASTE advance and doorway headers are readable through the turn; route line and arrow lead cleanly. |
| C06 REACTOR THRESHOLD | 94 | F02/STAND CLEAR plates, layered panels, fasteners, handles, wear and orange accents are crisp. |
| C07 BYPASS | 93 | S01/PLANT overhead and angled identities plus S02/CLEAN and floor turn marking give an unambiguous branch read; black patch is gone. |
| C08 SERVICE JUNCTION | 92 | S02/CLEAN sign and arrow remain readable with clear open route; no inherited black floor artifact. |
| C09 MATERIALS | 95 | Carrier body, straps, lifting eyes, clamps, saddles, tray, wheels, labels and parking boundary are exceptionally clear. |
| C10 PLANT HEADER | 94 | Paired S01/PLANT doors, header, stand-clear plates, lower hardware and work-point board read completely. |
| D01 CARRIER OPERATION | 95 | Handling hardware, restraint logic, labels, wheels and contact surfaces are highly legible. |
| D02 WORKBENCH | 93 | Tools, lock, gloves, grease, flask, case and bench hardware tell a clear maintenance story; top line is lightly cropped by the fixed composition. |
| D03 UTILITY | 95 | SERVICE AIR label, pipe bends, valve, gauge, regulator, hose and mounts have strong separation. |
| D04 REACTOR WIDE | 94 | Corrected dark-on-light F02/REACTOR header is readable; layered doors, wear and transfer labels hold at wide scale. |
| D05 GATE MECHANISM | 95 | Motor fins, orange ring, terminal, warning plate, backing, supports, rail and identity label are crisp and operationally believable. |
| D06 SERVICE RECESS | 95 | Service-air panel, gauge, wheel, regulator, pipework, hose and mounts remain a strong tactile close-up. |

## Final conditional status

F05 is the first candidate in this pass whose complete sixteen-view pixels, CPU technical audit, source replay and material/UV/packed-texture replay all clear the requested strict-above-90 bar. I find no remaining broad visual defect in the complete F05 pack. The canonical cold pack is visually equivalent at scene scale, but its C08 pixel comparison exposes a real narrow coplanar construction at the right-wall support edge; this remains a reproducibility failure until F06 corrects and rechecks it. The read-only render manifest's `scene_saved:false` flag does not mean the source artifact was unsaved.

**Luna F05 result: 16 visual categories above 90 and all 16 views above 90; saved-artifact reproducibility is 90/fail pending C08 repeatability and player-eye evidence. No runtime or whole-map approval.**
