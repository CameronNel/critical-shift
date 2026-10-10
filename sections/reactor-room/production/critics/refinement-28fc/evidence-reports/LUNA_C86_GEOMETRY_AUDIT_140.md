# C86 finite geometry QA disposition (#140)

**Candidate:** `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`  
**SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`

## Decision

Accept #140 as completion of the requested finite support/intersection QA for the inventoried current C86 assemblies. This is a bounded technical disposition; it is not a claim that every possible all-pairs collision or every vertex is proven clear, and it does not close any remaining visual/artistic issue.

## Evidence

C86's 14 authoring checks pass in `/workspace/scratch/reactor-refinement-cycle86/checks.json` (SHA-256 `4cb605ddc1d3e088afc60cd209b485efbbdde46b83e384dab9a1fdac6d37fca5`). The independent control-room verifier passes in `/workspace/scratch/reactor-refinement-cycle86/control-room-check.log` (SHA-256 `7520a87811c8c17e04afb211e09bd12846ec2f30da30729ef1e8459405f4ae1c`). The exact audit `/workspace/scratch/reactor-refinement-cycle86/audit.json` (SHA-256 `00cd3c2f195c2860738f39307256aae44601af87f0f39c1da4a3c58748c342a1`) reports 203 sign records with zero failures; 2,809 sampled support/contact records with zero failures; 1,957 registered assemblies across 27 owner groups; zero empty registrations; and 290 protected objects unchanged.

C85→C86 exact scene delta `/workspace/scratch/reactor-refinement-cycle86/scene-delta.json` (SHA-256 `c42367ebfd261f5740877fc126aa387afe7a73e79515b6eadaf86207a70abecc`) changes only `RH floor service oil film`, with 1,932 unchanged objects and no additions, removals, or unexpected changes. C84→C86 exact delta `/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json` (SHA-256 `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19`) records the intended C85 changes (41 changed, 13 added, 1,879 unchanged) and no unexpected changes. Cold C86 checks and the separate control-room verifier pass; `/workspace/scratch/reactor-refinement-c86-cold/scope.json` (SHA-256 `73518ecd86054b74c1242ae44277024ecee563af3200bcd94a6392294700bffb`) records 55/55 declared owned comparisons matching the declared scope. It does not establish whole-scene equivalence.

Independent probes further check the two new or fitted geometry families:

- Oil film: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C86_OIL_FILM_PROBE.json` (source-bound to C86) finds 482 vertices, 1,056 edges, 576 faces, positive signed volume `0.00014953879408669563 m³`, zero nonmanifold edges, zero degenerate faces, underside vertices at z=0, and 481/481 interior/perimeter rays to `R2 floor`. Maximum floor-hit z error is `3.73e−9 m`.
- Pool inlet: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C86_DIFFUSER_CLEARANCE_PROBE.json` samples every evaluated diffuser vertex and face centroid against the exact evaluated liner BVH. Minimum sampled separations are 8.57 mm for the body, 6.59 mm for slots, and 3.66 mm for the IRON flange.

Prior finite whole-room support inventory and the declared check scope are in `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_GEOMETRY_AUDIT_140.md` and its C82/C49 bounded predecessors. C86 has no unreviewed new assembly type beyond the corrected oil film, fitted pool inlet, and the already-covered C85 additions; the exact deltas and cold owned-scope comparison bind those changes to this result.

## Limits

The audit samples registered interfaces and inventoried families. It is not an exhaustive all-vertex/all-pair collision certificate; motion checks sample declared poses; cold comparison is limited to the 55 declared owned comparisons. The oil-floor rays and diffuser-liner distances are finite surface samples. The artistic review remains open, including pool-inlet appearance (#85), remaining rod/construction rows, board faces/states, and final whole-room hierarchy. Issue #61 is visually accepted from exact-C86 full-quality views03 and61; see `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C86_VIEW03_FLOOR_REVIEW.md`. No overall or area score follows from this geometry-only disposition.
