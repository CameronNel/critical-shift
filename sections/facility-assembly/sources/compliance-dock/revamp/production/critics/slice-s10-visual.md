# Compliance dock s10 — independent visual slice review

**LOCAL PASS.** The bounded staff-door / check-in slice demonstrates the requested visual language against the four actual spawn reference images. There is no blocking local visual defect and no required visual repair before this language is expanded. This is not full-room acceptance or a room rubric score.

## Evidence identity

- Native source: `production/checkpoints/slice-s10.blend`.
- Verified SHA-256: `f817b83c4d0bcf1dec88e6f3b7bf39ddc9100da66e74a1a1c5015ebbe52c5265`.
- All three slice render manifests identify that same hash and are complete. Their six image hashes were checked against the actual files.
- All **10 actual PNG images were opened individually with `view_image`**. No montage, prior verdict, author code or builder explanation supplied the visual judgment.
- Geometry and native source were not modified. Only this report and its companion JSON were written.

| Batch | Opened camera / view identifiers |
|---|---|
| `renders/slice-s10` | `SLICE_ENTRY`, `SLICE_MATERIAL`, `SLICE_DOOR` |
| `renders/slice-s10-uv` | `SLICE_ENTRY`, `SLICE_DOOR` |
| `renders/slice-s10-neutral` | `SLICE_MATERIAL` |
| `renders/spawn-reference` | `VALIDATE_Material_A`, `VALIDATE_LockerDoor`, `VALIDATE_Spawn`, `BRIEFING_INDIRECT` |

The slice images are 1067 × 600. The recorded perspective cameras are at 1.65 m height: `SLICE_ENTRY` 22 mm, `SLICE_MATERIAL` 32 mm and `SLICE_DOOR` 30 mm. Diagnostic renders use the corresponding scene-view camera matrices; the JSON records those identifiers and transforms.

## Visible findings

**Wall and staff door.** `SLICE_ENTRY` and `SLICE_DOOR` show a believable wall system: warm pale upper finish, navy lower protection zone, a trim break, substantial jamb/reveal depth and a thick counter opening. The orange door has distinct inset panel contours, hinges, lever/lock plate and a metal kickplate; the closer is also visible in entry. Construction communicates a door before the STAFF / 01 plate does. A blue junction housing, clipped conduit and clearance reader form a short purposeful utility route. Large adjacent wall areas remain quiet.

**Check-in hero and practical.** The illuminated public counter and bolted grille intercom lead `SLICE_ENTRY`. Transparent barrier panels, narrow upright posts and the darker office table behind them communicate a controlled service point rather than an arbitrary screen stack. The shielded practical beneath the sign exposes the counter opening and paperwork; the door side, lower wall and secondary room stay darker. Its light pool, falloff, and local contact shadows provide depth without hiding the hero construction.

**Material separation and wear.** `SLICE_MATERIAL`, `SLICE_DOOR` and neutral `SLICE_MATERIAL` separate the subdued granular wall finish, painted door, grey metal edge/lever, compact molded reader/intercom casings, dull rubber stamp mat, folded cloth and matte paper. The clear barrier has the strongest deliberate reflection. Wear stays localized: the stamp mat has use marks and the kickplate has contact scratches, while broad wall/paint planes remain maintained. The neutral diagnostic does not expose a shared generic satin-plastic response across the cluster. Both checker views show coherent scale on the visible principal wall, leaf, frame, opening and counter surfaces, without a dominant stretch or missing-face artifact.

**Human traces and institutional tone.** Five small purposeful groups are visible in the close counter view: the paper queue tray, folded muted-green cloth, form/clipboard, stamp and open ink pad on a worn working mat, and small tethered counter implement. They occupy a work surface with space between them. STATE YOUR NUMBER and the physical barrier make the institutional relationship coercive. WE VALUE YOUR TIME / ALL DELAYS ARE YOUR RESPONSIBILITY supplies the specified reassuring message with a punitive second meaning. These are a few concentrated functional labels, not a room covered in explanatory text.

**Comparison to the opened spawn references.** `VALIDATE_Material_A` establishes orange painted metal, folded cloth and modest personal/use traces. `VALIDATE_LockerDoor` establishes strong silhouette, dark framing, navy surroundings and controlled practical lighting. `VALIDATE_Spawn` establishes the quiet upper/lower wall grouping and specific industrial door construction. `BRIEFING_INDIRECT` establishes a warm focal light pool with darker secondary surfaces. The slice carries those craft and colour relationships through sharper manufactured door/intercom forms and a more austere public/office separation. Its subdued accent count and contained dressing preserve negative space. No dominant local generic low-poly, web-demo, repeated box-plus-bevel, uniform satin plastic, toy PPE, sci-fi greeble or photoreal-noise veto is visible.

## Scope of the pass

This is a **local visual pass for the style-validation slice only**. The scanner, broader inspection route, distant office/storage and other untouched room context appearing in the images are not approved by this verdict. Numerical clearances, true support contact, hidden UV coverage, native dependencies, reproducibility, cold-start equivalence and runtime behavior require separate evidence. No full-room category scores or full-room acceptance were invented.
