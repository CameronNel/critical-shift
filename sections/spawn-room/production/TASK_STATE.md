# Spawn Room — Task State

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Current phase:** Built; final pass run, NOT accepted (see [final-pass/REPORT.md](final-pass/REPORT.md))
**Current overall score:** Independent critics 85 and 72 of 100 on the pre-suit renders (needs >= 90); not re-scored since
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
Hero suits are done (the crew worker's own suit on a boot dock in each of the four lockers, with a baked locker strip light; owner-approved) and the Geiger checkpoint is dropped (player HUD). Remaining, from [final-pass/REPORT.md](final-pass/REPORT.md): uniform clean materials (locker paint, airlock door, floor tile), flat hall lighting and black doorways, Material_A framing, white blob in LockerReverse glass, bench uprights in Walk_C, plants and signage. Not yet re-scored since the suits.

## Next actions
1. Owner decision: does the suit reappear if the player returns or removes it (`final-pass/SUIT_EQUIP.md`); the equip toggle itself is runtime work, not built.
2. Material wear and hall/doorway lighting pass on the canonical module, then regenerate the optimised derivative.
3. Reframe Material_A; fix Walk_C bench and the LockerReverse blob.
4. Re-run critics (at least 4 cycles) and a cold start.
