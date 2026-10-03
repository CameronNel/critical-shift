# Independent technical audit — R17

**Artifact inspected:** saved `sources/refinery/module_overhaul_R1.blend` (read-only scratch copy)\
**Revision:** R17; SHA-256 `83e9cb20eba2cad911e359f7d064a99202f24d244bd2bc0a2662e41cec71d019`\
**Formal validation:** PASS, 418,686 visible evaluated triangles, no reported issues. This is a geometry and lighting audit; it is not a visual score or runtime certification.

## Findings requiring repair

1. **Two hatch rust films and two plaster lips face away from their support surfaces.** Pointwise nearest-surface checks show the two `Hatch latch rust bleed` sheets lie 29.6–30.0 µm off the evaluated hatch face, but their face normals have dot −1 against the hatch normal. `North broken plaster lip 1` and `North broken plaster lip 2` likewise sit 20 µm from their respective wall bays but have normal dot −1. Lip 0 and all three larger north spall patches face correctly (dot +1). Reverse the winding of the four affected single-face sheets.

2. **One floor fracture is buried across a slab/panel transition.** The 26 authored crack quads were sampled at vertices, edges and face centers against the union of actual floor tops. All are about 20 µm above the visible floor except `Hairline service-floor fracture 7.002`: samples across its transition into `RF1 | Worked floor panel.022` reach 0.58 mm below that panel's top. Its two endpoints are seated, but the intervening sheet bridges between the bare slab height and the raised panel height and is partly hidden by the panel. Split the line at the panel boundary or project intermediate samples to the local top surface.

3. **The floor discoloration shader changes exterior sill users through a shared material.** R17 adds the room-coordinate discoloration nodes directly to `RF1_concrete`. That material is assigned to `Floor` and the indoor `RF1 | Swept floor repaired screed`, but also `MINE_external_sill` and `REACTOR_external_sill`. Those exterior objects therefore receive the interior wear color mask as well. Copy/isolate the interior floor material before adding the wear shader so exterior sill appearance remains independent.

## Checks that passed

- R17's saved candidate matches `validation_R17.json` by SHA-256. The report records all 29 protected interfaces unchanged, world strength 0, and 21 practical lights.
- Compared all 11 camera and 21 light object world matrices against R15. All 32 names/types match with no matrix differences at 1e−9 tolerance. R17 keeps the original camera/light poses.
- All 21 lights are AREA sources bound to physical fixture lenses. The six intended outages remain correctly paired and dark in both source and lens shader: PV hood 1; ceiling pendants 0, 3, and 5; wall service lamps 0 and 2. Each has zero energy and zero lens emission. The remaining 15 fixture lenses each use a unique material with emission 1.8 and match a weak nonzero practical source. Formal aperture checks remain unblocked, with maximum lens-normal deviation 1.27°.
- Additional emission is limited to a sorter status slit (0.5) and the processor/emergency amber indicators (0.2). The retained task/warm-lamp emission materials have no object users. I found no external light or world fill.
- All 16 north-wall damp/mineral films corrected from R16 now sit approximately 20 µm off their assigned wall faces, with face normals aligned to the room-facing support normals (dot +1). The three larger spalled-paint sheets also align and sit 20 µm off their wall bays; only two narrow plaster lips have reversed winding as noted above.
- All three PV corrosion strips are now projected against the evaluated pressure-vessel mesh. Every vertex is 19.6–20.6 µm from the nearest shell point; face-to-shell normal dot is 1.00000, 1.00000, and 0.99972. This removes R16's millimeter-scale floating/penetrating points.
- The four service-seep floor patches, nook wall seep, and remaining floor fracture samples sit about 20 µm off their actual target surfaces with aligned normals. Floor `RF1_screed_0..3` materials are used only on worked floor panels; `RF1_epoxy` is confined to the indoor process/fabrication epoxy fields.
- The traffic-paint transparency materials are copies and are assigned to floor paint, walkway borders, floor arrows, and floor stencils. They do not replace materials on machines or signage elsewhere in the room.

## Limits

The R17 validator's support registry tests designated anchors with a 5 mm gap and 2 mm penetration allowance. The pointwise checks above are independent measurements of the declared surface films. The formal PASS does not flag the reversed open-sheet normals, the one cross-seam buried crack, or the shared exterior material use. This audit does not certify exhaustive intersections, render quality, collision, or runtime behavior; no visual rating is offered.
