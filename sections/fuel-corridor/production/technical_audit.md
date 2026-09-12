# Final technical state — F10 PASS

See FINAL_ACCEPTANCE.md and evidence/final-pass/delivery-receipt.json for the current verified artifact. Geometry/support/routes, source and material replay, cold16 and player-eye evidence are complete. Historical reports below retain their original failure state.

---

# Current technical evidence — final-F05

The slice report below is historical. Current evidence/final-pass/F05-technical.json is PASS. See F05-source-replay.json, F05-material-replay.json, F05-branch-handoff.json, F05-engineering-motion.json and delivery-survey.json. Canonical SHA256: f11dc1c5210f0d7c0552db0aafc1148724b54ef6beb0ce6abc6e9d0e42c85c6b. Full render settings are1440×960,32 samples,16 frozen cameras. Independent Luna interpretation is in critics/final-pass/luna-f05-final-visual.md. Final cold numeric exception is explicitly tracked in FINAL_PASS.md; no blanket final acceptance yet.

---

> Historical independent slice03 audit, retained unchanged below. Current full-scene evidence is in critics/astra-eng06-engineering.md and evidence/technical_eng06.json; final acceptance remains pending.

# Fuel Corridor independent technical audit

Status: **FAIL / full connector not yet audited**. Latest examined saved revision: `slice03`, cold reopened in Blender 5.2.0 LTS. No render, live Blender session, scene mutation or save was performed by this auditor. The full-route gate correctly remains `NOT_RUN` for the style slice.

The mandatory source is `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md` in the reactor-valorant worktree, especially sections 14, 14.1 and 18. This report does not award visual rubric points or establish final acceptance.

## Reproducible command

Use a fresh CPU-only background process with the section's private runtime. `--python-exit-code 1` propagates a failed audit to the caller.

```powershell
$env:BLENDER_USER_RESOURCES = 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/production/runtime'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/blender/Fuel_Corridor.blend' --python-exit-code 1 --python 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/blender/validate.py' -- --output 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/production/technical_validation.json'
```

Formal full-scene default is 32 samples at 1200 × 800. Slice evidence uses `--expected-samples 24`. This validator independently freezes all ten camera transforms, lens and framing settings, and checks Cycles, seed 71, denoising, 8 bounces, AgX Medium High Contrast, exposure 0.10, PNG/RGB, metre units and full-frame output. C03 was reset before formal review to location (-1.60, 7.20, 1.70), target (2, 11.4, 2), 23 mm; the builder is responsible for documenting and freezing the formal baseline.

## Current evidence and repair findings

`runtime/technical_slice03.json` records a fresh-process audit of the saved source; the saved and current source hashes matched at that run. Geometry, materials/dependencies, exact duplicate geometry and the revised camera/settings checks passed. All individual registered support anchors passed the strict geometric ray tests. Whole-assembly support still failed:

- The carrier barrel/band group sits 25 mm above its cradle at the closest measured point: retaining-band underside Z0.635 versus saddle top Z0.610. Both end-flange groups are separately disconnected from the sleeve; source geometry leaves approximately 8 mm axial gaps at sleeve ends.
- The task sconce hood/diffuser group has a measured 24 mm separation from its mounting arm: diffuser top Z2.421 versus arm underside Z2.445.
- The actual parked carrier envelope is 2.200 × 0.915 × 1.241 m. Its declared width is 0.900 m. The tool ledge reaches 15 mm beyond that total envelope. The validator now treats a dimension excess above 2 mm as a separate failure.

Earlier slice02 failures were repaired in slice03: disconnected caster suspension, valve handwheel, key tag, missing target registrations and degenerate gauge-face polygons. None of these repairs is evidence that the remaining issues are fixed; a new cold reopen is required.

## What is measured

