# Critical Shift

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Critical Shift is currently a planning-first game repository.

The previous prototype implementation, maps, generated assets, and engine project files were deliberately removed so the production build can be reconstructed cleanly from the design foundation.

## Repository layout

### design/
Global rules that apply to the entire game:

- GAME_SPEC.md — master game, systems, narrative, technical and validation specification
- CANON.md — setting and narrative canon
- ART_DIRECTION.md — authoritative visual direction
- ENGINE_DECISION.md — engine decision record and reopening conditions
- ROADMAP.md — stage-gated production plan
- AUTONOMOUS_SECTION_BUILD_PROTOCOL.md — mandatory headless-first, MCP-assisted Blender build/review protocol

### sections/
Each physical game area is kept as a self-contained package.

A normal section contains:

- scenery/ — detailed layout, dressing, atmosphere and functional environment specification
- prompt/ — model-facing build and iteration prompt
- blender/ — Blender source files for that section
- art/ — concept art, visual references and approved look-development material
- assets/ — exported meshes, textures, decals, reference documents and section-specific production assets
- production/ — persistent task state, rubric, validation cameras, critics, review renders, checkpoints and cold-start evidence

The first fully packaged section is the Spawn Room:

- [Spawn Room scenery specification](sections/spawn-room/scenery/spawnroom.md)
- [Spawn Room build prompt](sections/spawn-room/prompt/spawnroomprompt.md)

The reactor-room specification has also been moved into the same structure:

- [Reactor Room scenery specification](sections/reactor-room/scenery/reactorroom.md)

## Rule

Do not place room-specific files in the repository root. Put them inside their matching section package. Global rules belong under design/.


## Environment build policy

All playable 3D sections follow [design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md](design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).

The core build is **headless Blender CLI + versioned scripts**. MCP is the supervision and integration layer, not a hard dependency for reproducing the room.

A section is not complete because Blender produced a file. It must pass fixed-camera pixel review, fresh-context specialist criticism where available, a scored rubric, regression checks, and a fresh-process cold-start render.


## Current visual production rule

The previous low-poly/PEAK-rendering interpretation is retired. New environment work must first pass a **small style-validation slice** before an agent expands a room. Use the generated plates in [design/ART_REFERENCE_INDEX.md](design/ART_REFERENCE_INDEX.md) as visual calibration.

The current Spawn Room art pass should be treated as a layout/prototyping artifact only where useful. Its repeated bevelled-box construction, plastic material response, excessive signage and flat lighting are specifically rejected by the new art bible.
