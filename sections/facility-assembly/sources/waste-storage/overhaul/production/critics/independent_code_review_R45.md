# Independent bounded build/evidence code review — R45

Read-only review of the canonical build, full-room, validation, rendering, fingerprint and cold-comparison scripts, plus the package README, checklist and camera contract. I did not edit or execute the build scripts. The supplied R45 manifests contain all 21 main views and both D02/D03 details; these findings concern reusable fail-closed behavior and do not invalidate those present R45 files.

## Findings

### High — revision path traversal can overwrite the immutable source blend

`blender/build_overhaul.py:6` accepts `REV=args[0]` without checking that it is a plain revision basename. At line 354, it builds the output as `production/checkpoints/(REV + '.blend')` and passes that path to `bpy.ops.wm.save_as_mainfile`. With `REV='../../../module'`, path resolution produces `sections/facility-assembly/sources/waste-storage/module.blend`, exactly the immutable input identified at lines 8–10. The builder can therefore save the modified in-memory scene over the source file before the later validator detects its changed hash. The README asks for an unused revision name but gives no input guard.

Reproduction was checked without writing: resolving `production/checkpoints/../../../module.blend` yields the source blend path. Reject path separators/traversal and unsafe names before mutating the scene or creating outputs; also refuse a destination that resolves to the immutable input or an existing normal checkpoint.

### Medium — supplemental detail completion can pass while D03 is absent

`blender/render_detail.py:17–18` constructs the required-camera list from whichever names happen to exist in the current scene and asserts only that D02 is first. If D03 is missing, rendering D02 alone produces a manifest whose dynamic set can be marked complete. `blender/compare_coldstart.py:52–59` repeats the same dynamic membership test: it enters the detail comparison only if D02 exists and defines the expected set from whichever of D02/D03 exist in the checkpoint fingerprint. If D03 is absent from both checkpoint and rebuild, the comparison can omit it and still report detail PASS. `production/CAMERAS.md` explicitly requires both D02_CaptureService and D03_ExtractionRun.

The reusable gate should require the fixed set `{D02_CaptureService, D03_ExtractionRun}` in the scene/fingerprints, manifests and pixel comparisons, and fail if either is missing. R45’s actual detail manifest contains both, so this gap did not omit a current R45 image.

## Scope and status

I found no further concrete defects in the reviewed immutable-source checks, recursive disabled-socket validation, render hash/pose/settings resume checks, or authoring fingerprint comparison. The validation script clearly limits registered anchor and route-ray checks rather than claiming exhaustive runtime collision certification.

## R47 remediation follow-up

I re-reviewed the current canonical R47 guards. `blender/build_overhaul.py:7–18` restricts revisions to safe basenames, limits extra arguments to the optional `coldstart`, rejects existing normal checkpoint/archive outputs, and checks planned destinations for symlinks or resolution to the immutable source before reading or editing the scene. `blender/render_detail.py:14–23` applies a safe revision-name check and requires both named detail cameras to exist as cameras. `blender/compare_coldstart.py:52–60` now requires both fixed camera names in both authoring fingerprints and exact detail manifest/view sets.

The read-only `production/input_detail_guard_checks_R47.json` rejection evidence reports PASS for path traversal, existing archived revision, linked source output, missing detail render, and missing detail comparison. Each rejection check records the original source hash unchanged. Its complete-23-view control passes only for the copied historical R37 control and explicitly does not transfer that proof to R46/R47. These checks substantiate the two workflow fixes; they do not certify an R47 build or art result.

This report remains a bounded static code review, not a runtime integration certification or approval.
