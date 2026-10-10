# 870b wall illumination review

## Bound current evidence

- Candidate: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Canonical renderer: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py`, SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`.
- Full-quality main09: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/09/09_walls_north_fuel.png`, SHA-256 `811debf206433fc3145ed5c6742df08b29f856449d29298d8b2bd1a835f2234e`; manifest `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/09/render_manifest.json`, SHA-256 `2e97143ea41a9fc33f47fb5f32022bfa68fade81ff54f8b61bc83943e44fed34`.
- Full-quality main10: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/10/10_walls_west_access.png`, SHA-256 `e4a661840a636a5c9d4e962a27e562892ef7b8e06b89a78497ba083b08c316d0`; manifest `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/10/render_manifest.json`, SHA-256 `af2157a0a31be7df9bd7f430041eb10048a66e327d8e7c49e6bbcd2775691b1f`.
- Both images are 1280×720, Cycles CPU, 96 max/32 min samples, threshold 0.015, 16-bit RGB, OIDN, 12 bounces, guiding 64, frame 1, exposure 0. Main09 camera `(-5.6,4.4,3.6)` toward `(0,10.4,4.3)`, 18 mm; main10 camera `(-3.7,2.7,3.2)` toward `(-10.8,0.8,4.4)`, 18 mm.

## Pixel review

The exposed north and west wall panels read neutral gray in both views. Door interiors and nearby practical pools are localized; they do not wash the surrounding wall fields in green, orange, or another broad color cast. The west view shows a brighter door return and equipment service lighting, while the north view shows the fuel-door light; those local differences remain distinct from the surrounding neutral wall material.

**Disposition:** accept #133 for neutral wall illumination in the mapped current main09/main10 areas. This does not close #134 roof lighting or imply uniform room-wide exposure, and it does not waive the separate main10 STANDBY GENERATOR signage obstruction recorded in the #139 observation.
