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

## Still to do to reach the targets

- Static merge pass by material and region for architecture, wall panels, structure, services and floor details (about 3,500 objects). This is the big draw-call win.
- Material consolidation from 89 to 40 or fewer, driven by the palette.
- Pool shaft lining (224 tile-course objects, 45k triangles) rebuilt as a few textured cylinders.
- Remaining equipment (generator/reserve power, grid cabinets, fuel racks, bank housings) redone to the same per-asset budgets: hero asset at most 2k triangles, station asset at most 1k.
- Measure in an engine build once one exists; until then treat every figure here as an estimate.
