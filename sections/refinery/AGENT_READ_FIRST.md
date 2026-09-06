# Refinery — read first

**Paused by user, 7 September 2026. Not final acceptance.**

Read `production/TASK_STATE.md` before running anything. This package is on the isolated branch `codex/refinery-compact-20260907` in `worktrees/refinery-compact`. The original repository and another Spawn worktree contain unrelated work; do not disturb them or reuse a live Blender process.

Open `blender/Refinery.blend` for the saved editable scene, including the immediate correction pass. It contains all nine stations. `production/renders/review/` contains all eight first-pass images; `production/renders/final/` contains only the corrected images completed before the user stopped the job. `production/validation_report.json` records zero-error objective validation of the saved corrected scene.

**The final render batch, state previews, interface re-audit and cold-start verification remain incomplete.**

```powershell
& sections/refinery/blender/build.ps1 -Mode final -States
& sections/refinery/blender/build.ps1 -Mode cold-start
```

The wrapper launches fresh background Blender with a private resource directory and six CPU threads. It never uses the live Blender UI and fails non-zero on validation failures. Python entrypoint: `blender/build_refinery.py`.

Cart geometry faithfully preserves the existing Gullet cart with source hashes. The refinery adds a new 50° tipping cradle. Blender metadata prepares Unity interactions and physics; it does not implement them.

The user authorized one coordinated build/review/correction pass. Do not claim four formal review cycles. Resume the unfinished evidence work and inspect corrected pixels before judging completion.
