# R25 AAA finish (owner request, October 2026)

Owner asked for the refinery room to get the same treatment as the electrical room: final AAA materials and lighting, a
triangle check, and a scarier, gloomier mood. Scope chosen: materials and lighting on the same geometry; harsher lighting
from fewer working fixtures; triangle budget **400,000** visible triangles.

`../module_overhaul_R1.blend` is now R25 (R24 stays in git history and the accepted R24 evidence). R25 is **not** independently
reviewed or scored; the 99.10 review in `critics/R24_fresh_final.md` describes R24.

## What changed (`blender/revision_R25_aaa_finish.py`, applied once to the R24 candidate)
- **Floor screed (4 materials):** aggregate flecks, pits, hairline cracks and world-space puddles (dark, near-mirror, pooled
  rim) over about a fifth of the slab.
- **Wall plaster (3 materials):** chipped paint over primer with rust in the deeper chips, drip streaks, blotchy tone,
  orange-peel relief and cavity grime. Base tone lifted so it stays readable under the dimmer lighting.
- **Paint and bare metal (13 materials):** mottling, cavity grime, scratch roughness and bright worn edges.
- **Edges:** 257 machine bevels thinner than 4 mm widen to 4 mm angle-limited chamfers so edges catch the harsher light.
  Support-registered assemblies are skipped so their validated contacts are unchanged.
- **Lighting:** three more fixtures fail (Wall service lamp 3, Eyewash service practical, Mine transfer wall bulkhead), so nine of
  the 21 are out and 12 work. Their lens emission is zero and they are added to the failed-fixture registry. The remaining
  lights are re-balanced (task lights up, thresholds and fills down), spreads tightened to 130/150 degrees and tinted slightly sicker.
- **Haze:** a faint cold volume scatter (density 0.004) on the world. It has no emission; world illumination stays 0 and the
  only light sources remain the modelled fixtures.
- **Text legends:** 82 font objects drop from 12 to 6 curve segments per span. They are flat printed legends and stay legible
  at the fixed cameras; this is what brings the room under budget.

## Triangles
The room validator counts evaluated meshes **and** text curves. R24 measured **418,610** visible triangles (303,085 mesh +
115,525 curve/font), already over the 400,000 budget set for this pass. R25 measures **376,036** visible triangles, within
budget by 23,964. There is no repo-wide budget; 400,000 is the owner's figure for this pass. Engine draw calls were not measured.

## Evidence that ran
- `validation_R25.json`: the room's own `validate_overhaul.py -- R25` **PASS**: 29 protected interfaces unchanged, 21 light
  sources match modelled fixtures, nine failed fixtures verified at zero emission, world strength 0, no missing dependencies.
- `build_R25.json`: receipt of the stage, including triangles before and after.
- `renders/R25/`: the 11 fixed views from the existing renderer (960x540, 24 samples, seed 73).

## Not done / not claimed
- No independent critic review and no scoring.
- The R23 actual-map context was not re-rendered; R25 geometry and placement are unchanged except the bevel widening.
- Unity import, runtime performance and draw calls are unmeasured; the shaders add Bevel and AO nodes, and the haze adds volume cost in Cycles.
- Legacy cached material IDs for the whole-map diagnostic were not re-checked.
