# Waste Storage editable overhaul candidate

Reviewed additive R51 candidate: both independent pessimistic Luna reviews pass99 in every category (weighted99.00/99.10), with its own original-source state, validation and all23 RGB pixels reproduced exactly. The room follows the owner’s dark, run-down direction. The original module, accepted snapshot and facility map are unchanged.

The build uses Blender 5.2 LTS, procedural materials and modeled practical fixtures. No external textures, libraries, world illumination or unseen fill are required. Every checkpoint starts from the original module whose SHA-256 is `8912b5c3b3d2525abb64e838d1fe83a1ea90aa12fea0c9b5a730d4449caecedf`.

Run `git lfs pull` after checkout to hydrate editable scenes, review images and generated scene inventories. Large generated JSON inventories are stored in LFS with their exact bytes; scripts, review prose and comparison summaries remain ordinary text.

Cold pixel comparison runs with ordinary Python and requires Pillow (`python -m pip install Pillow`). See `production/HANDOFF.md` for the selected revision's complete original-source replay and `python "$WASTE_ROOT/blender/compare_coldstart.py" R51` comparison command.

From the repository root, set `WASTE_BLENDER` to Blender’s executable, `WASTE_ROOT` to `sections/facility-assembly/sources/waste-storage/overhaul`, and `WASTE_REV` to an unused revision name. Build, validate and render a new revision:

```bash
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/../module.blend" --python-exit-code 1 --python "$WASTE_ROOT/blender/build_overhaul.py" -- "$WASTE_REV"
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/checkpoints/${WASTE_REV}.blend" --python-exit-code 1 --python "$WASTE_ROOT/blender/validate_overhaul.py" -- "$WASTE_REV"
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/checkpoints/${WASTE_REV}.blend" --python-exit-code 1 --python "$WASTE_ROOT/blender/render_overhaul.py" -- "$WASTE_REV"
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/checkpoints/${WASTE_REV}.blend" --python-exit-code 1 --python "$WASTE_ROOT/blender/render_detail.py" -- "$WASTE_REV"
```

Use a new revision for changed source/settings. The renderer supports a trailing list of camera names and retains compatible prior views; only a complete 21-view manifest with independent full reviews counts as a full cycle. Supplemental D02/D03 manifests are separate and must also be complete for final evidence. Each build archives the exact builder and full-room module bytes. To replay an archived full revision, invoke `blender/history/<revision>_build.py` with that same revision; it loads its corresponding archived full-room module. Use `coldstart` for an archived replay: normal builds reject an existing checkpoint/history revision. New canonical builds validate revision basenames, reject linked output files, and prevent resolving outputs to the original module. Archived builders retain historical exact bytes: revisions through R46 predate basename/source guards, and archives through R50 predate the complete orphan-output guard. Invoke only the documented literal revision with coldstart; use the canonical builder for unused new revisions. Append `coldstart` to save the independent fresh-source result under `production/coldstart/<revision>` without overwriting the active candidate.

See `production/TASK_STATE.md` for current gates, `production/CAMERAS.md` for coverage, and the two independent critic reports for scored pixel findings. Numerical support/route checks are bounded samples; they do not certify Unity collision, navmesh, lighting or runtime performance. Candidate promotion and map integration are separate work.
