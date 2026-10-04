# R39 mine AAA mood (A1)

The correct mine is the wooden `R39 | Old mine` set from the assembled map. This folder holds it as a standalone module so the retiring
map file is not touched. **Not independently reviewed.** The concrete "Gullet Mine" is DO NOT USE and is not part of this module.

## What is here
- `extract_r39_mine.py`: copies the R36, R38, R39 and R40 mine collections (260 objects) out of `facility_environment.blend` into a new
  file and strips everything else. Run it against the map to reproduce the plain extraction (`module_r39.blend`, not committed; it
  is 115 MB and identical to this module apart from the lighting below).
- `r39_mine_aaa_finish.py`: the lighting pass applied to that extraction. Result: `module_r39_aaa.blend`.
- `aaa-build.json`: light and triangle counts from the build. `extract-receipt.json`: what the extraction kept.
- `renders-AAA1/`: 800x450, 24-sample Cycles previews, one per new camera.

## What changed
- Lighting only. The daylight sky is cut to about 12 % and exposure lowered 0.6 EV, giving a dim cold dusk. A very weak cool sun lamp
  (0.35) adds rim light and a faint cold haze fills the air.
- The 66 mine lights (lanterns, oil lamps, candles, notice lamp, cliff and cave crystals) are unchanged, so they read as accents; the
  crystal glows are 20 % stronger.
- Geometry and the hand-painted toon materials are untouched. Triangle count is unchanged at 4,083,512 (including text curves); the owner
  asked to keep the detail, so the 400k budget used for other rooms was not applied.
- Four new cameras: `R39_01_PORTAL_APPROACH`, `R39_02_TUNNEL`, `R39_03_YARD_WIDE`, `R39_04_SHED_FRONT`.

## Not done
- No room validator, collision sweep or reach check was run. No reach check was asked for.
- No full-resolution renders and no independent review.
- The mine's own interfaces (rail link to the refinery, doors) were not examined; the extraction keeps only the mine collections.
- `R39_04_SHED_FRONT` is almost black (the shed face is unlit at this camera); it should be re-aimed or lit. The other three views read well.
- The module has the sky but no ground beyond what the mine collections carry; the surrounding map terrain is not included.
