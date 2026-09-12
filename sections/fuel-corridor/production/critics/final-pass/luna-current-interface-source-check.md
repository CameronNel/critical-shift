# Luna current adjacent interface source check — Fuel Corridor

**Review date:** 11 September 2026  
**Scope:** read-only refinery/reactor source and saved-artifact identity check against P07  
**Result:** **source-level P07 consistency retained; assembled interface remains unverified**

I checked the current adjacent source paths named by `architecture/CONNECTION_CONTRACTS.md` and `production/critics/astra-interface-recheck.md`. I did not open or mutate a live neighboring scene. This check distinguishes current source expressions from historical saved checks and does not certify S01/S02/S03 destination fit.

## Refinery / F01

Current refinery source still derives the P07 seam from the same subordinate layout files:

- `blender/config.py` retains `S=sqrt(1.15)`, `DX=0.506663706334526` and `DY=0.434283176858165`.
- `blender/architecture.py` retains the REACTOR threshold at the original local opening and the 2.60 × 3.00 m nominal portal.
- `blender/layout_expansion.py` still translates REACTOR-owned geometry by `(DX,-DY,0)` and preserves the 1.10 m refinery sill.
- `blender/spacing_adjustment.py` moves stations and transfer belts while retaining portal locations and machine scale.

Those current source values remain consistent with P07's refinery threshold `(7.506663706,-4.084283177,0)` and outer seam `(8.606663706,-4.084283177,0)`. The refinery source entrypoint now has a different hash from the older Astra check (`4d0774523b...` current `build_refinery.py` versus historical `645cea921a...`) because the cobalt art/room pass is now called after layout and spacing. Its current saved scene is also a different artifact: `blender/Refinery.blend` is SHA-256 `890460de55c331bba30abc80da3eb71f29d11f9f8ada6bca465cd178b43d71d8`, while the older spacing050 saved check was `7d62a7e609f2abae566f6be364e8a284176e12a722739f780083cb3b91e02cd2`.

The current `production/cobalt_final_manifest.json` binds the `890460...` file to room dimensions `15.013327413 × 12.868566354 × 4.8 m` and records its scope as static geometry/access. It does not provide a fresh F01 seam ray/sill/cart-sweep proof. Therefore the P07 position is source-consistent, but the current changed refinery save does not inherit the old spacing050 cold-start evidence as exact current-save proof.

## Reactor / F02

Current reactor architecture source remains consistent with P07:

- `blender/build_scene.py` portal construction retains the `FUEL HANDLING` opening at local `(0,10.8,0)`, nominal width/height `5.00 × 5.00 m`, a 3.70 m link stub and outer seam at local Y14.50.
- The current factory helper hash is `b4dd705e17c1544f63085dc010e98b96390b4aeadaf73d34d6656a37a6e9160b`, matching the identity recorded by the prior interface audit.
- The active reactor saved scene remains SHA-256 `5c62f8f6fbe66322148aec53c9f272d40ca5c6ad13223961465c6bfc86714f52`, with its last-write identity matching the prior active palette-amber-02 record. This is historical saved-scene identity evidence, not a newly evaluated seam test today.

The current payload source is the incremental machinery workflow, not the legacy receiving block still present in the factory helper. `production/build_machinery_flow.py` remains hash `2c18168ff9c8e6d35c4d73bb8d3f32f5036f4bb57d02f3047cba39c42acb98e6` and constructs the replacement family as a 1.18 m body, 0.310 m body diameter, ±0.605 m closures, 0.035 m closure thickness and 0.340 m closure diameter, giving 1.245 m overall cartridge length. Current wall A/F passes retain this payload size; their recorded hashes remain `55b73fe46552c8b64e13196428a0489b76a6e092a3bce8b997ea6fa2d6419288` and `1e76272ca0a492510028d7c66d888b0607f58a2590ceca6fdb6f57e3e8e124c6`.

This is consistent with P07's current reactor payload description. It does not establish that refinery's 0.480 m units can be packed, converted or owned through to the reactor cartridge. The reactor's static distant fuel closure remains a barrier in the source architecture; no opening controller or through-passage proof is implied.

## Interface decision and limits

P07 remains correct as a **local source contract** for F01/F02 seam positions, normals, nominal openings and the current reactor cartridge family. The changed current refinery save and unchanged historical reactor save have different evidence freshness, so neither should be presented as a newly combined-world proof. F01 sampled clearance remains bounded, F02 neighboring doors remain closed, and assembled sill/stub overlap, collision, runtime opening and payload interchange remain unverified.

S01 PLANT, S02 CLEAN and S03 WASTE remain reserved local headers. No current adjacent destination dimensions or fit were found in this read-only check; interface consistency must not be converted into destination approval.

**Luna interface result: source-level P07 consistency retained; integration/runtime HOLD.**
