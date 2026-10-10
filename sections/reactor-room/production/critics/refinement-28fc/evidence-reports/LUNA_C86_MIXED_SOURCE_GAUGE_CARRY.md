# C86 bounded carry: mixed-source gauge evidence

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`  
**Current SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`

## Decision and exact lineage

Carry #16 (gauge information readability) and #30 (gauge housing depth) from the previously reviewed mixed-source 16-panel set. The panel renders remain tied to their exact historic sources: fourteen native panels from C79 `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` plus panels07/08 from C80 `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`. C82 is `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`; C84 is `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`; C86 is the exact candidate SHA above.

The previous detailed sixteen-panel report, including each panel's original path, image SHA, source SHA, native 640×360/96 settings, and review, is [`LUNA_C84_MIXED_SOURCE_GAUGE_CARRY.md`](LUNA_C84_MIXED_SOURCE_GAUGE_CARRY.md) and its linked [`LUNA_C82_MIXED_SOURCE_GAUGE_ACCEPTANCE.md`](LUNA_C82_MIXED_SOURCE_GAUGE_ACCEPTANCE.md). The panels show the authored 0/5/10/bar faces, pointers, glass and case depth at native size; the two darkest faces remained legible under the original review.

## Source comparisons

- C79→C82 cumulative comparison: `/workspace/scratch/reactor-refinement-cycle82/cumulative-c79-scene-delta.json` PASS; it records the crane identity fix and six door meshes, three additions, and 1,910 unchanged objects.
- C80→C82: `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json` PASS; only the six door-leaf STEEL meshes changed; 1,914 unchanged.
- C82→C84: `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` PASS; only the five drum material meshes changed; 1,915 unchanged.
- C84→C86: `/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json` PASS; 41 changed/13 added, no removals/unexpected, 1,879 unchanged. It does not change any gauge body, ink/numeral mesh, pointer, glass, bezel, gauge material, camera, or light object/settings.
- C85→C86: `/workspace/scratch/reactor-refinement-cycle86/scene-delta.json` PASS; only the oil-film mesh changed.

The C84→C86 changes include a global `R2 floor` material graph and the resized pool inlet. The selected gauge macros are tightly framed on the dial/casing, with the floor outside each camera image. The source comparisons preserve the original direct-view cameras, gauge meshes/material graphs, glass retainers, lights and camera optics. These changes therefore do not affect the tested gauge-face typography or housing depth. I do not extend this carry to the surrounding floor/material appearance, machinery-wide illumination, or any unreviewed current room area.

## Scope

This is a criterion-specific carry of the mixed-source gauge appearance and construction evidence. It does not claim sixteen fresh C86 frames; all listed original hashes remain historical. It does not set a final score or accept the ten requested C86 main views. The exact panel table and manifest identities remain in the linked prior report to avoid relabeling any image as current C86 evidence.
