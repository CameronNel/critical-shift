# R13 Blender technical audit

**Scope:** Read-only inspection of `checkpoints/R13.blend`, `build_R13.json`, `validation_R13.json`, `revision_R13.py`, and the cold-start comparison. Blender 5.2 opened the checkpoint with auto-execution disabled. I ran temporary evaluated-geometry diagnostics from `/tmp`; I did not run the builder or validator or save the source/checkpoint. The checkpoint SHA-256 is `c7de88aaeb74cce93b6ce22362611ee248abb8e735fb0db1a614ea147dc987d1`, matching build and validation records. A cold original-source rebuild also reports PASS with 2,970 object, 42 material and scene-state fingerprints matching; pixel comparison is still pending. I visually inspected the available `CAM_HERO_DETAIL` render, but did not score the full 11-view set. No fluid behavior, hidden vessel internals, runtime collision or performance was evaluated.

## Hollow product line, hose and fitting passage

Both formerly capped curves are now evaluated closed MESH tube shells with annular ends, not center caps. `Processor_product_line` has an outer radius of **110 mm** and inner radius **96 mm**; `RF1 | Refined product interstage hose` has an outer radius **67 mm** and inner radius **52 mm**. Independent topology review found zero boundary edges and exactly two incident faces per edge on each mesh; signed volumes are positive (**0.007560 m³** and **0.002621 m³**). Center-axis rays through each mesh are clear.

The four fittings remain aligned annuli with the following measured minimum hose clearances in their axial slabs:

| Fitting | Bore radius | Maximum hose radius in slab | Clearance |
|---|---:|---:|---:|
| Processor product coupling | 68.5 mm | 67.0 mm | 1.50 mm |
| Dryer product inlet flange | 75.0 mm | 70.1 mm | 4.92 mm |
| Hex compression nut | 71.5 mm | 69.0 mm | 2.49 mm |
| Coupling neck sleeve | 68.5 mm | 67.4 mm | 1.13 mm |

Independent checks agree with R13 validation: each bore axis is open, with zero hose vertices buried in a fitting and zero hose/fitting surface-overlap pairs. The two formerly over-compressed bands now have measured inner radii **66.50 mm**; maximum hose radii are **67.001 mm** and **67.005 mm**, giving **0.501 mm** and **0.505 mm** radial squeeze. Their four directional support checks report **0.437–0.471 mm** penetration. This is a modest registered clamp fit inside the declared 2 mm bound, not the earlier 4 mm embedding.

The short reducer interface is centered on the original nozzle axis. `Processor_product_line` ends at (2.433, 4.898283, 1.438) m; the original annular nozzle throat radius is **117 mm**, so the 110 mm outer tube radius leaves **7 mm** radial clearance. The processor coupling begins at that endpoint and has a 68.5 mm bore. The hose begins at x=2.462 m, within the coupling's x=2.433–2.463 m span. Centerline rays through the line, coupling and hose each pass, with their open ends meeting through the reducer step. This confirms a visible external open-bore cue and hose/fitting clearance; it does not simulate flow, pressure, or unseen vessel internals.

## Riser feed and former grey wedge

The rising section of source `Processor_sorted_feed` remains a beveled CURVE, parented to `ROOT_PROCESSOR`, with 160 mm bevel radius (320 mm diameter). It now follows the screw-casing axis: x=**0.093336 m**, y=**4.984283 m**, from z=1.25 to 2.05 m. Those coordinates match the center of `Processor_screw_lift_casing`; the prior slanted 50 mm path no longer projects through the casing edge. In the R13 saved scene, camera rays through the former R12 grey-wedge pixels (130, 390) and (130, 430) now hit the enamel casing, while the prior R12 pixel rays hit the steel feed tube. The available R13 hero image is visually consistent: the exposed grey wedge is gone, with only the normal horizontal feed segment visible at the bottom. This check covers the visible casing interface, not the feed path inside the casing.

## Press and reader sheet returns

Both press-access-sheet side returns meet `RF1 | Press hydraulic cast base` at zero-gap support rays. Their bounds span z=0.322–0.659 m at y=0.777–0.790 m and 1.510–1.523 m. Both reader calibration-cover side returns meet `Sorter_calibration_access` at zero-gap anchors; each return spans the actual cover height minus the specified bottom relief. These are formed return meshes with registered contact, not visual outlines only.

## Glove and crusher service record

The moved source glove group is now on `Assembly_worktop`: palm bounds are x=6.314–6.399 m, y=0.590–0.710 m, z=1.000–1.028 m against the deck top at z=1.000 m. The inherited support anchor reports a **0 mm** gap. The adjacent component tray ends at y=0.535 m, leaving about **55 mm** clearance to the glove; the press pillar ends at x=6.262 m, about **43 mm** from the nearest glove bounds. This confirms support on the deck and clear placement beside the tray/pillar.

The signed crusher maintenance sheet is seated on the hinged door at y=4.180983–4.181783 m, z=1.735–1.945 m. Its clip overlaps the top edge of the sheet by about **0.4 mm** and has its own passing door support contact. Both new text marks ray-check to the paper surface at about **20 µm** separation. The stored target checks and world bounds put the header and signature within the paper face.

## Global constraints and count interpretation

R13 validation is PASS: **29 protected interfaces unchanged**, world strength **0**, 21 AREA lights, no missing images/libraries, 105 five-point light samples with no unintended obstruction, 167/167 new support contacts and 133/133 inherited support entries passing, and 943/943 closed-mesh winding checks positive. The count now includes visible curve and font geometry: **418,890 total** evaluated triangles, comprising **301,073 mesh** triangles and **117,817 curve/font** triangles. R12's 284,329 figure was native mesh-only, so it is not an apples-to-apples total; the expanded R13 count remains below the one-million authoring budget. This is not runtime performance certification.

The validator documents its bounded scope: four fitting axial rays and evaluated hose overlaps, two band sections, short reducer-axis rays, print centers, explicit/inherited support contacts and closed-mesh winding do not prove exhaustive self-intersection, buried volume, fluid simulation or runtime collision. Visual review was limited to the available hero image; other views remain unscored here.
