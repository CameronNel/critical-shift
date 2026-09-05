# Critical Shift — Spawn Room Build and Self-Review Prompt


# 0. ART DIRECTION RESET — READ BEFORE BUILDING ANYTHING

The previous visual result is rejected.

Do **not** polish the existing generic low-poly sci-fi look. Preserve only useful gameplay dimensions, circulation, doorway positions and interaction locations.

## Target

Build **grounded stylized semi-realism**:

- believable real-world proportions;
- simplified but specific medium-complexity geometry;
- strong silhouettes;
- tactile, differentiated materials;
- restrained colour blocking;
- localized wear;
- strong practical lighting;
- contact shadows;
- sparse human storytelling;
- visual rest between focal clusters.

Primary influence: Valorant-style environmental art principles.  
Secondary influence: PEAK-style readability and restraint.  
Neither game is an asset/content template.

## Immediate hard vetoes

Stop and redesign if the scene reads as:
- repeated bevelled cuboids;
- low-poly asset pack;
- Three.js demo;
- glossy/satin plastic;
- generic sci-fi;
- showroom-clean procedural environment;
- toy-like PPE;
- wall of labels/screens;
- flat even ceiling lighting;
- photoreal AAA kitbash.

## Bevel rule

A bevel may finish an already-designed form. It may **never be the design**.

Locker, bench, door, scanner, wall cabinet, suit bay and briefing equipment must each have distinct construction logic.

## Signage rule

Text is not environment design. Use only functional navigation, hazard and procedure signs. Remove labels whose only job is to make a boring prop seem specific.

## PPE rule

Hazmat suits are clothing:
- believable adult proportions;
- fabric volume;
- broad folds;
- wearable seams/closures;
- believable visor, gloves and boots;
- simplified but not faceted/toy-like.

## Human-detail rule

Prefer:
- boots under a bench;
- one glove;
- used clipboard;
- mug;
- maintenance tape;
- folded suit;
- respirator filter;
- small toolkit;
- dented bin;
- repaired pipe;
- worn floor marker.

Do not scatter random props merely to increase density.

## Plant rule

Plants are **optional, not a requirement**. Default to zero. Add one only if the composition benefits from a deliberate humanizing object. Never use a plant to fill an empty corner.

## Required generated references

Inspect before modelling:
- `../art/reference/spawn_style_target.svg`
- `../art/reference/spawn_detail_density.svg`
- `../art/reference/spawn_material_lighting.svg`

## STYLE VALIDATION SLICE — DO THIS FIRST

Do not rebuild the whole Spawn Room.

Build only:
- one wall section;
- one believable door;
- one locker/PPE station;
- one bench;
- one ceiling/practical light;
- one utility element;
- 3–5 grounded storytelling props.

Render it from the actual gameplay camera.

The slice must score 8/10+ on `../production/RUBRIC.md` with no automatic veto.

Only after the slice passes may you propagate its geometry, materials, lighting and detail language through the hallway, briefing room and remaining locker/suiting area.

Style compliance is more important than content completeness.


<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**File:** spawnroomprompt.md  
**Target section:** Spawn Room  
**Required scenery spec:** ../scenery/spawnroom.md  
**Global art authority:** ../../../design/ART_DIRECTION.md  
**Game authority:** ../../../design/GAME_SPEC.md  
**Autonomous build authority:** ../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md  
**Persistent production state:** ../production/TASK_STATE.md  
**Rubric:** ../production/RUBRIC.md  
**Fixed cameras:** ../production/CAMERAS.md  
**Checklist:** ../production/CHECKLIST.md

---

# 1. Mission

Build the Critical Shift Spawn Room as a polished, editable, stylized 3D environment.

You are not being asked for a one-pass concept or a rough prototype.

You are responsible for:

- reading the specification
- planning the scene
- building the scene
- rendering and visually inspecting your own work
- measuring functional clearances
- identifying your own failures
- fixing them
- re-rendering
- repeating the process until the acceptance criteria pass

Treat yourself as the environment artist, technical artist, scene assembler and QA reviewer.

The final scene must look deliberately authored and suitable for a real stylized game.

---

# 2. Tool and Output Rules

## Execution architecture

Use a **headless-first, MCP-assisted** pipeline.

The authoritative build must be reproducible from a fresh process with Blender CLI and versioned scripts.

