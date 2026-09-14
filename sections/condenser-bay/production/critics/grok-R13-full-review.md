# Condenser Bay R13 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R13 (new images; R02/R04/R07/R08/R10 scores are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

C01_ENTRY, C02_HERO, C03_REVERSE, C04_EXHAUST, C05_RETURN, C06_COOLING, C07_OPERATOR, C08_MAINT, C09_ROOF, C10_MATERIALS, W01_ENTRY_CORNER, W02_SW_TURN, W03_NW, W04_NE, W05_SE, W06_WEST_AISLE, W07_EAST_PULL, W08_GALLERY_TURN — `production/renders/review/R13/`.

**R13 cold-open:** none (`cold-R13` missing; `cold-R07` is not this revision). **UNVERIFIED.**

Documents read, not scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R13), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, `render_manifest.json`.

Continuity (inspected): turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R13 vs R10 (observed, not gifted):** Cream waterbox with a bolted circular cover. CEP yellow **cages** (not six dowels), motor fins, both pumps in C05. CW globe bodies **on the header**, labeled `CW SUPPLY` / `CW RETURN` wall pads with hexagonal plugs. SHIFT LOG readable. `3.5 m BUNDLE CLEAR` readable on W04. Stairs with a continuous yellow rail in W02. C08/C09 show gold `2.5 m` / `1.5 m` on a rectangular ceiling hole behind a grate. W05 shows a `TO TURBINE U02` stub. That is a real construction cycle. It is **not** a pass.

---

## Three most consequential defects

### 1. U04 is a labeled grate-hole, not a readable steam receive

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`, `C08_MAINT.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | All four look **up through grey floor bars**. C08/C09: gold `2.5 m` and `1.5 m` on a rectangular jamb. C04: blown highlights on the bars, a cream beam, light through a hole. No neck, bellows, flange, gasket, or slab seal. C02 shows only a cream riser disappearing into the gallery. |
| Severity | **blocker** |
| Observed mismatch | A dimensioned rectangle behind a grate is not a condenser-to-turbine receive. The steam chest-to-slab connection is still unseen. Four cameras repeat the same up-view. |
| Practical/art consequence | Contract row 1 remains incomplete. Coverage and machinery cannot pass. |

### 2. Operator station and stairs still read as toys against neighbor fidelity

| Field | Content |
|---|---|
| Image name | `C07_OPERATOR.png`, `W02_SW_TURN.png`, `C02_HERO.png` |
| Visible location | C07: four grey cubes with beige slats and round knobs; a lamp; a mug; a **red cube**; a paper. Header `CSB-01 CONDENSER` is now readable. W02/C02: gallery stairs with thin yellow sticks as a rail on a charcoal wall-chunk. |
| Severity | **major** (clustered: fidelity blocker) |
| Observed mismatch | Turbine R07 C02 and cooling C05 are specific industrial hardware. This panel is still a board with blocks. Stairs are a massing study with dowel rails. |
| Practical/art consequence | ART_DIRECTION Q14 remains no. Construction/detail and Valorant/reference fidelity stay below 91. |

### 3. Return-process and gallery evidence cameras still miss their jobs

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `W05_SE.png`, `C08_MAINT.png`, `W08_GALLERY_TURN.png` |
| Visible location | C05: two caged motors, cropped `CEP A / CEP` plates — no hotwell takeoff, no level glasses, no discharge to the handoff. W05: a ceiling crop of one stub labeled `TO TURBINE U02` on an empty wall. C08/W08: grate undersides, not a standing gallery deck. |
| Severity | **blocker** |
| Observed mismatch | Checklist row 2 is not in C05. W05 is not an SE hall. Maintenance row 4 is not a walkable gallery. |
| Practical/art consequence | Process path and access remain partly caption-only. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C02_HERO.png` | West waterbox | — | **Progress:** cream box, grey bolt ring, inner bolted cover. Hollow orange nozzle is gone. | Waterbox is now a machine face. |
| `C02_HERO.png` | Shell / gallery | major | Shell still shows faceted banding. Riser into the gallery is a cream slab, not a bellows. | Distinctive condenser still incomplete. |
| `C03_REVERSE.png` | Drop / gauge | major | Globe-like rings and a wheel sit on the drop (**progress** vs hanging open pipe). Gauge sits on the shell with no fitting. Drop ends without a visible vessel nozzle. | Connection is stylized, not closed. |
| `C06_COOLING.png` | Header | — | **Progress:** isolators are on the run; labels uncropped; hexagonal plugs in wall pads. | CW sockets are now a header story. |
| `C06_COOLING.png` | Wall pads / hangers | major | Pads have a hex plug, not a bolt-ring blind flange. Ceiling rods end in discs; rings float on the pipe. | Unbound far side correctly unproven; local flange language is still thin. |
| `C05_RETURN.png` / `C10_MATERIALS.png` | Coupling | — | **Progress:** yellow cage and hubs, not six dowels. C10 shows rubber-ish rings. | Coupling now rhymes with cooling P-01. |
| `C05_RETURN.png` | Motor / IDs | major | Box fins, not a grille face. `CEP A / CEP` and `CEP B / CE` cropped. | Pair is present; identity and fan end are unfinished. |
| `C01_ENTRY.png` | From D01 | major | Jamb in frame (**progress**). Right third is a blank wall. SHIFT LOG readable. OP sliver on the left. | Entry proves a portal, not a full first-hall read. |
| `W01_ENTRY_CORNER.png` | Stub | major | Clear opening, dado, `UNBOUND CONNECTOR`, extinguisher. Threshold/sill and uncropped `CSB-01` still absent. | Hole yes; parked-open hardware still partial. |
| `W02_SW_TURN.png` | Tan floor under CD-01 | major | `3.5 m BUNDLE CLEAR` reads backwards from this side. W04 reads it correctly. | Decal is one-facing; SW approach still wrong. |
| `W04_NE.png` | Pull bay | — | **Progress:** `3.5 m BUNDLE CLEAR` readable; cone; grey drip pan. | Pull keep-clear is now a floor. |
| `W07_EAST_PULL.png` | East floor | — | **Progress:** tan reserve, trench slot, caged pump, sump-like pad. Not a waterbox worm’s-eye. | Pull camera finally shows the lane. |
| `C07_OPERATOR.png` | Desk | major | Red cube, paper, mug, lamp. Switches are still cubes with slats. | Dressing tokens on a toy board. |
| *set* | R13 cold-open | blocker | Zero R13 cold cameras. | Lighting/materials stability **UNVERIFIED**. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C02_HERO.png` | `BUNDLE KEEP CLEAR` | minute | Wall plate readable. | Does not prove swept volume. |
| `W06_WEST_AISLE.png` | Signs | minute | `CSB-01 TURBINE CONDENSER BAY` and SHIFT LOG readable. Grey rail crosses the dado. | Wayfinding works; rail is a stick. |
| `W03_NW.png` | Pumps | minute | Pair, cages, `TOOLS` cabinet, `3.5 m BUNDLE KEEP CLEAR` on a far plate. Black loop pipe dominates the frame. | Hall exists; composition is cluttered. |
| `C08_MAINT.png` | `1.5 m` | minute | Gold dimension on the jamb. | Label is not a measured audit. |
| `C04_EXHAUST.png` | Grate bars | minute | Specular blow-out hides the hole’s far edge. | Even the grate read is incomplete. |

