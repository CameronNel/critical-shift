# C84 bounded carry review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Candidate SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`  
**Prior reviewed candidate:** `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`  
**Prior source SHA-256:** `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`

## Disposition

I carry forward 61 previously accepted criteria from C82 to C84. The carried IDs are: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 49, 50, 51, 52, 56, 58, 59, 60, 66, 67, 71, 73, 78, 95, 106, 107, 109, 112, 113, 114, 115, 117, 118, 119, 124, 134, 135. Every carried row retains its original C82 evidence source, image path, and image SHA-256 in `LUNA_C84_DISPOSITIONS.json`; those images are historical evidence, not C84 renders.

At the time this bounded carry was written, I reopened **#136** because the prior material-family evidence included drums and C84 edits the drum-bearing material meshes. I also kept **#43** open until the exact C84 full-quality view31 completed. The later view31 review accepted #43 and #136 from the changed drum meshes, paired with historical C79 view01/view02 only for unchanged non-drum materials. See [LUNA_C84_VIEW31_DRUMS_AND_BARRIER_REVIEW.md](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_VIEW31_DRUMS_AND_BARRIER_REVIEW.md). All ten current C84 main views remain required. This remains a bounded carry report, not a final overall acceptance or score.

## Exact bounded delta

The C82→C84 scene comparison at `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` passes. It reports exactly five changed objects:

- `RH refine legacy drums GALV`
- `RH refine legacy drums RED`
- `RH stations props GALV`
- `RH stations props RED`
- `RH stations props YELLOW`

It reports 1,915 unchanged objects and no additions, removals, or unexpected changes. Its comparisons cover the declared per-object transforms, mesh geometry/material indices/smoothing/sharp-edge flags, material graphs and links, light settings, camera settings, parents, visibility, drivers, and action names. It does not establish whole-scene equivalence beyond those declared fields. Carry is limited to criteria whose reviewed subject/evidence is outside those five drum meshes. The all-ten C84 main views are still needed for final whole-room review and scoring.

## Current finite geometry QA (#140)

C84 has 14/14 scoped checks passing in `/workspace/scratch/reactor-refinement-cycle84/checks.json`, and the separate control-room verifier passes in `/workspace/scratch/reactor-refinement-cycle84/control-room-check.log`. The current audit `/workspace/scratch/reactor-refinement-cycle84/audit.json` reports 191 sign records with zero failures, 2,804 contact records with zero failures across 1,956 registered assemblies and 26 covered owner groups, no empty registrations, and 290 protected objects unchanged. These are finite checks and do not claim exhaustive all-pair collision coverage.

## Later full-quality drum evidence

The exact C84 full-quality view31 is `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/inspection-720p/31_props_drum_group.png`, SHA-256 `ca70652e1f16ee719820bc3541d362af29bba5aed105e2dd014900bde9dca811`, 1280×720/96. It closes #43 on the narrower 18 mm by 6 mm hoop profile and #136 on the visible galvanized/painted material distinction. It also supports #44–48 and #53/#57 in the linked view31 report. This image is current C84 evidence; it is not part of the historical carry set.
