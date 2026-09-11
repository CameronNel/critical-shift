# Independent Luna pixel review — Medical/Reanimation M01

Reviewer: Luna (independent)

Reviewed the fourteen actual M01 Blender images in `production/renders/review/M01`: ten fixed room cameras (`CAM_*`) and four workflow cameras (`W01_ENTRY_OUTSIDE`, `W02_CART`, `W03_SUPPLIES`, `W04_REAR_SERVICE`). Compared against the approved M03 whole-room guidance and M04 OCRU assembly guidance, the inherited R09 layout, and the strict Valorant-influenced target with no teal/cyan.

This is a pixel review. Rendered pixels support visual observations only. Geometry validation, collision/navmesh, support-contact tests, host-hook behavior, interaction state, and cold-reopen evidence are treated as unverified where they are not visible in the images.

## Decision

**M01 scene: FAIL.** The scene is a materially improved neutral-palette pass, but it does not meet the strict greater-than-90 gate. The strongest pass is color discipline; shape, materials, lighting, hierarchy, environmental storytelling, and technical proof remain below threshold. The room reads as a clean blockout with useful station labels and props rather than the fully constructed Valorant-style employee recovery room shown by M03/M04.

## Category scores

| Category | Score /100 | Gate |
|---|---:|---|
| Scale / circulation | 78 | **FAIL** |
| Shape / art direction | 70 | **FAIL** |
| Hierarchy / gameplay readability | 76 | **FAIL** |
| Materials | 69 | **FAIL** |
| Lighting | 73 | **FAIL** |
| Color discipline / no-teal | 95 | Pass |
| Environmental storytelling | 75 | **FAIL** |
| Technical correctness / evidence | 58 | **FAIL / unverified** |

Strict gate result: **FAIL**. Every relevant category must be strictly greater than 90; the color pass cannot compensate for the other failures.

## Pixel evidence by category

### Scale / circulation — 78

The wide entry and route views read as an adult-scale room with a broad central apron, a full-size recovery cot, a plausible wheeled cart, and a chamber opening large enough to suggest an adult berth. W01 establishes the entry threshold and W02 shows a complete cart with casters and a supported deck. W03/W04 establish usable work surfaces and a service wall.

The pixels do not yet prove the intended retrieve → decon → load route. CAM_ENTRY and CAM_ROUTE contain no staged body cart, the cart view is isolated from the chamber, and there is no loaded ragdoll or obstruction test. The R09 cart parking and east-bypass intent is therefore not visually demonstrated. Recovery transfer and clearance around the rear service band remain uncertain.

### Shape / art direction — 70

M01 is more readable than R09 and uses a neutral shell, but repeated softened rectangular slabs still dominate. The OCRU interior is a plain box with a berth; its shutter/gasket, transfer bridge, adjustable cradle, service coupling, guarded release, cartridge receiver, and removable service panel from M04 are not all visible as distinct constructed assemblies. The console is a board with three block buttons. The recovery cot, supply bench, cabinet, and decon fixtures rely on the same simplified box vocabulary.

M03/M04 show the needed target: layered manufactured panels, specific rails, supported hardware, controlled seams, and deliberate functional silhouettes. M01 has not translated enough of that construction language into the actual scene. CAM_HERO and CAM_PINCH are especially clear that the chamber remains an under-detailed enclosure.

### Hierarchy / gameplay readability — 76

The room has a recognizable sequence: OCRU left, restart center, cartridges and decon at rear, supplies/recovery right. CAM_ENTRY and CAM_ROUTE are understandable at a glance, and CAM_CONSOLE makes the monitor state and button cluster easy to find.

Value grouping is too uniform. Cream equipment, pale walls, and pale floor flatten the room; the OCRU is not separated strongly enough from the rear process wall; and the large `RESTART STATION` sign carries more visual weight than the actual controls. Small console labels and the cartridge/supply details disappear in wide views. The scene needs a stronger hero machine and clearer secondary/quiet zones.

### Materials — 69

