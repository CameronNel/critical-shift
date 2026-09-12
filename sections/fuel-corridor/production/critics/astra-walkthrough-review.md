# Astra walkthrough: specification, layout, doors and wayfinding

**The saved layout matches the chosen P07 topology and floor dimensions. It contains five external connections, six doorway assemblies and twelve main sliding leaves. Chapter 23 does not mandate a numeric exit count, corridor footprint or visible numbering sequence. The current wayfinding does need correction: repeated “04” has no clear role, door serials are duplicated, and several important wall labels cross posts or extend beyond their backing.**

This is a bounded review of the walkthrough baseline, not final-build acceptance. No source or scene edits, live Blender claim, neighbor access or rendering occurred.

## Evidence authority

The independent CPU inventory reopened frozen `production/checkpoints/full04/Fuel_Corridor.blend`, **7,837 objects**, SHA-256 `e2bcb2ddb4e2d6dda969520b2bbbaa7eab4e7f537d52e7b48537404091c24b35`. Its source/detail/interface identities are respectively `4bc2aa1a1ed9a81cadf37ec55873ca1e1d8ba898db3f8eba2035865684c46d92`, `69245a929ce08a7d0464db2f97e347fb8944d4af1dc638081296e6b5dbb6e012`, and `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e`. The saved blend remained unchanged.

Independent scene inventory and evaluated floor/font measurements are in `astra-walkthrough-full04-evidence.json`; source interpretation and exact citations are in `astra-walkthrough-spec-review.md`. The builder's separately collected live baseline, `production/evidence/walkthrough/wayfinding-before.json`, supplies the whole-glyph/arrow sample findings below. I read that evidence but did not independently claim or operate the live scene.

## Required scope versus implemented doorway count

GAME_SPEC chapter 23 places Fuel Corridor between Fuel Assembly and Reactor Hall, specifies travel targets and modular contents, and lists facility-wide route types. It does **not** require a corridor door for each later room or each listed shortcut. The assignment adds freight circulation, thresholds/doors, service bypass, service junctions and measured interfaces. Plausible dimensions may be chosen where unspecified.

| Saved assembly | Contract identity | Nominal opening W × H | Main leaves | Saved pose |
|---|---|---:|---:|---|
| REFINERY_BOUNDARY | F01_REFINERY | 2.60 × 3.00 m | 2 | Closed; removable presentation cap |
| REACTOR_BOUNDARY | F02_REACTOR | 5.00 × 5.00 m | 2 | Closed; removable presentation cap |
| PLANT_PORT | S01_PLANT | 2.00 × 2.50 m | 2 | Closed |
| CLEAN_PORT | S02_CLEAN | 2.00 × 2.50 m | 2 | Closed |
| WASTE_PORT | S03_WASTE | 2.40 × 3.00 m | 2 | Closed |
| FREIGHT_GATE | INTERNAL_FREIGHT_GATE; FG01 on plan | 3.40 × 3.40 m | 2 | Open |

Thus there are **five external ports plus one internal gate**, not six external exits. Twelve leaf meshes are not twelve doors. These are contract commitments chosen for the section; they are not a chapter-23 numeric exit mandate.

PLANT is one shared cooling/turbine/electrical header. CLEAN is one shared medical/reanimation/compliance header. Those labels do not establish several completed destination rooms or additional corridor exits. Neighboring refinery/reactor geometry and the section's presentation caps are separate ownership layers. In particular, neighboring reactor doors are documented as closed and destination assembly remains unverified. The five ports must not be described as five proven usable through-exits.

Relevant sources: authoritative `GAME_SPEC.md:2393`, `:2414`, `:2434`; master `BUILD_BRIEF.md:5`, `:9`; assigned `briefs/fuel-corridor.md:2`; local `architecture/CONNECTION_CONTRACTS.md:31`, `:35`, `:73`. The full absolute source paths are recorded in the companion specification review.

## Size and shape

The fourteen evaluated floor-cell meshes match P07 XY bounds within **1.15 micrometres**, with every finished floor top at **Z0**. Their overall floor envelope is **22.40 × 24.00 m**, spanning X −5.4 to 17.0 and Y 0 to 24. This is the bounding rectangle of an **irregular connected route**, not a filled rectangular room or the full outer envelope of walls, framing and fixtures.

The freight path has two right-angle turns: refinery approach, broad west staging turn, transverse passage/internal gate, east turn and reactor delivery leg. The service route bypasses the freight gate and reconnects beyond it. The plant branch projects west from that bypass; clean and waste are separate reserved branch ports.

