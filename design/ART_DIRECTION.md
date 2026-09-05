# Critical Shift Art Direction

**Status:** canonical visual authority  
**Applies to:** every character, room, prop, material, light, VFX element, concept, render and generated asset  
**Reference index:** [ART_REFERENCE_INDEX.md](ART_REFERENCE_INDEX.md)

> [!IMPORTANT]
> **Critical Shift uses grounded stylized semi-realism.**  
> Primary influence: **Valorant-style environmental art principles** — believable proportions, simplified but specific geometry, controlled material response, strong colour blocking, clear silhouettes and disciplined detail.  
> Secondary influence: **PEAK-style readability and restraint** — strong silhouettes, simple compositions, low visual noise and immediate gameplay legibility.  
> These are principle references only. Do not copy protected assets, layouts, characters, textures, branding, props or distinctive designs from either game.

This document supersedes every older instruction that describes Critical Shift as PEAK-led low-poly, deliberately faceted, toy-like, texture-light in the sense of flat untextured colour, or compact/chibi. It also supersedes any instruction that pushes the game toward modern AAA photorealism.

---

# 1. Visual thesis

Critical Shift should feel like:

> **A believable industrial facility that has been simplified and art-directed for a stylized PC game.**

The world should be grounded enough that a worker, locker, door, bench, respirator, pressure vessel, reactor console or maintenance cart reads as a plausible object with plausible scale and construction.

The stylization comes from:
- controlled simplification;
- strong silhouettes;
- deliberate proportions;
- broad colour/value grouping;
- simplified material response;
- restrained surface noise;
- selective wear;
- composition;
- lighting;
- gameplay readability.

The stylization must **not** come from turning every object into a bevelled box.

## 1.1 Required qualities

Every finished area should feel:
- believable;
- tactile;
- stylized;
- readable;
- atmospheric;
- human;
- slightly worn;
- purposeful;
- professionally art-directed.

## 1.2 Explicit non-targets

Critical Shift is **not**:
- modern AAA photorealism;
- a cinematic Unreal Engine tech demo;
- generic low-poly;
- toy-like;
- Roblox-like;
- mobile-game low fidelity;
- Fortnite-like exaggeration;
- a Three.js-looking web demo;
- a glossy sci-fi asset pack;
- a random kitbash of industrial parts;
- sterile procedural geometry;
- a grunge-covered abandoned bunker.

---

# 2. Reference hierarchy

## 2.1 Primary: Valorant environmental principles

Use high-level principles associated with readable stylized semi-realistic environment art:
- real-world-inspired architecture;
- believable human scale;
- clean silhouettes;
- simplified but specific shapes;
- controlled material families;
- broad colour blocking;
- restrained texture frequency;
- selective high-frequency detail;
- strong lighting hierarchy;
- readability from gameplay distance.

Do not imitate specific maps, architecture, textures, props, symbols or branding.

## 2.2 Secondary: PEAK readability principles

Borrow only the useful high-level lessons:
- clarity at a glance;
- strong silhouettes;
- restrained clutter;
- large readable visual masses;
- negative space;
- composition over microdetail;
- interaction readability.

Do **not** use PEAK as the rendering target. Critical Shift should no longer read as cartoon low-poly.

## 2.3 Real-world reference

Real industrial, institutional and nuclear workplaces are the functional reference for:
- scale;
- construction logic;
- PPE;
- maintenance;
- doors;
- furniture;
- piping;
- wall systems;
- electrical cabinets;
- consoles;
- safety hardware;
- signage logic;
- wear patterns.

Real-world reference informs **what objects are and how they are built**. The final rendering remains simplified and art-directed.

---

# 3. Shape language

## 3.1 Primary rule

**Shape first. Detail last.**

Every important asset should be designed in three levels:

1. **Primary form** — the overall silhouette and mass.
2. **Secondary form** — functional construction: panels, frame, hinges, recesses, supports, doors, handles.
3. **Tertiary detail** — labels, screws, scratches, decals, small wear, seams.

If an asset looks boring in flat grey with no textures, redesign it before adding detail.

