# C89 to 0058: camera 72 bearing review

**Disposition:** #128 remains pending. This is a review of the original 677c image, not a 0058 render or a relabeling of its pixels.

## Bound source and image

- Reviewed image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/72/72_wall_post_girder_bearing.png`
- Image SHA-256: `6c17d918c8c1dfeb77abd51afdbc95d23afbcbb20fa79cd132e1e05a8a7daf67`
- Manifest: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/72/render_manifest.json`
- Manifest SHA-256: `8e646490d423dd10e1fd4c8599d3e3637a158fefd2141cb7123b6e91e0bd329c`
- Rendered source: 677c `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`, SHA-256 `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`
- Render profile: original 1280×720 Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 12 bounces, AgX Medium High Contrast, exposure 0, frame 1. Camera 72 at `(3.0, 9.3, 16.1)`, aimed at `(3.6, 10.54, 16.63)`, 45 mm.

## 0058 lineage limit

The exact 677c→0058 delta is `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. It records nine switchgear circuit curves and `RH stations east WHITE` as the only ten changed objects, 1,944 unchanged objects, and no additions, removals, or unexpected changes. The receiving 0058 source is `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`, SHA-256 `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`.

This delta establishes that the roof bearing assembly was outside the declared changed-object set. It does not change the source identity of the rendered pixels, and does not turn the 677c image into 0058 evidence.

## Pixel assessment

The frame shows the girder underside, a distinct bearing-plate edge, the post head, and diagonal braces. The plate edge catches a narrow highlight, but the bearing/post interface itself is very dark; the braces mask much of the post head. At original resolution I cannot confidently distinguish a visibly seated bearing from a dark overlap or gap. Geometry/contact checks can corroborate physical fit, but they do not resolve this image-level ambiguity.

Therefore #128 is not accepted from this frame. Keep it pending for a full-quality 0058 view with the same bearing surfaces visible from a less obstructed angle. Preserve this 677c image and its manifest under their original identity; do not relabel it as 0058 evidence.
