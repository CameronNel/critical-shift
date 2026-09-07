# Electrical Room technical validation

The authoritative check is `blender/validate_scene.py`, run in a fresh, background Blender process against a saved file. It never builds, renders, saves changes to the scene, requests a GPU, or touches another Blender session. A JSON report is written before a failing check raises an exception. Use Blender's `--python-exit-code 2` option and treat every nonzero exit as failure.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' `
  --background --factory-startup 'sections/electrical-room/blender/electrical_slice.blend' `
  --python-exit-code 2 --python 'sections/electrical-room/blender/validate_scene.py' -- `
  --out 'sections/electrical-room/production/checkpoints/S03/validation.json'
```

Use `electrical_room.blend` for the full room and include `--require-current-source` for final acceptance. The stage normally comes from the saved scene; `--stage full` can deliberately audit a file against the full contract. A slice PASS applies to its 11.00 × 7.20 m partial hall and its validation cameras only. It cannot accept the 16.40 m full room. `--camera-baseline <prior-build-or-render-manifest.json>` additionally rejects changes to previously recorded camera positions, rotations and focal lengths. Full validation requires the agreed ten named C01–C10 views; slice validation requires S01 and S02 and allows supplemental coverage views.

## What is measured

- Scene identity, metre scale, saved-file existence, exact build-source fingerprint, render dimensions and camera integrity.
- Modifier-evaluated world-space geometry, finite coordinates, applied scales, positive transforms, material slots, polygon areas, closed-mesh signed volume, nonmanifold edges and hidden geometry. Open text, open tubes and surface decals remain an explicit warning inventory rather than an automatic failure.
- Missing linked libraries, file images, UDIM tiles, fonts and material output nodes. Packed assets and Blender built-ins do not require external files.
- Actual floor, ceiling and wall bounds against the architecture contract. Full validation adds ray measurements of the east wall and reserve-bay perimeter, floor and ceiling, plus interface marker positions.
- Named main passage and door-aperture AABB exclusion volumes. Full validation also checks the reserve branch and P03. The volume begins 25 mm above the floor to exclude deliberate flush thresholds, slab joints and thin floor finishes; it is 2.70 m high. Actual utility geometry crossing the main route must have an underside at least 3.50 m high.
- Physical support contact and actual geometry at each declared support anchor. The target is queried with an evaluated world-space BVH. Every sample reports its measured gap, normal, angle, contact object and contact position.
- Exact coincident geometry, independent of object names and vertex ordering. Separate geometry with the same world vertex multiset always fails, including duplicates inside an assembly.
- Cross-assembly triangle-surface crossings after conservative AABB filtering. The report distinguishes structural joins, internal assembly construction, nested assemblies, a finite named construction-joint table and explicit exact-object intersection declarations. Unknown crossings fail. The report exposes all named/declarative exceptions and their overlap measurements.

## Support authoring contract

Every physical mesh, curve and text object must have `assembly_member` equal to its nearest declared assembly-root ancestor. A support root has `assembly_root = True`, an existing mesh/curve object name in `support_target`, a JSON array of local XYZ `support_anchors`, and a JSON local XYZ `support_direction` pointing toward its support. Directions are transformed with the root. Legacy Floor/Ceiling roots may omit the direction; other target names may not.

The standard gates are a maximum 5 mm positive gap, 2 mm penetration and 12° support-angle deviation. These tolerances cannot be relaxed through object metadata. A declared anchor also needs a real directly owned component surface within 5 mm, with its physical contact checked separately. Dummy centre anchors between ceiling rods therefore fail even when the anchor itself lies on the ceiling. A numerical fallback permits a nearest surface only within 10 micrometres laterally of the ray; ordinary gap and angle gates still apply. This handles floating-point rounding at a shared floor edge.

Solid components need a contact face pointing toward their support. Open sheets whose actual thinnest world extent is at most 10 micrometres may present either face orientation; the target surface must still oppose the support direction. Every vertex of these planar sheets is checked, so one supported scuff cannot conceal another floating member in the same decal assembly.

Separate loose items on carts, shelves and benches should be nested support roots targeting the actual tray or shelf. Their internal geometry remains editable and registered to that nested root. The cart's floor anchors do not validate an elevated multimeter, fuse, work order or cloth.

Only explicitly recognized fixed construction names in the Architecture collection can use `assembly_member = 'fixed-architecture'` without a support root. Putting loose dressing in that collection or assigning that string does not grant an exemption. New construction names need a reviewed validator update.

An intentional cross-assembly engineering join may use `allowed_intersections` as a JSON array of exact object names on one of the involved objects. Use this only for a real reviewed connection. It is reported, never used to suppress duplicate detection, and does not waive support or route checks.

## Limits and outstanding evidence

A geometry PASS is not visual acceptance, collision certification, electrical-installation certification, a navigation test or proof of neighboring module alignment. AABB clearance is conservative and does not simulate body sway, two carriers or cabinet animation. Triangle-surface crossings can miss a solid fully contained inside another solid. Same-assembly intersections are classified construction, not proven collision-free; unrelated internal props need individual support declarations. Full acceptance still requires the independent pixel reviews, fixed-camera regression evidence, four complete review cycles and final fresh-process reproduction required by the production protocol.

The initial technical source audit identified dummy light/bus support anchors, floating cart contents, sliding leaves parked inside wall slabs, and bevel-generated degenerate instrument dial faces. The builder owns geometry corrections. Reports retain saved, current and checkpoint source fingerprints. Historical audits can verify the matching revision's checkpoint source when the current script has moved on, and emit a warning that this does not prove reproduction by the current script. Final `--require-current-source` audits fail unless the current script matches the saved build fingerprint.

## Execution evidence

Initial background validation completed and wrote `checkpoints/S01/validation-initial.json`. It reported a source-fingerprint mismatch while the builder was editing, degenerate dial faces, the doorway's numerical edge-contact case and previously unclassified named construction joins. The numerical edge case and finite construction classifications were subsequently addressed in the validator. Initial S01/S03 failure reports remain historical evidence.

**S04 partial geometry PASS:** `checkpoints/S04/validation.json` was produced by a fresh Blender 5.2 background process and measures 452 evaluated geometry objects, 16 support roots and 33 anchors. The S04 checkpoint script matched the saved build hash; the current script had already moved on, which the report flags as a warning. Camera transforms/focal lengths matched the S03 build manifest. All error gates passed; intentional open surface geometry remains a warning inventory. This is technical slice evidence only, not final current-source reproduction.

**Validator fault detection PASS:** `checkpoints/S04/validator-selftest.json` records nine deliberately injected, unsaved faults against the passing S04 scene: a dummy anchor between fixture rods, a 20 mm floor gap, 10 mm penetration, an incorrect support direction, a nonexistent support target, exact duplicate geometry inside an assembly, unregistered loose geometry, a prop inside the main route and inverted closed-mesh normals. Each test asserted the failure for the specific changed root/object. The dummy anchor was measured 134.9998 mm from real geometry. Baseline checks and restored-scene checks passed. No test saved a modified .blend. The earlier S03 category-only probe report is explicitly marked insufficient and is superseded by these isolated assertions.
