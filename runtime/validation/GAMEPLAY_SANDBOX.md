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
- Nine pure command-port tests, nine package safety tests and 40 native sandbox
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
The eight fixture batches begin at 12 logical units each. Physical mass uses
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

Registered cart contact observations are bounded to eight sources and 32 query
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
