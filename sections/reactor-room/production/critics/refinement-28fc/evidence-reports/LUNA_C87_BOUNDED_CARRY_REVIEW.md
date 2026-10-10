# C87 bounded issue carry and source lineage

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle87/hall_final.blend`  
**Current SHA-256:** `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`  
**Parent C86 SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`

This is a rolling review snapshot, not final acceptance or scoring. All ten 1280×720 main views remain required from exact C87, along with mapped state and direct inspection views. Exact C87 view36 has now been reviewed for the narrowly visible floor criteria #64, #65, and #75; no other appearance acceptance is inferred from it.

## Exact C86→C87 comparison

[`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle87/scene-delta.json) SHA-256 `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be` passes: three changed entries (`R2 floor`, diffuser steel shell, diffuser dark channel/core), 1,930 unchanged, no adds/removals/unexpected changes. The C87 corrections reduce aggregate albedo variation and relief on the floor and replace the closed-ring diffuser with actual side-window geometry. The current support, geometry and cold-rebuild gates are recorded in [`LUNA_C87_GEOMETRY_AUDIT_140.md`](LUNA_C87_GEOMETRY_AUDIT_140.md).

## C87 accepted dispositions

There are **97 accepted IDs** at this snapshot: 90 narrowly carried C86 acceptances plus current C87 #7, #64, #65, #75, #85, #92 and #140. The C86 image paths, manifests, hashes, and earlier source chain remain nested in the JSON prior-evidence records; none is relabeled as a C87 render.

The changed `R2 floor` aggregate material initially reopened several accepted floor criteria because it could affect their visible appearance. After exact view36 review:

- #61, wet/oil/dirt separation — needs current C87 main03 and direct view61 context.
- #63, slab material variation — needs current C87 main03/full floor context.
- #64 and #65, crack relief/branch hierarchy — accepted from exact current C87 view36.
- #66, route paint wear — remains open for current C87 main03.
- #75, floor visual noise — accepted from exact current C87 view36; the coarse angular aggregate islands are gone.

Exact C87 view36 now resolves #64, #65, and #75; see [`LUNA_C87_VIEW36_CRACK_FLOOR_REVIEW.md`](LUNA_C87_VIEW36_CRACK_FLOOR_REVIEW.md). Exact C87 view62 resolves #85; these conclusions are specific to those subjects and crops. Other pending/partial IDs remain open. See `LUNA_C87_DISPOSITIONS.json` and the item-by-item map for all 140 statuses and current requirements.

## Historical source chain for carried image evidence

| Link | Source comparison | Exact result |
|---|---|---|
| C82 → C84 | [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle84/scene-delta.json), SHA `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67` | Five drum meshes changed; 1,915 unchanged; no unrelated changes. |
| C84 → C86 | [`c84-to-c86-scene-delta.json`](/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json), SHA `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19` | 41 changed, 13 additions, 1,879 unchanged, no removals/unexpected. |
| C86 → C87 | [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle87/scene-delta.json), SHA `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be` | Three changed entries, 1,930 unchanged, no additions/removals/unexpected. |

Relevant candidate source hashes: C82 `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`; C84 `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`; C86 `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`; C87 `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`. The C84→C86 and C86→C87 scopes leave the historical door, steam-joint, stool/drain, splice, and gauge subjects outside changed entries. C87 changes concrete material, so old floor appearance is not carried for the reopened rows above.

The original pixel identities for door/steam/drain/stool/splice supplements remain in [`LUNA_C86_SUPPLEMENTAL_FAMILY_CARRY.md`](LUNA_C86_SUPPLEMENTAL_FAMILY_CARRY.md). The sixteen mixed-source gauge image paths/hashes and C79/C80 source identities remain in [`LUNA_C86_MIXED_SOURCE_GAUGE_CARRY.md`](LUNA_C86_MIXED_SOURCE_GAUGE_CARRY.md) and its linked C84/C82 reports. C87 changes no gauge object, face, materials, camera, or lighting; these remain criterion-specific historical carries, not current C87 panels. The exact source and image hashes are preserved in those records.

## Limits

The C87 geometry gates are finite. The C87 preview images are not accepted. No final score is assigned until every criterion has adequate evidence, all ten exact-C87 main views are reviewed, and the final source reaches at least 90 overall and 85 in each of the nine score areas.
