# C89 view 04 pool circulation review

Candidate: C89, source SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`.

Reviewed the original full-quality 1280×720 image at `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/04/04_floor_pool_circulation.png`. Its image SHA-256 is `2a3ac3d2a793445e8134fc18bcdfbfe570c17d0c8b98c453ae1bc2c02765a27a`; manifest SHA-256 is `0a03204f7ca70f81ae03778b5b422ff91e5d2c35542a896481150009359f852a`. It rendered in Cycles at 96 maximum samples, 32 minimum samples, 16-bit, with the C89 frozen recipe. The small crops at `/tmp/c89-pool-gate.png`, `/tmp/c89-pool-rail_left.png`, and `/tmp/c89-pool-depth.png` were used only to inspect portions of that original image; they are not independent render evidence.

## Accepted from this frame

**#87, pool depth marking contrast.** The `1M` and `3M` markings are both visible on the inner green lining and distinguishable from the surrounding tiles at the original 720p scale. The text is restrained in size, but it remains legible in the full-resolution frame; neither marking is obscured by the cage, rail, reflections, or grout lines. This closes the contrast/readability criterion in the normal-state scene. It does not claim water-state comparison or close the separate water-plane item #88.

**#68, route continuity, remains accepted from the previously documented combined evidence.** View04 shows circulation markings around the pool. This frame adds route-context evidence; the existing #68 report and exact floor-guidance audit remain the basis for the accepted scope.

## Reviewed but still pending

- **#74 floor movement/wear pattern:** paint chipping is visible, but the image does not show a convincing traffic or movement wear path across the floor. Keep the dedicated wear evidence open.
- **#80 rail post terminations:** the posts meet the circular rails, but the ends/caps and attachment details are too small in this wide view to judge.
- **#82 rail intersection joints:** the rail path is visible, but the gate/intersection joins are not resolved enough to verify their construction.
- **#83 pool gate construction:** the far-side gate is visible as a framed, barred assembly. Its hinge, latch, and usable opening are too small to verify here.
- **#84 pool lining joint depth:** the liner grid is visible, but this view does not establish the physical depth of the joints.
- **#86 pool wall staining origins:** no stain is clear enough in this view to trace to a specific liner joint or service port.
- **#88 water plane/depth readability:** the normal-state water is visibly transmissive, and the lined shaft reads as deep. This single state does not establish the required comparison across operating states.
- **#61 wet/oil/dirt separation:** the broad floor shows a dark wet patch, but it does not resolve the dedicated oil/wet material distinction.

No geometry or source issue was found in this view that warrants a C90 change. Retain the appropriate dedicated close-ups/state frames for the pending criteria above.

## Saved-geometry check for #82

Correction: the first local probe used nominal coordinates `(3.6349798, 0.0121118)` and selected a nearby rail/cap neighborhood, not the post body. That result is retained as superseded evidence at [old script](evidence/C89_RAIL_UPPER_JUNCTION_PROBE_SUPERSEDED.py) (SHA-256 `9bf5248fa96daf601545a2984d6a4ca2dc5705c112a8cf19c0357941d9c2f9bf`) and [old JSON](evidence/C89_RAIL_UPPER_JUNCTION_PROBE_SUPERSEDED.json) (SHA-256 `305a95ffb90498ca95c9d084e5139e0aa73b67f12e9c74ec27283d1df4e2ddd1`). Do not use its selected-vertex counts as evidence about the post.

A corrected read-only Blender probe loads the exact C89 scene and splits the saved `RH pool rail YELLOW` mesh by actual edge connectivity. It identifies the east-side vertical post component at center `(3.634330153, -0.069782706) m`, with bounds x `3.608931541–3.659728765 m`, y `-0.095181249–-0.044384163 m`, and z `0.215000004–1.309999943 m`. That component has 24 vertices and 26 faces with no boundary or nonmanifold edges. A separate nearby cap component occupies z `1.309999943–1.317999959 m`; it also has 24 vertices and 26 faces with no boundary or nonmanifold edges. The whole merged yellow guard object has 3,482 vertices, 3,394 faces, and 95 edge-connected components. The source builds the round top and middle rails as continuous sweeps through the uprights. These saved-mesh facts support a plausible capped through-rail/post construction; they do not prove a visible weld seam or a separate sleeve/collar. The C89 full04 image still does not resolve the joint seam well enough for the original close-up criterion, so #82 remains pending visual evidence.

Corrected probe and output, both bound to `candidate_sha256` `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`: [component probe](evidence/C89_RAIL_POST_COMPONENT_PROBE.py), SHA-256 `d7e4a25996d1aca5819006d3ccb32980c3234c6e4843d37470c829d34452081f`; [JSON result](evidence/C89_RAIL_POST_COMPONENT_PROBE.json), SHA-256 `090205ae9f27348594ba054e74c2c1949d4129aa35ce49e0c189c5bcb63ac849`.
