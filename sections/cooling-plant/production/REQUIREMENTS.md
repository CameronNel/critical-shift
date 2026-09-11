# Required equipment and scope traceability

| Requirement | Authority | Authored implementation | Verification scope |
|---|---|---|---|
| Pump/exchanger/valve maintenance room | Cooling assignment | Two original centrifugal pumps P-01/P-02, HX-01, isolators, service workshop | Saved geometry, rendered pixels, route checks |
| Traceable coolant supply/return | Assignment; GAME_SPEC cooling | West return → pump branches → hot header/crossfeed → HX → east supply | Local endpoint and pipe network checks; remote circuit unassembled |
| Pump health, pressure, flow, temperature readability | GAME_SPEC12,18 | Pump gauges, local FLOW/TEMP/PRESSURE/PUMP control panel, machine IDs | Visual/semantic handoff; simulated values not implemented |
| Cooling failure/repair/manual valve hold | GAME_SPEC2.3,12,18 | Accessible couplings/casings, isolators, repair bench, tools, manual wheels | Authored maintenance access; engine interactions deferred |
| Reserve restart and competing reserve usage | GAME_SPEC5.5,18–19 | Reserve isolator cabinet and feeder/socket | Local artifact only; shared authoritative pool remains engine responsibility |
| Portable mine battery and backup mine-water recovery | GAME_SPEC19 | Named capped battery and water connections; water branch connects secondary circuit | Local connections measured; no remote hose implied |
| Worker/cart/rescue circulation | Assignment, facility topology |2.2m center route,1.4/1.3m pump lanes,1.2m HX reach strip, workshop door | Evaluated volumes and sampled swept boxes; no engine physics claim |
| Reactor SE interface | Cooling brief and actual reactor |5×5m CP-P01; corrected outer-stub mating transform | Read-only saved-neighbour survey; closed reactor door unresolved |
| Drainage, supports and exchanger access | Assignment | Flush recessed grates/collector; saddles/bolts;3.5m pullout bay and hoist | Actual geometry/contacts and supplementary views |
| Original game art | Art specification + latest user | Ivory/charcoal/oxide-orange/yellow Valorant direction; no teal or imported mesh | Luna pixel review; built-in imagegen guidance |

Design choices, not explicit canonical dimensions:11×13m footprint;5.8m ceiling plane; two redundant18kW-labelled fictional pumps;3.85m exchanger shell, nominal3.35m cartridge; workshop dimensions; all utility bore sizes and local socket coordinates; wall palette, hoist, maintenance props. The brief explicitly fixes the reactor entry at5×5m; the existing3.7m stub is measured ownership evidence. The room includes no raised platform because floor-level service suffices.

Door/opening count: one external personnel/freight opening CP-P01, one internal personnel opening CP-D02, one glazed side aperture into workshop, eight named utility sockets (not pedestrian doors). All routes return to CP-P01; no invented turbine or refinery door. Unresolved neighbouring interfaces are recorded in architecture/CONNECTIONS.md.

Ten primary fixed cameras C01–C10 cover room/machinery/workshop. Eight supplementary W01–W08 views cover approaches, reserve/water, turns, workshop, withdrawal and rear utility service. The repeated saved-scene route audit uses player eye1.68m, body1.85m and conservative box footprints; it does not stand in for game-engine walkability.
