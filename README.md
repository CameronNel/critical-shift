# Critical Shift

A cooperative industrial comedy about human employees of an AI-run civilisation operating a uranium mine, fuel refinery, and nuclear power plant while taking illegal shortcuts, exposing resistance infiltrators disguised as legitimate employees, deceiving compliance officers, and preventing catastrophic meltdowns.

The foundational product, narrative, systems, technical, multiplayer, AI-production, and validation specification is in [`GAME_SPEC.md`](GAME_SPEC.md).

The current setting is defined in [`docs/CANON.md`](docs/CANON.md), and the visual direction is defined in [`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md).

This repository is currently a design and prototyping foundation.

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
the first-person controller, objective HUD, and a compact physical
**Radioactive Shoebox** annex to the authored fourteen-zone facility.

Controls: WASD move, mouse look, Shift sprint, Ctrl crouch, Space jump,
E interact, F take the displayed risky/alternate action, G or right mouse grab
and drag, left mouse throw, R reset after a result, and Escape release the
cursor.

The physical loop is:

1. Read the briefing.
2. Release dry ore and carry three rocks onto the conveyor.
3. Listen to the crusher; repair a wet jam or knowingly enable its bypass.
4. Carry two spawned fuel assemblies into the yellow reactor port.
5. Start the reactor and meet rising demand.
6. If unsafe fuel causes a delayed emergency, open the physical cooling valve.
7. Inspect the infiltrator and legitimate suspicious worker, respond to the
   compliance officer, hide evidence or accept the consequences of a bonk.
8. Shove the mine cart or arm TNT to create a recoverable casualty, drag the
   worker to the OCRU cabinet, and spend reserve power to reanimate them.
9. Read the cause -> warning -> consequence -> recovery debrief and restart.

Standalone machine test scenes live in `Assets/Scenes/Tests/` for the conveyor,
crusher, reactor, and OCRU. The Unity EditMode suite covers deterministic batch
transformation, machine faults/repair/reset, reactor crisis staging, physical
scope construction, worker recovery, reanimation cost, social escalation, and
causal debriefing.

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
