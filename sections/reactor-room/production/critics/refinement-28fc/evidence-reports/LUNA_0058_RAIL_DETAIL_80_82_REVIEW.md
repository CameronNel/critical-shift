# C0058 rail detail review: issues 80 and 82

**Receiving candidate:** `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`  
**Receiving source SHA-256:** `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`  
**Pixel source:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Pixel source SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`

This is an independent review of the original 677c full-quality image, not a 0058 render. The exact one-leg 677c→0058 scene delta is `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. It records ten changed meshes for switchgear label curves/strips, 1,944 unchanged objects, and no additions, removals, or unexpected changes. The pool rail is outside those edits. This scoped transfer does not assert full-scene or pixel identity.

## Original image and render identity

- Image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/64/64_pool_rail_post_joint.png`
- Image SHA-256: `7b84d7c5af19beee9c5910b7b8fab6e9b863f799a233744d962679325c83be37`
- Manifest: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/64/render_manifest.json`
- Manifest SHA-256: `e94651ab0f7062fe85c0b7e2e2374e0cff5eebff174026700f24e6e8667bb069`
- Renderer SHA-256: `5be1d209201d3ff8ed9b5240a78b622a8916a2fd3ac8d166c4924bc7a07d571a`
- Camera: `(6.1, 0.4, 1.55)` toward `(3.634330153465271, -0.0697827059775591, 0.76)`, 35 mm perspective.
- Full-quality profile: 1280×720, Cycles CPU, 96 maximum/32 minimum adaptive samples, OIDN, 12 bounces, AgX Medium High Contrast, exposure 0.

## Issue 82: rail intersection joints — accepted bounded carry

The full image resolves several upper-rail and mid-rail intersections with upright posts. The tubes meet cleanly and read as continuous joined guardrail construction; I see no visible gap, floating member, or clipping at the representative junctions. A separate weld bead is not modeled or claimed. The saved technical audit does not register upper-joint contacts, so this is a visual assessment of the rendered intersections only.

Accept issue 82 as a bounded carry to 0058 for the representative through-rail/post joints shown in image 64. This does not claim inspection of every circumference joint, the service gate hardware, or a measured upper-joint weld. The 677c image and manifest remain identified as 677c originals.

## Issue 80: rail post terminations — remains pending

The image clearly shows flat cap plates terminating several post tops. It also shows parts of the bolted post feet, though the toe-board and rim conceal portions. The receiving 0058 support audit independently records 88/88 rail-foot anchors seated on `RH pool tread TREAD`; maximum measured gap is `9.685754774613198e-9 m`, with zero penetration. Audit: `/workspace/scratch/reactor-refinement-switchgear-label-working/audit.json`, SHA-256 `a66f58ca9da25a790368d70358a3b9f72520128220e413fa207f7e7fc69c4a20`.

Keep issue 80 pending because the mapped criterion also asks for the actual rail-end return/cap construction. In view 64, the rail arcs continue out of frame; neither terminal end is shown well enough to inspect its cap or return into the adjacent assembly. This is a remaining evidence gap, not an observed geometry defect. The 88 foot contacts corroborate post-foot seating only; they do not prove rail-end construction.

## Boundaries

- #82 is a visual bounded carry from the exact 677c image through the exact 677c→0058 delta.
- #80 receives a partial visual/technical assessment only and remains pending until a full-quality current-source frame exposes a rail terminal end and its return/cap.
- These findings do not change #81, which has its own accepted rail-base disposition.
- No 0058 pixels are inferred from the 677c render; no whole-scene, exhaustive collision, or global lighting claim is made.
