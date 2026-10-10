# 870b roof illumination review

## Bound current evidence

- Candidate: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Canonical renderer: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py`, SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`.
- Full-quality main07: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/07/07_roof_crane.png`, SHA-256 `c06b2162ad7617c4de12896fb061390aea57523d7af694c22edec838f4bd330f`; manifest `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/07/render_manifest.json`, SHA-256 `f5de05e4fd075d5220245568a424455b4dda1aa4dd1c6bbfdbeb97a0c51a1911`.
- Full-quality main08: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/08/08_roof_girders_services.png`, SHA-256 `01c506bce62dc84747aa9210f92c73e3864e85d094ef2cd780ec826651eea80a`; manifest `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/08/render_manifest.json`, SHA-256 `529589cc3f70c3b86025a50a96be36b41b6e94e54a7ab15b887c9e192d6da357`.
- Both images are 1280×720, Cycles CPU, 96 max/32 min samples, threshold 0.015, 16-bit RGB, OIDN, 12 bounces, guiding 64, frame 1, exposure 0. Main07 camera `(0,-7.5,15.6)` toward `(-3,4.6,15.8)`, 20 mm; main08 camera `(6.5,1.4,15.3)` toward `(-3,6,16.8)`, 18 mm.

## Pixel review

Across both views, the roof panels and structural steel read neutral gray/white. The crane and service runs remain visually separate from the ceiling, and the added bearing lights produce localized neutral pools rather than a colored wash. The girder faces and panel edges remain discernible in the darker areas; the upper recesses are shadowed, but the structural boundaries are still visible at full resolution.

**Disposition:** accept #134 for neutral roof illumination and readable roof structure in the mapped main07/main08 views. This is not a claim of uniform brightness, room-wide focal hierarchy, or #118 fixture-mount acceptance; those retain their separate scopes.
