# Luna takeover baseline — Turbine Room

**Reviewer:** Luna, independent read-only baseline reviewer  
**Date:** 2026-09-11  
**Scope:** recovered turbine checkpoint, current design/interface documents, canonical brief/spec references, and completed Cooling Plant final pixels used as style calibration

## Review boundary

This is a baseline report, not an approval. No numerical score is assigned to the unreviewed slice-05 candidate, no concept or component is approved, and no final-room category is claimed at 90 or above. The report records what is visible in the saved evidence and what is still absent from the build.

The prior slice gate and its four full-room correction-cycle requirement are historical process evidence. The current takeover direction calls for the whole room early and does not make expansion wait on another fixed slice or cosmetic cycle. The slice remains useful as a defect record and style reference; it is not acceptance evidence for the complete room.

## Evidence inspected

- `sections/turbine-room/CONTINUE.md`, `README.md`, `architecture/ARCHITECTURE.md`, `architecture/MACHINE_DESIGN.md`, `interface.json`, `production/CAMERAS.md`, `production/RUBRIC.md`, `production/TASK_STATE.md`, and `production/TECHNICAL_VALIDATION.md`.
- Actual slice-05 pixels: `production/renders/review/slice-05/C08_maintenance.png` and `C10_materials.png`, with the slice-05 render/build manifests.
- Prior independent pixel reviews for slices 01, 02 and 04, plus the retained objective validation notes.
- Canonical `turbine-room.md` brief and the current `GAME_SPEC.md` sections covering reactor/power variables and controls, incidents/recovery, facility sequence/modularity, information and audio, and host authority.
- Completed Cooling Plant final pixels `W01_ENTRY_APPROACH`, `C02_HERO`, and `C10_MATERIALS`, and its R10 handoff as the current no-teal room-quality calibration.

## Saved-state truth

The recovered room has a metric architectural design: a 14 m by 24 m hall, 7.2 m clear height, opposed reactor/electrical portals, a continuous central route, west control and maintenance bays, an east service aisle, and documented steam, condensate, and generator-output interfaces. These are design bounds and interface intent, not proof that the saved Blender scene or runtime currently satisfies them.

The saved/rendered checkpoint is `slice-05`. It contains the original maintenance slice: a bench, vise, bearing/cradle, oil stand, work props, doorway, practical light, utilities and local architecture. Only C08 and C10 have actual slice render evidence. The eight other fixed cameras are definitions with stated unbuilt coverage.

The full conversion train is absent from the recovered source. The design specifies an HP-to-LP segmented turbine, bearings, shaft, coupling guard, generator, output terminal region, inlet branch, controls, service access and incident/readback hooks, but these remain design-only requirements. `build.py` references a future `hall.py`, while that module is absent; therefore a manifest string naming `blender/hall.py` must not be treated as proof of a full-hall build. The blend is an incomplete checkpoint, not a whole-room artifact.

The interface remains unbound to neighboring sections. Facility transforms, reciprocal portal acceptance, steam source, condensate destination, and electrical output adaptation are pending. The machine design also leaves the LP exhaust-to-condenser handoff unresolved and correctly warns that a drain collector is not itself a condenser. Those open dependencies must remain explicit during production and must not be silently filled with invented neighboring geometry.

## Visible baseline defects in slice-05

The images are stronger than the earliest slice, but they still expose the same baseline problems recorded by the prior independent reviews:

1. **Palette conflict with the takeover direction.** C08 is visually led by petrol/teal door, column, bench and oil-stand masses. C10 also carries a teal architectural field behind the bearing. The current request is no teal. The final palette needs to follow the Cooling Plant calibration: warm ivory/institutional neutrals, charcoal and steel, restrained oxide orange, and purposeful hazard yellow. Existing teal material names or prior design language are not final-room authority.
2. **The rendered content is a maintenance vignette, not a turbine hall.** C08 proves a bench corner and doorway; C10 proves a close bearing/worktop read. Neither view establishes the hall's HP/LP silhouette, generator, coupling, central route, east service aisle, controls, overhead process routing, or electrical handoff.
3. **Large architectural fields remain simplified.** The wall, doorway surrounds and vertical structural members read as broad clean masses. The doorway's dark destination is still visually shallow, and the sign/threshold must be rechecked for unobstructed navigation in the complete room. This is a baseline observation; candidate05 is not transferred a pass from the earlier review.
4. **Surface history is too light and too graphic.** Painted surfaces and the worktop remain broadly uniform and new. The small wear marks read as placed accents rather than contact, handling, grime, or maintenance accumulation. The final room needs selective, material-specific use evidence while preserving the restrained Cooling Plant cleanliness.
5. **Lighting lacks consistent room-scale hierarchy.** C08 has a useful work light and contact shadows, but broad ambient exposure still dominates the wall and doorway. C10 gives the bearing a broad bright highlight and a relatively even worktop. Full-room practicals need to create purposeful pools, quiet shadow, legible route transitions, and readable control/machine priorities.
6. **The hero objects are still local props, not authored machine assemblies.** The bearing/cradle and vise have improved construction cues, but the surrounding architecture and utility details remain more generic than the approved reference standard. The future train must be designed in primary silhouette, functional secondary construction, and restrained tertiary detail before labels or wear are added.
7. **Human evidence remains staged.** The paperwork, mug, cloth and orderly worktop communicate “maintenance” but not a particular live job, fault state, or worker routine. The completed room needs a coherent service story tied to bearing oil, coupling access, controls, incident response, or repair staging.
8. **Technical status is unresolved.** Slice-04 had objective failures involving bevel degeneracy, support/contact associations, detached or intruding elements and other measured issues. Later source corrections and slice-05 have not received a fresh complete technical audit. Pixel contact impressions do not replace a saved-file validator result.

