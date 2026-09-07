# Continue Medical / Reanimation

Stopped on user instruction to wind down the facility run because account usage
was low. This is an **incomplete, unaccepted checkpoint**, not a completed room.
Do not schedule an automation. Resume only when the user requests it.

## Exact location

- Worktree: `C:/Users/Camer/.codex/worktrees/1edf/critical-shift`
- Branch: `codex/medical-reanimation-20260908`
- Task: `01a07de5-77a6-79e1-8a42-1f82a167ea58`
- Own only `sections/medical-reanimation/`; preserve all other sections.
- Shared status: `C:/Users/Camer/Games/critical-shift/ops/facility-run/status/medical-reanimation.md`
- Independent reviewer: `/root/astra_reviewer`, Astra ultra.
- Technical auditor: `/root/technical_validation`, Astra ultra.

## Saved state

The dimensioned SVG/PNG and `scenery/interface.json` define an 8 × 9 m main room
with a 2.2 × 3.8 m recovery alcove: 80.36 m² interior. The main entry threshold
is local (0,0,0), +Y inward, +Z up. The sole pedestrian portal is 2.2 × 2.5 m.

Only the entry/gross-decontamination **style slice** has been modeled. Its last
completed source/render revision is **s08**, saved to `blender/style_slice.blend`.
The last complete render batch is:

- `production/renders/review/s08/C00_slice.png`
- `production/renders/review/s08/C00b_workstation.png`
- `production/renders/review/s08/validation.json`

The builder inspected both actual images. Original source is
`blender/build_medical.py`. The s07 source checkpoint is historical text to restore
into the normal build path if needed; do not execute it from the checkpoint folder.
The full OCRU, cart, reserve battery, consumable bay, recovery bed and remaining
room architecture have **not** been authored. `full_room.py` and
`medical_reanimation.blend` do not exist. `-Phase full` is consequently unavailable.
Ten planned full-room cameras exist as definitions, but there are **no ten-camera
full-room renders, no full-room review cycles, and no cold-start acceptance**.

## Actual review / audit state

Latest independent review is **s08 FAIL, 81.25/100**: scale85, shape80,
hierarchy83, materials78, lighting82, color90, storytelling78, technical74.
See `production/critics/s08.md`. Earlier formal slice means: s01cpu62.0,
s02 68.0, s03 69.25, s05 77.125. None was accepted. s04/s06/s07 were builder-inspected intermediate
corrections, not independent full review cycles.

Major remaining concerns: stiff textiles, paint chips reading as attached flecks,
uniform broad surfaces, inflated/regular glove form, and incomplete attachment
coverage is incomplete. The saved s08 validation proves measured 2.20 × 2.50 m
entry, .60 m-wide / 1.80 m-high standing access to arrival and wash, and its listed
contact checks only. Its `pass: true` is **not** complete technical acceptance.

The auditor's new `blender/register_supports.py` is **not yet integrated** before
save in `build_medical.py`. Its first real s08 audit found 304 geometric objects,
203 classified, 91 supported/rooted and 213 failures, with zero evaluation errors.
Some failures are real gaps; others arise from duplicate coincident vertices on
converted Blender curve/font caps falsely splitting connected components.
Read `production/critics/support-audit-s08-diagnostic.md` before changing geometry.
Do not increase tolerances to force a pass.

The newer `validate_geometry.py` includes support-report freshness checks, so an
old saved validation report must never be reused as fresh support evidence.

## First bounded action on resume

1. Read the latest slice review and support-audit checkpoint.
2. Correct the auditor's component analysis to account for coincident conversion
   vertices, preserving the 5 mm gap / 2 mm penetration / 12° defaults.
3. Integrate `register_supports(scene)` before saving the Blender file, retaining
   its full report; rerun the audit once. Repair confirmed real gaps and missing
   host classifications. Do not remodel based on known validator false positives.
4. Render the two unchanged slice cameras and request honest Astra ultra review.
   Expansion remains blocked until the style slice passes.

Then author the full original OCRU room from the floorplan, freeze all ten formal
cameras, complete at least four genuine full review/correction cycles, and attain
90 in **every** category. Finish with a fresh-process final reopen/render of all
ten cameras, compare pixels, verify dependencies/contact/clearances, and push the
verified section. No main merge or other-room edits.

## Commands

Run from the worktree in PowerShell. Scripts set private section-local Blender
resources. CPU rendering is intentional and needs no shared GPU lock.

```powershell
& 'sections/medical-reanimation/blender/run.ps1' -Revision s09 -Cameras 'C00_slice,C00b_workstation' -Samples 32 -Width 1280 -Cpu
```

Omit `-Cpu` to use the shared GPU gate. Every GPU job must use that wrapper; never
launch a GPU render directly or interfere with another worker's Blender.

```powershell
& 'sections/medical-reanimation/blender/run.ps1' -Revision audit-only -NoRender
```

Cold reopen plumbing was written but **not run or verified** during wind-down:

```powershell
& 'sections/medical-reanimation/blender/cold.ps1' -Blend style_slice.blend -Revision slice-cold -Cameras 'C00_slice,C00b_workstation' -Samples 32 -Width 1280 -Cpu
```

The authoritative full-room briefs/specs and approved references remain at the
original absolute paths recorded in `scenery/architecture.md` and
`art/reference-notes.md`. No old geometry was imported. No new generated reference
was adopted. One late queued GPU folder `review/s01/` used newer source and is
excluded from Git/history; `s01cpu/` is the authentic first visual baseline.
