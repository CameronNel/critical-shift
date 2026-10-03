# Compliance dock AAA finish (owner request, October 2026)

"Very high level pass", then "not good enough": a second, harder pass that also fixes F17's reviewed technical defects.
Stacked on the unmerged #66 branch, which failed its own review gate (C9 88.625 against 99). **This work has not been
independently reviewed or scored and does not claim to meet that gate.**

`../../module_overhaul_R1.blend` is F17 plus `../../dock_aaa_finish.py`, applied once.

## What changed
**Geometry (new in the second pass).** Three of C9's four technical defects, found by exact BVH overlap before and after:
- C09-T01 supply duct through five truss diagonals: 100 overlapping triangle pairs to 0 (clearance openings cut in the duct).
- C09-T02 suspension steel through the return duct: 96 to 0.
- C09-T03 pallet corner in pilaster and flange: 56 to 0.
The cuts are Boolean differences against slightly enlarged copies of the passing parts; originals are untouched, only the duct,
return duct and pallet meshes were replaced. The boolean left stretched UVs and two zero-area triangles, so those meshes are
welded, degenerates dissolved, triangulated and re-unwrapped isometrically into every UV layer (including `CD_Physical_1m`).
No opening sleeves or collars were modelled. **C09-T04 (consumed cloth return-chart distortion) is not fixed.**

**Floor.** Albedo halved, much larger wet zone (puddles cover roughly a third of the slab) with a dark pooled rim, gloss and
reflections, hairline cracks, aggregate and pits.

**Materials up close.** Chipped, rusted, desaturated plaster; on 14 paint/metal materials a floor-level grime gradient, rust
bloom on steel/navy/charcoal/blue/yellow, stronger edge wear and scratch roughness. The orange `coral` is knocked back so hazard
colour owns the accent (reviewer LUNA-V12), and the pink-mauve fields are gone (LUNA-V11).

**Lighting.** Light count and placement are unchanged; no light was added. Ceiling washes to 60 %, ambient fill to 30 %,
hero keys and cargo/inspection practicals up 1.5 to 4 times, low-bounce cargo lights 6 times, hazard spots 5 times (lead tunnel
spot 20 times) and tightened, other keys 90 %. World fill 0.12, exposure 0.6 (from 0.7), cool-tinted lights, spreads capped at 110
degrees, denser haze (0.008) so beams read.

## Triangles
**398,352** visible (within 400,000). F17 was 397,690; the cuts add about 660.

## Evidence that ran
- Exact overlap counts before and after for the three fixes (in `aaa-build.json`).
- `validate_dock.py` with the interface file (`aaa-validation.json`): **one failure, the same as untouched F17**
  (`aaa-validation-baseline-f17.json`): a linked library not present in this partial checkout (`facility_environment.blend`
  once pulled; later runs list further exterior files). All overhaul UV, zero-area-triangle, support and clearance checks that can run here pass.
- Tuning renders only (about 20 across both passes). No full fixed-view set.

## Honest self-assessment
- **Better:** floor, wall paint and edge wear read much more convincingly; the entry (C01), scanner approach (C04), gate (C06)
  and office (C07) views are strong. The room is no longer the bright, clean outlier.
- **Still weak:** the lead-tunnel view (C05) is still the darkest and is dim to the point of being hard to read; it is readable
  but not good, and its lighting depends on bounce I only partly restored. The reviewers' shape-language and storytelling
  deductions (repeated rectilinear shells, tidy staging, generic labels) are **untouched**: they need modelling and set-dressing work, not materials.
- C09-T04 not fixed; no independent critic scoring; no full-library validation; no full 12-view render; Unity cost unmeasured;
  the shaders add Bevel/AO nodes and denser haze costs Cycles time.
