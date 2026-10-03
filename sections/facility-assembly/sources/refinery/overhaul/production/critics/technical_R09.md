# R09 Blender technical audit

**Scope:** Read-only audit of `checkpoints/R09.blend`, `build_R09.json`, `validation_R09.json`, and the R08/R09 revision sources needed to understand the rebuilt parts. Blender 5.2 opened the checkpoint in background with auto-execution disabled; I did not run the builder or validator and saved no source, checkpoint or render. Checkpoint SHA-256 is `c680b1f4cfa15f0ba044486f4412660141078549b3cb20934b4e8fa3cebd7037`, matching both records. No runtime collision or performance certification was attempted.

## R09 repairs confirmed

- The PV service ledge ribs now meet the actual worktop underside. The top is at **z=0.826 m** and both rib tops are also **z=0.826 m**. The revised support entries identify `Processor_service_ledge_top` as the source group, use the actual underside height, and resolve to the respective cantilevers at **0 mm**. The cantilever roots overlap the original PV05 plinth by **1 mm**.
- The filter access sheet now meets the cabinet front at **y=3.819 m**. Its face spans y=3.805–3.819 m against the cabinet face at y=3.819 m. The recessed pull is joined to the sheet by the two added mounting studs; all related new support records pass.
- Both PV diffuser panes now meet the undersides of their reflectors, have two folded edge retainers, and have support records to their reflectors. All four suspension stays are registered: the clamps meet the underside of `RF1 | I girder lower flange.002`, each stay meets the clamp and reflector, and each diffuser/retainer contact passes. The fixture axes remain aligned to their physical lenses at **0°**.
- The tag wire is now seated in both endpoints. Its support entries resolve into the spring clip with **0.5 mm** penetration and into the signed paper with **1.5 mm** penetration. The clip itself meets the hatch bridge dog with **1 mm** penetration. The wire, clip and paper follow the interactive `Processor_sealed_hatch` through parent transforms.
- The new `RF1 | PV formed instrument carrier` is a closed, 44-vertex / 42-face shell across the **−135° to −45°** sector of the vessel. Its inner radius is **0.6598 m**, measured **0.2 mm** inside the vessel's nominal 0.6600 m 40-sided surface; the support ray reports the same **−0.2 mm** seated fit. The carrier's angular samples match the vessel's 9° facets. Both radial rivets intersect the carrier geometry (12 BVH face-pair overlaps per rivet) at the two end positions. Its closed-mesh winding is positive. The ready-indicator bezel sits in front of the carrier face at y=4.316 m and remains exposed.
- The yoke Boolean stack warning is repaired for R09: the revision removes the plate bevel/weighted-normal modifiers before applying the Exact Boolean, then adds the bevel afterwards. The saved yokes retain concave vessel-matched seats on the original plinth. No live Boolean modifier remains in the saved geometry.

## Remaining defects

### Hatch lettering and approval mark are displaced by a parent-space transform

The tag paper remains at world z=1.292–1.442 m, and its clip and replacement wire sit at the hatch. However, `revision_R09.py` sets `.location.y` directly on `PV worker tag checked`, `PV worker tag shift`, and `PV tag approval ink` after these details have already been parented to `Processor_sealed_hatch`. In this state those coordinates are local to the rotated parent. Their evaluated world bounds are now z=**5.732–5.748 m**, approximately **4.29 m above the paper**, while their world y remains around 4.024 m. The text and ink no longer appear on the signed service tag. Set their desired world transform with `matrix_world` or transform the intended paper-face point into the hatch's local space before assigning `location`.

### Ear-cup ellipse is still wide horizontally

The four ear cups/pads have cylinder axis along world X, so the ellipse must be measured in world Y/Z. The saved ochre cups are approximately **186 mm wide in world Y** and **120 mm high in world Z**. The revision scales local X by 1.18 and leaves local Y at 0.76; in this rotated basis, local X controls world Y and local Y controls world Z. The cups remain wider horizontally than vertically. If the intended shape is vertically elongated, increase the local axis that maps to world Z and reduce the axis that maps to world Y, then inspect both cup pairs.

## Other stored and independent checks

I independently repeated the five-point, 150 mm emission-ray screen. All **105/105** area-light samples had no occluding hit except the inspection practical's center sample, which reached the intended `Inspection_sample_fuel_retention_band.001` at **81.20 mm**; the other four rays for that light clear. There are no buried or blocked emitters in this screen. All 21 lights remain in-room AREA lights with physical lens objects within 5 mm and lens-normal deviations no greater than **1.27°**. World Background strength is **0**.

The stored R09 validation is PASS: **141/141** new contacts, **133/133** inherited support entries and **918/918** closed authored meshes pass; the protected interfaces remain unchanged, with zero sampled route obstruction and no listed missing images/libraries. An independent evaluated signed-volume pass found **zero negative volumes among 921 closed authored meshes**; 15 open/nonmanifold meshes were excluded. The independent count differs from the stored count because the mesh-collection methods differ; neither found an inverted closed mesh.

The root/contact fixes for the ledge, filter sheet, fixture suspension, carrier and tag wire are verified. R09 still has the displaced hatch writing and horizontal ear-cup ellipse described above. This audit makes no visual-score or art-acceptance claim.
