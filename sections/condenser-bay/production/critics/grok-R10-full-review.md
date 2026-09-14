# Condenser Bay R10 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Turbine R07 / Cooling R10 acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R10 (new images; R02/R04/R07/R08 scores are history, not reused)  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

C01_ENTRY, C02_HERO, C03_REVERSE, C04_EXHAUST, C05_RETURN, C06_COOLING, C07_OPERATOR, C08_MAINT, C09_ROOF, C10_MATERIALS, W01_ENTRY_CORNER, W02_SW_TURN, W03_NW, W04_NE, W05_SE, W06_WEST_AISLE, W07_EAST_PULL, W08_GALLERY_TURN — `production/renders/review/R10/`.

**R10 cold-open:** none. Only `review/cold-R07/` exists. R10 cold is **UNVERIFIED**.

Documents read, not scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `interface.json` (rev R10), `production/RUBRIC.md`, `production/CORRECTION_HISTORY.md`, `render_manifest.json`.

Continuity (inspected): turbine R07 `C02_hero.png`; cooling `C05_PUMP_A.png`.

**Scope:** this module and documented boundaries only.

**R10 vs R08 (observed, not gifted):** C04 is a new south-floor look **along the shell** toward a cream bar and a dark gallery soffit. C05 is a new side-on CEP-A. C06 isolator now has a stem and can. W01 unbound stub and labeled CW sockets remain. Most other cameras keep the prior compositions. That is a narrow cycle. It is **not** a pass. The builder’s own note that C04 is still blocked by the gallery deck matches the pixels.

---

## Three most consequential defects

### 1. `U04` receive is still not in the pixels

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`; `C08_MAINT.png`, `C09_ROOF.png`, `W08_GALLERY_TURN.png` |
| Visible location | C04: `CD-01` shell top, two orange manway rings, a cream rectangular bar, then a **dark gallery deck** filling the upper frame. No 2.5 × 1.5 m slab hole, neck, bellows, flange, or seal. C08/C09/W08 remain steel/fascia crops. |
| Severity | **blocker** |
| Observed mismatch | Checklist camera for the turbine receive still does not show the opening. Looking along the shell is not looking at U04. |
| Practical/art consequence | Coverage and machinery **cannot pass**. |

### 2. Coupling is now the C05 hero — and it is still yellow sticks

| Field | Content |
|---|---|
| Image name | `C05_RETURN.png`, `C10_MATERIALS.png` |
| Visible location | C05: orange volute, grey shaft, **six yellow dowels** as a “guard,” box fins, `CEP A`. Second pump is a crop at the right. C10: same sticks, orange field ~40% of frame. |
| Severity | **blocker** |
| Observed mismatch | Cooling `C05_PUMP_A` is a flange ring, a yellow **cage**, a finned can, a readable ID. This return camera proves the opposite: kitbash sticks. C05 no longer shows hotwell, pair, suction, or `IF_CONDENSATE_HANDOFF`. |
| Practical/art consequence | Construction and fidelity fail in close-up. Checklist row 2 is worse than R08’s wider pump view. |

### 3. Hollow waterbox nozzle, floating isolator, gallery/pull cameras still fail

| Field | Content |
|---|---|
| Image name | `C02_HERO.png`, `C06_COOLING.png`, `C08_MAINT.png`, `W07_EAST_PULL.png`, `W08_GALLERY_TURN.png` |
| Visible location | C02: pipe at the waterbox disc is still **cut open** (hollow interior visible). C06: yellow wheel on a grey can **beside** the Z-bend, not on the run; `CW RET` cropped. C08/W08: fascia. W07: worm’s-eye of the east cube. |
| Severity | **blocker** |
| Observed mismatch | Hard gates: disconnected service; generic boxes; maintenance cameras that do not show a standing gallery or 3.5 m keep-clear. |
| Practical/art consequence | Process and access remain unproven as operable hardware. |

---

## Further defects

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `W01_ENTRY_CORNER.png` | Through D01 | — | **Held from R08:** clear stub, dado, `UNBOUND CONNECTOR`, orange side leaves, extinguisher. | Portal hole remains proven. |
| `W01_ENTRY_CORNER.png` | Jamb / sign | major | Identity cropped to `B-01`. Threshold/sill not in frame. | Parked-open hardware still partial. |
| `C01_ENTRY.png` | Hall | major | Same 18 mm into CD-01. D01 behind camera. Cart, EJ-01, LEDs. | Entry still omits the portal. |
| `C03_REVERSE.png` | Mid-right pipe | major | Cap disc present. Pipe still hangs in air. Black rods scratch the tank. | Cap ≠ nozzle. |
| `C07_OPERATOR.png` | Panel / desk | major | Needles exist. Beige U-brackets, tiny desk, cropped `CSB-01 CON…`. | Toy station. |
| `W06_WEST_AISLE.png` | Wall card | major | `SHIFT LOG` still mirrored. Unfixed since R02. | Dressing unreadable. |
| `W04_NE.png` | Tan floor | major | `3.5 m BUNDLE` still mirrored. | Pull legend faces the wrong approach. |
| `W02_SW_TURN.png` | Stair | major | Yellow sticks, not a continuous handrail. | Climb still blockout. |
| `W03_NW.png` / `W05_SE.png` | Pumps / soffit | major | Pair visible; lollipop volutes; `TOOLS` slab; unarticulated lid. | Best hall views; still generic. |
| `C06_COOLING.png` | Wall collars | major | Pipes vanish into pads. No bolt ring, no blind cap. Isolator is a can in space. | Sockets labeled, not flanged hardware. |
| *set* | R10 cold-open | blocker | Zero R10 cold cameras. | Cold **UNVERIFIED**. |

### Minute

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` | Cart / `EJ-01` / `SCENIC / NO RATING` | minute | Tokens and honest plate. | Do not raise construction. |
| `C05_RETURN.png` | Volute back | minute | Cube bolts exist on the disc. | Not a flange ring. |
| `C04_EXHAUST.png` | Nameplate | minute | `CD-01 SURFACE / SCENIC / NO RATING` readable. | Does not show U04. |
| `C09_ROOF.png` | Hoist hook | minute | Yellow hoist fragment. | Does not show the slab hole. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

