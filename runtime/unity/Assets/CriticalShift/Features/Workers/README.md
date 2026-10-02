# Assignable worker movement and scene interactions

Unity 6000.4.3f1, Built-in pipeline. Gameplay scripts bind to the 49 named takes;
Blender animation sources, keyframes, exports and clip assets are **untouched**.
The animation work is still in progress. Current code calibration comes from
`claude/character-rig` revision `6792f25`; final visual/contact acceptance requires
finished assets and a native Unity run.

## Map binding workflow

Open `runtime/unity` in the pinned activated editor. Select exactly one worker as
Local Input; other workers need a separately implemented transport/input adapter. Canonical Application and seven
Domain DLLs are included under `Assets/CriticalShift/Plugins/Rules`; their importers
use explicit references. After changing pure rules, rebuild them from the repository
root with `python runtime/tools/build_unity_rules.py` using the pinned .NET SDK.
The build manifest detects stale source/DLL pairs. Do not copy rule source into Unity.

1. Use **Critical Shift → Scene bindings**. Select the worker root and choose **Bind
   selected worker**. Assign the final animation library when ready. The tool adds
   a separate capsule root, visual child, camera, grip, movement, crouch and ragdoll
   components and resolves
   existing bone names; it does not edit a clip, Avatar or character mesh.
2. Build/assign ragdoll joints and limb colliders using Unity's Ragdoll Wizard.
   Assign the pelvis and all ragdoll Rigidbody/collider references. A complete
   ragdoll is required. Assign suited/bare meshes and local head meshes separately;
   the local camera excludes the chosen head layer while other cameras can see it.
3. Select cargo, tools, carts or body markers and bind the appropriate physical
   object kind. Assign its actual Rigidbody and grip anchor. Body markers need the
   represented worker and the pelvis Rigidbody, with colliders under the marker's
   hierarchy so raycasts find it. Tools use the worker's Tool-bone socket. Enable
   **Allow assistance** on shared cargo/body objects and assign the second grip.
   Choose **Shovel** for the bonk shovel. Binding adds BonkShovel, a dedicated
   spatial AudioSource and the supplied tin-bonk sound; its Rigidbody must be on
   the bound root. Existing shovels need this binding step once.
4. Bind buttons, levers, valves, doors, service ports, aid points and suit lockers.
   Place the contact marker at the actual reachable handle, ordinarily chest height.
   Assign moving parts; doors require a collision-enabled Rigidbody/HingeJoint.
   Set the component's Operation to the intended action. Reanimation stations need
   a patient, chamber/exit anchor and a connected service port.
5. Bind production machines/reactors. A machine root owns its slot and authored
   recipe/definition. Additional control markers reference that root and choose a
   typed ProductionAction/ReactorAction plus the animation Operation: e.g. Insert,
   Button, Lever, ValveTurn. Material containers also need MaterialBinding. Insertion
   requires the held container within 0.8 m of a clear slot; slot overlap/path checks
   prevent pushing cargo through a wall. The collider layout must leave the slot free.
6. Run **Wire scene references**, then **Validate scene bindings**. Each scene has
   one FacilitySceneHost with explicit worker/target arrays. Duplicate object IDs,
   missing references, unsupported operations and incomplete clips fail validation.
   Duplicated prefab instances need distinct serialized identities; clearing an ID
   in the Inspector regenerates it through OnValidate.

When animations are finished, use the existing **Workers → Create animation library
from selected folder** command on their imported folder, or assign the 49 clips
manually to WorkerAnimationLibrary. This creates a binding asset and validates names
and loop flags; it does not rewrite import settings. Preserve +Z Unity forward,
+Y up, metre scale and compatible skeleton/Avatar mapping. Remove the Animator
controller because WorkerMovementAnimator owns its manual Playables graph.

## Controls and explicit calls

| Control | Behavior |
| --- | --- |
| WASD / mouse | Move / look; measured displacement drives playback |
| Shift / Alt | Sprint / walk, with carried/tool/hauling limits |
| Ctrl / Space / B | Crouch / buffered short jump / slow brace |
| F | Pick up; assist an existing tagged carry at the pickup cue |
| E | Use the looked-at target's Operation; hold for valve/tool loops |
| G / V | Release / place at the authored release cue |
| T / Alt+T | Chest / underhand throw with authored default velocity |
| C + mouse | Rotate held cargo |
| Left mouse | Swing the held bonk shovel; confirmed contact knocks another worker down |
| P / R | Point/ping / hold radio pose; pingEffect receives the hit position |
| Tab | Read detached machine/material/control status |
| Escape | Release cursor and cancel pending input actions; Escape, Enter or a click resumes |

