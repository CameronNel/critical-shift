# Condenser Bay R04 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R04 (new images; R02 scores 22–61 are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

C01_ENTRY, C02_HERO, C03_REVERSE, C04_EXHAUST, C05_RETURN, C06_COOLING, C07_OPERATOR, C08_MAINT, C09_ROOF, C10_MATERIALS, W01_ENTRY_CORNER, W02_SW_TURN, W03_NW, W04_NE, W05_SE, W06_WEST_AISLE, W07_EAST_PULL, W08_GALLERY_TURN — all under `production/renders/review/R04/`.

Documents read, not treated as scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R04), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, `production/renders/review/R04/render_manifest.json`.

Continuity comparison (inspected): turbine R07 `C02_hero.png`; cooling-plant `C02_HERO.png`, `C05_PUMP_A.png`.

**Cold-open:** none. **UNVERIFIED.** Cannot pass lighting/materials stability or any “finished artifact” claim.

**Scope:** this module and documented boundaries (`U04` receive, local condensate handoff, provisional CW sockets). Not turbine hall, not Cooling Plant, not whole-map assembly.

**R04 vs R02 (observed, not gifted):** walk cameras now exist and several (W03, W04, W05) actually show a hall. Analog gauge faces with needles appear on C07. CEP pair, EJ-01 cans, stairs, a hoist hook, and dadoed walls are visible. That is a real cycle, not a relabel. It is **not** a pass.

---

## Three most consequential defects

