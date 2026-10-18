# Unity gameplay sandbox development pass

## PR #111 independent review and repairs, 18 October 2026

Cameron requested a large ultra review, implementation of fixes by the primary
author, useful additions, and merge after completion. That instruction authorizes
this task's implementation and merge, superseding the earlier development-window
restriction below. Six separate ultra reviewers covered canonical rules,
interaction/facility physics, workers, composition/presentation/map integration,
tooling/evidence, and cumulative integration including PR #110. Codex remained
the sole repair author. Each affected reviewer independently inspected the repairs;
this is source review, not human playtesting or roadmap acceptance.

Reviewed baseline: `7d25129000395b62f6739395aa37596c15495600`, originally based on
PR #110 at `4bab143f132c17188433d1cf2819441e2240c7f1`. Delivery targets `main`
and includes those ten inherited bake/importer paths, with their defects repaired,
rather than merging gameplay only into the unmerged dependency branch.

Repairs:

- Portable slot bounds use current box/mesh geometry and correctly scaled sphere/
  capsule geometry in the body-neutral frame. Incoming crate rotation no longer
  inflates the loading envelope. Offsets, compound shapes and rescaling checks remain.
- Drag-target hoist state resets on both entity and lease replacement, including
  expiry/regrab within one command. Setup disconnect retires a worker's body before
  removing its mapping, preventing an orphan from becoming an ordinary claimable object.
- Recovery derives the expanded standing capsule's clearance from its support plane,
  admits walkable inclines, and checks every physical layer while respecting ignored
  collision pairs/layers. Pending support and motion are still rechecked.
- Every native runner audits copied first-party executable inputs and metadata after
  native phases and finally. Combined-map preparation also audits all four copied map
  inputs and initialized package-descriptor hashes. Native failure reasons survive
  final audit failures. Strict phases now reject general managed exception headers.
- The inherited all-stage bake reopens prepared geometry before finishing, preserving
  the original objects/hierarchy/animation after destructive in-memory bake joins.
  Round-trip checks validate all vertex and transformed coordinates, including NaN/Inf
  after vertex 1,000; non-finite bounds cannot compare as a false pass.

Executed verification of the repaired inputs:

- .NET SDK 8.0.423: **724/724 passed**, zero failed/skipped. Twelve scenarios passed
  twice, with 818 scenario assertions; deliberate failing-test, malformed/empty
  scenario and report-safety controls passed. A separate focused worker-body run
  passed all 15 cases. Source hashes are in ignored `runtime/dotnet/artifacts/summary.json`.
- Python tooling: **182/182 passed**, including fault injection for copied source,
  metadata, map and SDK-descriptor drift. Four separate bake-boundary regressions
  passed without invoking Blender. Static source and exact test-catalogue checks passed.
- Four new native gameplay cases are implemented: rotated crate admission, scaled/
  offset sphere/capsule admission, immediate expiry/regrab hoist reset, and inclined
  recovery with pending steepening. The low-ceiling case also covers Ignore Raycast
  physical geometry. The declared catalogue is now **136 cases**.

**Native validation of these repairs: NotRun.** This cloud workspace has no Unity
editor or Blender installation. The new native cases, fresh Player/build/rendered
checks and actual bake/FBX checks did not run here. Earlier `6554abef` native results
below remain evidence for that earlier source only. The existing local Win64 ZIP is
also the earlier build. No claim of 100% perfection, accepted feel, supported FPS,
multiplayer readiness, full facility/art acceptance or gate advancement is made.
The compact review index is `results/pr111-review-2026-10-18.json`.

## Prior development evidence

**Development validation completed; independent acceptance pending. See dated results below.**

Latest completed full native gameplay run: **Passed**, `6554abef`,
`sandbox-zxh6eap1`: clean initialization/preparation, **132/132 passed, zero
skipped**, strict-variant Win64 build and headless Player smoke with zero remaining
owned references. That same build passed a separate normal-window rendered PNG
capture and an opt-in typed deny/carry/drop exercise, including their rejection
controls. Its batch-mode capture attempt remains Failed. All 21 supplementary
API checks and both Windows/Ubuntu source/offline CI jobs passed on `6554abef`.
Separate foundation validation passed 12 EditMode / 9 PlayMode cases, build and
Player. Current combined-map URP preparation also passed 37 doors / 152 proxies /
13 anchors with maximum error 0.0002840849 m. These bounded sandbox results do not establish gameplay feel,
performance, combined-map or art acceptance.
The reviewed source policy in `4822787d` observes independent **25 m/s linear
speed and 312.5 J/kg specific rotational energy**, retaining raw angular
diagnostics. This remains an authored, unaccepted trial budget, not a physical
motion fix.
All earlier failures, the three failed solver/origin comparisons and the
historical 124-case pass retain their original status.

Owner authorization: Cameron requested a substantial ten-hour development pass
on 18 October 2026. The pass began at 10:29 UTC / 12:29 SAST and ends at
20:29 UTC / 22:29 SAST that day. Continue connected implementation batches until
that deadline unless Cameron redirects the task. Keep the active goal running;
do not equate a small commit with completion of this pass.

The initial gaming restriction allowed only small file operations and source
edits. On 18 October Cameron explicitly said gaming was finished and authorized
Unity headless/normal execution and testing. The primary author coordinates
engine/compiler runs against fixed snapshots. New map gameplay targets the
combined map only, preserving the current provisional coordinates. Do not edit
`sections/facility-assembly/unity/` or
`runtime/unity/Assets/CriticalShift/Content/Editor/` while Claude's PR #110 is
open; no source blend or room changes are authorized by this runtime work.

Primary author: Codex. Independent reviewer: unassigned. Base `ecaacf01`;
branch `codex/unity-gameplay-sandbox`. No self-merge or direct main edits.

On 18 October the owner authorized three coding subagents.
The primary author remains the integrator on this one task branch. File ownership
is disjoint: worker adapters and their physics/drag cases; facility motion and
its physics cases; validation tooling and its own source cases. The primary author
owns interaction/presentation/bootstrap and the shared catalogue and task record.
Workers do not stage, commit, push or merge. Their contributions receive source
review before integration; contributing agents do not count as independent
acceptance reviewers. All share the gaming restriction above and the original
20:29 UTC deadline.

The referenced HanaPath orchestrator was read at its relocated archived path,
`.agent-ignore/archived-fleet-2026-07-21/ops/agents/SOL_ORCHESTRATOR.md`, with
its protocol and current root `CLAUDE.md`. Its bounded dispatch/review/ownership
practice is adapted here. HanaPath-specific queues, application checks and
main-merge permissions do not override Critical Shift's branch, architecture,
validation or no-self-merge rules. This existing task record remains the run
record; no competing queue or guide is introduced.

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
  safety tests, five declared-boundary cases and 119 native sandbox
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
acceleration capped at 60 m/sÃ‚Â²; cart speed 3.5 m/s and safe cargo proxy 35 kg;
belt speed 1.4 m/s with acceleration capped at 8 m/sÃ‚Â² and a 2 s blockage latch.
The first fixture batch begins at 36 logical units; the other seven have 12 each.
Physical mass uses
0.75 kg/unit, clamped to 0.25Ã¢â‚¬â€œ250 kg, with converted output updating the same
physical container. Carry speed scales as `1/(1 + kg/20)`, bounded to 35Ã¢â‚¬â€œ100%.
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
upward speed, 20 m/sÃ‚Â² authored gravity, 0.10 s ledge grace, 0.12 s input buffer,
4 m/sÃ‚Â² air acceleration and the existing 0.05 s frame-step cap. The current mass
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
The same CarryBodyBinding owns that impulse, bounded to 35 NÃ‚Â·s and at most 5 m/s
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
The sandbox region is centre (0,2,3), size (34,20,32) metres. Its historical
diagnostic limits were 25 m/s and 25 rad/s; the reviewed specific-energy policy
recorded below supersedes the angular criterion on 18 October 2026. These are
authored trial-failure bounds, not balance, supported performance or shipped
rescue rules. The panel exposes current/peak
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

The fixture panel now disables selected-crate Grab for a non-interacting worker
and Release unless that actor holds the selected crate. Host admission remains
authoritative. Bypass help names the actual faster/wet-jam/suspect-fuel behavior,
and reactor instability includes its milliseconds unit. The source-only native
catalogue comparison currently finds 86 declared methods and 86 saved identities
with no missing/extra names; this is not Unity discovery or execution evidence.

## Bounded carry reach source

Add wheel input outside the visible control panel to adjust the current ordinary
crate's target by at most 0.75 m along the authored eye-local forward axis. Its
fixture range is 1Ã¢â‚¬â€œ2.5 m; existing spring/torque/error bounds remain the physical
writer. Position and orientation now share one current-portable-claim admission
check, and both reset on release, slot transfer, expiry, obstruction and a new
entity/lease. No body teleport, new command sequence or material change occurs.
Existing manipulation/reset/cart/worker native cases now include distance and
pause/exclusion assertions; all remain NotRun. The torque case is renamed
`ManipulatingHeldCrateUsesBoundedForcesWithoutAnotherLogicalMutation` in the
saved catalogue; the declared total stays 86. Compact help now wraps on narrower
windows. Native handling, comfort and rendering acceptance remain unvalidated.

## Non-launching Editor identity source

