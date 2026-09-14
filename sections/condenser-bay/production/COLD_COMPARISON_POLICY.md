# Cold and stability comparison policy

All comparisons require complete camera sets, identical saved-blend hash, renderer source hashes, camera transforms/lenses, resolution, sample count, render settings, backend/resource settings, and separate recorded Blender process IDs. Actual PNG hashes are checked against their render manifests. Copies do not count as fresh evidence.

Numerical equality is not assumed for Cycles GPU rendering and GPU denoising. The retained single R33 diagnostic C01 warm/cold pair measured mean channel difference0.019724/255, maximum13/255, and changed-pixel fraction0.056715. It is not a complete cold pass.

The GPU numerical screen permits mean channel difference at most0.10/255, maximum32/255, and at most0.001 of pixels with any channel difference above8/255. CPU historical comparisons retain mean0.01/255 and maximum2/255. These are disclosed render-variance screens; they do not replace independent visual inspection or the ten-category strict>90 art gate. Every raw per-image metric remains in the report. A failed screen returns a failing exit code for investigation.

The R34 policy is fixed before its full warm/cold review. Cross-round comparison uses the same policy and also requires the same blend, cameras, settings and renderer source. Independent Luna must inspect both complete sets and determine whether visible changes are acceptable render variance; a numerical PASS alone is not acceptance.
