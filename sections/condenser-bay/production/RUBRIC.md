# Turbine Condenser Bay — independent critic rubric

**Authority:** independent grok-4.6 critic subagent (see `production/critics/REVIEWER_IDENTITY.md`)  
**Status:** binding for all condenser-bay reviews  
**Pass rule:** every category independently **> 90 / 100**. Any category **≤ 90 is REJECT**. Unverified categories **cannot pass**.

This rubric is for the **underfloor Turbine Condenser Bay only**. Turbine R07 and Cooling Plant R10 local acceptances do not transfer.

---

## 0. Hard gates (any one is immediate REJECT)

1. Missing required evidence set (section 2). Unscored is not a pass.
2. Any of the ten categories ≤ 90, or any category left unverified.
3. Generic low-poly / universal bevelled-box language dominating assets.
4. Plastic / default-PBR / toy gloss across most surfaces.
5. Teal / turquoise / cyan decoration or lighting theme.
6. Condenser silhouette interchangeable with Cooling Plant HX-01 or a row of tanks.
7. Disconnected pipes, floating fittings, unsupported structure, or services that vanish into uncut walls.
8. Inaccessible controls, blocked routes, stairs/doors terminating against solid uncut geometry.
9. Player views that hide defects by disabling walls; unlabelled cutaways used as “complete room” proof.
10. Builder-preferred scores, concept sheets, or viewport claims offered instead of inspected pixels.
11. Relabelled identical images presented as a new correction cycle.
12. Silent edits to turbine-owned U02 cap/structure, or new openings cut in a neighbor without documented owner coordination.
13. Claimed facility cooling loop or reciprocal neighbor bind that the local sockets do not prove.
14. Cold-open failure, missing fonts/text, missing materials, or visual mismatch beyond honest render variance without disclosure.

---

## 1. Scoring law

| Rule | Enforcement |
|---|---|
| Ten independent categories, each /100 | No averaging, no “overall 91” rescue |
| Pass floor | **91 minimum** per category |
| 90 | **REJECT** |
| Unseen / unmeasured | Category fails; write `UNVERIFIED — cannot pass` |
| Time pressure | Irrelevant. Do not inflate. |
| Fix verification | **New images required** for every claimed fix |
| Defect order | Three most consequential first, then minute |
| Review set | Entire final set **and** cold-open set, not only the repaired crop |
| Prescription | Describe the problem. Do not dictate coordinates or replacement meshes. |

**Defect line (mandatory):** image name · visible location · severity (blocker / major / minute) · observed mismatch · practical/art consequence.

**Severity:**

- **Blocker:** contract miss, blocked access, disconnected process, hard visual veto, missing evidence for a scored claim.
- **Major:** readable but wrong construction, weak silhouette, material/lighting failure, incomplete wall/roof/machine face in supplied views.
- **Minute:** small contact, label crop, localized wear miss, one weak tertiary detail that does not collapse the category — still recorded; clustered minutes can drop a category to 90.

Approximate independent calibration (not a substitute for pixel judgment):

- **≤ 70:** greybox, missing hero machine, or wrong room.
- **71–85:** identifiable industrial room with generic assets, plastic materials, or broken process.
- **86–90:** close, but a hard-gate miss, unverified face, or Valorant-fidelity shortfall remains. **Still REJECT.**
- **91–93:** complete, specific, and evidenced, with only disclosed residual limits.
- **94–96:** neighbor-continuity quality with distinctive condenser construction.
- **97–100:** reserved for evidence that survives hostile close-cropping and cold reopen with almost no residual notes. Do not award because the builder asked.

---

## 2. Mandatory evidence (coverage cannot pass without these)

### 2.1 Documents

- Dimensioned floorplan reconciled to **saved** geometry (plan drawing alone is not proof).
- Measured `interface.json` with explicit transform relative to turbine origin.
- Equipment / contract checklist mapping every required system to named objects.
- Access / maintenance envelopes and intended interaction hooks.
- Explicit remaining integration list (U02 cap action, cooling remote ends, turbine slab mating, engine work).

