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
- The debug worker's arms and legs follow actual walking displacement. A current
  crate or cart grip blends the arm pose. These poses preserve ragdoll joint
  anchors and stop before the same bodies become dynamic on knockdown.
- While alert and down, WASD attempts a slow grounded crawl. The walking capsule
  stays disabled; unconscious, held, slotted or recovering workers cannot use
  this force path. H still needs a clear standing pose and the existing delay.
- Look at a nearby target: E grabs or transfers to/from equipment; G drops the
  current grip; F toggles machine power or reactor cooling; R starts, repairs
  or resumes the focused machine according to its current mode. Repair still
  requires power isolation. B starts with inspection bypass, preserving its
  faster processing and wet-batch jam risk. Loaded containers resolve their machine slot. Walls and
  unrelated bodies continue blocking focus and interaction.
- Stand behind the cart and E takes its exclusive rear handle. WASD (or arrow
  keys) drives and steers while gripped; Space brakes. The worker follows the
  cart's operator stance through collision-controlled movement. Moving too far
  away releases the exact grip lease. G releases the handle. These temporary
  IMGUI inputs are not a production input-framework selection.
- With a crate held over the cart, E releases it onto the bed before taking the
  handle. Cargo remains physically observed; this does not invent inventory.
- Carrying slows movement using the mass of the current held body. The cart's
  load beacon turns amber for overload and flashes red when its observation
  capacity is saturated. These are physical fixture observations, not inventory.
- A moving registered cart can knock the worker down. The existing worker rules
  release the claim; a bounded eleven-body debug rig takes over after the walking
  capsule is disabled. H attempts recovery after settling and the rule delay.
  Recovery needs static ground, a clear standing capsule and a second clearance
  check during the pending handoff. The panel also has an explicit fixture-only
  knockdown button. Reanimation remains separate work.
- Look at the test worker's physical suit grip and E begins a single-person
  drag; G releases. Pulling uses the same exclusive claim and current lease as
  containers, and slows movement using the 68 kg debug body proxy. Excessive
  separation or sustained obstruction releases the grip. The patient's fixture
  recovery button is blocked while that body is held. Hold Shift to raise the
  suit grip slowly; G releases the hoisted worker, allowing a cart-bed loading
  attempt. Hoist input cannot persist into a later lease. Reanimation, two-person
  carrying and accepted loading/transport behavior remain separate work.
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
is `runtime/validation/sandbox-expected-tests.json`: 65 implemented cases, all
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
requires the configured URP asset; Player execution remains a separate unrun
phase. Do not use a green import/physics result as evidence for that later phase.

The runner first checks source ownership, metadata and declared dependency
boundaries. The future native prepare step also compares production assemblies'
resolved project references with their declarations, checks pure assemblies for
engine references and requires compiled outputs. Its native inventory must agree
with the source count. These checks are written and NotRun; they do not constitute
an independently accepted architecture or a Player dependency audit.
