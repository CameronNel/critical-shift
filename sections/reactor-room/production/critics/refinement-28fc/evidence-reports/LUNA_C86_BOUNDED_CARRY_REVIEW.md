# C86 bounded evidence carry

**Candidate:** `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`  
**Candidate SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`  
**Prior reviewed candidate:** `/workspace/scratch/reactor-refinement-cycle85/hall_final.blend`  
**Prior SHA-256:** `61bad7f0b34d5a9f7336e349c9e64cd8081666be62530e94ea56b4d2e36354ac`

## Disposition

I carry forward 81 C85 bounded historical dispositions whose reviewed subject and relevant context are unaffected by the exact C85→C86 delta. I independently accept #140 on C86 only as the finite geometry support/intersection QA recorded in [LUNA_C86_GEOMETRY_AUDIT_140.md](LUNA_C86_GEOMETRY_AUDIT_140.md). The rolling JSON therefore has 82 accepted IDs and 58 pending IDs (including partial #19 and #131); visual review and scoring remain open.

The C85→C86 delta changes exactly one object, `RH floor service oil film`; it adds/removes no objects, reports no unexpected changes, and leaves 1,932 objects unchanged. This repair seats the oil-film underside at z=0. It does not change the film's surface material, footprint, floor material, water, lamps, cameras, or unrelated assemblies. I do not carry #61 appearance from the prior scene; it remains pending exact-C86 pixels. C86's exact delta is `/workspace/scratch/reactor-refinement-cycle86/scene-delta.json` (SHA-256 `c42367ebfd261f5740877fc126aa387afe7a73e79515b6eadaf86207a70abecc`).

C85's prior C84→C85 change scope also remains in force: 41 objects changed, 13 added, none removed/unexpected, and 1,879 unchanged. This includes the state-board cells/scales, R2 floor response, rods, fitted pool inlet, and oil film. Those C85-affected review rows remain pending in C86: #5, #6, #7, #58–68, #74, #75, #85, #91, #92, #94, #102, #131, #136–140 except #140 finite QA. The source-bound state, floor, rods, and pool pixels are required before visual dispositions.

## Exact C86 technical gates

- C86 source SHA: `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`.
- C86→C85 delta PASS: one changed oil-film mesh, 1,932 unchanged, no additions/removals/unexpected changes.
- C84→C86 delta PASS: 41 changed, 13 additions, no removals/unexpected changes, 1,879 unchanged.
- Warm C86 authoring checks: 14/14 PASS; separate control-room verifier PASS.
- Cold C86 authoring checks: 14/14 PASS; separate control-room verifier PASS. The 55 declared owned comparisons match successfully. This is not full-scene equivalence.
- Current audit: 203 sign records/0 blocked, 2,809 support-contact records/0 failures, 1,957 registered assemblies, 27 covered owner groups, 0 empty registrations, and 290 protected objects unchanged.
- Independent current oil-film probe: closed positive-volume mesh, 0 nonmanifold/degenerate faces, underside at z=0, 481/481 floor underlay rays hit `R2 floor` with maximum height error `3.73e−9 m`.
- Independent pool-inlet probe: against the exact evaluated liner surface, sampled minimum clearances are 8.57 mm at the diffuser body, 6.59 mm at the slot mesh, and 3.66 mm at the flange.

These checks do not close the current visual rows and do not claim exhaustive all-vertex or all-pair collision detection. All ten current full-quality main images are still needed, alongside the targeted views needed to resolve remaining rows. No overall or area score is assigned.
