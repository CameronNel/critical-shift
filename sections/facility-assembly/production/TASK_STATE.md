# Facility assembly — A04

Owner Astra. Workspace `C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra`; branch `codex/facility-assembly-20260912`. Owned scope is `sections/facility-assembly/` and the new shared assembly status/pointer. Original room worktrees are read-only.

User request: assemble the parts, think through the spec and flow first, and leave space for connecting structures because they do not yet exist.

Delivered scope: twelve linked full room modules, unit scale preserved, 21 explicitly unbuilt connection reservations and four reserved construction volumes. The master is `blender/facility_master.blend`. Supporting plan, transforms, sources, conservative geometry screen and cold-load check are in this directory. No original room geometry was rebuilt, cut, moved or overwritten.

Read first: [README](../README.md), [layout](LAYOUT.json), [source registry](SOURCES.json), [plan audit](PLAN_AUDIT.json), [cold check](COLD_MASTER_CHECK.json).

A01 reservations grazed cooling/turbine geometry. A02 still grazed the reactor approach. A03 cleared those candidates. A04 adds the southern maintenance crossover and raises the utility allowance above the route headroom. Old layouts/audits/images remain under checkpoints. Final overview labels were lowered to their corresponding roofs after pixel inspection revealed confusing aerial parallax; room transforms did not change.

Verification: zero remaining conservative reservation-clearance candidates outside the disclosed endpoint transitions; unit scales all one; source hash checks; twelve relative library links and packed dependencies; U04 centre error approximately 0.0000054m. The turbine/condenser pair remains an intentional stacked-interface broad-phase overlap, not an assertion of zero detailed mesh contact.

Travel is a planning model: connected graph, longest planned route248.5m,55.2s at assumed4.5m/s,62.1s at4m/s. This is not controller, cart, body-carrying or navmesh verification. No claim of perfect runtime flow is made before actual connectors exist.

Next task: build the reserved connector network against the frozen room interfaces; resolve doors/caps and seam details; verify actual loaded/unloaded travel and source-room transitions in Unity. Do not treat dashed reservations as finished floors. Preserve the selected source copies and explicit original/mutable hash distinction.