M01 introduces bone/graphite separation, dark rubber-like hose and pad elements, glass in the cabinet, and a few metal-looking gauges/rails. CAM_MATERIALS is useful evidence that reserve hardware is no longer the same cyan/grey box as R09.

The dominant response remains smooth cream satin across walls, equipment, recovery furniture, floor, and console. Painted metal, concrete, rubber, glass, and fabric are not consistently distinguishable. CAM_RECOVERY is almost entirely bone plastic/paint and reads as a hospital slab; CAM_DECON is a single pale enclosure with a dark grate; CAM_W03 supplies are uniform pale boxes. M03’s quieter broad surfaces and M04’s material-family separation are not yet present at scene quality. There is too little localized wear and too much generic bevel softness.

### Lighting — 73

Warm practicals are visible, contact shadows generally anchor furniture, and the OCRU has neutral task lighting. W01, CAM_ENTRY, and CAM_REVERSE show useful room depth from ceiling beams and local wall fixtures. There is no teal/cyan light wash.

Most of the room is still evenly exposed with broad cream fill. CAM_ENTRY and CAM_ROUTE lack a convincing focal pool on the OCRU; CAM_DECON and CAM_RECOVERY are flat and low in separation; CAM_CONSOLE is readable but lit like a product close-up. The scene needs stronger practical falloff, darker secondary bands, and clearer local contrast while retaining gameplay readability.

### Color discipline / no-teal — 95

M01 obeys the strongest user override: no visible teal or cyan in the room, chamber, monitors, or practicals. The neutral bone/graphite base and limited oxide-orange controls/straps read as a disciplined palette. Orange is concentrated on interaction hardware and small safety cues rather than flooding the room.

The score is below 100 because the orange accents are sparse and the broad neutral grouping is too cream-heavy to create the graphic separation shown in M03. This is the only category that clears the strict gate.

### Environmental storytelling — 75

The scene includes several useful props: labelled cartridge rows, reserve gauge and handle, shift log, supplies boxes, a sink, recovery cot, decon shower/grate, cart, stool, and status screens. CAM_CONSOLE and W04 communicate that the room is an operating work area rather than an empty shell.

The chapter 5 sequence is still a lineup of labeled stations rather than a visibly connected procedure. CAM_ENTRY has no cart in the arrival/parking read; CAM_DECON is a dry empty stall without a clear contamination-handling story; the OCRU has no visible subject-transfer bridge; the console controls have unclear physical semantics; and recovery is presented as a clean medical bed without fabric, used PPE, or localized worker evidence. The giant `RESTART STATION`/`CARTRIDGES` labels compensate for weak visual storytelling.

### Technical correctness / evidence — 58

The fourteen renders are present at consistent resolution and the objects generally sit on the floor without obvious catastrophic floating or clipping. W01 proves an exterior-facing entry view; W02/W03/W04 add workflow coverage; text is mostly forward-facing and readable in close cameras.

The images do not prove collision, adult/cart obstruction behavior, navmesh, support chains under physics, transfer clearance, host ownership, explicit host hooks, or interaction state transitions. The render manifest proves image production, not those behaviors. Geometry validation is pending and no technical pass is claimed. Visible technical defects include small/ambiguous control labels, broad unverified clearances, a dry decon with no visible drain/waste state, and no loaded-body test.

## View-by-view pixel scores

These are overall view-read scores for the individual images, not substitutes for the eight-category gate.

