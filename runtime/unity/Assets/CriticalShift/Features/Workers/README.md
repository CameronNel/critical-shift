# Worker movement animation adapter

Uses the 49 exact action/take names authored on `claude/character-rig` at
`6792f25d89430c5b1ff701d37957f88f3ae20e8a`. That branch is unmerged. Its
`sections/spawn-room/blender/README.md`, `character_rig.py` and `character_clips.py`
remain the animation source. This feature does not copy or merge that authoring work.

## Import and bind

1. Export the actions with the rig branch's existing `render_rig.py` `EXPORT=<dir>`
   option, and import the FBX files into this Unity project's content folder. Keep
   the exact uppercase take names. Review scale/axes and configure a compatible
   shared Generic rig or verified Humanoid Avatar. Blender's forward +Y must become
   Unity forward +Z. The authored extra Belly, Pack and Tool bones need explicit
   import/retarget review; no Avatar configuration is silently selected here.
2. In the FBX Animation import tab enable **Loop Time** for all walks, runs, turns,
   idles, holds, `FALL`, `TURN_VALVE`, `RADIO` and `SHOVEL_DIG`. Disable it for the
   one-shots. `MovementClipInfo.For` is the complete loop catalogue. Apply import
   changes. All clips must be nonlegacy and have positive lengths.
3. Select the imported folder and run **Critical Shift > Workers > Create animation
   library from selected folder**. It finds FBX sub-clips and standalone clips by
   exact name, rejects duplicates/missing clips/wrong loop flags, and creates a
   uniquely named library. It does not rewrite import settings or assets. The
   library Inspector also has a validation button.
4. Add `WorkerMovementAnimator` to the worker. Assign its Animator and library in
   the Inspector; leave the Animator controller empty. This component is the sole
   animation writer. It creates a manual Playables mixer, disables root motion,
   and waits for the first movement sample. No Animator controller asset is needed.

## Feed the actual motion

The existing/future physical binding calls this once per visual frame before
Animator evaluation. Use **actual velocity**, including blocked movement and
carrying slowdown. Transform world velocity with the worker root's
`InverseTransformDirection`, not a rotating camera or animated hip bone:

```csharp
Vector3 local = workerRoot.InverseTransformDirection(actualWorldVelocity);
animationDriver.ApplySample(new MovementAnimationSample(
    local.x, local.z, local.y, grounded, MovementPose.Carry,
    yawDegreesPerSecond: measuredYawRate,
    animated: motionOwnerPermitsAnimation), Mathf.Min(Time.deltaTime, 1f));
```

`Right`/`Forward`/`Vertical` are metres per second; positive yaw is a right turn in
degrees per second. Supply the committed presentation context: `Free`, `Carry`,
`Shovel`, `Pickaxe`, `Push`, `Pull` or `Drag`. Ground contact and the animation-control
flag come from the physical owner. The sample's default struct is suspended.

Standing blends idle, forward/back/side walks, RUN and SPRINT. Diagonals blend the
corresponding axes. Forward gait transitions use the authored 0.63/1.4/2.6 m/s
speeds; carrying uses 0.50/0.96 m/s. Tool, push, pull and drag speeds also use the
authored values. Playback is bounded to 2.5x. Shared stride phase aligns the two
strides in RUN/SPRINT with the one-stride walks. Turn playback uses the authored
48 degrees per second. There are no per-frame arrays/lists in selection/playback.

Vertical motion selects jump then fall; grounded contact after at least 0.1 seconds
of air selects LAND for its imported duration. A new jump interrupts landing.
Short grounding gaps do not trigger LAND. Carry/tool context resumes afterwards.

## Committed actions and physical handoff

After the first animated sample, send an already authorized visual action:

```csharp
animationDriver.TryPlayAction(MovementClip.PICKUP, visualEventSequence);
// Held loops remain until a matching release or a newer action:
animationDriver.StopAction(visualEventSequence);
```

One-shots end after the imported clip length; loops remain until stopped. Increasing
nonzero sequences suppress duplicate and stale presentation events; a stale stop
cannot cancel a replacement. This is local visual replay protection, not a network
command admission system. Disable/re-enable clears the binding's sequence history;
the world binder must reject old-epoch events before calling this component.

Airborne motion cancels an action. An `Animated=false` sample immediately stops the
graph, disables the Animator and clears action/air/landing history. It retains the
event high-water mark until unbinding. The physical owner must suspend animation
**before** enabling ragdoll bodies, and disable those bodies **before** permitting
animation/recovery. `GETUP_FRONT/BACK` only present an externally approved recovery;
completion never changes health, claims or controllers. On disable the component
destroys its graph, restores the previous root-motion setting, leaves the Animator
disabled, and resets visual history. It has no subscriptions or static mutable state.

The worker physical/health owner, Interaction custody owner and host workflow remain
authoritative. No input, movement integrator, networking, actual ragdoll, grab/release,
tool visibility or first-person camera binding is installed by this animation adapter.

## Limits and verification

The source has no crouch clips, directional carry/tool runs, pull/drag idle, or
two-person carry animation. Pull/drag freeze their gripping gait pose at rest;
carry/tool clips use forward-authored motion in other directions. Those are explicit
art gaps, not invented animations. Full-body actions override locomotion, so a host
must restrict motion during interactions where feet should remain fixed. Real grips,
extra-bone transfer, foot contact, avatar compatibility and camera clipping require
native inspection. The source clips' documented get-up/suit contacts remain.

Runtime assembly: `CriticalShift.Features.Workers.Unity`, depends on UnityEngine and
base C# only. Editor assembly: `CriticalShift.Features.Workers.Editor`, depends on
that runtime assembly and UnityEditor. All new source and folders have `.meta` files.
No existing consumer/serialized identity was replaced or removed. Pure selector/tests
are linked into the existing offline NUnit suite; there is one canonical implementation.

See [task and execution evidence](../../../../../validation/MOVEMENT_ANIMATIONS.md).
Run `python runtime/dotnet/tools/verify.py` with .NET 8 for the offline checks.
Native tests in `Tests/EditMode/WorkerAnimationBindingTests.cs` exercise library
validation and ten Playables enable/suspend/disable cycles. They require the pinned
activated Unity Editor; the foundation runner does not establish this feature's
native acceptance. No gameplay gate, performance or human feel pass is claimed.
