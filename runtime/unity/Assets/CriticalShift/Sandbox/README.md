# Isolated local-host gameplay fixture

**Source-only integration trial. Native import, compilation, tests and Player
execution are NotRun.** See [the development checkpoint](../../../../validation/GAMEPLAY_SANDBOX.md).

The fixture consumes the same canonical Application/domain source as the offline
runner via the local package in `runtime/dotnet/src`. It never loads a map, edits a
room, discovers objects through scene-wide searches or copies a rule implementation.
Stable fixture IDs are rebound to fresh world epochs on restart.

## Contents and controls

Once native execution is authorized, the editor menu **Critical Shift > Sandbox >
Create isolated gameplay scene** generates a new scratch scene containing only a
composition root. On play it builds debug geometry: eight crates, two production
machines, a reactor, a cart, a conveyor, a local collision controller and a downed
test worker. The second worker is controlled locally for this fixture.

- WASD: walk; right mouse drag: look; Tab: show/hide controls.
- Space makes a short hop while walking, with limited air acceleration, a small
  ledge grace window and input buffer. Carried mass reduces the hop. Space stays
  the brake while holding the cart; pause, knockdown and teardown clear hops.
- The debug worker's arms and legs follow actual walking displacement. A current
  crate or cart grip blends the arm pose. These poses preserve ragdoll joint
  anchors and stop before the same bodies become dynamic on knockdown.
- While alert and down, WASD attempts a slow grounded crawl. The walking capsule
  stays disabled; unconscious, held, slotted or recovering workers cannot use
  this force path. H still needs a clear standing pose and the existing delay.
  A conscious down worker can right-drag to look around; only the eyes turn.
  Crawl direction follows that heading. Recovery preserves the view after the
  physical handoff; an unconscious worker cannot use this look input.
- A small status light follows each worker's physical suit grip: amber while
  down, red while unconscious and blue during recovery. It hides once upright
  or stopped. These are derived debug cues, not another health system or a
  separately activated/shared emergency beacon feature.
- Look at a nearby target: E grabs or transfers to/from equipment; G drops the
  current grip; F toggles machine power or reactor cooling; R starts, repairs
  or resumes the focused machine according to its current mode. Repair still
  requires power isolation. B starts with inspection bypass, preserving its
  faster processing and wet-batch jam risk. Loaded containers resolve their machine slot. Walls and
  unrelated bodies continue blocking focus and interaction.
  Equipment reach/occlusion uses the visible console face; cart access uses its
  rear grip. Collider identity still belongs to the full registered assembly.
- Stand behind the cart and E takes its exclusive rear handle. WASD (or arrow
  keys) drives and steers while gripped; Space brakes. The worker follows the
  cart's operator stance through collision-controlled movement. Moving too far
  away releases the exact grip lease. G releases the handle. These temporary
  IMGUI inputs are not a production input-framework selection.
- With a crate held over the cart, E releases it onto the bed before taking the
  handle. Cargo remains physically observed; this does not invent inventory.
- Middle-mouse drag turns a currently held crate through its existing torque
  controller. Face markings make its orientation visible. Rotation clears on
  release, expiry, insertion or restart, and cannot turn a cart or worker grip.
- Scroll outside the visible control panel to bring a held crate closer or
  farther. The carry target shifts at most 0.75 m from its authored position
  (1–2.5 m forward in this fixture). The body still follows bounded forces.
  Reach offset resets with the claim and cannot move cart/worker targets.
- T throws a portable crate toward the current look heading. A committed
  release comes first; one bounded impulse follows only for that exact free
  body and lease. Retrying the release cannot throw again. Heavier crates get
  less extra speed. Worker bodies and cart handles use G release instead.
- Carrying slows movement using the mass of the current held body. The cart's
  load beacon turns amber for overload and flashes red when its observation
  capacity is saturated or its sensor is unavailable. Drive waits for a fresh
  active sensor sample; disabling/reenabling cannot clear the overflow latch.
  These are physical fixture observations, not inventory.
- A moving registered cart can knock the worker down. The existing worker rules
  release the claim; a bounded eleven-body debug rig takes over after the walking
  capsule is disabled. H attempts recovery after settling and the rule delay.
  Recovery needs static ground, a clear standing capsule and a second clearance
  check during the pending handoff. The panel also has an explicit fixture-only
  knockdown button. Reanimation remains separate work.
- Crate one has two extra yellow warning bands: 36 units / 27 kg. It is the
  fixture's explicitly registered falling-load hazard. A free downward contact
  above the authored speed/mass threshold uses the same knockdown flow. Held,
  slotted and lightweight bodies cannot take that hazard path.
- Open debug bins show eight prebound, non-contacting content markers. Their
  fill, shape and color follow batch quantity, kind and condition. Conversion
  changes the same pile; spent fuel remains accounted material. The solid box
  remains the physical proxy; individual pieces are presentation only.
- Look at the test worker's physical suit grip and E begins a single-person
  drag; G releases. Pulling uses the same exclusive claim and current lease as
  containers, and slows movement using the 68 kg debug body proxy. Excessive
  separation or sustained obstruction releases the grip. The patient's fixture
  recovery button is blocked while that body is held. Hold Shift to raise the
  suit grip slowly; G releases the hoisted worker, allowing a cart-bed loading
  attempt. Hoist input cannot persist into a later lease. Reanimation, two-person
  carrying and accepted loading/transport behavior remain separate work.
  A process pause stops active hoisting and lowers its target while the current
  claim remains held; ordinary passive Unity physics continues.