These observations are deliberately limited to what the pixels and retained records support. They do not claim that every earlier defect persists in slice-05, and they do not assign slice-05 scores.

## Historical failed record

The last formal pixel review was slice-04 and failed expansion. Its independent scores were: scale/circulation 87, shape/art direction 83, hierarchy 82, materials 75, lighting 80, color 90, and environmental storytelling 77. Technical correctness was left unscored because objective validation was not accepted. Slice-05 is newer but unreviewed; those numbers must not be copied forward or used as a final-room score.

The required whole-room evidence count at takeover is therefore zero accepted final cycles, zero accepted final cameras, and zero accepted category approvals. The incomplete history is retained because it explains why the old slice cannot authorize propagation.

## Full-room review coverage required by takeover

The final rubric retains eight independently scored categories. Each category must reach at least 90 on its own, with evidence attached to the saved revision. A pleasing average or a strong close-up cannot compensate for a failed category.

| Category | Required whole-room evidence before any approval |
|---|---|
| Scale / circulation | Saved-file measurements against the architectural/interface bounds; continuous D01-to-D02 route; portal and aisle clearances; machine/service envelopes; conservative cart/rescue and crossover sweeps; fixed-camera route readability. Design arithmetic alone is insufficient. |
| Shape / art direction | Independent pixel review of the train silhouette and each major assembly: HP/LP casing progression, bearings, shaft, coupling guard, generator, controls, utility supports and doorway construction. The room must read as grounded stylized industrial work with authored secondary forms rather than boxes, cylinders, or repeated bevels. |
| Hierarchy | All ten fixed cameras, especially C01/C02/C03/C04, proving entry orientation, the conversion train as hero function, control priority, service-route guidance, and destination signage. No light, pipe, prop, or label may steal or obscure a critical read. |
| Materials | Close and gameplay-distance pixels showing distinct painted metal, steel, rubber, fabric, wood/concrete and process surfaces; controlled roughness and selective wear; no broad pristine toy/plastic response. Compare against the Cooling Plant finals. |
| Lighting | Fixed settings and pixel comparison across all ten cameras, with local practical influence, contact grounding, machine depth, route visibility, and controlled highlights. Broad flat exposure or glare over signage is a fail condition. |
| Color | Explicit palette audit showing no teal in final room assets or architecture, with the no-teal Cooling Plant relationship preserved: warm ivory/neutral shell, charcoal/steel structure, restrained oxide orange, hazard yellow and only purposeful small status accents. Color must support state and wayfinding without noise. |
| Environmental storytelling | A readable operating/maintenance narrative: active conversion train, control/readback cluster, bearing-oil and coupling service logic, repair staging, incident cues, paperwork/signage and human traces that explain the current job. Props must have functional placement and condition rather than display dressing. |
| Technical correctness | Fresh CPU saved-file audit on the authoritative `.blend`: camera contract, metric configuration, finite/evaluated geometry, normals/topology, zero-area/coincident surfaces, dependencies, support/contact registry, route/portal volumes, assembly connections, machine axis/symmetry contract, and exact interface markers. Any failure remains a failure; this category receives no invented score. |

Final camera coverage must include C01 entry, C02 hero, C03 reverse, C04 route, C05 east service, C06 throttle, C07 coupling, C08 maintenance, C09 generator and C10 materials. C08/C10 slice evidence cannot stand in for the absent eight views. The review set must be rendered from the saved authoritative revision, with stable settings recorded, then reopened in a fresh Blender process and rerendered for cold-start comparison.

## Production requirements for the next review

The builder may proceed directly to whole-room production under the takeover direction. The first complete room pass needs the designed train and control/utility relationships present together so that camera composition, route, machine hierarchy and color can be judged in context. Keep the section local and preserve the interface IDs and documented envelope intent while neighbor transforms remain unbound.

The HP inlet/lift relationship must be made visibly serviceable: the removable final branch and its isolation logic need to coexist with the overhead lift reservation. The LP exhaust/condenser dependency must be either resolved through a separately agreed interface or clearly documented as a gameplay abstraction; U02 condensate return alone does not prove a complete thermodynamic loop. Small component removal can be shown only after actual disassembly, support and carried-envelope checks; the design does not authorize a claim that a complete 4.2 m train exits through a 2.4 m personnel portal.

The saved room should retain editable named assemblies and reproducible source. Runtime collision, navigation, interaction reach, door/guard animation, host-authoritative machine state, incidents, audio and network relevance remain engine handoff checks. Blender completion can document their markers and contracts but cannot claim those runtime systems are implemented.

## Baseline disposition

**Status: FAIL / takeover baseline only.** The recovered slice is useful evidence of prior construction progress and of defects to avoid. It is not a full turbine room, not a final style approval, not a technical pass, and not evidence that any of the eight final categories meets 90. Whole-room authoring and independent all-ten-camera review are the required next evidence, with the no-teal mandate applied from the first complete-room pass.
