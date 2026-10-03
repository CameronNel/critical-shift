# Independent technical audit — R16

**Artifact inspected:** `production/checkpoints/R16.blend`\
**Source:** `sources/refinery/module_overhaul_R1.blend`\
**Revision:** R16; SHA-256 `e763bf27eb0e5d734090475bdefaf4f2a66b0b35ee43ec4a5a51556ec40e9aa7` (checkpoint and source hashes match)\
**Formal validation:** PASS, no reported issues. This is a geometry, pose, and lighting audit; it is not a visual score or runtime certification.

## Findings requiring repair

1. **North-wall stain sheets have reversed face normals.** The four damp plumes and twelve dried trickles lie at `y=6.37998 m`, about 20.26 µm in front of their designated wall targets at `y=6.38 m`; all sampled vertices ray-hit the intended wall bay at that same offset. The room-facing concrete surface normal is `−Y`, but all 16 stain faces point `+Y` (normal dot −1). Reverse the face winding so the exposed side agrees with the wall surface. Positions and registration are otherwise sound.

2. **PV corrosion films do not conform to the evaluated vessel surface.** The three open strips have outward-oriented faces (film-to-shell normal dots 0.99715–0.99997), but a nearest-surface query on every evaluated strip vertex shows substantially larger deviations than the nominal 20 µm offset:

   | Strip | Signed nearest-surface offset range | Largest deviation location |
   |---|---:|---|
   | Run 0 | −0.051 to +1.674 mm | +1.674 mm at `(0.789836, 4.374876, 1.150000)` |
   | Run 1 | +0.021 to +1.861 mm | +1.861 mm at `(1.194320, 4.341754, 1.082500)` |
   | Run 2 | −0.307 to +1.642 mm | −0.307 mm at `(0.415937, 4.779318, 1.347500)` |

   Positive values are clearance from the evaluated vessel shell; negative values are penetration. For the run 1 maximum, the nearest shell point is `(1.193885, 4.343563, 1.082500)`. These are open surface films rather than closed collision bodies, so their signed-volume values are not meaningful. The maximum clearance remains just under the generic 2 mm support allowance, but it is a real mismatch for a coating authored with a 20 µm nominal offset. Project each strip vertex to the evaluated shell and offset along its local outward normal before registering the support.

## Checks that passed

- Compared all 11 camera and 21 light object world matrices against R15: all 32 names/types matched and no pose matrix differed at a `1e−9` tolerance. Camera and light poses are unchanged.
- The saved scene has 29 protected interfaces and the validation report lists no protected changes. World strength is 0.0.
- All 21 lights are AREA lights bound to actual fixture lenses; all are inside the room. Their five aperture samples each are unblocked in the formal report, and the largest lens-normal alignment error is 1.27°.
- The expected failed set is correctly paired and dark in both the light object and unique lens shader: PV hood 1; ceiling pendants 0, 3, and 5; wall service lamps 0 and 2. Each has energy 0 and lens emission strength 0. The other 15 physical fixture lenses have emission strength 1.8 and match their weak, nonzero practical sources.
- The remaining non-lens emission is confined to the sorter status slit (`RF1_reader_status_glass`, strength 0.5) and physical amber state/emergency indicators (`RF1_status_amber`, strength 0.2). The two retained task/warm-lamp emission materials have no object users. I found no external light or world fill.
- The four service-seep floor films sit 20 µm above the respective evaluated epoxy tops; all tested vertices ray-hit their designated floor, with +Z sheet normals agreeing with the floor normal. They do not introduce raised obstacles.

## Limits

The formal PASS establishes the checks represented in `validation_R16.json`; it does not resolve the wall-normal or pointwise PV-conformance findings above. This audit does not certify exhaustive intersections, render quality, collision, or runtime behavior. The R16 formal render set was still in progress during this audit, so no visual rating is offered.