Both native runners now inspect Windows Unity.exe product metadata before any
Editor invocation or disposable-project copy. Version and revision must exactly
match `runtime/toolchain.json`. The PowerShell script is constant and reads a
literal path supplied through a child-process environment value, without
executing the Editor or altering settings. Other hosts explicitly retain
NativeLogRequired status; every native run still needs its own version/revision
log evidence. Four new Python cases are written and NotRun (exact identity,
rejected mismatches, literal-path/no-Editor invocation and unsupported-host
honesty). A direct read-only file-metadata observation on this computer reported
ProductVersion `6000.4.3f1_39d1a88d4dd1` and FileVersion `6000.4.3.3789224`.
That read did not start Unity and does not constitute an import/compiler pass.

## Equipment interaction points

Source inspection found equipment reach/occlusion still using floor-level roots
and the cart centre, allowing floor or cargo geometry to interfere with intended
console/handle access. Keep each full collider hierarchy as the target identity,
but bind machines and reactor to their visible console faces, and the cart to
its rear grip, using the existing explicit interaction-point boundary. No global
reach increase or occluder bypass is added. A new actual-fixture native case
sets up a standing actor, inserts/processes/ejects ore with yield, then loads and
starts the reactor through real spatial admission. The existing grounded-cart
case now includes cargo before acquiring the handle. All remain NotRun; this is
a source correction pending native confirmation. The declared inventory is 87.

Native-resource lifecycle source review now tracks each created palette/contact
material before configuring it and disposes a partial palette if setup throws.
The existing ten-cycle native case also compares actual named Material and
PhysicsMaterial object counts after deferred destruction, rather than relying
only on cleared managed references. It ends with its tenth world stopped. This
global object enumeration exists only in the leak diagnostic, not runtime
binding discovery. The case remains NotRun; no leak-free native pass is claimed.

Slot lifecycle review now captures each portable body's original collision mode
and interpolation. It switches to ContinuousSpeculative/None before becoming
kinematic, then restores the original modes after returning to dynamic motion.
The existing slot native case now uses a continuous/interpolated body and checks
that handoff. This follows the same compatibility ordering as the worker rig.
The actual-console native case is extended/renamed to
`FacilityConsoleAnchorsAdmitProducedFuelThroughTheFullChain`: one container goes
through crusher yield, processor output, reactor loading and grid generation,
with conserved accounting. Test-only transport arrangements place the actor and
container between stations; it does not prove walking/handling feel or navigation.
The saved declared count remains 87; all engine/compiler/test execution is still
NotRun.

Pause reconciliation now cancels the worker hoist target and lift compensation
inside the physical binding owner, even if no further HUD/input callback arrives.
Resume keeps the lowered target until a fresh hoist input. The existing hoist
case now pauses directly without an input event and checks that resume cannot
restore the old lift; it remains NotRun. Equipment placement preflight also
checks host lifetime, samples the clock before the query and routes unexpected
observation failures through the same visible stop path as command execution.

Cart wheel animation now validates four unique, unnested visual pivots under the
same cart. Enabled contact shapes or Rigidbody descendants cannot be assigned to
the moving visuals. Validation finishes before installing the binding, so a
rejected setup cannot leave a partial LateUpdate path. Lost wheel/drive references
disable the cosmetic component and emit a named diagnostic. Reenable resamples
position to avoid treating disabled-time relocation as travel. The existing cart
speed case also observes wheel rolling, and one added native case rejects unsafe
bindings. The declared source catalogue is now 88 cases; every native case and
compiler remains NotRun.

The presentation assembly now checks its explicitly moved machine parts, reactor
valve/gauges/motes and bin contents through one setup check. Parts must be unique,
unnested descendants of the owning presentation object, without Rigidbody
descendants or enabled contact shapes, including inactive children. This closes
the reactor/inactive-child gaps and keeps animation out of physical ownership.
Machine/reactor pool validation finishes before installing their live query
binding. One new native case exercises rejected reactor setups and then a valid
setup on that same component, with unchanged world revision. Source catalogue:
89 cases, all NotRun. No engine/package/renderer decision changes.

Machine/reactor presentation also checks the full bound mote pool before every
refresh, including when an effect is idle or paused. A lost marker/renderer now
uses the same single disable-and-diagnostic path as a lost gauge or spindle;
it cannot throw repeatedly only once a running effect reaches that marker.
Surviving markers are hidden on disable. This remains source review, not an
executed failure-injection result.

Recovery motion clearance now applies its existing 1.25 m/s and 3 rad/s limits
to all eleven explicitly bound worker segments. A quiet pelvis cannot approve
standing while a forearm/leg is still moving quickly. Both initial placement and
the pending handoff recheck use this observation; non-finite motion throws a
named integrity failure instead of passing floating-point comparisons. One new
native case checks a moving limb at prepare and resolve, with the walking
capsule still disabled and the root unmoved. Source catalogue: 90 cases, all
NotRun. Thresholds remain unvalidated fixture values; no recovery-feel or
ragdoll-stability acceptance is claimed.

Attachment-failure callbacks now append a typed record to the existing bounded
Application trace, after the existing claim operation. Committed drops retain
the holder, entity, requested lease and previous/resulting claim revision. Stale
or wrong-epoch callbacks retain their rejection but cannot be attributed to the
current holder or publish another drop in the derived feed. No new custody/event
owner or notification callback is introduced; existing enum values are preserved
by appending the new kind. S04/S08 source coverage adds one pure diagnostics case
and one feed case. Native source catalogue: 91; both new cases and all compiler/
engine execution remain NotRun.

Lease expiry now adds its own typed entry after the existing claim-release
transition, preserving entity, generation and revision change even during process
pause. The existing released projection does not retain the former holder, so
that trace entry leaves actor empty rather than inferring an actor. It does not
copy a custody history or add another retention owner. The paused-expiry pure
case and the new feed case check one expiry notification without duplicate
publication on a repeated host sample. Declared counts are unchanged; execution
remains NotRun.

Portable-body bindings now retain their required contact shapes and verify that
those shapes remain enabled, solid, active and attached to the same Rigidbody.
Collision detection must remain enabled, and only the adapter's slot transition
may switch that portable body to kinematic motion. Lost contacts or a competing
motion mode stop the affected fixture visibly instead of leaving a held ghost
object. A new native case disables a held crate's solid shape and checks one
captured fault plus empty claims/bindings, without automatically repairing that
shape. Local-host test diagnostics are captured explicitly and unexpected faults
fail teardown; strict native log validation stays unchanged. Source catalogue:
92 native cases, all NotRun.

Terminal-world reconciliation now releases the local host's physical bindings
immediately when a pumped deadline or an externally ended/stopped/faulted world
is observed. That stops further admission and renewal in the same callback,
restores slotted bodies and keeps the terminal phase/outcome available for the
panel. Later fixture disposal still calls WorldSession.Stop. The physics monitor
also drops its references when the world closes, and always releases references
after a fault callback while retaining the fault/peak diagnostic values. Two
new native cases cover a deadline reached before a pending command and a full
deadline/visible-panel/dispose/fresh-epoch sequence. The existing monitor case
now checks reference release on normal closure. Source review also corrected
three lifetime-test member accesses that treated a WorldSessionView as its
mutable host owner; no compiler was run. Declared native catalogue: 94 cases,
all NotRun.

Portable placement bounds now retain the collider centre in metres rather than
dividing that offset by root scale. The captured world AABB is transformed into
a rotation-neutral enclosing box, then rotated into the loading slot; an
initially rotated compound remains conservative. Bound root scale must remain
unchanged because these placement bounds are authored at registration. A new
native case uses a scaled, offset solid box, verifies an adjacent obstacle blocks
insertion without consuming the command stream, then clears it and checks actual
slot geometry. Later rescaling must stop that binding rather than query stale
dimensions. Source catalogue: 95 native cases, all NotRun.

The cart handle now observes its required solid contact geometry, dynamic motion
mode, collision detection and still-parented active grip/stance anchors. Missing
contacts cannot leave an authoritative driver grip on a ghost cart. Fixture
composition binds the cart only after all bed/rail/handle/wheel shapes exist;
trigger sensors and disabled decorative colliders are excluded. One new native
case disables a held cart's solid shape and checks one captured fault plus empty
claims/bindings. Unexpected cart-test diagnostics fail teardown without weakening
the native log gate. Source catalogue: 96 native cases, all NotRun.

Cargo observation now exposes availability only after a fresh sample from its
active, enabled trigger on the bound cart. Disabling the component or losing the
volume cannot turn unknown cargo into an empty-load drive permission. Reenable
waits for a new sample; overflow stays latched across component toggles until a
fresh fixture is created. The drive callback and red warning both consume that
availability. Observation failures disable that module and remain visible rather
than repeating every FixedUpdate. One added native case checks fresh-sample drive
admission, and the overflow case checks disable/reenable retention. Source
catalogue: 97 native cases, all NotRun.

Conveyor setup now validates its enabled trigger and both permissions before
installing a live binding. A rejected setup cannot leave a force-producing
FixedUpdate path; corrected setup on that same unbound component is allowed.
Losing the bound observation volume disables the conveyor with a named error,
and the panel shows unavailability separately from an operational blockage.
Both volume components reject duplicate components on one object. A new native
case checks failed setup, zero drive, corrected binding and disable cleanup.
The optional Player smoke additionally requires the untouched cargo/belt sensor
baseline after its existing minimum 120 physics frames, before teardown; it
does not require a first-frame sample or change evidence thresholds. Source
catalogue: 98 native cases, all NotRun.

Cart motor setup now checks both observations and its dynamic, contact-enabled
body before installing drive authority. A rejected kinematic setup cannot later
gain force permission merely because that body becomes dynamic; it needs a
successful explicit binding. Losing collision detection also removes drive
permission. One new native case checks rejection, no force after changing the
body, corrected initialization and contact loss. Source catalogue: 99 native
cases, all NotRun.

