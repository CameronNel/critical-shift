# Isolated local-host gameplay fixture

**Dirty cargo handling continuation:** holding crate6's contaminated ore adds
12worker-load units per sampled shift-second before PPE (compromised6/intact3).
Material contamination must exceed500/1000. Dropping stops contact; regrabbing
retains the worker/source cooldown. Washing its ore to100 stops that source.
The wash area samples before handling, so holding dirty cargo there can add a
fresh dose after washing. Read the current cargo cue and worker meter; reading
the cue adds no dose. Contact history names both worker and crate and retains
the original dirty batch. Native catalogue174; new behavior remains NotRun.
[Scope and evidence](../../../../validation/DIRTY_CARGO_EXPOSURE.md).

**Ore washing continuation:** spare crate6 now contains800/1000 contamination.
The washer at(-3.5,0,9) spends1reserve over10s to lower it to100/1000, with wet
output1000/1000. Dry it before safe crushing, then use the existing fuel chain.
Material units, original cause and inherited inspection flags remain intact;
washing does not erase bypass history. The crate panel shows current moisture,
contamination and flags. The original clean quota route retains its stock.
Native catalogue171; current washer placement/loading remains NotRun.
[Scope and evidence](../../../../validation/ORE_WASHING.md).

**Suit mobility continuation:** current source derives a walking factor from
Workers-owned gear: no suit100%, worn intact/compromised80%. It composes with
carried mass for voluntary planar walking/air targets; cart stance correction,
vertical hop and passive motion retain their existing behavior. The HUD shows
the current factor and explains the fitting tradeoff. Native catalogue170:
four new motor comparisons remain NotRun. [Evidence](../../../../validation/SUIT_MOBILITY.md).

**Physical medical rescue continuation, 19 October 2026:** the current source
adds a chamber and explicit discharge area, paid timed stabilization controls
and own-patient emergency egress. The native catalogue contains **166 cases**,
including27 new medical cases, all new behavior **NotRun** without the pinned
editor. [Scope and current evidence](../../../../validation/PHYSICAL_MEDICAL_RESCUE.md).

**PR #111 review repairs:** rotated loading bounds, exact-lease hoist reset,
setup-disconnect body cleanup and recovery clearance have been repaired after
independent source review. The native catalogue now has **136 implemented cases**;
native execution of this repair revision is **NotRun** here. The 132-case results
below and the existing local Player ZIP belong to the earlier recorded source.
Current source/tool verification: 724 offline and 182 tooling tests passed. See
[the active review checkpoint](../../../../validation/GAMEPLAY_SANDBOX.md).

**Validated local integration trial; independent acceptance pending.** Source
`6554abef` passed all 132 native gameplay cases, a strict Win64 build, headless
startup/cleanup, a same-build normal-window PNG capture and the physical
deny/carry/drop exercise. See
[the development checkpoint](../../../../validation/GAMEPLAY_SANDBOX.md).

The fixture consumes the same canonical Application/domain source as the offline
runner via the local package in `runtime/dotnet/src`. It never loads a map, edits a
room, discovers objects through scene-wide searches or copies a rule implementation.
Stable fixture IDs are rebound to fresh world epochs on restart.

## Current contract source

The twelve-minute sandbox now uses one pure `SandboxGameplaySetup` for its stock,
recipes, reactor and four demand windows. The offline suite links that exact
source and executes a complete safe supply route through the normal local
command port. It renews held leases during simulated transport and retains
material/power accounting at the deadline. Native import of the extraction is
NotRun; this does not establish physical carrying/loading time or accepted balance.

The grid counts energy separately in each window. Surplus in preparation or an
earlier window cannot pay a later request. Stage fuel, maintain cooling, and leave
time for reloads. Hiding the control panel retains the current window countdown,
authored upcoming warning, and the latest settled missed-window shortfall/count.
This read-only formatter is tested offline; native wrapping/readability remains
NotRun. The logical reference route processes the heavy dry crate and
three ordinary dry crates through crusher and processor without bypass. It starts
the heavy fuel at04:20, follows with the original ready fuel, then uses the three
ordinary fuel batches from09:00. This is a reproducible fixture route, not a
required player solution or a physical playtest. See
[supply-route evidence](../../../../validation/SANDBOX_CONTRACT_ROUTE.md).

