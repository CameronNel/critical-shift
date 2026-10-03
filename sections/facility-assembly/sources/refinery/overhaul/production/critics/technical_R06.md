# R06 Blender technical audit

**Scope:** Read-only inspection of `checkpoints/R06.blend`, `build_R06.json`, `validation_R06.json` and the R06 revision source. Blender 5.2 opened the checkpoint in background; no candidate scene was saved and the build or validator was not rerun. Checkpoint SHA-256 is `2694e8dbc851ee46fbaf17334a7fbd6ad2b4f21826d6f8b2c68f99f6bb20cd2a`, matching the build record and validator source hash. I did not certify runtime collision or performance.

## R06 repairs independently confirmed

- The inspection scanner cheeks now seat on their added pads. `Inspection_work_surface` top is at **z=1.0425 m**; both pad bottoms are at **z=1.0425 m**, and both cheek bottoms meet their pads at **z=1.0650 m**. The sample locator plinth also starts at the work surface top. The cheeks are now represented by support records, and all **79/79** new records in the stored validation pass.
- The control-head selector and emergency-button child transforms remain correct: all **24** decoration centers match their authored button-local offsets to at most **1.31 μm**. This confirms the earlier evaluated-matrix fix survived R06.
- Independent signed-volume checks on evaluated visible, newly authored closed meshes found **zero negative volumes** among 848 evaluable closed meshes; 12 open/nonmanifold meshes were not treated as signed-volume evidence. The stored validator reports **845/845** closed meshes PASS. This confirms the stone-winding correction within the limits of closed-mesh testing.
- All **157/157** inherited support entries in the stored report pass, including the four local wheel anchors; all **79/79** new explicit supports pass. Independent screen ranges are **−0.000061 to 4.2834 mm** for new supports and **−0.000061 to 2.4999 mm** for inherited supports. The validator reports no route obstructions.
- The four PV hood fixture axes now agree with their lens normals: **0°** and **0.02°**. All four wall-service fixture axes also agree at **0°**. The remaining measured lens-normal angles are within 12°: nook **11.89°**, press **3.01°**, eyewash **1.27°**, mine/fuel thresholds **5.78°**, personnel **2.55°**, inspection **0°**, mine/fuel bulkheads **0.03°/0°**, and ceiling pendants **0°/0.02°**. Every one of the 21 lights is an in-room AREA light, associated with a physical lens object and within 5 mm of that lens. World Background strength is **0**, and the stored report lists no missing images or libraries. These checks establish fixture association/orientation and internal light sources; they do not establish an unobstructed light path.

## Defects still needing repair

### Wall service emitters are inside their housings

I cast five scene rays from each area-light rectangle (center and four near-corners), starting 1 mm beyond the emitter plane along its emission direction. For **each of the four** `RF1 LIGHT | Wall service lamp N` lights, **3/5** rays hit the matching `ART_Wall_fixture` housing only **15 mm** from the source. For example, lamp 0's center ray and two corner rays hit `ART_Wall_fixture` at 0.015 m. The other two rays miss geometry. Thus the corrected 0° lens-normal angle is not enough: most of each emitted rectangle is aimed into the solid housing. Open the fixture at the lens or move/resize the actual emitter plane into the aperture, then recheck emitted-ray visibility. The current validator's proximity and angle tests do not detect this.

### Press task light is largely occluded by the press crown

The five-ray screen for `RF1 LIGHT | Press task bar` found **3/5** rays hitting `Assembly_crown` after **0.103–0.122 m**. The other two hit `Assembly_worktop` after 1.255 m. This means most of the sampled emitter area encounters the crown before reaching the task surface. Reposition the source beneath a real opening or change the emitting direction/aperture so the task bed has a clear path, then rerun the ray screen and inspect the task view.

### Thermal cover retention parts do not touch the cover

Nearest evaluated-surface checks find the `RF1 | Thermal removable insulation saddle` **25.0 mm** from the DR06 drum and **7.50 mm** from each of the four `RF1 | Thermal cover hold-down` blocks. Each hold-down is itself **about 6.66 mm** from the drum. The blocks therefore do not currently retain or contact the saddle, and the saddle has no explicit support record. If this is intended as an insulated cover assembly, add contact feet/bridges from the panel to the blocks and mounted feet from those blocks to the drum/support frame; declare the resulting support dependencies. If the air gap is intentional for thermal clearance, retain the clearance but provide visible structural mounts that close the support path.

## Other contact observations

The three new rejected-mineral fragments are seated in `Sorter_reject_bin_base`, with nearest distances of **0.008 mm**, **0.634 mm**, and **0.090 mm**. I found no evidence that these loose fragments float. The two hidden task fixtures now contact their supporting assemblies in the stored supports/geometry review; the inspection strip has a named cast mounting hinge. These checks do not establish hidden collision clearance.

The validator now tests declared supports and lens orientation effectively, but it still does not require every independent prop root to declare a support path or test emitted-light occlusion. Add geometry-level scene-ray visibility checks for area-light aperture samples and support/contact declarations for new mounted prop roots. No claim is made here about render quality, overall 99/100 art acceptance, or runtime performance.
