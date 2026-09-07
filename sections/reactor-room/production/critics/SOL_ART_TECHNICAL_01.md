# Sol technical audit — P02 reactor scene 01

**Scope:** independent read-only audit of the newly authored `blender/build_scene.py`, approved P02 `architecture/build_drawings.py`, and newly authored `blender/reactor_scene.blend`. The saved scene was opened only in a private headless Blender 5.2 process with two threads. No legacy 3D file was opened or imported, and no scene was changed or saved by this audit.

**Decision:** **TECHNICAL FAIL / CORRECTION REQUIRED.** P02 placement and basic circulation are sound, but six measurable assembly and connectivity defects prevent technical acceptance. This is not a visual-art score or rendered-scene acceptance.

## Blocking findings

### 1. Control-bank moving parts disconnect from their fixed and submerged interfaces

**Severity: critical**

The parenting itself is coherent: each `BANK_*_MOVING` root has 33 moving children, both roots own animation actions, and a frame-by-frame sample across frames 1–240 measured exactly Z8.60 to Z6.80 with no overshoot. The carriage-to-drive-column gap also remains a constant 0.035 m.

The interfaces do not remain physically engaged:

- At frame 1, the object named `top sliding engagement` ends at Z9.72 while the fixed housing begins at Z9.91: a **0.19 m gap at nominal**.
- At frame 192/full drop, the same gap is **1.99 m**.
- At frame 1, the drive-column bottom is Z−2.395 while the matching submerged-guide top is Z−3.545: a **1.15 m gap at nominal**.
- At full drop the drive column overlaps the guide by 0.65 m, so the lower relationship changes from detached to engaged during motion.

The source creates the fixed housing and interfaces at lines 552–567, then parents the carriage, column, gland, and short upper engagement to the moving root at lines 568–589. The basic validator at lines 1022–1028 verifies only count, axis, nominal root height, and a stored `travel_m` value; it does not measure engagement at either pose.

**Acceptance condition:** the saved animation must show continuous physical engagement at the fixed and submerged interfaces through nominal trim and the complete 1.80 m emergency travel.

### 2. Coolant headers do not connect to the pump or emergency-cooling manifold

**Severity: critical**

The saved curve geometry measures:

- Coolant SUPPLY to the actual `Pump rising outlet`: **1.0004 m minimum separation**.
- Coolant RETURN to the actual `Pump rising outlet`: **1.0004 m minimum separation**.
- Coolant SUPPLY to `Emergency cooling manifold`: **4.4573 m minimum separation**.
- Coolant RETURN to `Emergency cooling manifold`: **4.5348 m minimum separation**.

This contradicts the source statement at lines 828–832 that the grouped headers terminate in pump/ECCS risers. The curves continue to unrelated east-side endpoints instead. No current validation check measures pipe-to-port continuity.

**Acceptance condition:** each claimed functional header endpoint must visibly meet its corresponding equipment port, with no free-floating end or incorrect destination.

### 3. D01 and D02 are not animation-ready assemblies

**Severity: high**

The door poses and openings are correctly placed and their route volumes are clear. However, each door consists of four independent, unparented objects: leaf, vision glass, panic bar, and marking. None has a door action. The vision glass and panic bar share the hinge-space transform, but each marking has its own origin away from the hinge. Rotating only the leaf therefore leaves attached parts behind.

The construction is visible at lines 945–951. It creates the parts inside a hinge transform but never binds them to one common moving assembly.

**Acceptance condition:** every visible part attached to each door must follow one hinge motion as a single animatable assembly.

### 4. The south service gate is narrower than the specified clear opening

**Severity: high**

The two fixed rail-post centre lines are X−0.70 and X+0.70 m. Each rail upright has a 0.032 m radius, leaving **1.336 m surface clearance**. The reactor specification requires **1.40 m clear**. The source comment at line 504 calls the centre-line separation a clear dimension, while lines 505–516 build the posts on those centre lines.

The gate does have a correctly placed pivot root and four child objects. It has no action, which is acceptable for a static review pose but does not prove operation.

**Acceptance condition:** measured free space between the physical obstructions at the gate must satisfy the written 1.40 m clear requirement.

### 5. The saved scene does not match the current procedural source

**Severity: high**

The current `utilities()` source declares three `Cabinet power drop` curves at lines 848–850. The saved `reactor_scene.blend` contains only two. Its two stored paths also differ from the current source points, and there is no saved drop serving Bank Control.

The current source SHA appears in `art/renders/art-02/validation.json`, but the validation records only total object counts and does not assert the declared drop count or endpoints. The saved geometry therefore disproves source/scene parity despite the matching hash field.

**Acceptance condition:** a fresh reproducible build must contain the same utility objects and paths declared by the audited source, and validation must detect this class of omission.

### 6. The observation glazing has unsupported seams

**Severity: medium**

The two W01 panes have the correct P02 bounds and datums, but their closest X separation from the opaque jamb/head/sill solids is **0.037 m**. The horizontal observation-floor glass ends at X11.80 while the main Control floor begins at X11.81, leaving a **0.010 m seam** across the interior edge. The only floor-glass frame objects are at the two Y ends.

These gaps come from the glazing and frame construction at lines 860–876. They are small enough to escape broad visual checks but establish that the panes are not physically retained by the named frame geometry.

**Acceptance condition:** the saved glazing must visibly bear on or be retained by opaque structure, with no unsupported free edge presented as a structural floor surface.

## Verified passes

- **P02 placement:** the Control floor spans X11.81–14.76, Y−3.20–3.20; the observation-floor glass covers the approved 5.40 m Y span; and the stair roof spans X12.46–18.71, Y3.20–6.40. These agree with the approved drawing source at `architecture/build_drawings.py` lines 21–28.
- **Pool:** the structural rim measures 7.80 m nominal diameter, the water top is Z−0.45, and the pool bottom top is Z−6.50.
- **Vestibule and doors:** the vestibule floor spans X11.16–12.46, Y1.60–5.60. No mesh intrudes into the south approach clear volume. D01 is parked north in the vestibule and D02 is parked inside its reserved Control-room swing area; no unrelated mesh blocks either route.
- **Stair geometry:** all four flights contain 13 treads, all 52 treads intersect a load-bearing stringer, and five landing slabs occupy the correct 0/2.5/5/7.5/10 m levels. The flight rail-face clearance is 1.20 m.
- **Ground support:** the measured bottoms of the registered columns, station skids, rack feet, workbench legs, and kiosk foot are at finished-floor Z0.00. Operator-desk plinths are at Control floor Z10.00. Pool rail feet correctly bear at the raised rim surface.
- **Bank hierarchy:** fixed housings remain outside the moving roots, both moving groups retain all sampled children, and the exact 1.80 m root motion is preserved.
- **Scene policy:** saved scene properties identify `build_scene.py` as the factory-scene authoring source and P02 as layout authority. No external or old 3D import was observed.

## Validation gap

`validate()` at lines 1014–1045 passes 53 checks, but 38 of them are registered base-height contacts. It does not test route-volume occupancy, door child relationships, gate surface clearance, bank engagement at animated poses, utility endpoint continuity, glazing support, or equality between declared and saved utility objects. Its current PASS result is therefore accurate only for its narrow checks and cannot establish complete technical validity.

Rendered lighting, materials, composition, Valorant-style execution, and overall visual quality remain unassessed in this report.
