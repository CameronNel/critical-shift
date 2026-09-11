# Luna R07 final review

**Reviewer:** Luna, independent final reviewer  
**Date:** 2026-09-11  
**Evidence:** R07 warm renders C01–C10 and W01–W06, independent cold renders in `production/renders/review/cold-R07/`, both render manifests, `production/validation/R07/technical.json`, `technical.md`, `exhaust-aperture.json`, `cold-comparison.json`, `source-readback.json`, `snapshot-a.json`, `snapshot-b.json`, `live-scene.json`, updated architecture floorplan PNG/SVG and `architecture/design_checks.json`  
**Scope:** final local Turbine Room scenery acceptance; no geometry, camera, material or interface edits

## Final evidence boundary

R07 contains the complete defined local hall: ten fixed views C01–C10 and six player-height walkthrough views W01–W06 at 1440 × 900. I inspected every warm and cold image directly. The cold batch was rendered from an independently reopened saved artifact. `cold-comparison.json` reports all 16 comparisons with a maximum channel difference of 1/255, mean differences of approximately 0.000034–0.000046 in 8-bit channel units, and changed-pixel fractions below 0.000183. The tiny numeric differences are render-process variance; visual content, text, dials, lighting, materials and composition remain consistent across warm and cold pixels.

The saved semantic evidence is stable. Snapshot A and B share the R07 artifact fingerprint `04c0a25d777cab961b8a411aed6f73ae18f7afb2925912be1cfca5ca262f4606`, the same blend hash, 1661 objects, 28 materials and 16 cameras. The live scene receipt also reports 1661 objects and the named portal and interaction markers. `source-readback.json` is PASS for all nine saved authoring sources. This is sufficient cold saved-artifact evidence for the defined local scenery review.

The R07 technical audit is **PASS** with 1661 objects and 1567 meshes. Support coverage, visible contact islands, dimensions, interface markers, route and portal clearances, machine axis, symmetry, build manifest and snapshot stability pass. `geometry.topology` remains **REVIEW** for intended open cloth/text and related open surfaces. `geometry.hidden` remains **REVIEW** because hidden render geometry requires explicit intent review. These reviews do not identify a visible R07 defect, and they are not a claim that every authored asset is a watertight solid or that hidden geometry is mechanically certified.

The previously held U04 requirement is now proven by saved evaluated geometry. `exhaust-aperture.json` is PASS for a 2.5 × 1.5 m opening centred at `(4.6, 11.45, 0)`: 15 downward evaluated rays through five target objects are unobstructed, and an adjacent solid-floor positive control confirms the test direction. The audit proves the opening only; it does not claim a condenser, flow simulation or neighbor construction.

The updated floorplan PNG/SVG visibly draws and labels `U04 / DOWN` inside the turbine envelope and states the real exhaust opening dimensions in the interface notes. The U03 annotation is clear of the D02 heading. `architecture/design_checks.json` records 20 design-arithmetic checks, all PASS. This is plan consistency evidence, not a replacement for the saved geometry audit.

The acceptance boundary is the defined local hall. The unassigned underfloor condenser owner, remote steam source, reciprocal electrical completion, reserved Fuel Corridor and other neighbor modules remain documented open interfaces. They are not missing R07 deliverables. Runtime speed/load/output state, audio, incidents, engine navmesh, collision, networking and whole-map transforms remain handoff responsibilities and are not claimed by this local Blender acceptance.

## Independent category scores

All eight requested categories are scored independently from the combined 16-view pixels and measured saved evidence. No score is averaged across categories.

| Category | Score /100 | Disposition | Evidence and limits |
|---|---:|---|---|
| Specification coverage | 93 | **Approved for defined local hall scope** | R07 visibly covers the staged turbine/generator train, separate throttle/load, SPEED/HEALTH/OUTPUT/DEMAND/RESERVE/SAFETY readbacks, guarded trip and coupling, bearing and oil service, maintained bench/tools, D01/D02 routes, reachable STEAM ISOLATE, diegetic service labels and local integration markers. The actual U04 opening is now proven. Runtime behavior/audio/incident implementation and unassigned neighbor machinery remain outside this scenery acceptance. |
| Layout flow | 94 | **Approved** | W01 gives a complete D01 entry read; C01/C03/C04/W03 establish the central rescue/cart route; C05/W06 show the east service aisle and steam service; W04 shows the north crossover and maintenance bay; W05 shows the oil-service approach. Saved route, portal, aisle, crossover and support checks pass. Engine swept-volume behavior is not claimed. |
| Machinery | 94 | **Approved** | C01–C03 establish the full train and process order, C07 clearly presents the guarded coupling/shaft, C09 gives the generator end and support, and W06 shows the service valve in context. HP/LP casing breaks, inspection covers, bearing supports, bus-side utility and generator separation remain readable at room scale. |
| Navigation readability | 93 | **Approved** | W01 fully reads `REACTOR / D01`; C01/C04/W03 read `ELECTRICAL / D02`; C08/W04 read `MAINTENANCE / 02`; W05 reads `LUBE / 01`; W06 reads `STEAM ISOLATE`; W02 reads all six control headings plus `THROTTLE`, `LOAD` and `TRIP`. C06 still crops the first letters of `HEALTH` at the inherited oblique camera edge and W04 crops the electrical sign’s suffix at the image edge. These are framing limitations, not lettering cut by geometry; complete reads exist in the combined acceptance set. |
| Construction | 94 | **Approved** | Foundations, soleplates, pedestal feet, split casing bands, fasteners, guard frame, crane, supported utilities, oil cabinet, bench and service valve read as grounded authored assemblies. Technical visible-contact and support checks pass. Topology/hidden reviews retain their stated open-surface limitations. |
| Materials | 92 | **Approved** | The final pixels maintain matte cream casing, charcoal structure, oxide-orange service surfaces, warning yellow, dark floor, warm timber, paper and bare metal with purposeful variation and restrained localized wear. C10 supports the bearing/bench material story. Large architectural fields remain quiet by design and do not drift into photorealistic grime. |
| Lighting | 92 | **Approved** | Suspended practicals, warm task lighting, readable contact shadows, controlled roof contrast and consistent exposure survive both warm and cold reopen renders. W01 keeps the D01 sign legible against the dark door; W02 keeps dials readable without glare; W05/W06 preserve service-point contrast. This is a grounded game-space treatment rather than a cinematic lighting claim. |
| Reference fidelity | 94 | **Approved** | R07 follows the strict A05/A08/A09/A10 language: broad planar forms, controlled matte response, ivory/charcoal/oxide orange and safety yellow, restrained wear and specific industrial silhouettes. No teal, A07 branding, slogans or external game/company marks appear in the reviewed final pixels. |