## Contents and controls

Once native execution is authorized, the editor menu **Critical Shift > Sandbox >
Create isolated gameplay scene** generates a new scratch scene containing only a
composition root. On play it builds debug geometry: eight crates, four production
machines (crusher, processor, safe ore dryer and washer), a reactor, a medical chamber, a cart, a conveyor, a local collision controller and a downed
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
  (1Ã¢â‚¬â€œ2.5 m forward in this fixture). The body still follows bounded forces.
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
- The test worker begins alert/down for drag and recovery checks. Use the explicit
  patient incapacitation button to create an unconscious rescue patient. Drag
  that body to the chamber at(9,0,10); E while looking at its console loads the
  held patient, and R requests stabilization. The panel shows actual reserve,
  cartridges, contamination limit and shift-clock time. Default treatment spends
  6reserve and1cartridge for3s; cancel/interruption retains those costs. Completing
  treatment leaves the worker alert/down inside the chamber. E ejects onto its
  separate clear pad, then ordinary settling, delay and standing clearance apply.
  Both bed and discharge need full-body clearance. An awake local patient can E
  out of their own ejectable chamber without camera focus, including after the
  operator disconnects; range and line of sight to the console still apply.
  These source controls and all chamber physics remain native NotRun.
- Select a nearby crate and Grab/Release. Current host reach and line of sight
  are checked. Carrying uses bounded forces; excessive obstruction drops the
  exact claim. Leases renew through the same connection's command stream.
- Select a machine, insert, power on, then start. The crusher turns ore into
  crushed ore; the processor turns crushed ore into fuel. Eject between stages.
  Wet material and inspection bypass exercise the existing jam/lineage rules.
  The ore dryer safely reduces wet-ore moisture before crushing, conserving
  quantity and retaining contamination/inspection history. It offers no bypass.
  Its current source placement/loading/GUI are native NotRun; see
  [drying contract](../../../../dotnet/SAFE_DRYING.md).
- The cyan crate is pre-made fuel for isolated reactor testing. Load it, open
  cooling and start. Cooling loss, reserve spending, trip/reset and fuel work
  remain the existing fictional game rules, not another simulation.
- With the reactor focused, X shuts it down and C requests emergency cooling
  using reserve power. R resets a tripped reactor when safe; press R again to
  start it. The two needle gauges show remaining fuel and reserve capacity.
  The reactor panel also exposes the optional finite backup supply: a timed
  stored charge restores reserve for a zero-reserve start. It generates no grid
  delivery; cancellation keeps the charge used. The source controls remain
  native NotRun; see [backup contract](../../../../dotnet/EMERGENCY_POWER.md).
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
The still-dynamic body remains eligible while standing recovery is pending; it
stops being a ragdoll load when the upright handoff completes.

The explicit scene generator prepares the owner-selected URP 17.4.0 asset using
already resolved packages. It retains ordinary and emissive Lit material templates
as serialized Player dependencies. Runtime palettes own only their clones. The
generator does not install packages or alter authored map art.

## Evidence boundary

The existing foundation runner still tests its foundation assembly selection;
it does not automatically claim sandbox coverage. The separate native inventory
is `runtime/validation/sandbox-expected-tests.json`: currently166 source cases.
New and changed cases remain NotRun. The historical132-case suite below belongs
to its earlier source. The
earlier 124-case checkpoint passed. The final URP candidate passed all 132 cases
with zero skips. The earlier 127/129 result and controlled solver/origin failures
remain historical failures; those comparisons established no physical motion fix.
The current diagnostic policy retains the independent 25 m/s linear limit and
replaces the authored 25 rad/s cutoff with native principal-frame rotational
energy per mass (312.5 J/kg). Raw angular speed is still recorded. These are
separate authored trial budgets, not a combined energy budget or accepted
production limits. The monitor changes no forces, caps, damping or motion.
Historical failures remain failures; a pass under this criterion would not
prove repaired ragdoll motion, far-origin stability or acceptable feel.
The latest pure suite passed 723 cases including the cause-trace assertion. Native
fixtures are offset from possible active-scene content
to avoid collisions with an unrelated map/scene at the origin.

