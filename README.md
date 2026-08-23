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
the first-person controller, objective HUD, and interactable shift stations to
the authored fourteen-zone facility.

Controls: WASD move, mouse look, Shift sprint, Ctrl crouch, Space jump,
E interact, F take the risky refinery bypass, R reset, and Escape release the
cursor. Complete briefing -> three ore loads -> two safe fuel batches -> reactor
for a clean shift. The refinery bypass saves time but creates a delayed cooling
emergency at the reactor shutdown station.

A Windows x64 development build is produced at
`Builds/Windows/CriticalShiftPrototype.exe`; build outputs are intentionally
ignored by Git.

[`prototype/threejs-facility/`](prototype/threejs-facility/) is a Three.js
greybox of the facility — a level-design and layout-review tool rather than
game code, removable by deleting that directory. See its
[design notes](prototype/threejs-facility/DESIGN_NOTES.md) for the layout
reasoning and how to ask for changes to it.
