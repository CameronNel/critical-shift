# Required equipment and operational handoff

This list distinguishes the specified operational functions from authored visual choices. Saved-geometry and visual acceptance are recorded separately in production/validation and production/critics.

| Function required by specification | Authored equipment / identifiers | Representation and access |
|---|---|---|
| Incoming turbine power and isolation | U01, SG01 | Matched incoming adapter, enclosed bus, source/load meters, isolator and status pilots |
| Main power distribution | SG02, U02 | Main bus bay, supported overhead casing, flanged branches and outgoing interface |
| Cooling and production load decisions | SG03 COOLING, SG04 PRODUCTION | Separate feeder controls and meters; production shedding hook |
| Facility distribution and health | SG05 FACILITY | Distinct feeder, operating control, state indication |
| Component failure and physical repair | SG06 SERVICE | Withdrawn breaker, exposed poles/contacts, carriage, trip links, springs, work light and racking interface |
| Power conversion/distribution construction | TX01 | Chosen guarded three-coil dry transformer, core/yokes, plinth, earth bond, terminal enclosure and supported duct entries |
| Backup restoration and manual transfer | TD01 | NORMAL/RESERVE operating arms, mechanical interlock, crank socket, reserve state readback |
| Cooling versus OCRU reserve priority | TD01 selector | COOLING / HOLD / MEDICAL; engine maps medical priority to OCRU reanimation |
| Shared reserve and backup service | RB01–RB03, U03 | Three serviceable reserve modules with state meters, disconnects, trays, terminals and charging header; shared gameplay pool |
| Portable/black-start input | INTERACT_PORTABLE_INPUT | Wall-mounted connection in reserve bay, accessible from branch apron |
| Practical maintenance | WB01, service cart | Supported bench, fuse cradle, toolcase, screwdrivers, hanging tools, isolation record and small used props; cart/work-permit/lockout evidence |
| Player circulation and rescue route | D01, D02, P03 | Opposite 2.4 × 2.7 m external portals, 2.4 m main aisle and reserve branch; no stairs |
| Readable operational environment | Labels, practical lights, audio/incident hooks | Consistent identifiers, backed text, task lighting, named engine integration anchors |

The six-bay sequence, three reserve cabinets, dry-transformer configuration and room dimensions are implementation choices serving the specification. No generated voltage, current, capacity or engineering certification is adopted. The external backup source is an unbound interface; no neighboring generator is invented.

All dynamic electrical flow, load shedding, shared reserve economy, injury/repair outcomes, animation interlocks, incidents, sounds, collision, navmesh and network authority belong to engine integration. Blender controls are visible mechanisms and hooks, not implemented game logic.
