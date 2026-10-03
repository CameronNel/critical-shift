# R12 Blender technical audit

**Scope:** Read-only inspection of `checkpoints/R12.blend`, `build_R12.json`, `validation_R12.json`, and `revision_R12.py`. Blender 5.2 opened the checkpoint with auto-execution disabled; temporary evaluated geometry diagnostics ran from `/tmp`. I did not run the builder or validator or save the source/checkpoint. The full render set was initially underway; a subsequent read-only follow-up inspected `CAM_HERO_DETAIL.png`. Checkpoint SHA-256 is `2cfad3e6757c1c265665bb70835a13b99457e5ec3d53ab4d56a1c120ef3bfa26`, matching the build and validation records. No runtime mechanism or fluid behavior was evaluated.

## Four annular fittings against the hose

The four replacement fitting meshes are actually hollow and aligned to the assembly. Each has an axial opening; centerline rays pass, there are no fitting/hose surface-overlap pairs, and no sampled hose mesh vertices lie inside a fitting. Independent measured radial clearance in each fitting's axial slab is:

| Fitting | Bore radius | Maximum hose radius in slab | Minimum measured radial clearance |
|---|---:|---:|---:|
| Processor product coupling | 68.5 mm | 67.0 mm | 1.50 mm |
| Dryer product inlet flange | 75.0 mm | 70.1 mm | 4.92 mm |
| Hex compression nut | 71.5 mm | 69.0 mm | 2.49 mm |
| Coupling neck sleeve | 68.5 mm | 67.4 mm | 1.13 mm |

These agree with all four stored `hose_fitting_checks` (clear axial ray, zero buried vertices, zero surface overlaps, PASS). The hose starts centered on the processor coupling axis and ends centered on the dryer flange axis. Support checks resolve the processor flange to the original nozzle flange, and the dryer flange to the dryer drum. Hose-to-neck support gap is **1.50 mm** (within the declared 5 mm maximum); neck-to-nut contact is **0.144 mm** penetration. The bounded evidence supports a clear external assembly passage through these four fittings; it is not a fluid simulation or proof of internal vessel geometry.

## Compression bands need less radial interference

The two bands now follow the evaluated hose spline, but their section remains major radius **69 mm** with **6 mm** tube thickness, so the ring bore radius is **63 mm**. The hose bevel radius is **67 mm**. This produces **4 mm radial interference** at each band. In evaluated geometry, **10 hose vertices** lie inside each band, **60 band vertices** lie inside the hose, and there are **142** and **144** world-space BVH surface-overlap pairs. The bands are positioned at their intended hose locations, but the penetration exceeds the generic 2 mm maximum used by the support checks; the validator does not include them in `hose_fitting_checks` or register them as support contacts. For a close compression fit, a 72.5 mm major radius with 6 mm section would give a 66.5 mm inner radius and about **0.5 mm** squeeze against the 67 mm hose.

## Processor outlet against the original nozzle

The original annular nozzle's measured inner radius is **117 mm**. The inherited `Processor_product_line` terminal remains a capped Bezier tube with a **110 mm** radius; its endpoint is at (2.433, 4.898283, 1.438) m, on the source nozzle axis with zero measured lateral offset. It ends about **0.55 mm** before the nozzle's outer X face. Thus the 110 mm terminal radius leaves **7 mm radial clearance** inside the original 117 mm throat, confirming the repaired axis/radius fit to the protected source nozzle.

There is a separate visible fitting-step question: the new processor coupling has a **68.5 mm** bore, substantially smaller than the 110 mm radius of the capped incoming line. The line ends at the coupling's first face (x≈2.433 m), rather than passing through its bore; the coupling's external hose bore is sized for the 67 mm hose. This may be an intentional reducer face, but the geometry does not show a continuous open path from the incoming line through that transition. The four passing fitting checks cover hose clearance only; they do not check `Processor_product_line`. If the external assembly is meant to read as a continuous open connection, represent the reducer with a visible transition opening and an annular line end. This is an assembly cue only; no unseen vessel interior or fluid simulation is implied.

## Timber polish and sharp sheet edges

Both working-edge polish pieces are now within the tabletop X bounds, beginning **10 mm** in from the short edge. Their y bounds are 1.5–4.5 mm inside the front edge; their z bounds are 2.5–11.5 mm below the top surface. They are not floating: independent mesh checks found four face-overlap pairs per piece and 6/8 polish vertices inside the tabletop. The nearest polish vertex is **0.71 mm** from the tabletop surface; the surface meshes also overlap at four face pairs. This is a slight partial embed at the timber edge, not a measured free gap, and has no explicit support record. Since these R12 renders were still in progress, I did not judge how much of the wood-on-wood detail is visible.

The selected folded-sheet parts retain a single-segment **1 mm** bevel: the crusher feed roof, press crown, optics bridge, hydraulic access cover, compact reader shell and front seal. Their bevel widths are clamped as intended; no broad rounded edge remained on these checked sheets.

## Hero-detail riser wedge follow-up

I inspected the pale triangular patch on the small left riser in R12 `CAM_HERO_DETAIL.png` and cast rays through its rendered pixels. This is an actual visible source object: pixels (130, 390) and (130, 430) hit **`Processor_sorted_feed`**, a source CURVE with material **`RF1_steel`**, at world points (0.07395, 4.80158, 1.53251) m and (0.08797, 4.78972, 1.42462) m. Adjacent orange pixels, including (130, 370), hit **`Processor_screw_lift_casing`** with `RF1_rolled_vessel_enamel`; lower dark pixels hit `Processor_feed_flange.001`. The grey wedge is therefore a projected view of the steel feed tube in front of the orange casing, not a cast shadow or the `ART_Processor_screw_lift_casing_surface_scuffs` overlay. The wedge pixels did not hit `Processor_screw_flight`.

`Processor_sorted_feed` is parented to `ROOT_PROCESSOR`, uses `RF1_steel`, and has a **160 mm** curve bevel radius (320 mm diameter). A nearest-vertex check puts it roughly **6.6–7.0 mm** from the casing; its object bounds overlap, so that sample is not an exact surface clearance certification. The unrelated screw flight sits near the casing crown: a mesh screen found 11 possible face-overlap pairs around z=2.196–2.215 m, while the casing top is z=2.210 m. That upper contact is separate from the lower rendered wedge and needs its own context if changed.

## Global constrained checks

R12 validation is PASS with **29 protected interfaces unchanged**, world strength **0**, 21 physical AREA light sources, no missing images/libraries, no route obstructions, **157/157** new contacts and **133/133** inherited support-screen entries passing. The five-point light ray screen covers **105 samples**; no sample is blocked except the intended inspection practical center ray to `Inspection_sample_fuel_retention_band.001` at 81.20 mm. Stored winding checks pass for **935** closed meshes. This remains bounded support, fitting, mark, light-ray and winding evidence; it is not exhaustive intersection, runtime collision/performance, or visual art acceptance.
