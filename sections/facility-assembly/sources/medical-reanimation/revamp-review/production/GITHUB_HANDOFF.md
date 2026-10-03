# Open the reanimation overhaul from another environment

Published review branch: `codex/reanimation-room-publish-20261001`.

The editable scene is `sections/facility-assembly/sources/medical-reanimation/module_overhaul_R2.blend`, scene `REANIMATION_EDIT_LOCAL`. Use Blender 5.2.2 LTS or newer. The other scene is the read-only linked assembled-map reference. The canonical map, original medical module, approved spawn input and interface remain unchanged.

## Download

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --single-branch --depth 1 --branch codex/reanimation-room-publish-20261001 https://github.com/CameronNel/critical-shift.git
cd critical-shift
git lfs install --local
git lfs pull --include="$(paste -sd, sections/facility-assembly/production/MINIMAL_PULL.txt)"
```

The 25 existing map libraries use the repository's existing Git LFS storage. The additive R1/R2 scenes and all overhaul review PNG/JPG files are ordinary Git blobs on this branch, so those files arrive with the clone. This scoped storage choice follows failed LFS upload authentication and failed release attachment requests; it does not alter any native source or image bytes. No GitHub release is required.

The accepted R2 native SHA-256 remains `39007192eef36f87c5299933e3a2a4f3462791871144c349a580ba2d9d322487`. Art/source evidence was committed locally in `be772bd5550d8f9a94f387575ba146a598209c7a`. The original authoring branch, `codex/reanimation-room-revamp-20260930`, and its full Git bundle preserve that history. GitHub rejected its unpublished historical LFS pointers, so the publication branch consolidates the final room directory into a fresh commit based on current main. All 519 converted asset files retain their exact native bytes; review history remains in the room's evidence files. Existing downloadable source/review archives and the Git bundle predate the publication handoff.

## Inspect

- Final images: `revamp-review/production/renders/cycle-17/` (24 labelled views at 1067 × 600).
- Earlier useful renders, original/spawn references, concepts, diagnostics and failed reviews remain under `revamp-review/`.
- Final acceptance: `revamp-review/production/acceptance.json` and `RUBRIC.md` (91.7/100, every category and camera gate passed, zero critical findings).
- Source/dependency checks: `objective-verification.json`, `cold-verification.json`, `cold-render-comparison.json` and `portable-delivery-verification.json` beside the acceptance record.
- Fresh GitHub checkout: `github-checkout-verification.json` records unchanged native bytes for all 519 scene/image assets, 25 resolved libraries, 124 valid file images and 1,366 editable objects. The existing portable verifier passed without saving the source after local Git LFS initialisation.

Verify a checkout without saving the scene:

```sh
blender -b --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python sections/facility-assembly/sources/medical-reanimation/verify_delivery.py -- --root "$PWD" --report /tmp/reanimation-checkout-verification.json
```

This is an additive art/source review branch. Automated PR review, triangle/draw-call budget validation, owner art approval, promotion into the map and runtime integration are separate outstanding gates. Native geometry inventory recorded 435,130 evaluated mesh triangles; that is authoring evidence, not a measured runtime budget or draw-call pass. No agent merge or main-map promotion is included.
