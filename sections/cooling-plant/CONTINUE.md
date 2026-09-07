# Continue Cooling Plant

**PAUSED / INCOMPLETE. No production acceptance.** The run coordinator relayed the user's low-usage wind-down instruction on 8 September 2026. Finish the already queued S03 render batch, preserve the checkpoint, and stop. No automation is scheduled.

- Task: `01a07deb-e7a7-7ee1-b3c6-03e0ad16ca0c`
- Worktree: `C:/Users/Camer/.codex/worktrees/ef37/critical-shift`
- Branch: `codex/cooling-plant-astra-20260908`
- Scope: `sections/cooling-plant/` only; the explicitly required shared status lives in the original checkout at `ops/facility-run/status/cooling-plant.md`.
- Builder/reviewer model request: Astra Ultra. Independent reviewer `/root/astra_reviewer` was explicitly launched as `gpt-6-astra`, `ultra`, fresh context. Technical auditor `/root/technical_audit` used the same model/effort.
- Current saved source/scene revision: **S03, slice**. `blender/cooling_plant.blend` is editable and builds from factory empty. `production/checkpoints/S03/` contains matching immutable source. Full-room construction functions exist but have **never been built or accepted**.
- Architecture: **CP-A02**, dimensioned SVG/PNG and `interface.json`. Arithmetic validation passes with a declared jamb/swing overlap; this does not certify the Blender geometry.
- Last independently reviewed renders: **S02**, three cameras at 1200×800, 40 samples. **S03 completed successfully** through the shared HIP gate: C07_PINCH, C10_MATERIALS and C08_WORKSHOP, same resolution/samples. All three images were opened by the builder after completion. S03 has **no independent art review**. See its `render_manifest.json`.

## Actual acceptance evidence

S01 failed expansion: shape73, hierarchy79, materials64, lighting73, color87, storytelling59. S02 failed expansion: shape80, hierarchy82, materials73, lighting76, color88, storytelling68. Scale/circulation and technical art-category scores remain unassigned. See reviewer-authored `production/critics/S01.md` and `S02.md`.

S02 observed weaknesses: pristine/synthetic material response; workshop tools/cloth/ring insufficiently convincing; staged dressing; near-black machinery surfaces lose information. S03 changes address some of these but are unreviewed. Never transfer S02 scores to S03 or claim a pass.

Corrected fresh-process S03 CPU audit (`production/technical/S03-validation.json`) reports **five failures**:

1. D02 leaf overlaps bench standing strip by about 20 mm.
2. Bench assembly exceeds its rear declared envelope by 10 mm.
3. Two hinge support anchors each measure 64.64 mm penetration; the mounting construction and support plane must be resolved.
4. Removed seal floats 20 mm above the wiping rag.

The last two items in (3) are separate failed anchor checks, hence five total failures. Material assignments, camera existence and measured utility joins passed the current slice audit. An earlier S03 validator invocation emitted 53 failures because decorative-curve endpoint metadata was treated in the wrong coordinate frame; the auditor fixed that bug and replaced the report with the five-failure result. Do not confuse the old terminal output with current evidence.

No ten-camera full-room batch, four full correction cycles, final stable pair, final independent >=90 scores, or final cold reopen/render comparison exists. The current fresh reopen is **CPU validation only**, not final cold-start art evidence. No game-engine integration or runtime simulation is implemented.

## Read before resuming

1. `C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md`, `briefs/cooling-plant.md`, and README.
2. Current canonical GAME_SPEC, ART_DIRECTION, ART_REFERENCE_INDEX and AUTONOMOUS_SECTION_BUILD_PROTOCOL under `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/`.
3. Blender skill and approved reference PNGs `reference-a02-hall.png` and `reference-b01-controls.png` in that reactor section's `art/reference/generated/`.
4. This section's TASK_STATE, reviewer reports, technical report and interface/architecture notes.

No old `.blend`, `.fbx` or `.glb` geometry was imported. Do not touch active reactor/turbine or completed rooms. Proposed reactor connection is translation `(8.4,-8.4,0)`, Z rotation `-135°`; it has **not** been applied. Shared wall seam and new turbine placement still require connector coordination.

## Next bounded action

On explicit resume, inspect completed S03 pixels and repair the five measured defects in the slice, then obtain a fresh independent pixel review. Keep existing fixed cameras. Do not expand until style passes. Once it passes, build the full plant, inspect all ten cameras, and perform at least four genuine full review/correction cycles until every relevant independent category reaches 90, with stable final evidence and cold reopen/render proof.

## Commands from the worktree

```powershell
# Rebuild slice after corrections (choose a new revision; preserve S03 evidence).
& 'sections/cooling-plant/blender/run.ps1' -Action build -Stage slice -Revision S04

# CPU objective checks: a FAIL exit is expected until measured defects are fixed.
$env:BLENDER_USER_RESOURCES = Join-Path (Get-Location) 'sections/cooling-plant/.blender-user-validation'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 4 'sections/cooling-plant/blender/cooling_plant.blend' --python 'sections/cooling-plant/blender/validate.py' -- --revision S04 --strict-exit

# Wrapper always acquires the shared GPU gate and uses private section resources.
& 'sections/cooling-plant/blender/run.ps1' -Action render -Revision S04 -Cameras 'C07_PINCH,C10_MATERIALS,C08_WORKSHOP' -Samples 40 -Width 1200

# Only after the slice passes:
& 'sections/cooling-plant/blender/run.ps1' -Action build -Stage full -Revision R01
& 'sections/cooling-plant/blender/run.ps1' -Action render -Revision R01 -Cameras all -Samples 48 -Width 1440
```

Never terminate another worker's Blender to get GPU access. Exit75 means the queue wait expired. Update the unique shared status after each review. Preserve honest failures; commit/push only this section, with no main merge.