### 1. `U04` receive is still not in the pixels

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png` (checklist camera); `C08_MAINT.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` do not rescue it |
| Visible location | C04: nearly the entire 1920×1080 frame is unlit black; a cream wedge on the right edge only. C08/W08: underside of a grey gallery beam. C09: a blank grey wall, a yellow stick, a hoist fragment. C02 upper-right: dark unarticulated slabs above the shell, not a neck/flange/opening. |
| Severity | **blocker** |
| Observed mismatch | The module exists to receive turbine `IF_LP_EXHAUST_CONDENSER` (2.5 × 1.5 m). These frames do not show an opening, bellows, mating flange, seal, or slab hole. C04 is the same failure mode as R02 (camera inside/against a dark volume). File size is ~1.3 MB vs ~2.1 MB for room views — consistent with empty black. |
| Practical/art consequence | Coverage and machinery logic **cannot pass**. A hollow neck in a blend file is not evidence. |

### 2. Receiving access and maintenance cameras still fail their jobs

| Field | Content |
|---|---|
| Image name | `C01_ENTRY.png`, `W01_ENTRY_CORNER.png`, `C08_MAINT.png`, `W07_EAST_PULL.png`, `W08_GALLERY_TURN.png` |
| Visible location | C01/W01 look **into** the machine from the south-west; D01 leaves, jambs, and threshold are never in frame. C08/W08 are jammed into the gallery fascia. W07 is a worm’s-eye of the east waterbox, not a 3.5 m pull lane. |
| Severity | **blocker** |
| Observed mismatch | Checklist rows 4 and 8 require D01 2.0 × 2.4 parked-open leaves and gallery/hoist/pull proof. None of those objects are readable as access. Stairs exist in C01/W02 as a grey flight with yellow sticks; that does not prove a door or a standing gallery. |
| Practical/art consequence | Circulation and contract coverage stay failed. “Walk cameras exist” is not the same as “every wall and the door are evidenced.” |

### 3. Process hardware is still greybox: open pipes, orange boxes, toy couplings

| Field | Content |
|---|---|
| Image name | `C03_REVERSE.png`, `C01_ENTRY.png`, `C06_COOLING.png`, `C10_MATERIALS.png`, `C07_OPERATOR.png` |
| Visible location | C03: white pipe elbows and ends in open air in front of the shell (same R02 dead-end, still present). C01 waterbox: white pipe meets a disc with a **hollow open cut** visible inside the tube. C06: same disc-and-pipe, four scattered bolts, a thin hanging ring, blown highlight. C10: yellow sticks between orange disc and motor. C07: beige U-frames, a red cube, a mushroom on a tiny shelf. |
| Severity | **blocker** |
| Observed mismatch | Hard gates: disconnected services; generic bevelled-box language; primitive controls. Cooling `C05_PUMP_A` still shows flange rings, a yellow coupling **cage**, finned motor, readable ID. This bay’s pumps are orange discs on orange legs. Waterboxes are cubes, not tube-sheets. |
| Practical/art consequence | Valorant/reference fidelity cannot approach neighbor continuity. The player cannot follow exhaust → condense → extract → CW in/out. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `W06_WEST_AISLE.png` | Wall card, mid-right | major | `SHIFT LOG` is still mirrored (`GOL TFIHS`). Same R02 lettering defect. Card is a floating rectangle. | Dressing is unreadable; R04 did not fix this. |
| `C01_ENTRY.png` | Far-left wall | major | Same reversed shift-log card visible beside cropped `CSB-01` / `VACUUM`. | Entry still does not orient a worker. |
| `W04_NE.png` | Tan floor field, lower left | major | Legend reads backwards: `3.5 m BUNDLE` mirrored. Decal faces the wrong side of the reserve. | Pull-bay instruction cannot be read from the approach that sees the bay. |
| `C09_ROOF.png` | Yellow cylinder vs grey wall | major | Member meets a blank wall with no fitting, sleeve, or end condition. Most of the frame is empty paint. Hoist hook is a corner sliver. | Roof/services camera does not show U04, extract, or a ceiling system. |
| `C05_RETURN.png` | Foreground orange disc | major | One volute fills the lens. Second CEP, hotwell suction, level glasses, and `IF_CONDENSATE_HANDOFF` are not in this checklist view. (W03/W05 show a pair; C05 itself still fails its row.) | Return equipment is only proven by other cameras, and still without the handoff stub. |
| `C06_COOLING.png` / `W07_EAST_PULL.png` | East waterbox / under-stair dark | major | No capped `IF_CW_SUPPLY`/`IF_CW_RETURN` wall flanges. Isolation wheels are not at a readable service distance. Gauge exists on a high pipe (C06, top-left) without a header story. | Cooling-water contract is **UNVERIFIED**. |
| `C07_OPERATOR.png` | Mid panel / shelf | major | Needles exist (improvement). Guards are still beige brackets around cylinders. Trip is a red cube plus a disc. Header `CSB-01 CON…` is cropped. Desk is a thin board. | Station is identifiable, not industrial, not at turbine-control density. |
| `C02_HERO.png` | Shell / waterbox | major | Hero is still a three-quarter of a cube-plus-tank jammed in the aisle, not a composed hall silhouette like turbine C02. Manways are orange rings. Cage rods read as black scratches on the shell. | Distinctive condenser mass is weak. |
| `W03_NW.png` | North-west pumps | major | Pair is visible. Volutes remain orange lollipops. `TOOLS` is a blank slab. Overhead pipe ends at a wall disc without a valve train. | Best process view in the set; still generic. |
| `W05_SE.png` | Under gallery looking north | major | Useful hall read: piers, grey drip pad, two motors, wall fan. Gallery soffit is an unarticulated black slab occupying the top third. | Architecture is a lid, not a ceiling. |
| `W02_SW_TURN.png` | Stair / yellow posts | major | Stair stringer is a charcoal wall; “rail” is disconnected yellow sticks that do not form a continuous handrail. | Maintenance access looks like a blockout. |
| `C10_MATERIALS.png` | Left 60% of frame | major | Orange field still dominates. Coupling is dowels. Motor fins are boxes. No gasket, glass, rubber, or concrete family in one readable set. | Mandatory material view remains inadequate. Cold-open **UNVERIFIED**. |
| *set* | D01 portal | blocker | No parked sliding leaves, no 2.0 × 2.4 opening, no threshold, no “what is behind the door.” | Access **UNVERIFIED**. |
| *set* | Cold reopen | blocker | No cold batch. | Artifact stability **UNVERIFIED**. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` / `C02_HERO.png` | `CD-01` / nameplate | minute | IDs exist (`CD-01 SURFACE / SCENIC / NO RATING`). Honest non-rating is correct. | Does not make the machine specific. |
| `W06_WEST_AISLE.png` | EJ-01 cans | minute | `EJ-01` lettering is readable on stacked cylinders with a strap. | Ejector is named, not a two-stage machine. |
| `C07_OPERATOR.png` | FLOW / CW IN / LEVEL / VAC | minute | Labels and analog faces are now legible. | Instruments still lack glass thickness, bezels, and a housing. |
| `W04_NE.png` | Distant OP panel | minute | Second small board with FLOW/LEVEL/VAC is visible across the hall. | Duplicate/remote panel is unexplained. |
| `C06_COOLING.png` | Ivory east wall | minute | Quiet dadoed panels match facility family. | Fragment only. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- **Cold-open** of the same 18 cameras
- **D01** leaves, jambs, threshold, and volume immediately outside/inside the portal
- **U04** 2.5 × 1.5 m slab opening, neck exterior, flange, seal, supports
- Capped **CW** wall flanges and isolators at service distance
- **`IF_CONDENSATE_HANDOFF`** stub (0.2 m toward turbine U02; cap not to be removed)
- Level glasses on the hotwell
- Gallery **standing** view (deck, rail, neck) — C08/W08 are fascia crops
- 3.5 m pull hatch as a keep-clear from a camera that is not under the waterbox
- Numerical clearances / cart envelope (screenshots cannot prove millimetres)
- Material family close-up that is not mostly one orange shader
- Every remaining wall corner at player height (north-east wall is partial; south portal wall unseen)