MCP is encouraged for:
- launching and supervising Blender jobs;
- reading/writing state;
- collecting renders;
- coordinating critics;
- aggregating scores;
- inspecting technical state;
- repository operations;
- later Unity integration.

MCP is not a hard dependency. The room must still build and cold-start validate without MCP.

## Preferred authoring tool

Use Blender for the authoritative environment source.

Prefer:

- editable meshes
- clean hierarchy
- reusable modular assets
- procedural modeling where it genuinely improves consistency
- Blender Python for repeatable generation and correction
- Geometry Nodes for repeated structures where helpful
- real object separation for anything likely to animate or interact

## Three.js prohibition

Do not use Three.js for the room build.

Do not create the authoritative environment as a browser scene.

Do not use a web-rendering prototype as the final visual target.

This prohibition exists to prevent the recurring failure mode where the scene is composed from primitive web-demo geometry with generic glossy materials and is then mistaken for finished environment art.

Three.js itself is not a synonym for bad art, but it is not part of this production pipeline.

## No primitive-as-final rule

Cubes, cylinders and planes are valid starting primitives.

They are not automatically final assets.

Before an object is accepted, ask:

- does its silhouette look intentionally designed?
- are its proportions stylized?
- does it have meaningful bevels, faceting or tapering?
- does it fit the room's shape language?
- does it look like a placeholder?

If it still looks like a default primitive, refine it.

---

# 3. Style Target

Follow the global art direction exactly.

The desired result is:

- stylized
- readable
- charming
- low-to-mid poly
- strong silhouette
- broad colour blocks
- tactile matte materials
- sparse but meaningful detail
- intentional lighting
- rich environmental storytelling
- clear first-person gameplay routes

Valorant-style environment principles are the primary reference for clean, believable stylized semi-realism. PEAK is a secondary reference for readability and restraint only. Do not reproduce assets or distinctive designs from either game.

Do not drift into:

- AAA photorealism
- cinematic hard-surface realism
- generic realistic nuclear facility
- generic sci-fi corridor
- shiny plastic
- random blocks
- low-effort greybox
- cartoon/faceted low-poly presentation
- dense realistic kitbash
- toy-room aesthetics
- over-smoothed blobs
- geometry covered in unnecessary greebling

---

# 4. Required Spatial Layout

Create a short internal hallway inside a larger building.

From the spawn position:

- optional briefing room is on the left
- locker room is on the right
- operational exit is straight ahead
- Geiger/radiation checkpoint is at the exit

Locker room:

- exactly 2 hero suits on the left
- exactly 2 hero suits on the right
- integrity check chamber in the middle

Briefing room:

- 4 primary tutorial seats
- tutorial/briefing display as focal object
- optional social feel
- no forced route through it

The scene must communicate the layout from the initial view without UI arrows.

---

# 5. Build Method

Work in controlled passes.

Do not attempt to model and dress the entire scene in one uncontrolled generation step.

## Pass 0 — Read and extract constraints

Before changing the scene:

1. Read spawnroom.md completely.
2. Read the global art direction.
3. List the non-negotiable layout constraints.
4. List the hero objects.
5. List the required prop categories.
6. List the major visual failure modes.
7. Create a short implementation plan.

Do not begin detailed modeling before this is complete.

## Pass 1 — Metric blockout

Build only:

- hallway shell
- briefing room shell
- locker room shell
- operational exit
- integrity chamber placeholder
- four suit-bay placeholders
- main furniture footprints

Set real-world scale.

Use a human-height first-person reference.

Validate:

- hallway width
- doorway width
- ceiling height
- four-player circulation
- chamber clearance
- seat spacing
- exit visibility

If the layout is not immediately readable from the spawn camera, fix it now.

Do not proceed merely because the geometry technically exists.

## Pass 2 — Architectural design

Convert the blockout into deliberate stylized architecture.

Add:

- wall thickness
- deep door frames
- ceiling rhythm
- tiled/sealed floor language
- lower-wall treatment
- service panels
- restrained ventilation/utility routes
- structural framing
- inaccessible-building cues

Then render the Spawn View.

Critique the image.

Explicitly answer:

- does this still look like a greybox?
- are walls merely rectangles?
- do doors feel substantial?
- is the architecture too realistic?
- is it too simple?
- does the larger-building illusion work?

