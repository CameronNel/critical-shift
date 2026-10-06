# Headless animation patterns

Adapted from the pinned RobLe3 module described in [SOURCE.md](../SOURCE.md).
These are selective recipes, not a replacement for the installed Blender API or
Critical Shift's existing rig/export conventions. No code runs on skill discovery.

## Timing and channel ownership

Preserve `scene.render.fps` and `scene.render.fps_base` unless changing timing is
explicitly in scope. Effective FPS is `fps / fps_base`; a frame difference of D
represents D / effective_FPS seconds. A range of N rendered frames contains N
samples, whereas the first-to-last key separation is N - 1 frame intervals.
Retiming keys and changing playback FPS are different operations.

Key properties on the data that owns them: object transforms, pose-bone channels,
camera/light data, shape-key blocks or material node inputs. Inspect existing
animation and drivers first. Do not key a constrained/driven output blindly; use
its intended control. Do not change unrelated channels or all objects in a scene.

### Bounded key insertion example

This helper inserts only local X-location keys. Call it only after approving the
specific target, frame range and shared-Action ownership. It does not clear old
keys, set interpolation, change FPS, bake constraints or save the scene. Existing
keys at the same frames on that channel can be replaced, intentionally.

```python
import math


def key_local_x(scene, obj, keyframes):
    """Insert finite, integer-frame X keys and restore the evaluation frame."""
    points = list(keyframes)
    if not points:
        raise ValueError("At least one keyframe is required")
    frames = [frame for frame, _ in points]
    if any(type(frame) is not int for frame in frames):
        raise ValueError("This example requires integer frames")
    if len(set(frames)) != len(frames):
        raise ValueError("Duplicate keyframe numbers")
    values = [float(value) for _, value in points]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Keyframe values must be finite")
    previous = (scene.frame_current, scene.frame_subframe)
    try:
        for frame, value in sorted(zip(frames, values)):
            scene.frame_set(frame)
            obj.location.x = value
            if not obj.keyframe_insert(data_path="location", index=0, frame=frame):
                raise RuntimeError(f"Key insertion failed at frame {frame}")
    finally:
        scene.frame_set(previous[0], subframe=previous[1])
```

This is an instructional example, not a transaction or general rig-safe editing
library. A failure can leave earlier inserted keys in the working copy; discard
that copy or restore its checkpoint before retrying. Follow with scoped curve
configuration and evaluated temporal QA, not an automatic success claim.

## F-curves, easing and rotations

Resolve the intended owner and assigned Action slot first. In layered Actions,
find that slot's channel bag in the relevant layer/strip and filter by exact data
path and array index. In a supported legacy Action, use its legacy F-curve API.
Do not collect every channel bag and edit every F-curve as a compatibility shortcut.
Do not mutate a shared Action without an explicit shared-edit decision or isolation.

Interpolation describes the segment leaving a key. To change a landing interval,
edit its starting key, not merely the last key in the Action. Select Linear for a
constant-rate channel, Constant for an intentional hold, and suitable handles or
easing for the requested spacing. Bezier does not automatically create convincing
physics; auto handles can overshoot or soften a contact that should be crisp.

Preserve the rig's rotation mode unless conversion is explicitly scoped and tested.
A continuous single-axis Euler curve can encode multiple revolutions; crossing
180 degrees does not inherently require a quaternion conversion. For quaternion
animation, maintain sign continuity and inspect the evaluated path. Equivalent
start/end orientations alone cannot encode a full spin. Test intermediate frames
for unexpected reversals, gimbal artifacts, track-axis changes and camera flips.

## Loop construction

Choose N unique playback samples at the existing FPS. For a periodic curve starting
at F, place the closure key at F + N, and normally render F through F + N - 1. Keep
the closure key for authoring, rather than accidentally playing a duplicate endpoint.
Respect a different existing exporter convention and verify that specific contract.

Check evaluated pose AND velocity continuity near the seam, not just equal endpoint
values. Intentional sharp events need their own stated acceptance rule. Root motion
may accumulate displacement rather than return to the origin; compare against the
expected cycle displacement/orientation instead of forcing a stationary root.
Apply Cycles modifiers only to the intended curves, and inspect how NLA repetition,
blend regions and driver/constraint evaluation affect the final result.

## Existing rigs and character movement

Read the rig's control and IK/FK conventions. Animate intended controls, not a
mixture of controls and driven deform bones. Preserve rest pose, hierarchy, bone
names, scale and rotation modes. Review a pose switch for discontinuities before
baking or transferring a clip. Creating a replacement rig is a separate scoped task.

For locomotion, establish contacts, passing poses, stride length and intended speed.
Check supporting feet in world space, body balance, joint limits, penetrations and
root displacement. For interactions, inspect grip/contact throughout the motion.
Use anticipation, follow-through, overlap and silhouette deliberately. Do not add
squash/stretch, idle noise or broad cartoon easing to realistic art automatically.
This module is not a complete mocap-cleanup or Rigify-specific retargeting toolkit.

## Shape keys and drivers

Reuse approved shape keys where available. A new named key identical to Basis is
not a completed expression: author real vertex-coordinate deltas programmatically
on a working copy and verify the deformation. Preserve topology/vertex order and
inspect neutral, extremes and combined shapes. Do not prescribe a universal viseme
set; use the actual facial rig and destination contract.

Define driver variables, dependency direction and coordinate spaces explicitly.
A source world-space transform is not interchangeable with a destination local-space
channel. Use restricted expressions appropriate to the task; do not enable global
script auto-run or alter application security preferences. Evaluate drivers and
constraints after changing the scene frame; no viewport refresh is required as a
workflow step. Report unsupported execution instead of bypassing security.

### Runtime-facing motion is authored in seconds

Motion that must run in an engine at any display rate (blinking lights, screen cycles, pulses, shimmer) is authored as drivers
of scene time in seconds, `T = frame*fps_base/fps` (read `render.fps` and `render.fps_base` as driver variables), never of the raw
`frame` and never as keys tuned to one fps. Keep expressions short (Blender caps them near 255 characters; split long schedules over
helper properties). Drivers do not export, so also publish a seconds-based runtime behaviour spec (period, formula, inputs) and
check frame-rate independence by evaluating the same real times at several rates. Reference implementation:
`sections/reactor-room/production/overhaul-R1/scripts/` (`crk.drv`, `fps_independence_check.py`, `cr_runtime_spec.py`).
Frame-count rates only for authored clips whose source is frame-based (record fps and duration in seconds).

## Actions, NLA, baking and export

Inspect active Action, slot, tracks, strip timing, influence, blend/extrapolation,
mute/solo and tweak-mode state before editing. Use explicit names from the project.
Avoid duplicate NLA tracks on repeated runs. Preserve the relevant slot assignment
when moving an Action to a strip on versions that support slots; verify evaluation
before detaching the active Action. Do not allow active Action and strip to apply
the same motion twice. Do not clear animation data to perform a push-down.

Keep editable control animation. If baking is requested, use a separate destination
with explicit objects/bones, channels, frame range and sampling. Compare evaluated
transforms before/after at keys and between keys, including loops and contacts.
Drivers, constraints and NLA do not necessarily survive every export format. Follow
the established exporter and re-import/runtime validation procedure; never change
the engine, skeleton or root-motion contract to make an export appear successful.
