# Unity gameplay sandbox development pass

**Source work in progress; every execution check is NotRun.**

Owner authorization: Cameron requested a substantial ten-hour development pass
on 18 October 2026. The pass began at 10:29 UTC / 12:29 SAST and ends at
20:29 UTC / 22:29 SAST that day. Continue connected implementation batches until
that deadline unless Cameron redirects the task. Keep the active goal running;
do not equate a small commit with completion of this pass.

While Cameron plays For Honor: small file operations and source edits only.
Do not launch Unity or Blender, run compilers or tests, import assets, bake,
render, or start other heavy operations. An explicit later instruction from
Cameron is needed before execution resumes. Do not infer permission from the
pass's clock or from the amount of completed source.

Primary author: Codex. Independent reviewer: unassigned. Base `ecaacf01`;
branch `codex/unity-gameplay-sandbox`. No self-merge or direct main edits.

## Scoped implementation decision

This is an isolated, local-host integration trial and physics fixture, not a
networking choice, new production room, finished art pass or accepted roadmap
gate. It uses Unity 6000.4.3f1 / 39d1a88d4dd1, C# and the existing game rules.
Map source, exported room content, baked lighting and the map team's layout
remain outside the touched paths.

1. Expose the canonical `dotnet/src` sources as the local first-party UPM package
   `com.criticalshift.gameplay`. Add explicit engine-free assembly definitions
   with the same dependency graph as the existing projects. No rule code is
   copied, moved or replaced. .NET intermediates/output move to ignored
   `dotnet/artifacts/compiled`, outside Unity's package. Native evidence tooling
   must include this local source package in its disposable copy and fingerprint.
2. Build a composed local-world adapter and explicit physical entity bindings.
   Current claims remain authoritative. Physics reconciles only current epoch
   and lease snapshots, releases on stop/expiry, and reports obstruction failure
   for the exact lease. Unity owns Rigidbody motion, not a second custody model.
3. Add bounded cart and conveyor physics, with injected ownership filters so
   they cannot keep accelerating a held or slotted object. Cart wheel motion
   and machine/lighting effects are presentation of observed state.
4. Add diagnostic IMGUI controls using the already selected foundation IMGUI
   module. This is a fixture interface, not adoption of production input/UI,
   networking, Steam, voice or persistence infrastructure. Add only Unity's
   already-selected built-in Physics module where needed.
5. Provide a deterministic scene-generation entrypoint for an isolated sandbox.
   The generator will be run only after execution is authorized. Wire a small
   source-backed production chain and replay/reset checks; no map assumptions.

These implement A01-A08, S01-S05/S07/S09 and H01/H04/H07 within a source-only
trial. ADR-CA-005 in the existing decision register records source packaging.
D-02 through D-09 remain open at their production deadlines; no gate advances.

## Validation and acceptance

Required after permission to test: package source/metadata/graph checks and their
negative fixtures; offline verifier; pinned Unity clean import; exact native
test discovery; local claim/lease/failure/reset and physical cart/conveyor
fixtures; Player startup and shutdown. Record actual versions, counts, failure
logs and limitations. Physical bindings, renderer behavior, performance, feel
and multiplayer acceptance cannot be established from source inspection.

The owner-selected renderer is URP. This pass does not install a URP version or
quietly accept the old Built-in foundation as the final game renderer. Pending
renderer integration remains explicit, and generated debug geometry is not
art acceptance.

## Current checkpoint

- Foundation repair `ecaacf01` is the separate preceding source commit.
- Canonical source package, matching engine-free asmdefs, build-output isolation
  and disposable validation-input wiring: written, unvalidated.
- Local command sender, current-state carry/slot bindings, explicit spatial
  access and unscaled host clock: written, unvalidated.
- Cart drive/brakes, load sensing, wheel travel animation, bounded conveyor and
  jam latch, local walking: written, unvalidated.
- Diagnostic controls, crusher/fuel/reactor fixture, lamps, valve/spindle/tread
  motion, material appearance and scratch-scene generator: written, unvalidated.
- Nine pure command-port tests, fourteen worker-body claim tests, nine package
  safety tests, five declared-boundary cases and 86 native sandbox
  tests are implemented, all **NotRun**. These are declared inventory counts,
  not discovered/executed results.
- Direct first-person focus, context transfer/drop, power/cooling and start
  controls are written, with the same authority and receipt path as the panel.
