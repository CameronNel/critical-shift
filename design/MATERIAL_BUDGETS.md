# Material budgets per room (approved targets, unmeasured in an engine)

Status: **approved by the owner on 2026-10-01** (per-view cap of 40, the 15 shared families and the room caps below, as written). Open decisions 3-5 below remain open. Nothing here is engine-measured and no Unity project exists in this repository. The only fixed input from the owner is **50 fps at 1080p on the Low preset, RTX 3050** (changed by the owner on 2026-10-01 from 60 fps, medium; recorded in [ENGINE_DECISION](ENGINE_DECISION.md)). The caps below were chosen for the old target and are deliberately **not** loosened: the new target is a lower frame-rate and quality bar, but nothing is measured, so relaxing a cap now would be a guess. Revisit them after the first Unity measurement. Every cap below is an engineering target chosen to make that likely; change it only with a recorded decision. This document changes no asset, scene or code.

It extends [GAME_SPEC section 9.4](GAME_SPEC.md) ("simple shared material families, vertex colour/masks where useful, sparse functional decals") and the room targets in `sections/reactor-room/production/overhaul-R1/BUDGET.md`. It supersedes the single "at most 40 unique materials" row there: that figure was written for one room, and it is redefined below as a per-view cap.

## Why per-room counting is the wrong tool

Counting materials per room rewards copying: every room that re-creates "painted metal" pays for it again. A shared family is one material asset used by every room, so it is paid once per map and once per view. The budget therefore has three numbers:

1. **Shared families** (section below): one asset each, used by all rooms. Counted once.
2. **Room-unique allowance:** materials that only one room may own.
3. **Per-view cap:** distinct materials loaded for anything the player can see at once (the room they are in, plus the rooms or exterior visible through doors and windows). Proposed: **at most 40**, of which at most 15 are shared families and at most 25 are room-unique across the rooms in view.

## Measured starting point (Blender, 2026-10-01)

Visible mesh, curve and text objects of each room file, material slots in use, image textures reached through those materials. `module.blend` for each room except the reactor room, which uses the additive `module_overhaul_R1.blend`. Estimates from headless Blender; not engine numbers.

| Room | Materials now | Image textures now | Triangles now | Lights now |
|---|---:|---:|---:|---:|
| spawn-room | 189 | 15 | 111,384 | 14 |
| reactor-room (includes control room, 63 materials) | 111 | 11 | 321,554 | 69 |
| mine | 46 | 68 | 607,989 | 49 |
| fuel-corridor | 34 | 3 | 182,608 | 51 |
| condenser-bay | 28 | 0 | 171,626 | 27 |
| turbine-room | 28 | 0 | 93,493 | 21 |
| refinery | 27 | 3 | 88,898 | 16 |
| electrical-room | 26 | 0 | 91,344 | 8 |
| compliance-dock | 24 | 0 | 26,088 | 16 |
| waste-storage | 24 | 0 | 127,986 | 19 |
| medical-reanimation | 23 | 0 | 33,728 | 16 |
| cooling-plant | 22 | 0 | 179,889 | 15 |
| **Sum** | **582** | | | |

Notes: each room's count is by material name within that room, so a material used in two rooms is counted in both; the mine already exceeds the 400k-triangle room target (a separate issue, flagged here, not fixed by this document); the spawn room is the art-fidelity reference, so its look is the thing the shared families must reproduce, not a thing to simplify.

## Shared families (15 assets, used map-wide)

Each is one material with one shader. Variation inside a family comes from the tricks below, not from new materials.

