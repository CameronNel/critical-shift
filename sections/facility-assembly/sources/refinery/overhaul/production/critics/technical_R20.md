# Independent technical audit — R20 floor films

**Artifact inspected:** immutable `production/checkpoints/R20.blend`.\
**Revision:** R20; checkpoint SHA-256 `2e533ace75ea83e27952f1bceda75d2923803a1452627ba583e5aba486ec5e53`; the build and validation manifests reference this same source hash.\
**Formal validation:** PASS; 29 protected interfaces unchanged, world strength 0, no reported issues. This is a read-only geometric review, not a visual score or runtime certification.

## Floor-fracture seating independently verified

I rebuilt an upward-facing BVH from the evaluated floor geometry, including `Floor`, all 24 worked panels, both epoxy fields, all six maintenance seams, and the irregular `RF1 | Swept floor repaired screed` face. The R20 cracks are split along actual projected floor-face edges and conformed to the closest local surface. This includes the raised screed patch and slab seams; it does not use their bounding boxes as surrogate floor planes.

Across **27 fracture objects**, I sampled all 196 evaluated vertices, each polygon centroid, and quarter, midpoint, and three-quarter points along each polygon edge (833 total hit samples). Every sample is **19.99–20.01 µm above** the first upward-facing local floor face. No sample missed the floor union, fell below it, or rose more than the intentional 20 µm film offset. All 49 evaluated crack faces have world-space normal Z exactly `+1.0`; no face is inverted. The evaluated target names include the worked panels, repaired screed, base floor, and maintenance seams, confirming that fragments crossing between surfaces were split and seated per region.

This resolves the R18 issue: fragments formerly embedded by 0.68–1.88 mm in the 1.90 mm high repaired patch now sit 20 µm above that patch. The R18 ray misses at panel edges were edge precision cases; R20's explicit clipping and 5 µm inward micro-inset give the independent point probes a valid local target on both sides of shared edges. The 11 mm bare-floor seam remains on the base slab rather than being bridged at panel height.

## Scope and limits

The check measures film placement against evaluated geometry only. It does not certify render appearance, exhaustive scene intersections, or runtime behavior. The formal validation's support tolerance is much looser than this pointwise measurement; the evidence above is the independent local conformance check.