### 2.2 Image set (actual scene renders, 1920×1080 review target)

At least these ten named views, plus player-height coverage:

| ID intent | Must prove |
|---|---|
| Entry | Receiving access, threshold, first readable volume, no wall-behind-door |
| Hero | Distinctive condenser assembly as the primary silhouette |
| Reverse | Opposite wall, return path, machine rear/side not hidden by hero camera |
| Exhaust connection | Plausible receive of turbine `U04` 2.5×1.5 m downhood; neck, flange, seal, support |
| Return equipment | Condensate collection/hotwell/pumps/controls; service points reachable |
| Cooling connections | Supply and return routed, isolated, supported; terminations deliberate |
| Operator station | Original IDs, readable controls, human-scale reach |
| Maintenance access | Platforms, lifting/removal provision, clearance around important parts |
| Roof / services | Ceiling structure, lighting fixtures, vents, overhead routing, no cardboard lid |
| Material-detail | Painted steel vs cast vs concrete vs rubber vs glass vs fabric at close range |

Also required:

- Player-height corners/turns so **every wall and awkward space** is visible.
- Full-resolution close crops of: exhaust flange, condensate controls, cooling isolators, operator labels, glass edges, floor/support contacts, door/access reveals.
- Cutaways **labelled as cutaways**. Player cameras must not cheat by hiding walls.
- Cold-reopen set of the same cameras with honest comparison (hashes, pixel delta, visual read).

A screenshot cannot prove:

- numerical clearances, cart/handler swept volume, or headroom millimetres;
- the unseen side of a machine, the far wall, the roof if not in frame, or underfloor voids;
- a neighbor bind, remote pipe destination, or turbine-owned cap removal.

Those require measured saved-geometry audits **and** views of the relevant faces. If either is missing, mark `UNVERIFIED`.

---

## 3. Contract facts the builder does not get to invent away

Read from turbine / cooling contracts and the 2026-09-11 assembly audit. Verify live saved neighbor geometry before treating numbers as current.

| Item | Recorded fact | Condenser-bay obligation |
|---|---|---|
| `U04` | `(4.6, 11.45, 0)`, outward −Z, **2.5 × 1.5 m** opening through hood/foundation/slab | Receive this exhaust. Do not restage the turbine hall. Do not cover the opening with a fake grate and call it a condenser. |
| `U02` | `(9.5, 0, 0.45)`, outward −Y, **0.2 m**, blind-terminated | Provide condensate return equipment and document the integration action. **Do not silently remove the turbine-owned cap.** |
| Turbine shell | 14 × 24 × 7.2 m clear; floor z 0; walls 0.25 m; foundation x 2.5..6.7, y 5.5..20 | Bay sits **below** this hall. Justify floor elevation, headroom, and footprint from equipment + circulation, not an arbitrary cavern. |
| Cooling Plant | Completed P-01, P-02, HX-01, workshop; SE reactor connection; **no direct turbine doorway** | Complete the **missing condenser system**. Do not duplicate the pump/exchanger room. A modeled local pipe ≠ facility loop. |
| CP secondary water | `CP-SECONDARY-WATER-01/02` at east wall, 0.2 m bore, proposed local sockets | May inform a **provisional** cooling-water story. Binding remains unproven until matched and accepted. |
| Ownership | Condenser bay owns `sections/condenser-bay/` only | No commandeering neighbor blends. No new neighbor openings without explicit owner coordination. |
| Game spec | No certified condenser ratings, MW, or pressure | Do not invent mandatory engineering numbers. Visual machinery ≠ certified plant. |

---

## 4. Category criteria

### 4.1 Contract / specification coverage

**Ask:** Does this module implement the assigned incomplete system, with named assets and documented boundaries?

Must be visible or explicitly evidenced:

