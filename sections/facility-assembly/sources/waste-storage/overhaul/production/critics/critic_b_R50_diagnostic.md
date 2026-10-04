# Independent R50 targeted diagnostic

This is a partial diagnostic record, not a full-cycle score or acceptance report. R50 stopped at 20 of 21 required main views; therefore its images are not a scored cycle.

## Observed shell finish

The actual R50 C02 and D03 images show the new shell-coating exposure more clearly than R49. The added irregular substrate breaks the previously smooth broad shell read at normal camera size. In C02, SC01 has two adjacent exposed areas on its forward body that come close to reading as one blotchy patch, but I do not see a graphic perimeter or decal outline. W04 and the remaining actual partial views did not show a clear new finish defect. This is targeted evidence only; full art scoring remains for a complete cycle.

## Portal-light regression and diagnostic

In actual R50 W02, the bright pool on the left wall beside the receiving frame and the brighter jamb separation seen in actual R49 W02 are absent. The receiving portal consequently loses readable frame depth. Paired actual W01, W03, W05, W06, and W08 also show reduced portal, wall, or workstation illumination/readability, with the largest consequence in W01–W03 and W06. The R50 run retained the same camera poses and recorded scene/render settings, but these pixel differences are still visible and consequential; the incomplete run receives no score.

I individually opened the packaged diagnostic [R50_W02_no_lighttree.png](../diagnostics/R50_W02_no_lighttree.png) beside the actual R49 and R50 W02 renders. Its SHA-256 is `d1a62827d535c4e2fdd790bd8ad42cac041a916077266c2fd3fd31c6185ef3de`, matching the `image_sha256` in `sampling_diagnostic_R50.json`. The diagnostic image restores the left-wall light pool and readable receiving jamb to the R49 appearance. The recorded only changed setting is `s.cycles.use_light_tree=False` at 24 samples. This confirms a targeted sampling-method diagnostic for the visible regression; it does not prove a material cause, establish equivalence of sampling, or substitute for complete R51 paired and cold evidence. R51's recorded no-light-tree setting should be evaluated as a declared sampling-method change, with R49 as the last complete visual baseline.
