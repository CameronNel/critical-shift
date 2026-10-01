# Quality tiers: Ultra and Low (proposed, unmeasured in an engine)

Status: **proposal.** Owner intent (2026-10-01): *Ultra looks as close to the Blender renders as a real-time renderer can; Low costs as little as possible so weak GPUs keep the frame rate.* Performance targets ([ENGINE_DECISION](ENGINE_DECISION.md)): Low is the minimum-spec floor, **50 fps at 1080p on an RTX 3050**; the typical player is expected to run **High at 1080p on an RTX 5060** (frame-rate figure proposed at 60 fps, not yet confirmed by the owner). The table below has only Ultra and Low; where the typical-player High preset sits between them is not decided. Nothing here is measured: no Unity project exists, so every statement about speed is a design intent or a vendor recommendation, not a result. Engine implementation is **Blocked**.

## Principle

Same art, computed once. Low does not remove content; it moves work from every frame to the build:

- Lighting that is never computed at runtime is the cheapest lighting (Unity's own guidance recommends baking static lighting instead of computing it every frame).
- Flicker, brownouts, the TV picture's light and the beacon pulse are **modulators**: small per-frame scalars that scale pre-baked lightmaps, so Low keeps the eerie look at near-zero GPU cost.
- Ultra adds real-time work on top of the same baked data.

## What the Low tier is made of (control room, built and checked in Blender)

Produced by `sections/reactor-room/production/overhaul-R1/scripts/cr_lightmaps.py`:

| Lightmap | Contains | Runtime modulator (from `control_room_runtime_behaviour.json`) |
|---|---|---|
| static | 12 baked lights, ambient, steady emissive surfaces | none (constant) |
| troffer | three troffers and their tubes at reference energy | troffer expression: stability, flicker, brownout |
| tv | the TV light (white, reference energy) and screen glow | TV colour x energy: follows the picture |
| beacon | the two red beacons at reference energy | beacon pulse |

Low-tier surface colour = `albedo x (static + troffer x m_troffer + tv x m_tv_rgb + beacon x m_beacon)`. All four maps share one second UV layer. Zero real-time lights, zero shadow maps. Decode values, scales and reference energies are in `control_room_lightmaps.json` next to the maps.

## Tier table

| Feature | Ultra | Low |
|---|---|---|
| Static lighting | the four lightmaps | the four lightmaps |
| Dynamic lights | up to 6 in view (3 troffers, TV, 2 beacons); at most 2 real-time shadow casters | none: modulators only |
| Shadows | real-time soft shadows for the 2 casters, baked shadows elsewhere (Mixed lighting) | baked only |
| Ambient occlusion | screen-space AO on top of the baked occlusion | baked only |
| Reflections | one baked reflection probe per room, box projected | one low-resolution probe per room |
| Surface detail | detail normal map (bump, bevel edge highlight) over the family albedo | vertex colour tint and neutral grain only |
| Texture resolution | full | one mip level lower |
| Post-processing | bloom, colour grading, vignette | colour grading only |
| Anti-aliasing | SMAA or TAA | FXAA |
| LOD bias, draw distance | high | reduced |
| Materials in view | at most 40 ([MATERIAL_BUDGETS](MATERIAL_BUDGETS.md)) | same |

Rows marked "detail normal map", "SSAO", "TAA" are not built yet; they are what Ultra spends its budget on and are proposals.

## Developer practices applied or planned (engine documentation and vendor guidance)

Source: Unity manual and Unity guidance pages found 2026-10-01 (optimising lighting, graphics performance, mobile lighting tips). I could not open the manual pages from this environment, so the list rests on the search summaries; exact setting names for Unity `6000.4.3f1` and the Built-in pipeline must be checked in the editor before they are committed to.

| Practice | State |
|---|---|
| Bake static lighting into lightmaps instead of computing it every frame | **Done** for the control room (Blender side); not tried in an engine |
| Reduce real-time lights and real-time shadows; Mixed lighting (baked indirect, shadowmask) for the few that remain | Planned (Ultra: 6 lights, 2 shadow casters) |
| Static batching for non-moving geometry sharing a material | Enabled by the family and static merge work (fewer materials and objects); the Static flag is an engine step |
| GPU instancing and shared meshes for repeated props | Planned (props are merged in world space today) |
| Occlusion culling in complex static scenes | Planned; needs the engine |
| LOD groups | Not done: the control room's props are merged per group, so LODs are meaningful only for individually placed props. Note that LOD groups change how baked lighting is applied (only the most detailed level is lit as static) |
| Fewer, shared materials; atlases | **Done** for the control room (63 -> 31), budgets for all rooms |
| Texture compression and mipmaps | Planned; engine import setting |
| Light probes for moving objects (players, doors) | Planned; probes are an engine step |

## Cost and check of the Low tier (Blender side, control room, PR #54)

- Texture memory: one 2048 px map plus three 1024 px maps, about 6.5 MB as PNG (engine compression will differ); 48.6 texels per metre over 663 m2 of surface; 37% of the atlas used.
- Visual check: the Low tier was emulated as `albedo x lightmaps` with no lights and rendered from the same four cameras as the path-traced renders. Mean luminance is 81%, 68%, 94% and 84% of the path-traced frame (wide, desk, rack, door); mean pixel difference 0.04-0.08. The side-by-side images were opened. It keeps composition, mood, the warm/green split, shadow shapes and decals; it loses real-time specular, contact grain and floor grime, window sheen and sharp shadow edges. A lightmap gain of about 1.2 would match mean brightness (not render-verified). Ultra adds the specular and shadows back with real-time lights.
- Engine check: **Blocked.** Real frame time on the target hardware is the only number that counts.

## Open decisions (owner)

0. Settle the tier names and what High (the 5060 target) switches on between Low and Ultra; confirm its frame-rate figure.
1. Approve the tier table (what Ultra spends, what Low drops).
2. Decide whether Low is the default for first launch on a weak GPU, or a manual choice.
3. Create the bounded Unity trial (project, one room, profiler capture on the target GPU). Without it the tier numbers stay estimates.
