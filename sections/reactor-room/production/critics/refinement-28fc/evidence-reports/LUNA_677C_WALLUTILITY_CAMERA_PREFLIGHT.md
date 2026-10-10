# C677c Wall Utility Camera Preflight

Candidate source: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
Source SHA-256: `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`

This is a camera-framing and finite visibility preflight for criteria #129 and #132. It is not pixel evidence and closes neither criterion. The probe loaded the exact saved candidate, hid the LP haze volume from the viewport ray test because it has no opaque surface, evaluated cameras at 1280×720 with a 36 mm horizontal sensor, and checked saved mesh vertices and first-hit rays.

## #129: wall box construction

The representative is the north-wall `a_junction` placement at wall index 4, `u=1.2`, `h=3.2`. The saved front assembly occupies approximately `x=4.568–5.032`, `y=10.606–10.800`, `z=3.060–3.672`. It combines the wall receiver/back plate, standoff, formed steel enclosure, four corner fasteners, yellow indicator, and two short black conduit tails. The broader `a_conduit_run` family was not isolated by the selected support rows, so this view proves only the representative mounted junction assembly.

Recommended direct view:

- Camera `(5.75, 8.55, 3.85)` aimed at `(4.80, 10.63, 3.43)`, 45 mm lens.
- All 158 of 158 selected assembly vertices project inside the frame; projected bounds are approximately NDC `x=.388–.649`, `y=.168–.749`.
- Of 128 front-facing component-face samples, 109 ray-hit the sampled box surface within 25 mm. The remaining samples meet another face in the same merged wall-assets family first, consistent with the layered plate, enclosure, conduit and fastener construction. No unrelated scene object is a first-hit blocker in the probe.

This framing keeps enough wall around the box to judge its back plate and stand-off against the host surface. The C89 wide north-wall view shows this family too small to judge those relationships.

The selected fixture is the individual `a_junction` family, which has two short conduit tails. The C677c support inventory contains 11 `a_junction` placements and no separately registered `a_conduit_run` assembly. The source has a helper for a continuous run, but this camera is not evidence for one. Issue #129 is titled “Wall box mounting/construction”; if its intended scope also requires a continuous routed conduit, that would need separate actual geometry and review.

## #132: doorway task lamp

The representative is the caged warm `a_lamp` directly above D2 / FUEL HANDLING on the north wall, centered near `(-3.75, 10.80, 5.85)`. Its evaluated bounds are `x=-3.858…-3.642`, `y=10.652…10.800`, `z=5.742…5.958`. It has a mounted rear plate, warm lamp body and black protective bars/rings. This is the doorway fixture; the hoist aperture LED is a separate object and cannot substitute.

Recommended close framing:

- Camera `(-4.25, 8.65, 5.56)` aimed at `(-3.75, 10.62, 5.84)`, 52 mm lens.
- All 656 of 656 selected lamp assembly vertices project inside the frame; projected bounds are approximately NDC `x=.402–.560`, `y=.357–.621`.
- Of 362 front-facing component-face samples, 330 ray-hit the lamp/cage surface within 25 mm. The other samples are on layered guard/body faces; they do not indicate unrelated-object occlusion.

For a little more doorway context at lower detail, camera `(-4.25, 7.80, 5.55)` aimed at `(-3.75, 10.62, 5.55)`, 45 mm, also frames every selected vertex. Its projected bounds are `x=.443–.539`, `y=.639–.804`; 341 of 364 front-face samples meet the component within 25 mm. Use the closer 52 mm view if the lamp cage and mount need a clear visual check.

The C89 view18 image shows the D2 sign/header and illuminated doorway, but the small lamp fixture itself is not large enough there to judge its guard, mount, and relation to the local light patch. A full-quality direct view of the saved fixture is still required.

## #131: typography

No concrete font, spacing, or curve-resolution defect has been found in the reviewed wall titles, signs, controls, or state boards. The saved 93-font inventory reports no degenerate evaluated glyph meshes, and actual current samples reviewed so far are clean. Keep #131 partial until the final source’s broad text set has been judged in its required images; this preflight does not identify a new camera or a specific bad glyph.

## Probe record

- Executed probe: `evidence/LUNA_677C_WALLUTILITY_CAMERA_PREFLIGHT.py`
- JSON output: `evidence/LUNA_677C_WALLUTILITY_CAMERA_PREFLIGHT.json`
- Candidate source and all projection/ray results are recorded in that JSON. Probe script SHA-256: `c6890ffbb18fe30ce9574c1da95d2cc3fc7de1a42a243a3d9fb7dbceeb840d4b`; JSON SHA-256: `25f3fa51a21bec1a9ca30f6b688f15a90c6a2d8e4dad42712f2aca496c43e223`.
