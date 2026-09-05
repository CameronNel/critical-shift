# Spawn Room Production Evidence

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


This folder is the persistent operating memory and proof package for the Spawn Room build.

Follow:
- ../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md
- ../scenery/spawnroom.md
- ../prompt/spawnroomprompt.md

The builder must keep TASK_STATE.md current.

Formal review uses RUBRIC.md, CAMERAS.md and CHECKLIST.md.

Review renders belong under renders/review/. Only approved evidence belongs under renders/final/.

Meaningful rollback points belong under checkpoints/.

MCP may supervise the process, but the room must remain reproducible through headless Blender without MCP.


## Production reset — 2026-09-05

The previous Spawn Room visual pass is not the approved art baseline. Preserve only useful gameplay dimensions, routes and interaction positions.

New order:
1. build one style-validation slice;
2. render fixed gameplay cameras;
3. score against the new rubric;
4. establish canonical geometry/material/light rules;
5. checkpoint the approved slice;
6. then expand hallway, briefing room and locker/suiting area.

Do not polish or propagate the old low-poly/plastic asset language.