1. Distinctive condenser assembly plausibly receiving `U04`.
2. Condensate collection and return with reachable controls and service points.
3. Cooling-water supply/return with routed pipes, isolation/access, supported fittings.
4. Maintenance access, lifting/removal provision, clearance around important parts.
5. Readable operator/service station with **original** equipment identification.
6. Drainage / limited collection / sump where justified, plus floor protection.
7. Complete walls, structural framing, roof/ceiling, floor, ventilation, practical fixtures.
8. Usable service-access arrangement and clearly defined module boundaries.
9. Restrained maintenance dressing, safety/direction labels, tools/storage, service documentation.
10. Every pipe connects, caps, or terminates deliberately. Every support lands.
11. Map of items → named objects, cameras, intended interaction hooks.
12. Honest leftover list: U02 integration, cooling remotes, turbine slab mate, engine work.

Automatic coverage fails:

- basement of boxes with a cylinder labelled “condenser”;
- copied Cooling Plant layout;
- missing roof, missing fourth wall, or “open void under turbine” with no room;
- claiming GAME_SPEC dimensions that do not exist;
- claiming neighbor assembly because a pipe aims at a wall.

### 4.2 Scale / layout

**Ask:** Would an adult worker believe they can stand, reach, and service this space? Is the volume earned by equipment?

Inspect:

- human-scale doors, rails, valves, platforms, benches, and headroom;
- floor elevation justified (exhaust neck length, condenser body, hotwell, human access);
- wall thickness and structural depth consistent with turbine 0.25 m / cooling 0.3 m language — not paper planes;
- equipment footprints that leave aisles rather than filling an arbitrary warehouse;
- no toy furniture, giant buttons, or miniature vessels;
- module bounds that do not occupy turbine interior volume or cooling-plant interior volume.

Unverified without: dimensioned plan **plus** player-height views in both long directions **plus** a section/cutaway labelled as such.

### 4.3 Machinery logic

**Ask:** Can a viewer follow exhaust steam → condense → collect → return, and cooling water in/out, without a caption?

Inspect process order:

- LP exhaust enters a recognisable condenser (shell, neck, tube-sheet/waterboxes or equivalent authored fiction), not a decorative tank;
- condensate leaves to collection/hotwell/pump/return toward the documented `U02` story;
- cooling water has distinct supply and return, isolators, and service access;
- pumps, if present, have motors, couplings/guards, bases, suction/discharge that are not clones of P-01/P-02 unless clearly a different duty and silhouette;
- orientation: shafts, flanges, and operator faces make sense;
- lifting points / removal lanes exist for the parts the story says are serviceable;
- no second reactor, no duplicate HX-01 pull-out bay used as a substitute condenser.

A local pipe into a capped wall is allowed only if labelled as a **provisional local socket**. Claiming a complete facility loop is a logic fail.

### 4.4 Circulation / readability

**Ask:** Can a player enter, reach every control, service the machine, and leave without clipping through props?

Inspect:

- receiving connection is a real opening with clear approach — no staircase into an uncut wall, no door with solid wall behind;
- keep-clear aisle(s) readable at player height;
- platforms and ladders land; rails do not block the only path;
- cart/tool movement at least plausibly reserved; drawn yellow lines are not proof of swept volume (`UNVERIFIED` if only a footprint exists);
- wayfinding sparse and diegetic; colour is not the only signal;
- labels readable in the views that claim them; cropped letters need a compensating view in the **same** review set.

Blocked route, unreachable handwheel, or maintenance platform you cannot step onto from the floor = blocker.

### 4.5 Construction / detail

**Ask:** Shape first, then functional secondary construction, then tertiary detail. Does grey-untextured mass still read as the object?

Inspect every visible:

- wall module, dado, corner, door/access reveal, header, threshold;
- roof girders/deck, hanger, light body, vent, cable tray;
- machine front **and** side: flanges, bolt rings, gaskets, saddles, feet, grout/pads, manways, gauges, nameplates;
- pipe shoes, anchors, guides, spring cans or equivalent supports that **touch structure**;
- glass: thickness, frame, edge; no infinitely thin panes;
- no clipping, hovering decals, z-fighting, or boolean leftovers in player views.

