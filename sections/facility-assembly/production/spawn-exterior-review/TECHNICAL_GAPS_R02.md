# R02 technical evidence review and minimum R04 carry-forward

R02 evidence read:

- `TECHNICAL_R02.json`: cold load passes; source preservation and section placements pass; wall anchors and utility wall returns pass; targeted checks **fail** because `Spare pipe rack foot`, `.001`, and `Wall planting bed.002` each have a 0.065 m signed ground gap. The report explicitly scopes itself to targeted new objects and is not blanket structural certification.
- `connections/completion/AUDIT_facility_spawn_concept02_R02.json`: all listed routes, including `R10`, `R22`, and `SPAWN_INNER_TRANSITION`, have samples and no findings. This supports the route category for the R02 revision, subject to the R04 geometry change not regressing it.
- `BUILD_R02.json` / render manifest: build provenance, object ledger, fixed cameras, EEVEE render context, and approved concept are recorded.

## Minimum evidence still needed for R04 technical review

1. **R04 exact geometry/support report:** rerun the targeted ground-contact and wall-anchor checks after the 6.5 cm rack/bed correction and south-conduit reroute. It must show zero unresolved support gaps or clearly disposition every exception, with evaluated coordinates and tolerances. Keep the existing scope caveat: this does not certify every retained source object.
2. **R04 route regression:** rerun the route audit against the R04 blend, including the spawn inner transition and rescue courtyard routes. Confirm no findings, route widths/clearances, thresholds, and no new obstruction from beds, rack, conduit, or hose.
3. **R04 interface/reservation audit:** provide explicit portal/aperture, neighboring-section reservation, and source-preservation checks for spawn/courtyard interfaces. Placement/hash pass alone does not prove reservation integrity.
4. **R04 dependency/material validation:** cold-load the exact R04 file in a fresh process and record linked libraries, image/material dependencies, missing assets, hidden/holdout/render visibility, and stable object naming. R02 `cold_load: PASS` is revision-specific.
5. **R04 Blender assembly performance check:** record a reproducible viewport/render or assembly benchmark with scene/revision, camera or workload, frame count, and result. This is the rubric's Blender assembly readiness evidence; it does not establish Unity runtime.
6. **Separate Unity readiness record:** if the delivery contract requires Unity acceptance, provide a separate status for collision, navmesh, controller traversal, cart/body-carrying behavior, and Unity performance. These remain `UNVERIFIED` even when the Blender assembly category passes.

No R04 score is assigned here. The R02 technical evidence can support scoped claims only after R04 reruns confirm that the corrected geometry and route have not regressed.
