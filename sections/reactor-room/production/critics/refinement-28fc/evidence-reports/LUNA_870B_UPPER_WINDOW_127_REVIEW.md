# 870b bounded historical review: issue 127 upper pane frame/recess

## Source and image identity

The receiving source is `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`. The reviewed image is a preserved 677c original: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/76/76_upper_window_recess.png`, SHA-256 `1ed65d373e3e90907ebd591d0f0d476c4062a2ad30ac6c925b711fef451bc04d`; original manifest `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/76/render_manifest.json`, SHA-256 `89bab44dba470f25869575948dd645057b8b947d412c2875abb0112b525a183f`; renderer SHA-256 `358436edc22b168355877f24a170d5217ee93614beec511e568e95a7a0b31956`. The image source is `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`.

The original was 1280×720, full-quality Cycles, 96 maximum / 32 minimum samples, 16-bit, OIDN, 12 bounces, guiding 64, threshold 0.015, exposure 0. Camera `(4.8,5.8,12.15)` toward `(2.9,10.6,12.15)`, 35 mm.

## Pixel review and scope

Two clerestory bays show deep concrete side reveals around the pane frames, intermediate mullions and distinct glazing. The right bay's lower sill and reveal show the frame's set-back; the foreground service tray crosses part of the lower band but does not obscure the side recesses that establish depth. The image is adequate for the representative frame/recess construction and variation visible in these bays.

## Verified source chain and carry limit

The reviewed pixels are from 677c and their bounded use on receiving source 870b is supported by both actual source-delta files:

1. 677c→0058: `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`. This changes ten objects: nine switchgear circuit-label curves and the east white label-strip mesh; 1,944 objects are unchanged. The clerestory frame/recess subjects in this image are outside the changed set.
2. 0058→870b: `/workspace/scratch/reactor-refinement-bearing-lit-working/scene-delta.json`, SHA-256 `d2f459528aff38b56ef2ef05b3accbdf33db6bf24b73ee26a5cd6533befcdebe`. This adds fourteen roof-bearing maintenance-light objects (twelve lights, housings and lenses), with 1,954 objects unchanged and no retained-object changes. The window geometry and materials are outside this addition; added lights mean this is not pixel-identical lighting evidence.

The old image remains a 677c original, not a current 870b render. This supports only the representative #127 frame/recess construction; it does not establish current 870b lighting or whole-room lighting equivalence.

**Disposition:** accept #127 as bounded historical pixel evidence for the representative upper pane frame/recess.