- **R10 cold-open** of all 18 cameras
- **U04** 2.5 × 1.5 m opening, neck exterior, flange, seal
- D01 **threshold/sill** and uncropped identity
- CW **blind caps / bolt rings** and isolators **on the pipe**
- **`IF_CONDENSATE_HANDOFF`** stub
- Hotwell **level glasses**
- Gallery **standing** view
- 3.5 m pull keep-clear from a camera that is not under the waterbox
- Numerical clearances
- Material close-up that can tell steel / cast / rubber / concrete apart

---

## Independent category scores

Pass floor **> 90**. Unverified cannot pass. Prior numbers are not copied.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **66** | **REJECT** | D01 stub and CW labels held. U04 still unseen. C05 no longer shows return process. No R10 cold. |
| 2. scale/layout | **74** | **REJECT** | Hall remains human-scale. Gallery chunk, toy desk, pull unseen. |
| 3. machinery logic | **55** | **REJECT** | Hollow nozzle; hanging pipe; stick coupling as the return hero; isolator off the run; U04 missing. |
| 4. circulation/readability | **76** | **REJECT** | W01 clear held. W07/W08 fail. Floor legend mirrored. |
| 5. construction/detail | **51** | **REJECT** | C05 is a stick coupling. Orange cubes, sparse bolts, box chest. Neighbor flange language unmet. |
| 6. materials | **57** | **REJECT (cold UNVERIFIED)** | Plastic orange; C10/C05 are dowels. No R10 cold. |
| 7. lighting | **62** | **REJECT (cold UNVERIFIED)** | C01 practicals; C04 upper frame is a dark slab. No teal. |
| 8. palette | **75** | **REJECT** | Ivory / charcoal / oxide / yellow; no teal. Orange still wraps waterboxes and volutes. Strongest category; still ≤90. |
| 9. storytelling | **56** | **REJECT** | Unbound lettering, cart, mug, extinguisher. Shift log still backwards. |
| 10. Valorant/reference fidelity | **47** | **REJECT** | C05 versus cooling P-01 is a different, cheaper language. ART_DIRECTION Q14 is **no**. |

**Unverified blockers even if scores were higher:** R10 cold-open; U04 receive; CW cap/isolator on pipe; condensate handoff; numerical clearances.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R10 files for the same defects.

1. **C04 / C09** of the **exterior** U04 opening (hole, neck, flange/seal/slab) — not the shell top under a gallery deck.
2. **C05** that shows both CEPs, hotwell takeoff, and the handoff stub — not a stick coupling close-up.
3. **C08 / W08** standing on the gallery.
4. **C02 / W07** with a closed flanged waterbox connection.
5. **C06** at service distance: bolt-ring or blind cap, isolator **on the pipe**, uncropped labels, pull-bay floor.
6. **C10** that can tell materials apart (a cage, not dowels).
7. **W06** shift-log facing the aisle; **W04** bundle legend facing the approach.
8. **Cold-open of all 18** R10 cameras.

This reviewer will not prescribe meshes or coordinates.

---

**REJECT** — R10 is not accepted for the defined local condenser-bay scope.
