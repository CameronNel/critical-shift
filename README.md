# Critical Shift

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

### sections/
Each physical game area is kept as a self-contained package.

A normal section contains:

- scenery/ — detailed layout, dressing, atmosphere and functional environment specification
- prompt/ — model-facing build and iteration prompt
- blender/ — Blender source files for that section
- art/ — concept art, visual references and approved look-development material
- assets/ — exported meshes, textures, decals, reference documents and section-specific production assets

The first fully packaged section is the Spawn Room:

- [Spawn Room scenery specification](sections/spawn-room/scenery/spawnroom.md)
- [Spawn Room build prompt](sections/spawn-room/prompt/spawnroomprompt.md)

The reactor-room specification has also been moved into the same structure:

- [Reactor Room scenery specification](sections/reactor-room/scenery/reactorroom.md)

## Rule

Do not place room-specific files in the repository root. Put them inside their matching section package. Global rules belong under design/.
