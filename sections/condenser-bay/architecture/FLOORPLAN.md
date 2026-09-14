# Condenser Bay dimensioned floorplan

Grok R21 layout, continued by Astra on 2026-09-12. Original text/drawing are preserved as FLOORPLAN_R21.md and floorplan_R21.svg. This describes the local scenic geometry and disclosed integration limits, not certified engineering.

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
| Why this size | CD-01 body 3.70 × 2.45 m under the 2.5 × 1.5 m U04 opening, west operator/service space, east service reserve, south stair strip preserving D01 access, and neck reaching the turbine slab. Saved audits sample 2.2 m floor routes and approximately 2.0 m gallery/stair standing height; broad planning zones are not certified clear volumes. |

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
- **Bundle service reserve** x 6.20 … 9.45, y 1.20 … 7.20: 3.25 m × 6.00 m nominal staging zone. Sampled standing access is documented separately; these bounds do not certify a full bundle extraction sweep or removal animation.
- **Stairs** first flight x 2.15 … 5.05, y 0.18 … 1.12; intermediate landing extends x 5.05 … 6.36 at z 2.07. Second flight centres x 5.90 (0.88 m tread width), y 1.12 … 3.95, reaching gallery datum z 3.90. Gallery walking surface is approximately z 3.94. The original z 4.18 platform had inadequate standing headroom and centerline hangers. One original interfering column moved to (6.65, 1.25) under the existing south girder.
- **Gallery** east x 5.45 … 6.35, y 3.95 … 6.295; north x 0.60 … 5.45, y 5.395 … 6.295; west x −0.30 … 0.60, y 1.805 … 6.295. Real open bearing bars; edge suspension; connected stair rails. West strip moved 0.40 m outward to clear waterbox at the repaired lower level.
- **Cart delivery** measured 0.80 × 2.20 × 1.60 m volume, centre x 0.05, travels straight from D01 to centre y 5.10 and reverses to exit. No unverified 90° cart turn is claimed. Broad aisle bounds include equipment and are not wholly clear.
- **Suction service** pump suction routes run in cut local floor trenches with flush covers. Motor cables descend beside their skids and continue below the floor. These do not bind remote utilities.
- **U04 joint** open 2.5 × 1.5 m throat, exposed lower/upper bolting plates at z 5.755 / 5.825 with gasket at 5.790; transition collar reaches the original slab opening. No neighbor cap or slab was edited.

Saved geometry checks and their limits are recorded per revision in production/validation. A PASS in one diagnostic scope is not full visual acceptance.

Drawing: `architecture/floorplan.svg`.