| View | Score /100 | Pixel read and limiting defect |
|---|---:|---|
| CAM_ENTRY | 78 | Good complete-room orientation and central apron; OCRU, console, decon, cabinet, and recovery all present. No visible cart/body; pale values flatten hierarchy and the OCRU still reads as a boxy shell. |
| CAM_REVERSE | 76 | Entry doors, OCRU side, east work area, and open floor read. Rear-facing composition is quiet and under-detailed; no route/transfer proof. |
| CAM_ROUTE | 78 | Best process-wall overview: console, cartridge rack, decon, supplies, and recovery are legible. Stations remain a row of pale boxes and the arrival cart is absent. |
| CAM_HERO | 74 | Adult berth and chamber volume are clear, with side service cue and rails. Interior construction lacks M04 shutter/bridge/receiver detail and is visually flat. |
| CAM_CONSOLE | 81 | Monitor state and physical buttons are findable. Button labels are tiny/unclear and the controls read as simple blocks on a white desk under product lighting. |
| CAM_DECON | 67 | Shower, hose, grate, and threshold are visible. Stall is empty and dry, with weak contamination/waste story and little material separation. |
| CAM_MAINT | 68 | Hose and cabinet edge establish a service corner. It does not show a distinct OCRU maintenance hatch or a convincing repair access state. |
| CAM_MATERIALS | 72 | Reserve gauge, handle, graphite/cream contrast, and fasteners read. The cabinet remains a softly beveled painted box; concrete, metal, and rubber separation is weak. |
| CAM_PINCH | 76 | Berth is continuous, adult-length, and supported; pads/straps are visible. Pillow and slab are generic and the chamber walls have little construction detail. |
| CAM_RECOVERY | 65 | Cot, pad, rails, and floor contact are visible. The all-bone slab reads hospital/morgue-like and lacks fabric, worker-use evidence, or a transfer relationship. |
| W01_ENTRY_OUTSIDE | 82 | Useful doorway-to-room composition with OCRU, process wall, decon, cabinet, recovery, and central route. It still reads as a clean blockout and does not show the cart parking state. |
| W02_CART | 74 | Complete wheeled stretcher/cart with casters, scissor support, deck pads, and handles. It is isolated against a wall; no chamber alignment, loaded subject, or route behavior is visible. |
| W03_SUPPLIES | 73 | Sink, bench, shift log, and three storage cases give human-use context. Props are uniform pale boxes and the shot lacks material/lighting variation. |
| W04_REAR_SERVICE | 80 | Cartridge labels, shelf structure, glazed supply cabinet, decon opening, and console edge make rear service legible. The power/reserve interface and maintenance access are not shown; surfaces remain boxy and pale. |

No individual view clears a 90 visual-read threshold, and no view proves runtime/physics behavior.

## Prioritized corrections

1. **Translate M04’s OCRU assembly language into the actual scene.** Make the access shutter/gasket, supported berth, folding transfer bridge and cart interface, suit-service coupling, capped cartridge receiver, guarded release, and service panel read as distinct constructed parts. Preserve the inherited envelope and berth orientation.

2. **Break the uniform cream/satin material read.** Establish clear painted metal, graphite, concrete/plaster, black rubber, glass, and fabric families with broad controlled response. Reduce generic bevel softness and add localized wear only at handles, cart routes, kick plates, and service contact points.

3. **Rebuild the visual hierarchy through light and value.** Give the OCRU a controlled hero pool with neutral task light; use warmer practical pools on the console/decon/recovery; let secondary wall zones fall darker; retain readable contacts and no teal/cyan.

4. **Make the chapter 5 procedure visible as a connected operation.** The fixed-camera pack needs readable arrival/cart staging, decon handling, chamber transfer, suit service, cartridge insertion, reserve/mains choice, physical restart, monitored cycle, and recovery. Use existing room placement and verify the route under a body/cart obstruction.

5. **Replace label dependence with specific interaction forms.** Refine the restart controls and monitor hierarchy so the guarded physical sequence reads without oversized signage. Keep canonical `Organic Continuity and Recommissioning Unit (OCRU)` naming and remove generated filler text.

6. **Correct decon/recovery storytelling.** Add visible but restrained contamination-control/waste evidence and a real recovery-work surface with fabric, used PPE, and localized shift evidence. Keep the room industrial and maintained rather than a luxury hospital or morgue.

7. **Complete technical proof after the visual pass.** Run and record adult/cart obstruction, transfer clearance, support/contact, navmesh, interaction-state, host-hook, and fresh-process cold-reopen checks. These are currently unverified by the pixels.

## Final review status

M01 is rejected at the strict scene gate. M03 remains the approved overall concept guidance and M04 remains approved OCRU assembly guidance. The actual scene needs a structural construction/material/lighting pass before another independent eight-category score; routine approval is not implied by the concept approvals.

