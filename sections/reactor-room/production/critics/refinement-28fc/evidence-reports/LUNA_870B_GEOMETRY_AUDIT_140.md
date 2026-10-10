# 870b bounded finite geometry audit — issue 140

## Receiving source and delta

Candidate `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`. The exact parent 0058 source is `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`. The source-bound comparison `/workspace/scratch/reactor-refinement-bearing-lit-working/scene-delta.json`, SHA-256 `d2f459528aff38b56ef2ef05b3accbdf33db6bf24b73ee26a5cd6533befcdebe`, reports 14 additions (12 mounted 2 W lights, shared housing and lens meshes), 1,954 unchanged objects and zero retained changes, removals or unexpected changes.

## Current and cold checks

- Current 14-check summary `/workspace/scratch/reactor-refinement-bearing-lit-working/checks.json`, SHA-256 `e331367443e812974313ac2f6a723de0bb0b5210b2b4e1791835b7bc700573de`: all 14 pass, each exit code 0, bound to the 870b SHA. The checks cover door hardware, floor guidance, blind covers, rod guides, roof utilities, gantry guards, bores, contracts, piping, clearance, palette, frame rate, motion and support.
- Current control-room check `/workspace/scratch/reactor-refinement-bearing-lit-working/control-room-check.log`, SHA-256 `8b6a7f2c3fd57bb13b1bdad0bc538251b8825ad896ca8d087d55da53a7f0840b`: `RESULT: PASS`.
- Current source audit `/workspace/scratch/reactor-refinement-bearing-lit-working/audit.json`, SHA-256 `d4db2d53e22af7cd6846a6e1f9993c83a8f20b0994d4d34a2e8908215d1067f2`: bound to the 870b source. It reports 203 signage records with zero failures, 732 camera-visibility records, 5 required camera sightlines, 3,521 support records with zero failures, 2,148 registered assemblies across 29 owners, zero empty registrations and all 290 protected objects unchanged.
- Current service-core probe `/workspace/scratch/reactor-refinement-bearing-lit-working/wall-bores.json`, SHA-256 `c7cc380fce3db144a4b14bdb204f1d4ba618a1817533f5eccd5f632611c5887e`: eight named service cores, 65 rays per port and zero reported enclosure hits.
- Cold candidate `/workspace/scratch/reactor-refinement-bearing-lit-working-cold/hall_final.blend`, SHA-256 `b3447d1fdb596633fcf30a0c8bdb46dc0b3d648bb0749b4b920f9621e488a300`.
- Cold 14-check summary `/workspace/scratch/reactor-refinement-bearing-lit-working-cold/checks.json`, SHA-256 `5d0ffcf70a41a89f34ff801bba887d3d85b1a9c80533c238dfdb8f727ec4bd9e`: all 14 pass and bind to that cold source. Cold control-room check `/workspace/scratch/reactor-refinement-bearing-lit-working-cold/control-room-check.log`, SHA-256 `dd2d46e69897c205bba599e1ac68fe725f8a7651c7c20dade03abbe8830a83ed`: `RESULT: PASS`.
- Cold declared-scope comparison `/workspace/scratch/reactor-refinement-bearing-lit-working-cold/scope.json`, SHA-256 `f48fed6a8634913febbefd63495650f4695eb5c05c3f25b7d8632218e20a3029`: 118 of 118 declared owned comparisons match between current and cold sources.
- Cold audit `/workspace/scratch/reactor-refinement-bearing-lit-working-cold/audit.json`, SHA-256 `958b30281f5c065f9109aa6d666d6f5825a884959fb1cac18eac4501cd81437c`: same bounded audit counts and no registered support/signage failures.

## Disposition and limits

Accept #140 for this exact finite 870b geometry/authoring scope. These checks establish the registered assemblies, named bores, 14 source-bound authoring checks, cold reproducibility and the declared 118 comparisons. They do not establish exhaustive all-vertex collision absence, every object-pair clearance, whole-scene current/cold equivalence, rendered legibility, global illumination quality or a final art score. The 870b roof-light additions are explicitly included in this candidate's technical scope.