The fixture panel now displays current and terminal material/cycle accounting,
grid delivery, reserve spending and spill. LocalCommandPort exposes the existing
immutable ProductionSummary, alongside its existing power view; presentation
adds no totals owner or result reconstruction. The outcome stays visible after
the live reactor/machines have been cleared. Existing command-port conversion
and reactor cases now check detached/final projections and conservation, and the
deadline fixture case checks final accounting remains readable. No cases were
added for labels alone; the declared native count stays 99, all NotRun. This is
a diagnostic summary, without a complete causal shift debrief or gate claim.

Worker cargo grouping now includes the pending recovery posture, whose same
physical ragdoll is still dynamic until the accepted standing handoff. A brief
logical Recovering state cannot make that observed load disappear. Held/slotted
workers remain excluded and upright workers are not ragdoll cargo. The existing
grouping native case now reaches a real pending recovery, checks the same 68 kg
group with its walking capsule off, and cancels the attempt. No extra case count
or material/health mutation owner is added; all 99 native cases remain NotRun.

Panel admission now disables machine/reactor buttons while the local worker
cannot interact, and disables pause/retry/belt-reset controls after terminal
closure. Restart and read-only feedback remain available. The power readout also
includes initial/generated units so its displayed totals can be reconciled with
reserve/spend/grid/spill. These are source UI corrections; no extra cases were
added for labels or enabled-state mirrors, and native GUI execution is NotRun.

The delegated source batch tightens physical and observation boundaries. Worker
rigs reject incomplete contact-capable setup before changing motion ownership,
and detect lost solid contacts, collision detection or physical head/suit-grip
ancestry while live. The existing worker-host failure route stops the fixture;
cleanup leaves the broken setting visible. Excluded-time impact samples are
cleared while paused/down or while a falling source is held, slotted or too light,
so an old velocity cannot create a new knockdown after release/resume. Five new
native source cases exercise these paths; test fixtures capture only their
expected diagnostics and fail on any extra fault.

Cart input is now admitted only with current drive permission and is cleared
when permission is observed lost. Reacquiring a handle, resuming a shift or
restoring a cargo sensor needs fresh drive input; pre-grip throttle cannot queue
a launch. Invalid cargo values and throwing observations disable drive once
before force math. Belt animation validates its complete same-owner, unique,
unnested, non-contacting parts before installing a live binding, including
inactive descendants. Three new native cases cover these boundaries; the older
handle-drive case now supplies fresh input after acquiring its lease.

Interaction control points must still belong to their registered equipment
hierarchy, so a detached nearby point cannot authorize or focus distant equipment.
Portable slot admission now recomputes its conservative enclosing bounds from
the current solid shapes rather than reusing the initial shape dimensions.
The metre-based offset and root-scale guard remain. Two new native cases check
detached controls and changed collider dimensions/centre against a real slot
obstacle. This supersedes the earlier note that placement dimensions were held
at registration. The integrated source catalogue declares 109 native cases,
all NotRun; no native discovery, compilation or execution occurred.

Three worker adapters now validate their required observations before installing
live fields, so rejected setup can be corrected without a partial binding. Walking
and down-crawl samples are cleared when pause/custody/recovery excludes motion;
fresh input is required after permission returns. Two additional native source
cases and the extended crawl case cover setup correction and resumed input. The
snapshot queued for the first native run declares 111 sandbox cases.

## Execution beginning after the gaming restriction was lifted

On 18 October at 16:25 UTC, `python -m unittest discover -s runtime/tools/tests -v`
reported 78 tooling cases: 77 passed, one skipped because this Windows account
could not create the symlink required by its negative fixture. This includes the
nine new runner provenance/cleanup cases. It is tooling evidence, not Unity or
gameplay evidence. Runner copies now compare fingerprints before launch and
retain the first failure/report through source-audit or timeout cleanup errors.

The offline verifier's 27 guard cases passed, then execution stopped at
`dotnet --version`: no compatible installed .NET SDK was found. No C# test or
scenario ran in that attempt. The failed SDK log is retained under
`runtime/dotnet/artifacts/sdk-version.log`. The already pinned supplementary
SDK may be prepared portably; no new project framework/package decision is made.

The pinned editor was then launched on snapshot `07075a41` in the disposable
sandbox workspace. Its Windows file identity and native startup log both report
6000.4.3f1 / 39d1a88d4dd1. Import exited 198 because no valid Editor license was
available; PlayMode discovery/execution, build and Player were NotRun. Inputs
were unchanged. First evidence: `runtime/out/sandbox-l1uyk5zk/report.json` and
`logs/import.log`. Cameron is activating Unity Hub; no license bypass is used.

The official pinned supplementary SDK 8.0.423 was acquired portably under ignored
`runtime/out/toolchains/`, with Microsoft's published SHA-512 verified. No global
installation/configuration changed. A frozen `07075a41` offline run compiled
without warnings and executed 712 cases: 711 passed and one failed. The failure
was a fixture assertion expecting a new commit when setting an already-powered
machine to powered. The corrected case now explicitly verifies NoChange and an
unchanged machine revision; no production rule was loosened. Original failure
artifacts remain under `runtime/out/offline-07075a41/`.

After integrating logical doors and that assertion correction, the offline
verifier executed **723 cases, all passed, zero skipped**, plus its scenarios,
27 guard cases and deliberate NUnit/scenario failure controls. Full source hashes
and results are in `runtime/dotnet/artifacts/summary.json`; its commit field is
the parent `07075a41`, so the recorded file hashes identify the uncommitted
candidate actually tested. This does not establish Unity physics.

The supplementary checker now compiles every declared production assembly and
all three test assemblies, using the exact installed Unity API files, the pinned
SDK and real NUnit/TestRunner DLLs. **21/21 assemblies compiled successfully**
with unchanged source. Its report is
`runtime/out/api-all-assemblies-01/api-compile.json`. TestRunner references came
from byte-identical bundled editor-template caches; this does not prove the
project resolved Test Framework 1.4.6, nor execute native tests. Its 22 tooling
cases passed. The separate combined-map runner's 16 fault fixtures also passed.

## Combined-map traversal extension

The owner's later instruction authorizes the combined map as gameplay input.
The derivative imports only the existing 437,436-byte collision/anchor FBX,
binding manifest, doors and collider-role table. It writes its own generated
scene under `Sandbox/Generated/CombinedMapTraversal.unity`; it leaves the retired
assembled map, source blends, room files and Claude's protected bake/importer
paths unchanged. Export provenance remains dirty/unreviewed, not promoted.

Logical doors now use the existing Interaction owner and command receipt stream.
Stable source IDs map into scoped logical GUIDs; 37 authored rows retain their
normal/evacuation defaults, and the sealed dock stays non-operable. Physical
bindings atomically apply epoch/revision projections and refuse stale/conflicting
deliveries. A bounded closure observation blocks characters and portable/ragdoll/
kinematic occupants without consuming the command sequence or toggling colliders
as a probe. Open threshold triggers remain focusable while unrelated triggers
do not occlude a target; solid walls still do.

The local scene reuses the worker controller and body/recovery owners. It starts
on the measured spine floor, uses actual imported mesh colliders, validates every
door/room anchor and collider AABB to 0.01 m, and retains debug material/shader
dependencies. A containment monitor stops escaped/runaway worker bodies visibly.
Connector proxies are not room floors. The condenser's six-metre ladder is not
implemented and no route-completion claim is made. The evacuation button is a
diagnostic exercise of the authored door transition, not a complete meltdown or
results flow. Art import remains Claude's separate pipeline in the same frame.

Eleven pure door cases passed within the 723 above. Eight new native source cases
cover physical bindings, occupied closure, focus and local delivery/lifetime.
The declared native catalogue is now 119; native discovery and execution remain
NotRun while import is blocked by licensing. Independent review and merge remain
pending for every contribution.

## Licensed native import and measured collision frame, 18 October

Unity Personal activation succeeded at 16:50 UTC in the exact 6000.4.3f1 editor.
The first licensed map import failed because `TestAssemblies` already injects
TestRunner references and the PlayMode asmdefs duplicated an explicit reference.
The explicit duplicates were removed. Actual installed package descriptors and
the native resolved lock report Test Framework 1.6.0 / NUnit 2.0.5; the profile,
manifest and lock now agree with those bundled versions under the bounded D-01
compatibility repair. No gameplay infrastructure package was selected.

The next import compiled, then correctly failed the one-centimetre coordinate
check by 185.4515 m. A separate native probe measured raw room anchors:
condenser `(1.6,-6,3.2)`, reactor `(0,0,-18.7)`, spawn `(8,0,-92.38)`.
This scoped collision FBX lands in `(x,z,y)`. The protected baked importer uses
`(-x,z,-y)`. Applying a 180-degree Y rotation to the generated derivative root
puts both in that existing placement frame. No source FBX, map file, protected
importer or tolerance changed. Failed reports/logs are preserved under
`runtime/out/combined-map-wyz4nga4`, `_7743wxj` and `xa85rijs` (each latter
suffix also has the `combined-map-` prefix).

Native preparation then **passed** at 16:59 UTC:
`runtime/out/combined-map-tp2zcdwj/report.json`. Unity imported the actual meshes,
created 152 contacts and checked their bounds plus 37 door / 13 room anchors.
Maximum error was **0.0002840849 m**. Original runtime and four map inputs stayed
unchanged. This is scene preparation, not PlayMode, Player or route completion.
The report identifies its exact candidate by source fingerprints; HEAD was still
`07075a41`, with the new source uncommitted.

