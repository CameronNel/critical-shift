# C82 door-hardware geometry review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`  
**Source SHA-256:** `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`  
**Disposition:** The bounded C82 geometry review passes for issue #124. Its current-C82 appearance acceptance is recorded separately in [`LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md`](LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md).

## Independent probe

The saved scene was opened with Blender 5.2.2. The probe independently evaluates the mesh surfaces at the actual 36 saved registrations and at the corresponding functional bearing samples, tests all thirty specified part-to-part joints, and checks edge incidence, triangle areas, and signed world-space volume for the six changed STEEL meshes.

- [Probe script](LUNA_C82_DOOR_GEOMETRY_PROBE.py)
- [Raw Blender log](LUNA_C82_DOOR_GEOMETRY_PROBE.log)
- [Machine-readable results](LUNA_C82_DOOR_GEOMETRY_PROBE_SUMMARY.json)

The first probe draft produced false negatives on hinge plates because I selected the hinge sample from the plate bounds. The seating module samples from the outer edge of the **leaf**. I corrected the independent probe to use that leaf-derived position and reran it against the same SHA; this report uses the corrected result.

## Bearing faces and joints

All 36 leaf-facing parts pass their actual rear-face ray checks: 12 latch stems, 18 hinge plates, and 6 kickplates. Their leaf-facing part surfaces are 0.498–0.501 mm into the formed leaf surface, and their measured rear-face normals point toward the leaf (dot product at least `0.9999999`). All registered anchors are within 1.35 μm of their respective component surfaces. The hinge check uses the measured leaf outer-edge sample and the kickplate check uses its center and four inset corners. This is a finite bearing check at the functional samples, not a proof of contact at every point of every face.

All 30 specified support joints have intersecting triangle pairs:

- 12 handle-stem-to-grip joins: 12–13 intersecting triangle pairs each.
- 18 hinge-barrel-to-plate joins: 18–20 intersecting triangle pairs each.

Nearest vertex/face-center samples can sit several millimetres from an intersecting joint because the contact occurs within triangle interiors; those distances are not treated as separation evidence when the BVH reports actual triangle intersections.

## Six changed STEEL meshes

Each mesh has 160 vertices, 296 edges, 150 polygons, and 292 Blender loop triangles, with seven connected solids. Every edge is shared by exactly two faces; there are no boundary, overused, or loose edges and no degenerate triangles at the `1e−12 m²` area threshold. Every connected solid has positive signed volume. Across all 42 solids the signed volumes range from `6.8054e−5 m³` to `7.373154e−3 m³`.

## Limits

The C82 package’s 14 authoring checks, separate control-room verifier, and declared scene delta pass. The geometry evidence above is limited to the six changed door-hardware meshes, their 36 leaf-facing parts, and the 30 specified joints. It does not prove appearance/readability by itself. The independent current-C82 pixel review in [`LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md`](LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md) provides the separate visual evidence for #124.
