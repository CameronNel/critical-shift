# Waste storage AAA finish (A1)

Additive module `module_aaa_A1.blend`, produced from the original W22 `module.blend` by `waste_aaa_finish.py`. The original module,
interface contract and layout are unchanged; the old map is not touched. **Not independently reviewed.**

## What changed
- Floor: wet, cracked, stained slab with pooled puddles and dark rims. The floor shared one material with the walls, so it got its own copy.
- Walls and repaired panels: rough chipped concrete with primer and rust showing through, drip streaks, cavity grime.
- Paint, steel and rubber (enamels, galvanized steel, bus casing, contact-wear steel, graphite beams, rubber): floor-level grime, rust bloom, scratches, edge wear.
- Lighting: no light added or removed. Practical pools cut to 45 %, directed washes to 80 %, other lights to 70 %, tinted slightly cooler; exposure -0.4 EV; world fill 0.03; faint cold volume haze.
- Geometry budget: 419,776 -> 351,868 triangles (budget 400,000), by lowering text and curve resolution only. Counts include text curves.
- Four new cameras: `AAA01_WIDE_ENTRY`, `AAA02_CASKS`, `AAA03_ISOLATOR`, `AAA04_DRY_QUARANTINE`. Existing cameras kept.

## Reach check
See `reach-check.json` for the model and per-item results. Summary: both contract hooks (`INTERACT_INVENTORY`, `INTERACT_VENT_ISOLATE`) and
all six overpack, dry-bin and quarantine lids are reachable. The two shielded-cask lid anchors sit at 2.24 m, above reach, but their
release levers are reachable (0.61-0.64 m) and their clamps marginal (0.70-0.72 m). The damper crank (2.37 m) and the jib chainwheel
(2.98 m) are out of reach; neither has a defined interaction. Nothing was moved to fix these.

## Evidence
`aaa-build.json` (triangle counts, light scales), `reach-check.json`, `renders-AAA1/` (800x450, 24-sample Cycles previews, one per new camera).

## Not done
- No room validator or collision/route sweep was run on this module.
- No full-resolution renders and no independent review.
- The isolator corner (`AAA03_ISOLATOR`) is dark; it is gloomy by intent but reads dim.
