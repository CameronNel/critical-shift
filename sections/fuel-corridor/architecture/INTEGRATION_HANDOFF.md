# Fuel Corridor integration handoff

Authored section: original freight connector, carrier staging, internal gate, service bypass and three reserved service headers. Strict Valorant direction: off-white mineral panels, charcoal steel and orange markings; no teal. Final F10 passes all 17 independent categories above 90; the exact saved-artifact receipt is production/evidence/final-pass/delivery-receipt.json. See production/FINAL_ACCEPTANCE.md for scores, cold stability and scope.

## Coordinate and connection contract

Metres, +Z up, finished floor Z0. Local origin is F01 outer seam. The combined envelope is22.40 ×24.00m; it is an irregular connected footprint, not a filled rectangle. See the dimensioned A101 SVG/PNG and numeric `interface.json` P07.

| ID | Local seam XYZ | Outward normal | Nominal opening W × H | Ownership / saved state |
|---|---|---|---|---|
| F01 REFINERY | 0,0,0 | 0,−1,0 | 2.60 ×3.00 | Corridor frame/sill and removable presentation leaves; closed. Refinery owns its1.10m sill beyond seam. |
| F02 REACTOR | 14.2,24,0 | 0,1,0 | 5.00 ×5.00 | Corridor frame/sill and removable presentation leaves; closed. Reactor owns3.70m stub and its separate closed doors. |
| S01 PLANT | −5.4,17.4,0 | −1,0,0 | 2.00 ×2.50 | Corridor termination; closed. Shared plant destination adapter unbound. |
| S02 CLEAN | 6.6,21,0 | 0,1,0 | 2.00 ×2.50 | Corridor termination; closed. Medical/compliance destination adapter unbound. |
| S03 WASTE | 16.4,16,0 | 1,0,0 | 2.40 ×3.00 | Corridor termination; closed. Waste destination adapter unbound. |
| FG01 FREIGHT | Internal gate at6.35,10,0 | Internal +X freight axis | 3.40 ×3.40 | Corridor-owned paired sliding leaves; saved open with enclosed storage pockets. |

There are five external door assemblies plus one internal gate: twelve editable leaf carriages. The bypass is an open internal route, not an additional external door.

Local seam mappings use column vectors: `p_neighbor=Rz(angle)*p_corridor+t`. F01 maps into refinery coordinates using−90° and t=(8.606663706334526,−4.084283176858165,0). F02 maps into reactor coordinates using180° and t=(14.2,38.5,0). These are separate local mating equations, not proof that the current independent rooms already occupy compatible global poses. No neighboring section was moved or rebuilt.

## Routes, equipment and operation

Freight centreline: (0,0)→(0,10)→(14.2,10)→(14.2,24),38.20m. Gross freight passages are4.40m, withØ3.00m turn allowances and a6.60 ×6.20m staging bay. The service bypass runs (0,10)→(0,19.2)→(14.2,19.2),23.40m, around FG01. The west leg is2.40m gross; the north leg is3.00m gross. Audited dressed passage targets are2.00m wide and2.20m high. Branch walk-up checks stop at the saved closed leaves.

The original carrier is1.60 ×.90m, parked at(2.65,12.32,0), axis+X. It carries one sealed1.245m ×Ø.340m reactor cartridge with saddles, restraints, latches, eyes, handle, wheels and brakes. Carrier runtime physics and steering are not implemented. The conservative transport allowance is2.20 ×.90m; the service bypass is not the loaded freight route.

The corridor includes a mounted pressure-air station, connected branch feed, capped supply reservations, isolation/distribution boxes, supported cable trays, geared gate drive, practical fixtures, a maintenance bench/toolboard, gloves/cloth, cases, grease/flask, paperwork, first-aid case and permit holders. `SPEC_CONTENTS.md` distinguishes brief requirements from these original implementation choices. Props remain outside the tested circulation envelopes.

The enlarged bypass/plant junction uses a trimmed L-shaped plant slab. The physical floor has no duplicate0.30 ×0.60m finish face at the junction; the union footprint and floor elevation are unchanged. Functional audio/network cells may overlap there.

Rear steel flanges stand4mm proud of the lower lining to avoid coincident finish faces. Sign mounting feet meet the first exposed support face instead of passing through an upright. The service extraction grille is400mm wide, centred at(10.73,21,2.26); the corner lamp is at(−1.5,20.60,2.36). These original fixture choices clear the adjacent sign backs and maintain the tested routes.

## Engine handoff

`scenery/handoff.json` must match the JSON embedded in the delivered scene. It contains collision-source policy, named carriages and their exact member lists, route centrelines, three spawn markers, three incident hooks, audio volumes and network cells. It is authored metadata, not completed engine behavior.

For an owned presentation-cap removal, remove only the specified moving members/carriages. Retain the fixed frame, sill, jambs and rails. Do not remove every object with a boundary prefix and do not remove neighboring doors. FG01 is the internal operational gate, not a disposable section cap. Its39 sampled translated positions retain roller support and show no penetrating mechanical obstruction in the replay; this is finite geometric evidence, not a continuous dynamic simulation or engine controller.

Static evaluated geometry is available for collider cooking; visual decals must not become blocking colliders. The carrier requires an appropriate convex/compound physics representation. Door triggers/controllers, navmesh, collision cooking, audio assets/mix, replication and gameplay handlers remain integration work. The markers are `FC_ENTRY_START`, `FC_EAST_REENTRY`, `FC_SERVICE_RESCUE`; incident hooks are `FC_HOOK_AIR_LEAK`, `FC_HOOK_GATE_JAM`, `FC_HOOK_RESTRAINT`.

## Remaining external uncertainties

- P07 F01/F02 positions remain current-source consistent in Luna's11September check. The current refinery saved artifact differs from the historical spacing050 seam evidence; that older clearance proof is not silently transferred to the new save.
- Reactor's own static fuel closure remains closed. Neither corridor cap removal nor nominal dimension matching proves an open assembled route.
- S01/S02/S03 destination transforms and adapters remain unbound. These reservations do not claim three completed neighboring connections.
- Refinery .480m units and the reactor1.245m cartridge are distinct. Packing/conversion ownership and process interchange remain unresolved.
- At an assumed loaded1.50m/s, the connector is25.47s; adding sill/stub gives28.67s. Room legs, turns, operating delays and door waits are excluded. The whole refinery-to-reactor15–30s gameplay target and full-map travel remain runtime-unverified.

Use the independent final-pass reviews and exact render/cold receipts for acceptance, not this handoff description alone. Historical rejected renders and technical failures are retained with their original status.
