# Issue 86: pool wall staining origins — bounded 79e pixel carry

**Disposition:** accepted as a bounded historical-pixel carry to 677c. This is not a current 677c render acceptance and does not assign a score.

**Receiving candidate:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Receiving candidate SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`

## Reviewed pixels

- Render source: `/workspace/scratch/reactor-refinement-pool-readability-working/hall_final.blend`
- Source SHA-256: `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c`
- Original full-quality image: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/working-originals/reactor-refinement-pool-readability-working/1.0/21_pool_depth/21_pool_depth.png`
- Image SHA-256: `7d45c81b5aa0ee74ee0be8b5ed428056cb9ae0fd4647416bb0d18e8346d3ec15`
- Original manifest: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/working-originals/reactor-refinement-pool-readability-working/1.0/21_pool_depth/render_manifest.json`
- Manifest SHA-256: `bd480ac5c7d881811444e59c8a08c43829431b8cabd603be9793458a7c9b82cf`
- Render profile: 1280×720, Cycles CPU, 96 maximum / 32 minimum samples, OIDN, 16-bit, AgX Medium High Contrast, exposure 0. Camera 21 is at `(0, -3.0, 2.2)`, aimed at `(0, 3.3, -2.5)`, 20 mm.

I reviewed the original image at native resolution and compared it directly with the rejected 45eb full-quality view21. In 79e, the localized warm mineral deposits read as irregular downward traces beginning at the upper liner grout/course and extending into the wall toward the 3 m course. Their warm tone separates them from the green liner and dark grout. The traces are still restrained under the water tint; this accepts only the stain-origin detail visible in this frame, not a broad claim about every liner surface or hidden stain.

The prior 45eb image did not make the stain legible enough. The 79e version improves that contrast while keeping the deposits localized. The accepted evidence is the unmodified 79e original image above; no crop, preview, material-node presence, or later render is used as acceptance evidence.

## Exact transfer to 677c

The 79e render followed the liner material revision. Its exact `9b→79e` scene delta (`0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575`) changes only `R2 pool pool lining TILE`; 1,935 other compared objects are unchanged. The rendered view therefore directly tests the revised liner appearance.

The historical pixels retain source 79e identity through these exact later legs:

| Leg | Delta SHA-256 | Scope relevant to this carry |
|---|---|---|
| C89→9b | `742aa950d30574149dddc41578207aa3ede6befac99f9571bc7d9ff91eea2ca8` | Includes the pool-liner material and door-return revision; this is upstream of the accepted 79e render. |
| 9b→79e | `0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575` | Revises only `R2 pool pool lining TILE`; the view21 image is from the resulting 79e scene. |
| 79e→f79d | `6280636c48c2bd8ac6e04df356d15d6d86c08e14ed643221e68340e34a343c2d` | Changes four switchgear prop meshes, away from the pool lining. |
| f79d→5fd | `bc5040fb11e5645728e0665b0480b8576816a92ee0d24546e698fc6f95a84b1c` | Revises the crane trolley and adds hoist clamps and an inspection opening, away from the viewed liner. |
| 5fd→677c | `10058827bfc2ae32887862b2938f41490ec02d0d78630e0ddf9f0d126960b2b1` | Adds the 1.2 W hoist-aperture tasklight housing, lens, and local light. It is aimed at the clamp faces; this carry does not claim all lighting is unchanged. |

The later deltas leave the pool liner and camera unchanged. The only later lighting addition is the 1.2 W clamp tasklight at the remote hoist aperture. It is aimed at the clamp faces; this carry rests on the light's low power and distance from the liner. I judge it unlikely to change the pictured stain appearance materially. This is a bounded transfer of the 79e image, not a claim that lighting is unchanged or that 677c itself has been rendered for issue 86.

The carry is limited to the pictured pool-wall staining-origin appearance. It does not close issue 88 (water/depth state comparisons), issue 90 (pool service-port construction), or any whole-room material/lighting criterion. The ten required 677c main views and overall scoring remain outstanding.

See the complete source-delta inventory in [`LUNA_677C_BOUNDED_CARRY_REVIEW.md`](LUNA_677C_BOUNDED_CARRY_REVIEW.md).
