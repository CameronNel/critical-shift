# Spawn Room — Task State

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Current phase:** Specification complete; build not started  
**Current overall score:** Not scored  
**Cold-start status:** Not run  
**Authoritative source:** ../blender/spawnroom.blend (future)

## Completed
- Detailed scenery specification
- Build/self-review prompt
- Production rubric
- Fixed-camera plan
- Acceptance checklist
- Automated support-contact validator and tagging convention

## Worst current visible defects
No rendered build exists yet.

## Next actions
1. Create the headless Blender build entrypoint.
2. Establish metric blockout.
3. Create fixed validation cameras.
4. Create the CS_SUPPORT_REQUIRED and dressing support collections.
5. Tag support-dependent props as they are created.
6. Run validate_contacts.py with every dressing pass.
7. Render baseline review set.
8. Start formal scoring loop.

## Last successful headless build command
Not yet established.

## Last successful render batch
None.

## Active checkpoint
None.

## Known regressions
None.

## Blockers
None recorded.


## Art-direction reset state — 2026-09-05

**Current phase:** STYLE VALIDATION SLICE  
**Previous visual pass:** REJECTED AS ART DIRECTION  
**Useful legacy content:** gameplay dimensions/routes/interaction locations only, where still valid  
**Expansion:** BLOCKED

Primary defects to prevent:
- repeated bevelled boxes;
- plastic material sameness;
- excessive signage;
- flat lighting;
- generic sci-fi devices;
- toy-like PPE;
- random filler;
- procedural cleanliness.

Next actions:
1. build one wall + door + locker/PPE + bench slice;
2. add 3–5 grounded human props;
3. establish differentiated materials;
4. light from actual practical fixtures;
5. render fixed gameplay cameras;
6. run contact validation;
7. score `RUBRIC.md`;
8. checkpoint only after pass.
