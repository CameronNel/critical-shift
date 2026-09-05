# Critical Shift — Autonomous Section Build Protocol

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Status:** Mandatory production protocol  
**Applies to:** Every playable room, corridor, facility zone and major 3D environment section  
**Primary DCC:** Blender  
**Execution model:** Headless-first, MCP-assisted

---

# 1. Principle

Critical Shift environments are not one-shot generated scenes.

Every section must be built as a repeatable long-horizon production loop:

**define → build → render → inspect pixels → score → diagnose → repair → rerender → compare → repeat → cold-start verify**

The agent is not allowed to declare a section complete because:
- scripts executed successfully;
- Blender saved a file;
- the scene tree appears complete;
- the viewport looks plausible;
- a single beauty render looks attractive;
- it subjectively “feels done”.

Completion is earned through evidence.

The protocol deliberately prioritizes a detailed definition of **what good looks like** over micromanaging every modeling operation. The model may choose efficient Blender techniques internally, but it must satisfy the spatial, visual and technical requirements defined by the section specification, global art direction and this protocol.

---

# 2. Execution Architecture

## 2.1 Headless-first

The authoritative environment build must be reproducible through Blender CLI and scripts from a fresh process.

Preferred core loop:
1. invoke Blender headlessly;
2. run versioned Python/build scripts;
3. save an editable .blend checkpoint;
4. render named fixed cameras;
5. inspect the rendered images;
6. record defects and scores;
7. modify scripts/scene;
8. rerun;
9. compare same-camera outputs;
10. repeat.

A graphical Blender session may be used for investigation, but the production pipeline must not require manual UI manipulation.

## 2.2 MCP-assisted

MCP is approved and encouraged as the orchestration/supervision layer.

MCP may:
- launch Blender jobs;
- inspect files and logs;
- edit scripts and planning documents;
- collect renders;
- organize critic runs;
- aggregate scores;
- compare iterations;
- inspect Blender state when useful;
- manage repository changes;
- later coordinate Unity import and runtime validation.

MCP must not become the only way the room can be built.

A valid room package must remain reproducible without MCP from:
- the repository;
- Blender;
- the documented command/build entrypoint;
- the room specification;
- the production state files.

## 2.3 Three.js

Three.js is not an approved authoritative environment-authoring path for production rooms.

Browser prototypes may be used for temporary visualization only when explicitly approved.

Final environment authorship belongs in Blender and final runtime integration belongs in the selected game engine.

The prohibition is not because Three.js intrinsically causes poor art. It exists because the project has repeatedly suffered from a web-demo failure mode:
- primitive-heavy geometry;
- generic glossy materials;
- insufficient lighting design;
- weak prop dressing;
- blockout forms being mistaken for finished art.

The production protocol must prevent that entire failure mode.

---

# 3. Required Room Package

Every section must use:

    sections/<section>/
    ├── scenery/
    ├── prompt/
    ├── blender/
    ├── art/
    ├── assets/
    └── production/
        ├── TASK_STATE.md
        ├── RUBRIC.md
        ├── CAMERAS.md
        ├── CHECKLIST.md
        ├── critics/
        ├── renders/
        │   ├── review/
        │   └── final/
        └── checkpoints/

Room-specific source files must not spill into the repository root.

---

# 4. Persistent State

## 4.1 TASK_STATE.md

The builder must continuously maintain TASK_STATE.md.

It records at minimum:
- current phase;
- current rubric score;
- per-category scores;
- completed work;
- worst visible defects;
- next actions;
- last successful headless build command;
- last successful render batch;
- active checkpoint;
- known regressions;
- blocked items;
- cold-start status.

Update it after every full review cycle.

This file exists so a fresh context can resume without inventing history.

## 4.2 Checkpoints

Create meaningful checkpoints before risky structural or material changes.

A checkpoint should make it possible to roll back a regression instead of “fixing” the fix until the scene is worse.

Do not checkpoint every trivial edit.

---

# 5. Fixed Validation Cameras