`WorkerController.StartAction(target, operation)` is the same bounded scene action
entrypoint for a scripted host caller. It rejects downed, airborne, busy, distant
or incompatible use. Rigidbody state, worker identity, hazard identity, tool grip,
materials, recipes and control intentions remain explicit scene assignments.
Radio here supplies the pose; the voice transport is still an open project decision.
Held actions end when their initiating key/button is released; unrelated held keys
cannot prolong a valve, radio or digging action. Scripted loops use explicit
`CancelSceneActions()`. Returning from application focus loss requires an explicit
resume; the resume click is consumed before gameplay input. Reachable targets show
a use/inspect prompt and feedback expires after 3.5 seconds.

Look, ping and reach queries exclude the worker's own colliders and carried object,
retain solid-wall obstruction, and use caller-owned 64-hit buffers. A saturated
query cannot establish a target or clear reach. Changing a primary grip between
carry/push/pull uses the existing accepted lease rather than trying to claim the
same cart again.

## All 49 clip routes

| Trigger/context | Exact clips |
| --- | --- |
| Free standing and forward motion | IDLE, WALK_F, RUN, SPRINT |
| Backward/lateral motion and standing yaw | WALK_B, WALK_L, WALK_R, TURN_L, TURN_R |
| Tools at rest/in motion | HOLD_SHOVEL, RUN_SHOVEL, HOLD_PICKAXE, RUN_PICKAXE |
| Jump anticipation, flight and contact | JUMP, FALL, LAND |
| Pickup, carry, placement/release/throws | PICKUP, CARRY_IDLE, CARRY_WALK, CARRY_RUN, PLACE, DROP, THROW_UNDER, THROW_OVER |
| Cart/body custody | PUSH_IDLE, PUSH_WALK, PULL_WALK, DRAG_BODY |
| Facility controls, service, signals | PRESS_BUTTON, PULL_LEVER, TURN_VALVE, HOLD_VALVE, OPEN, INSERT, CONNECT_PORT, POINT, RADIO |
| Minor impact directions and safe physical recovery | STAGGER_F, STAGGER_B, STAGGER_L, STAGGER_R, GETUP_FRONT, GETUP_BACK |
| Suit/cabinet workflow | SUIT_UP, LOCKER_EXIT, REANIM_IDLE, REANIM_JOLT, REANIM_EXIT |
| Shovel work | SHOVEL_DIG |

All names have a code route. This table is not proof of final imported-clip behavior.
No additional takes are invented. Crouching is a procedural hip/leg IK overlay on
current locomotion; it needs the seven assigned leg/hip transforms. Tool and hauling
movement directions are limited to those authored. Grip alignment, procedural crouch,
hands, capsule size, camera and ragdoll behavior require native review.

## Calibration and authority

Authored free speeds: forward walk/backward 0.63 m/s, sides 0.40, run 1.4 and sprint
2.6. Tool run is 1.2; carry walk/run 0.50/0.96; push/pull/drag 0.60/0.50/0.33.
Standing turns are authored at 48 degrees/s. RUN and SPRINT contain two strides.
The shared gait clock divides actual velocity by the weighted stride-distance vector
of the visible clips, including blend smoothing. This preserves the blended floor
speed; the earlier average-frequency clock did not. Individual blended foot contacts
still need native inspection; this is not a foot-locking guarantee.

A jump begins with the grounded anticipation pose and takes off at 7/14 of the
imported duration. Coyote/buffer defaults are 0.10/0.15 s. Gravity, acceleration,
capsule size, crouch height, jump height and sensitivity are Inspector settings.
The imported length controls action timing. WorkerController.contactTimings overrides
normalized interaction cues for final calibration **without modifying animations**.
One-shot and loop clocks restart together with the action clock. A jolt returns to
REANIM_IDLE until the host authorizes exit.
Cancelled jump anticipation clears both motor and visual jump state. Held action
clocks skip missed loop cycles after a frame hitch instead of queuing a later burst
of operations; one-shot cue crossings still execute once.

FacilitySceneHost composes one WorldSession. Commands use its current epoch, shared
per-worker sequence and terminal receipts. Production/reaction outcomes, worker
awareness/suit/recovery, control revisions and object claims stay in canonical rules.
SceneTarget.Apply performs only the committed physical/cosmetic projection. Effects
must not call back to mutate authoritative quantities or health.

Carrying applies bounded forces and keeps collisions with the map. Timeout,
disconnect, knockdown, obstruction and generation-specific attachment failure clean
up holds and restore collision pairs. Tagged two-person carrying keeps one primary
and one helper under one generation; helper loss, including a broken secondary
grip, preserves the primary, primary loss
or expiry frees both. Insertion requires the helper to release first. Neither actor
can hold a second object. The two configured grip points apply separate force limits.

## Bonk shovel

Left-click starts a host-approved 0.70 s swing, with 0.18 s wind-up and a strike
window ending at 0.32 s. The next swing is allowed 0.95 s after the previous start.
The procedural grip/arm pose layers wind-up, strike and follow-through onto the
existing held-tool pose. First contact recoils directly to rest. It changes no
animation source, clip or Animator controller. **E** still performs shovel work
at a bound DigSite using its existing animation and cue.

