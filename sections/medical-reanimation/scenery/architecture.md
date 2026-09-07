# Medical and reanimation architecture

Revision P01, 8 September 2026. Original section design for the Organic Continuity and Recommissioning Unit (OCRU). Dimensions below are authored implementation decisions because GAME_SPEC specifies the process and modularity, not this room's dimensions. This is fictional industrial game equipment.

The companion [floorplan.svg](floorplan.svg) is a dimensioned, original vector drawing. [interface.json](interface.json) records the same local geometry and unresolved facility connections. Neither document establishes rendered quality, engine functionality, or acceptance.

## Coordinate and envelope contract

Metres throughout. The clear main entry threshold is `(0, 0, 0)`; +Y points inward and +Z points up. Bounds describe usable interior wall faces; wall thickness is additional and must be checked in the Blender source.

| Element | Exact dimensions / bounds |
|---|---|
| Main room | x = −4.00…4.00, y = 0.00…9.00, z = 0.00…3.60; 8.00 × 9.00 m |
| Recovery alcove | x = 4.00…6.20, y = 4.60…8.40, z = 0.00…3.15; 2.20 × 3.80 m |
| Gross interior floor area | 8.00 × 9.00 + 2.20 × 3.80 = **80.36 m²**; before equipment deductions, excluding walls |
| Main exterior portal | x = −1.10…1.10 at y = 0.00; clear width 2.20 m, clear height 2.50 m |
| Entry mechanism | Sliding leaves with travel along X; no swing envelope in the arrival route |
| Alcove connection | Open side at x = 4.00, y = 4.60…8.40; width along Y 3.80 m, clear height 3.15 m |

The entry is the only exterior pedestrian portal. The alcove opening connects two spaces within this module. Rear-wall power, low-voltage, water and drain interfaces are utility termination allowances, not new doors or claims of connections to other departments. Global placement, neighbouring section identity, walking times and final utility sizes remain unresolved. GAME_SPEC §23.1's conceptual facility sequence does not determine a physical adjacency here.

## Functional arrangement

| Function | Floorplan allocation | Construction / use intent |
|---|---|---|
| Arrival and gross decontamination | Main-room band y = 0.00…2.60 | Flush transition and washdown-capable threshold; avoid a raised trip edge |
| Wash fixture | Nominal planned bay x = −3.85…−2.95, y = 1.00…2.50 | West-side wash station beside the arrival area; rear water and drain termination points reserved. Authored basin outer bounds are x = −3.89…−2.91, y = 1.06…2.24 |
| Cart parking | x = −3.70…−2.50, y = 3.10…5.50 | One 2.00 × 0.75 m cart can park longitudinally without occupying the west bypass |
| OCRU assembly | Centre (0.55, 6.20); outer x = −0.35…1.45, y = 4.55…7.85 | 1.80 × 3.30 m machine envelope, maximum opened-canopy height 2.40 m |
| Adult berth | 0.88 × 2.15 m, surface z = 0.78 | Centred at (0.55, 6.20); visibly supported berth, chamber opening, suit-service coupling and moving access parts |
| Operator controls | x = −1.35…−0.75, y = 5.80…6.60 | West-facing working side; nominal hand-control height z = 1.10 m; physical restart and readable monitoring |
| Cartridge interaction | West machine side at y = 5.00 | Accessible insertion, cartridge stock and spent-item handling; keep hoses out of bypass |
| Consumable storage | West wall, y = 6.70…8.60 | Shared service/storage bay; shallow allowance x = −3.85…−2.95, excluding the dedicated battery sub-bay; no continuous cabinet may overlap the battery |
| Reserve battery cabinet | x = −3.90…−3.35, y = 7.55…8.55, z = 0.00…1.25 | Floor cabinet in the west service/storage bay; remains west of rear maintenance circulation |
| Reserve-power / restart interface | Rear wall, x = −2.80…−1.50 | Flush supply connection and status; preserve the rear maintenance band |
| Recovery bed | x = 4.70…5.65, y = 5.55…7.75 | 0.95 × 2.20 m, pillow toward +Y; short recovery position after recommissioning |

The OCRU's frame, patient support, opening canopy, seals, service coupling, cartridge receiver, controls and maintenance panels should read as different constructed parts. The visible process is arrival → contamination removal → chamber loading → suit connection → power/cartridge/restart → vulnerable monitored cycle → recovery. The recovery alcove has a lower ceiling and quieter furnishing hierarchy, keeping the main machine dominant.

The wash fixture bay is a nominal planning allowance, not the final asset bounding box. The authored basin extends 0.04 m beyond both planned X edges, while remaining within the planned Y span and outside reserved essential routes. Final geometry handoff must record the complete fixture extents; the nominal floorplan rectangle alone does not certify them.