- Carry slowdown, cart load warnings, visual rotation markers and fresh-epoch
  bootstrap enable/disable lifecycle handling are written, unvalidated.
- Physical references now live in one world-scoped binding registry, separate
  from the host clock/command adapter. The cart uses an exclusive existing claim
  as its handle lease; only CartMotor drives its body. The local worker follows
  an explicit stance anchor, and lost proximity releases the exact lease.
- Next: continue source review and lifecycle failure cases, then extend concrete
  fixture interactions while execution remains deferred. Do not stop this goal
  after the first implementation checkpoint.
- A separate disposable sandbox runner is written; its default scope is native
  import and the declared PlayMode inventory. Optional Player build is URP-gated;
  Player execution, performance and human acceptance are still separate.
- Scene generation retains an explicit serialized shader dependency. Debug
  materials follow the already configured pipeline, without installing one.
- Physics mass uses an authored 0.75 kg per material-unit fixture mapping and
  updates from committed conversion output; this is a bounded physical proxy,
  not a real industrial mass model or a second material ledger.
- Tests, native import, builds and performance: **NotRun**, owner constraint.
- Independent review and merge: pending.

## Source checks actually performed

Only small file checks have run: `git diff --check`, parsing the changed Python
source with `ast.parse` (without executing test modules), and parsing assembly
definition JSON. Metadata was written by the source-only helper. These do not
compile C#, execute tests, import Unity packages or establish runtime behavior.
All compiler, test and engine execution counts remain zero for this pass.

## Local fixture values before first execution

These are initial test-fixture values, not shipped balance or measured results:
3.8 m interaction reach, 800 ms renewal interval with the inherited 3 s lease,
3.5 m hard carry separation and 1.5 s sustained obstruction timeout; spring
acceleration capped at 60 m/s²; cart speed 3.5 m/s and safe cargo proxy 35 kg;
belt speed 1.4 m/s with acceleration capped at 8 m/s² and a 2 s blockage latch.
The first fixture batch begins at 36 logical units; the other seven have 12 each.
Physical mass uses
0.75 kg/unit, clamped to 0.25–250 kg, with converted output updating the same
physical container. Carry speed scales as `1/(1 + kg/20)`, bounded to 35–100%.
These values make overload and slowdown observable in a small room; native
stability, feel and target-hardware performance must still be measured.

Source checkpoints: `aa172367` (one canonical Unity/.NET source package),
`532a5116` (first connected sandbox source), `8e9bae2a` (focus/carry/lifecycle)
`a58278db` (exclusive cart-handle claims) and `b70c4311` (worker physics trial).
Subsequent edits remain part of
this same ongoing ten-hour pass; no checkpoint is gate acceptance.

The physical cart-handle source trial uses 1.4 m entry distance from its operator
stance, a 1.5 m/s maximum entry speed and 2 m maintained proximity. Its body is
not also registered as a spring-carried body. One canonical actor claim covers
either a container or the cart handle; no parallel driver/holder authority is
introduced. Spherical wheel contacts use an owned low-friction material as a
rolling-resistance proxy; CartMotor supplies bounded lateral damping and drive.
One additional native case exercises the actual grounded fixture and stance
following. All cart-handle and grounded-drive cases remain NotRun.

## Worker physics source trial

This extends the same isolated fixture under S04/S07/S09 and the planned
HOLD-03, WORKER-01 and PHYS-01 cases. Application remains the consciousness,
posture and claim mutation owner. No worker-domain rules are copied or changed.
`Workers.Unity` switches between the walking capsule and an explicitly bound
eleven-body, ten-joint debug rig. Only one mode supplies physical motion.
The camera follows head position while retaining its look heading during a fall.

Registered physical contact observations are bounded to eight sources and 32 query
hits. A 1.8 m/s closing-speed and moving-cart threshold produces a configured
knockdown with a 1500 ms rule delay. Contact latching prevents repeated episodes
from one continuous contact; cause IDs and ordered per-source observations use
the canonical worker entrypoint. A separate explicit developer source exercises
the same path from the fixture panel. The locomotion push callback now permits
only explicitly authorized free portable bodies, excluding the driven cart.

Recovery stages a standing pose on static support, checks velocity, slope and
capsule clearance, then rechecks the exact attempt after 400 process-clock ms.
A new impact invalidates that placement. Blockage, missing support and stale
attempts preserve the down state. The physics handoff happens only after the
canonical completion accepts the current attempt. All initial thresholds and
joint anatomy are fixture values pending native tuning and feel review.

