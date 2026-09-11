# Cooling Plant scenery intent

11m × 13m clear service hall, 5.8m clear ceiling, local entry threshold `(0,0,0)`, +Y inward, +Z up. A 5m × 5m main opening feeds the permanent 2.2m cart/rescue lane. Two west-side pump skids and an east exchanger leave separate maintenance lanes and a rear tube-withdrawal reserve. A small west rear alcove holds the repair bench and cart.

Dimensions not supplied in the brief are explicit implementation decisions in `interface.json` and `architecture/README.md`. Proposed connections do not relocate existing rooms. Cooling failure, manual valve intervention, pump repair, portable power and mine-water recovery hooks follow GAME_SPEC, with host-authoritative implementation deferred to the engine.

The complete room is authored: two detailed pump skids, exchanger and hoist, workshop, reserve restart, water recovery services, drains, routes and lighting. Final acceptance is recorded in production/FINAL_HANDOFF.md when available; construction and historical failures are retained in production/CORRECTION_HISTORY.md. This is a local Blender scenery/contract package, not an assembled game-engine level.
