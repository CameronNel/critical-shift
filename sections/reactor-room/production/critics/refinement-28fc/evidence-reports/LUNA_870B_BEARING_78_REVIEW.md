# 870b issue 128: upper ledge/bracket supports

## Evidence identity

- Current candidate: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Full image: `/workspace/scratch/reactor-refinement-bearing-lit-working/proof/green/78/78_wall_post_bearing_lateral.png`, SHA-256 `3f26b295c686c781406dc2319b962d0f070b64a4e3d4e9162bfc947c0d4f6014`.
- Manifest: `/workspace/scratch/reactor-refinement-bearing-lit-working/proof/green/78/render_manifest.json`, SHA-256 `564be426d3b21f1e14228d11532edd3362f85d543acae729fd4b5be0aa58ddd1`.
- Renderer: `/workspace/scratch/reactor-refinement-bearing-lit-working/recipes/render_wall_bearing_lateral_870b.py`, SHA-256 `2fa6d126b50dc4fc1dba9cb3f90c363cd6fb0675a54a979ffabe4318f39c785f`.
- Profile: 1280×720, Cycles CPU, 96 maximum / 32 minimum samples, threshold 0.015, 16-bit, 12 bounces, path guiding 64, OIDN, frame 1, exposure 0. Camera `(4.4,10.54,16.52)` toward `(3.6,10.54,16.56)`, 45 mm.

## Pixel review

The full-resolution lateral view shows the support stack where the post head meets the bearing packer/plate and lower girder flange. The post head, packer edges and beam flange have separate readable boundaries. The braces remain clear of the contact area. The local maintenance lights reveal the interface without clipping its steel surfaces. A fine dark seam remains, but it reads as the seated plate boundary rather than an open gap; no unsupported or floating contact is visible in this view.

The current support audit also passes, but this visual disposition rests on the full image above, not the finite probe alone. Acceptance is for the representative bearing stack and its visible contact; it does not claim that this one frame visually verifies all roof bearings or establishes whole-roof appearance.

**Disposition:** accept #128 on exact current 870b view78 plus the current finite support audit. Keep the historical 0058 view78 as negative context only; do not reuse it as current evidence.