At 16:58 UTC the expanded Python tooling suite reported **109 cases: 108 passed,
one Windows symlink-privilege skip**. These are tooling checks only. Read-only
contributor review caught a deferred HUD cleanup callback capturing the mutable
bootstrap worker field; it now captures the composed worker locally. Two native
composition cases cover evacuation/contacts and immediate teardown/restart.
The source catalogue now declares **121** native sandbox cases, execution pending.

## First native physics results, 17:11 UTC

Two static-door drift cases and an occupied evacuation-closure case brought the
source inventory to **124**. Door bindings retain owner-relative contact poses
and shape signatures; whole-model movement stays valid while child proxy drift
faults visibly. A new evacuation exercise checks every required closing doorway
before committing its once-only cause; retries do not reapply defaults or require
fresh clearance.

`runtime/out/sandbox-0ogu9odh` compiled but stopped before tests at the native
assembly graph check. This exact editor injects both test runners into all three
production Editor-only assemblies too. Native Bee response files confirm it;
the checker now expects precisely those injected edges for Editor-only groups,
retaining exact equality for all other references and pure-assembly checks.
The supplementary compiler models that same native behavior. Its latest frozen
report, `runtime/out/api-all-assemblies-02/api-compile.json`, passed all 21
assemblies against actual installed APIs/NUnit 2.0.5. The Python tooling suite
then reported **118 cases: 117 passed, one symlink-privilege skip**.

`runtime/out/sandbox-7qro63i0` passed native import/graph validation and executed
**all 124 cases: 73 passed, 51 failed, zero skipped**. Its native XML and logs
are retained. Most failures cascade from worker-rig setup rejecting a disabled
segment contact; agents are correcting construction/ownership validation and
strengthening the existing regressions. One door case fails on a newly created
walking controller's occupancy observation. Three context-machine cases assumed
machines started unpowered; their preconditions now explicitly isolate power
before exercising a power-on toggle. Two feedback cases incorrectly expected
setting an already-powered machine on to create a new commit; they now require
NoChange. The gauge case now allows actual animation time instead of assuming
ten headless frames imply visible elapsed time. These changes await rerun;
none of the 51 failures is claimed resolved by source inspection alone.

The 17:08 UTC refresh found `origin/main` still at `3853995c`; no new upstream
commit required integration. Protected map/importer paths remain unchanged.

## Native gameplay checkpoint passed, 17:36 UTC

`runtime/out/sandbox-6x_q3k7r` progressed to 86 passes / 38 failures. Most were
teardown guards: fixtures destroyed live required adapters before closing their
bootstrap owner. Teardown now closes that owner first; unexpected adapter-disable
guards remain intact. Both bootstraps also close their worlds on application quit
before hierarchy callbacks. The combined-map restart test explicitly expects its
Ready log for each new epoch. Three immediate interaction queries now synchronize
both physics and interpolated Transform poses during test-only teleports, retaining
the actual runtime reach/occlusion policy.

`runtime/out/sandbox-albvxyeq` then reached 121 passes / three failures. The actual
remaining defects were current support observation and normal-pose synchronization.
Walking now checks nearby walkable support, respecting skin distance, slope and
ignored collisions, rather than relying only on a previous Move's grounded flag.
The walking capsule has no minimum-movement cutoff. Normal FK computes one
coherent segment pose before writing/synchronizing the kinematic hierarchy;
dynamic ragdolls retain their separate physics ownership and interpolation.
Existing tests now require stable landings, immediate loss of removed/ignored
support, native/visible pose agreement and the original one-centimetre joint bar.

The next exact-editor run **passed all 124 native PlayMode cases, zero skipped**,
with import and the 18-production-assembly graph check also passed:
`runtime/out/sandbox-ue0fz1ym/report.json` and `PlayMode.xml`. Original source stayed
unchanged during the run; the candidate hash is
`26feca1aa7838daf71abea9f6b35aedbdc3be93be218ce865fd2e55c993e6b73`.
Build/Player remain NotRun in that report. All earlier failures remain preserved.
The latest tooling run separately passed 123 / 124 cases, with the one Windows
symlink-privilege skip. No FPS, minimum-spec, visual, multiplayer or gate acceptance
is inferred from these results; per-frame synchronization cost is unmeasured.

The first URP dependency trial uses a separate frozen snapshot, not this passing
workspace. `runtime/out/urp-resolution-_wetgkim` resolved the bundled URP/Core/
ShaderGraph/config 17.4.0 packages and compiled their SDKs, then failed the strict
project graph check on the newly injected mandatory uGUI references. Earlier
ShaderGraph compiler diagnostics were followed by native API updating/recompilation;
they remain in the failed log. No renderer or Player pass is claimed. The actual
lock selected uGUI 2.0.0, Collections 6.4.0, Burst 1.8.29, Mathematics 1.3.3,
Searcher 4.9.4, Mono-Cecil 1.11.6 and test-framework.performance 3.4.0 as renderer
dependencies. The canonical project has not adopted them at this checkpoint.

## URP native trial in progress, 17:49 UTC

The 124-case gameplay checkpoint was saved as commit `59b4b80b`. The next
bounded trial now declares the already owner-selected URP 17.4.0 renderer,
its actual resolved dependency lock, Linear colour, and one default pipeline
inherited by every quality level. Only `CriticalShift.Sandbox.Editor` declares
the two required Core/URP runtime SDK references. The native graph checker
accounts for the precisely observed uGUI auto-references on engine assemblies;
pure assemblies still prohibit engine/SDK edges.

`runtime/out/sandbox-l_x_i_qa` failed native compilation on two helper API
errors: an ambiguous `PackageInfo` name and protected global-settings lookup.
The helper now qualifies the package type and uses the public
`EditorGraphicsSettings.TryGetRenderPipelineSettingsForPipeline` API, which
supports inspecting an inactive registered pipeline. The failed log is retained.

The supplementary compiler now accepts an explicitly supplied native SDK
context only when its editor identity, manifest and selected lock match the
canonical profile. It hashes the four actual Core/URP/uGUI SDK binaries and
their package descriptors, and audits them again after compilation. It neither
builds nor modifies that context and makes no binary-freshness claim. Its
`runtime/out/api-urp-first/api-compile.json` report passed all 21 assemblies.
The tooling suite reported 144 cases: 143 passed and one Windows symlink
privilege skip (`runtime/out/tooling-urp-context.log`).

The corrected native trial is now attempting import, all 124 PlayMode cases,
Win64 build and the existing headless Player lifecycle smoke. Canonical runtime
inputs remain frozen during that run. Native renderer assets/settings have not
yet been copied back, so the standalone foundation runner still needs that
serialization step before its new URP requirement can pass. A parallel review
also identified a missing serialized emissive material variant root; Player
startup evidence alone cannot establish correct emissive pixels.

## Initialized URP result and corrective work, 17:56 UTC

`sandbox-3p2qy93a` completed native scene preparation with exit zero, but its
strict log check correctly rejected the two initial SDK `GUID` compile errors
that Unity's API updater subsequently repaired. The separate retained
`runtime/out/urp-initialized-continuation` passed a new process's clean Prepare,
then executed all 124 cases: **122 passed, two failed, zero skipped**. The XML
identifies `MovingCartContactCausesOneKnockdownEpisode` and
`RecoveryPreservesDownLookAndUnconsciousWorkersCannotLook`; both encountered a
ragdoll segment exceeding the unchanged physical speed guard before cleanup.
Build and Player were not reached. This is not a clean URP gameplay pass.

The safety diagnostic now reports measured linear/angular speeds and their
limits. A cross-review is investigating the physical cause. The initial-import
logs and failed XML remain available. Package initialization and a mandatory
separate clean native acceptance process are being made explicit; the critical
log validator is not being relaxed.

The same initialized editor separately passed `FoundationBuild.Prepare`
(`runtime/out/urp-foundation-settings-prepare.log`). Its native serialized
renderer pair, global settings, default volume profile and Graphics/Quality/
Player/Editor settings were copied into canonical runtime sources with their
Unity-generated GUIDs. No YAML was authored by hand. The ordinary and emissive
Lit material-template proposal is now implemented in source; it still needs
native generation, serialization and Player verification.

Door cross-review found that the 2.4m focus threshold did not cover the full
4.96m reactor blast leaf. Closure now observes the union of both shapes from
their current geometry and transforms without briefly enabling the open leaf.
The new elevated-occupant regression covers box/imported-mesh contacts and map
translation/rotation, bringing the declared native inventory to **125**; it is
NotRun. A conflicting evacuation request now records the already-active actual
cause in the trace, with the existing pure regression strengthened. These new
changes are not covered by the earlier 124-case pass.

## Native preparation corrections and updated source checks, 18:16 UTC

The 17:58 offline rerun passed **723/723**, including the strengthened actual
evacuation-cause trace assertion; previous artifacts were preserved under
`runtime/out/offline-before-cause-test`. Its current summary remains in
`runtime/dotnet/artifacts/summary.json`.

Upstream `main` remained `3853995c`. Claude's open PR #110 had newer commits on
its own branch, so those commits through `320d2256` were integrated in `ef0d5ffb`
before further validation. Protected bake/importer paths match that upstream
branch exactly; this task made no authored change to them. Any review PR must
keep that dependency explicit rather than reintroducing the earlier bake code.

