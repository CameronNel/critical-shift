# R15 Blender technical audit

**Scope:** Read-only audit of `checkpoints/R15.blend`, R15 build/validation/cold-start records and `revision_R15.py`. Blender 5.2 opened the immutable checkpoint with auto-execution disabled. Temporary evaluated-geometry and contact probes ran under `/tmp`; I did not edit or save the scene or author code. The checkpoint hash is `3741cbdf4c5fe04135bbddaa79565502149111b5a2085917e93922e52ab4cc3a`, matching R15 build and validation records.

## R14 repairs

The original sensor fastener mesh now ends at **y=4.394283 m**, exactly matching the replaced `Sorter_sensor_head` front bearing plane. In R14 it stopped at y=4.393283 m, leaving the measured 1 mm gap; R15's world-Y move closes it without visible overtravel. The fastener assembly is parented to the frame and remains in the same camera/light setup.

## Pale glove moved to deck shoulder

The rigid source glove group now has world bounds **x=5.3175–5.449, y=0.6385–0.848, z=1.000–1.028 m**. The actual `Assembly_worktop` top spans x=5.286664–6.526664, y=0.135–2.165 m at z=1.000 m. The glove clears the deck's west edge by **30.8 mm**; its palm support empty is parented to the palm and moved with the group to **(5.370, 0.730, 1.000) m**. The legacy support screen remains at effectively zero gap, and independent world bounds put the group on the tabletop plane. No glove child has sampled vertices below the deck plane.

The nearest assembly component-tray footprint is x=5.751664–6.401664, y=0.185–0.535 m: it is separated from the glove group in both x and y (at least **302.7 mm** and **103.5 mm** respectively). The glove group is also outside the press work envelope: it is at least **176 mm** left of the hydraulic base x-minimum, and the press console begins at y=1.095 m, **247 mm** beyond the glove's y-maximum. The cast press uprights are farther away. These are measured clear separations, not inferred from the support record alone.

## Wipe and caliper moved on inspection table

The wipe and caliper remain seated on the real inspection work surface after their common **(−0.670, −0.990, 0) m** translation. The folded wipe bounds are **x=5.510–5.770, y=−3.350…−3.090, z=1.0425–1.0585 m**; the tabletop spans x=5.131664–6.481664, y=−3.390…−1.370 m with top z=1.0425 m. The updated support anchor is (5.640, −3.220, 1.0425) m; an independent target ray hits the actual table with zero gap.

The moved caliper bounds remain assembled over the wipe: beam **x=5.550–5.702, y=−3.330…−3.120, z=1.0655–1.0715 m**; fixed jaw lower cheek **x=5.550–5.686, y=−3.330…−3.312, z=1.0585–1.0655 m**; slider **x=5.675–5.714, y=−3.261…−3.229, z=1.0585–1.0785 m**; moving jaw **x=5.550–5.675, y=−3.254…−3.236, z=1.0585–1.0715 m**. Independent rays confirm the wipe/table and jaw/wipe, beam/jaw and moving-jaw/slider support faces at zero gap. The two jaw contact faces are coplanar with the wipe's raised top at z=1.0585 m; I found no buried beam or blade vertices in the wipe.

The sleeve remains a genuinely hollow closed mesh (48 vertices, 56 faces, no boundary edges, signed volume **+0.00002113 m³**). Its rectangular bore is **17 × 7 mm** around the **16 × 6 mm** beam cross-section, leaving **0.5 mm per side**. A separate centerline ray along the sleeve's Y axis passes through with no hit; vertex-containment checks find no beam/sleeve burial. The nine engraved scale bars remain in position on the beam, and all 38 printed-surface checks pass.

The nearest work-surface obstacle is the south folded return: its evaluated bounds end at y=−3.363 m, leaving **13 mm** to the wipe. The outer tabletop edge is 40 mm away. The REPROCESS tray is the closest tray, at **38.4 mm** measured mesh distance from the wipe; the approved/rejected trays are farther. The original `Inspection_batch_record_board` clipboard bounds are x=5.834164–6.039164, y=−3.309…−3.051 m. Y overlaps the moved wipe, but their x bounds leave **64.2 mm** clearance. The separate batch ledger is 430 mm away in y. The worktop cabinet begins 20 mm beyond the wipe's x-maximum but ends at z=0.882 m, so it is vertically **160.5 mm** below the tool surface. The west rolled lip is 356 mm away in x. These are clear of the moved group; the 13 mm return clearance is the tightest measured margin.

## Scene constraints and reproducibility

R15 validation is PASS with no issues: **29 protected interfaces** unchanged, world strength **0**, 21 AREA fixtures, zero off-room lights, no unintended aperture obstruction, **201/201** new support contacts, **133/133** inherited support-screen contacts, **965/965** closed-mesh winding checks, and an empty route-obstruction list. Independent checkpoint comparison against R14 finds **all 11 camera world matrices and all 21 light transforms/settings identical**. Triangle count remains **420,822**, within the recorded authoring budget.

The R15 cold-start validator passes, and the independent rebuild matches all 2,989 object, 45 material and scene-state fingerprints. The eleven cold-start images are now pixel-identical to the checkpoint renders (maximum channel delta **0**). This establishes R15 reproducibility, not art acceptance. I inspected `CAM_ASSEMBLY`, `CAM_DISPATCH`, `CAM_MATERIAL`, `CAM_PINCH`, `CAM_HERO_DETAIL`, and `CAM_WORK_NOOK`. They do not make the moved glove or wipe/caliper details clearly legible at their current framing; I make no visibility claim for those props from these pixels. The new scene geometry and numerical seating pass, but close-up visual legibility remains for art review.

**Audit limits:** The checks above cover the specified moved groups, their table and part contacts, nearby measured footprints, original sensor fastener seating, protected interfaces and lighting. They are not exhaustive intersection analysis, runtime collision or performance certification, or final art acceptance. Within this bounded R15 change, I found no remaining physical placement blocker.
