# Turbine Condenser Bay — final local visual handoff

**Accepted locally, 2026-09-12.** Independent Luna (`gpt-5.6-luna`, `/root/luna_critic`) inspected two complete, separately rendered 50-image rounds. Every category is strictly above 90 in both rounds. All six saved CPU checks pass. Both rounds' 18-camera and seven-camera supplemental cold comparisons pass. The cross-round main numerical maximum screen remains **FAIL**, independently adjudicated as localized GPU edge variance; the disclosure below is part of this acceptance.

## Asset and ownership

- Editable asset: [condenser_bay.blend](../blender/condenser_bay.blend), revision **R34**, **2,724 objects**, 18 fixed room cameras.
- SHA256: `26edf558d2e03b16b841940d20973b74017a52e9f8c0c320d5ff5487c9d9ea3b`.
- Owner: Astra. Worktree: `C:/Users/Camer/.codex/worktrees/3671/critical-shift`. Branch: `codex/condenser-bay-astra-20260912`.
- Local section-only commits; no main merge, push, neighbor modification, live Blender takeover, or GPU-lock deletion.
- Grok's original room/layout and R20/R21 evidence remain preserved. Immutable [R21 baseline](checkpoints/R21/grok-baseline.blend), SHA256 `ff361817176958680f4d80c35fcae54a9acb04b5a75ea176148ad51c440c23e2`, remains the continuation source. Failed intermediate reviews and audits are retained.

## Independent acceptance

| Category | R34 | R34-stability |
|---|---:|---:|
| Contract / specification coverage | 94 | 94 |
| Scale / layout | 92 | 92 |
| Machinery logic | 93 | 93 |
| Circulation / readability | 91 | 91 |
| Construction / detail | 91 | 91 |
| Materials | 94 | 94 |
| Lighting | 92 | 92 |
| Palette | 94 | 94 |
| Storytelling / environmental specificity | 92 | 92 |
| Valorant / reference fidelity | 91 | 91 |

Review records: [round one](critics/astra-R34-full-review.md), [round-one scores](critics/astra-R34-scores.json), [round two](critics/astra-R34-stability-full-review.md), [round-two scores](critics/astra-R34-stability-scores.json). Neither review transfers neighbor acceptance or claims whole-facility integration.

## Complete evidence and verification

Each round contains 18 warm + 18 fresh-process cold images, plus seven labelled supplemental warm + seven cold images, all 1920×1080 at 32 Cycles samples. R34-stability uses the unchanged saved scene, cameras, settings and renderer sources; these are fresh renders, not relabelled copies.

| Evidence | Round one | Round two |
|---|---|---|
| Main / cold gallery | [R34](critics/astra-R34-gallery.html) | [R34-stability](critics/astra-R34-stability-gallery.html) |
| Supplemental / cold gallery | [R34](critics/astra-R34-supplemental-gallery.html) | [R34-stability](critics/astra-R34-stability-supplemental-gallery.html) |
| Main cold comparison | [PASS](validation/R34/cold-comparison.json) | [PASS](validation/R34-stability/cold-comparison.json) |
| Supplemental cold comparison | [PASS](validation/R34-supplemental/cold-comparison.json) | [PASS](validation/R34-stability-supplemental/cold-comparison.json) |

Full images and per-image process IDs, PNG hashes, camera matrices, settings and renderer-source hashes are retained under `renders/review/R34*` and `renders/review/cold-R34*`. Exact controllers are copied into each pack's `renderer-source/` directory.

[CPU validation summary](validation/R34/cpu-validation-summary.json): six PASS checks covering the original validator, saved supports/routes/stairs/dependencies/cameras, open exhaust inlet, chest-to-shell contact, eight seated lower-chest fasteners, and measured geometry. These are disclosed static local tests, not engine movement or engineering certification.

**Cross-round variance disclosure:** [main comparison](validation/R34-stability/stability-comparison.json) retains its numerical **FAIL**: C02 has one pixel above the fixed 32/255 maximum (max 35); C08 has 18 such pixels (max 61). Mean difference and affected-area limits pass; worst mean is 0.0380896/255. [Localization](validation/R34-stability/variance-investigation.json) records the exact regions. Luna inspected both sets and found isolated GPU edge variance with no substantive geometry, material, lighting, framing or readability regression. Astra accepts this disclosed visual stability judgment under the unchanged [comparison policy](COLD_COMPARISON_POLICY.md); no threshold or raw result was changed. [Supplemental cross-round comparison](validation/R34-stability-supplemental/stability-comparison.json) passes numerically.