## 3.2 Geometry target

Use medium-complexity game geometry:
- simplified, not primitive;
- clean, not sterile;
- readable, not faceted for its own sake;
- specific to the object, not generated from a universal cube language.

Cubes, cylinders and planes are valid starting primitives. They are not automatically finished assets.

## 3.3 Bevel rule

**Bevels are finishing tools, not design tools.**

Forbidden failure mode:
- box;
- uniform bevel;
- solid colour;
- another box;
- same bevel;
- call it finished.

Use edge treatment according to construction:
- folded sheet metal;
- cast metal;
- molded plastic;
- rubber;
- concrete;
- timber;
- fabric;
- painted steel.

Avoid identical bevel widths across unrelated assets.

## 3.4 Silhouette test

At gameplay distance:
- doors must still read as doors;
- suit bays as suit bays;
- benches as benches;
- valves as valves;
- tools as tools;
- machine states as distinct.

If tertiary detail is required to identify an object, the primary/secondary forms are too weak.

---

# 4. Scale and proportions

Use believable human scale throughout.

Do not rely on cartoon inflation to create stylization.

Avoid:
- giant handles without functional reason;
- enormous buttons on every device;
- paper-thin walls;
- toy-sized furniture;
- oversized scanner booths;
- arbitrary thickening of all structures;
- tiny doors or strangely short ceilings.

Stylization should come from shape refinement and simplification, not broken scale.

---

# 5. Architecture

Architecture should feel built by people for work.

Use:
- believable wall thickness;
- sensible door frames and reveals;
- functional floor transitions;
- service access;
- structural variation;
- utility routing that enters and leaves somewhere plausible;
- ceiling systems with lights, vents and selected infrastructure;
- readable base trims, wall protection or lower-wall zones where appropriate.

Do not make every room:
- the same rectangular box;
- the same wall stripe;
- the same ceiling panel;
- the same rectangular doorway;
- the same row of props.

## 5.1 Architectural detail density

Large surfaces need breathing room.

A good composition may be:
- quiet wall;
- quiet wall;
- dense locker/bench cluster;
- open movement area;
- equipment focal point;
- door.

Do not decorate every square metre.

---

# 6. Materials and textures

Materials must be **stylized but believable**.

The player should be able to distinguish painted metal, bare metal, concrete, plastic, rubber, glass, fabric and flooring without reading labels.

## 6.1 Material families

### Painted metal
- matte to semi-matte;
- low-frequency roughness variation;
- localized scratches;
- restrained edge wear;
- occasional dents;
- grime only where use explains it.

### Bare metal
- controlled specular response;
- not mirror chrome;
- broad roughness breakup;
- use sparingly.

### Plastic
- molded character;
- distinct from painted metal;
- restrained gloss;
- slight surface variation;
- never default shiny toy plastic.

### Rubber
- dark;
- matte;
- soft visual response;
- subtle texture;
- used on boots, grips, seals, floor mats and bumpers.

### Fabric
- broad folds;
- matte;
- visible thickness;
- simplified weave or no visible weave at normal gameplay distance;
- should read as clothing, not polygon armour.

### Concrete / plaster
- broad tonal variation;
- subtle staining;
- low-frequency texture;
- occasional patching;
- no noisy scan detail.

### Flooring
- believable institutional/industrial system;
- slightly different roughness from walls;
- localized route wear;
- occasional replacement panel/tile;
- no wet-plastic reflections unless actually wet.

## 6.2 Texture frequency

Prefer:
- broad colour variation;
- low-frequency roughness;
- localized wear;
- sparse decals;
- selective small detail at focal points.

Avoid:
- 4K/8K uniqueness everywhere;
- photographic grunge;
- procedural scratch noise on every asset;
- dense normal maps;
- edge wear on every exposed edge;
- uniform material response.

---

# 7. Colour

Colour is functional.

Base environment:
- warm off-white / institutional grey;
- desaturated industrial green or teal;
- steel grey;
- charcoal;
- muted concrete.

Accents:
- hazard yellow;
- maintenance orange;
- emergency red;
- limited utility blue/cyan;
- department-specific identifiers.

