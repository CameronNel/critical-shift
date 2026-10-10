# C87 historical supplemental-family evidence carry

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle87/hall_final.blend`  
**Current SHA-256:** `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`

This report preserves the C86 historical-family carry on the new C87 candidate. It does not relabel old images or claim fresh C87 pixels. The exact C86 table of original image paths, image hashes, and their C80/C82 source hashes remains in [`LUNA_C86_SUPPLEMENTAL_FAMILY_CARRY.md`](LUNA_C86_SUPPLEMENTAL_FAMILY_CARRY.md); the immutable images and manifests remain in their original C80/C82 evidence folders.

## Source lineage

| Comparison | Exact scope |
|---|---|
| C80 lower-splice original | C80 `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`; full view51 `c80/mechanical-proofs-720p/51_column_splice_lower.png`, image SHA-256 `43a5c45b33dd7e3cc71fe41aace4c3ac080d2407f1344dd466886ecd765d7659`. |
| C82 `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` → C84 `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06` | [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle84/scene-delta.json) `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67`: five drum meshes changed, 1,915 unchanged. |
| C84 → C86 `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f` | [`c84-to-c86-scene-delta.json`](/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json) `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19`: 41 changed/13 added, 1,879 unchanged, no removals/unexpected. |
| C86 → C87 `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13` | [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle87/scene-delta.json) `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be`: three changed entries (`R2 floor`, diffuser shell, diffuser core), 1,930 unchanged, no additions/removals/unexpected. |

C87 leaves the historical door, steam tap, annular drain, stool, and splice geometry outside the changed set. Because the concrete aggregate material changed, #71 is carried for annular channel geometry/construction only; C87 current main04 remains necessary for floor-context appearance. Other supplemental-family scopes remain as described in the C86 report. The upper trolley image remains partial and does not close #108.

## Carried historical families

The following C86 carry table is incorporated without changing any image identity: door hardware #124 (C82 native54–56 and full57), annular channel #71 (C82 native34, geometry only), stool #56 (C82 native43), steam weld #38 (C82 full17), column splice #112 (C80 full51 and C82 full53), and partial upper trolley #108 (C82 full52, still pending complete load-path evidence). Exact SHA-256 values and manifest paths are retained verbatim in the linked C86 report; this report asserts no new C87 image evidence for these rows.
