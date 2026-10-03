# Reanimation room AAA finish (owner request, October 2026)

Same treatment as the electrical room, refinery and fuel corridor: deeper materials, a scarier and gloomier mood, and a
triangle check. Stacked on the unmerged #65 branch. Budget chosen by the assistant after measuring: **500,000 visible triangles**.

`../../module_overhaul_R2.blend` is now this finish (the delivered R2 is in git history of #65). It is **not** independently
reviewed or scored; the cycle-17 review describes R2.

## What changed (`../../reanimation_aaa_finish.py`, applied once to R2)
- **Floor (2 materials):** flecks, pits, hairline cracks and wet puddles in world space.
- **Plaster (2):** chipped paint over primer with rust, drip streaks and grime.
- **Enamels, steel, ivory, copper (12):** mottling, cavity grime, scratch roughness, bright worn edges (shader only).
- **Mood:** exposure lowered 0.5 EV, area-light spreads capped at 130 degrees, faint cold volume haze (no emission).
- **Triangles:** the interrupted-recovery care sheet (40k) gets a 0.35 collapse-decimate modifier.
- **Not touched:** the lighting contract (exactly four active lights: one red OCRU, one warm practical, two dim spots) is checked
  by `verify_overhaul.py`, so no light was added, removed or re-powered. Bevel modifiers and inherited text objects are unchanged:
  changing them moved inherited bounds (1e-6 m check) and 8 support gaps by up to 5.7 mm.

## Triangles
Visible evaluated: **517,406 -> 491,012** (meshes plus text curves, with modifiers). Budget 500,000. Source meshes are unchanged;
the decimation is a modifier and was not applied for export.

## Evidence that ran
- `verify_overhaul.py -- --cold`, result kept in `aaa-verification.json`: all 217 registered support contacts pass, no resized
  inherited objects, lighting contract holds. The single reported error is "Missing linked map/dependencies", which the unmodified
  R2 reports identically in this partial checkout (the exterior and preview files were not pulled). It was not re-run with a full checkout.
- `aaa-build.json`: receipt of the stage with triangles before and after.
- Three preview renders (entry, hero, recovery) were used to tune the look; no full fixed-view set was rendered.

## Not done / not claimed
- No independent review or scoring, and no full 17-view re-render; render the fixed views before accepting.
- Verification with all linked dependencies present was not run.
- Unity import, draw calls and runtime cost unmeasured; the shaders add Bevel/AO nodes and the haze adds Cycles volume cost.
