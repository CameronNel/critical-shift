# Temporal review for headless Blender

Use with the [animation skill](../SKILL.md) and existing section/render tools.
This is an animation extension, not a second production acceptance system.

## Capture evidence, not just key poses

Preserve baseline and result at the same frame rate, cameras, crop, lighting and
preview settings. Use a working copy for review cameras/material overrides. Render
through the existing headless renderer; a desktop viewport/OpenGL capture is not a
prerequisite. Prefer frame sequences so partial render failures remain diagnosable.
Encode a review video only with already available, authorized tools.

Choose frames from the motion's events, not only evenly spaced samples. Include
start/end, anticipation, extremes, contacts, direction changes, transitions,
intermediate poses and both sides of a loop seam. Label contact-sheet images with
frame numbers. Use close-ups or additional views only when a defect is occluded.

Inspect the actual output images with the available image-reading tool. Play at the
intended speed when the environment supports review playback; slow playback can
supplement, but cannot replace, judging the target speed. A contact sheet alone
cannot prove convincing rhythm, impact or absence of fast flicker.

## Targeted checks

| Property | Evidence to inspect |
| --- | --- |
| Timing and spacing | Holds, acceleration, impacts, readable anticipation/recovery |
| Silhouette and arcs | Readable poses and movement between them, not just endpoints |
| Contacts | Foot sliding, floating, grip drift, penetrations, support changes |
| Rotations/cameras | Flips, sudden roll, target-axis changes, motion outside frame |
| Loops/transitions | Pose/velocity seams, duplicate endpoints, blend pops |
| Facial/secondary motion | Neutral pose, extreme/composite shapes, lag and overlap |
| Evaluated rig | Constraints/drivers/NLA contributions, not raw key values alone |
| Export | Same clip timing, axes, scale, skeleton and intended root displacement |

Numerical checks should use evaluated scene data after `scene.frame_set(...)`.
Where available, use the dependency graph's evaluated objects/meshes, appropriate
world/local transforms, and release temporary meshes after inspection. Raw object
location or F-curve samples alone may omit parents, constraints, drivers or NLA.

Record finite transforms, requested clip ranges and sample coverage. Measure contact
drift over declared contact intervals, and loop position/orientation/velocity against
its actual policy. Establish tolerances from project scale/specification before
checking; there is no universal acceptable foot-slide distance or generic score.
Sampling is not continuous collision proof. Increase density near fast motion,
contacts or suspected discontinuities; do not report untested intervals as clean.

## Repair without resetting the animation

Classify a defect: pose, timing, interpolation, rig/constraint, Action/slot/NLA,
contact, camera, deformation, or export. Change the smallest responsible property.
Rerender the same interval and confirm both the fix and preservation of surrounding
motion. Preserve a good baseline and stop with a specific blocker rather than
performing an unbounded polish loop or rewriting approved work.

## Report separate statuses

Report technical evaluation, visual sequence inspection, real-time playback review,
and export/runtime validation separately. Name actual inspected frames and paths.
If a capability is unavailable, report blocked/not run for that capability. Do not
call a partial review complete, infer video quality from a single image or treat a
successful render as owner approval. Existing independent review and merge rules
remain unchanged.
