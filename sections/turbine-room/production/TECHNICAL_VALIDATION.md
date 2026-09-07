# Technical validation

The authoritative check is `blender/validate.py`, run in a new, CPU-only Blender
process against the saved section blend. It does not change or save the scene,
render, use the shared GPU, or attach to a live Blender session.

From the repository root in PowerShell:

```powershell
$env:BLENDER_USER_RESOURCES=(Resolve-Path 'sections/turbine-room/.blender-user').Path
$env:PYTHONUTF8='1'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background 'sections/turbine-room/blender/turbine-room.blend' --python-exit-code 1 --python 'sections/turbine-room/blender/validate.py' -- --expect-revision REVISION
```

Reports are written to `production/validation/REVISION/technical.json` and
`technical.md`. The JSON includes measured gaps, angles, route intrusion objects,
scene/validator hashes, Blender version and actual counts. A failed or incomplete
report exits nonzero; `--no-fail-exit` is available for diagnostic orchestration
and does not change any report status. `--output PATH` selects a report path.

Checks cover camera count, external camera contract, camera pose/lens, render and
metric configuration, saved file path, private resources, materials and external
dependencies, evaluated mesh/curve/font geometry, finite vertices and transforms,
normals, zero-area polygons, exact coincident surfaces, topology warnings,
support contacts, declared assembly connections, unexpected floating components,
and local route/portal clearance volumes from `interface.json`.

Clearance checks clip evaluated triangles to the intended open volume. They also
check whether a closed solid encloses the volume without crossing its faces.
The volume starts 20 mm above finished floor to allow flush joints, paint and
thresholds; this is not a swept player or cart collision simulation. The slice
checks only its built Y range (17–24 m), with the entry-side route explicitly
unproven. Geometry faces use a 0.01 mm numeric inset, not a clearance allowance.

Support records in scene `support_registry` require `anchor`, `prop`, `target`,
`direction`, `max_gap`, `max_penetration`, and `angle_deg`. `prop` identifies the
visible contact mesh, curve or font, or the anchor can be parented to that object.
The validator checks both the anchor and actual evaluated supporting extrema.
It also samples the evaluated prop face nearest the anchor when its normal
faces the support, so an interior tabletop support can pass without requiring
a mesh vertex directly above the rail.
An anchor touching its target while detached from the prop fails. Self-targeting
props fail. Missing intent associations fail even when a legacy name-based
diagnostic can infer contact.

An optional `members` array lists separate assembly components supported through
the contact prop. Each named member must have an actual evaluated geometric
contact chain to the prop within the record's gap tolerance. A declared name
alone is not support evidence. Root props enumerated for this authored room,
and any object carrying `support_required=true`, require registry coverage.

The separate visible-component audit checks all rendered geometry for a contact
chain within 5 mm to the structural floor, walls or roof. It finds omissions such
as a detached tabletop prop or a disconnected fixture assembly. It uses triangle
intersection and vertex-to-surface proximity, so a reported disconnection must
be inspected in geometric context. Segment-to-segment distances across evaluated
triangle edges also detect coplanar overlaps whose vertices lie outside the
opposing faces. Analytic checks verify this case, a separated parallel case,
and triangle-versus-clearance-volume intersection. Contact does not certify mechanical stability,
fastening, load capacity, or acceptable interpenetration.

The validator intentionally does not award visual scores. A fresh-process read
is only the objective-check portion of cold-start validation. Mandatory renders,
same-camera pixel comparison, independent visual scores, runtime collision,
navigation and neighboring-module alignment remain separate evidence gates.

Full-build machine checks require scene `machine_contract` JSON:

```json
{
  "axis_point": [4.6, 0, 2],
  "axis_direction": [0, 1, 0],
  "mirror_normal": [1, 0, 0],
  "shaft_objects": [{"name": "EXACT_SHAFT_NAME", "local_axis": "Z"}],
  "centered_objects": ["EXACT_SYMMETRIC_CASING_NAME"],
  "mirror_pairs": [{"left": "EXACT_LEFT_NAME", "right": "EXACT_RIGHT_NAME"}],
  "symmetry_tolerance_m": 0.002
}
```

The names above are schema examples, not existing-object evidence. The builder
must name actual shaft and shell geometry, excluding intentional asymmetric
appendages from the median-plane symmetry set. The validator measures evaluated
vertex-set reflection errors, shaft geometry centres, and transformed shaft axes.
It compares the declared common axis to all three equipment axes in the interface.
Full mode also requires the interface's exact local portal and utility markers.
