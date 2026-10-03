# Independent technical audit — R18

**Artifact inspected:** `production/checkpoints/R18.blend`\
**Revision:** R18; checkpoint, source, and validation SHA-256 `3a6584e744b4dc1628c46ec3abb1f8dfe6a87e4799fa138c70c1eb5ebb3d154e`\
**Formal validation:** PASS, 29 protected interfaces unchanged, world strength 0, no reported issues. This is a read-only geometry, material, and lighting audit; it is not a visual score or runtime certification.

## Remaining geometry issue

**Four floor-fracture groups are embedded in the raised repaired-screed patch.** R18 split and reseated the fracture sheets against worked-panel and slab bounds, but its `floors` set omits the actual six-vertex `RF1 | Swept floor repaired screed` patch. That evaluated face spans approximately `x=−4.28…−2.88 m`, `y=−2.47…−1.74 m` at `z=1.900 mm`. Independent point sampling against the actual floor top, including that patch and floor paint, finds fracture samples **0.68–1.88 mm below the patch face** in:

- `Hairline service-floor fracture 0.002`
- `Hairline service-floor fracture 0.003`
- `Hairline service-floor fracture 1`
- `Hairline service-floor fracture 1.001`

For example, fracture 0.003 is at `(−3.015, −2.370, 0.00002) m` while the evaluated repair-patch surface is at `z=0.00190 m`, a 1.88 mm penetration. At other samples in those strips the film is at the worked-panel level `z=0.00122 m`, still 0.68 mm below the repair. Include the repair face in the actual evaluated surface union when clipping/projecting the remaining film vertices.

The apparent 1.22 mm upward gaps from vertical rays on a few other samples are **not** equivalent defects: those samples fall exactly on worked-panel XY boundary edges. The nearest evaluated panel top is 20 µm away; the vertical ray misses because it grazes the edge. `Hairline service-floor fracture 2.001` similarly crosses the 11 mm bare-floor seam between two panel edges; the middle piece sits 20 µm over the base floor. I did not count those exact-edge ray misses as unsupported interior.

## R18 repairs independently verified

- Both hatch latch rust films are 29.6–30.0 µm off the evaluated hatch face with face-normal dot `+1.0`. All three north broken plaster lips are 20 µm off their target walls with face-normal dot `+1.0`. These close the four reversed-sheet findings from R17.
- The three PV corrosion runs remain conformed to the evaluated vessel: vertex clearances are 19.6–20.6 µm and face-to-shell normal dots are 1.00000, 1.00000, and 0.99972. The 16 north damp/mineral films, three larger spall patches, nook wall seep, and four floor seep films also remain seated at approximately 20 µm with aligned normals.
- Concrete wear is now isolated to `RF18_indoor_worn_concrete`, assigned to the interior `Floor` and `RF1 | Swept floor repaired screed`. `RF1_concrete` is back to the R15 base color and two ramp colors, and now has only the `MINE_external_sill` and `REACTOR_external_sill` as users. This removes the R17 exterior material spillover. Worked-panel `RF1_screed_0..3` and process/fabrication `RF1_epoxy` remain confined to indoor floor geometry; worn-traffic copies are used on floor paint, walkway borders, arrows, and stencils.
- Compared all 11 camera and 21 light object world matrices against R15: all 32 names/types match with no matrix differences at a `1e−9` tolerance. All lights remain bound to physical fixture lenses. The six expected failed fixtures have zero light energy and zero lens emission: PV hood 1; ceiling pendants 0, 3, and 5; wall service lamps 0 and 2. The remaining 15 lenses have unique paired materials at emission 1.8; small remaining emissions are only the sorter status slit and processor/emergency indicators. World strength is 0, with no exterior or hidden fill. Formal light checks report all five samples unblocked per source and a maximum lens-normal deviation of 1.27°.

## Limits

The formal support check accepts anchors with up to 5 mm gap and 2 mm penetration; it does not detect the pointwise crack penetration reported here. This audit does not certify exhaustive intersections, render quality, collision, or runtime behavior, and makes no visual rating.