Builder notes that U02 cap is not removed and CW is provisional are accepted as **documentation**. They do not excuse missing local sockets in the frames that claim to show them.

---

## Independent category scores

Pass floor is **> 90**. 90 or below is REJECT. Unverified cannot pass. R02 numbers are not copied forward.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **58** | **REJECT** | Room systems are started (CD-01, CEP pair, EJ label, OP, stairs, drip pad). Checklist cameras C01/C04/C06/C08/C09 still do not prove D01, U04, CW caps, gallery, or roof hole. Cold missing. |
| 2. scale/layout | **71** | **REJECT** | W03–W05 finally show a hall with human stairs and aisles. Gallery is a chunk; operator desk is toy; D01 and 3.5 m pull remain unseen. Identifiable layout, not a pass. |
| 3. machinery logic | **54** | **REJECT** | Open pipe on C03; hollow pipe into waterbox on C01/C06; U04 black; CW flanges absent; pumps are discs; no readable exhaust→hotwell→CEP→handoff chain. |
| 4. circulation/readability | **66** | **REJECT** | Walk set exists and west/south/east floor is partly readable. D01 **UNVERIFIED**. C08/W07/W08 are not circulation evidence. Floor legend mirrored. |
| 5. construction/detail | **51** | **REJECT** | Sparse cube-bolts, orange waterbox cubes, stick coupling, stick rails, unarticulated gallery, hanging ring, dead-end pipes. Neighbor flange/pedestal language is not met. |
| 6. materials | **57** | **REJECT (cold UNVERIFIED)** | Less foam than R02; orange still plastic; C10 is a volute blob plus box fins. Families not distinguishable. Cold-open absent. |
| 7. lighting | **59** | **REJECT (cold UNVERIFIED)** | Walk views are exposed. C04 is a black void. C06 waterbox is blown. C09 is a dark wall. No room key hierarchy. No teal. |
| 8. palette | **73** | **REJECT** | Ivory / charcoal / oxide / yellow family, no teal. Orange still wraps entire waterboxes and volutes instead of accents. Strongest category; still ≤90. |
| 9. storytelling | **50** | **REJECT** | Tools slab, cone, paper, backwards log. Cart, PPE, extinguisher, used service not evidenced. Sterile greybox plus tokens. |
| 10. Valorant/reference fidelity | **47** | **REJECT** | Versus turbine R07 C02 and cooling C02/C05: this is a different, cheaper language. ART_DIRECTION Q14 is **no**. Primitive panel and generic pumps remain veto-level. |

**Unverified items that block a pass even if scores were higher:** cold-open; D01 portal; U04 receive; CW caps; condensate handoff stub; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R04 files for the same defects. Each claimed fix needs **new** pixels.

1. **C01 / W01** that include D01 parked leaves, threshold, and the first hall — door in frame, walls on.
2. **C04** of the **exterior** neck and U04 opening (flange/seal/slab). Not the interior of a duct.
3. **C08 / W08** standing on the gallery: deck, rail, neck access.
4. **C09** looking at the actual ceiling hole and services, not a blank wall.
5. **C06 / W07** showing capped east-wall CW flanges, isolators, hoist, and pull-bay floor from a readable distance.
6. **C03** (or a new reverse) in which every visible pipe caps, flanges, or enters a nozzle — the hanging open end must be gone in pixels.
7. **C05** with both CEPs, hotwell takeoff, and the documented handoff stub.
8. **C10** that can tell painted steel / cast / rubber / concrete apart without a 60% orange crop.
9. **W06** with shift-log lettering facing the aisle.
10. **W04** with bundle-reserve lettering facing the approach.
11. **Cold-open** of the full 18-camera set with honest comparison.

This reviewer will not prescribe replacement meshes or coordinates. Cameras that remain inside the condenser, under the gallery fascia, or staring at a wall will fail on sight again.

---

**REJECT** — R04 is not accepted for the defined local condenser-bay scope.
