# Luna final-pass inherited survey — Fuel Corridor

**Reviewer:** Luna independent final-pass reviewer  
**Scope:** saved-scene provenance, architecture/interface, inherited visual evidence and acceptance gaps  
**Decision:** **HOLD — pre-render survey; complete F00 score is in `luna-f00-inherited-visual.md`**

This is the required pre-render survey of the current Fuel Corridor artifact, retained as the evidence-bound pre-render record. The complete F00 pixel review is now in `luna-f00-inherited-visual.md`; that report supersedes the temporary no-score state below while preserving the inherited evidence and failures. This file is not whole-map approval or runtime approval. I independently read the current section brief, `BUILD_BRIEF`, the current reactor-Valorant art/spec documents, the section architecture/interface records and the prior full-scene and engineering reviews. I inspected PNG pixels directly where available. No scene or source file was edited.

## Current artifact identity

The current mutable artifact is:

`sections/fuel-corridor/blender/Fuel_Corridor.blend`

The read-only saved survey at `production/evidence/final-pass/inherited-survey.json` records:

- SHA-256: `7d25367ddbc5d1fb3463e00026c2ba1438afda0d4704afdfad78ff096477c3f5`
- 7,939 scene objects and 33 materials
- 16 cameras, matching the ten mandatory plus six diagnostic names
- Cycles, 1440 × 960 at 100%, 32 samples, AgX Medium High Contrast, exposure +0.10
- packed T01/T02/T03 material images and no linked libraries
- scene revision `full04`, `stage` `full`, wayfinding revision `walk02`

This identity differs from the earlier paused full04/walk02 hashes documented in the shared status history. Those older hashes and captures are retained historical evidence; they are not assumed byte-identical to the current artifact.

## Architecture and interface audit

The authored section topology is coherent on its own terms: a 38.20 m freight centreline from F01 to F02, a 23.40 m service bypass, two freight turns, one internal freight gate and reserved S01/S02/S03 service headers. The interface document gives explicit dimensions and normals for F01/F02/S01/S02/S03. Door and destination semantics agree with the corrected walkthrough record: F01 refinery, F02 reactor, S01 plant, S02 clean, S03 waste and FG01 internal freight gate.

The interface also records limits that remain open and must stay visible in the final handoff:

- F01 has an upstream bollard-reduced width of 2.49 m and only a 2.40 × 2.20 m sampled clearance; assembled fit is unverified.
- F02 is a source-derived reactor stub with neighboring doors occupying the receiving line; the neighboring owner/runtime opening and assembled fit are unverified.
- S01, S02 and S03 are reserved connector openings whose destination dimensions are unverified.
- Travel figures are design estimates, not runtime timing proof.
- Engine collider cooking, navmesh baking, door controllers, audio assets/mix, networking, runtime physics and neighboring passage remain pending or unverified in the handoff.

These are honest integration boundaries, not failures of the local topology. They prevent a corridor-only result from being presented as assembled facility approval.

## Inherited pixel evidence

The only complete prior visual batch is full03, and it remains rejected. Luna's direct full03 review recorded a black/unusable `D05_GATE_MECHANISM.png`, with equipment 88 and environmental storytelling 89; Astra independently also found art 89, hierarchy 89 and lighting 88, with inconsistent exposure on branch signs and reactor-wide presentation. Those reports remain valid historical failures.

The interrupted full04 directory contains only C01–C05. Those five images cannot establish a complete cycle and are not treated as current all-camera evidence. The scoped walk02 PNGs support the corrected door/signage walkthrough only. The eng10 gate-drive PNG remains a bounded component review and was rejected for material identity 88 and Valorant art fidelity 89; it is not full-scene evidence. No visual category is rescored here from these historical or scoped captures.

The fresh F00 saved-scene batch subsequently completed all sixteen views and is scored independently in `luna-f00-inherited-visual.md`. The early partial observations remain useful context: C01 gives the overhead SERVICE cue strong forward priority while freight is carried mainly by the floor route; C02 introduces a prominent near-left F02 / REACTOR board beside the central destination board; C03 has a strong carrier/service composition while its left clean cue is partly cropped by the frame. The complete report assigns the resulting category and per-view scores.

