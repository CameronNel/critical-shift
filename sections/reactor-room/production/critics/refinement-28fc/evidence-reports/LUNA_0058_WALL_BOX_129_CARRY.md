# Issue 129: bounded wall-box evidence transfer to 0058

**Disposition:** Accept #129 for one representative wall-mounted `a_junction` assembly through the exact 677c→0058 delta. This is a source-scoped review of historical 677c pixels, not a 0058 render or a claim of pixel identity.

## Bound pixel evidence

- Original image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/74/74_wall_junction_box.png`
- Image SHA-256: `8ccaf294c486047c17ddbdea3a8302f446fd11a83baa96985bf5f4043fbccb14`
- Original manifest: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/74/render_manifest.json`
- Manifest SHA-256: `6d3cd1c8836bd4cb4db6079c522a1ba9edc5167d5c9c096ba2edaaff3065c75a`
- Rendered source: 677c `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`, SHA-256 `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`
- Camera and profile, per the original manifest: `(5.75, 8.55, 3.85)` toward `(4.8, 10.63, 3.43)`, 45 mm; 1280×720 Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 12 bounces, AgX Medium High Contrast, exposure 0, frame 1; renderer SHA-256 `2ca3b7d2c87dc3a7f6d842c8866cf542d3094e2fc165cf1c896608928e5dd1d7`.

## Visual judgment and scope

At original resolution, the representative box reads as a mounted enclosure against the actual wall surface: the formed case side and depth, layered face/backplate edges, lid inset, four corner fasteners, indicator, and a wall-cast separation shadow are visible together. Two short black tails terminate below the enclosure. This is sufficient for the bounded criterion of wall-box mounting/construction for the representative north-wall `a_junction` assembly. The tails are capped stub details in this evidence; no continuous feeder or conduit-run claim is made. The sample does not assert that every one of the eleven placements has independently reviewed pixels.

The saved-source framing preflight identifies the representative `a_junction` at wall index 4, `u=1.2`, `h=3.2`, with assembly bounds approximately `x=4.568–5.032`, `y=10.606–10.800`, `z=3.060–3.672`; it describes the receiver/back plate, standoff, formed enclosure, fasteners, indicator, and tails. That preflight is geometric corroboration only, not a substitute for the reviewed image. Its report is `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_677C_WALLUTILITY_CAMERA_PREFLIGHT.md`, SHA-256 `baf0085f0b6e1a0261b6d211805ae4bcb33a13aec1f4a2ec64431a8ddb429445`.

## Exact 677c→0058 receiving-source limit

The receiving candidate is `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`, SHA-256 `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`. The exact one-leg delta is `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. It records only nine switchgear circuit curves and `RH stations east WHITE` changed, 1,944 objects unchanged, and no additions, removals, or unexpected changes. The representative wall box and its host are outside this changed set.

This bounded transfer does not claim whole-scene or global-lighting equivalence. The 677c image remains identified by its original source, image, and manifest hashes in the disposition record; it is not relabeled as a 0058 render.
