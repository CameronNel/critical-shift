# Compliance dock s03 — independent local technical review

**Verdict: FAIL. Expansion remains blocked.** This verdict applies only to the front-office wall, D1, check-in counter, plaque, practical fixture and service junction. It is not a full-room rubric score, room acceptance, cold-render acceptance or runtime certification.

Reviewed native source: `sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend`, editable scene `COMPLIANCE_EDIT_LOCAL`, revision `s03`, source SHA-256 **`ebd89bcde2a460f53fcb53545df6a04b22af37d120365e9a0fa4faebcb9fa53e`**. Source hash matches all inspected s03 manifests and remains unchanged after fresh probes. Blender 5.2.2 LTS, build d13f752e3b9c. The root author owns all source changes; this critic wrote only the `critics/slice-s03-technical*` witnesses.

## Blocking defects and concrete repairs

1. **Coincident architectural front faces cause two black header patches.** Actual `slice-s03/SLICE_ENTRY.png` shows the black rectangles above the service junction and at the east end of the header. They persist in `slice-s03-uv/SLICE_ENTRY.png`, after the process replaces the surface material with an unbumped checker. Fresh evaluated ray probes at X=-4.6125 and X=-2.535, Z=2.7 return both the local full-height wall pier and `Office front head lintel` at Y=3.5199999809, with the same front-facing -Y normals. Mid-pier/lintel overlap spans X=-4.875 to -4.35000038; east-pier/lintel overlap spans X=-2.67000008 to -2.40000010. Both span Y=3.51999998–3.67999983 and Z=2.35000014–3.04999995. The shared volume is approximately 0.0588 m³ and 0.03024 m³ respectively. This is real duplicate surface construction, even though the meshes differ in size and the existing exact-duplicate check returns no duplicates. Remove the overlapping construction or its internal faces, preserving the combined outer wall envelope, door/hatch cutouts, floor datum and interface planes. A clean continuous wall mesh is also valid. Moving coincident faces apart would conceal the defect without resolving the construction.

2. **The speaking-glass cluster is suspended.** `Hatch speaking aperture plate` has its bottom at Z=1.22500002; the same-counter `Hatch security grille bottom` tops out at Z=1.05999994, a measured **165.0001 mm** separation. The counter itself tops out at Z=1.03999996, a **185.0001 mm** separation. New clamps contact the plate but their bottoms are Z=1.28499997, **225.0000 mm** above the base rail. In the neutral material image, the glass and grille visibly hang above the counter. The isolation pad supplies the grille-to-glass connection; it does not supply a glass-to-counter connection. Add grounded posts/stanchions and real clamp → post → base → counter contact, then measure that complete internal path. Parenting these parts to the inherited floor-supported counter root cannot substantiate their attachment.

3. **Three inherited small props float inside the polished counter cluster.** Against `CD | Counter linoleum inset` top Z=1.04200006, evaluated mesh distances give:

   | Prop | Bottom Z | Minimum vertical gap |
   | --- | ---: | ---: |
   | `Authority stamp rubber base` | 1.06199992 | 19.9999 mm |
   | `Ink pad tin base` | 1.05999994 | 17.9999 mm |
   | `Counter pen holder base` | 1.06100011 | 19.0001 mm |

   These exceed the protocol's 5 mm contact limit. The neutral image exposes the dark gaps under the stamp and ink-pad base. They are inherited pose issues, but they are inside the submitted polished slice and cannot pass by inheriting the counter's floor anchors. Repair the non-interface base construction to reach the tabletop while retaining inherited matrices and upper interfaces, and document each exception. Validate these tabletop contacts explicitly.

## UV and topology assessment

**Named UV coverage passes; a blanket nonstretch/metre-scale claim does not.** All 120 reviewed local meshes have the named `CD_Physical_1m` layer. Every source face and evaluated triangle has finite, nonzero UV area. The local `CD |` surface node graphs use that named UV map. Repeating overlaps/out-of-range coordinates are intentional tiled-material mapping, not a lightmap or atlas failure. Fonts and the conduit curve are separate geometry classes; their procedural shader response is not proof of a named mesh UV layer.

The actual entry and door checker images show consistent square density on the broad wall, door and countertop planes. Those cameras do not expose every cap or rear face. Analytical world-space Jacobians nevertheless inspect all evaluated triangles of the 120 meshes. Dominant-axis projection compresses sloped faces and bevel interpolation expands narrow strips. For example, a long face of `CD | Task folded shade` has UV/world singular values about **0.78489 and 1.00000**, hence about **21.5% compression** in one direction and **1.274 anisotropy**. The folded counter's diagonal section has values about **0.70711 and 1.00000**, hence **29.3% compression**. Common generated bevel strips reach approximately 1.93 anisotropy; very small transition triangles can be higher. These measurements are diagnostic, not an invented project tolerance or a visible catastrophic stretch claim. The documented universal “one UV unit per metre” statement needs correction or actual face-tangent metric mapping, including deliberate bevel/cap seams. Recheck the shade, fold, sidewalls and caps at useful distance after geometry repairs.