---

## R10 blockers — pixel verdict (R13 only)

| R10 blocker | R13 pixels |
|---|---|
| U04 2.5×1.5 unseen | **Partial.** Labeled rectangle visible through a grate. Neck, bellows, flange, seal **still unseen**. |
| CEP coupling as yellow dowels; C05 not return process | **Coupling addressed** (cage + hubs). **C05 still not return process** (no hotwell/level/handoff in that frame; stub only in W05). |
| Hollow waterbox nozzle; isolator off pipe; gallery/pull fail | **Waterbox and isolators addressed.** **Gallery standing still fails** (C08/W08 look up). **Pull lane addressed** on W04/W07. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- **R13 cold-open** of all 18 cameras
- U04 **neck, bellows, flange, seal** (hole labels are not that)
- D01 **threshold/sill** and uncropped portal identity
- Hotwell **level glasses**
- Condensate **handoff as a routed line** (W05 is a stub crop only)
- Gallery **standing** deck/rail/neck
- Hoist as a lifting system in a readable frame
- Extract fan
- Numerical clearances (screenshots cannot prove millimetres)
- Material family proof that is not mostly one coupling crop
- CW far-side cap (local hex plug is not a bolt-ring blind; unbound correctly not a facility loop)

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied. This is an identifiable industrial room with remaining generic hardware — not a 91.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **84** | **REJECT** | D01 hole, CW header, CEP cages, pull legend, U02 stub, labeled 2.5×1.5 grate-hole. U04 connection, level glasses, hoist, gallery standing, cold still missing. |
| 2. scale/layout | **85** | **REJECT** | Human hall, stairs, 3.5 m floor. Gallery is still a chunk. Desk is toy. |
| 3. machinery logic | **80** | **REJECT** | Isolators on the run; cages; globe on the drop; U02 stub. Steam receive is a hole, not a neck. Hotwell is a box. Gauge unfitted. |
| 4. circulation/readability | **84** | **REJECT** | W01 through-portal, W04/W07 pull, W02 stairs. W05 is a ceiling crop. W08 is not a standing gallery. |
| 5. construction/detail | **79** | **REJECT** | Bolted cover, cages, globes. Slat switches, stick rails, grate-only U04, hanger discs. |
| 6. materials | **76** | **REJECT (cold UNVERIFIED)** | Paint families starting to separate; C10 hubs. Still even sheen. No cold. |
| 7. lighting | **73** | **REJECT (cold UNVERIFIED)** | Practicals exist. C04/C08 grate is blown. No teal. No cold. |
| 8. palette | **86** | **REJECT** | Ivory / charcoal / oxide / yellow. Orange reserved more to pumps. Strongest category; still ≤90. |
| 9. storytelling | **78** | **REJECT** | Readable SHIFT LOG, mug, extinguisher, cone, unbound and U02 labels. Red cube on the desk. |
| 10. Valorant/reference fidelity | **74** | **REJECT** | Pumps now rhyme with cooling C05. Panel and stairs do not rhyme with turbine C02. Q14 is **no**. |

**Unverified blockers even if scores were higher:** R13 cold-open; U04 neck/flange/seal; level glasses; gallery standing; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R13 files for the same defects.

1. **C04** of the **exterior** receive: neck/bellows into the 2.5×1.5 opening with a flange/seal — not another grate underside.
2. **C08 / W08** **standing** on the gallery: deck, rail, neck, hole in context.
3. **C05** showing hotwell takeoff, both CEPs, and the handoff as a line — not motors only.
4. **C07** whose switches read as industrial hardware, not cubes with slats.
5. **W05** as an SE hall, not a ceiling stub (keep a dedicated crop of `TO TURBINE U02` if needed).
6. **C03** where the gauge has a fitting and the drop enters a nozzle.
7. **C06** wall pads as a bolt-ring or true blind, hangers that land.
8. **Cold-open of all 18** R13 cameras.

This reviewer will not prescribe meshes or coordinates.

---

**REJECT** — R13 is not accepted for the defined local condenser-bay scope.