The complete F00 manifest now binds the C07 finding to the exact inherited render. In `C07_BYPASS.png`, the S01 / PLANT and S02 / CLEAN cues are legible and the branch arrow is readable, but a distinct black rectangular patch appears on the floor at the lower-left foreground. The scored report records it as a current visual defect. The S01 board is also partly occluded by the near frame, although its principal destination text remains visible.

C08 keeps the clean and waste destination cues readable, but a second hard-edged near-black floor region is visible beneath/behind the left orange protection post at the junction. The repeated dark floor artifact across C07/C08 is scored as an unresolved current-pixel defect in the complete report. The builder later traced the scene cause to a floor-cell overlap, but this inherited visual report does not alter the F00 score from that diagnosis.

Additional partial-pack observations: C02's foreground F02 / REACTOR advance board occupies a large portion of the left edge and competes with the central destination board; C03's oblique composition leaves the far S02 / CLEAN board partly cut by the left frame while the carrier and FG01 / FREIGHT header remain strong. C05's S03 / WASTE advance board is partly occluded by the nearby frame/door assembly even though the main transfer header is readable. These are hierarchy/framing observations only; the complete set is required before deciding whether they materially lower a category.

Against the approved C07/C09/C10 reference pixels, the current C06 reactor leaves and C07/C08 branch views retain the right warm off-white, charcoal and orange language but are materially quieter: broad panel fields and repeated destination boards carry less localized wear, hardware variation and maintenance-story density than the reference family. The current C10 gate-drive component image remains a separate eng10 rejection for material identity and Valorant art fidelity. This is a current art-direction risk for the eventual full review, not a score or a prescription for replacement geometry.

D04 is present in the current pack. The complete F02 / REACTOR doorway reads at wide scale, but its bright header lettering has low contrast against the illuminated header face, repeating the earlier exposure concern recorded by Astra. The wide leaf fields remain visually sparse compared with the approved reactor-door reference. This is scored in the complete report.

## Current technical blockers and reproducibility gaps

The fresh CPU run recorded in `production/evidence/final-pass/F00-technical.json` failed with three gates:

1. **Geometry:** six wayfinding lower-trim meshes contain zero-area faces: `East_reactor_route_lower_trim`, `Bypass_clean_route_lower_trim`, `Plant_branch_identity_lower_trim`, `Clean_leg_identity_lower_trim`, `Waste_marker_lower_trim` and `Entry_marker_lower_trim`.
2. **Support contact:** the wayfinding marker assemblies are not registered as support-dependent geometry in this current saved scene. The failure includes the marker backing/trim/standoff/foot/fastener and text members for the waste and entry markers. The existing walk02 evidence therefore cannot substitute for a fresh full-scene support replay.
3. **Source match:** the saved scene records build source SHA-256 `4bc2aa1a1ed9a81cadf37ec55873ca1e1d8ba898db3f8eba2035865684c46d92`, while the current `build.py` hashes to `9b7e5e793f6a33e904092cda2ceeebcdf4f11ad958fd7d8e9a71db19f95df54a`. Detail source and interface hashes match. The current scene is therefore not yet reproducibly tied to the present source set.

The same F00 run is a genuine fresh background CPU replay, but it is a technical failure, not a visual approval. Its output must remain attached to the final record; do not collapse it into a generic PASS because earlier eng12 targeted checks passed.

## Required evidence before scoring

The next visual review must wait for a complete fresh saved-scene render pack from the exact artifact under review. It needs all ten mandatory and six diagnostic views, a matching render manifest and saved-file hash, with actual PNG inspection. The pack must be provenance-linked to the corrected source state after the current technical findings are resolved. A partial five-image batch, prior full03 images, walk02 captures, component inspection PNGs, object counts or JSON camera declarations cannot establish the final art, lighting, materials or storytelling scores.

Until that pack and a passing technical replay exist, this report assigns no category scores and makes no claim that every relevant category is above 90. The section remains pending final correction cycles, stable final-two proof, cold reopen/render comparison and the documented section-only handoff.

## Review boundary

This survey covers the Fuel Corridor section only. It does not approve or reject neighboring room source, assembled facility placement, engine runtime, whole-map travel, networking, audio, collision cooking or gameplay. It supplies observed defects and evidence requirements without coordinate recipes or replacement geometry prescriptions.

**Luna inherited final-pass status: HOLD pending corrected saved artifact, complete fresh render pack and technical replay.**
