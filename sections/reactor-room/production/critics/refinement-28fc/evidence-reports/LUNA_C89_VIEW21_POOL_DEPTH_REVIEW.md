# C89 full view 21: pool lining depth

**Candidate blend SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`  
**Image:** `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/21/21_pool_depth.png`  
**Image SHA-256:** `e9c49abd261ef423e66c70c4cf6cf9cd106e3293e24576872606d853a251bfab`  
**Manifest SHA-256:** `bbd902708d6d722cbc55c42ea126974788aeaf60699e8144b19dd21681672540`  
**Render:** 1280×720, Cycles, 96 maximum / 32 minimum samples, 16-bit, no preview. Camera 21 frames the wall liner from above the pool.

## Disposition

Accept **#84, pool lining joint depth**, for C89. The actual full-quality pixels show the vertical and horizontal grout grid on the green liner, with narrow dark relief shadows at the crossings and along the courses. The image makes the lining read as a tiled surface rather than a flat printed grid.

The exact-scene surface probe independently rebuilds BVHs from the saved liner meshes and casts radial rays toward the inward-facing pool wall. At the vertical seam sample (28.125°, z = −1.2 m), the tile face is at radius 3.38362813 m and the grout face at 3.375 m, an 8.628 mm recess. At the horizontal course sample (33.75°, z = −1.75 m), the tile is at radius 3.400000 m and grout at 3.391330 m, an 8.670 mm recess. The probe inventories the tile shell and the separate course and seam grout objects; it does not infer relief from vertex counts.

Probe script: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/evidence/C89_POOL_LINING_RELIEF_PROBE.py` (SHA-256 `4cc425bc3057a62c8cd725625b19b2381ebf7acbcd670792f757d1a399cd855c`).  
Probe result: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/evidence/C89_POOL_LINING_RELIEF_PROBE.json` (SHA-256 `b39b2ccc51c13c161d5c8b006b9d07aeb2e0f53f266bc139b64c8fd4936e9e2d`).

This is limited to physical lining relief and its visibility in view 21. It does not close the stain-origin criterion **#86**, cross-state water/depth criterion **#88**, or pool service-port construction **#90**.
