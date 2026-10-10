# 0058 bounded carry review: issue 122 wall/plinth transition

## Pixel evidence

- Original source: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`
- Original source SHA-256: `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`
- Original image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/73/73_wall_plinth_diagonal.png`
- Image SHA-256: `0d2f2df005fc87ddbb0e09055ca973c9454858e60fce20777198b30bd5152cc6`
- Original manifest: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/73/render_manifest.json`
- Manifest SHA-256: `09200ba2e677ae3836206ef3ce47ba71c3be9a3997dbde8e08a3a105b246a7b6`
- Renderer SHA-256: `f1bb31bd610307c0fb21e50617d4e1943049adf3b0858c5486770f9fda7b98f2`
- Full profile: 1280×720 Cycles CPU, 96 maximum/32 minimum adaptive samples, OIDN, 12 bounces, path guiding, 16-bit, AgX Medium High Contrast, exposure 0, frame 1.
- Camera: (8.065966, 7.284467, 0.5) toward (8.737717, 7.956218, 0.24), 35 mm.

The full-resolution view shows the lower wall course, projecting plinth face, and adjacent floor slab together. A dark foreground service assembly occludes part of the junction, but a clear right-hand segment remains visible and gives a readable wall-to-plinth-to-floor transition. This supports the representative transition subject in #122. It does not establish an unobstructed view around the full room or prove every doorway threshold.

## Transfer to 0058

The receiving candidate is `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend` (SHA-256 `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`). Its exact 677c→0058 delta is `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json` (SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`): it changes nine switchgear label curves and the `RH stations east WHITE` mesh, with 1,944 objects unchanged and no additions, removals, or unexpected changes. Those changes do not alter the reviewed wall/plinth geometry or camera. This is bounded historical pixel evidence; the original 677c image remains identified as such. No pixel-identical, global lighting, or whole-scene claim is made.

**Disposition:** accept #122 as a bounded carry for the visible representative wall/plinth/floor transition. Keep the separate ten-view 0058 main review and global score gates open.