Seven new native worker cases are implemented, all NotRun: claim drop/motion
handoff, actual cart contact and single episode, stationary contact rejection,
recovery delay and single controller, low ceiling, missing ground, and impact
interruption of a pending recovery. Ten-cycle teardown also checks that the old
body rig becomes kinematic. Body dragging, aid/reanimation, production character
art/animation and multiplayer coverage are still separate unfinished work.

The subsequent source review added three native-log parser fixtures for the
canonical local package's diagnostic paths and separation of vendor warnings,
plus one source-package fixture rejecting loose binaries with either DLL casing.
These tooling cases also remain NotRun. Native input copying rejects those
binaries before launching an Editor, and reports retain the exact expected test
inventory used for comparison. A lightweight main fetch after the worker source
checkpoint still resolves to `3853995c`; there were no new upstream commits.

## Process presentation source checkpoint

The existing machine/reactor feedback owners now drive a visible process gauge
and bounded cosmetic pools: eight spark markers per machine and six vent motes
for the reactor. They use only committed work/shift time and immutable projections;
no incident RNG, gameplay callbacks, colliders or per-effect object spawning.
Power pause hides processing sparks; process-clock pause freezes trajectories.
The simple opaque debug meshes do not establish finished steam, fire or VFX art.
Three additional native cases cover power-pause/progress consistency, paused
cosmetic trajectories and cooling-loss/trip feedback without another power spend.
All remain NotRun, alongside shaders, rendered appearance and measured cost.

## Next bounded source scope: single-worker dragging

Extend the existing worker/Interaction workflow under S04/S07, without selecting
two-person carrying or a transport. Register an explicit worker-body entity at
setup; only Down targets can be grabbed or renewed; held bodies cannot begin
standing recovery. Claims remain in the same store and command/receipt stream.
Disconnect retires the target's body claim before removing its worker binding.
The physical adapter will pull only an active ragdoll through its existing force
owner, with bounded separation/obstruction and exact-lease release. Use a second
explicit local fixture worker for source tests and interaction, never a map edit.
This scope is in progress. Physical dragging cases are now written and NotRun;
no drag, multiplayer, reanimation or human-feel acceptance is claimed.

The canonical body registration, target-condition gate and recovery/claim
exclusion are written. Fourteen new pure cases are implemented, NotRun, covering
registration failure, ordered rejections, contention, orthogonal conditions,
unconscious dragging without revival, recovery exclusion, impact/lease release,
both disconnect directions, body-owned timer cleanup, restart/epoch isolation
and rejection by material machinery. They add to the nine command-port cases;
neither group has executed in this pass.

Physical dragging is written through an explicit Interaction binding that calls
the worker rig's existing force owner. It does not reference the Workers Unity
assembly or create a parallel spring-force component. The second fixture worker
has an explicit body entity and moving suit-grip interaction point, with ten
physical entity bindings total. Each worker's recovery placement is routed by a
sealed, epoch-scoped registry. A held body blocks recovery in Application and
the fixture controls. Body/suit physical mass and contact friction are authored
debug proxies, not a material inventory or accepted balance.

Initial drag values: 68 kg total body proxy, 250 N maximum pull, 3 m hard
separation, 1.25 s sustained error timeout beyond 1.2 m, 0.18/0.15 suit contact
friction and a drag target 0.55 m above the rescuer's feet. The existing movement
scale clamps to 35% for this load. No value is measured or accepted yet.
Five native drag cases are written, NotRun: physical pull/slowdown, reach loss
and stale-lease rejection, held-body recovery exclusion, a moving suit anchor
independent of the old worker root, and teardown while dragging into a fresh
epoch. The ten-cycle fixture teardown now covers both physical worker rigs.

## Focused machine recovery controls

R now issues one current-state action: Start, Repair for a jam, or Resume for a
power-paused cycle. It never silently toggles power or bundles several changes.
F still isolates/restores power; B explicitly starts the existing inspection
bypass, including its canonical wet-batch jam and lineage consequences. Focus
hints expose the current step. Command admission still uses the same sender,
revisions and receipt stream. Focus preflight now samples the host clock before
checking phase, including pause and deadline boundaries.

