# Independent bounded code review — R49

Read-only review of the current canonical build and evidence gates, with attention to the R49 coating-loss additions. This is a source-level review; it does not certify the current build, render pixels, portable replay, or art acceptance.

## Findings

No new concrete code defect found in the R49 additions.

The seven R49 calls in `blender/full_room.py:1137–1150` reuse `projected_coating_loss` at `blender/full_room.py:841–876`. Each call uses one exposed-undercoat layer, deterministic per-label shape variation, dense tessellation, and ray projection onto the evaluated vessel shell. The function asserts every projected vertex hits the shell, offsets it along the hit normal, and records a support anchor. The two replacement materials use the existing `broken_substrate` material treatment. The four SC01 and three SC02 calls are bounded to named collar/carrier handling zones; they add no perimeter layer or lighting/pose changes. I found no unprojected geometry or disabled shader-socket dependency in this call path.

The R47 safety and required-detail guards remain in the current canonical scripts: `blender/build_overhaul.py:6–20` validates revision basenames and arguments, prevents normal reuse of archived revisions, and checks planned outputs against symlink/source resolution; `blender/render_detail.py:14–23` validates its revision and requires both fixed detail cameras; `blender/compare_coldstart.py:52–60` requires D02 and D03 in both authoring fingerprints and exact detail manifest/view sets. The archived R47 rejection evidence in `production/input_detail_guard_checks_R47.json` covers those failure cases. I did not rerun those checks for R49 because the guarded code is unchanged.

## Scope

This review covers source structure only. The R49 geometry/material validation, full manifests, paired visual review, and original-source cold replay remain separate evidence gates. No full-cycle or runtime claim follows from this review.
