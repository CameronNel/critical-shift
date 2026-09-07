# Cooling Plant scenery intent

11m × 13m clear service hall, 5.8m clear ceiling, local entry threshold `(0,0,0)`, +Y inward, +Z up. A 5m × 5m main opening feeds the permanent 2.2m cart/rescue lane. Two west-side pump skids and an east exchanger leave separate maintenance lanes and a rear tube-withdrawal reserve. A small west rear alcove holds the repair bench and cart.

Dimensions not supplied in the brief are explicit implementation decisions in `interface.json` and `architecture/README.md`. Proposed connections do not relocate existing rooms. Cooling failure, manual valve intervention, pump repair, portable power and mine-water recovery hooks follow GAME_SPEC, with host-authoritative implementation deferred to the engine.

This is a scenery/contract package under construction. Only the pump/workshop style slice is currently built; full-room functions are unproven. The next run must correct the recorded geometry and art failures before expansion.