## Circulation and obstruction limits

| Reserved path | Exact allocation | Nominal clear width |
|---|---|---|
| Arrival | x = −1.10…1.10, y = 0.00…4.30 | 2.20 m |
| West personnel bypass | x = −2.50…−1.45, y = 2.60…8.00 | 1.05 m |
| East bypass | x = 1.70…3.80, y = 2.60…8.00 | 2.10 m |
| Rear maintenance | x = −2.50…3.80, y = 8.00…8.95 | 0.95 m along Y |

The arrival lane and both bypasses connect through the open apron in front of the machine and the rear maintenance band. The west lane is a personnel path, not a promise that a body on a cart can turn there. The east path is the preferred internal recovery bypass. Bed access on the alcove's west side is 0.70 m from the open partition line to the bed; the bed's rear and front margins within the alcove are 0.65 m and 0.95 m. These are planned geometric allowances and require verification against the final objects.

The optional `obstruction-test` SVG layer shows two static diagnostic positions after the threshold: a dropped body footprint 1.80 × 0.70 m centred at (0.00, 1.90), bounds x = −0.90…0.90 and y = 1.55…2.25; and a transverse cart footprint 2.00 × 0.75 m centred at (0.00, 2.90), bounds x = −1.00…1.00 and y = 2.525…3.275. These positions support individual and combined tests. They deliberately obstruct central movement while remaining outside the east bypass and the canonical loading destination (0.55, 4.00). The layer is explanatory and is not evidence of simulated collisions. It does not prove that every obstruction placement preserves access. A transverse cart in the single doorway can block exterior access, and an obstruction at the loading destination can prevent chamber loading; both require physically clearing or dragging the obstruction. Personnel already inside may use the internal bypass where the actual obstruction permits it.

Engine integration must test actual ragdoll extents, cart swept volume and turning, grabbing/dragging, chamber loading, door trapping and network ownership. Clearance drawings cannot prove those behaviours. Avoid claiming that ragdoll or cart physics is solved. Maintain reachable restart, cartridge and manual maintenance interactions in blocked-arrival tests.

The rear service band is especially sensitive: equipment projected forward beyond y = 8.95 intrudes into its nominal 0.95 m clearance. The rear battery/restart supply interface is flush; its cabinet is separately located in the west service/storage bay at x = −3.90…−3.35, y = 7.55…8.55, top z = 1.25. That cabinet stays west of the rear route's x = −2.50 boundary. Shelf, door and cable extents must be checked before acceptance.

## Spec traceability

| Source | Architectural response | Remaining runtime responsibility |
|---|---|---|
| GAME_SPEC §5.2 | Body/cart arrival and obstruction test overlays | Shutdown ragdoll and dropped items |
| §5.3 | Canonical OCRU identity | Machine identity and interaction target |
| §5.4 steps 1–4 | Entry, gross-decon fixture, clear loading approach and adult berth | Retrieval, decontamination and body placement |
| §5.4 steps 5–9 | Suit-service coupling, power interface, cartridge receiver, physical restart controls and monitor | Resource use, physical sequence and vulnerable cycle |
| §5.5 | Reserve-power interface and restrained consumable storage | Battery depletion, facility power effects and costs |
| §5.6 | Rear maintenance access and local state/status surfaces | Recoverable pause, repair, remote lock and incorrect identity states |
| §5.7 | Small recovery alcove | Temporary impairment and return to play |
| §23.2 | Modest 80.36 m² interior module | Facility placement and actual travel-time measurement |
| §23.4 | Local origin, portal/utility metadata and named functional spaces | Collision, navigation, spawn markers, incident hooks, audio and network boundaries |
| ART_DIRECTION §§3–8, 10–11, 16–20 | Specific construction, human dimensions, tactile materials, localized practical lighting, sparse paperwork and clear space | Pixel review from fixed gameplay cameras |

Canonical sources were read from `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/`: `GAME_SPEC.md` chapters 5 and 23, `ART_DIRECTION.md`, `ART_REFERENCE_INDEX.md`, and `AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`. Run constraints came from `C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md`, `briefs/medical-reanimation.md`, and `README.md`.

## Visual decisions

Use warm institutional wall fields, desaturated teal/green painted machinery, matte dark rubber, limited exposed steel, glass with visible thickness and fabric on the recovery bed. Amber safety accents identify access and restart controls; colour is supplemented by shape and text. A practical light should establish the chamber as the visual focus, with softer threshold fill and a quieter alcove. Cluster service details and paperwork around working points, leave circulation visually quiet, and localize wear to handles, cart contact and floor routes. Keep original bureaucratic text brief, such as “Continuity receipt / return copy” on a small local form. Avoid luxurious hospital furnishings, horror dressing, decorative neon, universal gloss, and repeated boxes disguised by labels.
