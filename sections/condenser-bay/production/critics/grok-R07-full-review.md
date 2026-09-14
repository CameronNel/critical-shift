# Condenser Bay R07 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R07 (new images; R02 22–61 and R04 47–73 are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

C01_ENTRY, C02_HERO, C03_REVERSE, C04_EXHAUST, C05_RETURN, C06_COOLING, C07_OPERATOR, C08_MAINT, C09_ROOF, C10_MATERIALS, W01_ENTRY_CORNER, W02_SW_TURN, W03_NW, W04_NE, W05_SE, W06_WEST_AISLE, W07_EAST_PULL, W08_GALLERY_TURN — `production/renders/review/R07/`.

Partial cold: `production/renders/review/cold-R07/` contains **only** C01, C02, C04, C07, W01. Those five visually match the warm frames. The other thirteen cameras have **no** cold-open. Full cold-open is **UNVERIFIED**.

Documents read, not scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R07), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, warm and cold `render_manifest.json`.

Continuity (inspected): turbine R07 `C02_hero.png`; cooling `C02_HERO.png`, `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R07 vs R04 (observed, not gifted):** W01 now looks at a D01 assembly. C01 is a wider 18 mm hall into CD-01 with cart, EJ-01, and ceiling fixtures. C03’s hanging pipe now shows an end cap. C07 mug is a cylinder. C08 is slightly off the fascia. That is a real cycle. It is **not** a pass. CPU “0 cameras within 0.35 m” is not a composition or contract proof.

---

## Three most consequential defects

### 1. `U04` receive is still not in the pixels

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png` (checklist); `C08_MAINT.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: gallery steel, a light bar, a cream fascia — no 2.5 × 1.5 m slab hole, neck, bellows, flange, or seal. C08: underside of a cream box and black beams. C09: a blank grey wall, a yellow stick, a hoist-hook sliver. W08: jammed into a beam knuckle. |
| Severity | **blocker** |
| Observed mismatch | The bay exists to receive turbine `IF_LP_EXHAUST_CONDENSER`. C04 is still not an exhaust camera; it is a steel close-up. Cold C04 is the same image. |
| Practical/art consequence | Coverage and machinery **cannot pass**. A clear ray through empty space is not a visible receive. |

### 2. Process hardware is still greybox: hollow nozzle, orange cubes, stick coupling

| Field | Content |
|---|---|
| Image name | `C02_HERO.png`, `C06_COOLING.png`, `C10_MATERIALS.png`, `C07_OPERATOR.png` |
| Visible location | C02 waterbox: white pipe meets a disc; the tube is **hollow and open** (interior of the cut is visible). C06: same disc-and-pipe, scattered bolts, hanging ring, blown highlight. C10: yellow dowels between orange disc and motor; box fins; `CEP A` plate. C07: analog needles exist; guards are beige U-brackets; tiny desk. |
| Severity | **blocker** |
| Observed mismatch | Hard gates: disconnected service; generic bevelled-box language; primitive controls. Cooling `C05_PUMP_A` still shows a flange ring, a yellow **cage**, a finned can, a readable ID. This bay does not. C03’s cap is a local fix; the waterbox nozzle is not. |
| Practical/art consequence | Exhaust → CW → condensate cannot be read. Valorant/reference fidelity cannot meet neighbor continuity. |

### 3. Checklist cameras for CW, gallery, pull, and roof still fail

| Field | Content |
|---|---|
| Image name | `C06_COOLING.png`, `W07_EAST_PULL.png`, `C08_MAINT.png`, `W08_GALLERY_TURN.png`, `C09_ROOF.png` |
| Visible location | C06/W07: worm’s-eye of the east orange cube. C08/W08: beam/fascia crops. C09: empty wall. |
| Severity | **blocker** |
| Observed mismatch | No capped `IF_CW_SUPPLY`/`IF_CW_RETURN` wall flanges. No standing gallery of neck access. No 3.5 m pull-bay keep-clear as a readable lane. No ceiling hole. |
| Practical/art consequence | Rows 3, 4, and 7 of the checklist are unproven. Relabeling these files is not a fix. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `W01_ENTRY_CORNER.png` | D01 centre field | major | A D01 **assembly** is finally in frame (orange side pockets, frame, extinguisher). The centre reads as a **solid charcoal slab**, not a traversable 2.0 × 2.4 opening with a visible threshold/floor. Sign cropped to `B-01`. | Access is photographed, not proven open. Contract “parked-open leaves” is not evidenced. |
| `C01_ENTRY.png` | Behind camera | major | 18 mm shows the hall, CD-01, cart, EJ-01. D01 itself is not in this entry frame. | C01 still does not do the portal job; W01 must carry it and currently does not prove clear. |
| `W06_WEST_AISLE.png` | Wall card | major | `SHIFT LOG` still mirrored (`GOL TFIHS`). Unfixed since R02. | Dressing remains unreadable. |
| `W04_NE.png` | Tan floor | major | `3.5 m BUNDLE` still mirrored. | Pull instruction faces the wrong approach. |
| `C05_RETURN.png` | Foreground volute | major | One orange disc fills the lens. Pair, hotwell takeoff, level glasses, `IF_CONDENSATE_HANDOFF` are not in this checklist view. (W03/W05 show two pumps.) | Return row is only partly covered by other cameras. |
| `C03_REVERSE.png` | Mid-right pipe | major | End now has a **cap disc** (R04 dead-end improved). Pipe still hangs in air in front of the shell with no nozzle into the vessel. Black cage rods still scratch the shell. | Cap ≠ connection. Process still decorative. |
| `W02_SW_TURN.png` | Stair | major | Charcoal stringer; yellow sticks not a continuous handrail. | Maintenance climb still blockout. |
| `W03_NW.png` | Pumps / TOOLS | major | Pair visible; overhead line now ends in a cap. Volutes remain lollipops. `TOOLS` is a blank slab. | Best process view; still generic. |
| `W05_SE.png` | Under gallery | major | Useful hall: piers, drip pad, two motors, wall fan. Soffit is an unarticulated black slab. | Architecture is a lid. |
| `C08_MAINT.png` | Cream box under beams | major | A rectangular chest is glimpsed. No bellows, no U04, no standing deck. | Not a maintenance view. |
| `C10_MATERIALS.png` | Coupling | major | Yellow sticks, faceted hub, orange field still ~40% of frame. | Material family not proven. |
| *set* | Full cold-open | blocker | 5 / 18 cameras only. | Cold stability **UNVERIFIED** for the review set. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` | Cart / EJ-01 | minute | Cart with boxes, `EJ-01` cans, floor scuff, ceiling LEDs. Honest `SCENIC / NO RATING` plate. | Story tokens exist; they do not raise construction. |
| `C07_OPERATOR.png` | Mug | minute | Cylinder mug replaces the R04 cube. Needles and FLOW/CW IN/LEVEL/VAC are legible. Header still cropped `CSB-01 CON…`. | Station is identifiable, still toy. |
| `W01_ENTRY_CORNER.png` | Extinguisher | minute | Red cylinder at the jamb. | Good token; portal still unproven. |
| `C06_COOLING.png` | High-left gauge | minute | A clock-face exists on a pipe. | Not a CW header story. |
| `W04_NE.png` | Distant small board | minute | Second FLOW/LEVEL/VAC board across the hall. | Duplicate unexplained. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- **Full cold-open** of all 18 cameras (five exist and match; thirteen do not exist)
- **U04** 2.5 × 1.5 m opening, neck exterior, flange, seal
- **D01** as a **clear** parked-open opening with threshold (assembly is shown; traversal is not)
- Capped **CW** wall flanges and isolators at service distance
- **`IF_CONDENSATE_HANDOFF`** stub
- Hotwell **level glasses**
- Gallery **standing** view
- 3.5 m pull keep-clear from a camera that is not under the waterbox
- Numerical clearances / cart envelope
- Material close-up that can tell steel / cast / rubber / concrete apart