Every room must define permanent named evaluation cameras before serious polish begins.

Cameras are evidence, not marketing.

They must cover:
- entry/readability;
- primary route;
- hero functional composition;
- reverse view;
- circulation pinch points;
- material/lighting problem areas;
- important secondary rooms;
- any area that could be hidden by flattering beauty framing.

Once formal review begins, camera transform and focal length remain fixed unless the camera itself is proven invalid. If changed, record why and establish a new baseline.

All iteration comparisons must use the same camera, render settings and output framing.

---

# 6. Pixel-Based Review

Visual criticism must be grounded in rendered pixels.

Critics must not award visual quality because:
- object names look organized;
- the script claims a feature exists;
- the builder describes the intended effect;
- the scene tree contains many assets;
- material node graphs appear complicated.

If the intended quality is not visible in the render, it does not count.

Technical checks are evaluated separately.

---

# 7. Fresh-Context Specialist Critics

At formal review points, use fresh-context critics wherever tooling permits.

A critic should receive only:
- the section objective/specification;
- relevant global art requirements;
- current fixed-camera renders;
- the scoring rubric.

The critic should not receive:
- the builder's chain of reasoning;
- excuses;
- implementation effort;
- previous self-congratulation;
- code unless performing the technical critic role.

Default critic disciplines:

1. **Spatial Readability Critic**
   - navigation
   - circulation
   - functional hierarchy
   - scale
   - first-person clarity

2. **Stylized Art Direction Critic**
   - silhouette
   - shape language
   - PEAK-level simplification/readability without copying
   - consistency
   - anti-AAA drift
   - anti-placeholder drift

3. **Materials / Anti-Plastic Critic**
   - roughness differentiation
   - material identity
   - shader response
   - unwanted gloss
   - toy/plastic appearance
   - texture/noise discipline

4. **Lighting / Atmosphere Critic**
   - hierarchy
   - readability
   - focal guidance
   - mood
   - emissive discipline
   - exposure consistency

5. **Environmental Storytelling Critic**
   - human presence
   - prop purpose
   - signage/paper/art quality
   - clutter balance
   - larger-world implication
   - specificity over filler

6. **Blender Technical Quality Critic**
   - scale
   - duplicate geometry
   - intersections
   - normals
   - pivots/origins
   - object separation
   - modifiers
   - missing dependencies
   - reproducibility
   - headless/cold-start behavior

Critics should be skeptical. Their job is to find failures.

---

# 8. 100-Point Default Rubric

Unless a room defines a stricter rubric:

- Layout / route readability: **20**
- Art-direction compliance / silhouettes: **20**
- Hero objects / focal clarity: **15**
- Materials / anti-plastic quality: **15**
- Lighting / atmosphere: **10**
- Dressing / worldbuilding: **10**
- Technical cleanliness / reproducibility: **10**

Total: **100**

Room-specific rubrics may redistribute points when justified, but must still total 100.

---

# 9. Completion Thresholds

A room cannot be marked complete until:

- overall score is **90/100 or higher**;
- every rubric category reaches at least **85% of its available points**;
- there are **zero critical failures**;
- every mandatory validation camera passes;
- every objective geometry/clearance check passes;
- the final two full review cycles contain no material regression;
- a fresh Blender process can open/build/render the final state;
- all required outputs are present.

A builder is not allowed to round 89.4 up because it is tired.

---

# 10. Review Cycle

Each full review cycle follows this exact order:

1. save/checkpoint current source;
2. run objective/geometry checks;
3. render all required validation cameras;
4. run specialist critique;
5. score the rubric;
6. identify the three to five highest-impact defects;
7. record them in TASK_STATE.md;
8. repair those defects;
9. rerun objective checks;
10. rerender the identical cameras;
11. compare each new render to the prior render;
12. mark each target issue:
    - improved;
    - unchanged;
    - regressed;
13. roll back or repair regressions;
14. update rubric and TASK_STATE.md;
15. begin another cycle if completion thresholds are not met.

