# Independent C85 review and bounded carry

**Status:** rolling review only; no C85 visual evidence has been accepted and no overall score is assigned.

## Candidate and gates

- C84 parent: `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`, SHA-256 `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`.
- C85 candidate: `/workspace/scratch/reactor-refinement-cycle85/hall_final.blend`, SHA-256 `61bad7f0b34d5a9f7336e349c9e64cd8081666be62530e94ea56b4d2e36354ac`.
- Exact C84→C85 object delta: `/workspace/scratch/reactor-refinement-cycle85/scene-delta.json`, SHA-256 `11928627e159dc90a2f7df05772c60a7296fe02f05f02b1caea6ae184320c9c9`. It records 41 changed objects, 13 additions, no removals, no unexpected changes, and 1,879 unchanged. Its hash covers object transforms, parentage, animation bindings, mesh positions/faces/material indices/smoothing/sharp edges, font fields, material graphs, lights, and cameras within the declared comparison. This is a bounded object comparison, not exhaustive proof of every runtime or global scene property.
- Current candidate has 14/14 scoped authoring checks pass (`checks.json`, SHA-256 `f8ca350ba721b675428c0c99a124ba84624aefd753232d9eb4021919a814739c`), separate control-room verifier PASS, support audit PASS, and motion check PASS. These finite gates do not close the visual criteria or constitute an exhaustive all-pair collision audit.
- The separately rebuilt C85 cold scene SHA is `71cd73c2478e1dd0fe3203a4b8ce0b0471a6d1e8327de408960cdff285adab07`; its 14 checks and control-room verification pass. No whole-scene equivalence claim is made between the cold scene and the warm C85 blend.

## Exact correction scope

C85 contains five scoped changes:

1. Three board scales: 30 existing state-cell meshes moved, three existing scale text objects edited, and twelve additional scale labels added. Threshold materials, state drivers, actions, board mounts, and panel geometry are retained. C84 state frames showed fill from the wrong end. The corrected physical mapping still needs exact C85 green/orange/red pixels before #7 can pass.
2. Rod finish: two material graphs changed for absorber pins and drive guides. C85 makes the guide brighter and machined, and the pins darker satin metal. Geometry, lights, drivers, and rod supports are outside this edit; rows about their visible material distinction must be reviewed from current pixels.
3. Floor travel wear: the R2 wet-concrete material graph changes traffic/scuff response. Paint, water geometry, and floor mesh geometry remain unchanged. Because this material is used across the floor, prior pixels for floor appearance and material wear are not automatically carried.
4. Pool inlet: three saved diffuser/flange meshes have selected radial vertices reduced to radii 0.070 m, 0.072 m, and 0.075 m. At center `(-1.4,-3.0)`, radial distance from the pool center is 3.31059 m; against the 3.4 m liner, the largest part has a nominal 14.4 mm radial clearance. Current-C85 pixels are still needed to verify the inlet reads as a properly terminated assembly.
5. A local oil film is added near `(-8.58,-4.24)`. The current saved mesh has positive volume `0.000111536353 m³`, closed topology, 96 perimeter rays that hit the floor, and five support anchors. However, its underside is at z=0.00050 m while the floor is at z=0, leaving a 0.50 mm air gap. The support registration allows 1 mm and therefore does not prove the film touches the floor. The perimeter rays also do not sample the full interior footprint. **This is a confirmed C85 geometric defect; C85 remains a negative prototype and #140 stays open until a corrected candidate proves contact and clear interior.** Root has retained this C85 blend as a negative reference and is preparing C86 with the underside seated at z=0 and denser interior floor-clearance samples.

The oil-film defect means no C85 visual fix is accepted for #61, regardless of whether a diagnostic render looks attractive. C85 full render queues were not started.

## Bounded C84 carry

The machine-readable disposition file is [`LUNA_C85_DISPOSITIONS.json`](./LUNA_C85_DISPOSITIONS.json), source-bound to the exact C85 hash. It carries 81 previously accepted criteria from exact C84 evidence only where the changed subjects and neighborhoods are outside that criterion. C84 image paths, source hashes, and image hashes remain nested in each carried row. This is historical evidence carry, not a claim that C85 images were reviewed.

The following 25 issue IDs are not carried as accepted because C85 changes the relevant content, material, rendered substrate, or new geometry: **5, 6, 7, 58, 59, 60, 61, 62, 63, 66, 67, 68, 74, 75, 85, 91, 92, 94, 102, 131, 136, 137, 138, 139, 140.** Their prior C84 evidence remains historical context only. #131 stays partial pending current and room-wide typography evidence; all other listed rows remain pending current C85 evidence or geometry verification.

All other unresolved C84 items remain unresolved in C85. The C85 JSON has 81 bounded carries, 59 pending rows (including two partial rows), and no score. Ten current-candidate main views, exact current board states, affected floor/pool/rod pixels, and independent #140 geometry verification remain outstanding.
