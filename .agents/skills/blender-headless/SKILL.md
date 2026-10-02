---
name: blender-headless
description: Use for Critical Shift Blender scene or asset authoring, bpy scripts, materials, lighting, headless rendering, reference matching and visual QA. Not for unrelated runtime code or documentation-only tasks.
---

# Critical Shift: headless Blender

A shared workflow for Codex and Claude. Preserve good modeling judgment; add
reliable project discovery, measurable constraints and honest visual review.
This skill is an entrypoint, not a replacement art bible or a new build system.

## Read the existing authority first

1. Read [AGENTS.md](../../../AGENTS.md) and the current task scope.
2. For map work, read [MAP.md](../../../MAP.md) and [MAP.json](../../../MAP.json).
   Resolve current entrypoints from these files, not from remembered filenames.
3. Read [ART_DIRECTION.md](../../../design/ART_DIRECTION.md),
   [ART_REFERENCE_INDEX.md](../../../design/ART_REFERENCE_INDEX.md) and
   [AUTONOMOUS_SECTION_BUILD_PROTOCOL.md](../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).
4. Read the affected section's `AGENT_READ_FIRST.md`, scenery specification and
   current production state. Inspect the existing build, render and validation
   scripts before choosing commands. For runtime exports, also follow the
   authoring-to-runtime boundary in the existing architecture plan.

Existing authorities and stricter section requirements take precedence over these
convenience instructions. If the task and current authority disagree, surface the
conflict; do not silently change the art target, source ownership or acceptance bar.
Do not treat an old handoff or an unreviewed asset as current approval.

## Adaptive effort, identical quality standards

Choose effort from the task and observed defects, not a claimed model identity.
All agents may choose their own modeling techniques. No mandatory rewrite of
working scripts, universal bevel recipe or unsolicited overhaul of approved art.

- **Small, bounded edit:** inspect a baseline, make the focused change, run the
  affected existing checks, render the affected views and inspect the images.
  Reuse valid cameras and section tooling; do not create a second QA system.
- **Complex, uncertain or reference-sensitive task:** record dimensions and
  interface constraints, block out the changed area, review multiple views,
  diagnose specific defects and iterate before adding detail.
- **New room, major environment pass or formal acceptance:** follow the full
  existing production protocol, including the style-validation slice, mandatory
  cameras, review cycles, specialist critics where available, support-contact
  validation and cold-start checks. The small-edit path is not a shortcut to
  declaring a room complete. Preserve stricter current section/map thresholds.
- **A regression or unclear geometry:** load the diagnostic reference, isolate
  the failing property and repair it. Stop and record a blocker when the tool,
  input or review capability is unavailable; do not loop without a defect target.

## Working loop

1. Establish the current source, permitted outputs, affected section and baseline.
   Preserve unrelated working-tree changes. Do not hydrate large assets for a
   documentation-only task.
2. Use real dimensions or explicitly labeled estimates. Record origin, orientation,
   bounds, support targets and clearances where relevant. Preserve existing room
   interfaces and world placement; do not substitute generic furniture dimensions
   for measured project constraints.
3. Build/edit with the existing headless Python/CLI pipeline. Use checkpoints
   before risky changes and retain procedural source where it is part of the asset.
4. Run applicable numerical checks, then render named views from the actual scene.
5. Open the resulting images with the available vision/image-reading tool.
   Identify visible defects, fix the highest-impact ones and compare the same views.
6. Save the intended editable deliverable only after the applicable checks.
   Update existing production state with commands, evidence, defects and blockers.

A successful Python process, saved `.blend`, geometry count or finished render
is not visual acceptance. Do not claim to have inspected an image you could not
open. If vision is unavailable, report **visual QA blocked**, not pass. Successful
agent self-review is not independent review or owner art approval.

## Load only the reference needed

- [Headless execution](references/headless.md): cloud preflight, safe CLI commands,
  LFS, version/renderer constraints and existing map verification.
- [Visual review and repair](references/visual-review.md): fixed-view comparisons,
  geometry diagnostics, reference matching, materials and lighting.
- [Integration guide](../../../design/blender-headless/README.md): shared discovery,
  what this installation does not change and maintenance checks.

## Non-destructive boundaries

Do not overwrite the canonical map, selected room modules, immutable caches or
frozen provenance as a side effect of diagnosis. Follow MAP.md's current ownership
and additive-overhaul/promotion process. Diagnostic material/camera changes belong
in a disposable copy or process and must not be saved over production assets.

Do not change runtime code, export contracts, packages, workflows, cloud settings,
permissions or repository merge rules merely to use this skill. MCP is optional;
a live Blender desktop is not a prerequisite. No third-party skill is installed
or executed automatically by these instructions.

## Handoff

Report changed and deliberately unchanged files; exact successful and failed
commands; inspected render paths; numerical check results; remaining defects;
current checkpoint; cold-start status when required; and independent review/merge
status. Keep technical, visual and runtime validation separate. Never substitute
one for another, invent scores or claim unmeasured performance.
