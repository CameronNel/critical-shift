# Fuel corridor AAA finish (owner request, October 2026)

Owner asked for the same treatment as the electrical room and refinery: final AAA materials and lighting, a triangle check, and
a scarier, gloomier mood. Choices: materials and lighting on the same geometry; **700,000 visible triangles** (first asked
400k, then raised to 700k after the room measured 2.1M).

`../../facility-assembly/sources/fuel-corridor/module.blend` is now this finish (F23ci stays in `production/checkpoints/`).
It is **not** independently reviewed or scored; the 99 reviews describe F22ci/F23ci.

## What changed (`blender/fuel_aaa_finish.py`, applied once to the F23ci native)
- **Floors (7 materials):** aggregate flecks, pits, cracks and wet, glossy puddles in world space.
- **Plaster (3):** chipped paint over primer with rust, drip streaks, grime. Base tone darkened a little.
- **Enamels, steel, brass (13):** mottling, cavity grime, scratch roughness, bright worn edges.
- **Edges:** the 49 two-segment 3 mm bevels become single-segment chamfers.
- **Mood:** light colours tinted slightly sicker and spreads tightened; a faint cold volume haze (no emission); exposure lowered
  0.6 EV. **Light energies are untouched and no fixture was added or removed**: their keyed flicker and optic emission are
  validated against the build manifest, so the mood is graded with exposure instead of re-powering fixtures.
- **Triangles:** text legends drop from 12 to 2 curve segments per span; 188 dense meshes (1,000+ triangles) get a 0.36
  collapse-decimate modifier, except the cartridge carrier, where it showed a texture glitch.

## Triangles
- Before: **2,115,734** visible (about 1.10M meshes + 1.01M text curves).
- After: **678,692** visible (432,300 meshes + about 246k text curves). Budget 700,000.
- This is evaluated triangles with modifiers; the source meshes are unchanged. A baked/exported delivery would need the modifiers
  applied, which was not done or measured.
- The corridor's own validator counts meshes only (432,300 now; 1,100,702 before the decimation modifiers). 

## Evidence that ran
- `AAA_VALIDATION.json`: `validate_overhaul.py` against `BUILD_MANIFEST_AAA.json` (a copy of the build manifest with the new
  native hash; the original manifest is untouched): **PASS, 0 failures**, including fixture-lighting and temporal flicker checks.
- `AAA_BUILD.json`: the stage's receipt (triangles, materials changed, light energies unchanged assertion).
- `renders/AAA1/`: the 19 fixed views (960x540, 24 samples) with the existing review renderer.

## Not done / not claimed
- No independent critic review and no scoring.
- The actual assembled-map views and the map-dim state captures were not re-rendered.
- Decimation is geometric simplification: silhouettes of dense props are coarser than F23ci; compare close views before accepting.
- Unity import, draw calls and runtime cost were not measured; the shaders add Bevel/AO nodes and the haze adds Cycles volume cost.
