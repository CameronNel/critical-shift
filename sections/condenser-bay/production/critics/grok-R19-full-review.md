# Condenser Bay R19 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R19 (new images; R17/R18 scores not reused)  
**Disposition:** **REJECT**

## Evidence inspected

Warm, 1920×1080 EEVEE — all 18 under `production/renders/review/R19/`, opened and close-cropped.

Cold-open: all 18 under `cold-R19/`. SHA256 differs on every pair vs warm. Visual match on C01, C04, C05, C07, C08 (TAA). **Cold complete.**

Hashes vs R18: all 18 **NEW** (re-rendered). Composition on C01–C04, C06–C10, W01–W04, W06–W08 is the R18 language. **W05 is worse.**

Documents: `FLOORPLAN.md`, `CHECKLIST.md`, `interface.json` (rev R19), `RUBRIC.md`, `CORRECTION_HISTORY.md`.

Continuity: turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**R19 vs R18 (observed):** No construction cycle on U04, C05 drop, hangers, panel, stairs, or fan. W05 is now a blank wall with the U02 stub cropped to `NE U02` in the corner. That is not a fix. **Not a pass.**

---

## Three most consequential defects

### 1. U04 is still a labeled bar with sparse cubes

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: cream chest, zigzag sleeve, dark flange with `U04 2.5 x 1.5`, a handful of cube bolts on the left, blown specular. No continuous bolt ring. Gasket is a thin dark line. Tight crop. C09/W08: corrugation underside; deck sliver. |
| Severity | **blocker** |
| Observed mismatch | Same as R18. A stencil and four cubes are not a sealed slab landing. |
| Practical/art consequence | Contract row 1 is not complete. A screenshot cannot prove 2.5×1.5 mm. |

### 2. C05 drop unclosed; W05 is now an empty wall

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `W05_SE.png` |
| Visible location | C05: white elbow from under the hotwell; vertical drop ends in a **grey ring**. Level tubes opaque. W05: charcoal wall, gallery soffit, stub cropped to the corner as `NE U02`. |
| Severity | **blocker** |
| Observed mismatch | Return path unchanged. W05 **regressed**: R18 at least framed the collar; this is a blank wall. Not an SE hall. |
| Practical/art consequence | Row 2 and circulation fail. Handoff is unverified as a readable line. |

### 3. C07 / hangers / stairs / fan remain primitives

| Field | Content |
|---|---|
| Image name | `C07_OPERATOR.png`, `C06_COOLING.png`, `C08_MAINT.png`, `W02_SW_TURN.png` |
| Visible location | C07: faceted beige discs. C06: hanger rods and discs that do not land. C08: concentric-circle fan; yellow T-hoist. W02: charcoal stair mass, stick rails. |
| Severity | **major** (clustered: fidelity) |
| Observed mismatch | Unchanged vs R18. Cooling C05 and turbine C02 are still a different language. |
| Practical/art consequence | Construction and Valorant/reference fidelity stay below 91. Q14 is **no**. |

---

## Further defects

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` | D01 jamb | major | Jamb in frame; right third blank. | First hall cropped. |
| `W01_ENTRY_CORNER.png` | Stub | major | `UNBOUND CONNECTOR`. No sill, no uncropped identity. | Parked-open hardware partial. |
| `C02_HERO.png` | Shell | major | Bolted waterbox held. Faceted shell. Riser is a cream slab. | Hall-scale condenser incomplete. |
| `C03_REVERSE.png` | Drop / tubes | major | Globe on drop; opaque tubes. Drop does not enter a nozzle. | Levels are not glass. |
| `C06_COOLING.png` | Pads / hangers | major | Isolators on the run. Hex plugs, not bolt-ring blinds. Hangers float. | CW language thin. |
| `W04_NE.png` | Tan floor | major | Dual legends, one inverted, stacked. | Crude two-way paint. |
| `C09_ROOF.png` | Sleeve | major | Gallery zigzag. | Not a roof system. |
| `W08_GALLERY_TURN.png` | Corrugation | major | Deck sliver. | Not a standing turn. |
| `C08_MAINT.png` | Rail | major | Rail/grate/fan/hoist jammed. | Standing-ish, not a walk. |
| `C10_MATERIALS.png` | Motor | major | Cage/hubs held. Box fins, not a grille. | Short of cooling P-01. |
| `W06_WEST_AISLE.png` | Signs | minute | CSB-01 and SHIFT LOG readable. Stick rail. | Wayfinding works. |
| `W03_NW.png` | Loop | minute | Pair visible; loop dominates. | Hall exists. |
| Cold vs warm | C01/C04/C05/C07/C08 | minute | Hash DIFF, visual match. | Honest TAA. |

---

## Missing evidence (`UNVERIFIED`)

- U04 **full bolt circle, readable gasket, measured slab jamb**
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

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied. W05 regression is scored, not ignored.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **88** | **REJECT** | U04 labeled. W05 stub worse. Full bolt circle, D01 sill, glass levels, roof system missing. |
| 2. scale/layout | **86** | **REJECT** | Human hall, 3.5 m floor. Gallery chunky. Desk toy. |
| 3. machinery logic | **85** | **REJECT** | Closed labeled receive. Drop unclosed; levels opaque; handoff cropped. |
| 4. circulation/readability | **84** | **REJECT** | W01 through-portal, W04/W07 pull. W05 empty wall. W08 underside. Dual legend fights itself. |
| 5. construction/detail | **86** | **REJECT** | Labeled flange + sparse bolts. Hangers, stick stairs, 2D fan, unclosed drop remain. |
| 6. materials | **80** | **REJECT** | Cold exists. C10 hubs. Level tubes not glass. Even sheen. |
| 7. lighting | **80** | **REJECT** | Cold exists. C04/C09 still blown on the sleeve. No teal. |
| 8. palette | **87** | **REJECT** | Ivory / charcoal / oxide / yellow. Strongest; still ≤90. |
| 9. storytelling | **80** | **REJECT** | SHIFT LOG, mug, book, unbound. Dual legend mess. U02 cropped. |
| 10. Valorant/reference fidelity | **80** | **REJECT** | Panel, fan, stairs still cheap vs turbine/cooling. Q14 is **no**. |

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images

Do not resubmit these R19 files for the same defects. W05 must not be another empty wall.

1. **C04** of a **full** flange landing: continuous bolt ring, readable gasket, slab rectangle.
2. **C09** of roof as a system (slab, hole, fan).
3. **C05** where the drop enters a nozzle.
4. **W05** as an SE hall **and** a readable handoff line.
5. **W08** standing on the deck.
6. **C07** bezels that read as industrial rotaries.
7. **C06** hangers that land.
8. **C03** level columns that read as glass.

This reviewer will not prescribe meshes.

---

**REJECT** — R19 is not accepted for the defined local condenser-bay scope.