Fix all failed answers before proceeding.

## Pass 3 — Hero objects

Build the main authored objects:

- four suit stations
- four hero suits or production-ready presentation stand-ins if the final character suit asset is supplied separately
- central integrity chamber
- tutorial display
- operational exit door
- Geiger/radiation checkpoint
- briefing chairs/bench system

Each hero object must be inspected from multiple angles.

Do not accept an object because it looks good from one beauty camera.

## Pass 4 — Material foundation

Create a restrained reusable material palette.

At minimum:

- painted wall
- tile/sealed floor
- powder-coated equipment
- structural metal
- dark rubber
- soft chair vinyl/padding
- glass
- paper/card
- optional plant pot only if deliberately used
- optional plant foliage only if deliberately used
- emissive indicator
- screen material

Render a material review.

Check specifically for the plastic failure mode.

Ask:

- is roughness too uniform?
- are all materials responding to light the same way?
- do painted metal and molded surfaces look identical?
- are floors unnaturally glossy?
- does glass look like clear plastic?
- are plants shiny?
- do chairs look like molded toy furniture?

Correct material values and lighting until each family reads distinctly.

## Pass 5 — Primary dressing

Add the larger secondary objects:

- benches/chairs
- notice boards
- cabinets
- optional single plant only when compositionally justified
- bins
- wall art
- portrait frames
- technical poster boards
- floor mats
- maintenance trolley or compact tool support
- directional signage

For every wall-, floor-, or ceiling-supported dressing prop, assign the support-contact metadata required by the shared protocol. All support-dependent dressing must be registered in the validation collections. Use explicit support anchors for irregular shapes.

Render all four required composition views.

Check hierarchy.

If secondary dressing competes with the routes or hero objects, reduce it.

## Pass 6 — Narrative dressing

Add authored small detail:

- portraits
- shift papers
- safety procedures
- suit diagrams
- crew recognition
- inspection sheets
- handwritten notes
- personal photos
- labels
- maintenance tag
- replacement tile
- small localized rubble
- subtle scuffs and repair evidence

Every paper/image asset must have a believable physical mounting method.

Every paper, portrait, framed artwork, sign, notice board and similar wall-mounted object must:
- be registered for support-contact validation;
- identify its exact support target;
- define its support direction;
- pass the automated gap/penetration/orientation checks.

Do not float decals or image planes in space.

## Pass 7 — Lighting

Build the safe-zone lighting hierarchy.

Hallway:

- clear practical rhythm
- easy navigation
- modest forward pull to the exit

Briefing:

- slightly softer/warmer
- tutorial display readable

Locker:

- brightest/cleanest
- each suit silhouette readable
- chamber subtly emphasized

Exit:

- slightly more industrial contrast
- Geiger station obvious

Render again.

Do not accept “moody” lighting that makes navigation unclear.

---

# 6. Mandatory Self-Inspection Loop

This loop is not optional.

After every major build pass:

1. Save the Blender source and update ../production/TASK_STATE.md.
2. Render the defined validation cameras.
3. Inspect each render as if reviewing another artist's work.
4. At formal review points, run fresh-context specialist critics using only the scenery goal, global art requirements, fixed-camera renders and rubric. Do not give visual critics the builder's reasoning.
5. Write down visible defects.
6. Classify each defect:
   - layout
   - scale
   - silhouette
   - material
   - lighting
   - prop quality
   - clutter
   - emptiness
   - collision/clearance
   - worldbuilding
   - style drift
7. Score the room using ../production/RUBRIC.md.
8. Record the three to five highest-impact defects in TASK_STATE.md.
9. Fix those defects.
10. Render the identical cameras again.
11. Compare new renders against the previous cycle.
12. Mark each targeted issue improved / unchanged / regressed.
13. Repair or roll back regressions.
14. Update rubric scores and TASK_STATE.md.
15. Repeat until all completion gates pass.

Do not perform a critique and then stop without making corrections.

Do not say “looks good” unless the evidence passes the explicit checklists below.

---

# 7. Objective Geometry Checks

Visual self-critique is necessary but not sufficient.

Use Blender scripting or direct measurements to validate objective constraints.

Check:

