# Cooling plant AAA finish (A1)

Additive module `module_aaa_A1.blend`, produced from the original R10 `module.blend` by `cooling_aaa_finish.py`. The original
module, interface contract and geometry layout are unchanged; the old map is not touched. **Not independently reviewed.**

## What changed
- Floor and patched concrete: wet, cracked, stained screed with pooled puddles and dark rims.
- Walls (`mineral`): rough chipped plaster with primer and rust showing through, drip streaks, cavity grime.
- Paint and metal (cream, yellow, oxide, dark, steel, edge, rubber and others): floor-level grime, rust bloom, scratches, edge wear.
- Lighting: no light added or removed. Ceiling, motor-return, workshop, west-wall and entry fills cut to 20-60 %, practicals to
  80 % and tinted cooler; exposure -0.5 EV (now -0.4); world fill 0.02; faint cold volume haze.
- Geometry budget: 513,357 -> 314,609 triangles (budget 400,000). Text and curve resolution lowered (about -91k) and bevel
  segments 2 -> 1 on 1,180 objects under 1 m (about -108k). Larger objects keep two segments. Counts include text curves.
- Four new cameras: `AAA01_WIDE_REAR`, `AAA02_EXCHANGER_LOW`, `AAA03_PUMP_ROW`, `AAA04_WORKSHOP`. Existing cameras kept.

## Pump isolation valves moved into reach
The pump isolation wheels sat at 2.45 m behind each pump skid, out of reach of a player (assumed 1.75 m tall, shoulder 1.45 m,
reach 0.7 m; the repo sets no real size). `cooling_valve_relocate.py` re-routes each pump's return branch so it drops from the wall
header into the open lane between the pumps (pump A at y 6.1, pump B at y 8.7) and runs along the floor to the pump suction. The
valve (flanges, bonnet, wheel) is lowered to a 1.35 m wheel facing +X into the lane. No valve was added or removed. Recorded in
`interface.json` as `relocated_pump_isolation_valves`.

Saved-scene checks: no overlap with other meshes (each pipe touches only its own pump's suction hardware); wheel centre within
0.24 m of connected floor space in front of it, with a clear hand ray at 0.35, 0.5 and 0.65 m. A first layout put pump A's wheel
facing the wall controls panel, and a second put it against a wall column; both were rejected after the owner and the check
found the obstruction. **One deliberate overlap:** the wheels and bonnets stand about 0.23 m inside the keep-clear operator lanes
(3.85 m wide, minimum 1.3-1.4 m), which they leave far wider than the minimum. Pump A's floor run is raised to 1.0 m to clear
a wall cleat, and pump B's likewise. Cameras `AAA05_PUMP_VALVES` (pump A); pump B has a check render
`AAA06_PUMP_B_VALVE_check.png` taken from an unsaved camera. Receipt `valve-relocation.json`. Geometric reach only: no engine
interaction exists yet.

## Evidence
`aaa-build.json` (triangle counts, light scales), `renders-AAA1/` (800x450, 24-sample Cycles previews, one per new camera).

## Not done
- No room validator or collision/route sweep was run on this module; the R10 evidence belongs to the unfinished original.
- No full-resolution renders and no independent review.
- Hard-edge detail on small objects is now single-segment, so highlights are a touch crisper than the original.
