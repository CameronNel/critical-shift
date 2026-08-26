# Critical Shift

A cooperative industrial comedy about human employees of an AI-run civilisation operating a uranium mine, fuel refinery, and nuclear power plant while taking illegal shortcuts, exposing resistance infiltrators disguised as legitimate employees, deceiving compliance officers, and preventing catastrophic meltdowns.

The foundational product, narrative, systems, technical, multiplayer, AI-production, and validation specification is in [`GAME_SPEC.md`](GAME_SPEC.md).

The current setting is defined in [`docs/CANON.md`](docs/CANON.md), and the visual direction is defined in [`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md).

**Current visual direction:** highly stylised, low-detail 3D with PEAK as the high-level north star for simplicity, silhouette readability, compact expressive characters, broad colour blocking, and texture-light materials. Critical Shift must remain an original industrial design language rather than copying PEAK-specific assets. Sea of Thieves painterly styling, grounded/photorealistic rendering, and dense realistic PBR detail are obsolete targets.

This repository contains the design foundation and a local single-player Unity
vertical slice of the complete first shift.

## Working agreements

Agent working rules live in [`AGENTS.md`](AGENTS.md), with Claude Code
specifics in [`CLAUDE.md`](CLAUDE.md).

Agents open a pull request for every change and **merge it themselves** once
checks are green — finished work is not left waiting for a human to land it.
Nothing is pushed directly to `main`, and anything blocked by red checks,
open review comments, or a decision that belongs to the repository owner stays
open with the reason stated.

## Prototypes

### Unity playable shift

Open the repository as a Unity `6000.4.3f1` project, load
`Assets/Scenes/FacilityGreybox.unity`, and press Play. A runtime bootstrap adds
the first-person controller, objective HUD, and gameplay directly to the
authored fourteen-zone facility. The detached **Radioactive Shoebox** remains a
fallback/test fixture; it is not the startup experience in the authored scene.

Controls: WASD move, mouse look, Shift sprint, Ctrl crouch, Space jump,
E interact, F take the displayed risky/alternate action, G or right mouse grab
and drag, left mouse throw, R reset after a result, and Escape release the
cursor.

The playable 25-minute physical loop is:

1. Accept the briefing and either complete the 16-second suit procedure or
   knowingly skip it.
2. Walk to the integrated Gullet mine, drill three physical dry/wet ore chunks,
   grab them, and load the parked mine cart.
3. Release the brake and follow the loaded cart through haulage to the authored
   receiving hopper.
4. Tip the cart, operate crusher, sorter, processor, dryer, fuel assembly and
   inspection in order, and respond to readable jams or risky bypasses.
5. Carry two released fuel assemblies through the fuel corridor into the
   reactor receiving port.
6. Start coolant flow, raise the reactor, connect grid demand and deliver the
   energy quota while watching heat, stability and the world objective beacon.
7. If unsafe production causes a delayed emergency, inject physical emergency
   cooling before staged meltdown completes.
8. Inspect the infiltrator and legitimate suspicious worker, respond to the
   compliance officer, hide evidence or accept the consequences of a bonk.
9. Shove the mine cart or arm TNT to create a recoverable casualty, drag the
   worker to the OCRU cabinet, and spend reserve power to reanimate them.
10. Read the cause -> warning -> consequence -> recovery debrief and restart.

Standalone machine test scenes live in `Assets/Scenes/Tests/` for the conveyor,
crusher, reactor, and OCRU. The Unity EditMode suite covers deterministic batch
transformation, the full authored route markers, an end-to-end safe production
shift, cart loading/overload/reset, the timed suit sequence, every refinery
stage, machine faults/repair/reset, reactor crisis staging, worker recovery,
reanimation cost, social escalation, and causal debriefing.

This build is an honest local single-player proof-of-fun. Four-player
host-authoritative networking, object contention, disconnect cleanup, Steam and
proximity voice remain Gate 1 work and are not claimed as implemented.

A Windows x64 development build is produced at
`Builds/Windows/CriticalShiftPrototype.exe`; build outputs are intentionally
ignored by Git.

[`prototype/threejs-facility/`](prototype/threejs-facility/) is a Three.js
greybox of the facility — a level-design and layout-review tool rather than
game code, removable by deleting that directory. See its
[design notes](prototype/threejs-facility/DESIGN_NOTES.md) for the layout
reasoning and how to ask for changes to it.
