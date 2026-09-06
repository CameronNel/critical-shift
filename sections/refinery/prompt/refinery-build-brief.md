You are taking over the next Critical Shift environment task: build the compact refinery section in Blender.

IMPORTANT: ANOTHER TASK IS CURRENTLY RUNNING IN BLENDER / THE LOCAL REPO MAY CONTAIN UNSAVED OR UNCOMMITTED WORK.

DO NOT disturb the current Blender session.

Git / session safety rules:

* Do NOT run `git pull`, `git reset`, `git rebase`, `git checkout`, `git clean`, `git restore`, or anything else that changes the existing working tree until you have established that doing so cannot damage the currently active work.
* Do NOT close, restart, kill, replace, or reuse the currently running Blender process.
* Do NOT overwrite any `.blend` file that may currently be open.
* Do NOT stash somebody else's active work unless absolutely necessary and explicitly safe.
* First inspect the repository status and currently running Blender processes.
* `git fetch` is allowed because it does not modify the working tree.
* If the current working tree is occupied or dirty, create a SEPARATE Git worktree on a new branch for the refinery task and work there.
* Prefer something like:
  `git fetch`
  then create a new worktree/branch from the latest appropriate upstream commit.
* The refinery build must run in its OWN fresh Blender process, preferably headless.
* Never use the active interactive Blender instance as your build environment.
* Preserve all unrelated local modifications exactly as they are.

Before doing anything, read:

* `design/GAME_SPEC.md`
* `design/ART_DIRECTION.md`
* `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`
* `design/ENGINE_DECISION.md`
* `sections/README.md`
* `sections/mine/AGENT_READ_FIRST.md`
* the current Spawn Room material/style work where useful as the facility art-language reference.

The refinery is the middle gameplay department between the Gullet Mine and Reactor.

The authoritative gameplay chain is:

ORE CHUNKS
→ ORE BATCH
→ CRUSHED BATCH
→ SORTED BATCH
→ PROCESSED MATERIAL
→ DRIED MATERIAL
→ FUEL COMPONENTS
→ FUEL ASSEMBLY
→ INSPECTION RESULT
→ REACTOR DELIVERY

The refinery must therefore include all of these functional stations:

1. ore receiving / cart unloading
2. inclined feeder conveyor
3. crusher
4. sorter
5. processor
6. dryer
7. fuel assembly station
8. inspection station
9. fuel dispatch toward reactor

Do NOT simplify the refinery down to only three machines just because earlier concept art did.

## Core gameplay layout

Target a compact, fast, readable room.

Recommended starting footprint:

* roughly 14 m × 12 m
* approximately 4.8 m clear ceiling
* around 2.2 m clear primary walking route

These dimensions are starting recommendations, not sacred numbers. Adjust them if the existing mine/cart geometry requires it.

The room must feel comfortably usable by 1–4 players without becoming a giant factory hall.

The player should be able to understand almost the complete refinery process from a few positions in the room.

Avoid long travel distances.

Do NOT build:

* a giant warehouse
* huge empty floor areas
* a full-height maze of catwalks
* a separate distant control room
* unnecessary corridors
* machinery so large that players spend their time walking around it

Compactness must come from intelligent arrangement, not by deleting functionality.

Suggested arrangement:

MINE-SIDE / LEFT:

* cart docking
* receiving hopper
* inclined feeder
* crusher
* sorter

BACK / CENTRAL:

* processor
* dryer

REACTOR-SIDE / RIGHT:

* fuel assembly
* inspection
* dispatch trolley / transfer point
* reactor exit

Keep an open shared working floor through the centre.

## Ore-to-crusher solution

Players must NOT carry ore upstairs.

The mine cart arrives at floor level.

Build:

* cart alignment guides
* bump stop
* brake/latch point
* low receiving hopper
* hopper size gate
* spill tray / cleanup area
* inclined feeder conveyor
* crusher above the feeder discharge

The hopper opening must be BELOW the actual cart discharge lip.

Inspect the existing mine cart geometry before setting the hopper height.

Validate the complete cart unloading/tipping motion so the cart does not collide with the hopper or surrounding architecture.

Suggested feeder:

