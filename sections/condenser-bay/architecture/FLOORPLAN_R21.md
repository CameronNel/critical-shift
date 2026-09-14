# Condenser Bay dimensioned floorplan

Implementation decision by the condenser-bay builder, 2026-09-11. Not a user-approved engineering rating and not a certified drawing. Saved Blender geometry is the evidence; this sheet is the design intent used to author it.

## Frame

| Item | Value |
|---|---|
| Local origin | D01 service threshold centre, finished bay floor |
| Axes | +Y inward, +Z up, +X right |
| Origin in turbine-local | `(1.6, 7.4, −6.0)` m |
| Transform | `turbine = local + origin_in_turbine` |

## Room

| | |
|---|---|
| Clear plan | x −1.80 … 9.60 (11.40 m), y 0 … 9.40 (9.40 m) |
| Clear height | 6.00 m |
| Wall thickness | 0.28 m |
| Why this size | CD-01 body 3.70 × 2.45 m under the 2.5 × 1.5 m U04 opening, 2.4 m west operator aisle, 3.5 m east bundle reserve, south stair strip that does not block D01, 2.4 m headroom in aisles, neck reaching the turbine slab |

## Interfaces

| ID | Local centre | Section / note |
|---|---|---|
| D01 / `IF_PORTAL_D01_SERVICE` | (0, 0, 0) outward −Y | 2.0 × 2.4 m, leaves parked open. Unbound remote connector. |
| U04 receive / `IF_LP_EXHAUST_CONDENSER` | (3.00, 4.05, 6.00) | Maps to turbine (4.60, 11.45, 0). 2.5 m X × 1.5 m Y from accepted aperture audit. |
| `IF_CONDENSATE_HANDOFF` | (7.90, 0.00, 5.42) | Local stub toward turbine U02. **Do not remove the turbine-owned cap.** Integrator must continue the 0.2 m line to turbine (9.5, 0, 0.45). |
| `IF_CW_SUPPLY` / `IF_CW_RETURN` | (9.60, 3.20, 3.15) / (9.60, 4.90, 3.15) | Capped wall flanges. Not a proven cooling-plant loop. |
| `IF_DRAIN_OUT` / `IF_VENT_OUT` | east/north walls | Unbound. |

## Equipment footprints (local)

- **CD-01** centre (3.00, 4.05, 3.15): oval shell along X, steam chest and bellows neck to U04, hotwell, east/west waterboxes, piers.
- **CEP-A / CEP-B** (2.35, 7.05) / (4.05, 8.20): condensate extraction, suction from hotwell, discharge to U02 handoff.
- **EJ-01** (−0.55, 7.55): two-stage air ejector, air offtake from shell.
- **OP** west wall at y 4.05: vacuum / level / CW / CEP controls.
- **Bundle reserve** x 6.20 … 9.45, y 1.20 … 7.20, marked 3.5 m clear.
- **Stairs** south strip x 2.15 … 6.20, y 0.18 … 1.12, then north to gallery z 4.18.

Drawing: `architecture/floorplan.svg`.
