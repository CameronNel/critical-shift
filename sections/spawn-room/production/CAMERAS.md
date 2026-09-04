# Spawn Room — Fixed Validation Cameras

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
