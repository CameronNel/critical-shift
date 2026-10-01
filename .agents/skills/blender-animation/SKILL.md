---
name: blender-animation
description: Use for Critical Shift headless Blender animation, existing-rig posing, keyframes, F-curves, drivers, shape keys, NLA clips, loops and camera motion. Not for static scene edits or runtime animation-system code.
---

# Critical Shift: Blender animation

Headless adaptation of RobLe3's `blender-animation` module, not installation of
the full upstream plugin. See [provenance and changes](SOURCE.md) and [license](LICENSE).
Keep artistic judgment and existing animation intact; add targeted temporal review.

## Authority and scope

Read [AGENTS.md](../../../AGENTS.md) and the
[shared headless skill](../blender-headless/SKILL.md) once per task, including its
applicable art, section, map and runtime-export authorities. This specialist adds
animation guidance; it does not replace those rules or lower acceptance standards.
Load the references below only when the task needs them. Do not recursively reload
entrypoints already read for the same task.

Use for moving props, doors, mechanisms, existing character rigs, facial shape
keys, cameras and animated properties. Creating/replacing a rig, importing motion
capture or changing a runtime Animator/controller is not implied permission.
Discover the existing rig, clips and exporter before proposing those larger tasks.

## Preflight: identify what owns the motion

Record the input/checkpoint, Blender version, permitted objects/bones/properties,
Action and slot assignments, NLA tracks, constraints, drivers, rotation modes,
frame range, `fps` and `fps_base`. Inspect existing scripts and source ownership.
Preserve skeleton names, rest pose, object origins, world placement, clip names and
export contracts. Establish whether motion is in-place or root-motion driven from
the existing specification; do not invent that decision or a new frame rate.

Check whether Actions, mesh data or node trees are shared. Isolate a working copy
when an edit must not affect other users. Do not clear all animation data, sweep
all Action slots or rebuild an approved rig to make a bounded change easier.
Do not install dependencies, start MCP servers or enable untrusted Python execution
just to use this skill. Read-only review must not save over production assets.

## Choose the smallest suitable animation system

| Intent | Starting point, not a compulsory recipe |
| --- | --- |
| Transform or property motion | Key only the intended channels on their owning data |
| Constant-speed mechanism | Linear curves on the channels that need constant speed |
| Organic/stylized motion | Deliberate poses, timing, spacing, arcs and selective easing |
| Discrete state or blocked poses | Constant interpolation where a hold is intended |
| Facial deformation | Existing shape keys, or explicitly authored vertex deltas |
| Mechanical relationship | Scoped constraints/drivers with explicit coordinate spaces |
| Reusable/layered clips | Existing Actions/NLA, preserving slot ownership and blending |
| Camera motion | Existing shot framing, evaluated path/aim and stable orientation |

Read [animation patterns](references/animation-patterns.md) for keying, rotations,
loops, existing rigs, shape keys, drivers and Action/NLA safety.

## Adaptive working loop

1. Inspect a baseline and define the motion's intent, timing, contacts, loop policy
   and acceptance evidence. Reuse the project's current tooling and cameras.
2. For a small edit, change only the affected channels and review the affected
   interval. Do not force a full reblocking pass on an already good animation.
3. For new or complex movement, establish readable key poses and breakdowns first.
   Review silhouette, balance, arcs, contacts and gameplay readability before
   polishing interpolation, overlap or secondary movement. Exaggeration must fit
   the existing art direction, not a generic cartoon style.
4. Execute through the existing headless `bpy`/CLI pipeline. Checkpoint before
   changing rig state, constraints, shared Actions or baking. Use the APIs supported
   by the installed Blender version; never assume every version has `action.fcurves`.
5. Evaluate between keys, at contacts/transitions, and across any loop seam. Render
   a cheap frame sequence and inspect the actual images. Review at intended speed
   when playback is available; use the [temporal QA reference](references/temporal-qa.md).
6. Repair a specific observed defect and compare the same frames/settings. Increase
   diagnostic depth only for uncertainty, reference fidelity or detected defects.
7. Save the intended authoring output, preserving the editable source. Bake/export
   only when requested under the existing contract, then test the exported result
   separately. An authoring preview does not prove runtime correctness.

## Definition of done and handoff

A successful script, two keyed poses, a still render or a saved `.blend` is not
proof of satisfactory animation. Report technical checks, inspected temporal
imagery, real-time playback review and runtime/export checks as separate statuses.
A contact sheet can expose poses and intersections but cannot establish perceived
rhythm at speed. If playback is unavailable, state **real-time motion review blocked**;
if images cannot be opened, state **visual QA blocked**. Do not substitute a pass.

Report changed and deliberately unchanged files/channels; exact commands; frame
range and effective frame rate; Action/slot and root-motion decisions; evidence
paths and inspected frames; loop/contact results; unrun checks and remaining
defects; checkpoint; and independent review/merge status. Existing stricter section
requirements remain mandatory. This skill grants no self-merge permission.