All 120 reviewed evaluated meshes are closed triangle manifolds in the existing validator, their recentered signed volumes are positive, and their raw shared-edge winding is coherent. The counter folded profile and new panels therefore have no observed winding reversal. Recentring the signed-volume calculation avoids numerical cancellation on tiny fasteners placed far from the origin. No exact duplicate evaluated mesh group is reported, but the confirmed partial wall overlap demonstrates the limit of that result.

The two counter gussets touch/intersect both the sill wall and worktop. The shade intersects its wall brackets and the frosted lens contacts the shade. The plaque, fixture and junction's external wall anchors pass. These findings establish geometry contact, not structural strength. The service lid/back has a 3 mm AABB separation; it is not treated as a new critical defect under the current 5 mm gap limit, but its hidden fastening construction remains simplified.

## Fresh static/source results

- Correctly invoked existing validator: **five applicable slice checks pass**, zero errors, zero warnings; **19 registered assemblies and 46 measured anchors**. Five full-room/runtime properties remain explicitly unverified. The validator itself states that ancestry/anchors do not establish every component load path.
- All **1,077 inherited objects exist**, all their world matrices match within 1e-6, and all inherited architectural dimensions match within 1e-5 m.
- The source's documented speaking-grille repair is the sole inherited non-architectural dimension change detected: original ring 0.20 × 0.20 × 0.02 m; new grille approximately 0.23 × 0.17 × 0.021 m. Counter slab footprint and top datum remain unchanged.
- All **five frozen input hashes** match `protected-inputs.json`: canonical map, selected dock module, accepted dock snapshot, interface contract and approved spawn module.
- All **25 loaded map/dependency libraries resolve**. The top map link and subordinate paths are relative; the local edited scene has no linked object/data ownership. Existing images resolve or are packed/generated, and fonts are built-in. Library datablock paths resolve relative to the current blend; image paths resolve in their owning library context. Do not double-apply a library parent to the already rebased library filepath.
- Actual source geometry has 1,177 objects and 321,268 evaluated authoring triangles. These are Blender counters. Full-room material-family/submesh targets and runtime performance are outside this local approval.

## Actual images opened

The s03 beauty manifest was `complete:true` with all three requested shots before this verdict. All s03 images are 1067 × 600, CPU Cycles, 24 samples, seed 8217, AgX Medium High Contrast, exposure 0.7. The diagnostic batches also report `complete:true`; they alter only process lighting/materials and do not save the source.

- `revamp/production/renders/slice-s03/SLICE_ENTRY.png`
- `revamp/production/renders/slice-s03/SLICE_MATERIAL.png`
- `revamp/production/renders/slice-s03/SLICE_DOOR.png`
- `revamp/production/renders/slice-s03-neutral/SLICE_MATERIAL.png`
- `revamp/production/renders/slice-s03-uv/SLICE_ENTRY.png`
- `revamp/production/renders/slice-s03-uv/SLICE_DOOR.png`
- `revamp/production/renders/spawn-reference/VALIDATE_Spawn.png`
- `revamp/production/renders/spawn-reference/VALIDATE_Material_A.png`
- `revamp/production/renders/spawn-reference/VALIDATE_LockerDoor.png`
- `revamp/production/renders/spawn-reference/BRIEFING_INDIRECT.png`

The four spawn images are the recorded unchanged-source reference capture, not a newly rendered spawn acceptance batch. They calibrate grounded construction/material separation and colour use. No room score is inferred from them.

## Probe commands and witnesses

Run from `/workspace/critical-shift`:

```sh
/workspace/tools/blender-5.2.2-linux-x64/blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s03-technical-probe.py

/workspace/tools/blender-5.2.2-linux-x64/blender --background --factory-startup --disable-autoexec sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/validate_dock.py -- --expected-stage slice --interface sections/facility-assembly/sources/compliance-dock/contracts/interface.json --output sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s03-technical-validator-corrected.json
```

Both completed successfully in fresh processes; stdout/stderr were redirected to the corresponding `slice-s03-technical-probe.log` and `slice-s03-technical-validator-corrected.log`. The probe independently cold-opens the selected baseline, records dimensions/poses, then cold-opens the s03 source, evaluates winding/UV/world-space contacts/coplanar rays and checks hashes. It never saves Blender data.

The first existing-validator command omitted `--interface .../contracts/interface.json`, so it failed with `missing_interface`; its report/log remain as `slice-s03-technical-validator.json` and `.log`. This was a critic invocation error, not a native geometry failure. A critic-only probe edit also initially failed syntax validation with `IndentationError`; the corrected fresh probe succeeded. Only the final corrected probe output supports the findings above.

Witnesses: `slice-s03-technical-probe.py`, `.json`, `.log`; `slice-s03-technical-validator-corrected.json`, `.log`; and the preserved initial validator report/log. Commands and measurements do not establish Unity import, collision, navigation, door sweep, structural engineering, full-room material approval, or final cold-render stability. The pixel batch used append-based process loading (`cold_open:false`); the fresh native probe proves source loading/dependency resolution, not cold-render equivalence.

**Required next gate:** repair the three confirmed local construction/contact blockers, resolve or qualify the UV metric claim, rerun the affected measured checks and all three fixed slice views, inspect neutral/checker evidence, and obtain fresh independent slice review. Keep full expansion blocked until that review passes.