Rules:
- most surfaces remain restrained;
- saturation is reserved for useful information;
- interactables and hazards must stand out without turning the whole room into colour confetti;
- colour is never the only gameplay signal.

---

# 8. Lighting

Lighting is a core art-direction system, not a final polish layer.

Avoid flat interior exposure where every surface is equally bright.

Use:
- localized practical lights;
- clear key-light zones;
- darker secondary spaces;
- soft indirect fill;
- strong contact shadow;
- visible light falloff;
- controlled warm/cool contrast;
- subtle atmospheric depth;
- selective emissive cues.

Every ceiling light should visibly influence nearby surfaces.

Objects must feel grounded through:
- contact shadow;
- AO;
- believable placement;
- support contact;
- local light response.

Do not hide poor modeling in darkness. Gameplay readability wins.

---

# 9. Wear and imperfection

The facility is active and maintained.

Use restrained evidence of use:
- worn handles;
- scuffed floor routes;
- chipped paint in plausible contact areas;
- repaired pipe wrap;
- taped label;
- dented bin;
- slightly mismatched replacement panel;
- cable sag;
- crooked paperwork;
- chair slightly out of alignment;
- boots left under a bench;
- glove left behind;
- used clipboard;
- mug;
- maintenance kit.

Avoid:
- blanket grime;
- uniform edge damage;
- abandoned-building decay;
- random debris;
- procedural dirt everywhere.

Imperfection should look authored.

---

# 10. Environmental storytelling

The core rule is:

> **People work here.**

Tell that story through objects and placement, not walls of text.

Good examples:
- open locker;
- folded protective clothing;
- spare respirator filters;
- maintenance tape;
- gloves;
- boots;
- battered mug;
- clipboard;
- replacement component;
- tool left near a repair;
- shift paperwork;
- one personal item;
- localized cleaning equipment.

Every prop should have a plausible reason to exist.

Random clutter is not storytelling.

---

# 11. Signage and text

Use signage sparingly.

A sign should:
- serve navigation;
- identify a hazard;
- explain an interaction;
- communicate procedure;
- support institutional character.

Do not use signage to compensate for weak environment design.

Avoid:
- a label on every wall;
- title panels for obvious objects;
- multiple warnings saying the same thing;
- decorative fake UI;
- screens that exist only to create visual noise.

The environment should be understandable before reading text.

---

# 12. Technology and sci-fi restraint

Critical Shift is industrial first.

Technology should feel:
- manufactured;
- maintained;
- practical;
- specialized;
- slightly dated in places;
- physically operated.

Use:
- analogue gauges;
- guarded switches;
- industrial displays;
- CRT-like equipment where appropriate;
- early flat-panel displays;
- physical controls;
- believable housings.

Avoid:
- holograms;
- decorative glowing lines;
- meaningless screens;
- futuristic hexagon motifs;
- dense greebling;
- random vents;
- decorative pipe spaghetti;
- spaceship corridor language.

---

# 13. Character direction

Workers are stylized adult humans with **believable adult proportions**.

Do not target compact/chibi 5.5-head characters.

Target:
- approximately believable adult proportions;
- slightly simplified anatomy;
- readable hands and boots without cartoon inflation;
- clear silhouettes;
- slightly simplified faces;
- restrained skin/hair detail;
- clothing and PPE doing most of the character design.

The character should look like a person from a stylized semi-realistic PC game, not a polygon mascot.

---

# 14. Hazmat and PPE direction

The hero hazmat suit must read as **protective clothing**.

Required:
- believable fabric volume;
- broad folds;
- recognisable seams;
- closure logic;
- visor thickness;
- glove construction;
- boot construction;
- harness/pack integration;
- functional hoses only where needed;
- dosimeter/status device;
- readable rescue handle;
- modular department/player identifiers.

Avoid:
- armour-like polygon plates;
- inflated toy proportions;
- faceted mannequin bodies;
- oversized helmet cubes;
- random hard-surface greebles;
- glossy plastic suit material.

The suit may be simplified, but it must look wearable.

---

