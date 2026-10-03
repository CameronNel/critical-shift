# R05 Blender technical audit

**Scope:** Read-only audit of `checkpoints/R05.blend`, `build_R05.json`, `validation_R05.json`, the R05 builder revisions and the R05 validator. Blender 5.2 opened the checkpoint in background with `--disable-autoexec`; no scene, candidate or render was saved. Checkpoint SHA-256 is `bf14d5bb3a928bd98328dcc612af8fa961b472e5988b31c644f00bfdece425da` (11,941,090 bytes), matching both `build_R05.json` and the validation source hash. No runtime collision or performance certification was attempted.

## Remaining defect: inspection scanner cheeks float above the work surface

The two new root meshes `RF1 | Inspection tapered scanner cheek` and `.001` are not parented or registered in `support_registry`. Each has its four bottom vertices at **z=1.0650 m**. The measured top plane of `Inspection_work_surface` is **z=1.0425 m**. Downward raycasts from all eight bottom vertices hit that work surface with a **22.5 mm gap**, over four times the 5 mm support tolerance. No support registry entry names either cheek. The bridge and task lamp sit on this cheek pair, so the scanner assembly is left hovering over its bench.

The R05 validator reports PASS because it checks the 60 declared new support anchors but does not require contact records for these independent support-dependent roots. Lower the cheek bases to the measured worktop plane or add feet that contact it, then register and validate the support anchors. Include both cheeks in the rebuilt support report.

## R04 fixes confirmed

- I evaluated visible, newly authored meshes and computed signed volume for closed manifold meshes. **792 closed meshes** were evaluable; none had negative signed volume. The R04 ore-stone winding defect is repaired. The stored validator also reports all **790** meshes it classifies as closed PASS; the count difference comes from the independent evaluation method, and both checks found zero inverted meshes.
- All **24** selector and emergency-control decorations now have button-local centers at their authored offsets. Maximum measured center error is **1.31 μm** across the 18° tilted control heads. The inserted `view_layer.update()` before reading the decoration matrices repaired the prior 23–39.56 mm center error. Their parent links resolve to the corresponding buttons.
- All four inherited wheel contacts now resolve through the child `SUPPORT_CSM_Cart_wheel*_00` anchors. Their target rails are hit with a gap of **−0.000016 to −0.000009 mm** and **0°** normal deviation. The R05 validator records all 160 inherited support entries PASS, including these four.

## Independent support results

I reran the stored support-ray method directly against evaluated target geometry. All **60/60** new explicit support anchors pass; gap range is **−0.000054 to 4.2834 mm**, and maximum normal deviation is **7.50°**. All **160/160** inherited support entries pass; gap range is **−0.000061 to 2.4999 mm**, and maximum normal deviation is **0.020°**. These results confirm the wheel-anchor repair and the registered contacts; they do not clear the unregistered scanner cheeks described above.

The recorded R05 validation also reports 29 protected interfaces unchanged, world strength zero, no missing used images/libraries, no sampled aisle obstruction, and **273,452** evaluated triangles across **2,382** visible mesh objects. Those aisle samples are not a swept-volume clearance test.

## Practical-light source and fixture orientation

The scene contains **21 area lights** and no other light types. All 21 have named, present fixture-lens objects, sit inside the refinery bounds, and are within **5 mm** of a surface on their lens object. The world Background strength is **0**. There are no used external image or linked-library dependencies. The three nonzero-emission material families are used on practical diffuser lenses and status/emergency indicators, including the sorter scanner indicator; there is no world or ambient fill source.

I compared each area light's world-space emission axis (`local −Z`) with the outward normal of the nearest physical lens face. All 21 axes point into the outward hemisphere; none points back into its housing. Measured angles are:

| Fixture group | Count | Emission angle from lens normal |
|---|---:|---:|
| Ceiling pendants | 6 | 0° |
| Wall service lamps | 4 | 15.26° |
| PV task hoods | 2 | 38.42° and 41.62° |
| Inspection sample practical | 1 | 22.30° |
| Work nook, press, eyewash, threshold and personnel practicals | 6 | 1.27°–11.89° |
| Mine/fuel transfer bulkheads | 2 | 0° |

The two PV hood sources and inspection task source are noticeably oblique to their flat diffuser planes, but the nearest lens face remains on the emitting side and each source is close to its lens. This is not a back-facing or external-light defect. The R05 validator checks fixture proximity but does not check this angle; retain the measured angles for the rendered-pixel review.

## Disposition

R05 fixes the R04 winding, control-decoration and wheel-contact defects, and its light objects use in-room physical fixtures with world fill disabled. The inspection scanner cheek pair remains a measured unsupported cluster and is absent from the support registry despite the validator PASS. Repair and revalidate that contact before technical acceptance. This audit makes no visual score or art-acceptance claim.