- exactly four suit stations exist
- two are left of the locker-room center line
- two are right of the locker-room center line
- integrity chamber occupies the center region
- no suit bay overlaps chamber circulation
- hallway clear width remains within target
- room doors remain traversable
- chairs do not overlap each other
- chairs have plausible seated human scale
- no prop penetrates doors
- no prop blocks the operational exit
- no decorative object intrudes into primary walking route
- no visibly floating props
- no duplicate overlapping meshes
- no inverted or broken normals on visible geometry
- no absurdly tiny or giant asset scale
- pivot/origin placement is sensible for future interactive parts
- every support-dependent dressing prop is registered for contact validation
- wall-mounted props are within 5 mm of their intended support surface
- support penetration does not exceed 2 mm
- support orientation is plausible
- floor/ceiling props with explicit support anchors pass contact checks

Run `validate_contacts.py` after dressing changes and during every formal review cycle. A contact-validation failure is a technical critical failure.

Create automated checks where practical.

---

# 8. Validation Cameras

Use the permanent camera definitions in ../production/CAMERAS.md.

Maintain the named cameras exactly once formal review begins. Their transforms, focal lengths, aspect ratio and render framing are part of the evidence baseline.

## VALIDATE_Spawn

Human eye height at the starting position, looking toward the operational exit.

Must simultaneously communicate left briefing, right locker and forward exit.

## VALIDATE_LockerDoor

From the locker-room entrance.

Must show 2-left, 2-right and chamber-center structure clearly.

## VALIDATE_BriefingDoor

From briefing-room entrance.

Must show tutorial focal display and usable seating.

## VALIDATE_ExitReverse

Near the Geiger station looking back toward spawn.

Tests reverse readability and dressing balance.

## VALIDATE_Walk_A / B / C

Additional first-person-height views through circulation pinch points.

## VALIDATE_Material_A

A material audit view containing representative wall, floor, painted equipment, rubber, paper and glass.

## VALIDATE_Hero_A

A hero-composition audit of the suits and integrity chamber.

Do not evaluate only from elevated beauty cameras.

All cycle-to-cycle comparisons must use identical validation-camera settings.

---

# 9. Specific Anti-Plastic Review

Run this review after material setup and again before final acceptance.

Inspect each major material family under scene lighting.

Fail the pass if:

- almost every surface has the same specular response
- walls look like injection-molded plastic
- painted metal looks like glossy toy material
- chairs look like cheap default plastic
- plants look waxed
- floors reflect like wet resin
- roughness is visually uniform
- bevel highlights are excessively sharp and synthetic
- colours are overly saturated and clean without tonal hierarchy
- lighting is so broad that every surface appears smooth and flat

Fix using:

- more appropriate roughness
- better value separation
- restrained surface variation
- material-specific response
- lighting direction
- geometry refinement
- controlled bevel/facet treatment
- selective matte finishes

Do not “fix plastic” by adding realistic scratches everywhere.

---

# 10. Specific Anti-Blockout Review

Fail the pass if:

- walls remain naked cubes
- benches are simple boxes with no designed silhouette
- suit bays are plain rectangular holes
- chamber is just a cylinder/glass tube
- Geiger station is a box with a screen
- any deliberately used plant looks like a believable stylized plant, never default low-poly foliage
- chairs look like primitive classroom props
- door is a slab without framing/seal logic
- ceiling is a flat plane with lights
- every prop has 90-degree box geometry

Refine shape language through:

- taper
- thickness
- faceting
- controlled chamfers
- layered masses
- supports
- clear functional pieces
- stylized curvature
- proportion

Keep detail broad.

---

# 11. Dressing Review

For every validation camera ask:

## Does the scene feel inhabited?

Evidence should include some of:

- portraits
- papers
- staff signage
- shift information
- personal note
- maintenance evidence
- chairs not perfectly aligned
- one deliberate humanizing accent (plant only if justified)
- repaired tile
- small human object

## Does the scene feel cluttered?

If yes:

- remove filler
- consolidate paper clusters
- simplify utility routes
- increase negative space
- move props away from gameplay routes

## Does the scene feel empty?

If yes:

- add one meaningful composition cluster
- add wall content
- strengthen material rhythm
- add a restrained furniture or human-use element; use a plant only if specifically justified
- improve ceiling/floor design

Do not solve emptiness with dozens of random small props.

---

# 12. Final Quality Gates

Do not mark the room complete until each gate passes.

## Gate A — Layout

