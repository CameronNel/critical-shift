# Column splice construction acceptance (#112)

**Bounded current candidate:** C82 `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`, SHA-256 `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`.  
**C83 continuation:** `/workspace/scratch/reactor-refinement-cycle83/hall_final.blend`, SHA-256 `02eb2a2ff8deeede8fee0e2a727157d9081aae314cee18f00a7403a1d023b8d3`.  
**Disposition:** Accept #112 from the paired full-quality lower and upper splice views. This is a criterion-specific mixed-source disposition, not acceptance of unrelated roof framing.

## Pixel evidence

- Lower W4 splice: C80 image [`51_column_splice_lower.png`](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/mechanical-proofs-720p/51_column_splice_lower.png), SHA-256 `43a5c45b33dd7e3cc71fe41aace4c3ac080d2407f1344dd466886ecd765d7659`; manifest `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/mechanical-proofs-720p/render_manifest.json`, source SHA `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`.
- Upper W4 splice: C82 image [`53_column_splice_upper.png`](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/mechanical-proofs-720p/53_column_splice_upper.png), SHA-256 `312c067e6b35ab5e3eb8fa93a1d7a1ef3d30bdb65a707ce9f4596e99b5900e41`; manifest `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/mechanical-proofs-720p/render_manifest.json`, source SHA `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`.

Both are 1280×720 CYCLES CPU renders at 96 maximum samples. Each full splice plate and all six bolt heads are visible. The upper frame also shows its adjacent service bracket without covering the plate. The framing is deliberately close and demonstrates the plate/bolt construction rather than relying on a distant hall view. The plate and bolt heads read as attached to the column joint in both images.

## Bounded evidence lineage

The exact C80→C82 delta at `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json` changes only six door-leaf `STEEL` meshes; 1,914 objects are unchanged, with no additions/removals/unexpected changes. Its declared comparator includes object transforms, parent links, visibility, drivers/action names, mesh vertices/faces/material indices/smoothing, font geometry, material graphs, light properties, and camera lens/shift/clipping. The splice column/plate is outside the six changed objects and the imagery settings/camera are unchanged.

The exact C82→C83 delta at `/workspace/scratch/reactor-refinement-cycle83/scene-delta.json` changes only five merged drum material meshes; 1,915 objects are unchanged, with no additions/removals/unexpected changes. The splice assemblies, cameras, lights and materials are outside the changed scope. Therefore the C80 lower image and C82 upper image remain valid evidence for the paired splice criterion on C83. This does not claim whole-scene equivalence or waive fresh C83 views required for other criteria.
