# Compliance dock — persistent agent handoff

Branch: `codex/compliance-dock-overhaul-20261001`. Draft PR: https://github.com/CameronNel/critical-shift/pull/66. One primary author, root. No merge or canonical-map promotion is authorized by this handoff.

## Current checkpoint

Published/editable native: `sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend`, scene `COMPLIANCE_EDIT_LOCAL`. Current f06 SHA-256: `8d7588a5513a984a96c086e21fd12d3b38f65a51cf08dbae1464bb3b044934f7`. The full room links a read-only canonical map scene. The map still selects its original dock; protected map/module/spawn/interface/accepted input hashes remain exact.

The local style slice s10 independently passed; full-room cycle1 failed with conservative category scores87/85/82/81/80/94/80/84. See `FULL_CYCLE_01.json`, six critic reports and retained raw probes. F04 diagnosis identified exposed rear-lintel overlap,25mm motor/plate penetration, two webbing gaps above5mm and distorted textile mapping. All evidence remains available; preformal previews are not full review cycles.

F05 repaired the measured construction defects, true gate openings/caster forks, moving-leaf pressed panels, cloth bearing/mapping and physical oblique lights outside the cart corridor. It saved below all planning targets. Static validation then found15 new moving-leaf support claims naming immediate leaves instead of registered supported ancestors. F06 is a bounded metadata-only repair: physical leaf parents, every matrix, mesh, UV and material remain unchanged from f05. Exact lineage is stored in the native and build-state.json; repair_support_metadata.py and immutable f05/f06 checkpoints preserve reproduction. The full builder contains the same corrected ancestry behavior.

Current counts:1278 objects /433934 evaluated triangles /1119 material submeshes /36 used local material datablocks; all three planning targets pass. Static validation-full-f06.json:7 checks PASS,0 failures,1 conservative inherited-geometry warning,5 explicit unverified checks. Cycle2 full27-view600p renders are in progress; a fresh independent technical critic is inspecting this frozen source. No current full-room acceptance is claimed. Read `build-state.json` and `TASK_STATE.md` before building.

## Reproduce and inspect

Read repo `AGENTS.md`, `MAP.md`/`MAP.json`, uploaded `.agents/skills/blender-headless/SKILL.md` and `.agents/skills/blender-uv-texturing/SKILL.md`, global art/reference/build protocol, `revamp/scenery/OVERHAUL_BRIEF.md` and local `RUBRIC.md`.

Clone or fetch this branch, not main. Install Git LFS locally for normal checkout filters. The GitHub LFS download endpoint returned403 in this environment. Required dependencies are therefore also included in ordinary-Git SHA-verified compressed parts; run `python3 sections/facility-assembly/sources/compliance-dock/restore_dependencies.py` before cold opening. This restores exactly the original 25 native files from their recorded bytes, rejects different edited files, and does not construct or edit the map. An LFS pointer is not a Blender payload. Use a recent Blender supporting the authored native format (authoring used Blender 5.2.2 LTS). New overhaul natives, recipes and PNGs are ordinary Git objects; inherited inputs retain the repository's existing LFS policy. The portable dependency package mirrors exact payloads without changing that policy or canonical source.

From the repository root, with `BLENDER` set to the Blender executable:

```bash
"$BLENDER" -b --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/overhaul_dock.py -- --stage full --revision next
"$BLENDER" -b --disable-autoexec sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend --threads 1 --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/validate_dock.py -- --expected-stage full --interface sections/facility-assembly/sources/compliance-dock/contracts/interface.json --output /tmp/dock-validation.json
"$BLENDER" -b --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/render_dock.py -- --out new-review-directory
```

Use a fresh render output directory; the renderer refuses silent image reuse. It appends the local editable scene without saving the input. `--cold` performs a full native open; `--source` accepts an immutable checkpoint for local-scene evidence. Archival `.blend` links were authored relative to the room root: restore a checkpoint copy to the room-root filename in an isolated checkout, never overwrite an active review source. See checkpoint README.

Current camera repair recipe adds one office-front elevation and rebaselines the obstructed scanner/wide and wall evidence views. Every temporary hidden part is declared in each manifest. Do not compare a new camera against an old one as if its transform were unchanged. Freeze the complete usable recipe for the final two materially stable cycles.

## Remaining completion gates

Each of eight independent categories must be strictly above 93, with zero critical failures and all objective/support checks. Minimum four complete full-room review cycles, final two materially stable, actual checker/neutral inspection and final cold-open/render comparison remain mandatory. Source planning targets: <=450000 evaluated triangles, <=1150 material submeshes, <=36 used local material datablocks; these are not engine budgets.

Do not inherit a PASS from counters or successful save. Root is repairing real screen/frame/floor geometry and bearing paths, continuous textile coordinates, contextual wear/handover and fitted inspection lights. Continue from actual source and critic findings. Runtime material equivalence, FPS/draw calls, interaction/collision/navigation and map promotion remain unmeasured. No owner art approval or merge is claimed.

All useful actual images remain under `renders/`, with hashes/settings/camera matrices/source SHA in manifests. `render-gallery.html` indexes the images without editing them; original interrupted and failed black/bright diagnostics are explicitly retained. `index_renders.py` rebuilds that gallery.

## Verified GitHub transfer

Commit `65a454a` was fetched from GitHub into an isolated checkout. Its ordinary-Git dependency parts restored all25 exact canonical native payloads from their HEAD LFS pointers. The fetched checker cold-opened the fetched f04 native with1258 local editable objects,25 relative/resolved native libraries and119 packed/present images: PASS. Source hash matched and did not change. This verifies native portability, not the still-pending final render comparison. Exact reports/logs: `remote-verification/github-package-proof.json` and adjacent files.
