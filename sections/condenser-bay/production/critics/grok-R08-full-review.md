# Condenser Bay R08 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R08 (new images; R02 22–61, R04 47–73, R07 48–74 are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

C01_ENTRY, C02_HERO, C03_REVERSE, C04_EXHAUST, C05_RETURN, C06_COOLING, C07_OPERATOR, C08_MAINT, C09_ROOF, C10_MATERIALS, W01_ENTRY_CORNER, W02_SW_TURN, W03_NW, W04_NE, W05_SE, W06_WEST_AISLE, W07_EAST_PULL, W08_GALLERY_TURN — `production/renders/review/R08/`.

**R08 cold-open:** none. Only `review/cold-R07/` exists (five cameras). R08 cold is **UNVERIFIED**.

Documents read, not scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R08), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, `render_manifest.json`.

Continuity (inspected): turbine R07 `C02_hero.png`; cooling `C02_HERO.png`, `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R08 vs R07 (observed, not gifted):** W01 now looks **through** D01 into an owned stub with floor, walls, dado, and `UNBOUND CONNECTOR`. C06 now shows labeled east-wall `CW SUPPLY` / `CW RET…` sockets. C04 and C09 are still steel/fascia crops, not U04. Most other cameras keep the R07 compositions and the same defects. That is a real, narrow cycle. It is **not** a pass.

---

## Three most consequential defects

### 1. `U04` receive is still not in the pixels

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`; `C08_MAINT.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: cream fascia and grey gallery beams, a yellow rail sliver — no 2.5 × 1.5 m slab hole, neck, bellows, flange, or seal. C08: underside of a cream box and black steel. C09: looking up at gallery plates, a hoist hook, and the orange waterbox — still no opening. W08: jammed into a beam knuckle. |
| Severity | **blocker** |
| Observed mismatch | The bay exists to receive turbine `IF_LP_EXHAUST_CONDENSER`. C04 remains a steel close-up. C09 was reframed and still does not show the hole. |
| Practical/art consequence | Coverage and machinery **cannot pass**. |

### 2. Process hardware is still greybox: hollow nozzle, orange cubes, stick coupling

| Field | Content |
|---|---|
| Image name | `C02_HERO.png`, `W07_EAST_PULL.png`, `C10_MATERIALS.png`, `C07_OPERATOR.png` |
| Visible location | C02: white pipe at the waterbox disc is still **cut open** — the hollow interior of the tube is visible. W07: same disc, sparse cube-bolts, hanging ring, blown highlight. C10: yellow dowels between orange disc and motor. C07: analog needles exist; guards are beige U-brackets on a tiny desk. |
| Severity | **blocker** |
| Observed mismatch | Hard gates: disconnected service; generic bevelled-box language; primitive controls. Cooling `C05_PUMP_A` still shows a flange ring, a yellow **cage**, a finned can. This bay does not. |
| Practical/art consequence | Exhaust → CW → condensate cannot be read as specific machinery. Fidelity cannot meet neighbor continuity. |

### 3. Gallery, pull, roof, and isolators still fail their cameras

| Field | Content |
|---|---|
| Image name | `C08_MAINT.png`, `W08_GALLERY_TURN.png`, `W07_EAST_PULL.png`, `C06_COOLING.png` |
| Visible location | C08/W08: fascia/beam crops, not a standing gallery. W07: worm’s-eye of the east cube, not a 3.5 m keep-clear. C06: wall sockets exist, but a yellow wheel sits around a **floating grey cylinder** with no valve body to the pipe; `CW RET` is cropped; camera is under the headers. |
| Severity | **blocker** |
| Observed mismatch | Rows 3–4 and 7 still lack a readable pull lane, gallery deck, roof hole, and serviceable isolators. C06 is a real add; it is not a finished CW story. |
| Practical/art consequence | Maintenance and cooling-water contract remain unproven as operable hardware. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `W01_ENTRY_CORNER.png` | Through D01 | — | **Observed progress:** clear opening, stub floor, dado, `UNBOUND CONNECTOR`, orange side leaves, extinguisher. | Portal is no longer a charcoal slab. |
| `W01_ENTRY_CORNER.png` | Jamb / sign | major | Identity cropped to `B-01`. Threshold/sill not in frame. Leaves are orange pads in pockets, not a full sliding-leaf read. | Opening is proven; 2.0 × 2.4 parked-open hardware is only partial. |
| `C01_ENTRY.png` | Hall | major | Same 18 mm into CD-01 as R07. D01 is behind the camera. Cart, EJ-01, ceiling LEDs visible. | Entry still does not include the portal; W01 must carry it. |
| `C06_COOLING.png` | Wall collars | major | Pipes meet circular pads and vanish into the wall. No bolt ring, no blind cap on this face. Isolator wheel is a torus on a can, unconnected to the run. | Sockets are labeled, not flanged/capped hardware. Unbound far side **UNVERIFIED** (correctly not a facility loop). |
| `C03_REVERSE.png` | Mid-right pipe | major | End cap disc present. Pipe still hangs in air in front of the shell. Black rods scratch the tank. | Cap ≠ nozzle. |
| `C05_RETURN.png` | Foreground volute | major | One orange disc. Pair / hotwell / level glasses / `IF_CONDENSATE_HANDOFF` not in this checklist view. | Return row still leans on W03/W05. |
| `W06_WEST_AISLE.png` | Wall card | major | `SHIFT LOG` still mirrored (`GOL TFIHS`). Unfixed since R02. | Dressing unreadable. |
| `W04_NE.png` | Tan floor | major | `3.5 m BUNDLE` still mirrored. | Pull legend faces the wrong approach. |
| `W02_SW_TURN.png` | Stair | major | Charcoal stringer; yellow sticks, not a continuous handrail. | Climb still blockout. |
| `W03_NW.png` / `W05_SE.png` | Pumps / soffit | major | Pair visible; volutes are lollipops; `TOOLS` is a blank slab; gallery soffit is an unarticulated lid. | Best hall views; still generic. |
| `C10_MATERIALS.png` | Coupling | major | Yellow sticks, faceted hub, orange field ~40% of frame. | Material family not proven. |
| *set* | R08 cold-open | blocker | Zero R08 cold cameras. | Cold stability **UNVERIFIED**. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` | Cart / `EJ-01` / `SCENIC / NO RATING` | minute | Tokens and honest non-rating plate. | Do not raise construction. |
| `C07_OPERATOR.png` | Mug / gauges | minute | Cylinder mug; FLOW/CW IN/LEVEL/VAC readable. Header cropped `CSB-01 CON…`. | Station identifiable, still toy. |
| `C09_ROOF.png` | Hoist hook | minute | Yellow hoist fragment exists. | Does not show U04. |
| `W04_NE.png` | Distant small board | minute | Second FLOW/LEVEL/VAC board. | Duplicate unexplained. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- **R08 cold-open** of all 18 cameras
- **U04** 2.5 × 1.5 m opening, neck exterior, flange, seal
- D01 **threshold/sill** and uncropped identity
- CW **blind caps / bolt rings** and isolators that actually sit on the pipe
- **`IF_CONDENSATE_HANDOFF`** stub
- Hotwell **level glasses**
- Gallery **standing** view
- 3.5 m pull keep-clear from a camera that is not under the waterbox
- Numerical clearances / cart envelope
- Material close-up that can tell steel / cast / rubber / concrete apart