`runtime/out/sandbox-9l6muhyd` stopped during package resolution on Windows EPERM
while renaming the ShaderGraph cache directory; no compilation/tests ran. The
separate fresh `sandbox-47ihoem1` completed package initialization, preserving
the original strict Failed SDK diagnostics, exact known updater classification,
updated source hashes and unchanged first-party code identities. Its separate
Prepare passed renderer/assembly checks but stopped at the material helper.
URP owns a hidden `AssetVersion` subasset, contradicting the helper's one-object
assumption. The helper now permits only that exact native hidden metadata type
and rejects other subassets. Native inspection also showed the material importer
derives `_EMISSION` from its emissive flags; creation now establishes those flags
before import. Neither correction is presented as a new native pass yet.

Cross-review corrected the new door regression's clear-space fixture: each
shape branch starts from independent root TRS, and its clear occupant is beyond
the complete conservative observation volume at every tested yaw. Runtime
closure remains conservative. The optional development Player capture now uses
the built-in Screen Capture/Image Conversion 1.0.0 modules, requires actual
owned-camera render callbacks, decodes the native PNG and publishes a new file
before normal smoke teardown. Rendered execution remains NotRun.

`runtime/out/api-urp-capture-materials/api-compile.json` passed all **21** authored
assemblies against actual pinned SDK references. Tooling subsequently passed
**176/177**, with the one existing Windows symlink-privilege skip
(`runtime/out/tooling-urp-pin-audits.log`). Initialization rejects other managed
exception headers, and sandbox/foundation re-audit native selected pins and
descriptor hashes after each clean phase and at final completion. The original
critical log validator is unchanged. No native physics threshold was relaxed.

## Material serialization and worker safety candidate, 18:34 UTC

The fresh `sandbox-jrocmn4e` attempt preserved another material-helper failure:
the native URP `AssetVersion` object is not classified as an `IsSubAsset` by
this editor. A separate diagnostic inspection in that retained workspace
confirmed its exact type, assembly, hidden flags and owning asset path. The
helper now verifies that owning path instead. The initial diagnostic probe's
obsolete-API warnings remain recorded; its corrected second process and a
separate `SandboxSceneBuilder.Prepare` passed strict native log checks. Their
logs are `urp-native-material-probe-02.log` and
`urp-native-material-prepare-fixed.log` under `runtime/out`. The two actual
Unity-generated ordinary/emissive templates and their metadata are now source
assets. This warm diagnostic preparation is separate from a fresh full run.

Five additional native processes each repeated the two earlier failing ragdoll
cases in that retained diagnostic project: **10/10 passed**. The report is
`runtime/out/ragdoll-measured-repeat/report.json`. That project's worker code
predates the new motor changes below. These repetitions did not reproduce the
intermittent speed faults and do not establish that they are resolved.

The worker motor now reports a saturated walking-support query through its
existing world owner's failure callback. It latches the failure, clears pending
motion, disables its driver before synchronous cleanup, and cannot proceed into
`CharacterController.Move` after the fault. Getter and Update regressions use
real native query saturation and require one report, stopped world, cleared
bindings and no subsequent movement. The declared inventory is now **127**;
these two cases and the full-leaf closure case are pending native execution.

Worker normal poses and standing recovery now commit complete precomputed poses
through Rigidbody position/rotation setters, then call the pinned editor's
public `PublishTransform` API in setup-cached hierarchy order. Direct Transform
writes to those jointed bodies were removed. Unity's installed documentation
distinguishes this physics-to-Transform publication from `SyncTransforms` and
warns against direct Transform movement of jointed kinematic bodies. This fixes
that documented synchronization hazard; it is not a proven sole explanation for
the earlier intermittent speed faults. Forces and safety limits are unchanged.
The supplementary matching-SDK compile passed all **21 assemblies** at
`runtime/out/api-urp-publish-pose/api-compile.json`. Fresh native tests, build,
headless Player and rendered capture are next. None is claimed here yet.

## Hierarchy fence and foundation fixture correction, 18:40 UTC

`sandbox-mheyrj1u` stopped before compilation on a Windows EPERM rename of its
Burst package cache. Its Failed report and native log remain intact; the original
runtime input fingerprint was unchanged. This attempt ran no gameplay tests.

The separate `wp01-7vt5fx24` foundation run completed package initialization and
clean preparation, then passed all **12 EditMode cases**. All **nine PlayMode
cases failed**: their explicit `LogAssert.NoUnexpectedReceived` calls rejected
the normal READY/STOPPED messages which the same tests assert. The fixture now
expects those exact normal messages before emission, with anchored version/build,
frame and error-bit checks. All original state/count assertions and unexpected-log
checks remain; no foundation runtime behaviour or test identity changed. Build
and Player were not reached in that failed run.

Cross-review found that reparenting a segment or intermediate node inside a
worker could invalidate the cached publication order while preserving earlier
binding checks. The rig now fences its complete setup ancestor chains up to its
controller root before pose preparation/publication. Whole-worker/fixture motion
and reparenting remain valid. Two real-host regression cases require no pose
writes and once-only stopped-world cleanup after internal hierarchy mutation.
The sandbox inventory is now **129**, pending native execution.

Sandbox Development builds now temporarily enable strict shader variant matching,
restore the prior setting in `finally`, and emit a build-GUID-linked strict-mode
marker. This makes a missing variant visible instead of silently choosing a
nearby one. The first rendered run is still pending and will be recorded as
appearance/startup evidence rather than final lighting or performance acceptance.

## Measured native failures and isolated comparison, 18:55 UTC

`sandbox-n92p66j2` completed initialization and separate clean URP preparation.
Its actual XML reports **127 passed, two failed, zero skipped** out of 129. The
new full-leaf closure, saturated-support and hierarchy-mutation regressions all
passed. `ReleasedOrStaleHoistInputCannotRaiseTheNextLeaseTarget` encountered a
patient left-forearm angular speed of **28.2995949 rad/s** (linear 1.67764533 m/s).
`AlertDownWorkerCrawlsWithOneMotionOwnerAndStopsDuringPause` encountered a local
right-forearm angular speed of **26.237051 rad/s** (linear 1.775384 m/s). Both
crossed the unchanged angular guard of 25, stopping their world. Build and
Player were not reached. Package descriptor/pin and original-source audits passed.

The first fault occurs around a released body's landing; the crawl case fails
during its initial settling period before crawl input. These observations do not
justify changing crawl or hoist command rules. The installed Unity documentation
explicitly recommends increased velocity-solver iterations for ragdolls moving
too much after collisions. The existing per-body angular cap is applied before
the physics step and does not guarantee a post-solver cap.

A separate ignored experiment retains the original native logs/XML/report and
compares the four affected historical case identities over three predeclared
rounds, baseline position6/velocity1 versus position6/velocity10. It temporarily
instruments only the retained diagnostic workspace, samples native velocities
and joint-anchor separation at the existing safety boundary (including a fault
sample), and writes one external JSON per fixture at shutdown. It does not log
per frame, alter guard limits, clamp observed velocities, change forces/masses,
or enable nonphysical joint projection. Original sources and environment are
restored afterward. These measurements are diagnostic, not full-suite or Player
acceptance, and no result is claimed before the rounds complete.

`wp01-zv0bm4w7` separately failed before compilation on another Windows EPERM
ShaderGraph cache rename. Its failure and unchanged-source audit remain intact.
An explicit one-off cache-seed wrapper is prepared: only the already initialized,
matching SDK `Library/PackageCache` is copied into a fresh first-party workspace,
with complete before/after tree hashes, exact descriptors/pins and provenance.
The unchanged native runners still compile/import and perform their strict
tests/build/Player/audits. This will not be described as fresh cold package
extraction; it has not executed yet.

## Completed velocity comparison and opt-in Player exercise, 19:05 UTC

`runtime/out/ragdoll-solver-comparison-01/report.json` completed all 24 declared
single-case native processes. Baseline6/1 passed **11/12** with peak worker spin
25.2723541 rad/s and maximum sampled anchor separation 0.0450824 m. Velocity10
passed **9/12**, with peak spin 28.3686447 rad/s and maximum sampled separation
0.0577769 m. Those angular and separation maxima are independent observations,
not proof that they occurred on the same joint or frame. The velocity-only
setting is not supported as a correction and was not integrated. Original
source/environment, prior native artifacts and canonical inputs were restored
and verified unchanged. Guard limits remain untouched. Position10/velocity1 is
the next separate controlled comparison.

The explicit Development Player exercise is now integrated in source, with its
own new internal driver and no new package or rule owner. With both smoke and
exercise flags it rejects ID106 through actual spatial admission, grabs ID102
through the real host, measures native carry, drops the exact lease and observes
gravity-driven release before ordinary zero-claim teardown. It verifies typed
trace identities/results and complete immutable fields for those two batches;
all eight containers retain the ordinary existence checks. There are no direct
pose/velocity/clock/material writes. Stage105 completion, hard limits of 180
fixed steps/15 real seconds, failure markers and unfinished-teardown cancellation
checks are explicit. Normal play/editor/passive smoke remain inactive for this
driver. All **21 assemblies** passed matching-SDK API compilation at
`runtime/out/api-urp-player-exercise/api-compile.json`; native execution of the
new flag remains NotRun. Separate ignored validation requires every ordered
exercise marker plus normal Player smoke and a missing-smoke rejection trial.

Read-only preflight of the one-off SDK cache seed now passes all 20 selected
packages. Eight versioned builtin descriptors contain only Unity's extra
40-hex `_fingerprint`; the seven module descriptors are semantically unchanged.
The wrapper permits only that observed optional generated field, compares every
remaining field with the installed vendor descriptor and retains both raw hashes.
No native cache-seeded run has executed yet.

