# Astra independent eng07 engineering follow-up

**Verdict: FAIL for eight new reactor-leaf seam intersections.** Camera near-field, selected outside-carriage clearance, mounted-body regression, nominal approaches and typed handoff checks pass within the bounds below. This is a CPU geometry review, with no art score or full visual-cycle credit. It does not change the separate full03 visual rejection.

## Exact authority and method

Fresh Blender 5.2 factory-startup CPU processes reopened `production/checkpoints/eng07/Fuel_Corridor.blend`: **7,744 objects**. No render, scene save, transform change, neighbor import or neighbor edit occurred. The final on-disk blend hash remained unchanged.

| Frozen item | SHA-256 |
|---|---|
| Fuel_Corridor.blend | `c0ddd75920fdc6cdd2415039bab88e12a79ff522d070ea40c4a5f1b7ca539579` |
| build.py | `f45e856a9b6eb0b7dd7b6067f8700c6e8e8660bc548aa9a841551c8d4844c0f3` |
| valorant_details.py | `7273687ad085d33b83fea62accc55b12e4722398c8c08dffcf0037cf605645b6` |
| interface.json | `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e` |
| build_manifest.json | `817ce0865c9ceeebac06f395ee33514fbea209bb0dc4a4085b9e7310b78200d7` |
| handoff.json, file bytes | `c76018aaf4fdbbf67ce5c5d2e6a060ea87a663c242e1f92a6b2216d181c0631a` |
| Canonically encoded saved handoff | `3302da51727983d0d87c7734aba83c7fbda729fa1bdf2e03b8b51db47ad64997` |

Saved scene provenance matches both source files and the interface. The handoff file matches the saved JSON and manifest. Interface bytes are unchanged from eng06. The independent probes do not import the checkpoint validator.

## Blocking leaf-fit finding

**Moderate severity — new solid seam strips penetrate the enlarged identity inserts and relocated middle ribs on both reactor leaves.** Evaluated triangle intersections establish these contacts; they are not only overlapping bounding boxes or micrometre rounding.

| Affected body | Other actual objects | Positive AABB overlap per pair | Pairs |
|---|---|---|---:|
| `REACTOR_BOUNDARY_leaf_identity_field` | `REACTOR_BOUNDARY_leaf_panel_seam`, `.001` | approximately 8 × 8 × 105 mm | 2 |
| `REACTOR_BOUNDARY_leaf_identity_field.001` | seam `.002`, `.003` | approximately 8 × 8 × 105 mm | 2 |
| `REACTOR_BOUNDARY_leaf_stiffener.001` | seam base, `.001` | approximately 8 × 7.5 × 55 mm | 2 |
| `REACTOR_BOUNDARY_leaf_stiffener.008` | seam `.002`, `.003` | approximately 8 × 7.5 × 55 mm | 2 |

The measured insert upper edge is 2.430000 m, while the seam strips begin at 2.325000 m. The relocated middle ribs occupy 2.452500–2.507500 m and cross those same strips. The insert and middle rib themselves retain **22.5 mm** vertical separation. Frozen eng06 source placed both the insert top and middle-rib top below the seam start; therefore these eight pairs are regressions introduced by the eng07 changes. The seam strips are physical dark-steel meshes, not flagged surface decals. Their penetration should be resolved as an actual fit issue. No replacement geometry is prescribed here.

The probe also records retained same-carriage overlaps at folded returns, orange strips, kick plates and gussets. Those are disclosed in the evidence rather than treated as a certificate that every older leaf joint is mechanically resolved. Normal bolt embedment, joined handle ends/rails and connected lower-rib corners are distinguished from the eight new seam crossings.

## Passing targeted evidence

- **58 selected reactor attachment parts:** all have the correct leaf carriage and presentation-cap flag; zero intersections with physical geometry outside their own carriage. The new service-pull backs and lower ribs meet their supporting leaf surfaces within about 2 micrometres. Pressed borders remain in contact; their fasteners embed about 3 mm into their own sheet and strike no outside body. These contact witnesses do not certify structural strength.
- **26 complete mounted groups against 6,729 evaluated physical meshes:** no new mounted-body clash. The eight reported spacer/wall overlaps are each 1.907 micrometres deep, consistent with numeric contact. The service-pipe junction is continuous; its centerline endpoint gap is 0.119 micrometres. No branch/station pipe intersection with tested architecture occurred. The plant and clean blade bodies, guide08 and relocated lights remain clear in the tested geometry.
- **Camera near-field:** an independent 17 × 17 frustum lattice for each of 16 saved cameras, **4,624 rays total**, found zero first hits within 0.12 m. D05's center ray reaches `FREIGHT_GATE_drive_access` at **1.149566 m**. Its sampled first hits include the motor, chain, roller, bearing and drive parts. The old eng06 D05 centerline, mathematically replayed through the retained eng07 gate region, hits `Tray_hanger_saddle` at **5.796968 mm**. This corroborates immediate obstruction at the previous pose; it is not a new render or complete proof of the black image's causes. Clear near-field does not establish useful exposure, framing or visual acceptance.
- **Approaches and seams:** the five retained nominal-opening lattices have zero blocked rays (32,056 total); the three branch walkups have zero blocked rays (12,645); plant/clean sign-region underpasses have zero blocked rays (5,670). Sampled floors remain continuous. Retained fixed portals are inboard. The separate shell probe found no F01/F02 masonry/shoulder overrun across the named seams. Closed presentation caps were filtered only for the specified operational opening checks; this is not proof of a stored open pose.
- **Cap and handoff integrity:** reactor cap inventory is **177 members, 89 left / 88 right**, including 40 new wear meshes, three identity marks, 12 added pull components and eight added lower stiffeners. F01 remains 104. All 12 carriage records, 34 typed markers and 7,348 collision entries are consistent; no missing/extra registry objects were found. All 43 new reactor surface decals remain attached to the correct removable cap/carriage.

## Evidence and limits

Local evidence: `astra-eng07-leaf-camera-evidence.json`, `astra-eng07-details-evidence.json`, `astra-eng07-branch-evidence.json`, `astra-eng07-branch-inventory.json`, and `astra-eng07-branch-shell-evidence.json`, with corresponding read-only probe scripts/logs in this directory. The branch/handoff probe was independently delegated to the existing refinery-source reviewer; the leaf, mounted-body and camera probes were run by Astra.

This audit is bounded to actual saved closed leaves, selected attachment/body fits, finite camera/approach samples, local seams and typed-data consistency. It does not rerun continuous gate travel, prove external open/storage states, certify a neighboring scene or engine controller, or judge unrendered eng07 materials, signs, floor graphics and door artwork. The eight new seam/body intersections prevent a clean leaf-fit pass despite the separate passing checks.
