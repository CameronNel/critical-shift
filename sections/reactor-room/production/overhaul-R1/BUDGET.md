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

## Final state of this revision (same measuring method)

| State | Triangles | Objects | Draw-call estimate | Materials in use |
|---|---:|---:|---:|---:|
| `module.blend` (original) | 1,981,445 | 11,795 | 11,797 | 107 |
| This revision (`module_overhaul_R1.blend`) | 260,074 | 1,271 | 1,271 | 77 |

Triangles are inside the 400k target (the roof/sky proxy, 53,780, is excluded as before). Draw calls are still about 1.6x the 800 target: roughly 675 of the objects are the gameplay-addressable stations and controls (`05 PERIMETER EQUIPMENT`, `MF WORKFLOW MACHINERY`), which were deliberately not merged so each interaction stays separately addressable. Materials are 77 against a target of 40. There are 50 lights: fine for Cycles, but a real-time build can only run a handful dynamically. The Cycles procedural materials (bevel and world-position nodes) must be baked to textures with UVs for an engine build; nothing is UV-unwrapped or baked yet. None of this is engine-measured.

## Still to do to reach the targets

- Static merge pass by material and region for architecture, wall panels, structure, services and floor details (about 3,500 objects). This is the big draw-call win.
- Material consolidation from 89 to 40 or fewer, driven by the palette.
- Pool shaft lining (224 tile-course objects, 45k triangles) rebuilt as a few textured cylinders.
- Remaining equipment (generator/reserve power, grid cabinets, fuel racks, bank housings) redone to the same per-asset budgets: hero asset at most 2k triangles, station asset at most 1k.
- Measure in an engine build once one exists; until then treat every figure here as an estimate.
