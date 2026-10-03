# Compliance dock AAA finish (owner request, October 2026): "very high level pass"

Same treatment as the electrical room, refinery, fuel corridor and reanimation room, pushed further because the dock was the
brightest and cleanest room (exposure +0.7, pastel pink plaster, tidy floor). Stacked on the unmerged #66 branch, which
failed its own review gate (C9 88.625 against the 99 gate); this pass does not claim to fix that review's findings.

`../../module_overhaul_R1.blend` is now this finish (F17 stays in #66's history). It is **not** independently reviewed or scored.

## What changed (`../../dock_aaa_finish.py`, applied once to F17)
- **Floor and concrete (3 materials):** flecks, pits, hairline cracks, wet stained patches.
- **Plaster (1):** heavily chipped, desaturated, rusted, with drip streaks and corner grime.
- **Paint and metal (14):** navy, charcoal, blue, ivory, coral, yellow, steel, brass, rubber and others get mottling, grime,
  scratch roughness and bright worn edges (shader only).
- **Mood:** exposure lowered 0.9 EV (+0.7 to -0.2), world fill cut from 0.16 to 0.05, the five unmotivated fill lights cut to 30 %,
  the 21 key lights to 80 %, colours tinted cooler and sicker, area spreads capped at 130 degrees, faint cold haze.
- **Not touched:** geometry, cameras, interfaces, light count and placement. This overrides F17's own "global exposure fixed"
  contract note, deliberately, per the owner's request.

## Triangles
Unchanged at **397,690** visible (378,905 meshes + 18,785 text curves), within a 400,000 budget (the figure used for the other rooms).
No reduction was needed or made.

## Evidence that ran
- `validate_dock.py` (`aaa-validation.json`): geometry and contract checks that can run in this partial checkout pass; the only
  failures are 18 `missing_library` errors for linked exterior/module files I did not pull. I did not run it against the unmodified F17 for comparison.
- Three preview renders (entry, hero dock, scanner approach) were used to tune the look; no full fixed-view set was rendered.
- `aaa-build.json`: receipt of the stage.

## Not done / not claimed
- No independent review or scoring; F17's known defects (duct/brace, return-duct/hanger and pallet/pilaster intersections,
  localized cloth distortion) are geometry issues and are **not** fixed here.
- No full 12-view re-render; no re-validation with all linked libraries present.
- Unity import and runtime cost unmeasured; the shaders add Bevel/AO nodes and the haze adds Cycles volume cost.