U02 cap not removed and CW provisional: accepted as documentation, not as an excuse for missing local sockets in the frames that claim them.

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior revision numbers are not copied.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **63** | **REJECT** | Hall, CD-01, CEP pair, EJ, OP, cart, D01 assembly now visible. U04, CW caps, handoff, gallery/roof hole still unproven. Partial cold. |
| 2. scale/layout | **73** | **REJECT** | C01/W03–W05 show a human-scale hall. Gallery is a chunk; desk is toy; pull/D01 clear unproven. |
| 3. machinery logic | **55** | **REJECT** | One pipe capped. Waterbox nozzle still hollow. U04 unseen. Pumps are discs. No readable exhaust→CW→extract chain. |
| 4. circulation/readability | **72** | **REJECT** | Walk set exists. D01 is photographed as a slab, not a clear. W07/W08 fail. Floor legend mirrored. |
| 5. construction/detail | **52** | **REJECT** | Orange cubes, sparse bolts, stick coupling, stick rails, box chest, hanging ring. Neighbor flange/pedestal language unmet. |
| 6. materials | **58** | **REJECT (cold incomplete)** | Less foam than R02; orange still plastic. C10 is dowels + volute. Five cold frames match; thirteen missing. |
| 7. lighting | **62** | **REJECT (cold incomplete)** | C01 practicals work. C06 blown. C04/C09 are compositionally dark/empty. No teal. |
| 8. palette | **74** | **REJECT** | Ivory / charcoal / oxide / yellow; no teal. Orange still wraps waterboxes and volutes. Strongest category; still ≤90. |
| 9. storytelling | **55** | **REJECT** | Cart, mug, extinguisher, cone, tools slab. Shift log still backwards. Sterile plus tokens. |
| 10. Valorant/reference fidelity | **48** | **REJECT** | Versus turbine C02 and cooling C02/C05 this is a cheaper language. ART_DIRECTION Q14 is **no**. |

**Unverified blockers even if scores were higher:** full cold-open; U04 receive; D01 clear opening; CW caps; condensate handoff; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R07 files for the same defects.

1. **C04** of the **exterior** U04 opening (hole, neck, flange/seal/slab) — not gallery steel.
2. **C08 / W08** standing on the gallery: deck, rail, neck.
3. **C09** of the actual ceiling hole and services.
4. **C06 / W07** of capped east-wall CW flanges, isolators, hoist, and pull-bay floor at readable distance.
5. **C02 / C06** in which the waterbox pipe is a closed, flanged connection — the hollow cut must be gone in pixels.
6. **W01** that proves a **clear** opening and threshold, not a charcoal slab; identity sign uncropped.
7. **C05** with both CEPs, hotwell takeoff, and the handoff stub.
8. **C10** that can tell materials apart.
9. **W06** shift-log facing the aisle; **W04** bundle legend facing the approach.
10. **Cold-open of all 18** cameras with honest comparison.

This reviewer will not prescribe meshes or coordinates.

---

**REJECT** — R07 is not accepted for the defined local condenser-bay scope.