All eight categories independently meet the 90 threshold for the defined local Turbine Room. This acceptance does not expand the assignment into whole-map, runtime or neighbor certification.

## All-view pixel findings

### C01–C05 fixed views

- **C01 entry:** The room presents a clear central route, a dominant but readable machine train, overhead crane and `ELECTRICAL / D02` destination. The left controls are intentionally edge-cropped; this is a camera composition limit, not a scene text cut.
- **C02 hero:** Cream HP/LP casing, oxide section, dark coupling, LUBE / 01 panel and pedestals produce the strongest machine silhouette. Surface variation stays matte and planar in the cold pixel set.
- **C03 reverse:** The generator end, dark reverse machinery and `REACTOR / D01` destination establish orientation from the opposite direction. The route remains open beside the train.
- **C04 route:** The yellow guide lines lead to D02. `MAINTENANCE / 02` is intact in front of the structural column, and the oil-service corner reads beside the route. The former sign-splitting defect is absent.
- **C05 east service:** The side aisle and wall utility pipe remain visibly separate from the train base. The white service drop is supported and does not intrude into the central route frame.

### C06–C10 fixed views

- **C06 throttle:** `OUTPUT`, `DEMAND`, `RESERVE` and `SAFETY` are fully legible with analog dials and pointers. `HEALTH` loses only its first letters at the left image edge because this inherited oblique detail camera begins inside the panel; W02 supplies the complete control bank. `THROTTLE`, `LOAD` and `TRIP` remain identifiable on the physical ledges.
- **C07 coupling:** `GUARD / 01`, the yellow cage, dark coupling and shaft are clear. The guard reads as a physical hazard barrier with a visible shaft behind it.
- **C08 maintenance:** The `MAINTENANCE / 02` sign, bearing-service sheet, oil stand, timber bench, vise, bearing cradle, tools and D02 doorway form a coherent repair bay. The scene remains source-safe and no branding is visible.
- **C09 generator:** The ribbed generator end, supports, utility leads and distinct electrical body read cleanly. Output-side runtime behavior remains a handoff responsibility.
- **C10 materials:** Bearing, cradle, wrench, rag, paper and timber worktop show the intended tactile material family. The clean broad surfaces are deliberate and do not undo the localized use history.

### W01–W06 walkthrough views

- **W01 entry return:** The corrected 4.2 m view fully shows `REACTOR / D01`, threshold, door and floor guide lines. It provides real entry orientation and is no longer a blank-door close-up.
- **W02 controls full:** All six status headings and analog pointer dials read together under `TURBINE CONTROL`. The separate throttle/load levers and guarded trip are visible below. This is complete control coverage even though C06 remains an oblique detail crop.
- **W03 south cross:** The south crossover, central route and D01 destination are clear. The distant controls are intentionally secondary because W02 covers their detail.
- **W04 north cross:** `MAINTENANCE / 02`, bench, oil stand and crossover are clear. The electrical header is cropped at the right image edge; it is not physically cut, and D02 is fully readable in C01/C04/W03.
- **W05 oil service:** `LUBE / 01`, its analog dial, guard and surrounding rails are clear at a useful service distance. The close framing is paired with C08/W04 for the wider bay and route.
- **W06 steam service:** The geared red handwheel is visibly reachable at the authored player-height view, and `STEAM ISOLATE` is fully readable. The vertical drop still occludes part of the casing, but it no longer hides the operation point or creates an ambiguous destination. U04’s below-floor opening is separately proven by the aperture audit rather than inferred from this view.

## Final review result

**R07 is approved for the defined local Turbine Room scenery scope.** All eight categories independently score 90 or higher, all 16 warm views and all 16 cold views are visually consistent, the saved technical audit passes, the U04 opening is proven by 15 unobstructed evaluated rays with a positive control, the semantic snapshots match, source readback passes, and the updated plan is consistent across its 20 design checks.

The acceptance preserves the documented boundaries: topology and hidden-geometry checks remain REVIEW with their stated intent limitations; engine behavior and whole-map integration are not certified; unassigned neighbor modules and the condenser remain open interfaces. No geometry, camera, material, footprint or interface was changed by this review.
