# C87 view62: pool inlet diffuser construction (#85)

**Candidate:** `/workspace/scratch/reactor-refinement-cycle87/hall_final.blend`  
**Source SHA-256:** `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`  
**Image:** `/workspace/scratch/reactor-refinement-cycle87/parallel-720p/inspection/green/62/62_pool_inlet_diffuser_fit.png`  
**Image SHA-256:** `a56323539fe3ce1c8c5c4521ed43d7b962bfa93f23113b3b538676aab46242d2`

This is an exact-source 1280×720 Cycles CPU image at 96 maximum / 32 minimum samples, threshold 0.015, OIDN, path guiding, 12 bounces, and exposure 0. Its manifest is adjacent to the image.

The stainless shell now reads as a diffuser rather than a smooth cylinder with continuous rings. Multiple open side windows are visible around the body; the dark recessed core is distinct behind them. The upper feed pipe enters a separate collar above the slotted head, and the silhouette is sufficiently clear to judge the assembly at this view. I accept #85 for the visible construction of this over-rim pool inlet/diffuser.

The exact-source finite geometry probe [`diffuser-probe.json`](/workspace/scratch/reactor-refinement-cycle87/diffuser-probe.json), SHA-256 `5c3daf39172401d1c2fef5452b20bcd9d7c9de6cb92a71e1a21fa64d635ecdd4`, reports both new meshes closed, positive-volume and without degenerate faces or sampled liner intersections. These checks corroborate the fit; they are not exhaustive collision proof. This disposition is limited to this inlet assembly and does not close #90 through-wall routing or general pool penetrations.

