# 677c issue 125: bounded door-return staining evidence

**Disposition:** accept #125 as a bounded historical-pixel carry for the localized door-return stain treatment. This evidence is the D1 / MAIN ACCESS return visible in 9b view10; it does not establish room-wide wall appearance, neutral lighting, or material-family quality.

## Original image and source

- Original source: `/workspace/scratch/reactor-refinement-next-corrections-working/hall_final.blend`
- Original source SHA-256: `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7`
- Original image: `/workspace/scratch/reactor-refinement-next-corrections-working/proof/green/10/10_walls_west_access.png`
- Image SHA-256: `bc79c34195544a88fdfc2526915ab4298a068b881d2e34ab9151c9aefdf40dd4`
- Manifest SHA-256: `cec8ffa42ed8d7976274f83259f93eb37e509ccdc983bca488b580ade2219652`
- Renderer SHA-256: `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`
- Render: 1280×720, Cycles CPU, 96 maximum / 32 minimum adaptive samples, 16-bit RGB, OIDN, 12 bounces, path guiding, AgX Medium High Contrast, zero exposure.

## Pixel finding

The west-access frame shows a restrained gray-brown deposit at the visible MAIN ACCESS side return near the floor joint. It reads as localized surface grime against the lighter, comparatively clean return face and neighboring wall. It does not form a broad brown wash. This is a modest effect at room-view scale; its visibility is sufficient to establish the treatment on this representative D1 return, but not a standalone judgment of the other two door families.

The source module `/workspace/scratch/reactor-refinement-next-corrections-working/production-integration/rh_door_return_stain_fit.py` (SHA-256 `70e897f794816624e62c0533abbb71734f5f80d2a2fefaa95112796890fa3428`) applies the same bounded material treatment to the six side-return meshes belonging to MAIN ACCESS, FUEL HANDLING and COOLING PLANT. Its mask is limited to the first 1.2 m from each opening mouth, with separate low floor-joint, upper head-joint and edge components. The C89→9b delta changes those six named `*.link wall` meshes and the pool-lining object; it changes no lighting or camera. That delta is `/workspace/scratch/reactor-refinement-next-corrections-working/scene-delta.json`, SHA-256 `742aa950d30574149dddc41578207aa3ede6befac99f9571bc7d9ff91eea2ca8`.

The later exact delta chain to candidate 677c is:

| Leg | Delta SHA-256 | Door-return scope |
|---|---|---|
| 9b→79e | `0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575` | Pool lining only. |
| 79e→f79d | `6280636c48c2bd8ac6e04df356d15d6d86c08e14ed643221e68340e34a343c2d` | Four switchgear-prop meshes only. |
| f79d→5fd | `bc5040fb11e5645728e0665b0480b8576816a92ee0d24546e698fc6f95a84b1c` | Hoist hood and clamp assembly only. |
| 5fd→677c | `10058827bfc2ae32887862b2938f41490ec02d0d78630e0ddf9f0d126960b2b1` | Three local hoist tasklight objects only; the light is aimed at the remote clamp faces. |

The final 677c source is `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`, SHA-256 `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`. These later changes leave the six return surfaces and their assigned stain materials unchanged. The final local hoist light is not a global-lighting carry, and #133, #136 and #137 remain independently open for current-source review.

**Scope limit:** the accepted visual sample is the visible D1 return in this one original 9b frame. It supports the repeated treatment because the same authored mask is assigned across the six inspected return meshes; it is not a claim that this image directly shows all six surfaces or all door approaches.
