# Reactor room performance budget (proposed, unmeasured)

Fixed input from the owner: **50 fps at 1080p on the Low preset, RTX 3050** (changed by the owner on 2026-10-01 from 60 fps, medium; see `design/ENGINE_DECISION.md` once PR #59 lands). The caps below were chosen for the old target and are not loosened: nothing is measured. The numbers below are engineering targets I chose to make that likely; none has been profiled. There is no Unity project or engine build in this repository, so no engine frame time was measured. Triangle counts are Blender evaluated, triangulated meshes; object and draw-call counts are the Blender object count and an object x material estimate before any static batching.

## Targets (to confirm)

| Item | Target | Why |
|---|---|---|
| Room triangles (excl. skylight/sky proxy) | at most 400k total, main view at most 250k visible | leaves headroom for shadow passes, which re-render geometry |
| Draw calls after static batching | at most 800 (animated and interactive objects stay separate, about 150) | draw calls, not triangles, are the main risk for this scene |
| Unique materials | at most 40, sharing at most 6 texture sets | fewer state changes, easier atlasing |
| Micro geometry | none (fasteners, tile courses and grating bars belong in textures/normal maps) | invisible at play distance |
| Animated/interactive | keep named, separate objects (`BANK_A_MOVING`, `COOLANT_VALVE`, `TURBINE_THROTTLE`, ...) | gameplay addressability (spec section 7) |

## Measured in Blender (same method for each row)

| State | Triangles | Objects | Draw-call estimate | Materials |
|---|---:|---:|---:|---:|
| `module.blend` (original) | 1,981,445 | 11,795 | 11,797 | 107 |
| After R1 layout + fastener and stair-residue cleanup + Asset Kit 1 | 594,301 | 4,535 | 4,537 | 89 |

The skylight/sky proxy adds 53,780 triangles and is excluded from both rows.

What produced the drop: about 1,760 orphaned stair-finish objects left over from the deleted stair, about 4,900 modeled fasteners and floor grating bars, and Asset Kit 1 replacing four heavy equipment groups.

## After the architecture rebuild and static merge (measured the same way)

| State | Triangles | Objects | Draw-call estimate | Materials |
|---|---:|---:|---:|---:|
| `module.blend` (original) | 1,981,445 | 11,795 | 11,797 | 107 |
| Rebuilt shell + Asset Kit 1 + lighting (`w25`) | 412,623 | 2,779 | 2,781 | 93 |
| After static merge (`i2_static_merge.py`) | 412,623 | 1,611 | 1,613 | 93 |

The rebuilt architecture is 23.5k triangles (176 objects); the legacy walls, structure and services it replaced were several hundred thousand. Triangles are inside the 400k target only if the roof proxy is excluded and are still slightly over it (412k). Draw calls are about twice the 800 target: the remaining objects are the gameplay-addressable stations, bank mechanisms and controls, which the merge pass deliberately leaves alone (all-caps interaction names, animated or parented objects, `MF WORKFLOW MACHINERY`, `04 BANK MECHANISMS`, `05 PERIMETER EQUIPMENT`). About 45 lights were also added, which a real-time build cannot run dynamically. None of this is engine-measured.

## Final state of this revision (all geometry counted: meshes, curves and text)

An earlier version of this table counted meshes only and understated curve and text objects (260,074 triangles / 1,271 objects). `scripts/stats2.py` counts everything.

| State | Triangles | Objects | Materials in use |
|---|---:|---:|---:|
| `module.blend` (original) | 2,191,850 | 12,936 | 107 |
| This revision (`module_overhaul_R1.blend`, after the station remodel, crane, dressing and door-stub pass) | 264,603 (mesh 258,284, curve 2,356, text 3,963) | 1,439 | 47 |

- Triangles are inside the 400k target (the roof/sky proxy, 53,780, is excluded as before; the glTF re-import counts 317,483 including it and the export's own triangulation).
- Draw calls: about 1,439 estimated, against the 800 target. Roughly 675 of the objects are gameplay-addressable stations and controls that were deliberately not merged. Not engine-measured.
- Materials: 48 against a target of 40. Every mesh has world-scale box-projected UVs.
- Lights: about 50. A real-time build can only run a handful dynamically; the rest need baking or emissive-only treatment.
- Engine hand-off: `engine/reactor_room_R1.glb` (26 MB, 22 animation clips) plus 29 baked 512 px tileable albedo textures. Bakes carry base colour and mottling only; edge wear and grime are Cycles-only. No lightmap UVs. The glb was re-imported to confirm counts; it has not been opened in an engine.

## Still to do to reach the targets

- Static merge pass by material and region for architecture, wall panels, structure, services and floor details (about 3,500 objects). This is the big draw-call win.
- Material consolidation from 89 to 40 or fewer, driven by the palette.
- Pool shaft lining (224 tile-course objects, 45k triangles) rebuilt as a few textured cylinders.
- Remaining equipment (generator/reserve power, grid cabinets, fuel racks, bank housings) redone to the same per-asset budgets: hero asset at most 2k triangles, station asset at most 1k.
- Measure in an engine build once one exists; until then treat every figure here as an estimate.

## Control-room optimisation pass (measured in Blender, same counting as above)

Scope: `31 CR CONTROL ROOM REDO` only. Visual-neutral tricks, all scripted:
- **Bevel segments 2 -> 1** (`crk.BEVSEG`): a single smooth-shaded chamfer reads the same at 2-12 mm and halves the bevel triangles (the main saving).
- **Cylinder sides scale with radius** (`crk.prism_seg`, 8 minimum): casters, screws, stems and lamps no longer carry 16-20 sides.
- **Ceiling tiles unbevelled** (their edges sit under the grid flange and cannot be seen).
- **Hidden-face removal** (`cr_optimize.py`): faces whose centre and corners are all flush (<= 1.5 mm) against another surface are deleted; coplanar dissolve with UV/material delimits.
- **Static merge** by material for dressing groups (wall, deco, ceiling, clutter, shelf, break corner, work table, door): 292 -> 226 mesh objects. UV layers are unified by name first (a mismatch put 8.9% of loops at (0,0)).

| State | Control-room triangles | Mesh objects | Materials in use |
|---|---:|---:|---:|
| Before | 154,462 | 292 | 85 |
| After | 74,589 | 226 | 85 |

Whole module (`scripts/stats2.py`): 413,910 -> 334,049 triangles including the 53,780-triangle roof proxy (about 280k without it, under the 400k target). glTF round trip of the control room: 74,613 triangles in and out, bounds difference 0.0 m, 0.3% of UV loops at the origin.
Same four views rendered before and after at frame 1: mean pixel difference 0.003-0.005, no 16 px block above 0.07 (sampling noise level); the cork board was regressed by a first, too eager face test (centre only) and fixed by requiring full coverage.
Not changed: **materials** (132 in the file, 85 in the control room, target 40: needs the atlas/bake step), **draw calls** (about 226 control-room objects, 1,704 module-wide, target 800; not engine-measured), no LODs, no instancing (props are merged world-space geometry). All numbers are Blender estimates, not engine measurements.

## Control-room real-time lights and material consolidation (measured in Blender)

**Light budget** (`scripts/cr_rt_lights.py`, spec in `control_room_light_budget.json/.md`): 18 authored lights -> 6 dynamic (three troffers with flicker/brownout/stability, the TV light, two beacons) of which 2 cast real-time shadows (middle troffer, TV); 12 are baked at their rest value (drivers removed, flagged `rt_mode=baked`). The CRT/rack flicker cue stays on the emissive screens and LEDs. Visible cost: during a brownout only the troffers and TV dip (mean frame luminance 0.150 with baked lights vs 0.132 with everything dipping), the rest of the room holds steady.

**Decal atlas** (`scripts/cr_atlas_decals.py`): 24 image materials (posters, notices, stickies, stains, floor paint, stencil, photo) -> one 2048 px RGBA atlas (scale 0.85 to fit, 4 px edge padding), one material, one joined object (29 objects -> 1).

| State | Control-room materials | Delivery images | glTF materials / images (round trip) | glb |
|---|---:|---:|---:|---:|
| Before | 85 | 72 | 87 / 72 | 12.7 MB |
| After | 63 | 49 | 64 / 49 | 11.7 MB |

Module file: 132 -> 109 materials, 1,704 -> 1,676 objects. Triangles unchanged (74,613 in and out of the glTF round trip, bounds 0.0 m, 0.2% of UV loops at the origin). Same four views before/after: mean pixel difference 0.004-0.006, no block above 0.07.
Still over target: **materials** (63 in the control room, 109 in the file, target 40 - the procedural surfaces, 13 blinking LED variants and screens remain separate), **draw calls** (200 control-room objects after the merges; module-wide target 800 not met). Nothing is engine-measured.

## Material families, step 1 (budgets in `design/MATERIAL_BUDGETS.md`, approved by the owner)

`scripts/cr_families.py` replaces the 39 procedural spawn-recipe materials of the control room with 7 shared family materials (S01 painted metal, S02 bare metal, S03 plaster and tile, S05 plastic and rubber, S06 fabric, S07 wood/paper/organic, S09 cable). The recipe values travel on the mesh: colour attribute `Col` (RGB base colour, A roughness) and `Mat` (R metallic, G bump, B variation, A edge highlight). Objects of the same group and family are joined.
Delivery (`cr_delivery.py`): a family exports as one glTF material (shared neutral grain tile) multiplied by `COLOR_0` (the `Mat` attribute is removed on the export copies because a second colour attribute makes the exporter write white, tested). The round trip multiplies `COLOR_0` into the base colour the way a glTF-compliant engine does; Blender's importer does not, so the check render adds it.

| State | Control-room materials | Mesh objects | glTF materials / images (round trip) | glb |
|---|---:|---:|---:|---:|
| Before step 1 | 63 | 200 | 64 / 49 | 11.7 MB |
| After step 1 | 31 | 120 | 32 / 11 | 10.9 MB |

Same four views before/after: mean pixel difference 0.006-0.008, no block above 0.07; the round-trip render (family materials via `COLOR_0`) was opened and keeps the colours, the cork board, the decals and the wall dado. Triangles unchanged (74,613 in and out, bounds 0.0 m).
Lost in the glTF export (Cycles-only): per-material mottling scale, bevel edge highlight, bump; the neutral grain tile replaces the mottling. Not lost in the Blender scene.
Still over the control-room cap of 16: 31 materials. What remains: 16 emissive materials (13 blinking LEDs, tubes, beacon, lamps), 4 emissive screens (3 CRTs, TV), the decal atlas, floor tile, keyboard plane, glass, haze, 2 baked. Next steps: one emissive family with shader-clock blink (design item 7), one screen shader with an indexed atlas (item 8), floor into S04, glass into S13. Nothing is engine-measured.
