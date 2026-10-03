# Turbine room AAA finish (owner request, October 2026)

Same treatment as the electrical room, refinery, fuel corridor, reanimation room and compliance dock. The turbine room is
the original module, not a previously overhauled one, and it was the brightest room by far (1,250 W "broad daylight",
entry and clerestory fills, exposure +0.45), so the mood change is large.

`module_overhaul_R1.blend` is `module.blend` plus `turbine_aaa_finish.py`, applied once. `module.blend` and `accepted.blend` are
untouched, so this is additive: nothing is promoted into the map. **Not independently reviewed or scored.**

## What changed
- **Floor (2 materials):** terrazzo and cast concrete halved in albedo with large wet reflective zones, cracks, aggregate.
- **Plaster (1):** chipped, rusted, streaked, grimy.
- **Paint and metal (13):** floor-level grime gradient, rust bloom on structural steel, primer, oxide and ochre enamels and machined
  steel, age darkening, stronger edge wear and scratch roughness.
- **Lighting:** light count and placement unchanged. Daylight 12 %, entry fill 10 %, clerestory fills 22 %, wall pools 35 %,
  practical pools 55 %, door pools 70 %, bench light up 1.3 times; area spreads capped at 120 degrees; cooler tint.
- **Mood:** exposure 0.45 to -0.45, world fill 0.18 to 0.05, cold haze (0.012) so the clerestory beams read.

## Triangles
**350,549** visible before and **350,549** after (282,557 meshes plus about 68k text curves), within 400,000. Geometry unchanged.

## Evidence that ran
- Before/after signature of all 1,661 objects (names, world matrices, vertex and polygon counts, modifiers, materials, cameras):
  **identical**; the only differences are the 21 intended light energies.
- About eight tuning renders (entry, hero, route, throttle, maintenance). No full 16-view set, no validator (there is no turbine
  validation script in the repo).

## Not done / weak
- No independent review or scoring; no full-view re-render; Unity cost unmeasured; shaders add Bevel/AO nodes and the denser
  haze costs Cycles time.
- The turbine casing still reads pale cream next to the dirty floor and walls. It is lit by the beams and a practical, and the
  age darkening was not enough; a dedicated casing material pass would fix it.
- Only materials and lighting changed: no new geometry or set dressing (PR #63's detail pass is separate).
