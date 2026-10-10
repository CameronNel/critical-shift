# C84 supplemental-family evidence lineage

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Current source SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`  
**Historical C82 source:** `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`  
**Historical C82 SHA-256:** `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`  
**Historical C80 source for lower splice:** `/workspace/scratch/reactor-refinement-cycle80/hall_final.blend`  
**Historical C80 SHA-256:** `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`

This report records the original images and exact render lineages behind bounded C84 dispositions. It does not relabel a historical image as a C84 render. C82→C84 delta `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` passes with exactly five changes (`RH refine legacy drums GALV`, `RH refine legacy drums RED`, `RH stations props GALV`, `RH stations props RED`, `RH stations props YELLOW`), 1,915 unchanged objects, and no additions, removals, or unexpected changes. The relevant door, floor, steam-tap, column-splice, and trolley subjects are outside the changed set.

## Supplemental evidence and settings

All C82 images below come from Blender 5.2.2 LTS, Cycles CPU, 96 maximum samples, adaptive minimum32/threshold.015, OpenImageDenoise, 16-bit RGB, exposure0.0, no preview. File SHA-256 values were recomputed and match their manifests. The 640×360 panels are native resolution and have not been enlarged.

| Criterion | Historical source SHA | Image SHA-256 | Original image | Native camera |
|---|---|---|---|---|
| #124 door operation: fuel door | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | 4b59e2a40a56b6d42d5150454890bc0e74109c9be60f469594420466b7a3b3e5 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/door-hardware/54_fuel_door_hardware.png` | 640×360; (0,8.25,2.5) → (0,14.36,2.5), 24mm |
| #124 door operation: main access | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | 5df46ae9624a4ec8e88761e64df387e3504ab5dfeaeb93eef69c7b51459c63e4 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/door-hardware/55_access_door_hardware.png` | 640×360; (−7.75,0,2.75) → (−14.36,0,2.75), 22mm |
| #124 door operation: cooling plant | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | a90dc397d29b9a615a328669f389af46d96c9f72a167e32056360fb5ecb92924 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/door-hardware/56_cooling_door_hardware.png` | 640×360; (7.7,−7.7,2.5) → (10.917,−10.917,2.5), 18mm |
| #124 fuel-leaf hardware detail | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | ef1d7191ec5020982aaf007548979bd0c908cf193c553c50ce1f5d1aa9a3bfc5 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/door-hardware-detail-720p/57_fuel_leaf_hardware_detail.png` | 1280×720; (1.2,11.6,1.85) → (1.2,14.3,1.85), 28mm |
| #71 annular drain recess | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | bf1fa5c53cc17e61977a8396fc529c12fe038b907b5112478e8bd06807207b66 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/native-geometry/34_floor_annulus.png` | 640×360; (−4.6,−5.7,1.2) → (−2.4,−3.8,−0.15), 28mm |
| #56 stool construction | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | d49c3f00c3a9da67aa849ae9238bfc495e090870656111abb9d082c986cdefec | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/native-geometry/43_stool.png` | 640×360; (8.2,4.2,1.15) → (7,3.07,0.32), 40mm |
| #38 welded steam tap appearance | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | 2e12007796333ae887fdb72f8d53927fd9d1d387a8ca38afd2b510bf026b7d53 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/steam-tap/17_steam_tap_weld.png` | 640×360; (9.8065,−3.9415,6.7464) → (10,−3.89,6.4), 40mm |
| #112 upper column splice | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | 312c067e6b35ab5e3eb8fa93a1d7a1ef3d30bdb65a707ce9f4596e99b5900e41 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/mechanical-proofs-720p/53_column_splice_upper.png` | 1280×720; (3.1,8.6,9.3) → (3.1,10.43,9.3), 50mm |
| #112 lower column splice | `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051` | 43a5c45b33dd7e3cc71fe41aace4c3ac080d2407f1344dd466886ecd765d7659 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/mechanical-proofs-720p/51_column_splice_lower.png` | 1280×720; (3.1,8.6,6.6) → (3.1,10.43,6.6), 50mm |
| #108 partial upper trolley context only | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | 766e5c5fad1da45bb060711c9a7af1377aa51c4145411b1eb9bbf1ac8b914372 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c82/mechanical-proofs-720p/52_trolley_raised.png` | 1280×720; (−8,3,16.6) → (−6.5,4.6,15.7), 35mm |

C80→C82 scene delta `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json` leaves the column splices, their cameras, lighting and materials unchanged; that delta changes only six door-leaf STEEL meshes and adds no objects. The crane identity plate and supports were added earlier in C79→C80, and remain unchanged in C80→C82. The subsequent C82→C84 delta changes only the five drum meshes. #112 therefore uses a deliberately mixed historical pair of views, not a same-source composite.

## Current C84 disposition scope

- #124, #71, #56, #38, and #112 remain accepted under their already-recorded bounded dispositions. This report retains original paths, hashes, settings, and source SHA lineage for packaging.
- The C82 images do not become C84 images. All ten requested current C84 main views are still required, and no global visual score follows from these supplemental carries.
- **#108 remains pending.** Historical C82 full52 shows the trolley motor, drum, left running gear, and upper frame, but its red bridge rail masks the lower hook/block area. It is partial evidence only, not acceptance. Use exact C84 views26/27/28 for the hook, rope entry, and continuous load path. C82→C84 does not change the trolley itself, so view22 adds no indispensable evidence if 26/27/28 plus main07 and the historical52 image clearly cover their distinct details; do not use22 as a substitute for those direct views.
- Do not carry #116 on the basis of trolley-rope views. Its service-cable termination evidence is routed to current views24/46 and the corresponding saved service-run probes.
