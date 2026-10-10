# 870b bounded historical review: issue 97 bank frame corner

## Source and image identity

The receiving source is `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`. The reviewed image is a preserved 677c original: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/66/66_bank_frame_corner.png`, SHA-256 `f159ce135a09b5b5e38c77e42d5d770fa83f4f0b7e86e8dc37afce412a8bad86`; its original manifest is `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/66/render_manifest.json`, SHA-256 `df5ce4521eae89734e25bbbaf6a529ae39b9bc503f7b208b46f9e241662f90a6`, rendered by `d2b92f1d430e70ada763ce1923eba9e48c4652691bdf038bf810a9e9eac4bf61` from source `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`.

This was a 1280×720 full-quality Cycles render: 96 maximum / 32 minimum samples, 16-bit, OIDN, 12 bounces, guiding 64, threshold 0.015, exposure 0. Camera `(-3.45,-2.2,13.3)` toward `(-2.28,-0.88,12.55)`, 50 mm.

## Pixel review and scope

The orange corner upright visibly joins the perpendicular louvered cabinet faces. Its cap and the upper case corner are in view; the two orthogonal faces and their channel returns are distinct. The thin dark seam at the cap reads as a shadowed junction at this scale, not a demonstrated open or unsupported gap. This is a representative upper bank-corner construction review, not an assertion that all hidden faces are visible.

## Verified source chain and carry limit

The reviewed pixels are from 677c and their bounded use on receiving source 870b is supported by both actual source-delta files:

1. 677c→0058: `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. This changes ten objects: nine switchgear circuit-label curves and the east white label-strip mesh; 1,944 objects are unchanged. The bank-corner subjects in this image are outside the changed set.
2. 0058→870b: `/workspace/scratch/reactor-refinement-bearing-lit-working/scene-delta.json`, SHA-256 `d2f459528aff38b56ef2ef05b3accbdf33db6bf24b73ee26a5cd6533befcdebe`. This adds fourteen roof-bearing maintenance-light objects (twelve lights, housings and lenses), with 1,954 objects unchanged and no retained-object changes. The bank-corner geometry and materials are outside this addition; added lights mean this is not pixel-identical lighting evidence.

The image remains a 677c original, not an 870b render. This supports only the representative #97 bank-corner construction; it does not establish current 870b lighting or whole-scene identity.

**Disposition:** accept #97 for the representative bank frame/post/case corner, on the exact historical pixels and verified two-leg 677c→0058→870b source chain.
