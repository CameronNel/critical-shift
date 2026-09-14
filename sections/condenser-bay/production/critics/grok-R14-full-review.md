# Condenser Bay R14 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R14 (new images; prior scores are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm, 1920×1080 EEVEE, ray tracing off, opened and close-cropped — all 18 under `production/renders/review/R14/`.

Cold-open: all 18 under `production/renders/review/cold-R14/`. SHA256 differs on every pair (genuine second pass). Visual match on C04/C07 compared at crop: same geometry, same materials, TAA noise only. **Cold exists for this revision.**

Documents read, not scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R14), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, warm and cold `render_manifest.json`.

Continuity: turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R14 vs R13 (observed, not gifted):** C04 looks up the cream neck into stacked frames over a grate. C05 includes the cream hotwell and a suction elbow. C07 has round beige bezels instead of cubes. C08 shows yellow rail, grate deck, wall fan, hoist ring. Dual `3.5 m BUNDLE CLEAR` on W04. Opaque tubes on the hotwell. Full 18-camera cold. Real cycle. **Not a pass.**

---

## Three most consequential defects

### 1. U04 is still not a readable flange/seal receive

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: cream rectangular duct into nested grey/black frames; a grate visible **inside** the duct; blown specular on the frames. No gasket ring, no bolt circle on the slab, no 2.5×1.5 jamb labels in this frame. C09: almost the entire frame is blown grate bars. W08: `1.5 m` on a grate, a sliver of deck at the right. |
| Severity | **blocker** |
| Observed mismatch | Nested picture-frames around a cream box are not a bellows convolution landing on a sealed slab opening. The steam chest-to-turbine mating face is still unseen. C09 is not a roof camera. |
| Practical/art consequence | Contract row 1 remains incomplete. Coverage and machinery cannot pass. |

### 2. Condensate handoff left the set; C05 suction does not close; W05 is empty wall

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `W05_SE.png` |
| Visible location | C05: hotwell box, white elbow from under it, globe on a drop that still ends in a grey ring, not a vessel nozzle. Level “glasses” are opaque grey tubes with cube caps. W05: a charcoal wall and the underside of a gallery — no hall, no `TO TURBINE U02` stub (that label was in R13 W05 and is gone here). |
| Severity | **blocker** |
| Observed mismatch | Checklist row 2 still lacks a closed takeoff and a routed handoff. W05 fails as an SE walk. |
| Practical/art consequence | Return path is partly implied. `IF_CONDENSATE_HANDOFF` is **UNVERIFIED** in this revision’s pixels. |

### 3. Secondary hardware is still toy against neighbor fidelity

| Field | Content |
|---|---|
| Image name | `C07_OPERATOR.png`, `C06_COOLING.png`, `C08_MAINT.png`, `W02_SW_TURN.png` |
| Visible location | C07: faceted beige discs with a knob; lamp occludes the first switch; desk is mug + paper + book. C06: hanger rods end in discs that do not land on the ceiling; rings float on the pipe. C08: extract “fan” is concentric circles in a square; hoist is a yellow T with a ring. W02: charcoal stair mass, thin rails. |
| Severity | **major** (clustered: fidelity shortfall) |
| Observed mismatch | Cooling C05 and turbine C02 are specific. These switches, hangers, fan, and stairs are still primitives. |
| Practical/art consequence | Construction and Valorant/reference fidelity stay below 91. ART_DIRECTION Q14 remains no. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C04_EXHAUST.png` | Neck | — | **Progress:** exterior cream duct into the ceiling hole, not a grate-only up-view. | Receive is started, not finished. |
| `C05_RETURN.png` | Hotwell / elbow | — | **Progress:** cream box and suction elbow in frame with a CEP. | Process is partly readable. |
| `C07_OPERATOR.png` | Switches | — | **Progress:** round bezels, not cubes. Header `CSB-01 CONDENSER` readable. | Still a board with discs. |
| `C08_MAINT.png` | Gallery | — | **Progress:** rail, grate, fan, hoist ring in one standing-ish view. | Camera is jammed on the rail; deck is a sliver. |
| `C01_ENTRY.png` | From D01 | major | Jamb in frame. Right third blank wall. OP sliver, EJ-01, SHIFT LOG. | Portal yes; first hall still cropped. |
| `W01_ENTRY_CORNER.png` | Stub | major | Clear opening, dado, `UNBOUND CONNECTOR`. Threshold/sill and uncropped identity still absent. | Hole yes; parked-open hardware partial. |
| `C02_HERO.png` | Shell / riser | major | Bolted waterbox cover held. Shell faceting. Riser is a cream slab, not a bellows read from the hero. | Distinctive condenser still incomplete at hall scale. |
| `C03_REVERSE.png` | Drop / tubes | major | Globe on the drop; two grey tubes on the hotwell. Gauge stem is a black stick. Drop still does not enter a nozzle. | Level “glasses” are not glass. |
| `C06_COOLING.png` | Pads | major | Isolators on the run held. Hex plugs, not bolt-ring blinds. Hangers do not land. | Local CW language still thin. |
| `W04_NE.png` | Tan floor | major | Two legends, one inverted, stacked on the same paint. | Dual-facing is crude and fights itself. |
| `W02_SW_TURN.png` | Floor under CD-01 | major | Bundle text still backwards from this side. | SW approach still wrong. |
| `C09_ROOF.png` | Entire frame | major | Blown grate close-up. No hole, fan, or slab. | Roof camera fails. |
| `C10_MATERIALS.png` | Coupling | — | Cage and hubs held. | Motor still box fins, not a grille. |
| `W07_EAST_PULL.png` | East floor | — | Tan reserve, trench, caged pump, sump pad held. | Pull lane exists. |
| `W08_GALLERY_TURN.png` | Grate / deck | major | `1.5 m` label; deck sliver. Still mostly underside. | Not a standing gallery turn. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C07_OPERATOR.png` | Lamp | minute | Shade sits on the first bezel. | Control is unreadable. |
| `W06_WEST_AISLE.png` | Signs | minute | `CSB-01 TURBINE CONDENSER BAY` and SHIFT LOG readable. Stick rail. | Wayfinding works. |
| `W03_NW.png` | Black loop | minute | Pair and cages visible; loop dominates. | Hall exists; composition cluttered. |
| `C05_RETURN.png` | CEP ID | minute | Foreground volute has no readable plate in this crop. | Identity leans on other views. |
| Cold vs warm | All 18 | minute | Hash DIFF, visual match. | Honest TAA; not a copy. |