## Delivered polish and residual visual limits

The original condenser room now has connected return nozzles and fittings; supported CW/hoist attachments; physical glass walls, liquid and meniscus; a continuous rectangular U04 throat, joined chest and seated flange fasteners; tactile painted metal and restrained neutral/warm lighting. The original operator rotaries, southeast equipment view, real stairs, gallery underfoot and room layout remain.

Retain the complete supplemental evidence with this handoff. Luna still records tight C04/C09 underside readability, C06 dependence on the full CW supplement, C08/W08 gallery congestion/dark destination, and a W03 structural-column occlusion. These disclosed residuals are included in both passing scores; they are not claims of flawless framing.

## Placement and integration actions

Room: **11.40 × 9.40 × 6.00 m**. D01 local origin `(0,0,0)`, +Y inward, +Z up. Transform: **turbine_xyz = condenser_xyz + (1.6,7.4,-6.0)**. Use [interface.json](../interface.json), [measured floorplan](../architecture/FLOORPLAN.md), [saved measurements](validation/R34/saved-measurements.json), [equipment checklist](CHECKLIST.md) and [camera corrections](CAMERA_CORRECTIONS.md).

| Interface / system | Local state and next action |
|---|---|
| U04 exhaust | Open 2.5 × 1.5 m receive at `(3,4.05,6)`, mapping to turbine `(4.6,11.45,0)`. Integrator must reconcile slab/header mating in the assembled assets. |
| U02 condensate | Local 0.2 m stub `(7.9,0,5.42)`, facing −Y. Route continuation to turbine U02 `(9.5,0,0.45)` in turbine coordinates. Turbine-owned blind cap remains untouched; coordinate its action with that owner. |
| Cooling water | Capped local 0.3 m sockets `(9.6,3.2,3.15)` and `(9.6,4.9,3.15)`. Design/bind the external loop; Cooling Plant's proposed 0.2 m sockets are not a proven reciprocal match. |
| D01 | Local 2.0 × 2.4 m portal; unbound receiving connector. Supply and align the remote corridor, then verify assembled travel. |
| Drain / vent | Bind the unbound endpoints in interface.json and inspect assembled penetrations. |
| Gameplay and runtime | Implement engine import/export adaptation, optimization, collision, navigation, runtime lighting, controls, animation, networking and whole-map checks using the saved hooks. |
| Major maintenance | Validate the carried bundle/removal sequence in engine. The east area is staging space; a full extraction sweep is not certified. |

No MW, RPM or pressure rating, working facility cooling loop, remote bind, or engine-ready runtime performance is claimed. [Asset notes](ASSET_NOTES.md) describe dependencies and runtime ownership.

## Replay and GPU configuration

In a separate isolated section copy, restore `production/checkpoints/R34/*.py` into `blender/`, retain the immutable R21 baseline, and invoke the restored `astra_continue.py` with a new revision label under `resource_guard.py` and the shared GPU gate. Do not execute a checkpoint script in place: its relative paths expect `blender/`. `build_condenser.py` retains Grok's factory-source alternative; pixel-identical factory replay is not claimed.

Current full-round command from the worktree: `& ./sections/condenser-bay/blender/astra_full_round.ps1 -Revision <new-review-name> -Samples 32`. A completed label must not be overwritten. Comparison command: `production/compare_pack.py <new-review-name> <previous-review-name>`; also compare their `-supplemental` packs.

The user reauthorized GPU and requested maximum speed. Verified configuration: Blender 5.2, RX 9070 XT, Cycles HIP hardware ray tracing, GPU OpenImageDenoise, persistent data, normal priority and all 16 logical CPU processors. One worker uses `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py`, owner `astra-condenser-bay`. No global driver/game settings were changed. Explicit CPU-only mode remains available; the old CPU cap is superseded. Final rendering has finished.
