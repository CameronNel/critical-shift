# Compliance dock — persistent agent handoff

Branch: `codex/compliance-dock-overhaul-20261001`. Draft PR: https://github.com/CameronNel/critical-shift/pull/66. One primary author, root. No merge or canonical-map promotion is authorized by this handoff.

## Current checkpoint

Published native: `sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend`, editable scene `COMPLIANCE_EDIT_LOCAL`. Current f02 native SHA-256: `dc608cae0a42303e614f2db3dc0cd9d50e4366dc738ac57c35957c6df34e0331`. The full room exists and links a read-only canonical map scene. The map still selects its original dock module. Neither the selected module nor map/spawn/interface was overwritten.

The independently approved local style slice is s10; this is not approval of the full room. First complete full-room review FAIL: conservative eight category scores 87/85/82/81/80/94/80/84. All 26 labelled 1067×600 beauty frames plus four approved spawn references were opened by five visual disciplines; the independent technical critic inspected native geometry and relevant actual images. Scanner hero framing, detached fittings, duplicate exposed surfaces and fragmented cloth mapping prevent acceptance. See `FULL_CYCLE_01.json`, `critics/full-c01-*.md/.json` and retained raw probes.

F03 repair build stopped before saving because an inherited webbing strap is a curve. The corrected recipe explicitly converts that object while retaining its name and pose. F04 rebuild is underway. Current recipes may therefore describe newer repairs than the active f02 native. Read `build-state.json` and `TASK_STATE.md` before opening or building. No f03 native exists; its failed log is preserved.

## Reproduce and inspect

Read repo `AGENTS.md`, `MAP.md`/`MAP.json`, uploaded `.agents/skills/blender-headless/SKILL.md` and `.agents/skills/blender-uv-texturing/SKILL.md`, global art/reference/build protocol, `revamp/scenery/OVERHAUL_BRIEF.md` and local `RUBRIC.md`.

Clone or fetch this branch, not main. Install Git LFS locally and hydrate the required linked map dependencies before cold opening; an LFS pointer is not a Blender payload. Use a recent Blender supporting the authored native format (authoring used Blender 5.2.2 LTS). New overhaul natives, recipes and PNGs are ordinary Git objects; inherited inputs retain the repository's existing LFS policy.

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
