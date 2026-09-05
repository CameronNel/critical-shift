# Spawn Room — Fixed Validation Cameras

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Once formal review begins, transforms and focal lengths remain fixed unless a camera is proven invalid and the change is documented.

## Required cameras

### VALIDATE_Spawn
Human eye height at spawn looking toward the operational exit.

Must prove simultaneously:
- briefing room is left;
- locker room is right;
- exit is forward;
- hallway scale works for four players;
- the building feels larger than the playable slice.

### VALIDATE_LockerDoor
Human eye height at locker entrance.

Must prove:
- exactly two suit bays left;
- exactly two suit bays right;
- integrity chamber centered;
- circulation remains obvious;
- suits read as hero objects.

### VALIDATE_BriefingDoor
Human eye height at briefing entrance.

Must prove:
- at least four usable seats;
- tutorial display is focal;
- sightlines work;
- room reads as optional/social.

### VALIDATE_ExitReverse
Near Geiger station looking back toward spawn.

Must prove:
- reverse navigation remains coherent;
- dressing is balanced;
- hallway does not become visually dead from the far end.

### VALIDATE_Walk_A
Primary hallway pinch point.

### VALIDATE_Walk_B
Integrity-chamber circulation edge.

### VALIDATE_Walk_C
Briefing seating aisle.

### VALIDATE_Material_A
Close/medium view containing wall, floor, painted equipment, rubber, paper and glass.

Used specifically for anti-plastic review.

### VALIDATE_Hero_A
Locker hero composition emphasizing suit silhouette and chamber quality.

## Render consistency
Use identical:
- camera transform;
- focal length;
- aspect ratio;
- resolution;
- color-management settings;
- major lighting state

for cycle-to-cycle comparisons.


## Art-direction camera checks

Every spawn validation camera must let reviewers judge:
- believable human scale;
- door / wall / bench / locker construction;
- PPE fabric volume and proportion;
- material separation;
- localized practical lighting;
- contact shadow and support contact;
- negative space;
- whether signage is subordinate to the environment;
- whether detail clusters feel occupied rather than procedurally decorated.

At least one fixed camera must expose the locker/suit area and one must expose the briefing room. Do not use only flattering beauty angles.


## Reference-to-camera mapping

- Entry camera compares against plates 00, 01 and 17.
- Hall-forward camera compares against plates 07, 08, 11 and 12.
- Locker-entry camera compares against plates 03, 04, 05, 06, 21 and 23.
- Locker-reverse camera compares against plates 09, 10, 13 and 15.
- Briefing-entry camera compares against plates 02, 18 and 19.
- Material-close camera compares against plates 10, 20 and 24.

Each review note should cite the plate number being used as the visual criterion.
