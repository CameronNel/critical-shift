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

## Evidence
`aaa-build.json` (triangle counts, light scales), `renders-AAA1/` (800x450, 24-sample Cycles previews, one per new camera).

## Not done
- No room validator or collision/route sweep was run on this module; the R10 evidence belongs to the unfinished original.
- No full-resolution renders and no independent review.
- Hard-edge detail on small objects is now single-segment, so highlights are a touch crisper than the original.