**Reference-detail count rule:** if a selected/approved view shows N purposeful conduits, fasteners, or fittings, identify and author those N. A generic cube row is a miss. Do not reproduce generator mistakes or unsafe blocked arrangements merely because an image-edit hallucinated them.

Neighbor bar (inspected 2026-09-11): turbine coupling guard, pedestal feet, split-case bands, cooling pump bolt rings and yellow cages, exchanger saddle/bolt-ring language. Condenser-bay construction must meet that **density of intent**, with different primary forms.

### 4.6 Materials

**Ask:** Can painted steel, cast metal, concrete, rubber, fabric, and glass be told apart without labels?

Must:

- matte-to-semi-matte painted metal; controlled bare metal, not mirror chrome;
- concrete/plaster with low-frequency variation, not scan-grunge;
- rubber on grips, seals, mats, bumpers;
- glass with edge and slightly different spec than wet plastic;
- wear only at contact/use: handles, kick, floor routes, wrench flats — not procedural mottling everywhere;
- no universal glossy plastic; no identical roughness on concrete and enamel.

Material-detail view is mandatory. Hero beauty lighting cannot hide a plastic shader.

### 4.7 Lighting

**Ask:** Do practicals create hierarchy, contact shadow, and readable falloff without hiding modeling in darkness?

Must:

- localized practical lights that actually light nearby surfaces;
- key zones vs darker secondary space;
- grounded contact shadow / AO at feet, saddles, pipe shoes;
- no flat equal exposure; no cinematic god-ray demo; no cyan/teal practicals;
- labels and gauges readable, not blown out;
- ceiling lights exist as objects **and** as illumination.

Gameplay readability wins. Unlit corners that conceal missing walls fail both lighting and construction.

### 4.8 Palette

**Ask:** Is this the same facility family as turbine/cooling without becoming those rooms or a cyan sci-fi basement?

Required family:

- light neutral / ivory panels;
- charcoal framing;
- gunmetal equipment;
- controlled burgundy / oxide-amber / safety-yellow accents;
- quiet large fields; saturation reserved for hazards and interactables.

Forbidden as theme:

- teal, turquoise, cyan decoration or lighting (A05 pool colour is **not** licensed here);
- colour confetti; identical orange wrapping every pipe;
- treating the handover swatch as “already user-approved” without tuning against neighbor pixels.

Compare against inspected turbine R07 and cooling finals. Drift into green-cyan industrial stock or Fortnite saturation is a palette fail.

### 4.9 Storytelling

**Ask:** Do people work here, or was a prop pack emptied on the floor?

Good (authored, sparse): clipboard, used rag, one tool at a real service, slightly misaligned chair, taped label, floor scuff on the route, mug off the walk path, replacement packing near a pump.

Bad: random debris, abandoned-bunker decay, a label on every wall, screens that only make noise, duplicated cooling-plant “P-02 / SEAL REPAIR” beat-for-beat.

Every prop needs a reason. Empty sterile plant also fails — the facility is active and maintained.

### 4.10 Valorant / reference fidelity

**Ask:** Would a cold screenshot read as a commercially released stylized PC game environment in this project’s language?

Must exhibit:

- believable proportions;
- simplified **but specific** geometry;
- strong silhouettes (condenser ≠ pump ≠ cabinet ≠ door ≠ cart);
- broad value/colour grouping;
- tactile materials;
- selective wear;
- negative space;
- secondary construction (panels, frames, recesses, supports) visible at gameplay distance.

Must not exhibit:

- PEAK/low-poly toy language;
- Three.js web-demo gloss;
- AAA photoreal grime;
- kitbash greeble;
- copied Valorant/PEAK/A05 protected layout, branding, or cyan hero;
- A07 slogans / external marks.

A05 is the **construction-depth** bar. Turbine/cooling finals are the **continuity** bar. Falling below either, even if “complete,” is a fidelity REJECT.

ART_DIRECTION pass/fail questions (all must be yes on the pixel set):