All geometry checks use evaluated world-space mesh surfaces, including bevels, solidify, curves and text. Empty/missing/invalid material geometry and degenerate/non-manifold evaluated faces fail. Open surface boundaries are listed separately because intentional text, surface markings or cloth need not be closed collision solids. Exact duplicates compare world-space polygon topology at 1 micrometre precision independently of vertex order; any exception requires `intentional_duplicate_reason` on every involved object. Different-part intersections in a documented assembly are not classified as exact duplicate geometry.

Support roots must provide explicit world-space anchors, directions, exact intended support targets and tolerances. Missing registration fails even when a source helper accidentally assigns a support-dependent assembly the role `architecture`. Per-anchor `support_targets` and optional `support_directions` are supported. The source resolves target names from the authored intended anchor rays; the independent validator raycasts those recorded targets again, measures signed gap and verifies the nearer architectural surface has not been skipped. Author-written success flags are not evidence.

The maximum gap is 5 mm, maximum penetration 2 mm, and maximum surface-angle deviation 12 degrees. Each anchor must also lie within 5 mm of its own assembly's actual surface. Every member must reach an anchor through measured triangle intersections or sampled surface contacts within 5 mm. This distinguishes legitimately assembled parts from unrelated or floating dressing under the same parent. Root-to-root support dependencies must eventually reach a registered architectural support surface; mutual prop support cannot certify itself. This remains a geometric approximation, not a structural fastening/stress simulation.

Full scenes additionally receive these collision checks:

- Freight: 2.4 × 2.2 m crosshatched straight-route volume along the interface centerline, with measured width and headroom. The nominal 2.6 m design width remains a separate declaration and is not inferred from a 2.4 m passage test.
- Freight turn bays: a 3.0 m diameter, 2.2 m high operating cylinder at (0, 10) and (14.2, 10), conservatively enclosing the centered 2.2 × 0.9 m cart's planar rotation. This is not a steerable-wheel trajectory or operator-body simulation.
- Dressed bypass: a 2.0 × 2.2 m straight-route volume.
- Stretcher: nominal 2.2 × 0.75 × 1.1 m dimensions, straight-route clearance and a centered 0–90 degree rotation in 5 degree increments at the bypass corner. Attendants and dynamic steering are not included.

Route rays use transverse pitch up to 75 mm, vertical pitch up to 100 mm and longitudinal cross-sections up to 125 mm. Rays begin 5.1 mm above floor datum to honor the 5 mm threshold/upstand allowance. Floor continuity and centerline headroom are separately sampled. Actual meshes determine all obstructions; floor-cell numbers or AABBs alone cannot pass a route. Finite sampling can miss sub-grid features, so this is not engine collision certification.

## External boundaries and integration limit

Only the leaf members and their attached stiffeners, returns and kick plates under the exact `REFINERY_BOUNDARY` and `REACTOR_BOUNDARY` roots are excluded from the internal-route measurement. Jambs, sills, frames and all internal doors stay included. A generic exclusion flag elsewhere cannot exempt a barrier.

The validator separately raycasts and reports the section-owned presentation caps in their actual closed state. They are removable integration caps; their removal does not open neighboring geometry. No refinery/reactor mesh has been imported or edited by this audit. The existing reactor-owned doors are independently documented closed in `interface.json`; adjacent/global alignment, cross-section passage and runtime opening remain unverified.

## Validator controls

The disposable `--factory-startup --self-test` path creates no production files or saved scenes. `runtime/validator_self_test.json` records 13 passing controls: exact contact, allowed 4 mm gap and 1 mm penetration; rejected 20 mm gap, 5 mm penetration, fabricated anchors, missing target, unsupported assembly member, a 10 mm route barrier, generic cap-exclusion misuse and exact duplicates; and an unobstructed route pass. These controls verify that the new validator does not merely accept metadata.

Final acceptance still requires a full saved scene, all technical gates passing, all fixed-camera pixel reviews, the required repeated improvement cycles, and a separate final cold render comparison. This audit currently grants none of those outstanding acceptance claims.
