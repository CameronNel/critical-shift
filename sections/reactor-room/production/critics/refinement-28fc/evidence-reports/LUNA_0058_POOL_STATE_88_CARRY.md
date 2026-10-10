# C0058 bounded pool-state review: issue 88

**Receiving candidate:** `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`  
**Receiving source SHA-256:** `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`  
**Pixel source:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Pixel source SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`

## Decision

Accept #88 as a bounded carry of the three-state water-plane/depth comparison shown in the original 677c view21 renders. The submerged shaft reads as a tinted transparent volume: the lined wall grid, depth markers and lower pool floor remain visible through it. Green, orange and red states each produce a distinct water/light tint without erasing the depth cues. In all three, the bright central practical reflection partly washes the centered 1 m marking; the side 1 m markings remain legible, and the 3 m and 5 m markers are visible. This is a visible reflection limitation, not a state-specific loss of the plane or depth read.

The exact 677c→0058 delta is `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. It changes nine switchgear label curves and `RH stations east WHITE`; 1,944 objects are unchanged, with no additions, removals or unexpected changes. The pool lining, water, depth markers, camera, and lights are outside the changed subject. This carry does not claim pixel identity or global lighting identity, and does not replace the ten required full-quality 0058 main views.

## Original source/render identities

All three are full-quality 1280×720 Cycles CPU renders. They share renderer SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`, camera `(0, -3, 2.2)` aimed at `(0, 3.3, -2.5)`, 20 mm lens, 96 maximum adaptive samples, threshold 0.015, 12 bounces, path guiding, AgX Medium High Contrast, and exposure 0.

| State | Original image | Image SHA-256 | Manifest SHA-256 |
|---|---|---|---|
| Green | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/21/21_pool_depth.png` | `6cf29f2a9869ef2c23df075dc334489c14677a2745aebea8eb6ca317452f504a` | `b564216ec6f11b491dd3dd0601299c5705138516a7903f75a03c708fac76988a` |
| Orange | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/orange/21/21_pool_depth.png` | `3095b1b008549e811994cf86fac95434e74ffb7620b3ff7b6392d50f849db0fe` | `3f49a5ba54e3875efb06f85731d61383ba49904de75f96fce27b82bb72396597` |
| Red | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/red/21/21_pool_depth.png` | `75a46c6df2dc163a2923977b9b1c78c88aa5f4cd569939019089a107f779430b` | `06f18744dfc8d0cbc1f593faabfae6405ce934fa1b37821e75314cc317001379` |

The original PNG and manifest paths above remain bound to source 677c; none is relabeled as a 0058 render. This disposition is limited to water-plane and depth readability across the three states. It does not score other pool construction or lighting rows.