Do not spend a full cycle polishing tiny props while a structural problem remains.

---

# 11. Minimum Iteration

After the first visually complete version exists, perform at least **four** complete review cycles.

Suggested emphasis:

- Cycle 1: architecture, scale, circulation, composition
- Cycle 2: silhouettes, hero assets, material language
- Cycle 3: lighting, dressing, environmental storytelling
- Cycle 4: holistic regression audit, technical cleanup, final balance

Four cycles are a minimum, not a stop condition.

---

# 12. Stagnation / Structural-Pass Rule

Track rubric movement.

If:
- the score remains below completion threshold; and
- improvement is less than **1 point across two consecutive full cycles**,

stop adding small props and microdetail.

Perform a structural pass.

A structural pass may revisit:
- room proportions;
- route widths;
- major architecture;
- hero object size/placement;
- silhouette hierarchy;
- furniture density;
- negative space;
- ceiling/floor rhythm;
- lighting hierarchy;
- material palette;
- major prop groups.

The purpose is to prevent a mediocre composition from being buried under increasingly desperate decoration.

---

# 13. Regression Control

Every fixed-camera render must have a prior-cycle baseline.

For each correction target, record:
- prior image;
- new image;
- intended improvement;
- result: improved / unchanged / regressed.

If a change improves one camera but damages another, treat that as a real tradeoff and resolve it. Do not silently choose the flattering view.

The final two cycles must be materially stable.

---

# 14. Objective Validation

Where practical, use Blender Python to automatically validate:
- exact required object counts;
- bounding-box clearances;
- room dimensions;
- door/route widths;
- player circulation;
- duplicate/intersecting objects;
- floating props;
- missing materials;
- missing image dependencies;
- non-manifold/problem geometry where relevant;
- normals;
- origin/pivot sanity;
- hidden accidental objects;
- render camera existence;
- render resolution;
- file save path;
- linked dependency availability;
- support-dependent prop contact.

## 14.1 Support-contact validation

Fixed cameras do not prove physical contact. A poster can float off a wall, a plant can hover above the floor, or a ceiling fixture can be detached while every review camera misses the gap.

Every support-dependent prop must therefore be validated geometrically.

For each wall-, floor-, or ceiling-supported prop, record:
- the intended support target;
- the expected direction from prop toward support;
- maximum allowed gap;
- maximum allowed penetration;
- orientation tolerance;
- explicit support anchors when bounding-box contact is insufficient.

The validator must fail when:
- a support-dependent prop is not registered for validation;
- the intended target does not exist;
- no support surface is found in the expected direction;
- the gap exceeds tolerance;
- penetration exceeds tolerance;
- the contacted surface is at an implausible angle;
- a support anchor is floating.

Recommended default tolerances:
- maximum visible gap: **0.005 m (5 mm)**;
- maximum penetration: **0.002 m (2 mm)**;
- maximum support-angle deviation: **12°**.

Thin wall dressing such as papers, portraits, signs, notice boards and framed art must use this system.

Floor props and ceiling props must also use it when their contact cannot be proven reliably from ordinary collision/clearance checks.

Use explicit child support-anchor empties for irregular objects such as chairs, benches, plants, pipes or fixtures when a bounding-box face would create false results.

A room cannot pass technical validation while any required support-contact check fails.

Visual quality cannot be fully automated. Spatial and technical mistakes often can.

---

# 15. Anti-Plastic Gate

A scene fails if major surfaces share the same generic glossy response.

Review:
- wall roughness;
- painted metal;
- structural metal;
- rubber;
- vinyl/fabric;
- glass;
- floor;
- foliage;
- screens;
- paper;
- emissive areas.

Do not fix plastic appearance by covering everything in realistic scratches.

Fix:
- shape;
- broad value;
- roughness differentiation;
- light direction;
- selective bevel/faceting;
- restrained surface variation;
- material-specific response.

---

# 16. Anti-Blockout Gate

A scene fails if the final environment still reads as default primitives.

