# Spawn Room Assets

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Store Spawn Room-specific production exports and supporting asset files here.

Examples:

- FBX or glTF exports
- texture and decal files
- signage images
- portrait images
- paper/poster images
- source/licensing notes for external assets

The authoritative editable Blender scene belongs in ../blender/.


## Production protocol

Any generated or imported section art/assets must remain compatible with the room's headless Blender source and ../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md. Do not introduce hidden MCP-only dependencies or unrecorded external sources.


## Asset style constraints

Spawn assets must read as real workplace objects simplified for a stylized PC game. A locker, bench, scanner, suit bay, door and wall cabinet must each have distinct construction logic and silhouette.

Use shared material families, but not one shared visual response:
- painted metal;
- coated structural metal;
- rubber;
- fabric/PPE;
- concrete/plaster;
- institutional flooring;
- restrained plastic;
- glass;
- paper/card.

Reject any asset that only becomes recognizable after labels are added.