Two additional native cases are implemented, NotRun: wet bypass through jam,
power isolation, repair and resume with retained cause/flags; and resuming the
same cycle with preserved committed work. No new gameplay rule or cost is added.

## Current-volume cargo observations

The cart sensor now uses a bounded 64-collider current-volume query instead of
retained enter/exit event counts. This removes stale load after collider disable,
removal or relocation. It tracks at most the configured 32 distinct observed
bodies by default; overflow remains visible and prevents drive until reset.
Explicit callbacks group free material bodies individually and a free Down
worker's eleven segments under one physical representative and 68 kg mass proxy.
Held/slotted bodies are excluded. Any observed worker part counts the full group;
this conservative handling proxy neither writes custody nor establishes that a
worker was successfully loaded or transported. Belt permission remains limited
to known free material bodies.

Four more native cases are written, NotRun: multi-Rigidbody load deduplication
and eligibility changes; disabled/relocated colliders leaving no ghost load;
visible overflow after clearing; and the actual fixture worker's group identity
before/during/after a drag claim. Actual loading, transport stability, appearance
and performance still require native execution and human review.

Machine power controls now have a visible state-driven handle, with the existing
feedback owner retaining all writes to its visual pivots. A jam remains visibly
red after power isolation. Cart wheel steering presentation now reads effective
drive authority, so walking input cannot steer an unclaimed cart's visual wheels;
passive wheel spin still follows actual observed travel. Existing native cases
include the changed bindings/authority assertions and remain NotRun.

Later source commits: `7223a933` (canonical worker-body claims), `88aa0778`
(suit-grip binding), `7799966e` (process pools), `22de3cfb` (context machine
recovery), and `f74e324d` (current-volume grouped cargo). All are local source
checkpoints, unmerged and pending independent review. The ten-hour goal remains
active; neither these commits nor the declared inventory constitute completion.

Worker physics/drag tests now inject a fixture clock before startup and advance
it with their explicit physics steps. Editor wall-clock stalls therefore cannot
spend a recovery deadline in those cases. Normal fixture play retains the
existing unscaled host clock. Source review also tightened recovery support:
the short downward search begins by the pelvis and rejects surfaces above it,
with a bounded body-to-standing-root height. This prevents an overhead platform
from being selected as the new floor. The existing low-ceiling/ground tests
cover the affected path when execution is allowed; they remain NotRun.

## Source and future native assembly boundaries

The existing source checker now classifies first-party module declarations and
rejects peer Unity adapters, editor leakage, unselected precompiled SDKs and
runtime test-assembly opt-in. It checks platform/purity/reference settings and
unique C# ownership. Five source fixtures are implemented, NotRun. This is an
executable check for the existing architecture, not a replacement policy guide.

The sandbox runner now has a separate source phase before native import. The
future Editor prepare step reads Unity's compilation description, requires each
production module's resolved project references to match its declaration, checks
pure compiled references for engine leakage and requires the output assembly.
A native count marker must match the source production-module inventory. No
Editor was launched to verify these assumptions; native graph/import status
remains NotRun. Test discovery, Player graph/build, behavior, feel and performance
remain their separate evidence requirements. No package or CI workflow is added.

## Controlled worker hoist source

Add a held Shift hoist to the existing single-person suit-grip path so its source
fixture can attempt loading a worker over the cart bed. This is continuous host
physics input under the current lease, not another custody state or heal action.
Only the existing worker rig adds force. The low drag target rises by 1.5 m at
2.5 m/s; hoisting adds authored gravity compensation with a bounded force budget.
Release, expiry, impact and teardown clear the mode and target. Three new physical
cases are now written and NotRun; loading/transport acceptance remains NotRun.
The force budget is the authored body weight plus 250 N, capped at 1100 N; these
are game fixture values. The rig adds gravity compensation only for the current
hoist generation. Tests cover same-lease rise with unchanged Down state, release
and stale-input isolation (including old input cancelling a newer hoist), and a
physically hoisted worker dropped over a
deliberately placed test cart becoming one observed load. The last case does not
yet prove steering/transport stability or human ease of loading.

## Down-worker agency source