| ID | Family | Trick that gives the variety |
|---|---|---|
| S01 | Painted metal and trim sheet | trim-sheet atlas (panel edges, bolts, stripes on strips); colour from palette UV |
| S02 | Bare metal: galvanised, graphite, steel, grating | packed mask texture; tint by vertex colour |
| S03 | Plaster, concrete, mineral wall | world-space (triplanar) tiling, no unwrap; vertex-colour grime and AO |
| S04 | Floor: tile, epoxy, concrete | triplanar tiling; floor-marking decals from S12 |
| S05 | Plastic and rubber | palette atlas (colour, roughness, metal per swatch) |
| S06 | Fabric, leather, canvas | palette plus vertex tint; one weave texture |
| S07 | Wood, laminate, paper, cardboard | one grain/paper atlas; palette tint |
| S08 | Flat-colour props and signal colours | **palette atlas**: a small swatch grid, UVs pick the swatch |
| S09 | Pipes, cables, hoses | palette plus vertex colour for service colour coding |
| S10 | Emissive: lamps, LEDs, indicator lights | palette UV picks colour; blink pattern id in vertex colour, blink computed from the global shader clock in seconds |
| S11 | Screens (CRT, TV, panels) | one shader, content from a texture atlas or array indexed per object |
| S12 | Decal atlas (alpha) | one map-wide atlas of posters, notices, stains, floor paint, stencils |
| S13 | Glass | one transparent material; tint per room by vertex colour |
| S14 | Haze, steam, light shafts | one transparent additive material, shared |
| S15 | Terrain, rock, soil | triplanar tiling; mine and exterior |

Only three of these are transparent or additive (S12 cutout, S13, S14), which also bounds overdraw.

## The tricks, in the order to apply them

1. **Palette atlas** (S05, S08, S09, S10): a 64 by 64 swatch grid carries colour, roughness and metal. A prop picks its colour by UV placement, so a thousand differently coloured flat props are one material and one texture. This is the largest single reduction.
2. **Trim sheet** (S01): one tileable atlas of strips (edge wear, panel seams, bolts, hazard stripes). Walls, doors and machine panels use strips by UV; no per-object texture.
3. **Triplanar world-space tiling** (S03, S04, S15): plaster, concrete, floor and rock tile in world space, so they need no UV unwrap and share one texture set across all rooms.
4. **Vertex colour for tint, grime and AO** (all families): the same material reads as three different paints, with baked occlusion, at zero extra materials and one extra mesh attribute.
5. **Packed mask texture**: roughness in one channel, metal in another, AO in a third, emission mask in alpha. One sampler instead of four.
6. **One decal atlas** (S12): as the reactor control room already did (24 materials to 1, 2048 px atlas, padded cells). Room-specific decals get a second atlas only if a room exceeds the first.
7. **One emissive material with shader-driven blink** (S10): blink pattern id in vertex colour; the shader derives the blink from the global clock in seconds (frame-rate independent, see `.agents/skills/blender-animation/references/animation-patterns.md`). This replaces the control room's 13 separate LED materials and keeps static batching intact, unlike per-object property blocks.
8. **One screen shader with an indexed atlas** (S11): every TV and monitor is the same material; the picture is an index, not a new material.
9. **Baked lighting, not dynamic lights**: lightmaps and probes carry the lit look; flicker rides on emissive. Budget: at most 6 dynamic lights in view, at most 2 shadow casters (as in the control-room light budget).
10. **Bake procedural materials to shared tile sets at export**: Cycles recipes do not survive glTF or FBX. The export step maps each recipe to the nearest family and bakes its mottling and wear into the family's tiles or into vertex colour, instead of exporting one baked material per recipe. This is how the spawn room's 189 recipes become about 24 materials without changing its look: the recipe differences are tint and wear, which vertex colour and the palette carry.
11. **Static batching and GPU instancing**: keep props that share a family mergeable; repeated props (chairs, lockers, rack units) share one mesh. This is what makes a low material count turn into a low draw-call count.

## Room caps

"Cap" is the most distinct materials the room's own file may use. "Shared used" is how many of S01-S15 it may draw from; "unique" is the room-owned remainder. Caps are tight on purpose: a room that needs more must say which family fails it.