PASS only if a new viewer can identify the three choices from Spawn View:

- briefing left
- locker right
- exit forward

## Gate B — Locker composition

PASS only if LockerDoor clearly shows:

- exactly two suit stations left
- exactly two suit stations right
- chamber center
- readable circulation

## Gate C — Briefing usability

PASS only if:

- at least four seats are clearly usable
- tutorial screen has clear sightlines
- optional character is obvious

## Gate D — Larger-building illusion

PASS only if:

- architecture, signage, service routes and inaccessible cues imply a larger complex
- the player does not mistake inaccessible zones for the main route

## Gate E — Visual quality

PASS only if:

- scene no longer reads as greybox
- scene no longer reads as random primitives
- scene no longer reads as plastic
- scene does not drift into either photoreal AAA or cartoon low-poly
- scene is cohesive with the Critical Shift art direction

## Gate F — Dressing

PASS only if all required categories are represented intentionally:

- portraits
- information papers
- original art/posters
- optional plant only if justified; plant is not required
- chairs/benches
- small localized rubble/repair evidence
- tile variation

## Gate G — Technical cleanliness

PASS only if:

- no duplicate geometry
- no obvious z-fighting
- no floating props
- sensible scale
- clean hierarchy
- reusable asset grouping
- major interactive pieces remain separate
- source remains editable
- support-contact validation passes with zero failures

---

# 13. Minimum Iteration Requirement

Perform at least four full visual correction cycles after the first visually complete scene exists.

Cycle 1:
- architecture
- layout
- scale
- route readability

Cycle 2:
- silhouette
- materials
- lighting
- anti-plastic cleanup

Cycle 3:
- lighting
- dressing
- narrative detail
- clutter balance

Cycle 4:
- holistic regression audit
- technical cleanup
- final composition
- cold-start preparation

If any major quality gate still fails after cycle 4, continue iterating.

Four cycles are a minimum, not permission to stop.

## Stagnation rule

If the room remains below the completion threshold and improves by less than one rubric point across two consecutive complete cycles, stop adding microdetail.

Perform a structural pass on layout, proportions, hero placement, silhouette hierarchy, negative space, lighting structure and material palette.

Do not try to rescue mediocre composition with prop spam.

---

# 14. Evidence Required Before Declaring Done

The room may not be declared done until:
- overall rubric score is at least 90/100;
- every category reaches at least 85% of its available points;
- zero critical failures remain;
- the final two full cycles are materially stable;
- a fresh Blender process passes cold-start validation.

Before completion, provide:

- final Spawn validation render
- final LockerDoor validation render
- final BriefingDoor validation render
- final ExitReverse validation render
- final Material_A validation render
- final Hero_A validation render
- final scored RUBRIC.md
- updated TASK_STATE.md
- cold-start PASS evidence
- final ../production/contact_validation.json with PASS
- list of automated/measurement checks performed
- list of major defects discovered during self-review
- description of how each defect was corrected
- confirmation that Three.js was not used
- confirmation that the authoritative editable source is Blender
- confirmation that the final scene passes every quality gate

Do not hide failed checks.

Do not claim completion based only on code execution or file generation.

## Cold-start requirement

Before final delivery:
1. save source and production state;
2. close the active Blender process;
3. launch a fresh Blender process;
4. open or rebuild the authoritative source;
5. verify dependencies and materials;
6. rerun objective checks;
7. rerender mandatory validation cameras;
8. compare against approved renders;
9. mark cold-start PASS/FAIL in TASK_STATE.md.

The work is done only when the room looks correct, functions spatially, survives specialist criticism and regression review, and reproduces from a fresh process.

---

# 13. Commercial screenshot test

Before completion, render the fixed gameplay cameras at final intended exposure and ask:

1. Would this plausibly be a screenshot from a released stylized PC game?
2. Does every major prop have a specific silhouette?
3. Can painted metal, plastic, rubber, fabric, glass, wall and floor materials be told apart without labels?
4. Is the brightest/most detailed area actually important?
5. Are there quiet areas?
6. Does the room look used, not randomly decorated?
7. Are support contacts visibly convincing?
8. Has text/signage been kept subordinate?
9. Is anything obviously a bevelled box with a colour on it?
10. Is anything trying to look more realistic than the rest of the scene?

If question 1 is no, or question 9 is yes for a major prop, continue iterating.
