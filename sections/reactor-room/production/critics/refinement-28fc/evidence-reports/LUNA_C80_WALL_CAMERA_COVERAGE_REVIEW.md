# C80 wall and mechanical camera coverage review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle80/hall_final.blend`  
**Source SHA-256:** `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`  
**Scope:** read-only saved-scene geometry/projection audit for issues #3, #112, and #124. No criterion is accepted from previews or projection probes alone.

## #3 — orange trim at transfer columns

`rh_walls.py` defines wall 4 as W4 from `(6,10.8)` to `(-6,10.8)`, with the door transfer column at local `u=6`, world `x=0`. The transfer column starts at lintel elevation `LINT=5.40 m`. In `column(w,u,kind)`, transfer-column `h0` is also `5.40 m`; its front flange spans wall-frame `v=0.30..0.35 m`. The orange edge strip is created at `v=0.35..0.352 m` and `z=max(2.1,h0)..WH-0.35`, which evaluates to `z=5.40..12.95 m` for this transfer column. Its lower edge therefore begins at the column/lintel junction and its back face touches the flange; it does not continue down through the unsupported space below the transfer member.

The correct visual route is full C80 main09, the north-fuel wall view. Views06 and19 are unrelated to the W4 transfer-column trim. The 480×270/16 main09 preview (`review-evidence/c80/main-diagnostics/09_walls_north_fuel.png`, SHA-256 `4f81017850367547aa2a64dbb715ab4ba9497b560663b84417b10568c28fd8a7`) includes the relevant columns, but cannot close attachment/readability at final quality. **Disposition remains pending main09.**

## #112 — wall-column splice plates

The actual wall-column splice bands in `rh_walls.py` are at `z=CZ+0.3=6.60 m` and `z=9.30 m` (transfer columns receive the upper splice only). These are the original wall columns, not the separate raised roof posts. The saved C80 mechanical cameras 51 and53 directly frame the lower and upper W4 jamb splice plates. Their full-quality 720 previews show each complete plate centered; the six bolt heads are visible but low-contrast at preview scale. The 51/53 full-quality queue is in progress. The broad roof view08 and running-gear view15 do not substitute for these wall-jamb plates. **Disposition remains pending full-quality51/53 pixels.**

## #124 — door operating hardware camera feasibility

An independent Blender 5.2.2 probe read the exact saved C80 door leaf and hardware bounds, placed temporary cameras, projected every vertex, and ray-sampled the mounted meshes. The volume-only LP haze object was hidden only in the temporary probe so it could not falsely count as an opaque blocker. It was not saved or altered in the candidate. Candidate viewpoints below place the full double leaf and its operating hardware inside the frame:

| Door assembly | Candidate camera → target | Lens | Projected hardware bounds (normalized image) | Nearest opaque scene surface to camera |
|---|---|---:|---|---:|
| FUEL HANDLING | `(0,7.8,2.5)` → `(0,14.36,2.5)` | 24 mm | Both leaves and hardware inside; NDC y `.060.. .909` | 3.13 m |
| MAIN ACCESS | `(-7.75,0,2.75)` → `(-14.36,0,2.75)` | 22 mm | Both leaves and hardware inside; NDC y `.059.. .913` | 2.84 m |
| COOLING PLANT | `(7.4,-7.4,2.5)` → `(10.917,-10.917,2.5)` | 18 mm | Both leaves and hardware inside; NDC y `.064.. .905` | 2.03 m |

All camera centers are clear of nearby mesh bounds. On the selected 160 hardware-vertex samples per leaf, 124 ray samples per leaf reach the geometry unobstructed; the remaining 36 are outer hinge/edge samples behind the matching `*.link wall` return. These are finite sampled projections, not final render evidence.

I also projected the C80 door meshes against the exact required wide-camera transforms (1280×720, 36 mm sensor, final18/20 mm lenses). Main09 includes the north FUEL HANDLING leaf, but sampled rays to its first leaf’s steel/hinge geometry are blocked by the fuel-receiving sign, service equipment, and adjacent concrete; only76/160 STEEL samples are clear and0/60 GALV-hinge samples are clear. On the other leaf124/160 STEEL and60/60 GALV samples are clear, though36/160 STEEL points lie behind the link-wall return. Main10 places both MAIN ACCESS leaves inside frame, but one leaf has only100/160 STEEL and40/60 GALV samples clear because of the west station and return; the other leaf has124/160 STEEL and60/60 GALV samples clear. Most decisively, the COOLING PLANT leaf/hardware has zero in-frame vertices in main09 and main10; it is also outside main01/main02. Thus the current wide views cannot, by themselves, cover all three door operating-hardware assemblies. Review current full09/10 pixels; a direct detail is needed for the Cooling Plant assembly unless another completed view clearly supplies it. The table gives safe measured direct-camera candidates without clipping the leaves. **Disposition remains pending useful current pixels.**

## Files and limits

- Exact candidate: `/workspace/scratch/reactor-refinement-cycle80/hall_final.blend`
- Camera probe source: `LUNA_C80_DOOR_HARDWARE_CAMERA_PROBE.py`
- Direct-door camera probe output: `LUNA_C80_DOOR_HARDWARE_CAMERA_PROBE.log`
- Exact-wide-camera projection probe: `LUNA_C80_MAIN_DOOR_PROJECTION_PROBE.py` and `.log`
- Mechanical ray/projection probes: `LUNA_C80_SPLICE_TROLLEY_RAY_PROBE.py` and `.log`
- Preview inputs are explicitly diagnostic and are not acceptance evidence.

This report addresses framing and saved geometry only. It neither asserts that a proposed macro has been rendered nor closes any row in the 140-item review.
