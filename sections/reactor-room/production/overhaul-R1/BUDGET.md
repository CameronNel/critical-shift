# Reactor room performance budget (proposed, unmeasured)

Fixed input from the owner: **60 fps on an RTX 3050, medium settings, 1080p**. The numbers below are engineering targets I chose to make that likely; none has been profiled. There is no Unity project or engine build in this repository, so no engine frame time was measured. Triangle counts are Blender evaluated, triangulated meshes; object and draw-call counts are the Blender object count and an object x material estimate before any static batching.

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
