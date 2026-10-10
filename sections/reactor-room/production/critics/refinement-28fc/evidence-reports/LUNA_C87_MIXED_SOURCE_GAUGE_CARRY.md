# C87 mixed-source gauge image carry

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle87/hall_final.blend`  
**Current SHA-256:** `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`

Carry #16 (gauge information) and #30 (gauge housing depth) from the previously reviewed mixed-source 16-panel set. These are historical image identities, not fresh C87 panels. The exact per-panel path, native resolution/settings, image SHA-256, camera and original source SHA are preserved in [`LUNA_C86_MIXED_SOURCE_GAUGE_CARRY.md`](LUNA_C86_MIXED_SOURCE_GAUGE_CARRY.md) and the linked C84/C82 acceptance report. The C86 report identifies fourteen panels from C79 SHA `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` and panels07/08 from C80 SHA `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`; those original image hashes remain unchanged.

## Exact comparison chain

- C82 SHA `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` → C84 SHA `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`: `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json`, SHA `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67`, only five drum meshes changed, 1,915 unchanged.
- C84 → C86 SHA `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`: `/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json`, SHA `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19`, 41 changed and 13 added; 1,879 unchanged. Gauge bodies, dials, ink, pointers, bezels/glass, gauge materials, direct-view cameras and lights are outside this delta.
- C86 → C87 SHA `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`: `/workspace/scratch/reactor-refinement-cycle87/scene-delta.json`, SHA `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be`, only the concrete `R2 floor` material target and two diffuser meshes changed; 1,930 unchanged. The direct gauge image bounds exclude the floor. The comparator reports no gauge mesh/material, camera, or light changes.

This carry is limited to gauge face readability and housing depth as originally reviewed. It does not claim current C87 gauge renders, whole-room illumination equivalence, or any final score.