* approximately 5.5–6.5 m long
* begins around 0.3 m above floor
* rises to crusher input around 2.5 m high
* cleated belt
* side skirts
* head and tail rollers
* visible return belt
* motor/gearbox
* support structure
* discharge hood into crusher

The feeder should run beside a wall or machine edge, not dominate the room.

## Crusher

The crusher must look mechanically plausible and have a strong unique silhouette.

Build:

* structural base
* tapered feed throat
* guarded crushing mechanism
* toothed rollers / crusher elements
* bearing housings
* motor + gearbox
* inspection/service door
* crushed-material discharge
* waste/dust handling point
* removable or repairable access panels

Separate anything that may later animate.

Player-accessible controls at human height:

* START
* STOP
* REVERSE
* SPEED
* EMERGENCY RELEASE
* SAFETY BYPASS

Provide interaction markers / empties for these.

Represent fault/repair locations:

* jam clearing
* tooth damage
* motor overload
* access panel
* emergency release
* prohibited-object/body detection

Do not create a machine that is just a large cube with a screen.

## Sorter

Build a short material belt after the crusher.

Include:

* scanner bridge
* readable sensing hardware
* belt drive
* pivoting/diverter gate
* accepted-material route
* reject route
* removable reject bin
* calibration panel / calibration access
* manual override point

Player controls / interaction markers:

* belt speed
* scanner sensitivity
* diverter
* recalibration
* manual override

It should be visually obvious what happens to rejected material without reading signage.

## Processor

Build a compact industrial process vessel.

Avoid a giant sci-fi glowing aquarium.

Use:

* believable vessel body
* shaped top/bottom or appropriate caps
* structural supports
* inspection/access hatch
* gauges
* valves
* supply/return pipes
* coolant connections
* pressure/temperature control locations
* emergency dump route
* seal repair point
* modest process-state indicator

Visual interest should come from silhouette, construction and local lighting, not meaningless glowing tubing.

## Dryer

The dryer must remain a distinct machine even if placed next to the processor.

Build:

* insulated housing / short drying tunnel
* sealed access door
* fan/blower
* removable filter
* moisture-check point
* exhaust route
* intake/output handling
* temperature control access

Provide interaction/repair markers for:

* increased heat
* moisture check
* filter bypass
* blocked filter
* fire/fault state

## Fuel Assembly Station

Build:

* structural press frame
* independently movable ram
* guide columns
* die / assembly nest
* casing rack
* component tray
* alignment fixture
* safety guard
* completed fuel cradle/output position

Controls and interaction points should support:

* normal press operation
* high-speed pressing
* casing loading
* alignment
* seal stage
* jam clearing
* output pickup

Fuel units must be physically reachable and carryable.

## Inspection Station

Build a compact inspection bench / scanner.

Include:

* fuel cradle
* scanner hardware
* modest results screen/display
* approved tray/location
* rejected tray/location
* reprocess bin/location
* falsification/override interaction point if appropriate
* dispatch pickup

Inspection must visually support imperfect information.

Do not imply the scanner magically guarantees safety.

Prepare for these decisions:

* approve
* reject
* reprocess
* blend
* falsify
* send uninspected

## Dispatch

Create a small fuel trolley/cart/rack beside the reactor route.

Fuel should physically leave inspection and become a carryable object bound for the reactor.

Keep the reactor route clearly visible/readable.

## Art direction

THIS MUST MATCH CRITICAL SHIFT'S CURRENT ART DIRECTION.

Primary visual target:
grounded stylized semi-realism using VALORANT-style environmental-art principles.

Not photorealistic.
Not generic low-poly.
Not glossy sci-fi.
Not a web-demo look.
Not a kitbash warehouse.
Not toy-like.

Use:

* believable human scale
* clean silhouettes
* simplified but specific geometry
* restrained bevels
* medium-complexity game geometry
* broad colour/value grouping
* localized wear
* controlled material response
* gameplay readability
* detail clusters with quiet areas between them

Suggested palette:

* warm off-white / institutional grey walls
* desaturated teal/green machinery
* charcoal structural metal
* muted concrete
* restrained hazard yellow
* emergency red only where useful
* subtle cyan/green machine-state light only where justified

Floor:

