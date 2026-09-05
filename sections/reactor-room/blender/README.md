# Reactor Room Blender Source

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Store the future authoritative reactor-room Blender source here.

Recommended primary filename: reactorroom.blend


## Build policy

Reactor Room source is headless-first and must remain reproducible without MCP.

See ../../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md.


## Modeling guardrails

The reactor Blender source must prove object-specific construction before detail. Major machinery, consoles, doors, pool rim, control-bank assemblies and railings must not share one universal bevel language. Bevels are finishing operations only.

Build a small reactor material/lighting validation slice before duplicating modular pieces across the hall. Check the generated reactor reference plates in `../art/reference/` from the actual gameplay camera.
