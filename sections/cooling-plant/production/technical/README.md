# Cooling Plant measured validation

`blender/validate.py` reads the saved scene in a new headless CPU process. It never renders, changes geometry, saves the blend, contacts another Blender instance, or assigns visual scores. The JSON report is authoritative measured evidence; the Markdown companion is a short defect list.

Run from PowerShell, replacing the revision with the saved scene revision:

```powershell
$coolingSection = 'C:/Users/Camer/.codex/worktrees/ef37/critical-shift/sections/cooling-plant'
$env:BLENDER_USER_RESOURCES = Join-Path $coolingSection '.blender-user-validation'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 4 (Join-Path $coolingSection 'blender/cooling_plant.blend') --python (Join-Path $coolingSection 'blender/validate.py') -- --revision S02 --strict-exit
```

The report defaults to `production/technical/<saved-revision>-validation.json`. `--out` may select another `.json` path inside this technical directory. Omitting `--strict-exit` preserves the same honest report but does not fail the Blender command for measured defects. A successful Blender exit is never a validation PASS.

The validator distinguishes `slice` and `full` from the saved scene property. A passing slice cannot certify the full section. Current source hashes, saved-scene source hash, blend hash, interface hash and fixed cameras are recorded. A source mismatch is a failure requiring rebuild or an explicitly retained historical report. The scene is opened fresh, but no cold-start render comparison is implied.

Measurements include:

- Evaluated meshes, curves and text after modifiers, transformed into world metres. Keep-clear AABBs are only the broad phase; actual triangles are clipped to the open reserved volume, with solid-containment fallback.
- Outer section bounds, equipment bodies, route and portal volume collisions, and the required underside of utility crossings above the main route.
- Actual support-contact surfaces, signed gap, penetration and support-normal angle. Missing registration, target, anchor geometry or intended support are failures.
- Missing material assignments, external images and linked libraries; missing or changed fixed cameras and cameras inside geometry.
- Exactly coincident evaluated geometry to 10 microns, and actual curve endpoint/connection/socket coordinates.

Every exemption is enumerated. The expected floor and known flush dressing under 10 mm are excluded from route obstruction tests. The intentional D02 leaf is excluded only from its own swing reserve. The same leaf remains subject to portal and adjacent-route clearance. Cameras, lights and metadata empties have no collision geometry. Known architectural shell/trim and explicitly tagged `validation_role='architecture'` geometry do not need prop support registration; this designation must not be applied to independent furniture, fixtures or utility assemblies.

Support registration belongs on each independent assembly root, or on an independent mesh when no root is useful:

```python
root['support_target'] = 'Floor'             # real scene object name
root['support_anchors'] = [[x, y, z]]        # world metres, actual contact footprint
root['support_direction'] = [0, 0, -1]      # prop toward support
root['max_gap_m'] = .005
root['max_penetration_m'] = .002
root['support_angle_tolerance_deg'] = 12
```

Ceiling anchors typically point upward. Wall anchors point toward the relevant wall. An anchor at the centre of a ring's hole is invalid: use a location crossing its actual support footprint. The ray begins 80 mm toward the support from the anchor and searches 250 mm back into the prop. After finding the actual prop surface, a second ray toward the named support measures contact. Anchors do not prove contact by themselves. An entire registered root does not assert every internal component is connected; independent support-dependent props need their own registration, even when nested under a larger assembly.

Unparented renderable geometry outside the explicitly recognized architectural and flush categories is inventoried as unregistered. Assembly roots lacking registration fail. This hierarchy-based audit is explicit about its limits: it does not claim perfect semantic recognition of every component from names.

Equipment entries may declare `object_name` to identify the exact root. A real service component may carry `envelope_role='utility'`, or its exact name may be listed under an equipment entry's `utility_object_names`. That removes it only from the machine-body envelope; all circulation, portal and outer-shell checks still apply. Keep-clear entries may list `permitted_object_names` for a specifically authorized installed mechanism or support. This is an auditable contract permission, not a blanket exception for anything with a convenient name.

Utility sockets may declare `source_object` and `source_endpoint` (`start`, `end`, or `centre`). Start/end use actual curve spline source coordinates, not stored metadata. Centre uses the evaluated geometric bounds centre of a named socket/cap. A socket with no actual source mapping fails in the full scene. Explicit extra curve connections can be stored in `scene['pipe_connections_json']` as a JSON list of `{object, endpoint, target, target_endpoint}`. Targets support `start`, `end`, `centreline`, `surface`, or `solid`. Solid termination requires an actual endpoint inside or in contact with its declared flange/cap; decorative labels do not establish connection.

Degenerate evaluated triangles are informational: bevels and tessellation can create zero-area triangles, and their existence alone does not establish a visible flaw. Their counts remain visible. This validator does not certify arbitrary intersections, all manifold/normals cases, pressure-vessel engineering, hydraulic flow, game collision or runtime interaction.

Final acceptance remains outside this objective checker: independent scores of at least 90 in every required category, four genuine full review cycles, ten fixed-camera final renders, stable last two cycles and a fresh-process render comparison are mandatory. Missing evidence remains incomplete rather than becoming an invented PASS.
