# Condenser Bay R15 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R15 (new images; R13/R14 scores not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm, 1920×1080 EEVEE, opened and close-cropped — all 18 under `production/renders/review/R15/`.

Cold-open: all 18 under `production/renders/review/cold-R15/`. SHA256 differs on every pair vs warm. Visual match on C01, C04, C05, C07, C08 (TAA only). **Cold complete for this revision.**

Hashes vs R14: all 18 **NEW-VS-R14** (re-rendered, not a file copy). Composition on most cameras is still the R14 language.

Documents: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R15), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`.

Continuity: turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R15 vs R14 (observed):** W05 again shows a `TO TURBINE U02` collar on a ceiling stub. C09 is a second neck/frame view instead of a blown grate crop. Cold still complete. That is a narrow cycle. **Not a pass.**

---

## Three most consequential defects

### 1. U04 is still nested frames over a grate, not a flange/gasket/seal

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04/C09: cream rectangular duct into stacked grey/black frames; grate visible **inside** the duct; blown specular. No gasket ring, no bolt circle on the slab, no 2.5×1.5 jamb. W08: grate underside, deck sliver, no `1.5 m` this time. |
| Severity | **blocker** |
| Observed mismatch | Picture-frame stack is not a bellows convolution landing on a sealed slab opening. C09 duplicates C04 instead of showing a roof system. |
| Practical/art consequence | Contract row 1 remains incomplete. |

### 2. C05 suction still does not close; W05 is a ceiling stub, not an SE hall

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `W05_SE.png` |
| Visible location | C05: white elbow from under the hotwell to the pump; vertical drop with a globe still ends in a grey ring, not a vessel nozzle. Level “glasses” remain opaque tubes with cube caps. W05: looking up at a collar labeled `TO TURBINE U02` on an empty plane — stub is back, hall is not. |
| Severity | **blocker** |
| Observed mismatch | Handoff is a labeled penetration, not a routed line in a readable room. Takeoff from the shell is still unclosed. |
| Practical/art consequence | Row 2 is implied. W05 fails circulation. |

### 3. C07 / C06 hangers / stairs / fan remain primitives

| Field | Content |
|---|---|
| Image name | `C07_OPERATOR.png`, `C06_COOLING.png`, `C08_MAINT.png`, `W02_SW_TURN.png` |
| Visible location | C07: faceted beige discs; lamp eats the first switch. C06: hanger rods and discs that do not land on the ceiling. C08: concentric-circle “fan”; yellow T-hoist. W02: charcoal stair mass, stick rails. |
| Severity | **major** (clustered: fidelity shortfall) |
| Observed mismatch | Unchanged vs R14. Cooling C05 and turbine C02 are still a different language. |
| Practical/art consequence | Construction and Valorant/reference fidelity stay below 91. Q14 is **no**. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `W05_SE.png` | Ceiling collar | — | **Progress:** `TO TURBINE U02` is in the set again. | Stub exists; camera is not an SE hall. |
| `C09_ROOF.png` | Neck | — | **Progress vs R14:** not a blown bar crop. | Duplicates C04; roof as a system still missing. |
| `C01_ENTRY.png` | D01 jamb | major | Jamb in frame. Right third blank. | Portal yes; first hall cropped. |
| `W01_ENTRY_CORNER.png` | Stub | major | `UNBOUND CONNECTOR`, dado. No sill, no uncropped identity. | Hole yes; parked-open hardware partial. |
| `C02_HERO.png` | Shell | major | Bolted waterbox held. Faceted shell. Riser is a cream slab. | Hall-scale condenser still incomplete. |
| `C03_REVERSE.png` | Drop / tubes | major | Globe on drop; opaque tubes. Drop does not enter a nozzle. | Level columns are not glass. |
| `C06_COOLING.png` | Pads / hangers | major | Isolators on the run held. Hex plugs, not bolt-ring blinds. Hangers float. | CW language still thin. |
| `W04_NE.png` | Tan floor | major | Dual legends, one inverted, stacked. | Crude two-way paint. |
| `W08_GALLERY_TURN.png` | Grate | major | Deck sliver only. | Not a standing turn. |
| `C08_MAINT.png` | Rail | major | Rail/grate/fan/hoist in one jammed frame. | Standing-ish, not a walk. |
| `C10_MATERIALS.png` | Motor | major | Cage/hubs held. Box fins, not a grille. | Short of cooling P-01. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C07_OPERATOR.png` | Lamp | minute | Shade on first bezel. | Control unreadable. |
| `W06_WEST_AISLE.png` | Signs | minute | CSB-01 and SHIFT LOG readable. Stick rail. | Wayfinding works. |
| `W03_NW.png` | Black loop | minute | Pair visible; loop dominates. | Hall exists. |
| `W02_SW_TURN.png` | Floor | minute | Bundle text backwards from this side. | SW approach still wrong. |
| Cold vs warm | C01/C04/C05/C07/C08 | minute | Hash DIFF, visual match. | Honest TAA. |

