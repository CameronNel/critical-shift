# R06 support-connectivity broadphase

Ran support-connectivity-R06.py in fresh background Blender 5.2 without rendering, GPU work or model saves. It builds a graph from evaluated world AABBs using Euclidean box separation <=5 mm plus 1 micron numerical epsilon. Roots are the 847 render-visible original mesh objects; there are 211 additive meshes.

**193 additive meshes connect to an original mesh candidate; 18 are detached across 11 components.** Six of those are a clipboard cluster at essentially the 5 mm threshold, not a meaningful newly discovered visible failure.

| Detached component | Nearest connected candidate | Measured AABB separation |
|---|---|---:|
| Localized hand wear and .001 (two separate components) | Intercom mounting block | 6.500 mm each, Y |
| Service cabinet bolt through .003 (four separate components) | Service cabinet inset door | 12.500 mm each, X |
| Localized hand wear.002 | Permit stamp shelf | 10.595 mm combined axis distance |
| Compliance sign backing | Gate lintel concrete skin | 13.002 mm, Y |
| Shielded dock task light + Recessed luminaire lens | Canopy front folded fascia | 22.501 mm, Y; roof is 40.000 mm above housing |
| Shielded dock task light.001 + Recessed luminaire lens.001 | Canopy front folded fascia | 22.501 mm, Y; roof is 40.000 mm above housing |
| Clipboard board, sheet, clip and three ruled lines | Inspection station backing | 5.001 mm, Y |

Investigate/repair the sign attachment and two light mounting connections first, then bolt placement and wear-chip attachment. Bring thin wear geometry close to its intended surface, rather than inventing brackets for decals. The clipboard exceeds the 5 mm nominal threshold by about 1.07 microns; this is numerical-borderline evidence, not a useful geometry defect. The holder shoes are graph-connected in R06. The planned R07 1 mm shoe adjustment was not part of this inspection.

These are **broadphase contact candidates, not exact validated supports**. A disconnected AABB pair proves the actual enclosed surfaces cannot touch across a smaller distance, but the actual surface gap may be larger. Connected AABBs can overlap across empty space; deep intersections also pass this graph; touching a nearby object does not establish appropriate load-bearing support. Original roots are render-visible meshes, not independently classified structural/collision objects. Text and curves are excluded. No support-angle, intended anchor, mounting orientation or penetration acceptance is implied by graph reachability.

Accordingly this report grants no full support-contact PASS. It narrows the concrete construction investigations and records exact *AABB* distances, without presenting those as exact closest-surface measurements. Script and full graph report: support-connectivity-R06.py and support-connectivity-R06.json. The JSON includes detached components, nearest candidate pairs and axis distances, original root candidates and additive evaluated bounds. No engine binding work is relevant to these findings.
