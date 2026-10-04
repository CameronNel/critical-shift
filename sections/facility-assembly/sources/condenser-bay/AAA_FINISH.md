# Condenser bay AAA finish (A1)

Additive module `module_aaa_A1.blend`, produced from the original R34 `module.blend` by `condenser_aaa_finish.py`. The original
module, interface contract and layout are unchanged; the old map is not touched. **Not independently reviewed.**

An earlier restrained version of this finish (calm floor, bright ambient light) was built first and rejected by the owner as looking
bad; this dark, accent-lit version replaced it. It is heavier than `design/ART_DIRECTION.md` asks for ("a grunge-covered abandoned
bunker" is a listed non-target); it follows the owner's request.

## What changed
- Floor and floor patch: wet, cracked, stained slab with pooled puddles and dark rims.
- Plaster and cast concrete: rough chipped surface with primer and rust showing through, drip streaks, cavity grime.
- Paint, steel, iron, brass and rubber: floor-level grime, rust bloom, scratches, edge wear.
- Lighting: no light added or removed. Ceiling battens cut to 30 % so the local task, wash and gallery lights read as accent pools; other lights 50 %; tinted slightly cooler; exposure -0.4 EV (now -0.5); world fill 0.03; faint cold haze.
- Geometry budget: 641,598 -> 386,490 triangles (budget 400,000). Text and curve resolution lowered and bevel segments 2 -> 1 on 2,093 objects under 1 m. Counts include text curves.
- Four new cameras: `AAA01_WIDE_NE`, `AAA02_PUMPS`, `AAA03_OPERATOR`, `AAA04_PULL_BAY`. Existing cameras kept.

## Reach check
See `reach-check.json`. The door, pumps, vacuum and ejector controls, hoist and operator panel are reachable. **Not reachable:** the two
cooling-water isolation valves (overhead main, 3.4 m), the condenser isolate hook (3.17 m), and the operator trip control (1.12 m, needs
a closer look). Nothing was moved; the overhead valves need a design choice.

## Evidence
`aaa-build.json`, `reach-check.json`, `renders-AAA1/` (800x450, 24-sample Cycles previews, one per new camera).

## Not done
- No room validator or collision sweep was run on this module.
- No full-resolution renders and no independent review.
- Hard-edge detail on small objects is single-segment, so highlights are slightly crisper than the original.
