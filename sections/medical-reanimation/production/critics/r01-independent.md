# Independent critic — OCRU R01

Reviewer: independent Grok subagent. Scope: rendered pixels from the ten fixed cameras plus the written section spec (`scenery/architecture.md`, `scenery/interface.json`, `prompt/ocru-build-brief.md`, GAME_SPEC §5 procedure). Approved plates used as material/lighting/layout-language principles only, not as layouts to copy.

No geometry was invented. No coordinate recipes, replacement meshes, or placement instructions are offered. Defects are described as visual or functional failures.

**Automatic visual FAIL is triggered.** The dominant read across the readable cameras is generic low-poly / Three.js: uniform satin plastic, flat even fluorescent lighting, and repeated box-plus-strip construction. That veto fires before any category can approach 90.

| Category | Score /100 |
|---|---:|
| Scale / circulation | 37 |
| Shape / art direction | 13 |
| Hierarchy | 15 |
| Materials | 17 |
| Lighting | 20 |
| Color | 26 |
| Environmental storytelling | 18 |
| Technical correctness | 23 |

**Overall mean: 21.1**

**Gate (every category ≥ 90): FAIL**

Builder `validation_report.json` records `status: PASS`, a berth span note, 26 supports, and 598 meshes. That is a builder claim, not visual proof. CAM_HERO and CAM_PINCH contradict a readable adult berth. Support-contact and cold-reopen are not demonstrated in this pixel packet and are not converted into invented passes.

---

## 1. Scale / circulation — 37

CAM_REVERSE and CAM_ROUTE show a hall whose door, dado, ceiling fixtures, stool, and recovery gurney roughly imply adult occupation, and the central floor field is empty enough to walk. That is the only real credit in this category.

Circulation as a *process room* does not read. CAM_ENTRY is a black frame with a hairline vertical slit; the designated arrival camera does not show a threshold, cart lane, or interior. No body cart is visible in the west parking bay in CAM_REVERSE or CAM_ROUTE — the wheeled table in CAM_REVERSE sits on the east supply side and reads as a worktop, not a retrieval cart. The OCRU presents no loading mouth, so the west machine-face route cannot be judged as a place where a ragdoll or cart is committed to a chamber. CAM_DECON is a shallow empty stall; a suited adult workflow is not credible from that enclosure.

## 2. Shape / art direction — 13

Severe failure. CAM_HERO is a labelled white fascia around a blank dark rectangle. CAM_PINCH is the same rectangle filling the frame. Spec requires the OCRU frame, berth, opening, seals, service coupling, cartridge receiver, restart controls, and maintenance panels to read as different constructed parts; the pixels show a shuttered slab, a rail, an orange brick, and a few rivets.

Secondary hardware is primitive CSG. CAM_CONSOLE is a blank board with a yellow cube, a peach puck, a red cylinder, nine grey cubes, and three silver pegs. CAM_DECON is a pipe, a disc, and a yellow cube. CAM_RECOVERY is a grey slab on a white box with stick legs. Doors, cabinets, ceiling ribs, and wall plaques are bevelled boxes. Compared with the Valorant plates (constructed housings, gauges, rails, weight) and the med-bay plates (open cyan chamber, berth, chunky console, cartridge rack), this is a generic low-poly kitbash, not grounded stylized semi-realism.

## 3. Hierarchy — 15

The hero landmark is a dead field. CAM_HERO and CAM_PINCH give the eye nothing inside the largest mass. CAM_ROUTE lets that black wall occupy the left third while the remaining station cluster is tiny, same-value, and equally quiet, so the rear console, decon opening, and recovery gurney do not step down as a readable interaction sequence.

Cyan, which should be the OCRU-interior and diagnostic landmark, is absent from the machine and the screens. It instead leaks from the entry-door slits in CAM_REVERSE, pulling focus to the wrong wall. CAM_ENTRY and CAM_PINCH contribute no hierarchy at all. CAM_MAINT is mostly a blank door leaf; the three-lamp panel is a footnote. The floor stencil in CAM_ROUTE/CAM_REVERSE becomes a competing graphic because the chamber has no interior light or constructed mouth.

## 4. Materials — 17

One satin response covers painted equipment, walls, furniture, and floor. CAM_MATERIALS, the materials camera, shows a dark cabinet, backwards emissive type, and a glass pane with concentric ring artifacts — not tactile painted metal, concrete, rubber, glass, or fabric.

CAM_DECON and the glass edge in CAM_CONSOLE repeat the same Newton-ring / fingerprint glass. The recovery “towel” in CAM_RECOVERY is two stacked white boxes; there is no cloth. The orange OCRU pad in CAM_HERO does not read as rubber. Floor tiles in CAM_REVERSE/CAM_ROUTE are flat value fields. The two-tone dado is the only paint break. Spec forbids uniform satin plastic as a dominant read; that is the dominant read.

## 5. Lighting — 20

CAM_REVERSE and CAM_ROUTE are washed by even ceiling rectangles. Falloff is weak, contacts are thin, and there is no practical pool structure of the kind in the Valorant plates or the warm directional med-bay plates.

CAM_ENTRY is unlit except for the slit. CAM_PINCH is a brown-black void. CAM_HERO lights the white fascia and leaves the chamber as a dead plane — no interior volume, no glass thickness, no cyan emission. CAM_CONSOLE screens do not emit. CAM_MATERIALS is a muddy brown close-up. Door-slit cyan in CAM_REVERSE is the only small emissive accent, and it is in the wrong place. Flat even lighting is an automatic-fail condition and it is the room’s lighting language.

## 6. Color — 26

