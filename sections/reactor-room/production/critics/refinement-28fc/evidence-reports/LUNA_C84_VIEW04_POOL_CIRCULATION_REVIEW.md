# C84 full view04 pool and floor review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Candidate SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`  
**View04:** `/workspace/scratch/reactor-refinement-cycle84/parallel-720p/main/green/04/04_floor_pool_circulation.png`  
**View04 SHA-256:** `a1342ba56482fa577d1040831f67b622162ebd627da187ba74528621eb9db641` (1280×720, 96 samples)  
**Companion view03:** `/workspace/scratch/reactor-refinement-cycle84/parallel-720p/main/green/03/03_floor_access_lane.png`  
**View03 SHA-256:** `d37f0ba794c131d8122c318205881431842c3a1515b99ac526e343175b74ce70` (1280×720, 96 samples)  
**Exact C84 support audit:** `/workspace/scratch/reactor-refinement-cycle84/audit.json` (SHA-256 `ccc6ca6a26dff44537faecff9dc3742d37a78c8fadad19c762e053161d5d98e6`)  
**Floor guidance audit:** `/workspace/scratch/reactor-refinement-cycle84/floor-guidance.json` (SHA-256 `d20ee9b35828d2f85acc77542d3949133a106d5022a4d823179c0626c03005b5`)

## Accepted from exact C84 pixels and scoped saved geometry

- **#68 — Route marking continuity.** View03 proves local painted arrows and runoff route; the broad high-angle view04 shows the aisle markings and the continuous pool perimeter path across the scene. The C84 floor-guidance audit separately reports no cone footprint overlap with the white arrow or yellow route paint. The route reads as connected and unobstructed at normal viewing scale.
- **#54 — Bollard floor mounting.** Views01 and04 show flared base plates meeting the slab on representative bollards. The exact C84 support audit records 104 floor-seat anchors across all 26 bollards, with zero failed records. This is finite registered contact evidence, not an exhaustive all-pair test.
- **#55 — Bollard cap and finish.** Both views show the high-visibility yellow cap/body treatment and contrasting black hazard band on multiple bollards; the materials remain distinguishable at 720p.
- **#70 — Circular cover seating.** Both actual manholes are in frame, with their round covers visually set within their square surrounds. The exact C84 support audit records four frame seats and four cover-to-frame seats at each position: centers `(-6.2, -1.9)` and `(7.2, 4.4)`. The recorded contact gaps are within about 2.3 nanometres of zero; no cover appears raised or floating in the image.
- **#75 — Floor visual noise.** The floor is busy, as an operating service area should be, but the props cluster around work zones and the circulation lanes remain readable. Concrete aggregate is restrained; no floor texture or marking pattern overwhelms the slab joints, route, drain, or pool.
- **#76 — Pool rim layer consolidation.** The full view has a distinct curb, drain/grate band, outer yellow safety-circle paint, guardrail, and inner lining. Those layers read as separate functional parts. The redundant high-frequency outer tick ring is absent; the yellow marking does not collapse into a dense stack.
- **#77 — Pool rim thickness hierarchy.** At 720p, the curb and grated channel have real visible width; the rail sits above them and the darker lining begins inside the rim. No important edge collapses into a single dark stripe.
- **#79 — Pool rim neutral material readability.** Grey concrete, dark grating/metal, and yellow painted steel separate cleanly. The green pool lighting stays inside the pool and does not turn the outside coping green.
- **#81 — Rail base attachment.** View04 shows posts landing on the rim rather than floating beside it. The exact C84 audit records 88 rail-foot anchors with near-zero contact gaps; this is finite registered interface evidence, not an exhaustive collision test.

## Remains open

The broad frame does not resolve rail terminations (#80), intersections (#82), or the gate latch/details (#83). Lining-relief depth (#84), port collars/staining origins (#85–86), depth-marker legibility (#87), and warning/critical-state water depth readability (#88) still need closer or state-specific pixels. Pool operating controls and service penetrations (#89–90) also require their direct views. The remaining separate floor wear/noise distinction #74/#137 is not established by view04.

No overall score is assigned here.
