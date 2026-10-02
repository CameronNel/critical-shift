# Spawn Room — Task State

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Current phase:** Built; final pass run, NOT accepted (see [final-pass/REPORT.md](final-pass/REPORT.md))
**Current overall score:** Independent critics 85 and 82 of 100 on the earlier suit after the polish pass (needs >= 90); not re-scored with the HZ-01 suit
**Cold-start status:** Not run
**Authoritative source:** ../../facility-assembly/sources/spawn-room/module.blend (runtime derivative: module_optimised.blend)

## Completed

- HZ-01 owner-reference suit revision on its own task branch: see
  [the asset handoff](hero-suit-reference/README.md) and
  [asset review state](hero-suit-reference/TASK_STATE.md). New asset approval and
  runtime delivery remain pending; this does not advance room acceptance.
- Detailed scenery specification
- Build/self-review prompt
- Production rubric
- Fixed-camera plan
- Acceptance checklist
- Automated support-contact validator and tagging convention

## Worst current visible defects
Suits, Geiger drop and the polish pass (wear, doorway spill, bench posts, Material_A framing) are done; see [final-pass/REPORT.md](final-pass/REPORT.md). The critics still score 85 and 82. The 85 and 82 scores were taken on the earlier suit and predate the HZ-01 replacement (#68) and its locker LOD (#69); the HZ-01 suit's owner review and a critic rescore are pending (see [hero-suit-reference/TASK_STATE.md](hero-suit-reference/TASK_STATE.md)), so the old "toy mannequin" criticism is not a verdict on the current suit. Remaining from those critiques: even hall lighting with little falloff, subtle wear, large flat locker doors in LockerDoor/LockerReverse, low-poly plants and heavy signage, LockerDoor hiding one suit per side behind open doors, and the chamber-glass reflection reading as an artefact.

## Next actions
1. Re-run the critics (fresh context, at least 4 cycles) on the HZ-01 suit and the 90+ pass (plants cut to the briefing room, slogan notices and the duplicate notice board removed, locker door inside faces detailed, hall tubes graded; see final-pass/REPORT.md). The 85 and 82 predate all of it.
2. Owner can reverse any 90+ default (plants kept, signage restored, tube power) in `../../blender/pass_90plus.py`.
3. Runtime: equip toggle and locker interaction (`final-pass/SUIT_EQUIP.md`), not built.
4. Owner review of the HZ-01 suit, then re-run critics on the HZ-01 locker LOD (at least 4 cycles) and a cold start.

HZ-01 suit LOD: the locker library is reduced to 22,371 triangles per suit (from 114,094); see hero-suit-reference/README.md.
