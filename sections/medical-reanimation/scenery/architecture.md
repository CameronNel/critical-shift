# Organic Continuity and Recommissioning Unit — architecture

Revision R01, 9 September 2026. Original section design. GAME_SPEC specifies the reanimation procedure, not this room's dimensions; values below are implementation decisions. Equipment is fictional game art, not medical guidance.

Companion files: [floorplan.svg](floorplan.svg), [interface.json](interface.json). Neither file certifies rendered quality or engine behaviour.

Canonical sources read from `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/`: GAME_SPEC.md chapters 5 and 23, ART_DIRECTION.md, ART_REFERENCE_INDEX.md, AUTONOMOUS_SECTION_BUILD_PROTOCOL.md. Run constraints: `ops/facility-run/BUILD_BRIEF.md`, `briefs/medical-reanimation.md`. Visual calibration: approved reactor generated plates `reference-a02-hall.png` / `reference-b01-controls.png` (material and lighting principles only) and user med-bay plates `art/reference/med-bay/front.png` / `back.png` (layout language, not a trace).

## Coordinate and envelope

Metres. Clear main entry threshold is `(0, 0, 0)`; +Y inward; +Z up. Bounds below are usable interior lining faces. Wall thickness 0.18 m is additional and must be checked in Blender.

| Element | Exact dimensions / bounds |
|---|---|
| Main hall | x = −4.00…4.00, y = 0.00…9.00, z = 0.00…3.60; **8.00 × 9.00 × 3.60 m** |
| Decon alcove | x = 1.48…3.18, y = 9.00…11.12, z = 0.00…2.55; **1.70 × 2.12 × 2.55 m** |
| Gross interior floor area | 8.00 × 9.00 + 1.70 × 2.12 = **75.604 m²** |
| Main portal | x = −1.10…1.10 at y = 0.00; clear **2.20 × 2.50 m**; sliding leaves, no swing into the arrival lane |
| Decon threshold | x = 1.55…2.75 at y = 9.00; clear **1.20 × 2.15 m**; open framed stall |

The entry is the only exterior pedestrian portal. The alcove is inside this module. Global adjacency remains unresolved; GAME_SPEC §23.1 sequence does not place this room.

## Functional arrangement

The visible process is arrival → gross decontamination → chamber loading → suit-service hookup → power / cartridge / physical restart → monitored cycle → recovery.

| Function | Floorplan allocation | Construction intent |
|---|---|---|
| Arrival / airlock | Portal at origin; grated threshold y = 0.00…0.45 | Heavy sliding personnel door, viewing slits, pressure frame, L3-01 identity |
| Cart parking | x = −3.82…−2.42, y = 0.18…2.48 | One 2.10 × 0.74 m cart parks longitudinally without occupying the west face of the OCRU |
| OCRU T-01 | x = −3.9575…−1.46, y = 2.48…6.78, z to 2.55 | West-lining machine; adult berth 0.88 × 2.20 m at z = 1.02; opening faces +X; constructed jambs, rails, pads, suit-service hoses |
| Operator console | x = −1.34…0.52, y = 8.10…9.00 | Flush to rear wall; dual diagnostic screens, guarded restart, drawers, stool |
| Cartridge bank | x = 0.64…1.36, y = 8.30…9.00 | Vertical insertion cabinet, four labelled rows, restock drawer |
| Reserve battery | x = −2.58…−1.72, y = 8.44…9.00, z to 1.18 | Floor cabinet west of the console, flush to Y = 9.00 |
| Decon stall | alcove bounds above | Tile, floor grate, shower, yellow waste, bottle shelf |
| Power interface | panel x = 3.18…3.72, y = 8.86…9.00 | MAINS / RESERVE / ISOLATE lamps and guarded switch |
| Recovery | x = 2.58…3.88, y = 3.52…5.88 | Small gurney, wheels, pad, towel; foot toward −Y |
| Supply bench | x = 3.08…3.9575, y = 0.42…2.52 | East worktop, drawers, stool, paperwork |
| Wash | x = 3.42…3.9575, y = 2.62…3.28 | Small basin on east lining near arrival |
| Supplies cabinet | x = 3.22…3.9575, y = 6.52…8.42 | Glazed wall cabinet, bottles, metal boxes |

The OCRU frame, berth, opening, seals, service coupling, cartridge receiver, restart controls and maintenance panels must read as different constructed parts.

## Circulation and obstruction

| Reserved path | Allocation | Nominal clear width |
|---|---|---|
| Arrival | x = −1.10…1.10, y = 0.00…3.20 | 2.20 m |
| West machine face | x = −1.46…−0.40, y = 2.50…7.20 | 1.06 m |
| East bypass | x = 1.55…2.55, y = 2.60…8.20 | 1.00 m |
| Rear service | x = −1.60…3.10, y = 7.85…8.95 | 1.10 m along Y |

A dropped adult footprint 1.80 × 0.70 m at (0.00, 1.90) and a transverse cart 2.10 × 0.74 m at (0.00, 2.90) occupy the arrival centre while leaving the east bypass and the OCRU loading mouth reachable from inside the room. A cart jammed in the single doorway still blocks exterior access and must be dragged; that is accepted. Restart, cartridge and maintenance interactions stay reachable from the rear service band.

## Visual decisions

Neutral graphite / bone painted equipment, not teal machines or cream rooms. Warm practical ceiling light; cyan confined to the OCRU interior and diagnostic screens. Yellow is hazard language only. Black rubber hoses and pads. Glass with thickness. Fabric on the recovery towel. Restrained original bureaucratic copy (LIFE REBUILDS VALUE, FIT PEOPLE / SAFER SITES). Original triangle facility mark; do not reproduce protected logos from reference plates. Wear is local to handles, cart routes and kick plates.

## Spec traceability

| Source | Architectural response |
|---|---|
| GAME_SPEC §5.2 | Arrival lane and obstruction overlays |
| §5.3 | Canonical OCRU identity |
| §5.4 steps 1–4 | Entry, decon stall, loading mouth, adult berth |
| §5.4 steps 5–9 | Suit-service, power, cartridges, physical restart, monitors |
| §5.5 | Reserve battery and consumable storage |
| §5.6 | Maintenance hatch and status surfaces |
| §5.7 | Small recovery position |
| §23.2 / §23.4 | Modest modular envelope, local origin, portal metadata |
| ART_DIRECTION | Specific construction, tactile materials, practical lighting, negative space in the apron |