---

## R14 blockers — pixel verdict (R15 only)

| R14 blocker | R15 pixels |
|---|---|
| U04 nested frames, not flange/gasket/seal | **Not addressed.** C04/C09 still the frame stack over a grate. |
| W05 empty wall; handoff stub gone | **Partial.** Stub returned. W05 is still a ceiling crop, not an SE hall. |
| C05 suction not entering a nozzle | **Not addressed.** White elbow from under the box; vertical drop still a grey ring. |
| C07 toy; C06 hangers; stairs/fan primitives | **Not addressed.** |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- U04 **flange, gasket, bolt circle, slab seal**
- D01 **threshold/sill** and uncropped identity
- Level glasses as **glass**
- Closed hotwell **nozzle** on the drop
- Gallery **standing turn** (W08)
- Roof as a **slab system** (C09 duplicates C04)
- SE **hall** (W05 is a stub crop)
- Numerical clearances
- Handoff as a **routed line** in a readable room (collar only)

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **87** | **REJECT** | U02 stub back. U04 mating face, D01 sill, glass levels, roof system still missing. |
| 2. scale/layout | **86** | **REJECT** | Human hall, 3.5 m floor. Gallery chunky. Desk toy. |
| 3. machinery logic | **83** | **REJECT** | Elbow implied; drop unclosed; U04 not sealed; levels opaque. |
| 4. circulation/readability | **85** | **REJECT** | W01 through-portal, W04/W07 pull. W05 ceiling. W08 grate. Dual legend fights itself. |
| 5. construction/detail | **82** | **REJECT** | Same hangers, stick stairs, 2D fan, unclosed drop, nested frames. |
| 6. materials | **80** | **REJECT** | Cold exists. C10 hubs. Level tubes not glass. Even sheen. |
| 7. lighting | **79** | **REJECT** | Cold exists. C04/C09 still blown on frames. No teal. |
| 8. palette | **87** | **REJECT** | Ivory / charcoal / oxide / yellow. Strongest; still ≤90. |
| 9. storytelling | **80** | **REJECT** | SHIFT LOG, mug, book, unbound, U02 label. Dual legend mess. |
| 10. Valorant/reference fidelity | **77** | **REJECT** | Pumps rhyme with cooling. Panel, fan, stairs, frame-stack “bellows” do not. Q14 is **no**. |

**Unverified:** U04 mating flange/seal; D01 sill; glass levels; closed nozzle; gallery standing turn; roof system; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images

Do not resubmit these R15 files for the same defects.

1. **C04** of the neck **landing**: gasket, bolt circle, slab rectangle — not nested frames over a grate.
2. **C09** of roof as a system, not a second C04.
3. **C05** where the drop enters a nozzle.
4. **W05** as an SE hall **and** a readable handoff line (not only a ceiling collar).
5. **W08** standing on the deck.
6. **C07** without the lamp eating a switch.
7. **C06** hangers that land.
8. **C03** level columns that read as glass.

This reviewer will not prescribe meshes.

---

**REJECT** — R15 is not accepted for the defined local condenser-bay scope.