* matte industrial concrete
* broad tonal variation
* cracks/repairs only where plausible
* drainage channels
* maintenance seams
* route wear
* occasional replacement patch
* no glossy wet-plastic floor unless actually wet

Materials must visibly distinguish:

* painted steel
* bare metal
* concrete
* rubber
* glass
* plastic
* paper
* fuel casings

Do not plaster procedural scratches over everything.

Wear should occur where humans and machines actually contact surfaces.

## Detail / environmental storytelling

Add purposeful refinery dressing, not random clutter.

Useful small clusters:
Crusher area:

* pry bar
* shovel
* spare crusher tooth
* small cleanup bin
* maintenance rag

Sorter:

* calibration block/sample
* clipboard
* rejected material bin
* adjustment tool

Processor:

* replacement gasket/seal
* wrench
* chemical/supply container
* taped maintenance note

Dryer:

* spare filter
* removed dirty filter
* heat-resistant gloves

Assembly:

* empty casings
* alignment tool
* glove pair
* component tray

Inspection:

* batch clipboard
* rejected fuel holder
* inspection sample
* modest paperwork

General:

* spill kit
* emergency shower / eyewash
* extinguisher
* cable runs
* drains
* hose
* utility cabinet
* 2–4 sensible storage crates
* small tool trolley

Do NOT fill every square metre with props.

People work here. It is maintained, not abandoned.

## Signage

Keep signage restrained.

Use signs only for:

* navigation
* hazards
* procedures
* interaction understanding
* institutional character

Do not label every machine surface.

Environment readability must work without text.

## Python / Blender architecture

Blender is the visual source of truth.

The refinery must be reproducible headlessly.

Create a clear entrypoint, preferably:

`sections/refinery/blender/build_refinery.py`

Suggested modules:

* `config.py`
* `geometry.py`
* `materials.py`
* `machines.py`
* `dressing.py`
* `states.py`
* `cameras.py`
* `validate.py`

Do not create a gigantic monolithic Python file unless there is an overwhelming reason.

Use reusable helpers for:

* structural frames
* sheet metal panels
* railings
* pipes
* conveyor rollers
* industrial controls
* decals/signage
* lights
* material assignment
* support anchors
* interaction markers

Reuse parts where useful, but avoid obvious copy-paste repetition.

The build must:

1. start from a fresh Blender process;
2. generate/update the refinery;
3. apply materials;
4. install cameras;
5. add metadata/markers;
6. validate;
7. save an editable `.blend`;
8. render review cameras;
9. return non-zero on validation failure.

## Scene hierarchy

Use clean collections such as:

REFINERY_ARCHITECTURE
REFINERY_MACHINES
REFINERY_CONVEYORS
REFINERY_UTILITIES
REFINERY_PROPS
REFINERY_LIGHTING
REFINERY_INTERACTION
REFINERY_VALIDATION
REFINERY_CAMERAS

Each major machine gets its own collection/root.

Separate moving pieces.

Set sensible origins/pivots now.

Do not make Unity later untangle joined meshes that should obviously move independently.

## Gameplay metadata

Add named empties / markers for at least:

INPUT / OUTPUT
controls
repair points
service access
carry pickup
cart dock
hopper
jam point
reject output
processor dump
dryer filter
assembly casing input
fuel output
inspection input
approve/reject/reprocess
dispatch
reactor route

Use consistent naming.

Produce a machine/interaction manifest if useful.

Gameplay itself belongs in Unity, not Blender.

Blender should prepare the visual/physical structure and markers.

## Representative state previews

Create enough static or simple animated state setups to visually prove:

* refinery idle
* normal production
* crusher jam
* wet-ore / overloaded intake
* sorter gate fault
* processor warning
* dryer fault/filter issue
* assembly jam
* inspection uncertainty
* emergency stopped state

Do not waste time creating final game simulation in Blender.

## Physics scope

Do not simulate thousands of ore chunks.

Use:

* representative chunks where visually useful
* consolidated piles/batches
* controlled conveyor representation
* perhaps a small limited physics demonstration if needed

Tiny debris should remain visual/local-only in runtime.

Important gameplay objects such as:

* carts
* fuel
* large ore containers
* tools
* bodies

remain runtime/networked responsibilities.

## Cameras

Create fixed review cameras before final polish.