1. Believable place?
2. Stylized without cheapness?
3. Shapes specific, not primitive?
4. Materials distinguishable?
5. Wear localized and plausible?
6. Lighting creates depth?
7. Negative space present?
8. Used by people?
9. Signage restrained?
10. Props grounded and supported?
11. Avoids generic sci-fi?
12. Avoids generic low-poly?
13. Avoids modern AAA photorealism?
14. Screenshot could pass as a shipped stylized PC game?

A “no” on 14 is an automatic fidelity category fail.

---

## 5. Inspection checklist (every review cycle)

The critic must actually open images. Tick only what was seen.

### 5.1 Views

- [ ] Entire warm set inspected, including player-height corners
- [ ] Entire cold-open set inspected
- [ ] Close crops of exhaust, return, cooling, operator, glass, contacts
- [ ] Cutaways labelled and not used to hide player-view defects
- [ ] Roof/underside of turbine interface visible in at least one honest view or labelled cutaway

### 5.2 Faces (fail the relevant category if a claimed-complete room still hides these)

- [ ] All walls
- [ ] All door/access edges and reveals
- [ ] Roof / ceiling services
- [ ] Floor, trenches, grates, sump
- [ ] Condenser front
- [ ] Condenser side
- [ ] Condenser connection to U04
- [ ] Condensate equipment
- [ ] Cooling-water isolators and terminations
- [ ] Operator station and labels at readable distance

### 5.3 Neighbor non-regression (document-only unless the builder touched them)

- [ ] No claim of turbine interior edits
- [ ] U02 cap/structure not silently removed
- [ ] Cooling Plant not duplicated or overwritten
- [ ] Unbound remotes listed as unbound

---

## 6. Review output template

Each review file under `production/critics/` must contain:

1. Reviewer identity string: `independent grok-4.6 critic subagent`
2. Evidence list (exact image filenames, plan, interface, audits, cold comparison)
3. Scope sentence (this module + documented boundaries only)
4. **Three most consequential defects**
5. Remaining minute defects (image-referenced)
6. Missing-evidence list (`UNVERIFIED` items)
7. Independent scores table for all ten categories, each with disposition `PASS (>90)` or `REJECT (≤90 or unverified)`
8. Explicit statement if any category is unverified
9. Required new images to re-review claimed fixes
10. Final line: `REJECT` or `PASS FOR DEFINED LOCAL CONDENSER-BAY SCOPE` — never “pass pending renders”

Do not issue numeric scores at startup. Do not score plans, concepts, or hypothetical meshes.

---

## 7. Startup evidence state (2026-09-11)

Read independently:

- `C:/Users/Camer/Downloads/Grok_Condenser_Bay_Handover.md`
- `design/ART_DIRECTION.md`, `design/ART_REFERENCE_INDEX.md`
- turbine `FINAL_HANDOFF.md`, `CONNECTIONS.md`, `interface.json`, `TAKEOVER_REQUIREMENTS.md`
- cooling-plant `CONNECTIONS.md`, `interface.json`
- assembly audit `ASSEMBLY_AUDIT_20260911.md`
- neighbor renders: turbine `production/renders/final/R07/`; cooling `production/renders/final/`
- reactor `reference-a05-user-edited-orange.png`

**Condenser-bay scene renders: none at critic startup.**

**Disposition: NO SCORES. Standing by for actual rendered evidence.**


## Astra final independent acceptance record — 2026-09-12

The binding scoring law above is unchanged. Independent Luna reviewed R34 and R34-stability, all50 images each. Both scored coverage94, scale92, machinery93, circulation91, construction91, materials94, lighting92, palette94, storytelling92, fidelity91. Both cold18+7 comparisons PASS, six saved CPU checks PASS. Main cross-round numeric maximum FAIL remains retained; Luna adjudicated19 isolated above-threshold pixels acrossC02/C08 as honest GPU edge variance with no substantive regression. Astra accepts the disclosed visual stability judgment, without changing thresholds or raw results. Full evidence, residual limits and integration scope: [FINAL_HANDOFF.md](FINAL_HANDOFF.md).
