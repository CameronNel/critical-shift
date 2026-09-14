# Measured connection contract and topology

All values are metres, Z up. The scene contains empties with the exact CP identifiers in interface.json. Local coordinate origin and transform are unapplied authoring coordinates, not an assembled-map claim.

| Connection | Threshold/position | Normal into destination | Opening | Ownership/status |
|---|---|---|---|---|
| CP-P01 | Cooling(0,0,0) | Cooling+Y |5.0×5.0| Cooling ownsY≥0; reactor owns its existing stubY0..3.7 in reactor portal coordinates |
| Reactor cooling hall portal | Reactor(8.4,-8.4,0) |(.707106781,-.707106781,0)|5.0×5.0 nominal| Reactor-owned |
| Reactor stub outer seam | Reactor(11.0162950904,-11.0162950904,0)|same|5.0×5.0 nominal| Proposed mating seam; saved static doors prevent traversal |
| CP-D02 | Cooling(-4.1,9.9,0)|+Y|1.2×2.2| Cooling internal workshop |
| Fuel F01_REFINERY | Corridor(0,0,0)|outward(0,-1,0)|2.6×3.0| Mates refinery outer sill(8.6066637063,-4.0842831769,0), outward+X; refinery owns1.1m sill |
| Fuel F02_REACTOR | Corridor(14.2,24,0)|outward+Y|5.0×5.0| Mates reactor fuel outer seam(0,14.5,0); reactor owns3.7m stub from(0,10.8,0), static doors remain |
| Fuel S01_PLANT | Corridor(-5.4,17.4,0)|outward-X|2.0×2.5| Reserved shared plant header, no installed Cooling destination |

Proposed coherent topology: refinery dispatch → Fuel Corridor freight route → reactor fuel stub → reactor hall → existing southeast cooling stub → CP-P01 → Cooling central route. CP-D02 branches to the maintenance alcove. A separate future link from S01_PLANT requires a connector-owner decision and assembled footprint checks; this section adds no speculative door or duplicate corridor for it.

Cooling-to-reactor transform: Rz(-135°), t=(11.0162950904,-11.0162950904,0). Map points as p_reactor=R*p_cooling+t. The two5m threshold endpoints become(12.7840620434,-9.2485281374,0) and(9.2485281374,-12.7840620434,0). Finished floors areZ0 with zero step. Reactor link floor's saved local bounds areX[-2.5,2.5],Y[0,3.7000000477],Z[-.319999993,0]. Its closed distant doors occupyY[3.589999914,3.690000057], full5m width/height. Source and saved object measurements agree; the nominal seam rounds their float precision to3.7m. The Cooling footprint lies beyond the stub and does not claim its walls/floor.

Fuel's two published local mating transforms are independent contracts, not a solved global assembly: corridor→refinery Rz(-90°),t=(8.6066637063,-4.0842831769,0); corridor→reactor Rz(180°),t=(14.2,38.5,0). Fuel's freight centerline length is38.2m and its bypass23.4m. Refinery's bollards reduce low-level lateral width to about2.49m; inherited short clearance rays do not prove whole-cart transit. Final assembly must reconcile these transforms rather than force another worker's room to move.

## Local utility sockets

| Identifier | XYZ | Outward normal | Bore/cable diameter |
|---|---|---|---|
| CP-COOL-SUPPLY | [4.99, 0, 3.76] | [0, -1, 0] | 0.3 |
| CP-COOL-RETURN | [-5.03, 0, 3.76] | [0, -1, 0] | 0.32 |
| CP-RESERVE-POWER | [5.27, 0, 3] | [0, -1, 0] | 0.048 |
| CP-PORTABLE-BATTERY | [4.88, 1.9, 1.03] | [-1, 0, 0] | — |
| CP-MINE-WATER | [4.86, 3.15, 0.78] | [-1, 0, 0] | 0.152 |
| CP-SECONDARY-WATER-01 | [5.5, 5.8, 3.0] | [1, 0, 0] | 0.2 |
| CP-SECONDARY-WATER-02 | [5.5, 7.85, 3.3] | [1, 0, 0] | 0.2 |
| CP-DRAIN-OUT | [5.5, 10, -0.1] | [1, 0, 0] | — |

All remote utility endpoints remain unassigned. Local pipe endpoints, water recovery branch, feeder and buried drainage collector exist in the saved scene. Portable battery and backup-water couplings are capped/presentation-ready; functional hose insertion, valve actuation, shared reserve competition, cooling failures and repairs are later engine integration work. No duplicate power reserve is created here.

Read-only survey: production/technical/neighbour-saved-measurements.json records neighbour file hashes before/after, world/object-local bounds, rotations and names. All three files were unchanged by the survey. Current data must be rechecked if neighbouring owners revise their artifacts. Current whole-map turbine fit and shared plant-header destinations are unresolved.
