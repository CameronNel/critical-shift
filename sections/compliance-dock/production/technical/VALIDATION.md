# Static geometry validator

`blender/validate_dock.py` evaluates the **loaded, saved** Blender file. It performs CPU geometry queries without rendering, connecting to a live Blender process, saving the scene, or changing its pose. The JSON output identifies the exact `.blend` SHA-256, file/runtime Blender versions, revision, stage, actual bounds, source/evaluated polygon counts, cameras and measured support contacts.

Run from the repository root in a private section-local Blender resource directory:

```powershell
$env:BLENDER_USER_RESOURCES = Join-Path (Resolve-Path 'sections/compliance-dock').Path '.blender-validator-user'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' `
  --background --factory-startup `
  'sections/compliance-dock/blender/compliance_dock.blend' `
  --python-exit-code 1 `
  --python 'sections/compliance-dock/blender/validate_dock.py' -- `
  --expected-stage full `
  --output 'sections/compliance-dock/production/technical/full-validation.json'
```

For a slice, select `style_slice.blend`, use `--expected-stage slice`, and write `slice-validation.json`. Full-route checks are explicitly not applicable to a slice. `--interface` can override the default section `interface.json`. Keep `--python-exit-code 1`; the validator writes its report and raises on failure, but Blender only reliably propagates the failure when this option is present.

## Checks and metadata

- Every supported root must be an empty, have `support_class='supported_assembly'`, and appear exactly once in scene `contact_assemblies`. Every geometric component needs matching `assembly` metadata and actual parent ancestry; architectural objects must be explicitly classified.
- Child anchors have `contact_anchor=True`. Their world positions and the assembly's transformed local `support_direction` are tested against evaluated world-space target triangles. Signed gaps, penetrations, target normals, contact angle, first external hit and the nearest actual assembly surface are recorded for every anchor. An anchor that touches the wall but has no nearby component fails.
- Contact limits may be stricter than, but never exceed, 5 mm gap, 2 mm penetration and 12 degrees. The target search extends 250 mm each side of the anchor. Unsupported anchors and target misses fail.
- Geometry must have finite, invertible transforms and finite evaluated vertices. Material slots and polygon assignments, unresolved image resources, unassigned texture image nodes and linked libraries are checked. Original authorship is not proven by these checks.
- Duplicate candidates require the same world transform and evaluated local bounds. Coincident evaluated vertices/topology then fail unless **each** member has `allow_stacked_overlap=True` and a nonempty `duplicate_reason`. Precision is 0.1 micrometres for this comparison; geometrically similar but differently tessellated meshes are not certified unique.
- Slice cameras `S01_style` and `S02_material` must exist. Full stage additionally requires exactly ten other review cameras. Lens and clipping values are checked.
- Full clearance uses the dimensions and polylines in `interface.json`. It tests evaluated `circulation_solid=True` objects with world bounds, triangle/box separating-axis tests and closed-mesh containment. Substantial unlabelled architecture is conservatively included and reported as a warning: above the floor skin, at least 50 mm thick on every local bounds axis, and at least 0.015 m³ in bounding-box volume. This prevents an omitted ceiling or curb label from silently erasing an obstacle. Rectangular route segments include square joins. Ground is sampled every 0.5 m. Perimeter faces and portal widths are measured with rays; portal volumes include the authored wall depth. A 1 mm side/top numerical skin and a separate 20 mm floor/sill allowance are reported explicitly.
- Door/gate poses are never guessed or silently excluded. An object, or its ancestor, can declare `clearance_open_translation=[x,y,z]` in world coordinates, or `clearance_open_angle_deg` with `hinge_world=[x,y,z]` and `hinge_axis='X'/'Y'/'Z'`. A separate in-memory geometry representation receives this transform. Both saved-pose and declared-open-pose intersections are reported. Runtime actuation and swept door movement remain unverified.

## Interpretation

A static pass is not an engine collision certificate, navigation test, playtest, structural analysis, or proof that a loaded cart/body can negotiate a curved turn. The report records these limitations, the reliance on authored bulky-obstacle labels, and any stage checks that were not performed. The sealed exterior arrival portal is intentionally listed as unverified rather than measured as an open passage.

The initial headless run caught four genuine slice defects: three accessories targeted the desk substrate below its laminate, and one intercom anchor was detached from the casing. Those findings were returned to the builder for correction. The validator's core geometry routines also passed seven independent adversarial assertions covering a corner-only intrusion, disjoint and overhead triangles, a solid enclosing the whole clearance prism, and nonfinite diagnostic serialization. Each generated validation JSON applies only to its recorded scene hash and revision.

The corrected slice then passed with 24 measured anchors. A second private process rotated every scene root by 23° around Y and 29° around Z, then translated the scene by `(3.8, -1.3, 2.1)` metres without saving. All 24 contact outcomes remained unchanged; the largest measured difference was below 0.8 micrometres. Five additional in-memory fault injections were all detected: removed assembly registration, missing target, 30 mm gap, 10 mm penetration, and support direction exceeding the angle limit. These fixtures never saved or modified the delivered `.blend` file.