No human feel review, ragdoll/body-dragging acceptance, multiplayer convergence,
supported FPS, final lighting/art or roadmap gate is established here. Scoped
renderer/lifecycle/Player evidence is now recorded; physical feel and diagnostic
budget acceptance remain open. Execution is authorized. Independent source review of
the PR repair revision is complete; its fresh native execution remains NotRun here.

When execution is authorized, `runtime/tools/run_sandbox.py` prepares and tests
in a fresh disposable copy, retaining the canonical local-package path. Pass the
pinned editor with `--unity` and `--target Win64`. The optional `--build-player`
requires the configured URP asset. Adding `--run-player` explicitly requests a
headless startup/teardown smoke of that same new build on its matching OS. It
requires the pinned version/build identity, generated meshes, declared physical
bindings, at least 120 physics frames and two seconds, then empty teardown
counters after deferred destruction. The final Win64 build/Player passed. A green
import/physics result does not establish a Player pass, and headless startup
does not establish rendered playability, lighting, feel or supported performance.

The Development Player also supports an explicit additional
`--cs-sandbox-exercise` flag together with `--cs-sandbox-smoke`. It sends an
out-of-reach grab, a reachable grab and a drop through the existing host; checks
typed same-epoch traces and the exact lease; measures native carry/fall movement;
and returns to the ordinary zero-claim sensor/teardown baseline. It changes no
pose, velocity, clock or material data directly. Its bounded driver is inactive
in the editor, normal play and ordinary passive smoke. The final same-build
exercise passed in 105 fixed frames: about 2.003 m carry progress and 0.994 m
fall after release, with unchanged material accounting and zero remaining
custody/owned references. The separate validator also observed the required
exit22 rejection when the smoke flag was omitted. These automated observations
do not replace a human control/feel review.

The runner first checks source ownership, metadata and declared dependency
boundaries. The native prepare step also compares production assemblies'
resolved project references with their declarations, checks pure assemblies for
engine references and requires compiled outputs. Its native inventory must agree
with the source count. These checks passed natively for the final candidate;
they do not constitute an independently accepted architecture. Native runs used
only a verified initialized SDK package-cache seed; first-party sources compiled
in fresh workspaces. Cold package extraction is not passed. The observed Null
Player property-reflection exemption retains all material identities, keywords
and GI checks; Editor and graphics Players retain property reflection checks.

## Combined-map traversal derivative

`Critical Shift > Combined Map > Create collision traversal scene` reads only
the combined map's current collision/anchor export and manifests. It generates
`Sandbox/Generated/CombinedMapTraversal.unity`, with the existing worker controls,
revisioned doors and an explicit evacuation exercise. E opens/closes a focused
door; occupied openings cannot close. The sealed dock remains non-operable.
WASD, Space, right-drag and H reuse the local movement/hop/look/recovery approach.

This derivative contains connective collision proxies. It does not invent room
floors, import baked art, support the condenser escape ladder or implement a
meltdown incident/countdown. The start is the measured spine-floor centre.
The builder checks imported anchor positions and actual mesh-collider bounds
against the source frame to 0.01 m. No source blend, room, old map or protected
Content/Editor bake importer is modified. Debug materials are not art acceptance.

For a disposable, input-hashed native preparation, use
`runtime/tools/run_combined_map.py --unity <pinned Unity.exe> --target Win64`.
Its scope is import/preparation and alignment, not a Player or traversal pass.
The first sandbox native attempt was license-blocked before test discovery.
Activation has since succeeded, and native map preparation passed: 37 doors,
152 actual-mesh proxies and 13 room anchors, with maximum error 0.0002840849 m.
The collision export's measured raw frame is `(x,z,y)`; only its generated root
is rotated 180 degrees to match the existing baked placement frame `(-x,z,-y)`.
The current offline 723 cases passed. Native sandbox discovery/execution and
Player acceptance remain separate; see the active task record for current counts,
exact evidence and its limits.
