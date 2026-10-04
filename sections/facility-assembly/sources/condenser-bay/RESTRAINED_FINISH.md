# Condenser bay restrained finish (A1)

Additive module `module_restrained_A1.blend`, produced from the original R34 `module.blend` by `condenser_restrained_finish.py`. The
original module, interface contract and layout are unchanged; the old map is not touched. **Not independently reviewed.**

This is the first finish written to `design/ART_DIRECTION.md`: wear is localized and the room reads as active and maintained, unlike
the earlier cooling-plant and waste-storage finishes, which are heavier than the art direction asks.

## What changed
- Floor and floor patch: calm slab with broad tone variation, sparse cracks and a few small puddles.
- Plaster and cast concrete: broad staining, low wall scuffs and a few chips. No rust, no drip streaks.
- Paint and metal: floor-level grime, cavity dirt, light mottle; edge wear only on contact materials (brass, cast iron, ochre handrail enamel, brushed steel); one rust patch material (oiled iron, near the floor).
- Lighting: no light added or removed. Practicals trimmed to 85-90 %, tinted slightly cooler; exposure -0.15 EV (now -0.25); world fill 0.08; very faint cool haze.
- Geometry budget: 641,598 -> 386,490 triangles (budget 400,000). Text and curve resolution lowered, and bevel segments 2 -> 1 on 2,093 objects under 1 m. Larger objects keep two segments. Counts include text curves.
- Four new cameras: `AAA01_WIDE_NE`, `AAA02_PUMPS`, `AAA03_OPERATOR`, `AAA04_PULL_BAY`. Existing cameras kept.

## Reach check
See `reach-check.json`. Reachable: the door, both pumps, vacuum and ejector controls, hoist, operator panel (marginal). **Not reachable:** the two
cooling-water isolation valves (overhead main, 3.4 m), the condenser isolate hook (3.17 m), and the operator trip control (1.12 m, needs a
closer look). Nothing was moved; fixing the overhead valves needs a design choice.

## Evidence
`restrained-build.json`, `reach-check.json`, `renders-restrained/` (800x450, 24-sample Cycles previews, one per new camera).

## Not done
- No room validator or collision sweep was run on this module.
- No full-resolution renders and no independent review.
- Hard-edge detail on small objects is single-segment, so highlights are slightly crisper than the original.