Add the spec's bounded conscious crawl to the same local ragdoll force owner.
Only an Alert, Down worker in a Running world, outside a held/slotted body claim
and outside pending recovery, can request it. A short grounded support query
prevents airborne propulsion; moving support velocity is accounted for. The
walking capsule stays disabled. Initial limits are 0.65 m/s desired crawl speed
and 220 N horizontal force. This changes physical motion, not health or custody.
Three additional native cases are now written and NotRun: alert crawl with one
motion owner and pause exclusion, upright/unconscious exclusion, and crawling out
from under a low ceiling before clearance-approved recovery. An existing drag
case also checks that a held worker cannot apply crawl forces. Crawl feedback
reports only actual physical drive admission; it is not another logical pose.
Native/human acceptance remains NotRun.

## Normal worker presentation source

Add small walking/carrying poses to the existing debug body while its walking
capsule owns motion. Four explicit two-segment chains preserve the same joint
anchors used by ragdoll, with angles inside the authored fixture limits. The
normal pose path never writes dynamic bodies and stops on handoff to Down.
Root movement drives walking phase; an injected current-grip query drives the
arm pose. This is runtime debug presentation, not a Blender/character art pass.
Two additional native cases are written and NotRun: walking joint continuity
through knockdown, and carrying/release poses without material or worker-state
mutation. Native handoff, visual and performance acceptance remain NotRun.

## Reactor console source

Add focused X shutdown and C emergency cooling using the existing typed reactor
command stream. R resets a tripped core; a separate R starts it afterward. These
controls retain reach/occlusion, current revisions, existing interlocks, costs
and replay receipts. Add two debug needle gauges driven by remaining fuel time
and current reserve/capacity. Their visual smoothing never advances production.
Three additional native cases are written and NotRun: emergency cost/replay and
trip reset without automatic startup; target/pause/empty-core exclusion; and
instrument projections through pause and teardown. No reactor rules, fictional
costs, renderer settings, map assets or package decisions change.

## Short-hop locomotion source

