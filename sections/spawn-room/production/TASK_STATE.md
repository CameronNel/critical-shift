# Spawn Room — Task State

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Current phase:** Built; final pass run, NOT accepted (see [final-pass/REPORT.md](final-pass/REPORT.md))
**Current overall score:** Independent critics 85 and 82 of 100 after the suits and the polish pass (needs >= 90)
**Cold-start status:** Not run
**Authoritative source:** ../../facility-assembly/sources/spawn-room/module.blend (runtime derivative: module_optimised.blend)

## Completed
- Detailed scenery specification
- Build/self-review prompt
- Production rubric
- Fixed-camera plan
- Acceptance checklist
- Automated support-contact validator and tagging convention

## Worst current visible defects
Suits, Geiger drop and the polish pass (wear, doorway spill, bench posts, Material_A framing) are done; see [final-pass/REPORT.md](final-pass/REPORT.md). The critics still score 85 and 82. Remaining: the critics read the suit as a toy mannequin (owner decision 2026-10-01: keep the original hero suit unchanged, linked from `hero_suit.blend`), even hall lighting with little falloff, subtle wear, large flat locker doors in LockerDoor/LockerReverse, low-poly plants and heavy signage, LockerDoor hiding one suit per side behind open doors, and the chamber-glass reflection reading as an artefact.

## Next actions
1. Owner decisions: whether to cut or replace the plants; how much signage stays; door sizes or open angles for the locker cameras.
2. Hall lighting falloff pass, if the owner wants more change to the approved lighting.
3. Runtime: equip toggle and locker interaction (`final-pass/SUIT_EQUIP.md`), not built.
4. Re-run critics (at least 4 cycles) and a cold start.