## Completed solver/origin comparisons and reviewed diagnostic policy, 19:29 UTC

The three reports below each completed **24 single-case native processes**:
the same four declared case identities, three rounds and two variants, in the
already initialized `sandbox-n92p66j2` workspace at baseline `c37905f6`.
Every report is `CompletedWithFailures`, with `acceptance_status=NotRun`, zero
skipped and zero inconclusive cases. These are separate warmed-project diagnostic
comparisons, not fresh imports, a full suite, Player execution or performance proof.

- [Comparison 01 report](../out/ragdoll-solver-comparison-01/report.json):
  18:52:56Ã¢â‚¬â€œ19:03:46 UTC; position 6 / velocity 1 versus position 6 / velocity 10.
- [Comparison 02 report](../out/ragdoll-solver-comparison-02/report.json):
  19:05:25Ã¢â‚¬â€œ19:16:05 UTC; position 6 / velocity 1 versus position 10 / velocity 1.
- [Comparison 03 report](../out/ragdoll-solver-comparison-03/report.json):
  19:16:21Ã¢â‚¬â€œ19:27:08 UTC; unchanged 6/1 solvers at the original versus near test roots.
  WorkerPhysics roots were (2500,0,2500) versus (100,0,100); WorkerDrag roots were
  (4000,0,4000) versus (150,0,150). Only the two fixture root literals changed.

Counts below are exact; displayed telemetry is rounded from the report's native
float values. The raw per-body measurements, timestamps, commands, XML and logs
remain in each evidence directory.

| Comparison | Variant | Passed / failed / skipped | Peak linear m/s | Peak angular rad/s | Maximum joint-anchor separation m |
| --- | --- | --- | --- | --- | --- |
| 01 | Baseline 6/1 | 11 / 1 / 0 | 6.38478756 | 25.2723541 | 0.0450823829 |
| 01 | Velocity 6/10 | 9 / 3 / 0 | 5.54994488 | 28.3686447 | 0.0577769391 |
| 02 | Baseline 6/1 | 11 / 1 / 0 | 6.15257978 | 25.2000504 | 0.0446592830 |
| 02 | Position 10/1 | 6 / 6 / 0 | 4.47526169 | 27.3606834 | 0.0398721769 |
| 03 | Far roots 6/1 | 9 / 3 / 0 | 6.34169722 | 26.8237858 | 0.0454107784 |
| 03 | Near roots 6/1 | 10 / 2 / 0 | 6.23770666 | 27.0270863 | 0.0477398746 |

All comparison failures retained a native 25 rad/s guard fault. The released/stale
hoist case accounted for every failure except the position10 variant's three
additional `MovingCartContactCausesOneKnockdownEpisode` failures. The separate
angular-speed and separation maxima are not same-body/same-frame correlations;
samples occur at the existing safety boundary, including the fault sample, and
early faults censor the rest of that run. None of these comparisons supports
integrating a solver increase or claiming that near origins resolve the problem.
Production solvers remain position 6 / velocity 1; the original kilometre-origin
fixtures remain unchanged. Physical stability and far-origin support remain
unverified.

All three reports verify `original_code_restored`, `original_evidence_unchanged`
and `canonical_inputs_unchanged` as true. Their before-comparison and every
post-process package pin/descriptor audit passed; comparison 03 additionally
verifies `production_builder_unchanged=true`. The experiment finally blocks
restore their process environment and retained source bytes. Original
`sandbox-n92p66j2` report/XML/log hashes are recorded in each report and remain
unchanged. No failed process or original full-suite result is relabelled Passed.
Each comparison records its own frozen canonical fingerprint; comparison 01's
fingerprint differs from 02/03 because canonical source advanced between runs,
not during a comparison.

The primary author and validation-tooling subagent reviewed a different diagnostic
criterion before integration. Commit `4822787d` replaces the authored raw-spin
failure condition with independent limits of **25 m/s** and **312.5 J/kg** specific
rotational kinetic energy. The latter equals `0.5 * 25Ã‚Â²`, the specific
translational energy at 25 m/s; it is not a bound on combined translational plus
rotational energy. It remains an authored, unaccepted fixture budget under D-09,
not a GAME_SPEC numerical requirement or production safety limit.

The observer calculates `0.5 * (Ix*wxÃ‚Â² + Iy*wyÃ‚Â² + Iz*wzÃ‚Â²) / mass` in the native
principal-inertia frame, using inverse(body.rotation * inertiaTensorRotation).
Dynamic mass must be finite and positive; moments finite and nonnegative;
body/tensor rotations valid. Unity's zero moments encode infinite inertia, so
meaningful projected motion on such an axis fails. Only the explicit projection
roundoff bound `8 * float_machine_epsilon * max(1 rad/s, |world omega|)` is allowed
on those zero axes. Positive-axis motion contributes in full. Raw angular speed
and peak diagnostics remain, with double magnitude/energy arithmetic; finite
pose/velocity checks, containment and once-only owner failure/teardown remain.
This observer writes no physical state and changes no solver, force, mass,
damping, cap, contact, joint projection, input or fixture origin. It does not
establish a physical motion correction, energy conservation, surface-speed
safety, far-origin support or gameplay feel. The original 25 rad/s failures stay
Failed under the policy that produced them.

Three new real-Rigidbody guard cases distinguish small/large native inertia at
the same 30 rad/s, a nonidentity principal frame, and legal zero/infinite inertia
with rotational constraints. Their exact identities in the parent-owned catalogue
bring the inventory from 129 to **132**. The supplementary SDK check at
[`api-urp-energy-observer/api-compile.json`](../out/api-urp-energy-observer/api-compile.json)
passed all **21 assemblies** and the static source checks, with
`source_unchanged=true`, during 19:29:03Ã¢â‚¬â€œ19:29:15 UTC. Its report records HEAD
`de2a6de5` and the working input fingerprint
`ffdb28c63fe1dbafb40e9f5e1e55417f4f52976dd7b341410bf3edb81cfb08de`;
the reviewed energy changes were then committed as `4822787d`. This is API/source
evidence, not Unity execution. The fresh 132-case native run and requested
build/Player phases are in progress using the explicitly disclosed preinitialized
SDK cache; no result or acceptance for them is recorded here yet.

Upstream Claude commit `282f9dfb` was integrated by merge `de2a6de5` before this
checkpoint. A read-only diff against that upstream commit is empty for
`sections/facility-assembly/unity/` and
`runtime/unity/Assets/CriticalShift/Content/Editor/`: this task has no authored
changes in those protected paths. Independent gate, art and human play acceptance
remain unassigned/unmet; contributor source review does not grant them.

## Cache-path failure and constrained-inertia setup checkpoint, 19:44 UTC

The first cache-seeded full run, [`seeded-5_xxebrz/sandbox-7hdy57_k`](../out/native-cache-seed/seeded-5_xxebrz/sandbox-7hdy57_k/report.json),
used source `4822787d` during 19:29:32Ã¢â‚¬â€œ19:34:04 UTC. It remains **Failed in
package initialization**, before Prepare or any native test, build or Player.
Unity returned zero and its strict log validator passed, but the separate
initialization exception check rejected six managed `DirectoryNotFoundException`
or `IOException` headers. These referenced SDK files that were present, including
the Collections `System.Runtime.CompilerServices.Unsafe.dll` at a 284-character
absolute path, versus 247 characters in the initialized seed. The two referenced
Core USS files were present at 273/267 characters, versus 236/230 in the seed.
This is the observed long-path failure context, not a general SDK defect or a
license failure; its original diagnostics and Failed status are retained.

The [cache provenance](../out/native-cache-seed/seeded-5_xxebrz/cache-seed-provenance.json)
records an exact seed-before/after and copied-target cache tree digest of
`cf0cbaaeb63e17d6b3bdc8a73c5cd3131065ee954e408de917ced5f412baeb88`:
14,863 files, 1,353,074,735 bytes and 1,000 directories. Seed source, runner source
and native helpers were unchanged; the target cache still matched the seed, and
the final selected-package audit passed. `VerifiedCopy` describes the copy,
not a successful native run. Only `Library/PackageCache` was seeded; no first-party
compiled code or other Library state was copied into the fresh workspace.

The original one-off wrapper is preserved as
[`run_seeded-original.py`](../out/native-cache-seed/seeded-5_xxebrz/run_seeded-original.py).
The reviewed local wrapper change passes its explicit output parent to each of
the three unchanged native runners, instead of nesting their output below the
wrapper artifact directory, and records `native_output_parent`. The new attempt
explicitly used `--out runtime/out`. Fresh disposable workspace creation, cache
verification, strict initialization/Prepare checks, selected-pin and source
audits remain in place; this change adds no automatic retry or diagnostic waiver.

The separate short-path [`sandbox-sd91_t34` report](../out/sandbox-sd91_t34/report.json),
source `e4f0c342`, ran during 19:35:14Ã¢â‚¬â€œ19:40:47 UTC. Initialization completed with
return code zero, a Passed strict log and no managed exception headers. Strict
Prepare passed. Native PlayMode returned two with **131 passed / one failed /
zero skipped / zero inconclusive, total 132**. The sole failed identity in the
[original XML](../out/sandbox-sd91_t34/PlayMode.xml) is
`CriticalShift.Sandbox.Tests.FacilityPhysicsTests.PhysicsMonitorAcceptsHealthyNativeInfiniteInertiaConstraints`:
its setup expected angular speed `2 +/- 0.0001`, but observed `1.82574308`, before
the later safety sample. Every other case, including the existing ragdoll cases
and the other new energy cases, passed under the current diagnostic policy.
The overall result remains **Failed**, and build/Player remain **NotRun**.
After-import and final package audits passed, `source_unchanged=true`, and the
separate [short-path cache provenance](../out/seeded-whmsat5t/cache-seed-provenance.json)
again records the exact cache digest above and unchanged seed source.

