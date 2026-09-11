# Luna R06 final-candidate review

**Reviewer:** Luna, independent pixel reviewer  
**Date:** 2026-09-11  
**Evidence:** R06 fixed renders C01–C10, R06 walkthrough renders W01–W06, `production/renders/review/R06/render_manifest.json`, `production/validation/R06/technical.json` and `technical.md`, `snapshot-a.json`, `snapshot-b.json`, and `live-scene.json`  
**Scope:** independent final-candidate visual review of the defined local Turbine Room; no geometry, footprint, interface, or camera edits

## Candidate boundary and cold evidence

R06 is a complete 16-view batch at 1440 × 900: ten fixed cameras plus six walkthrough cameras. The manifest records all 16 files and their hashes under revision R06. I inspected every image directly.

The saved technical result is **PASS** with 1660 objects and 1566 meshes. `support.visible_contact_islands`, dimensions, local interface markers, all listed route and portal clearances, axis, symmetry, build-manifest and snapshot-stability checks pass. `geometry.topology` remains **REVIEW** for intended open cloth/text and other open surfaces; it is not reported as a technical FAIL. The validation document explicitly says this is geometry evidence and not a cold-start render acceptance.

The cold semantic evidence is strong: snapshot A and snapshot B share blend hash `16947db01526fba2713267e57ca4fc67c98c7439209c1d40d457b7f91d5a4517`, artifact fingerprint `44896c32e4f4fa9dcb2bfa4d5933919afcd37014e8441e4a53afa6605d69f6cb`, 1660 objects, 28 materials and 16 cameras. The live scene reports the same 1660-object count and the named portal/interaction markers. This establishes saved-file semantic stability, but the planned final-artifact cold render is still pending.

This review uses the local integration scope. The unassigned condenser neighbor, remote steam source, reciprocal electrical neighbor and other neighboring modules are open interfaces, not absent deliverables. Runtime audio, incident behavior, engine navmesh and collision certification are outside the saved local Blender evidence. The owned U04 below-floor exhaust handoff is different: it requires direct confirmation that the saved scene contains an actual geometric opening rather than only a marker. That check is still pending in the current evidence.

## Independent R06 category scores

These scores cover the eight requested categories independently. They are final-candidate scores from the complete visual set and saved technical evidence, not final approval before the cold artifact render.

| Category | Score /100 | Status | Evidence and remaining condition |
|---|---:|---|---|
| Specification coverage | 89 | **Hold / preliminary fail** | The set visibly covers the turbine/generator train, speed/load controls, six state readbacks, health/safety/trip, reserve, guarded coupling, maintenance bench, bearing service, oil cabinet, D01/D02 route, steam-isolate valve and local utility markers. The actual U04 below-floor exhaust opening has not yet been proven from saved geometry; the technical check reports markers and local interfaces but does not establish that opening. Runtime audio/incident behavior is also not measured here. If U04 is marker-only, the local handoff remains incomplete; if a real opening is confirmed, this category can be reconsidered against the existing visible coverage. |
| Layout flow | 93 | **Candidate pass** | W01 now shows a full D01 entry and guide lines; C01/C03/C04 and W03 show the central route; C05/W06 show east service; W04 shows the north maintenance crossover; W05 shows the oil-service reach. Technical route, portal and aisle clearances pass in the saved audit. Engine swept-player/cart behavior remains unproven. |
| Machinery | 94 | **Candidate pass** | C01–C03 establish the staged cream/oxide turbine train, C07 makes the shaft guard and coupling legible, C09 gives the generator a distinct end and support system, and W06 shows the steam service point. C02/C09 remain close asset views, so output-side runtime behavior is not claimed. |
| Navigation readability | 93 | **Candidate pass on combined coverage** | W01 fully reads `REACTOR / D01`; C01/C04/W03 clearly read `ELECTRICAL / D02`; C08/W04 clearly read `MAINTENANCE / 02`; W05 clearly reads `LUBE / 01`; W06 clearly reads `STEAM ISOLATE`; W02 reads all six control headings and physical control labels. Fixed C06 still crops the left edge of `HEALTH`, and W04 crops the electrical sign’s right suffix at the image edge. These are camera framing crops, not text geometry cuts, and combined coverage remains sufficient. |
| Construction | 94 | **Candidate pass** | R06 shows grounded soleplates, feet, split casing bands, guard frame, crane, supported utility runs, oil cabinet, bench and service valve. The saved technical PASS verifies visible contact islands and authored support roots; topology REVIEW is limited to intended open surfaces. Mechanical stability and engine collision remain outside the audit. |
| Materials | 92 | **Candidate pass** | R06 has controlled matte variation across cream casing, charcoal structure, oxide service panels, dark floor, wood bench, paper and metal. C10 shows purposeful bearing/bench contrast and R06 avoids the earlier uniform flat fill. Large wall and casing fields remain intentionally quiet; the result stays graphic rather than photographic. |
| Lighting | 92 | **Candidate pass** | Suspended practicals, warm task light, readable contact shadows and dark roof framing establish a coherent industrial hall. W01’s dark door is now legible because the D01 sign and threshold are in frame. The fixed detail crop in C06 is bright but readable; the cold artifact render must confirm the same exposure and text contrast. |
| Reference fidelity | 94 | **Candidate pass** | R06 consistently follows the strict A05/A08/A09/A10 direction: no teal, broad planar value blocks, restrained oxide orange and warning yellow, matte painted surfaces, authored signs and grounded mechanical silhouettes. No A07 game/company branding or slogans appear. |

