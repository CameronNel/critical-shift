# Visual review and targeted repair

The [art direction](../../../../design/ART_DIRECTION.md),
[reference index](../../../../design/ART_REFERENCE_INDEX.md) and
[production protocol](../../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md)
remain the authority. This is a diagnostic aid, not a replacement scoring rubric.

## Preserve the successful workflow

Let the agent choose effective geometry and scene-construction methods. Do not
replace an approved result with generic procedural primitives to satisfy a recipe.
Choose extra inspections because of risk or observed defects, not because a model
has a particular name. Preserve small-edit autonomy without lowering formal gates.

For a bounded edit, compare affected fixed views and relevant numerical checks.
For new sections or substantial environment passes, use the full existing protocol:
prove the style slice first, use the mandatory gameplay-height views, complete the
required review cycles and cold-start checks, and meet the current thresholds.
An existing room is not automatically re-approved after a small local fix.

## Fixed-view evidence

Use the section's existing named evaluation cameras and CAMERAS.md. Cover the
changed geometry and its surrounding gameplay context. For major work, include
entry, route, hero interaction, reverse, pinch points and problem surfaces as the
canonical art direction requires. Add orthographic/front/side/top views when they
answer a specific shape or placement question; do not replace gameplay views with
a flattering turntable. Record a new baseline if a camera was genuinely invalid.

Keep camera transform, focal length, frame, lighting, resolution, render engine and
color management fixed for comparisons unless one of them is the correction target.
Record unavoidable setting changes; such pairs are not strictly comparable.
Render from the actual edited checkpoint and open the images with a vision tool.
File existence, script comments and object names are not pixel inspection.

Record each finding in the existing production state or critic report:

| View / region | Visible defect | Intended correction | Numerical check | Result |
| --- | --- | --- | --- | --- |
| Exact render filename and region | Specific observation | Geometry/material/light/camera change | Applicable measurement, or not applicable | Improved / unchanged / regressed / blocked |

Do not fill this table with imagined observations. Prioritize silhouette, proportion,
circulation and functional composition before surface detail. Change one causal
category at a time where practical. Recheck other affected views for regressions.

## Escalating diagnostics

Run only the diagnostics needed, in a disposable copy/process. Never save temporary
material overrides, hidden collections or diagnostic cameras over production assets.
Use the existing section tools where they provide the required view/check.

| Suspected problem | Useful evidence | What it does not prove |
| --- | --- | --- |
| Wrong silhouette or proportion | Flat/clay renders, orthographic views, measured bounds and landmarks | Matching a front view does not establish correct depth |
| Floating or penetrating props | Support anchors, gap/penetration measurements, close views | Contact shadows or an overlapping bounding box do not prove contact |
| Hidden intersections or seams | Opposing views, selective object/surface IDs, wireframe | Wireframe is not a complete self-intersection or manifold test |
| Normals/shading artifacts | Normal orientation checks, clay renders, topology inspection | Blanket smooth shading is not a repair for bad geometry |
| Material ambiguity or plastic look | Same-view beauty render under unchanged lighting | A clay/ID pass cannot validate final material response |
| Depth ordering confusion | Depth pass plus calibrated view and object IDs | Uncalibrated depth brightness is not a world-space distance |

Open/non-manifold meshes can be intentional for game assets. Nonuniform scale,
intersections and disconnected parts also need context; report issues against the
asset contract, not a universal zero-warning rule. Do not auto-apply modifiers,
recalculate all normals, merge vertices or delete geometry as a blanket repair.
For procedural/instanced objects, distinguish source geometry from evaluated
geometry; raw mesh counts do not establish rendered triangles or runtime draw calls.

## Reference-sensitive work

Read the approved reference and compare matching camera/projection where feasible.
Record measured proportions or explicit estimates, XYZ placement, anchors,
clearances and interface planes. Fix major forms before detail. Do not move the
camera merely to conceal a proportion error. A single reference leaves hidden
surfaces ambiguous; identify those assumptions instead of inventing precision.

Current Critical Shift art targets grounded stylized semi-realism, not generic
low-poly, uniform glossy plastic, decorative sci-fi clutter or AAA texture noise.
Use object-specific primary/secondary forms, believable construction, distinct
material families, localized wear, practical lighting and readable negative space.
The canonical art documents specify these choices; this skill introduces no new
palette, fixed dimensions, bevel widths, renderer settings or character proportions.

## Honest completion

Numerical checks and visual review are separate. Fix or report actual defects;
never invent favorable scores or certify images that were not opened. If the
budget or capabilities are exhausted, preserve the last good checkpoint and name
the remaining blocker. Do not drop acceptance criteria to finish the loop.
Use fresh-context critics where the current tooling permits, and label unavailable
independent review explicitly. An agent's own second pass is still self-review.