Add the spec 4.2 short hop to the existing collision controller: 4.8 m/s initial
upward speed, 20 m/s² authored gravity, 0.10 s ledge grace, 0.12 s input buffer,
4 m/s² air acceleration and the existing 0.05 s frame-step cap. The current mass
slowdown also scales hop height. These are bounded debug fixture values, not
measured feel acceptance. Cart grip keeps Space as its brake. Pause, down state,
recovery, focus loss and teardown cannot retain a queued hop. Above contact cuts
upward drive and the same capsule owns all upright movement.
Three more native cases are written, NotRun: bounded hop/landing, low-ceiling
contact without retained upward drive, and pause/cart/ragdoll exclusion. No new
input package or logical worker posture is introduced. The Unity 6000.4 API
contracts for [Move](https://docs.unity3d.com/6000.4/Documentation/ScriptReference/CharacterController.Move.html),
[isGrounded](https://docs.unity3d.com/6000.4/Documentation/ScriptReference/CharacterController-isGrounded.html)
and [collision flags](https://docs.unity3d.com/6000.4/Documentation/ScriptReference/CollisionFlags.html)
were consulted; that is API research, not an executed native check.

## Current-claim crate orientation source

Add middle-mouse drag to adjust only the current portable body's carry target.
The existing bounded torque path remains the body rotation writer. Input does
not commit another custody/material operation, bypass reach or turn a worker
drag/cart handle. Per-actor orientation resets on a different entity or lease,
release, slot insertion, expiry, obstruction drop and teardown. Pause rejects
rotation input while preserving the current target. Target bindings now reject
sharing one Transform across actors. Small face markings show crate orientation;
solid carry bounds are bound before those non-contacting decorations are added.
Two further native cases are written and NotRun: torque/claim/material ownership,
and pause/release/new-lease/teardown resets. Existing cart and worker drag cases
also check rotation exclusion. No physical/visual/feel acceptance is claimed.

## Explicit heavy-load contact source

Extend the same bounded worker contact observer with a configured falling-body
path. The first crate now contains 36 units / 27 kg and carries two yellow
warning bands. It is registered for both fixture workers; all other crates keep
12 units / 9 kg. Only its free, unslotted, dynamic physical state can report a
falling contact, with authored minimum mass 20 kg and downward/closing speed
2.2 m/s. Current and immediately prior linear speeds cover the solver stopping
the source at contact, without interpreting spin as downward translation. The
existing cart's planar path remains at 1.8 m/s. Both routes use the same trusted
observation identities, bounded impulse and continuous-contact latch; neither
is a new health writer or a real injury model.
Three additional native cases are written and NotRun: one falling-crate episode,
held-source exclusion and the physical mass threshold. Contact timing, feel and
ragdoll acceptance remain unvalidated. This does not install general collision
damage, conveyor harm, reanimation or map hazard bindings.

## One-shot portable throw source

Add T to release and throw an ordinary portable body. The host samples time and
current posture/claim, commits the existing Release command, reconciles current
bindings, then checks the exact released epoch, revision and lease generation
before applying one impulse. Historical replay is not a new physical effect.
The same CarryBodyBinding owns that impulse, bounded to 35 N·s and at most 5 m/s
additional speed; existing momentum remains. The look heading supplies aim
independently of manual crate rotation. Worker/cart grips and paused/expired
claims cannot launch. These are authored game-fixture values.
Two further native cases are written and NotRun: one release/impulse despite
retries and rotation, and pause/expiry exclusion. Existing cart and worker drag
cases also check that T preserves those grips. Native safety, feel and impact
results remain unvalidated. No command kind, resource cost or transport changes.

## Bounded physics observation source

Add a fixture-only observer over 31 explicitly bound bodies (8 containers, cart,
two 11-segment workers), with a hard 64-binding capacity. It checks finite poses
and dynamic velocities, active bindings and root-relative containment, then
reports one latched failure through the existing stop/error handler. It never
clamps motion, teleports cargo, respawns a worker or changes material accounting.
The sandbox region is centre (0,2,3), size (34,20,32) metres; diagnostic limits
are 25 m/s and 25 rad/s. These are authored trial-failure bounds, not balance,
supported performance or shipped rescue rules. The panel exposes current/peak
dynamic counts and peak observed speed. Teardown drops all explicit references.
Three more native cases are written and NotRun: dynamic/kinematic observation
without motion writes; one runaway failure; and escaped held cargo stopping the
actual fixture and clearing the claim. These support future PHYS-02 evidence;
no tunnelling, native stability, frame-time or performance pass is asserted.

## Material-content presentation source

The same eight portable box proxies now have open debug bin visuals and eight
prebound, non-contacting content markers each. One existing presentation owner
reads the canonical batch and updates visible fraction, shape and condition
color. It never creates inventory entities or spawns pieces during an update.
Ore is irregular, crushed material flatter, fuel/spent fuel aligned. Markings
move onto the front wall so manual orientation remains readable. The original
solid box stays the declared physical proxy; no containment behavior is implied.
Spent fuel keeps its authored ledger quantity and stays visible after reactor
exhaustion. A missing/stopped projection hides the pile; reenable refreshes even
when the batch revision is unchanged. Three new native cases are written and
NotRun: conversion/yield without another commit; spent-fuel accounting; and
paused reenable/teardown with no new visual objects. Appearance, physics proxy
fit and rendering cost remain unvalidated and require later native/human review.

## Machine and conveyor mechanical presentation source

Add explicitly bound visual loading clamps and a reciprocating ram to each debug
machine. Occupancy drives clamp position; committed work drives the ram stroke,
which stays at its committed position during a jam or process pause. Existing
process-feedback cases now assert that freeze and no gameplay writes; they stay
NotRun. Add two conveyor end rollers, driven by the same bounded tread travel.
Their angular phase is independent of the tread wrap so a full belt-length wrap
cannot snap the rollers. All parts are non-contacting decorations; existing
physical supports, slot checks, material ownership and machine rules remain the
same. No extra test is added just to mirror a cosmetic tween. Native visual and
performance review remain outstanding.

## Runtime-created primitive dependencies

The shape factory now directly references and validates MeshFilter,
MeshRenderer and the expected Box/Sphere/CapsuleCollider types. It accepts only
the four primitive shapes actually used by this fixture and immediately assigns
its owned material, whose shader is already a serialized scene dependency.
This addresses the documented runtime-component stripping risk without a broad
linker exemption, default-material dependency or renderer/package migration.
The [Unity 6000.4 CreatePrimitive reference](https://docs.unity3d.com/6000.4/Documentation/ScriptReference/GameObject.CreatePrimitive.html)
was consulted. Actual stripped Player startup remains NotRun.

## Future standalone Player lifetime source

Add explicit `--run-player` opt-in to the existing disposable sandbox runner,
requiring `--build-player` in the same source run. URP configuration remains a
build prerequisite. The new development-Player-only smoke flag disables fixture
input, validates meshes/material references and observes the unchanged baseline
for at least 120 physics frames and two seconds. It then tears down and waits
across deferred destruction before reporting exact zero logical, claim, timer,
connection, physical-binding and observation-reference counters. Native Player
version, build GUID, epoch and initial binding inventory must agree. The binary
hash is recorded; a mismatched execution OS is Blocked. No existing Player is
silently reused. Bootstrap cleanup now records actual post-disposal reference
counts before releasing its fixture and always detaches the smoke log listener.
Eight Python evidence/runner cases are written and NotRun: valid evidence plus
wrong identities, missing/duplicate/malformed markers, lifecycle order/world
mismatch, short/incomplete inventory, residual/error counters, failed process
or critical log, and execution without a fresh build. Existing native lifetime
cases check the new actual cleanup counters. No engine, compiler, tests or Player
was launched to implement this. Headless startup cannot establish rendering,
human feel, network convergence, FPS or an accepted roadmap gate.

The deliberate escaped-cargo negative fixture now captures an explicitly
injected diagnostic sink and asserts the exact failure. The runtime default
still logs the exception. This keeps expected test faults from looking like
unexpected errors to the strict native log validator; no critical-log pattern
is removed or globally ignored. The diagnostic override is composed before
startup and released with the bootstrap.

## Bounded causal display source

Expose the existing detached SessionTraceView through the local query port and
project it into at most 12 recent diagnostic rows, polled four times per second.
Rows use actual committed production/reactor/worker records and their recorded
cause, actor, entity and hazard identities. Replay/noncommits, clock advances and
routine generation ticks cannot mint display incidents. Existing trace storage
and retention are unchanged; sequence gaps and exhaustion remain visible, and
the panel does not claim a full shift debrief or accepted CAUSE-01 evidence.
Three more native cases are written and NotRun: wet-jam attribution/replay;
explicit source eviction gaps without fabricated incidents; and bounded rows
through a stopped-world read without state mutation. No new event authority,
cause reconstruction, gameplay randomness or persistence is introduced.

Input review also aligned hoist admission with other active controls: it samples
the trusted clock and enables lifting only during Running. Pause lowers the
target without releasing the current lease or changing the worker's Down state.
The existing hoist native case now includes that exclusion and remains NotRun.
Tab toggling also ignores key autorepeat using the existing held-key set.

## Conscious down-look source

Permit bounded look input for Alert Down/Recovering workers while the walking
capsule remains disabled. Only the eye pivot rotates; dynamic body transforms
and their ancestor remain under the existing physics owner. Crawl uses the
flattened view heading. Recovery keeps the latest world-space eye orientation;
after the approved handoff ends dynamic motion, the normal motor aligns its
upright yaw to that view. The obsolete stored pre-fall eye rotation is removed
(private runtime state, not serialized asset data). Unconscious/paused workers
cannot look through this path. Two more native cases are written and NotRun:
eye-only look with view-directed crawl and unchanged worker revision; and view
continuity through recovery plus unconscious exclusion. Camera comfort and all
physics/human acceptance remain unvalidated.

## Derived worker status lighting source

Add one explicitly bound, non-contacting status marker and shadowless point
light per fixture worker. It follows the physical suit grip and reads only
worker/world projections: amber Down, red Unconscious, blue Recovering, hidden
Upright or after world stop. Pulse uses process time; it cannot advance health,
claims, recovery, randomness or power spending. This is a diagnostic cue, not
implementation of a separately activated networked emergency beacon. Existing
knockdown/recovery native cases now check visibility after the controller
handoffs; they remain NotRun. No new test is added solely to mirror the colors.
Lighting quality, comfort, rendering cost and multiplayer visibility remain
unvalidated; map and accepted room lighting are untouched.

Presentation lifecycle review moved native MaterialPropertyBlock construction
from MonoBehaviour field initializers into each explicit setup method. Managed
arrays/callback fields remain ordinary initialization; the normal cosmetic pool
already allocates its blocks during that same setup path. No render or import
has run to validate this lifecycle change, and no performance gain is asserted.

Presentation binding loss now disables only the affected cosmetic component
and emits a named error, rather than silently freezing a stale lamp, instrument,
ram, tread or roller. This never rolls back or retries a committed game action.
The strict native log/Player error checks stay in force. A latched physics fault
also shows its existing reason in the wrapped fixture status panel. These source
diagnostics have not been executed; no new cosmetic mirror test is introduced.