U02 cap not removed and CW provisional: accepted as documentation.

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **67** | **REJECT** | D01 opening and labeled CW sockets now exist. U04, handoff, gallery/roof hole, isolator hardware still unproven. No R08 cold. |
| 2. scale/layout | **74** | **REJECT** | Hall remains human-scale. Portal is now a visible stub. Gallery chunk, toy desk, pull bay unseen. |
| 3. machinery logic | **58** | **REJECT** | CW wall runs help. Hollow waterbox nozzle, hanging pipe, disc pumps, missing U04. |
| 4. circulation/readability | **76** | **REJECT** | W01 is a real clear. Walk set exists. W07/W08 fail. Floor legend mirrored. |
| 5. construction/detail | **53** | **REJECT** | Orange cubes, sparse bolts, stick coupling, floating isolator, box chest. Neighbor flange language unmet. |
| 6. materials | **58** | **REJECT (cold UNVERIFIED)** | Plastic orange; C10 is dowels. No R08 cold. |
| 7. lighting | **63** | **REJECT (cold UNVERIFIED)** | C01 practicals; C06 contact shadows; C04/C09 empty/steel. No teal. |
| 8. palette | **75** | **REJECT** | Ivory / charcoal / oxide / yellow; no teal. Orange still wraps waterboxes and volutes. Strongest category; still ≤90. |
| 9. storytelling | **56** | **REJECT** | Honest unbound lettering, cart, mug, extinguisher. Shift log still backwards. |
| 10. Valorant/reference fidelity | **49** | **REJECT** | Versus turbine C02 and cooling C02/C05 this is still a cheaper language. ART_DIRECTION Q14 is **no**. |

**Unverified blockers even if scores were higher:** R08 cold-open; U04 receive; CW cap/isolator construction; condensate handoff; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R08 files for the same defects.

1. **C04 / C09** of the **exterior** U04 opening (hole, neck, flange/seal/slab).
2. **C08 / W08** standing on the gallery: deck, rail, neck.
3. **C02 / W07** in which the waterbox pipe is a closed flanged connection — hollow cut gone.
4. **C06** at service distance: bolt-ring or blind cap, isolators on the pipe, uncropped labels, pull-bay floor in the same readable set.
5. **C05** with both CEPs, hotwell takeoff, and the handoff stub.
6. **C10** that can tell materials apart.
7. **W06** shift-log facing the aisle; **W04** bundle legend facing the approach.
8. **W01** with threshold/sill and uncropped identity if claiming parked-open hardware complete.
9. **Cold-open of all 18** R08 cameras.

This reviewer will not prescribe meshes or coordinates.

---

**REJECT** — R08 is not accepted for the defined local condenser-bay scope.
