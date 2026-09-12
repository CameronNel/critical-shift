# Astra independent visual review — style22 slice

Date: 2026-09-10. **Decision: VISUAL PASS for this slice.** All seven relevant visual categories reach 90 or higher. This is a threshold pass, not a claim of exact reference equivalence, flawless finish or full-module acceptance.

## Evidence and limits

Directly inspected all five actual style22 PNGs: C03_HERO, C09_MATERIALS, D01_CARRIER_OPERATION, D02_WORKBENCH and D03_UTILITY. Reopened and compared the actual approved reactor A05, mine entry/heading/sump and C06 paintover through their supplied same-content JPEG viewing copies in `production/evidence/reference-previews`. Every score below is a fresh judgment of the current pixels; earlier scores and the builder's reported changes are not proof of quality.

Manifest identity: `style22`, `slice`, blend SHA-256 `1f50e64d042f5c3f3d1c40b497c239ac5ae28689c5543de13c66563bec947c3a`. The frozen style22 checkpoint is the relevant P05 source state. Mutable P06 full-only changes are not represented or verified by these images.

The supplied `technical_style22.json` identifies style22 and reports support PASS, packed-material PASS and matching saved/source identity. Its only failed gate is `internal_routes`, explicitly NOT_RUN for the slice. I read the supplied result but did not independently replay its geometric checks. Accordingly, no independent numeric technical score is assigned here.

## Scores

| Category | Score / 100 | Current image evidence |
|---|---:|---|
| Scale / circulation | **91 — local slice only** | C03 provides coherent human-scale doorways, workbench and carrier, with the cart contained in a legible staging bay and open local approaches. The image supports local plausibility, not continuous full-route widths or remote turns. |
| Shape / art direction | **90** | Manufactured framing, carrier saddles/restraints, casters, tool construction and regulator fittings establish specific industrial objects. Broad panel fields and restrained details follow the approved direction. Some close tool profiles remain blunt, limiting refinement but not making the slice read as placeholder geometry. |
| Hierarchy | **92** | Service, freight, staging and maintenance functions are easy to distinguish in C03. The white cartridge against its dark backing, service sign/light and orange floor direction cue establish clear priorities. Detail views preserve the identity of each equipment cluster. |
| Materials | **90** | Concrete, painted framing, exposed steel, cartridge enamel, rubber, brass, textile and filter glass are visibly distinct across the five views. Glove/cloth fabric is readable and the filter interior is visible. Coarse glove weave and broad metal mottling remain minor finish limitations. |
| Lighting | **90** | C03 now preserves visible face differences in the upper crossmembers and enough separation at beam junctions to avoid the previous featureless-band reading. The ceiling pool is softer and no longer overwhelms the surrounding dark structure. Practical sources, local wall pools, readable material highlights and grounded shadows form a coherent whole. Some deep junction shadows and a less nuanced floor-light gradient remain below the references' best finish, but are no longer consequential slice failures. |
| Color | **92** | Cool grey floor, off-white fields, gunmetal and controlled orange consistently match the approved palette. Warm practicals provide separation without flattening the neutral color structure. |
| Environmental storytelling | **90** | Staging/inspection identifiers, checked payload tag, restraint hardware, parking cues, service-air controls and identifiable maintenance items communicate how this junction is used. The orderly bench is credible, though still more arranged than the reference bench. |
| Technical correctness | **Not independently scored** | The supplied slice-applicable audit passes. A fresh independent technical replay, full-route checks, later engineering changes and end-to-end assembly remain outside this visual report. |

## Remaining visible defects

1. **Minor — glove texture is over-prominent in D02.** Its coarse weave competes with some finger folds and the leather patches. Fabric identity is clear, but its texture density is less restrained than the rest of the scene and the references.

2. **Minor — small tool profiles and metal variation lack some refinement (D02/D03).** Spanner ends remain blunt and closely related, while the worktop and exposed pipe finish show broad mottling rather than consistently localized wear. Equipment and material identity remain readable despite this limitation.

3. **Minor — several upper junctions remain dark (C03).** The frame faces are now sufficiently legible, but the deepest beam-to-wall areas and parts of the right gate header still have limited tonal detail. The current light treatment passes; it does not yet equal C06/A05's richest dark-steel response.

4. **Minor — the bench still feels carefully arranged (D02).** Paired gloves, aligned containers and clean labels reduce the sense of an interrupted task. The objects nevertheless establish a sufficiently specific maintenance story for this slice.

No new consequential visual artifact was observed in C09/D01: the payload, restraint fittings, brakes and wheels remain readable, and the earlier pale floor slivers are absent. D03 retains visible filter depth, graduations, housing fittings and distinct control materials.

## Acceptance boundary

This report clears **Astra's visual slice gate** only. It does not clear P05/P06 full-only geometry, gate movement, service-feed continuity, external ownership/mating, nominal port clearance, full routes, final review cycles, cold full-camera renders or runtime handoff. Those require their own built and verified evidence. No source edits, geometry changes, scene operations, neighbor writes or renders were performed; only this report was written.

## Image identity

| Image | SHA-256 |
|---|---|
| C03_HERO.png | `459e6592f0c9a3e5cec1a6d4a78564322e4b0c9bd043c318c7ac4172335a78f0` |
| C09_MATERIALS.png | `f0614484472a90a6fbd8cc4cacb7740422193f624af6ed6fbaf7305a102a97ea` |
| D01_CARRIER_OPERATION.png | `191339e2619769d63cac1a1f9b4ca291a67b53ac76ebbf85316b539a7d9ffc04` |
| D02_WORKBENCH.png | `2f95a1de2b53c7bd0319d00e3129be1bc5c14f50ee7cf9b5ffeff588721af13e` |
| D03_UTILITY.png | `dec8e510d8b79fd8a7d687c30ab1ad13c8e7b77765b461dfb2929683540c4d89` |
