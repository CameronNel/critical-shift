# R29 documentation and evidence gaps

Reviewer: independent Luna critic. Bounded read-only audit against the binding condenser-bay rubric and the defined local acceptance scope. No art score, Blender, render, or geometry change.

## Current documents checked

- `architecture/FLOORPLAN.md`: present, dimensioned, and updated through R29 geometry language. It records local bounds, U04/U02/CW interfaces, equipment footprints, gallery/stair changes, cart scope, and explicit limits.
- `architecture/CONNECTIONS.md`: present and consistent with the local-only boundary. It clearly labels U02 as a local stub, CW as capped/unbound, and D01/vent/drain as unbound where applicable.
- `interface.json`: present at revision R29 with origin transform, portals, utilities, envelopes, interaction hooks, and handoff limits.
- `production/CHECKLIST.md`: present, but its explicit audit reference still says **R28** (`validation/R28/saved-measurements.json`) and its evidence paragraph does not identify the R29 audit/hash. This is stale for an R29 acceptance packet.
- `production/validation/R29/astra-saved-audit.json`: available, hash `34c23f7e5298413ea348eb99a74e9ebb1221afcc3c26cc15cbced17c736d49a0`, PID 5728, status PASS. It reports U04 bore, D01, supports, sampled routes, gallery standing route, cart sweep, stair volume, interface markers, dependencies, and fixed-camera checks.
- `production/validation/R29-validation.json`: available, status PASS, but explicitly legacy sampled door/bore/anchor coverage and says the extended audit is required for routes and physical support acceptance.

## Mandatory proof still absent or stale

1. **Stale checklist linkage — major documentation gap.** The checklist points readers to R28 saved measurements and does not bind its claims to the R29 blend hash or R29 extended audit. A reviewer can find the R29 audit, but the required item-to-object/evidence map is not revision-closed.

2. **Neighbor alignment remains explicitly unverified.** `interface.json` has `neighbor_alignment_verified: false`. This is acceptable for the stated local-only scope where remote assembly/binding is handoff work, but the local transform and marker correspondence remain documented as unverified rather than accepted neighbor integration. U02 and CW must retain their local-stub/provisional wording.

3. **U04 is documented as geometric receive, not an assembled facility join.** `interface.json` correctly says `binding_status: geometric_receive_of_accepted_U04_opening_not_assembled`, and FLOORPLAN/CONNECTIONS repeat the limit. Local proof still needs the labelled section/cutaway plus same-revision pixels for the obscured throat; a plan or saved audit alone cannot show that interior face.

4. **R29 cold-open evidence is not yet present in this documentation packet.** The saved geometry audit has no cold-process or pixel-comparison result. The upcoming full review must supply independently reopened cold images and an honest comparison for the same R29 hash/process separation; this is an evidence requirement, not a remote binding requirement.

5. **Runtime claims remain intentionally unimplemented.** Interaction hooks are `design_contract_not_runtime`; navigation, runtime collision, whole-facility travel, and thermodynamics are marked pending/not simulated. These are correctly disclosed and are outside the local scenic acceptance boundary, but they cannot be presented as completed proof.

6. **Remote endpoints remain unbound by design.** U02 turbine continuation, CW plant loop, D01 remote corridor, drain, and vent are disclosed as local stub/unbound/provisional. No document supports claiming a facility bind. This is a handoff limitation, not a defect in the local documentation, provided it remains explicit in the final packet.

## Local proof status

The floorplan, connections, interface transform, checklist mapping, interaction-hook list, and R29 extended saved audit form a usable local documentation base. Before R29 can be treated as a complete review packet, the checklist must be revision-linked to R29 and the mandatory same-revision visual/cold evidence must be attached, including a labelled U04 interior cutaway and clear CW/roof/service coverage. No numeric category scores or acceptance disposition are issued by this audit.