| Layout element | Measured/contracted size |
|---|---|
| Main approach and delivery legs | 4.40 m gross width |
| West staging/turn bay | 6.60 × 6.20 m |
| East turn bay | 6.40 × 6.20 m |
| Cross passage | 4.40 m gross width |
| Refinery inlet enclosure | 3.20 m gross width |
| Reactor adapter | 5.60 m gross width |
| West service bypass | 2.40 m gross width |
| North bypass leg | 3.00 m gross width |
| Dressed service-route target | 2.00 m; a clearance target, not its gross wall width |
| Main / service ceiling contract | 4.40 / 3.00 m |
| Inlet / reactor enclosure ceiling contract | 3.90 / 5.90 m |

Freight centerline is **38.20 m**, service bypass **23.40 m**, plant-header centerline **5.40 m**. The freight estimate is **25.47 seconds at an assumed 1.50 m/s**, within the chapter's 15–30 second planning target. It excludes room-internal travel, turning, handling and door delays, so actual end-to-end timing is still unverified. No larger footprint is required by the reviewed specifications solely to satisfy a prescribed door count.

## Numbering and identity defects

**Moderate ambiguity:** the large east-wall reactor direction reads `04`; the entry marker and staging-bay marker also read `04`; the internal gate reads `FUEL TRANSFER / 04`. Separately, `02` accompanies `SERVICE` and `MEDICAL / CLEAN`. The scene provides no visible distinction between an area code, a route destination number and a doorway identifier. The same value could be a legitimate zone code, but it is currently presented in several roles without explaining that meaning.

**Duplicate equipment identifiers:** the five external door pairs contain ten serial texts, repeating `FC-04 / L` five times and `FC-04 / R` five times. `FC / 04` also repeats on access covers and equipment. Shared model/department codes can repeat; unique serial or doorway labels should not masquerade as those shared codes. Smaller `TOOLS / 04` labels have another context and should not become additional exit numbers.

The existing plan already distinguishes **F01/F02**, **S01/S02/S03** and **FG01**. Using that documented identity structure consistently is compatible with the specification and does not invent additional exits. No reviewed source requires a contiguous visible sequence such as doors 01 through 06. Destination words remain necessary; color or an unexplained numeral alone is insufficient.

Type hierarchy is also inconsistent in the baseline: large destination titles range from about **0.106 m** (`CLEAN SERVICES`) to **0.245 m**, with PLANT at about **0.198 m** and the delivery REACTOR title about **0.233 m**. Some size adjustment can be intentional, but shrinking words to fit unrelated wall spans has created uneven prominence. Font size values alone do not prove reading-distance legibility.

## Text extending beyond backing or crossing structure

My independent center rays found backing behind all 127 saved font objects, generally within a few millimetres. That is **not a whole-label fit test**: a word's center can be supported while its ends hang past a corner. The builder's evaluated glyph/arrow evidence contains 143 objects and demonstrates this distinction:

| Label or group | Baseline sampled finding |
|---|---|
| Plant `PLANT` title | 32/182 vertices unbacked; 32/182 have a forward structural obstruction |
| Three plant arrows | 11/18 vertices unbacked in total; two additional forward obstruction hits |
| Plant `SERVICES` subtitle | 66/189 vertices obstructed by the wall web/flanges |
| Cross-passage `FUEL ROUTE` | 45/197 vertices obstructed by wall web/flanges |
| Cross-passage `KEEP TURN CLEAR` | 14/183 vertices obstructed |
| Delivery `REACTOR` | 42/184 vertices obstructed by wall web/flanges |
| Delivery `FREIGHT APPROACH` | 51/181 vertices obstructed |

These are relevant placement defects in primary wayfinding. Their correction needs to establish both a real backing surface and an unobstructed approach-facing text area; changing the string alone cannot establish that.

Other sampled hits require context. `Bypass_first_aid_type` is behind its **clear lid**, so its 205/205 physical ray hits do not establish visual unreadability through transparent material. The fully obscured spare-parts-case label is equipment dressing, not a route exit. The service-air label has 24/184 samples obstructed by its union, and the plant door word has two pull-rail hits; those are smaller label-placement observations. None of these counts alone is a rendered legibility score.

## Review boundary

The paused general build review has not resumed. This report covers the authorized walkthrough/specification correction scope. It does not approve any pending live edits, prescribe replacement geometry, or claim tested navigation, vehicle turning, runtime door operation, neighboring passage, final material/lighting quality or safety-code egress. A later corrected snapshot can be checked against the identities, floor/port commitments and actual glyph-support findings recorded here.
