# C86 supplemental-family carry and lineage

**Current candidate:** `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`  
**Current source SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`

This report preserves exact source/image lineage for accepted historical supplemental families. It does not relabel an old image as a C86 render. Current ten C86 main views remain mandatory. C85→C86 changes only the service-oil-film mesh; C84→C86 changes 41 existing meshes and adds13, with no removals or unexpected changes. The C84→C86 changed set is the deliberate C85 scope: board cells/scales, R2 floor material, two bank drive columns, fitted pool diffuser/flange, absorber finishes, and the oil film. It does not change the listed door, steam-weld, stool, annular-drain, or column-splice meshes. C82→C84 changed only five drum material meshes. These delta scopes do not assert whole-scene equivalence or prove that indirect illumination is identical.

## Exact source chain

| Candidate | SHA-256 | Relationship |
|---|---|---|
| C80 | `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051` | Source for the lower column-splice frame. |
| C82 | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | Source for doors, annular drain, stool, steam joint and upper splice frames. |
| C84 | `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06` | Intermediate current candidate; C82→C84 delta changes only five drum meshes. |
| C85 | `61bad7f0b34d5a9f7336e349c9e64cd8081666be62530e94ea56b4d2e36354ac` | State boards/floor/rods/pool inlet/oil-film scope. |
| C86 | `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f` | Current exact candidate; only the oil-film underside/anchors differ from C85. |

The C82→C84 delta is `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json`; C84→C86 is `/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json`; C85→C86 is `/workspace/scratch/reactor-refinement-cycle86/scene-delta.json`. The comparators include transforms/parents, mesh arrays/material assignments and material graphs, object visibility/drivers, light settings, and camera optics as declared in each delta. The known R2 floor material change in C84→C86 is global to that material, so the annular drain carry below is geometry-construction evidence; current C86 floor context remains subject to view04 review.

## Supplemental criteria and immutable historical pixels

All C82 native panels are original640×360/96-sample Cycles CPU renders with 16-bit output, unless the table says1280×720. Paths/hashes are preserved in `LUNA_C84_SUPPLEMENTAL_FAMILY_CARRY.md` and the C82 manifests.

| Criterion | Historical render/source | Image SHA-256 | Use in C86 |
|---|---|---|---|
| #124, fuel door hardware | C82 SHA `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`; `c82/door-hardware/54_fuel_door_hardware.png` | `4b59e2a40a56b6d42d5150454890bc0e74109c9be60f469594420466b7a3b3e5` | Paired with C82 images55/56 and full57; all door geometry is outside C82→C86 changed sets. |
| #124, access-door hardware | Same C82 source; `c82/door-hardware/55_access_door_hardware.png` | `5df46ae9624a4ec8e88761e64df387e3504ab5dfeaeb93eef69c7b51459c63e4` | Direct hardware context. |
| #124, cooling-door hardware | Same C82 source; `c82/door-hardware/56_cooling_door_hardware.png` | `a90dc397d29b9a615a328669f389af46d96c9f72a167e32056360fb5ecb92924` | Direct hardware context. |
| #124, fuel-leaf detail | Same C82 source;1280×720 image `c82/door-hardware-detail-720p/57_fuel_leaf_hardware_detail.png` | `ef1d7191ec5020982aaf007548979bd0c908cf193c553c50ce1f5d1aa9a3bfc5` | Full detail of stems, handles, hinge barrel and plates; C82 seat audit corroborates physical joints. |
| #71, annular drain geometry | C82 source; `c82/native-geometry/34_floor_annulus.png` | `bf1fa5c53cc17e61977a8396fc529c12fe038b907b5112478e8bd06807207b66` | Carries recess/channel geometry only. C86 main04 must confirm current floor/substrate context before final overall acceptance. |
| #56, stool construction | C82 source; `c82/native-geometry/43_stool.png` | `d49c3f00c3a9da67aa849ae9238bfc495e090870656111abb9d082c986cdefec` | Stool ring, feet and construction; C86 floor material is not an acceptance of general floor appearance. |
| #38, welded steam tap | C82 source; `c82/steam-tap/17_steam_tap_weld.png` | `2e12007796333ae887fdb72f8d53927fd9d1d387a8ca38afd2b510bf026b7d53` | Close image of seat, nipple, union and gauge body; C82 actual-interface probe documents the deliberate welded connection. |
| #112, upper splice | C82 source;1280×720 `c82/mechanical-proofs-720p/53_column_splice_upper.png` | `312c067e6b35ab5e3eb8fa93a1d7a1ef3d30bdb65a707ce9f4596e99b5900e41` | Upper splice plate/fasteners, current C86 geometry unchanged. |
| #112, lower splice | C80 source;1280×720 `c80/mechanical-proofs-720p/51_column_splice_lower.png` | `43a5c45b33dd7e3cc71fe41aace4c3ac080d2407f1344dd466886ecd765d7659` | Lower splice plate/fasteners, current C86 geometry unchanged. |
| #108, partial upper trolley | C82 source;1280×720 `c82/mechanical-proofs-720p/52_trolley_raised.png` | `766e5c5fad1da45bb060711c9a7af1377aa51c4145411b1eb9bbf1ac8b914372` | Partial upper motor/drum/running-gear context only. The red bridge rail hides part of the lower hook/block; #108 is NOT accepted. Current C86 views26/27/28 remain necessary. |

The full settings, exact native camera transforms, manifests, source hashes and additional image identity are retained in `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_SUPPLEMENTAL_FAMILY_CARRY.md`. The C82→C84 drum-only carry report and C84→C86 material/board/rod/floor scope are adjacent to these original image records.

## Dispositions and limits

The C86 independent JSON carries #38, #56, #71, #112 and #124 within these narrow unchanged-subject scopes. For #71, the acceptance is specifically the annular channel's formed recess/geometry; C86 main04 is required to confirm it remains legible in the current floor context. #108 remains partial and pending direct hook/load-path evidence; #116 service-cable terminations are not proved by the trolley images. No blanket whole-room or render-lighting carry is implied.