Check:
- doors have depth, framing and sealing logic;
- walls have deliberate rhythm;
- ceilings have designed structure;
- furniture has recognizable authored silhouettes;
- hero machines are not boxes/cylinders with screens attached;
- plants are not generic low-poly blobs;
- props have intentional proportions;
- modularity does not create obvious copy-paste repetition.

Low-poly is not the same as low-effort.

---

# 17. Dressing Discipline

Use a hierarchy:

1. architecture / route
2. hero function
3. secondary composition
4. narrative dressing
5. micro accents

Do not solve emptiness by adding dozens of unrelated props.

Do not solve “detail” by adding texture noise.

Every prop cluster should support:
- function;
- story;
- composition;
- human presence;
- route guidance;
- scale.

Negative space is an authored asset.

---

# 18. Cold-Start Validation

Before final acceptance:

1. save all source and state;
2. close the active Blender process;
3. start a fresh Blender process;
4. open or rebuild the authoritative source;
5. verify all dependencies resolve;
6. verify materials/textures load;
7. verify named cameras exist;
8. rerun objective checks;
9. rerender the mandatory final cameras;
10. compare final cold-start renders with the approved previous renders;
11. verify no material or dependency regression;
12. update TASK_STATE.md with PASS/FAIL.

A room that only works inside one long-lived Blender session is not production-ready.

---

# 19. Blender Source Expectations

The authoritative .blend must remain editable.

Requirements:
- meaningful object/collection names;
- clean major collections;
- separate interactive/animated components;
- sensible transforms;
- sensible origins/pivots;
- reusable materials;
- procedural systems documented;
- no accidental dependency on temporary absolute paths;
- no hidden junk required for the render;
- scripts retained when they are part of reproducibility.

Prefer broad reusable systems over thousands of bespoke one-off objects.

---

# 20. Runtime Handoff

Blender owns visual source authoring.

The game engine owns:
- runtime collision;
- interaction;
- networking;
- gameplay state;
- final runtime lighting decisions where engine-specific;
- animation state;
- audio triggers;
- optimization;
- build validation.

Do not contort Blender into the game engine.

When engine integration resumes, use MCP where useful to import and validate, but preserve the headless Blender source pipeline.

---

# 21. Final Evidence Package

A completed room must include:

- authoritative .blend;
- build/rebuild scripts where applicable;
- TASK_STATE.md;
- final RUBRIC.md with scores;
- CAMERAS.md;
- CHECKLIST.md;
- fixed-camera final renders;
- latest review renders or a curated audit trail;
- defect/fix summary;
- support-contact validation PASS report;
- cold-start PASS;
- asset/dependency notes;
- confirmation of runtime handoff readiness.

The proof is part of the deliverable.


# Art-direction validation gate

Before a section may move from blockout into full production, the builder must prove one polished **style-validation slice** from gameplay camera height.

Minimum slice:
- one believable wall/architectural transition;
- one door;
- one primary prop cluster;
- one practical light;
- one utility element;
- 3–5 human storytelling props.

The slice must demonstrate:
- believable scale and construction;
- object-specific geometry rather than repeated bevelled boxes;
- distinct painted metal / plastic / rubber / fabric / concrete responses;
- localized wear;
- controlled colour blocking;
- localized lighting and contact shadow;
- restrained signage;
- negative space;
- no toy-like PPE;
- no generic sci-fi greeble language.

**Expansion is blocked until this slice passes.** A technically valid Blender build is not permission to propagate a failed visual language across an entire room.

## Visual veto checks

A review is an automatic visual FAIL if the dominant read is any of:
- generic low-poly;
- Three.js/web-demo;
- uniform satin plastic;
- flat even lighting;
- repeated box + bevel construction;
- excessive labels/screens;
- random decorative clutter;
- toy/mannequin hazmat suits;
- AAA photoreal texture noise.

The pixel-review loop must compare against [ART_DIRECTION.md](ART_DIRECTION.md) and [ART_REFERENCE_INDEX.md](ART_REFERENCE_INDEX.md), not merely against the previous render.
