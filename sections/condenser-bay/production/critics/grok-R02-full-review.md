# Condenser Bay R02 full review

**Reviewer identity:** independent grok-4.6 critic subagent  
**Not:** Luna. Neighbor acceptances do not transfer.  
**Date:** 2026-09-11  
**Revision:** R02  
**Disposition:** **REJECT**

## Evidence inspected (pixels, not builder claims)

Warm renders, all 1920×1080 EEVEE, ray tracing off, opened and close-cropped:

- `production/renders/review/R02/C01_ENTRY.png`
- `production/renders/review/R02/C02_HERO.png`
- `production/renders/review/R02/C03_REVERSE.png`
- `production/renders/review/R02/C04_EXHAUST.png`
- `production/renders/review/R02/C05_RETURN.png`
- `production/renders/review/R02/C06_COOLING.png`
- `production/renders/review/R02/C07_OPERATOR.png`
- `production/renders/review/R02/C08_MAINT.png`
- `production/renders/review/R02/C09_ROOF.png`
- `production/renders/review/R02/C10_MATERIALS.png`

Documents read, not treated as scenery proof: `architecture/FLOORPLAN.md`, `production/CHECKLIST.md`, `production/CAMERAS.md`, `interface.json`, `production/RUBRIC.md`, `production/renders/review/R02/render_manifest.json`, `production/validation/R02-validation.json`.

Continuity comparison (inspected): turbine R07 `C02_hero.png`; cooling-plant `C02_HERO.png`, `C05_PUMP_A.png`.

**Not in this batch:** W01–W08 player-height views. **No cold-open set.** Builder support audit reports 13 failed ceiling/hanger anchors (`gap: 99`); that is corroboration only, and it does not replace missing faces.

**Scope:** this module and documented boundaries (`U04` receive, local condensate handoff, provisional CW sockets). Not turbine hall, not Cooling Plant, not whole-map assembly.

---

## Three most consequential defects

### 1. The evidence cameras do not show the room

| Field | Content |
|---|---|
| Image name | `C01_ENTRY.png`, `C02_HERO.png`, `C04_EXHAUST.png`, `C08_MAINT.png`, `C10_MATERIALS.png` (and C03/C05/C06 as jammed fragments) |
| Visible location | Entire frames: camera bodies sit against or inside equipment |
| Severity | **blocker** |
| Observed mismatch | C01/C02 are nearly identical worm’s-eye crops of the west waterbox and shell, not D01 threshold or a CD-01 three-quarter in a hall. C04 is mostly black, looking up the interior of a cream cylinder. C08 is a railing jammed into an orange block. C10 is a full-frame orange noise field. Walk cameras were not rendered. |
| Practical/art consequence | Contract items mapped to these cameras are **unproven**. A complete-looking checklist and 936 objects cannot be scored as a room. Relabeling these files would not be a new cycle. |

### 2. Turbine `U04` receive is not evidenced

| Field | Content |
|---|---|
| Image name | `C04_EXHAUST.png`; `C09_ROOF.png` does not rescue it |
| Visible location | C04: cream barrel and a dark rectangular recess above a strap, then unlit void. C09: gallery rail, dark girders, linear fixtures, a distant circular fan — no readable 2.5 × 1.5 m slab opening, neck, bellows, flange, or seal |
| Severity | **blocker** |
| Observed mismatch | The assigned purpose of this module is to receive turbine `IF_LP_EXHAUST_CONDENSER`. These pixels do not show a mating opening, a steam chest that can be read as a connection, or any dimensioned relationship to the turbine slab. The builder’s ray-audit JSON claiming `u04_opening.ok` is not a substitute for a visible receive. |
| Practical/art consequence | The one neighbor obligation that defines this bay remains **UNVERIFIED**. Coverage, machinery logic, and scale cannot pass. |

### 3. Construction language is greybox primitives, far below neighbor/A05 fidelity