---

## R13 blockers — pixel verdict (R14 only)

| R13 blocker | R14 pixels |
|---|---|
| U04 labeled grate-hole, not a neck | **Partial.** Cream duct into stacked frames is now in C04. Flange, gasket, bolt circle, slab jamb still unseen. C09 is worse. |
| C07 cube switches | **Partial.** Round bezels exist. Still faceted discs; lamp collision. |
| C05 motors-only | **Partial.** Hotwell and suction elbow in frame. Takeoff does not close; handoff stub gone from W05. |
| Gallery standing missing | **Partial.** C08 has rail/fan/grate/hoist. Camera is on the rail; W08 still a grate. |
| No cold | **Addressed.** 18/18 cold, hashes differ, visual match. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- U04 **flange, gasket, bolt circle, slab seal** (nested frames are not that)
- **`IF_CONDENSATE_HANDOFF`** as a labeled routed stub (absent in this set)
- D01 **threshold/sill** and uncropped portal identity
- Level glasses as **glass**
- Closed hotwell **nozzle**
- Gallery **standing turn** (W08)
- Roof as a **slab system** (C09)
- Numerical clearances
- CW far-side cap as a bolt-ring blind (unbound correctly not a facility loop)

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **86** | **REJECT** | D01 hole, CW header, CEP cages, pull, gallery tokens, C04 neck start, cold set. U04 mating face, handoff stub, C09, D01 sill still missing. |
| 2. scale/layout | **86** | **REJECT** | Human hall, stairs, 3.5 m floor. Gallery still chunky. Desk toy. |
| 3. machinery logic | **83** | **REJECT** | Suction implied; isolators on the run. U04 not sealed; drop unclosed; handoff gone; level tubes opaque. |
| 4. circulation/readability | **85** | **REJECT** | W01 through-portal, W04/W07 pull, C08 rail. W05 empty wall. W08 grate. Dual legend fights itself. |
| 5. construction/detail | **82** | **REJECT** | Neck frames, bezels, gallery rail. Floating hangers, stick stairs, 2D fan, unclosed drop. |
| 6. materials | **80** | **REJECT** | Cold exists. C10 hubs. Level tubes not glass. Even sheen. |
| 7. lighting | **78** | **REJECT** | Cold exists. C04/C09 blown. No teal. |
| 8. palette | **87** | **REJECT** | Ivory / charcoal / oxide / yellow. Strongest; still ≤90. |
| 9. storytelling | **80** | **REJECT** | SHIFT LOG, mug, book, extinguisher, cone, unbound. Dual legend is a mess. |
| 10. Valorant/reference fidelity | **77** | **REJECT** | Pumps rhyme with cooling. Panel, fan, stairs, nested-frame “bellows” do not rhyme with turbine C02. Q14 is **no**. |

**Unverified:** U04 mating flange/seal; condensate handoff stub; D01 sill; glass level columns; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R14 files for the same defects.

1. **C04** of the neck **landing**: gasket, bolt circle, slab opening as a rectangle — not nested frames over a grate.
2. **C09** of the roof as a system (hole, fan, slab), not a blown bar crop.
3. **C05** where the suction enters a nozzle; keep hotwell and CEP.
4. A view of **`IF_CONDENSATE_HANDOFF`** as a labeled stub (W05 must also be an SE hall).
5. **W08** standing on the deck looking at rail + hole, not the grate underside.
6. **C07** without the lamp eating a switch; bezels that read as industrial rotaries.
7. **C06** hangers that land.
8. **C03** level columns that read as glass.

This reviewer will not prescribe meshes or coordinates.

---

**REJECT** — R14 is not accepted for the defined local condenser-bay scope.