Two single-case native probes used that retained workspace with fresh external
result/log paths. Both saved, hashed and restored the test source bytes. Their
instrumentation temporarily bypassed the early angular-speed assertion to
collect the actual native frames and reach the monitor assertion; this diagnostic
instrumentation is not the canonical test change.

| Probe | Native result | Observed world angular velocity (rad/s) | Angular velocity in full native principal frame (rad/s) | Monitor observation |
| --- | --- | --- | --- | --- |
| [Original setup](../out/energy-constraint-native-probe/report.json), 19:42:31 UTC | Exit 2; 0/1 passed, 1 failed | (0.04470525, 1.60717082, 0.86506718) | (0.29128820, 1.66666877, -0.68608016) | Infinite-inertia-axis fault |
| [Published pose](../out/energy-constraint-native-probe-published/report.json), 19:43:28 UTC | Exit 0; 1/1 passed | (0.64977843, 1.33438015, 1.34060442) | (-0.00000098, 2.00000119, -0.00000068) | No fault; 2.0000013048566305 J/kg |

The [first native fields](../out/energy-constraint-native-probe/native-fields.json)
and [published-pose fields](../out/energy-constraint-native-probe-published/native-fields.json)
record the same body rotation, principal tensor rotation, `(0,1,0)` tensor and
requested world angular velocity. The first probe's recorded energy zero is the
retained healthy-stage peak before the later fault; it is not a measurement of
zero rotational energy for its faulting motion. The controlled difference
supports publishing the test's native pose before applying the constrained
velocity setters. It does not establish a general Unity bug or correct the
earlier physical motion/far-origin concerns.

Both probe reports record `source_restored=true`, with original test-source
SHA-256 `4dcf765b4c35b6e6a3e34dfd296e5737995ac283371365b0dd07e1eb5a52460a`.
The original full-run report/XML/logs were not targeted or relabelled by the
probes. A before/after hash audit of all those original evidence files was not
instrumented, and the retained workspace's compiled Library was not restored.
The failed full-run evidence and failed diagnostic probe remain failed.

Commit `6a550c00` adds only a comment and one `body.PublishTransform()` call to
the constrained-inertia test, after assigning the body rotation and before the
tensor, constraint and angular-velocity setters. It retains the original angular
assertion, all later assertions/tolerances, rotations, tensor, constraints and
guard policy. Production motion code is unchanged. The matching-SDK
[`api-urp-energy-published-pose` check](../out/api-urp-energy-published-pose/api-compile.json)
passed all **21 assemblies**, with `source_unchanged=true`, at 19:44:05Ã¢â‚¬â€œ19:44:19
UTC; it performs no native Unity execution. The subsequent
[`tooling-energy-published-pose.log`](../out/tooling-energy-published-pose.log)
records **177 tests: 176 passed, one Windows symlink-privilege skip**, ending
19:45:51 UTC. A fresh short-path, SDK-cache-only seeded full native run,
`sandbox-hwcmv9_t`, is in progress on `6a550c00`; no full-suite/build/Player result
for that candidate is recorded here yet.