| Field | Content |
|---|---|
| Image name | `C02_HERO.png`, `C07_OPERATOR.png`, `C03_REVERSE.png`, `C05_RETURN.png`, `C10_MATERIALS.png` |
| Visible location | Orange waterbox faces; operator panel; north shell pipe; pump volute/motor; material “close-up” |
| Severity | **blocker** |
| Observed mismatch | Waterbox is a large orange box with a handful of scattered cube-bolts and a plain black disc, not a tube-sheet/bolt-ring assembly (cooling `C02_HERO` / `C05_PUMP_A` show what a flange ring and motor actually look like in this facility). Shell shading is faceted. C07 “gauges” are blank leather-textured discs with no glass, ticks, or needles; “switches” are beige cubes on a tiny shelf. C03 white pipe ends in open air. C10 proves only a noisy orange shader. |
| Practical/art consequence | Hard visual vetoes fire: generic bevelled-box language, primitive control panel, faceting, plastic/noise materials. This would not read as the same shipped stylized PC game as turbine R07. |

---

## Further defects (major, then minute)

### Major

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` | Left wall, mid-frame | major | Wall card lettering reads mirrored (`SHIFT LOG` backwards). Paper is a floating rectangle with no pin, tape, or thickness. | Dressing is unreadable; entry still does not show D01. |
| `C01_ENTRY.png` | Underside of cream mass / orange body at left | major | Low-poly faceted orange/cream volumes and black cube feet. No grout, soleplate, or pier that matches turbine pedestals. | Machine does not look built; scale of the “hotwell” is a box on cubes. |
| `C03_REVERSE.png` | Mid-right, white line after the elbow | major | Pipe is an open cylinder hanging in front of the shell. No nozzle, flange, cap, or vessel penetration. | Disconnected service. Process cannot be followed. Hard gate. |
| `C03_REVERSE.png` | Thin black rods over the shell | major | Cage is a few unsupported sticks, not a walkway, ladder, or structured gallery. | Secondary construction is placeholder. |
| `C05_RETURN.png` | Upper-left sign | major | Gold lettering is mirrored (`VACUUM` reversed). Camera is looking at the back of a wall sign. | Return view does not show CEP-A **and** CEP-B, hotwell suction, or the `U02` handoff. |
| `C05_RETURN.png` | Orange hemisphere + grey cylinder | major | One pump volute fills the frame. Motor is a smooth can with a cube box and a stick; no fins, coupling, or yellow guard (cooling `C05_PUMP_A` is the continuity bar). `CEP-A` plate is barely a black tag. | Condensate return equipment is not a readable two-pump system. CEP-B is **UNVERIFIED**. |
| `C06_COOLING.png` | Orange east face, pipes entering from above | major | White pipes meet the waterbox with no flanges; one thin ring; two stray bolts; a black disc. Grey slab eats half the frame. | CW supply/return, isolators, capped `IF_CW_SUPPLY`/`IF_CW_RETURN`, hoist, and 3.5 m pull bay are **not** in this picture. |
| `C06_COOLING.png` | Far left sliver | major | Yellow rail, dark opening, truncated sign `B-01`, orange leaf-like plane. | Stairs/D01/identity are fragments. Cannot score access. |
| `C07_OPERATOR.png` | Four upper discs | major | FLOW / CW IN / LEVEL / VAC labels sit under blank padded circles. No pointers, glass, bezels of industrial character, or readable values. Header `VACUUM / CEP / CW` is cropped and washed. | Operator station fails diegetic information and the ART_DIRECTION primitive-panel veto. CSB-01 identity is not on this panel. |
| `C07_OPERATOR.png` | Shelf | major | Four beige cubes, one red cube, one beige block, a white card. No guarded trip, no analog levers, no enclosure sides in context. | Controls do not read as reachable industrial hardware. Aisle reach is **UNVERIFIED**. |
| `C08_MAINT.png` | Yellow member vs orange block | major | Yellow rail **clips through** the orange mass. Orange shader is glossy brushed-wood grain, not painted steel. | Maintenance/gallery/neck access is unreadable; clipping is a construction fail. |
| `C09_ROOF.png` | Upper volume | major | Dark slab, some linear lights, yellow handrail posts, distant fan disc. U04 hole, steam neck, extract as a system, and ceiling services over the condenser are not shown. | Roof/services camera fails its checklist duty. |
| `C10_MATERIALS.png` | Entire frame | major | Orange procedural mottling only. No motor, coupling, gasket, concrete, rubber, glass, or timber family comparison. | Mandatory material-detail view is empty. Wear/material categories cannot pass. |
| *set* | D01 portal | blocker | No image shows a 2.0 × 2.4 m opening, parked sliding leaves, threshold, or receiving connector. | Access contract is **UNVERIFIED**. Builder `d01_opening.ok` is ignored without pixels. |
| *set* | EJ-01, hoist, sump, level glasses, bundle reserve | blocker | Not identifiable as those objects in this set. Orange cylinder with a white band on C03 floor is a primitive, not a tool story. | Checklist rows 4, 6, 9 are unproven. |
| *set* | Cold reopen | blocker | No cold renders, no comparison JSON. | Cold stability **UNVERIFIED**. |

### Minute (still recorded; they would not save any category)

| Image | Visible location | Severity | Observed mismatch | Consequence |
|---|---|---|---|---|
| `C01_ENTRY.png` / `C02_HERO.png` | Shell lettering `CD-01` | minute | Vertical seam splits the ID; nameplate `CD-01 SURFACE / SCENIC / NO RATING` is the only honest contract note in the set. | ID is present but not a room-scale wayfinding system. |
| `C01_ENTRY.png` | Lower-right floor | minute | Partial yellow legend (bundle reserve) is edge-cropped under the piers. | Painted instruction exists; the reserved volume is unseen. |
| `C06_COOLING.png` | Right wall | minute | Quiet ivory panels and dado are in-family, and a yellow wheel exists in the distance. | A fragment of architecture is competent; it does not prove CW. |
| `C07_OPERATOR.png` | Wall dado | minute | Ivory/charcoal split matches turbine/cooling. | Palette fragment only. |
| `C09_ROOF.png` | Linear fixtures | minute | Lights exist as objects and throw some illumination on a far wall. | Practicals are started; they do not light a readable roof story. |

---

## Missing evidence (`UNVERIFIED` — cannot pass)

Walk/player-height (none rendered): W01 entry corner, W02 SW turn, W03 NW, W04 NE, W05 SE, W06 west aisle, W07 east pull, W08 gallery turn.

Faces/systems not shown in the C-set:

- D01 leaves, jambs, threshold, and the volume behind the door
- Full CD-01 three-quarter in the hall (front **and** side as a room silhouette)
- South reverse wall / return path
- U04 2.5 × 1.5 m opening, bellows/neck, flange, seal, slab underside
- Hotwell, level glasses, CEP-A **and** CEP-B as a pair, suction from hotwell, discharge to `IF_CONDENSATE_HANDOFF`
- CW headers, isolation wheels at service distance, capped east-wall flanges
- Hoist beam, hook, 3.5 m pull hatch as a keep-clear
- Gallery walking surface, stair approach that does not block D01
- EJ-01 as a two-stage ejector
- Drainage trench/sump as equipment, not a floor sliver
- Roof as a complete lid with services
- Material family close-ups (steel / cast / concrete / rubber / glass)
- Numerical clearances, cart envelope, headroom (screenshots cannot prove these anyway)
- Cold-open of the same cameras
- Neighbor bind (correctly **not** claimed in `interface.json`; do not treat local pipes as a cooling-plant loop)

A screenshot cannot prove unseen sides or millimetre clearance. Those items stay failed until **new** views **and** measured audits exist together.

---

## Independent category scores

Pass floor is **> 90**. 90 or below is REJECT. Unverified cannot pass.

| Category | Score /100 | Disposition | Basis |
|---|---:|---|---|
| 1. contract/specification coverage | **41** | **REJECT** | Documents exist. Pixels do not prove D01, U04 receive, two-pump return, CW caps, hoist/pull, gallery, EJ, drainage, or complete architecture. Checklist-to-camera map is false for C01, C04, C05, C06, C08, C09, C10. |
| 2. scale/layout | **34** | **REJECT (UNVERIFIED)** | No readable hall. Operator cubes vs giant orange waterbox. Plan 11.40 × 9.40 × 6.00 m and aisle widths are claims, not seen. |
| 3. machinery logic | **38** | **REJECT** | Exhaust path unreadable. Open-ended pipe. CW pipes enter a box without isolators in frame. Condensate pair/hotwell/`U02` stub not shown. Blank gauges carry no state. |
| 4. circulation/readability | **22** | **REJECT (UNVERIFIED)** | Walk set missing. C01 is not an entry. No keep-clear, no door, no stair-to-gallery path, mirrored/cropped labels. |
| 5. construction/detail | **36** | **REJECT** | Faceted shell, cube bolts, cube switches, stick cage, clipping rail, paper-thin plates, no bolt rings. Builder support audit: 13 hangers/battens miss the slab. |
| 6. materials | **33** | **REJECT** | C10 is orange noise. Gauges read as upholstery. C08 orange reads as glossy timber. Pump volute is foam-grain. Families are not distinguishable. |
| 7. lighting | **47** | **REJECT** | Linear practicals exist (C06/C09). C04 is a black void. No room key/fill hierarchy. Contact shadow on C07 does not save unlit exhaust/roof proof. |
| 8. palette | **61** | **REJECT** | Local swatch is ivory / charcoal / oxide orange / yellow; no teal in these pixels. Orange wraps whole waterboxes and the pump instead of controlled accents. Room-scale blocking **UNVERIFIED**. Strongest category; still ≤90. |
| 9. storytelling | **35** | **REJECT** | Backwards shift log, primitive bollard, empty cube desk. Cart, PPE, extinguisher, tools, service docs claimed in the checklist are not in this set. |
| 10. Valorant/reference fidelity | **29** | **REJECT** | Versus turbine R07 C02 and cooling C02/C05: missing specific silhouettes, secondary construction, tactile metals, composed gameplay cameras. ART_DIRECTION Q14 is **no**. Primitive panel and faceting are immediate vetoes. |

**Any category unverified?** Yes: scale/layout and circulation/readability are unverified from missing room/walk coverage. Palette room-scale grouping, U04 receive, D01, cold-open, and several equipment faces are unverified and already fail their parent categories.

No category exceeds 90. **10 / 10 REJECT.**

---

## Required new images to re-review claimed fixes

Do not resubmit these R02 files. Each claimed fix needs **new** pixels. Minimum:

1. **C01** from the D01 threshold: parked leaves, clear opening, first hall volume, condenser as a distant mass — walls on.
2. **C02** three-quarter of the full CD-01 in the room (shell, both waterboxes, neck toward ceiling, piers, aisle).
3. **C03** from the north at player height: south wall, return path, machine rear/side.
4. **C04** exterior of neck/U04: opening, flange/seal, supports, slab — not the interior of the duct.
5. **C05** both CEPs, hotwell connection, discharge toward the documented handoff, readable IDs.
6. **C06** east waterbox **and** CW isolators **and** capped wall flanges **and** hoist **and** pull-bay floor marks, in one readable composition plus a crop of the caps.
7. **C07** operator station in the west aisle: enclosure, analog (or otherwise specific) instruments, guarded controls, CSB identity, reach space.
8. **C08** gallery standing view: deck, rail, neck access, stair landing — no clipping.
9. **C09** ceiling looking at the actual U04 hole and services.
10. **C10** motor/coupling/gasket/paint/concrete in one frame that can tell materials apart.
11. **W01–W08** as listed in `CAMERAS.md`.
12. Close crops of: D01 reveal, U04 opening, any glass edges, floor/support contacts, labels that were mirrored.
13. **Cold-open** of the same cameras with honest comparison.

Cutaways, if any, must be labelled as cutaways. Player views must keep walls.

This reviewer will not prescribe replacement meshes or coordinates. Camera placement that still sits inside the condenser will fail again on sight.

---

**REJECT** — R02 is not accepted for the defined local condenser-bay scope.
