> Historical slice03 snapshot. Superseded by production/TASK_STATE.md. Do not execute its old next-step instructions.

# Resume Fuel Corridor — incomplete, acceptance FAILED

Paused at the reactor orchestrator's account-usage wind-down instruction, 2026-09-08 00:45 SAST. All owned Blender batches exited. Reviewers/auditor stopped. No automation.

- Task: `01a07dee-610e-7492-af4a-806593fcf3f6`.
- Worktree: `C:/Users/Camer/.codex/worktrees/3598/critical-shift`.
- Branch: `codex/fuel-corridor-20260908`, base `97bb68c`.
- Own **sections/fuel-corridor only**, plus the assigned original-checkout status file. Other rooms and live Blender instances untouched.
- Independent reviewer: `/root/astra_reviewer`, `gpt-6-astra`, `ultra`. Technical auditor `/root/technical_validation`; interface author `/root/interface_audit`.
- No commit/push: the section has not met the user's “only your verified section” condition. All files are preserved in this worktree.

## Exact saved state

`blender/Fuel_Corridor.blend` is **slice03**, an original staging bay only, 435 objects. SHA256 `8aa22f6492a5749bebd3a7047916db0d2f141356f3fa29a793699bdfa4947f45`. It contains ten predefined cameras, but only C03/C09 have meaningful rendered slice evidence. The complete corridor has **not been built or reviewed**.

Matching rendered source: `production/checkpoints/slice03/build.py`, SHA256 `94572fdfa0e263a98a003273bf5f407709f6d3c567598764d59a06765c623e1e`.

`blender/build.py` is **slice04-source-only**, also copied to `production/checkpoints/slice04-source-only/build.py`. SHA256 `80f487a49e2ba5a2f92516c39b75264c3059abe90b1d66072f09e82c0943330d`. Python AST parsing passed. It has **not** run in Blender, been rendered or reviewed. It attempts to repair saddle/barrel/end-cap contact, sconce support, carrier width, cloth shape/material and repetitive wear. The saved .blend is not this newer source.

Last complete renders: `production/renders/review/slice03/C03_HERO.png` and `C09_MATERIALS.png` (1200×800, 24 samples). Slice01/02 comparisons and independent reviews retained. No final renders; no full review cycles; no final cold-render acceptance.

## Actual scores and defects

Latest independent visual **FAIL**: scale/circulation 88 (local/provisional), shape 85, hierarchy 85, materials 84, lighting 85, color 87, storytelling 82; technical visually unscored. Every relevant category requires 90. See `production/critics/slice03.md`.

Visible defects: papery/flat cloth, repetitive handling marks, uneven shell/support refinement, broad architectural exposure and washed-out valve; right outer jamb cropped by C03. No full-route visual approval.

Independent cold CPU audit of slice03 **FAIL**: barrel/bands float 25 mm above saddles; end flanges have 8 mm axial gaps; sconce hood/diffuser separated 24 mm from arm; carrier is 2.200×0.915×1.241 m against 0.900 m declared width. Geometry/material/dependency/camera/duplicate gates and registered individual anchors passed; whole assemblies did not. Validator controls 13/13 PASS. Reports: `production/evidence/technical_slice03.json`, `validator_self_test.json`, and `production/technical_audit.md`. Source-only fixes require fresh measurement.

Additional unmeasured source risks for eventual full expansion: parked carrier crosses declared bypass centerline near Y12.32; cable-tray suspension rods may miss cross rungs; service wall supports must meet actual cladding. Repair and measure these after style approval. Never weaken the validator to obtain a pass.

## Next bounded action

Read this file, `production/TASK_STATE.md`, latest reviews and technical audit. Inspect the source-only changes and run **one slice04 build/render**, then independent CPU contact validation. Correct until the style slice passes; only then expand. Keep shared GPU serialization and private resources.

```powershell
Set-Location 'C:/Users/Camer/.codex/worktrees/3598/critical-shift'
& './sections/fuel-corridor/blender/run.ps1' -Stage slice -Revision slice04 -Cameras 'C03_HERO,C09_MATERIALS' -Samples 24 -Width 1200
$env:BLENDER_USER_RESOURCES = 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/production/runtime'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/blender/Fuel_Corridor.blend' --python-exit-code 1 --python 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/blender/validate.py' -- --expected-samples 24 --output 'C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/production/evidence/technical_slice04.json'
```

`run.ps1` freezes source per revision before waiting at the shared GPU gate and sets private resources plus section-root environment. Never render directly on HIP outside `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py`. Exit75 means queue timeout; never kill another worker.

After slice acceptance: full scene, objective route/contact checks, ten fixed cameras, at least four full reviews with genuine corrections, every relevant score>=90, final two cycles stable, saved-.blend fresh-process reopen and ten-camera rerender/compare, then verified section-only commit/push. No main merge.

## Architecture and integration limits

`interface.json`, `architecture/CONNECTION_CONTRACTS.md`, editable `architecture/A101-plan.svg` and inspected PNG document source-derived seams and proposed topology. Origin is refinery outer sill, +Y inward. Refinery nominal 2.6 m portal narrows to 2.49 m. Reactor owns its approach to local Y14.50 and its doors are closed. Independent mating transforms do not prove shared global placement. Refinery small units and reactor long cartridges have unresolved interchange semantics. Three service destinations and complete travel timing are unverified. Existing rooms must not move or be rebuilt; mine remains shallow decline, no elevator.

Shared status: `C:/Users/Camer/Games/critical-shift/ops/facility-run/status/fuel-corridor.md`.