[Draft PR #111](https://github.com/CameronNel/critical-shift/pull/111) is stacked
on Claude's PR #110/upstream `282f9dfb`; the authored diff in both protected paths
above remains empty. The pushed `e4f0c342` checkpoint's
[CI run 39159560168](https://github.com/CameronNel/critical-shift/actions/runs/39159560168)
completed successfully on both Windows and Ubuntu. Those source/offline jobs do
not execute Unity and predate `6a550c00`. Node 20 deprecation and Ubuntu-image
notices are nonblocking annotations, not native validation results. Independent
review, human play/art acceptance and the unaccepted diagnostic trial budget
remain open; no historical failed evidence is promoted by these checkpoints.

## Full native pass, strict build and Null-device Player checkpoint, 19:56 UTC

The [completed `sandbox-hwcmv9_t` report](../out/sandbox-hwcmv9_t/report.json)
records source `6a550c00`, 19:44:06Ã¢â‚¬â€œ19:51:22 UTC. Package initialization completed
with a Passed strict log and no managed exception headers; separate strict
Prepare passed. The [native PlayMode XML](../out/sandbox-hwcmv9_t/PlayMode.xml)
contains **132 discovered/executed, 132 passed, zero failed/skipped/inconclusive**,
including the constrained-inertia case with its original assertions retained.
The Win64 build passed with GUID `9067140286ae41f0b6c6c912c7a67d75`; its
[build log](../out/sandbox-hwcmv9_t/logs/build.log) records the matching
`CS_SANDBOX_BUILD_STRICT_VARIANTS ... enabled=1 target=StandaloneWindows64`
and successful build markers. The executable SHA-256 is
`748b8feff0cf8e727ed412006cfe11f0591bdfec6bd5634e89acacae0ab8b38e`.

The same run's headless Player exited **20** before fixture setup completed:
the [original Player log](../out/sandbox-hwcmv9_t/logs/player.log) retained the
material-template validation exception. Consequently, the full candidate remains
**Failed**, despite its Passed tests/build. All after-import, after-PlayMode,
after-build and final selected-package audits passed, and
`source_unchanged=true`; no failed phase has been relabelled.

The separate [graphics diagnostic 01 report](../out/player-graphics-diagnostic-01/report.json)
executed the **unmodified same executable**, with that exact SHA and build GUID,
in graphics-enabled batch mode at 960Ãƒâ€”540. Existing passive-smoke validation
passed: exit zero, **120 frames / 2,403 ms**, zero errors, 293 meshes, initially
10 bindings and 31 bodies. Bindings, bodies, objects, claims, timers and
connections all reached zero at cleanup. This is a separate graphics startup
and passive-smoke diagnostic; it supplies no captured-image or active-exercise
evidence and does not override the full candidate's failed headless phase.

The incremental [material-detail probe](../out/player-material-null-probe/report.json)
built a different diagnostic Player in the retained workspace and again exited
20. Its added exception detail measured `device=Null`, the expected
`Universal Render Pipeline/Lit` shader name, non-null distinct material references,
both expected shader references, no ordinary-material keywords, exactly
`_EMISSION` on the emissive material, `BakedEmissive` GI flags and the enabled
emission keyword. **Only `emissionProperty=False`** failed this predicate set.
This narrows the observed headless setup issue to `_EmissionColor` property
reflection; it is not evidence that all rendering is correct.

The separate [precise-fix probe](../out/player-material-null-fix-probe/report.json)
rebuilt with only the proposed Null-device property-inspection condition and
guarded lamp color write. Its
[smoke validation](../out/player-material-null-fix-probe/smoke-validation.json)
passed headless: build GUID **`67f36e5ed69c475093939632bb8c2564`**, exit zero,
**120 frames / 2,406 ms**, zero errors, 293 meshes, initial 10 bindings/31 bodies
and every cleanup counter zero. It is a **different diagnostic build**, not the
original full candidate or a fresh complete native/build/Player validation.
Both probe reports retain `acceptance_status=NotRun`, restore the original
`SandboxPrimitives.cs` bytes and record
`original_build_and_evidence_unchanged=true` for their instrumented original
executable, report, XML and log hash set. Original source SHA-256 is
`ccf8afc1d3bff2d4f58d8656f7692f3940b86df06f5afca5e596f4428b56a259`.
This check does not claim restoration of the retained compiled Library or an
audit of every original build-data file.

Commit `6554abef` changes only two sites in `SandboxPrimitives.cs`. Property
reflection remains required in the Editor and every graphics-enabled Player;
only a Null-device Player can pass validation without `_EmissionColor` property
reflection reporting success.
Shader/material identities, distinct references, exact keyword combinations and
emissive GI checks remain required in every device mode. The lamp's
`SetColor("_EmissionColor", ...)` is conditional on `HasProperty`. The facility
subagent's independent source review approved this exact scope; it does not
constitute independent gameplay/art gate acceptance. A fresh full 132-case
native run, strict build/headless Player and supplementary API check on
`6554abef` are in progress, with no result recorded at this checkpoint. Earlier
failed full runs, probes and solver/origin comparisons retain their status; no
physical motion or far-origin fix is claimed.

## Completed sandbox gameplay checkpoint, 20:05 UTC

The full [`sandbox-zxh6eap1` report](../out/sandbox-zxh6eap1/report.json) is
**Passed** on commit `6554abef`, 19:55:45Ã¢â‚¬â€œ20:02:42 UTC. Explicit package
initialization completed with a Passed strict log, no managed exception headers
and unchanged first-party code; the separate strict native Prepare passed.
The [PlayMode XML](../out/sandbox-zxh6eap1/PlayMode.xml) contains **132 passed,
zero failed/skipped/inconclusive**, with every declared case executed. The Win64
build passed with GUID **`49da467f5ff346359e6d8a500d21ef38`**, and its
[build log](../out/sandbox-zxh6eap1/logs/build.log) records strict shader-variant
matching enabled for that GUID and `StandaloneWindows64`.

The same build's [headless Player log](../out/sandbox-zxh6eap1/logs/player.log)
passed the unchanged passive-smoke validator: exit zero, **120 frames / 2,411 ms**,
zero errors, 293 meshes, initial 10 bindings and 31 bodies. Bindings, bodies,
objects, claims, timers and connections all reached zero. Native source audit
records `source_unchanged=true`; after-import, after-PlayMode, after-build,
before-success and final selected manifest/lock/descriptor audits all passed.

This run used the explicit **SDK `Library/PackageCache` seed only**, not a cold
package extraction. Its [seed provenance](../out/seeded-99vjlaik/cache-seed-provenance.json)
records `VerifiedCopy`, unchanged seed source, an exact target-cache match after
native execution and unchanged canonical runners/native helpers. The cache tree
remains `cf0cbaaeb63e17d6b3bdc8a73c5cd3131065ee954e408de917ced5f412baeb88`,
14,863 files / 1,353,074,735 bytes / 1,000 directories. No seed Assets, Packages,
ProjectSettings, other Library folders, ScriptAssemblies or first-party compiled
code were copied. Compilation, preparation, tests, build, Player and audits ran
in the fresh scoped workspace; prior extraction and initialization failures
retain their original status.

The supplementary [`api-urp-null-property` report](../out/api-urp-null-property/api-compile.json)
passed all **21 assemblies** on the same commit during 19:55:44Ã¢â‚¬â€œ19:55:58 UTC,
with source unchanged and `native_unity_execution=false`.
[CI run 39161045390](https://github.com/CameronNel/critical-shift/actions/runs/39161045390)
also completed successfully for both Windows and Ubuntu at `6554abef`; those
source/offline jobs are separate from the native evidence above.

The first same-build capture attempt,
[`capture-nj3lt470`](../out/player-render-validation/capture-nj3lt470/report.json),
remains **Failed**. Graphics-enabled batch mode reached Player Ready but no
rendered capture request/completion arrived before the native 30-second capture
deadline; the Player exited 21. Its separate existing-output rejection control
passed with exit 21 and an unchanged sentinel hash. No frame or image pass is
claimed for this attempt.

The explicit normal-window follow-up,
[`capture-2bd3qhpf`](../out/player-render-validation/capture-2bd3qhpf/report.json),
is **Passed**, 20:04:31Ã¢â‚¬â€œ20:04:42 UTC. Its separate ignored helper copy changes
only the launch-mode report field and omission of `-batchmode`; neither launch
uses `-nographics`. It retains all existing preflight, strict same-build GUID,
ordered marker, PNG decoding, no-overwrite and rejection checks. The fixture's
own active Game-camera render callbacks preceded the capture request at frame 3.
The actual [rendered PNG](../out/player-render-validation/capture-2bd3qhpf/rendered-fixture.png)
decodes to **960Ãƒâ€”540 RGB**, **70,167 bytes**, SHA-256
**`d7009d17d4f80a8551671e2517b341b86621dc2b9553f676e3a2b05e3f146fde`**.
Native completion and external bytes/hash/dimensions agree. Passive smoke passed
120 frames / 2,439 ms with zero errors and all cleanup counters zero. The
existing-output rejection again exited 21 and preserved the sentinel exactly.
The primary author viewed this PNG: distinct debug materials, shadows, machines
and crates are visible, with no obvious magenta. That basic visual check is not
art acceptance; the automated report's independent visual review remains NotRun.

The same-build [`exercise-supmdpz9` report](../out/player-exercise-validation/exercise-supmdpz9/report.json)
is **Passed**, 20:04:56Ã¢â‚¬â€œ20:05:00 UTC. The opt-in headless exercise completed in
**105 frames**, under its 180-frame / 15-second bounds. Ordered typed markers
retain the same build GUID and epoch: distant entity 106 was denied at sequence
1 with zero claims; nearby entity 102 was grabbed at sequence 2 with lease 1 /
revision 2; Drop at sequence 4 used the same lease and advanced to revision 3,
with zero claims. Native marker measurements record progress **2.003331 m**,
remaining carry distance **0.13984938 m** and post-drop fall **0.9942635 m**.
The accompanying passive smoke passed 120 frames / 2,406 ms, zero errors and all
cleanup counters zero. The separate missing-smoke control exited **22** at Setup,
frame zero, with the exact required-flags reason and no success markers.

Both capture attempts and the exercise preserve the original successful input
report and executable hashes. The exercise additionally records its reviewed
capture helper unchanged; the normal-window helper is an explicit separate copy.
All use build `49da467f5ff346359e6d8a500d21ef38` and executable SHA-256
`748b8feff0cf8e727ed412006cfe11f0591bdfec6bd5634e89acacae0ab8b38e`.
These results establish only the declared sandbox startup/teardown, rendered
file and typed interaction bounds. Ordinary player input, physical feel, FPS,
multiplayer, combined-map traversal/art and independent gate acceptance remain
unverified. Fresh foundation validation on `6554abef` is still running and
combined-map URP preparation is pending at this checkpoint. All old failed
candidate, diagnostic and solver/origin results remain historical failures.

## Foundation, combined map and delivery checkpoint, 20:18 UTC

The separate foundation run `runtime/out/wp01-2kda5zu2/report.json` is Passed:
12/12 EditMode and 9/9 PlayMode identities executed with zero failures/skips,
plus clean preparation, Win64 build and Player. Its lifecycle repair and earlier
log-expectation failures are preserved in WP01.md and FOUNDATION_LIFECYCLE.md.
The final URP combined-map run `runtime/out/combined-map-vvj_fald/report.json`
is also Passed: 37 doors, 152 collision proxies, 13 room anchors and maximum measured
anchor error 0.0002840849 m. Runtime and map input audits, selected package pins and
verified SDK-cache provenance passed. This is preparation/alignment evidence;
no full-map route, ladder, meltdown, Player, art or performance pass is inferred.

The [compact evidence index](results/gameplay-2026-10-18.json) checks/records the
exact 132/12/9 XML catalogues, current API 21/native source/pin/build identities,
723 pure assertions and negative controls, same-build graphics/exercise results,
raw-report hashes and initialized-cache disclosure. Its source code identity is
`6554abef808879191629884048ee6d3df19e4463`. A final read-only first-party code
fingerprint check equals all three native initializations:
`91787aca6cfde6c713b5d76e625e8e64037f42af0cf48cf18c885fb7056335ea`.
Later status documentation changes do not change that executable code. The
[game-camera PNG](results/gameplay-2026-10-18.png) is copied without alteration
from the verified normal-window capture, SHA256
`d7009d17d4f80a8551671e2517b341b86621dc2b9553f676e3a2b05e3f146fde`.
Primary-author viewing found distinct debug materials/shadows and no obvious
magenta shader failure; this is a basic diagnostic observation, not art review.

Local standalone delivery is
`runtime/out/CriticalShift-Gameplay-Win64-20261018.zip`: 70,212,953 bytes,
308 Player files, 164,374,578 uncompressed Player bytes. Archive SHA256 is
`a99aa2bd75812746b2af15d2fe00a0063c3b7a73f36628f357242e5f5ee01464`;
source Player tree SHA256 is
`266f14e07b9b47bf675e1fe1ac98d39662586959feedb3fd85c5d8c504da09dc`.
CRC checks, unique entry inventory and every archived file's bytes matched the
native build. The first lexical ZIP-name hash comparison was rejected because
its order differed from Windows pathlib source ordering; the subsequent explicit
source-order/per-file comparison passed. A fresh extraction at
`runtime/out/gameplay-delivery-vrpx1dgp` passed 120 frames / zero-error startup and
zero-owned-reference teardown under the same build GUID. This does not require
opening Unity. The ZIP stays local/ignored; it is not a released product.

Upstream main remained 3853995c at the 20:10 refresh. Claude's three latest bake-only
commits through 4bab143f were pulled and integrated by 5ed85b1e; no runtime inputs
changed. Authored diff against that base is empty in the protected bake/importer
paths. Draft PR #111 is stacked on Claude's branch and remains unmerged; no agent
self-merge or independent gate/art/feel acceptance occurred. Multiplayer,
full-facility traversal/art, final lighting, accepted diagnostic budgets and
supported performance remain open.

## Normal-window soak and handoff, 20:23 UTC

The separate [normal-window idle report](../out/gameplay-window-soak-6nt344tr/report.json)
is **Passed**, 20:16:40-20:21:41 UTC. The final gameplay executable remained
alive for **300.062 seconds**, at a requested 960 x 540 window size, without
smoke/capture/exercise flags or injected input. Exactly one local-host Ready
marker and the pinned engine identity were found. No logged physics or managed
errors were detected. A normal window-close request was accepted, and the Player
exited zero without forced cleanup. Input native-report and executable hashes
remained unchanged. Native log SHA-256:
`cd661eca747f6427f9f88e6dbdf6d304373bb1ef6112701e6eb67c5273a8d30a`.

This idle observation does not measure FPS, memory, input behavior or physical
feel. Normal mode emits no owned-reference teardown counters; those zero counts
come from the separate structured smoke/exercise evidence, not this idle run.

A contributing validation agent performed a read-only handoff consistency
check: all ten indexed raw-report hashes and the committed PNG hash matched.
It identified stale foundation-pending wording in runtime/README.md; that active
section now records the completed bounded native run. This consistency check is
not independent whole-PR acceptance. Documentation-only corrections preserve the
tested executable source and the standalone ZIP. PR #111's description now cites
the completed native, rendered, physical exercise, map preparation and archive
results, with initialized-cache and acceptance limits explicit.
