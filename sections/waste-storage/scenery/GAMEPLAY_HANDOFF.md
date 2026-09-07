# Waste Storage runtime handoff

This package authors visual geometry and measurable architectural allowances. It does not implement game simulation, network replication or final engine collision.

| Functional element | Future interaction and state | Visible evidence expected |
|---|---|---|
| Receiving monitor / inventory station | inspect dose, register incoming batch, approve cell, acknowledge alarm | physical controls, restrained status display, paperwork and access reader |
| Cart and sealed casks | grab/push, load/unload, inspect seal, transfer custody | rubber wheels/grips, lifting/sealing construction, human-reachable handles |
| Four segregated cells | capacity, legal location, occupancy, dose/contamination zone | different container classes and spatial separation |
| Quarantine hold | verify unknown batch, isolation, unauthorized release | controlled access and a selective unresolved work item |
| Ventilation/filter equipment | isolation, blocked filter, damaged sensor, maintenance, reset | service front, gauge/switch, plausible routed utility |
| Controlled dispatch | seal scan, inventory reconciliation, door permissions, audit | clear level cart portal and verification point |

Host authority owns batches, cask seals, positions, dose fields, inventory discrepancies, capacity and gate state. Clients submit inspect/carry/operate requests; the host validates range, permissions and conflicts. Disconnect must release held carts or tools safely. No static dressing is automatically converted to physics.

Required scenario hooks from GAME_SPEC: waste backlog starts with near-full storage; bypassing registration or storing a legal cask in the wrong cell creates evidence; sensor failure is visible before unsafe exposure; contamination may travel on carts, boots and tools; inspection follows the circulation route and compares casks with logs. Recovery must permit isolation, correct relocation, maintenance and renewed inspection. A waste container may support concealment only with explicit capacity, visibility, sound, search/escape and risk fields; this environment does not implement those behaviors.

Engine integration must validate collision and navigation; moving door/cask/cart states; carried-body envelopes; obstruction recovery; audio/dose/incident zones; network relevance boundaries; facility travel targets; performance and draw calls; final runtime lighting. Blender measured clearances are static evidence, not a multiplayer or physics PASS.