The only category below 90 is specification coverage, pending direct U04 opening confirmation. No final whole-room approval is issued until that handoff and the cold artifact render are independently checked.

## Complete-view findings

### Fixed views C01–C05

- **C01 entry:** The D02 electrical destination is readable, the central route is open and the machine hierarchy is immediate. The left control row is intentionally cropped by the frame; this does not cut the scene text or geometry.
- **C02 hero:** The cream casing stages, oxide section, dark coupling and LUBE / 01 panel read as a coherent train. The close framing emphasizes the machine over the route, as intended for a hero view.
- **C03 reverse:** The generator end and `REACTOR / D01` destination are readable. The reverse view provides a second orientation cue rather than relying on a single door sign.
- **C04 route:** The central yellow guide lines lead toward D02, and the maintenance sign now sits visibly in front of the structural column with its wording intact. The earlier sign-splitting defect is not present in this pixel set.
- **C05 east service:** The side aisle, lower wall utility pipe and turbine service side read clearly. The frame is sparse enough to communicate the aisle; the pipe does not enter the route as the earlier overshoot did.

### Fixed views C06–C10

- **C06 throttle:** Actual dials and pointers are now visible for the state cards. `OUTPUT`, `DEMAND`, `RESERVE` and `SAFETY` read clearly. `HEALTH` loses its first letters only because the inherited oblique detail camera begins at the image edge; W02 supplies the complete control panel. The control text is not cut by a neighboring mesh.
- **C07 coupling:** The yellow guard, shaft, dark end-bell and `GUARD / 01` plaque are clear. The grid communicates a physical hazard barrier and the coupling remains visible behind it.
- **C08 maintenance:** `MAINTENANCE / 02`, bearing-service paper, oil stand, bench, bearing cradle, tools and D02 doorway form a coherent service corner. The sign is fully legible and not occluded by the column.
- **C09 generator:** The generator’s ribbed end, pedestal supports and cable/terminal housing read as a distinct electrical machine. Its close framing does not prove neighbor bus mating or runtime output behavior.
- **C10 materials:** The bearing, cradle, wrench, rag, paper and timber worktop show the intended matte, used material family with restrained localized wear. No teal or external branding is visible.

### Walkthrough views W01–W06

- **W01 entry return:** This correction is successful. At the full entry distance, `REACTOR / D01`, threshold, door and floor guide lines are all visible. It now provides useful orientation and is not the blank door close-up from R04.
- **W02 controls full:** All six headings—`SPEED`, `HEALTH`, `OUTPUT`, `DEMAND`, `RESERVE`, `SAFETY`—are legible. Each card has a visible dial and pointer; the separate `THROTTLE`, `LOAD` and `TRIP` affordances are readable below. This view supplies the complete control coverage missing from C06.
- **W03 south cross:** The south crossover and central route read clearly, with D01 at the left and the control bank at the far side. The controls are too distant for detailed readback evidence here, but W02 covers that requirement.
- **W04 north cross:** The maintenance sign is centered and legible, with the bench, oil stand and crossover visible. The electrical header is cut at the right image edge; this is a camera crop, not geometry cutting the lettering. D02 is fully readable in C01/C04/W03.
- **W05 oil service:** `LUBE / 01` and its analog dial are readable, with the guarded coupling and utility rails behind. This is a clear oil-service interaction context, while the wider route is covered by C08/W04.
- **W06 steam service:** The geared red steam-isolate wheel is reachable in the view and `STEAM ISOLATE` is legible on its marker. The vertical service pipe still occludes part of the casing, but the operation point is no longer ambiguous and the prior sign obstruction is removed. This view does not prove the separate below-floor U04 opening.

## Remaining checks before final artifact review

1. Confirm from saved evaluated geometry that U04 at `(4.6, 11.45, 0)` has a real open exhaust handoff and is not only an empty/interface marker. If marker-only, specification coverage remains below 90.
2. Run the planned cold final-artifact render from the saved R06 scene and compare all 16 outputs for exposure, text, dial visibility, matte response, and no-teal/source safety. The current manifest is a warm rendered batch plus cold semantic snapshots; it is not the final artifact proof.
3. Preserve the combined-view interpretation for C06 and W04. Their edge crops are framing limitations with complete text visible in other accepted views, not evidence of mesh intersections or cut lettering.

## Review result

**R06 is a strong final candidate with one explicit coverage hold.** Seven categories independently meet 90 on the combined 16-view pixels and saved technical PASS. Specification coverage is 89 until the owned U04 below-floor opening is directly verified. The C06 `HEALTH` and W04 electrical suffix issues are image-edge crops; all required control and portal labels are fully readable elsewhere, and no text is physically cut by geometry in the inspected views. No geometry, interface, footprint, material or camera was changed by this review.
