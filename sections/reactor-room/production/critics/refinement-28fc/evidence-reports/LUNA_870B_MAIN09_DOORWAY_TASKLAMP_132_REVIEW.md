# Issue 132: 870b main09 doorway task-lamp review

## Bound current evidence

- Candidate: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Full-quality PNG: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/09/09_walls_north_fuel.png`, SHA-256 `811debf206433fc3145ed5c6742df08b29f856449d29298d8b2bd1a835f2234e`.
- Manifest: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/09/render_manifest.json`, SHA-256 `2e97143ea41a9fc33f47fb5f32022bfa68fade81ff54f8b61bc83943e44fed34`.
- Canonical renderer: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py`, SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`.
- Camera: `(-5.6,4.4,3.6)` toward `(0,10.4,4.3)`, 18 mm.
- 1280×720, Cycles CPU, 96 max/32 min samples, threshold 0.015, 16-bit RGB, OIDN, 12 bounces, guiding 64, frame 1, exposure 0.

## Pixel review

In the north fuel doorway, the actual LP task fuel 5 appears as a separate black task head on its pole/cantilever mount, just inside the D2 opening. Its mounting and relation to the doorway are visible. The interior door return and floor are visibly illuminated with a localized warm practical response against the neutral gray exterior wall and surrounding surfaces. The fixture reads as a mounted task light with a useful target, not simply a colored patch or generic caged wall lamp.

The generic caged wall light in view75 is a different fixture and is not used as evidence for this decision. The view09 pixels directly establish the mapped D2 task-lamp criterion.

**Disposition:** accept #132 for the actual D2 doorway task fixture, visible mounting, and useful illuminated doorway area in this current 870b view. This is not a blanket lighting acceptance; #133 and #134 remain separate, and #138/#139 retain their broader mapped scopes.