# 15. Department direction

## 15.1 Spawn / preparation

Feeling:
- institutional;
- safe but slightly oppressive;
- used daily;
- human;
- practical;
- clean enough to work in;
- visibly connected to a larger facility.

Use:
- lockers;
- PPE;
- benches;
- paperwork;
- doors with believable frames;
- modest maintenance evidence;
- restrained safety signage;
- material variation;
- localized fluorescent lighting;
- quiet areas between prop clusters.

Avoid:
- showroom cleanliness;
- random potted plants as filler;
- wall gadgets every metre;
- giant scanners dominating the room;
- toy suits in display alcoves.

## 15.2 Mine

Feeling:
- rough working environment;
- heavy structure;
- moisture;
- dirt;
- constrained work lighting.

Use simplified real mining vocabulary, not low-poly rock cartoons.

## 15.3 Refinery

Feeling:
- kinetic;
- hot;
- mechanical;
- process-driven.

Use clear process equipment and readable material flow without industrial pipe spaghetti.

## 15.4 Reactor and power plant

Feeling:
- maintained;
- monumental;
- controlled;
- technical;
- slightly dated industrial science fiction.

Hero:
- cyan reactor pool;
- exactly two dominant control-bank assemblies;
- believable 1990s/early-digital control language;
- restrained perimeter equipment;
- readable circulation.

The reactor is the cleanest department, but still uses believable materials, subtle wear and grounded construction.

---

# 16. Detail density

Detail must be clustered.

Use three density levels:

### Quiet
Large surfaces, simple structural rhythm, minimal props.

### Working
Furniture, one utility route, a few signs, functional equipment.

### Focal
Hero machine, interaction point, character station or important repair area.

Never make the entire room focal-density.

---

# 17. Gameplay camera rule

All art decisions are judged from the actual gameplay camera.

Every major pass must render:
- entry;
- primary route;
- hero interaction;
- reverse view;
- circulation pinch point;
- material/lighting problem area.

Check:
- scale;
- silhouettes;
- prop contact;
- clipping;
- floating objects;
- lighting;
- material readability;
- detail visibility;
- route clarity.

A prop that looks good only in Blender's free camera has failed.

---

# 18. Validation slice rule

**Do not build a full room before proving the style.**

For each new section, first build one polished validation slice containing roughly:
- one wall section;
- one door;
- one main prop cluster;
- one light;
- one utility element;
- 3–5 storytelling props.

The slice must prove:
- geometry language;
- proportions;
- materials;
- lighting;
- wear;
- colour;
- prop style;
- detail density;
- gameplay-camera readability.

Expansion is blocked until the slice passes visual review.

---

# 19. Hard visual vetoes

A review can fail the scene immediately if any of these dominate:

- obvious generic low-poly look;
- repeated bevelled-box construction;
- plastic materials across most assets;
- primitive sci-fi control panels;
- excessive signage;
- flat even lighting;
- toy-like PPE;
- random decorative clutter;
- procedural cleanliness;
- photoreal texture noise inconsistent with the style;
- modern AAA fidelity arms race;
- generic web-demo presentation;
- floating or unsupported props;
- unreadable silhouettes.

---

# 20. Pass / fail questions

Before approving any art pass, ask:

1. Does this look like a believable place?
2. Does it look stylized without looking cheap?
3. Are important shapes specific rather than primitive?
4. Are materials clearly distinguishable?
5. Is wear localized and plausible?
6. Does lighting create depth?
7. Is there negative space?
8. Does the room feel used by people?
9. Is signage restrained?
10. Are props grounded and supported?
11. Does the scene avoid generic sci-fi?
12. Does it avoid generic low-poly?
13. Does it avoid modern AAA photorealism?
14. Would a screenshot plausibly look like a commercially released stylized PC game?

If the answer to 14 is no, the art pass is not complete.

---

# 21. Production mantra

**Believable first. Stylized second. Readable always.**

Do not confuse simplicity with cheapness.

A simple object still needs:
- good proportions;
- construction logic;
- material identity;
- silhouette;
- placement;
- lighting;
- purpose.
