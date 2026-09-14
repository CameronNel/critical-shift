# Condenser Bay R18 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R18 (new images; R16/R17 scores not reused)  
**Disposition:** **REJECT**

## Evidence inspected

Warm, 1920×1080 EEVEE — all 18 under `production/renders/review/R18/`, opened and close-cropped.

Cold-open: all 18 under `cold-R18/`. SHA256 differs on every pair vs warm. Visual match on C01, C04, C05, C07, C08, C09 (TAA). **Cold complete.**

Hashes vs R17: all 18 **NEW**.

Documents: `FLOORPLAN.md`, `CHECKLIST.md`, `interface.json` (rev R18), `RUBRIC.md`, `CORRECTION_HISTORY.md`.

Continuity: turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**R18 vs R17 (observed):** C04 now carries gold `U04 2.5 x 1.5` on the dark flange, a few cube bolts on the left, and a thin dark band at the chest. Closed wall and corrugation held. That is a real, narrow cycle. **Not a pass.**

---

## Three most consequential defects

### 1. U04 is labeled; the mating face is still not a bolt circle

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: cream chest, zigzag sleeve, dark flange with `U04 2.5 x 1.5`, a handful of cube bolts on the left only, blown specular. No continuous bolt ring. Rubber “strip” is a thin dark line, not a readable gasket. Tight crop. C09/W08: corrugation underside; deck sliver. |
| Severity | **blocker** |
| Observed mismatch | A dimension stencil and four cubes are not a sealed slab landing. Roof is still the sleeve, not a slab system. |
| Practical/art consequence | Contract row 1 is closer, not complete. A screenshot still cannot prove 2.5×1.5 mm. |

### 2. C05 drop still does not enter a nozzle; W05 is still a ceiling collar

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `W05_SE.png` |
| Visible location | C05: white elbow from under the hotwell; vertical drop ends in a **grey ring**. Level tubes opaque with cube caps. W05: `TO TURBINE U02` on a ceiling plane. |
| Severity | **blocker** |
| Observed mismatch | Unchanged vs R17. Handoff is a labeled penetration, not a routed line in a hall. |
| Practical/art consequence | Row 2 and W05 circulation fail. |

### 3. C07 / hangers / stairs / fan remain primitives

| Field | Content |
|---|---|
| Image name | `C07_OPERATOR.png`, `C06_COOLING.png`, `C08_MAINT.png`, `W02_SW_TURN.png` |
| Visible location | C07: faceted beige discs. C06: hanger rods and discs that do not land. C08: concentric-circle fan; yellow T-hoist. W02: charcoal stair mass, stick rails. |
| Severity | **major** (clustered: fidelity) |
| Observed mismatch | Unchanged vs R17. Cooling C05 and turbine C02 are still a different language. |
| Practical/art consequence | Construction and Valorant/reference fidelity stay below 91. Q14 is **no**. |

---

## Further defects

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C04_EXHAUST.png` | Flange | — | **Progress:** `U04 2.5 x 1.5` readable; sparse bolts exist. | Identity yes; construction still a bar. |
| `C01_ENTRY.png` | D01 jamb | major | Jamb in frame; right third blank. | First hall cropped. |
| `W01_ENTRY_CORNER.png` | Stub | major | `UNBOUND CONNECTOR`. No sill, no uncropped identity. | Parked-open hardware partial. |
| `C02_HERO.png` | Shell | major | Bolted waterbox held. Faceted shell. Riser is a cream slab. | Hall-scale condenser incomplete. |
| `C03_REVERSE.png` | Drop / tubes | major | Globe on drop; opaque tubes. Drop does not enter a nozzle. | Levels are not glass. |
| `C06_COOLING.png` | Pads / hangers | major | Isolators on the run. Hex plugs, not bolt-ring blinds. Hangers float. | CW language thin. |
| `W04_NE.png` | Tan floor | major | Dual legends, one inverted, stacked. | Crude two-way paint. |
| `C09_ROOF.png` | Sleeve | major | Gallery zigzag, distinct from C04. | Not a roof system. |
| `W08_GALLERY_TURN.png` | Corrugation | major | Deck sliver. | Not a standing turn. |
| `C08_MAINT.png` | Rail | major | Rail/grate/fan/hoist jammed. | Standing-ish, not a walk. |
| `C10_MATERIALS.png` | Motor | major | Cage/hubs held. Box fins, not a grille. | Short of cooling P-01. |
| `W06_WEST_AISLE.png` | Signs | minute | CSB-01 and SHIFT LOG readable. Stick rail. | Wayfinding works. |
| `W03_NW.png` | Loop | minute | Pair visible; loop dominates. | Hall exists. |
| Cold vs warm | C01/C04/C05/C07/C08/C09 | minute | Hash DIFF, visual match. | Honest TAA. |

---

## R17 blockers — pixel verdict

| R17 blocker | R18 pixels |
|---|---|
| U04 dark bar without bolt circle, gasket, dimensioned jamb | **Partial.** Label `U04 2.5 x 1.5` exists. Sparse cube bolts on one side. Gasket is a thin line. No full ring, no rubber read, C04 still a tight crop. |
| C05 drop / W05 ceiling stub | **Not addressed.** |
| C07 toy; C06 hangers; stairs/fan | **Not addressed.** |

---

## Missing evidence (`UNVERIFIED`)

- U04 **full bolt circle, readable gasket, measured slab jamb** (label is not a measurement)
- D01 **threshold/sill**
- Level glasses as **glass**
- Closed hotwell **nozzle**
- Gallery **standing turn**
- Roof as a **slab system**
- SE **hall**
- Handoff as a **routed line** in a readable room
- Numerical clearances

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **89** | **REJECT** | U04 labeled. Full bolt circle, D01 sill, glass levels, roof system still missing. |
| 2. scale/layout | **86** | **REJECT** | Human hall, 3.5 m floor. Gallery chunky. Desk toy. |
| 3. machinery logic | **85** | **REJECT** | Closed labeled receive. Drop unclosed; levels opaque; handoff is a collar. |
| 4. circulation/readability | **85** | **REJECT** | W01 through-portal, W04/W07 pull. W05 ceiling. W08 underside. Dual legend fights itself. |
| 5. construction/detail | **86** | **REJECT** | Labeled flange + sparse bolts. Hangers, stick stairs, 2D fan, unclosed drop remain. |
| 6. materials | **80** | **REJECT** | Cold exists. C10 hubs. Level tubes not glass. Even sheen. |
| 7. lighting | **80** | **REJECT** | Cold exists. C04/C09 still blown on the sleeve. No teal. |
| 8. palette | **87** | **REJECT** | Ivory / charcoal / oxide / yellow. Strongest; still ≤90. |
| 9. storytelling | **80** | **REJECT** | SHIFT LOG, mug, book, unbound, U02 and U04 labels. Dual legend mess. |
| 10. Valorant/reference fidelity | **80** | **REJECT** | Labeled flange is more specific. Panel, fan, stairs still cheap vs turbine/cooling. Q14 is **no**. |

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images

1. **C04** of a **full** flange landing: continuous bolt ring, readable gasket, slab rectangle — not four cubes and a stencil.
2. **C09** of roof as a system (slab, hole, fan).
3. **C05** where the drop enters a nozzle.
4. **W05** as an SE hall and a readable handoff line.
5. **W08** standing on the deck.
6. **C07** bezels that read as industrial rotaries.
7. **C06** hangers that land.
8. **C03** level columns that read as glass.

This reviewer will not prescribe meshes.

---

**REJECT** — R18 is not accepted for the defined local condenser-bay scope.
