# 28fc #9 STANDBY GENERATOR visibility review

## Exact receiving-source pixels

Candidate `/workspace/scratch/reactor-refinement-generator-visible-working/hall_final.blend`, SHA-256 `28fc09a259369b685ca1f96ad78cfd19bc0992f4ae67b200cb2143d9272905e3`.

- Intended west-wall context: `/workspace/scratch/reactor-refinement-generator-visible-working/standard-720p/green/10/10_walls_west_access.png`, SHA-256 `2e548c6807c3e8543763c0d0b524a6bc9ebc0082eaae6c541085f8c6ea29f165`; raw manifest `/workspace/scratch/reactor-refinement-generator-visible-working/standard-720p/green/10/render_manifest.json`, SHA-256 `270b8455c7264cb511ebdf326d21d04d3c391c5777599ad359b0da7039d4631a`.
- Direct plaque inspection: `/workspace/scratch/reactor-refinement-generator-visible-working/proof/green/37/37_generator_plaque.png`, SHA-256 `248f445ddbaf39fcf876ca18cd302d95b121dc7ec12cf59d272e09ddebbac78b`; raw manifest `/workspace/scratch/reactor-refinement-generator-visible-working/proof/green/37/render_manifest.json`, SHA-256 `a8e9fcf2c0c5ea197066d813d2094c444559682ef78bb0be9ebd61a10cc479e6`.
- Canonical renderer `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py`, SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`. Both manifests bind the 28fc source and this renderer at 1280×720, 96 maximum samples, 32 minimum samples, 16-bit color, 12 bounces, path guiding and zero exposure. Main10 uses the saved west-wall view; direct37 is the 35 mm frontal inspection pose.
- The source delta from 870b is `/workspace/scratch/reactor-refinement-generator-visible-working/scene-delta.json`, SHA-256 `d460a1f10d05647b5076d4211f048fbcce791685bccdd5c591f151ba1836de28`.

## Disposition

Accept #9 on these receiving-source full-quality pixels. In main10, the plaque is visible in the intended west-wall context and the R2 conduit no longer crosses the plaque face. Direct37 shows the complete “STANDBY GENERATOR” lettering, full face and trim, with the moved plate attached through the extended wall spacers. The lettering is small in the wide context image, so the direct image is part of this acceptance.

This closes the specific obstruction finding for #9. It does not close the broader #139 room-wide signage visibility review, which still requires the remaining receiving-source main views and criterion-mapped sign images. It makes no final-scene or score claim.