The host sweeps a bounded blade volume and checks solid obstruction before
applying a hit. The first contact consumes that swing; a wall blocks a worker
behind it. Player contact uses canonical Knockdown, releases the victim's held
claim and enters their existing ragdoll with a bounded impulse. A conscious victim
remains conscious and can crawl/brace; recovery is permitted after 2 s plus the
existing quiet-motion/clearance checks. Hitting an unconscious worker does not
restore consciousness. Misses are silent; confirmed player or solid-object contact
plays the original 0.54 s tin-bonk sound.

Swing ownership requires the current exclusive shovel lease. Pause, cancellation,
incapacitation, release, disconnect or expired ownership stops the action and
restores ordinary dynamic tool carrying. Final rig contact alignment, physical
feel and scene audio balance need a native Unity playtest. See
[bonk task and evidence](../../../../../validation/BONK_SHOVEL.md).

## Ragdoll authoring and controls

In **Critical Shift > Scene bindings**, bind the worker, then run **Build selected
ragdoll physics**. It reads the Humanoid or exact generic bone names and creates
16 weighted limb bodies, capsule shapes, 15 limited CharacterJoints and collision
relays. The pelvis stays free; the motion root stays upright at unit world scale
with a CharacterController and no Rigidbody. The builder preserves bone transforms
and animation files. Elbow flex axes derive from the calibrated hanging A-pose;
knees bend backward. Rebuilding reuses components. Bind the worker as a Body object
for dragging/carrying; its body/contact and two grip anchors use the physical pelvis.

The default profile is 70 kg, 12 m/s linear and 18 rad/s angular motion bounds,
a maximum impact velocity change of 7 m/s, 12/4 solver iterations and a 0.2 s
recovery blend. Inspector tuning has finite bounds; manually assigned body mass
must total 10–200 kg. All owned bodies and solid shapes must be declared. Supported
shapes are box/sphere/capsule; the limb graph uses CharacterJoint. Unbounded/foreign
joints, undeclared solid geometry and a scaled or pitched root fail validation.

Knockdown suspends playback and disables the capsule before enabling limb physics.
It preserves measured motor velocity and sampled limb/angular motion. Additional
impacts preserve active motion, with bounded aggregate impulse. Normal closing speed
classifies hazards; tangential/receding contact does not create a knockdown. A worker
uses one hazard identity across its limb relays, bounded observation cooldowns and
canonical episode/receipt fences. Broken/disabled bodies or non-finite motion stop
physics and latch the adapter fault. Host synchronization stops the world on an
unexpected physical binding failure. Teardown freezes limbs and restores captured
collision policy; map collisions remain enabled during carrying.

An alert downed local worker uses WASD to crawl (default 0.25 m/s), B to brace,
H/P for help/beacon feedback and E to grip/release a nearby fixed handle (G also
releases). **Bind selected downed handle** wires a RagdollHandle to the host;
assign a solid raycast shape/contact. This is a force-limited compliant hand
constraint, with equal reaction on a dynamic anchor. It uses the nearest declared
hand, falling back to the pelvis if hands are absent. GripHandle reuses canonical
claims, revision checks, contention, leases and receipts; ordinary cargo/control
use remains unavailable while Down. Unconscious workers have no input agency.
Accepted impact, expiry, disconnect and recovery release handles. Local auto-recovery
waits while a handle remains held. The camera follows the actual downed head/pelvis.

Recovery requires quiet limb motion, supported current pelvis position, acceptable
floor slope/motion and clear standing space. It chooses front/back from anatomical
axes, moves the root while preserving parent-first bone world poses, then blends
into the get-up. The host checks the same attempt and standing clearance before
completing. Imported get-up/exit durations must fit the 4.5 s adapter budget inside
the 5 s canonical window; frame hitches use elapsed real time. A blocked attempt
returns Down; an obstructed locker exit waits for space.

Use Alt+E to connect a reanimation station, deliver and release its assigned
unconscious patient inside the chamber, then E to start. Chamber/patient exclusivity,
epoch, injury episode, timer identity and presentation generation fence completion.
Disabling/swapping a station cancels its timer without overriding a newer physical
transition. Cosmetic effects publish last, catch their own failures and cannot
reenter Execute. Alt+E also selects pull for a held cart.

## Validation and limits

See [the task record](../../../../../validation/MOVEMENT_ANIMATIONS.md) and
[architecture](../../../../../../design/code-architecture/README.md). Offline
selection/cue/control/custody tests use actual canonical C# source. Native library
binding and physics fixtures are present but have not run here: there is no activated
Unity Editor or imported finished character in this environment. No Player,
multiplayer, frame-rate, visual/physics or game-feel acceptance is claimed.

This is a host scene adapter. Networking, microphone/voice, final character/FBX import,
map colliders and human animation review remain separate requirements. Existing
rules do not yet define mining yield, medical cartridge inventory, OCRU resource
costs, radiation/exposure zones or restraint gameplay. Dig/work effects and recovery
are wired; those broader gameplay owners are not fabricated in cosmetic callbacks.
