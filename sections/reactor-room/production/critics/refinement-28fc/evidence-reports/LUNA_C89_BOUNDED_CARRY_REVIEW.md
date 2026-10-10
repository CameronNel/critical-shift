# C89 bounded carry review

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Current SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`  
**Parent candidate:** C88 `85766edcb5cf1ba1d5fa9bc624a956132885298e9c379aad3867a1fca0560cf6`  
**Current source delta:** [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle89/scene-delta.json), SHA-256 `10465cf8bd40ab5583827107465da2d49ef4ebc59d45fc16b9df7a8d4abc5320`.

## Disposition

I carried the 96 previously accepted non-#140 criteria from the C88 review under a criterion-specific scope. #140 was independently rerun and accepted only for the finite current-C89 geometry/support scope; its report is [`LUNA_C89_GEOMETRY_AUDIT_140.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C89_GEOMETRY_AUDIT_140.md). This yields 97 accepted items in the rolling snapshot, with the same 43 pending IDs (including 2 partial dispositions). No final score is assigned.

The accepted pixel evidence remains tied to its original exact source, image hash, manifest, camera, and quality settings in the nested prior evidence of [`LUNA_C89_DISPOSITIONS.json`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C89_DISPOSITIONS.json). Nothing in this carry is relabeled as a current C89 render.

## Exact five-leg lineage

| Source leg | Delta SHA-256 | Declared scope |
|---|---|---|
| C82 `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` → C84 `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06` | `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67` | Five named drum meshes changed; 1,915 unchanged; no additions/removals/unexpected changes. |
| C84 → C86 `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f` | `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19` | 41 changed, 13 added, 1,879 unchanged; scoped board/floor/rod/inlet changes. |
| C86 → C87 `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13` | `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be` | Three named floor/diffuser meshes changed; 1,930 unchanged; no additions/removals/unexpected changes. |
| C87 → C88 `85766edcb5cf1ba1d5fa9bc624a956132885298e9c379aad3867a1fca0560cf6` | `852b2d50e4293200ea86437a776ab3c31a3fbec68af745bccc10046d1cb028dd` | `RH walls girders STEEL` finish changed; 1,932 unchanged; no additions/removals/unexpected changes. |
| C88 → C89 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `10465cf8bd40ab5583827107465da2d49ef4ebc59d45fc16b9df7a8d4abc5320` | Three merged girder meshes changed; three connection meshes added; 1,930 unchanged; no removals/unexpected changes. |

All earlier comparison legs retain their own original source hashes and declared object scopes. The C88→C89 comparator additionally covers geometry/material/socket-link hashes and camera/light settings, but it is not a whole-scene dynamic-state or all-custom-property comparison.

## Carry limits and reopened items

The C89 addition is confined to secondary roof-girder termini at sixteen primary-web joints: 16 end plates, 64 annular washers, and 64 bolt heads. The stage reports four retained continuous primary I-girders and leaves the separate `RH pool girder STEEL/YELLOW` crane-track geometry outside its replacement scope. Accordingly, previously accepted unrelated subjects remain eligible for bounded carry; the historical evidence still proves only its original view/criterion.

#110 (girder section readability) and #111 (girder connection construction) remain pending exact C89 full-quality pixels. The current direct 480×270/16 view is not compositionally adequate to inspect the small joint hardware and is not acceptance evidence. All ten final main views must be freshly rendered from the exact final source. The historical upper-trolley evidence remains partial for #108; it does not prove the lower hook/block.

The sixteen mixed-source gauge panel hashes and their original C79/C80 source identities are retained in [`LUNA_C89_MIXED_SOURCE_GAUGE_CARRY.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C89_MIXED_SOURCE_GAUGE_CARRY.md); their eligibility is limited to the unchanged measured gauge/camera/light subject scope and does not waive any required current main view or final gate.