At minimum:

1. `CAM_ENTRY`

   * room entry/readability

2. `CAM_MINE_TO_CRUSHER`

   * cart dock + hopper + feeder + crusher

3. `CAM_MAIN_ROUTE`

   * complete refinery flow / player route

4. `CAM_PROCESS`

   * sorter + processor + dryer

5. `CAM_ASSEMBLY`

   * fuel assembly + inspection + reactor route

6. `CAM_REVERSE`

   * opposite direction

7. `CAM_PINCH`

   * tightest gameplay circulation area

8. `CAM_MATERIAL`

   * worst-case material/lighting inspection view

Use realistic first-person camera height / FOV for gameplay evaluation.

Do not rely on flattering elevated beauty shots.

## Validation

Automate as much as possible with Blender Python.

Check:

* required objects exist
* required machines exist
* required machine counts
* required cameras exist
* room dimensions
* route widths
* cart docking clearance
* hopper compatibility
* complete cart unloading/tipping sweep if possible
* feeder alignment
* transfer continuity
* machine access
* control reach zones
* doorway clearances
* floor collisions
* no accidental overlapping major geometry
* no floating props
* support contact
* missing materials
* missing textures
* missing external dependencies
* normals
* pivots
* invalid hidden objects
* final save path

Support-dependent props must be validated against intended surfaces using the project's support-contact logic.

## Speed / one-shot instruction

This task should be executed as ONE COORDINATED AUTONOMOUS PASS AS QUICKLY AS POSSIBLE WITHOUT COMPROMISING DETAIL.

The normal repository protocol requires multiple formal correction cycles for final room acceptance.

For this task:

* produce the strongest visually complete version possible in the first build;
* run objective validation;
* render all fixed cameras;
* inspect the resulting pixels;
* perform ONE immediate correction pass for obvious high-impact failures discovered in those renders;
* rerun validation;
* cold-start verify;
* hand over the evidence.

Do NOT fake or claim four completed production review cycles.

This is a one-shot production pass, not final formal acceptance under the full section protocol.

Do not sacrifice:

* machine completeness
* believable construction
* gameplay routes
* material quality
* lighting
* purposeful dressing
* clean hierarchy

for raw speed.

Gain speed through:

* reusable components
* modular builders
* shared materials
* procedural placement
* batch operations
* instance reuse
* headless execution

NOT by leaving things out.

## Deliverables

Create the refinery as its own proper section package:

`sections/refinery/`

with at least:

scenery/
prompt/
blender/
art/
assets/
production/

Deliver:

* editable `Refinery.blend`
* complete build Python source
* config/constants
* machine hierarchy
* interaction marker hierarchy
* required assets/textures
* fixed validation cameras
* review renders
* validation report
* cold-start report
* build command
* machine/interaction manifest
* short handoff/read-first file

Preserve all generated/reusable source needed to rebuild it from scratch.

Do not leave the only good version locked inside one `.blend`.

## Absolute acceptance criteria for this pass

Before handing over, verify:

* existing active Blender session was never disturbed
* unrelated local work remains untouched
* refinery was built in a separate safe workspace/process
* cart can physically reach the unloading point
* unloading hopper is compatible with the real cart
* ore has a believable physical path from cart to crusher
* crusher is not manually loaded from upstairs
* crusher/sorter/processor/dryer/assembly/inspection all exist
* each required stage is visually distinguishable
* material flow is understandable
* players have clear routes
* controls are reachable
* machine repair/service points exist
* compact scale is preserved
* no giant unnecessary spaces
* room reads as VALORANT-influenced grounded stylized semi-realism
* no generic glossy sci-fi appearance
* no placeholder/blockout machine remains presented as final art
* fixed-camera renders exist
* objective validation passes
* fresh-process cold start succeeds
* final `.blend` is editable
* source rebuild remains reproducible

When finished, report:

1. exact branch/worktree used;
2. exact build command;
3. files created/changed;
4. Blender file path;
5. validation result;
6. cold-start result;
7. render locations;
8. remaining known defects;
9. anything intentionally deferred to Unity;
10. confirmation that the previously running Blender/local work was left untouched.

Do the task autonomously. Do not stop after planning. Build the refinery and hand over the evidence.