| Room | Cap | Shared used (max) | Unique (max) | Unique materials this room is expected to own |
|---|---:|---:|---:|---|
| spawn-room (art reference) | 24 | 14 | 10 | hero PPE and suit set, signage face, suit-station glass trim, briefing screens variant |
| reactor-room (all) | 30 | 13 | 17 | pool water, core glow, crane, plus the control room sub-budget below |
| reactor-room: control room (inside the 30) | 16 | 13 | 3 | TV screen (custom clip slot), keyboard painted plane, window glass film |
| mine | 20 | 10 | 10 | rock variants, ore, timber, tracks, dust |
| fuel-corridor | 18 | 12 | 6 | fuel-rod glow, hazard barrier, rails |
| condenser-bay | 18 | 12 | 6 | water, tube bundles, wet-wall variant |
| turbine-room | 18 | 12 | 6 | turbine casing, rotor glow, oil sheen |
| refinery | 18 | 12 | 6 | tank skin, process-liquid glow, flare |
| electrical-room | 18 | 12 | 6 | busbar copper, insulator ceramic, panel glow |
| compliance-dock | 18 | 12 | 6 | dock rubber, manifest board, cargo wrap |
| waste-storage | 18 | 12 | 6 | drum plastic, contaminated-floor decal variant, glow |
| medical-reanimation | 20 | 12 | 8 | clinical white, reanimation glow, tubing, sheets |
| cooling-plant | 18 | 12 | 6 | coolant pipe glow, tower fill, wet metal |

**Map-wide total:** 15 shared plus the sum of the unique allowances, about 15 + 98 = 113 materials, against 582 slots counted above (before cross-room duplicates).

**Per-view check:** the worst view is probably a window or door looking from one hero room into another, for example spawn-room (10 unique) with the reactor room (17 unique) seen across a connector. That is 15 + 10 + 17 = 42, above the 40 cap. Resolve it when it is measured: the reactor room's unique count is the one to cut first, or its far-side materials fall back to the shared families beyond a distance. This is flagged, not hidden.

## Texture budget alongside the material cap

Proposed, unmeasured: shared sets total at most 6 textures (palette, trim sheet, plaster/concrete, floor, decal atlas, screen atlas); each room may add at most 4 room-unique textures, each at most 1024 px unless it is a hero asset. The mine currently reaches 68 image textures, so it breaks this outright and is the first candidate for the triplanar rock family.

## What each room's overhaul must report

For each room, next to its triangle and draw-call numbers:

- materials used, split into shared families and room-unique, against the cap above
- image textures used, against the texture budget
- number of dynamic lights and shadow casters, against the light budget
- the family each former recipe was mapped to, and the before/after look check (same views, same lighting)

Mark engine-side verification **Blocked** until a Unity target exists. Do not report a family mapping as visually accepted without the comparison renders.

## Open decisions (owner)

1. Approve the per-view cap of 40 and the 15 shared families, or change them.
2. Approve the room caps, in particular the hero rooms (spawn 24, reactor 30, mine 20, medical 20).
3. Decide who owns the shared families: they are map-wide assets, so a change to one touches every room (one owner and one branch at a time, as for `module.blend` files).
4. Confirm that the spawn room's look is the target the families must reproduce, and that the reactor room's unique count is the first to be reduced if the per-view check fails.
5. No upscaler or render-pipeline change is assumed here; the repository records the Built-in Render Pipeline ([ENGINE_DECISION](ENGINE_DECISION.md)), and some tricks above (texture arrays, shader-time blink) need a shader-level check in that pipeline before they are committed to.

## Progress log

- 2026-10-01, reactor-room control room (PR #54): step 1 applied, 63 -> 31 materials via seven shared families (S01, S02, S03, S05, S06, S07, S09) with recipe values on the mesh. Cap 16 not yet met; next: emissive family with shader-clock blink, indexed screen shader, floor into S04, glass into S13. Same-view renders before/after differ at noise level; the glTF round trip keeps the colours via `COLOR_0`. Not engine-measured.