Restrained grey/bone masses and yellow hazard tape on the OCRU jambs, door frame, and gurney end (CAM_HERO, CAM_REVERSE, CAM_RECOVERY) are the only disciplined notes. Yellow as hazard language is otherwise sparse and correct on those stripes.

The shell is a cream office, which the spec explicitly rejects (“not cream rooms”). Cyan is missing from the OCRU interior and from diagnostic screens, and is illegally present in the CAM_REVERSE door slits. CAM_CONSOLE introduces candy yellow, peach, and red primitives that are not hazard language and that make the restart deck read as toys. Without a cyan chamber landmark, the room has no departmental colour hierarchy — only beige, grey, and a black hole.

## 7. Environmental storytelling — 18

Required procedure (retrieve → decontaminate → load → suit service → power → cartridge → physical restart → monitored cycle → recovery) is not readable in pixels.

- Arrival: CAM_ENTRY dead; no body cart in the parking bay.
- Decon: an empty stall with a stick shower; no wet floor, grate, or waste vessel; wall copy reversed (CAM_DECON).
- Chamber / suit-service: sealed dark rectangle; no berth, no hoses (CAM_HERO, CAM_PINCH).
- Cartridge insertion: no four-row insertion cabinet in CAM_ROUTE or CAM_CONSOLE.
- Restart and monitoring: toy solids and a blank slab (CAM_CONSOLE).
- Power: three lamps and a cabinet labelled backwards (CAM_MAINT, CAM_MATERIALS).
- Consumables: a white box-cabinet and a bare east bench (CAM_ROUTE, CAM_REVERSE).
- Maintenance: CAM_MAINT is a door jamb, not an OCRU service hatch.
- Recovery: a morgue-like slab with a boxed pillow and a fake towel (CAM_RECOVERY), against the brief’s “not a hospital or morgue.”

Some original copy exists (OCRU / T-01, CLEAN SAFE ACCESS ONLY, CAUTION KEEP CLEAR AUTOMATED SYSTEM, OCC HEALTH). Much of it is mirrored or too small. LIFE REBUILDS VALUE, FIT PEOPLE / SAFER SITES, and a triangle facility mark do not read. The comic-bureaucratic tone is a few decals on an unused showroom.

## 8. Technical correctness — 23

Pixel-visible construction errors are systematic.

CAM_ENTRY does not image the room; closed leaves plus an exterior camera produce a black evaluation plate. CAM_PINCH is an unusable near-black field. Labels are mirrored on multiple assets: OCC HEALTH (CAM_RECOVERY), RESERVE (CAM_MATERIALS), MAINS / RESERVE / ISOLATE (CAM_MAINT), RINSE / SANITIZE / RETURN TO WORK (CAM_DECON). Glass carries concentric shader rings (CAM_MATERIALS, CAM_DECON). The hero opening reads as an opaque plane, not a chamber with glass thickness or interior parts.

No exploding mesh is obvious in the eight partly readable frames, and gurney/stool feet appear to meet the floor. That is not enough. Support-contact and cold-reopen evidence required by the rubric are not in this packet. The builder validation PASS, including the berth-span note, is contradicted by CAM_HERO/CAM_PINCH and cannot raise this score.

---

## Camera notes (observational)

- **CAM_ENTRY:** Black field, thin bright slit. Arrival, doors, and interior are not judgeable.
- **CAM_HERO:** OCRU T-01 fascia, hazard stripes, rail, orange pad, one green lamp. Chamber is a blank dark rectangle.
- **CAM_REVERSE:** Empty beige hall, grey double doors with cyan slits, floor stencil, east bench/stool, west black slab. Cart parking empty.
- **CAM_ROUTE:** Process wall as a row of underscaled boxes. Cartridge bank not identifiable. OCRU still a black wall.
- **CAM_CONSOLE:** Blank monitor slab; restart/monitoring reads as kindergarten solids. No diagnostic image.
- **CAM_DECON:** Empty stall, stick shower, reversed copy, artifacted glass, no waste/wet language.
- **CAM_RECOVERY:** Adult-length slab, boxed linen, reversed OCC HEALTH, morgue read.
- **CAM_PINCH:** Dark rectangle, rivets, rail corner. No chamber, glass, or hookup.
- **CAM_MATERIALS:** Dark cabinet, backwards RESERVE, ringed glass. Fails as a materials proof.
- **CAM_MAINT:** Door leaf, three-lamp panel with mirrored captions. No OCRU maintenance interior.

---

## Top 5 highest-impact defects

1. **The hero OCRU reads as a blank dark rectangle.** No human-sized chamber, berth, constructed access, glass volume, or suit-service hookup. Kills shape, hierarchy, lighting, and the entire recommissioning procedure (CAM_HERO, CAM_PINCH, CAM_ROUTE, CAM_REVERSE).
2. **Generic low-poly / Three.js language is the room.** Uniform satin plastic, flat fluorescent wash, repeated boxes. Automatic visual FAIL against Valorant-influenced grounded semi-realism and against both approved plate families.
3. **CAM_ENTRY is a black frame.** Body/cart arrival is not imaged by the camera named for it.
4. **Restart, monitoring, and cartridge insertion do not exist as readable functions.** CAM_CONSOLE is a blank slab plus toy primitives; no four-row cartridge cabinet appears in any plate.
5. **Decals and glass are technically broken, and several process props are simply absent.** Mirrored type on recovery, reserve, power, and decon; concentric glass rings; no retrieval cart, no hoses, no waste vessel, no fabric, no OCRU maintenance hatch.

---

## Decision

**FAIL.** Mean 21.1. Every category is independently far below 90. Automatic style veto applies. This is not an industrial employee recovery room in pixels; it is an empty cream hall facing a dark rectangle.