- Select a nearby crate and Grab/Release. Current host reach and line of sight
  are checked. Carrying uses bounded forces; excessive obstruction drops the
  exact claim. Leases renew through the same connection's command stream.
- Select a machine, insert, power on, then start. The crusher turns ore into
  crushed ore; the processor turns crushed ore into fuel. Eject between stages.
  Wet material and inspection bypass exercise the existing jam/lineage rules.
- The cyan crate is pre-made fuel for isolated reactor testing. Load it, open
  cooling and start. Cooling loss, reserve spending, trip/reset and fuel work
  remain the existing fictional game rules, not another simulation.
- With the reactor focused, X shuts it down and C requests emergency cooling
  using reserve power. R resets a tripped reactor when safe; press R again to
  start it. The two needle gauges show remaining fuel and reserve capacity.
- Drop free crates onto the belt or cart. Held/slotted/unknown objects are
  excluded from belt authority. A belt blockage latches until cleared and reset.
- Process-clock pause pauses rules while real-time leases continue. It does not
  freeze all Unity physics. Restart tears down bindings and constructs a fresh
  world; Retry repeats the identical prior user intention, not a new action.
  A terminal shift releases physical bindings and observations while keeping
  its outcome/feedback visible. Restart creates fresh bindings and a new epoch.
  The panel reads current/final material accounting, process-cycle counts,
  grid delivery, reserve, spending and spill from the existing immutable views.
- The fixture watches its 31 explicitly bound Rigidbody segments. A missing,
  non-finite, escaped or runaway body stops the trial with a named diagnostic.
  It never silently teleports cargo or changes material quantities. The panel
  shows dynamic-body counts and observed peak speed for later investigation.
- The recent-event panel projects the existing host trace into at most 12 rows.
  It shows recorded machine, reactor and worker causes, ignores replayed commits
  and routine generation ticks, and flags gaps if source diagnostics were lost.
  Exact-lease binding drops and lease expirations also appear once in this feed.
  This is a bounded diagnostic view, not a complete shift debrief.

## Owners and dependencies

`Sandbox.Bootstrap` constructs dependencies and owns fixture teardown. Application
owns game rules and command admission. `Features.Interaction.Unity` owns clock
sampling, physical claim/slot reconciliation and trusted spatial observations.
`Features.Workers.Unity` owns local locomotion, the walking/ragdoll handoff,
bounded trusted cart-contact observations and physical recovery clearance. It
uses the existing Application worker operations for logical transitions. FacilityPhysics
owns bounded cart/belt forces and their physical sensors; its authorization
queries are injected. Presentation reads detached projections and sends typed
commands through injected callbacks. No transport, voice, Steam or persistence
package is selected. No domain instance is exposed to presentation.

Cart load is a bounded physical sensor observation of authorized cargo bodies,
not a second material inventory. Wheel motion follows cart travel. Belt treads,
machine spindles, cooling-valve movement, lamps, emission and batch colors are
presentation; none changes materials, custody, reactor state or power. Process
gauges and small preallocated spark/vent-mote pools also follow those projections.
Loading clamps follow slot occupancy; a visual ram follows committed machine
work and holds its stroke during a process pause or jam. Conveyor end rollers
follow tread travel and stop with the belt. These details add no contact shapes.
Their trajectories use process time, without consuming incident randomness,
adding colliders or creating objects during an effect. These are debug visuals.
The cargo sensor samples its current volume and groups eligible ragdoll segments
as one 68 kg debug load. Any intersecting part counts that whole body, a
conservative fixture proxy. Held/slotted bodies are excluded; disabled, removed
or relocated colliders cannot retain an old trigger-event load. The belt keeps
its separate free-material-only permission.

The fixture uses the project's **already configured** shader family for debug
geometry. This explicitly supports the old Built-in foundation for import and
physics investigation; it does not accept that as the final renderer. The Player
build entrypoint requires the owner-selected URP asset, which remains unconfigured
on the inspected baseline. No package is downloaded by the generator.

## Evidence boundary

The existing foundation runner still tests its foundation assembly selection;
it does not automatically claim sandbox coverage. The separate native inventory
is `runtime/validation/sandbox-expected-tests.json`: 99 implemented cases, all
NotRun. Nine new pure command-port cases, fourteen worker-body claim cases and
nine source-package safety cases and five declared-assembly boundary cases
are also NotRun. Native fixtures are offset from possible active-scene content
to avoid collisions with an unrelated map/scene at the origin.

No human feel review, ragdoll/body-dragging acceptance, multiplayer convergence,
supported FPS, final lighting/art or roadmap gate is established here. Renderer
migration, physics tuning and lifecycle validation require actual editor/Player
evidence after permission to execute. This source trial is unmerged and awaits
independent review.

When execution is authorized, `runtime/tools/run_sandbox.py` prepares and tests
in a fresh disposable copy, retaining the canonical local-package path. Pass the
pinned editor with `--unity` and `--target Win64`. The optional `--build-player`
requires the configured URP asset. Adding `--run-player` explicitly requests a
headless startup/teardown smoke of that same new build on its matching OS. It
requires the pinned version/build identity, generated meshes, declared physical
bindings, at least 120 physics frames and two seconds, then empty teardown
counters after deferred destruction. Both native phases remain NotRun. A green
import/physics result does not establish a Player pass, and headless startup
does not establish rendered playability, lighting, feel or supported performance.

The runner first checks source ownership, metadata and declared dependency
boundaries. The future native prepare step also compares production assemblies'
resolved project references with their declarations, checks pure assemblies for
engine references and requires compiled outputs. Its native inventory must agree
with the source count. These checks are written and NotRun; they do not constitute
an independently accepted architecture or a Player dependency audit.
