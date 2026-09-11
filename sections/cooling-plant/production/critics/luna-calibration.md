# Luna review calibration — Cooling Plant resumed 2026-09-11

Reviewer: Luna (independent reviewer; no Astra review requested for this resumed run)

## Acceptance stance

This is a calibration record, not an acceptance score. No score is awarded until the complete room is rendered from all ten frozen cameras and the actual pixels are inspected. Builder intent, object names, node graphs, or a saved `.blend` do not count as visual evidence. The room remains blocked while any relevant category is below 90/100 or while objective clearance/support validation fails.

The user’s current priority is an integration-ready room early. A complete room may therefore be judged as one coherent facility service space, but the full-room pass must still preserve the authored slice’s quality and repair its known failures before propagation. Tiny-prop polish cannot compensate for missing room function, unreadable routes, or untraceable services.

## Category standards (each independently 90+)

| Category | 90+ observable standard |
|---|---|
| Specification coverage | Cooling support plant visibly contains the 11m x 13m, 5.8m-clear service hall, 5m x 5m reactor service opening, two pump skids, shell-and-tube exchanger with rear tube-withdrawal reserve, restart/portable-battery terminal, maintenance alcove/bench, drains, and the declared supply/return, secondary-water, reserve-power, mine-water and drainage sockets. Failure/recovery affordances are legible without inventing runtime behavior. |
| Layout/flow | First-person read immediately separates reactor/cart entry, permanent 2.2m cart/rescue lane, pump service lanes, exchanger side/rear work volume, restart station and alcove. No installed object, door leaf, pipe, prop or parked cart blocks those intended operations. The exchanger withdrawal reserve remains visibly and physically usable. |
| Machinery | Pump casings, motor/coupling guards, skids, valves, gauges, exchanger barrel/saddles/covers, hoist provision and restart terminal have distinct, believable industrial silhouettes and maintenance logic. The scene shows how an operator isolates, inspects, repairs and restores circulation. Hero machinery must not read as generic bevelled boxes/cylinders with screens. |
| Navigation/readability | Entry and return orientation, service-side access, operator reach, overhead clearance, hazard zones, and emergency recovery path read at gameplay height. Route guidance uses shape, value, light and sparse signage together; no wall of labels is required. Cart/rescue traversal and door operation remain clear in the actual images. |
| Construction | Walls, jambs, overhead service door, floor transitions, pipe supports, flanges, drains, cable/pipe penetrations, guards, handrails and fixings appear physically assembled and maintained. Utility supply and return are traceable from socket through pumps/exchanger; services do not cross the entry below the 5m opening head. No floating, unsupported, or implausibly penetrating components. |
| Materials | Painted teal/green metal, charcoal structure, bare stainless/steel, concrete/panel walls and floor, rubber seals/hoses, timber bench, paper/fabric and glass each separate by roughness/value/specular response. Surfaces show restrained localized use wear and contact shadow; no universal satin plastic, blanket grunge or wet-plastic floor. |
| Lighting | Practical fixtures create readable key zones at pumps, exchanger, controls and bench, with falloff into secondary space, strong contact shadows and controlled warm/cool contrast. Gauges, labels, couplings and route edges remain readable. Dark machinery cannot lose its form; emissive/cyan cues remain selective. |
| Reference fidelity | Applies the approved reactor plates’ principles: broad cream/institutional wall fields, teal machinery, charcoal framing, stainless highlights, limited safety yellow, sparse legible labels, clear controls and disciplined negative space. Mine references inform industrial transition, rough service evidence and restrained wear only; cooling plant must remain a maintained service hall, not a cave or generic kitbash. |

## Mandatory visual checks

- All ten fixed cameras are present and rendered: entry, hero, reverse, route, pinch, pump, exchanger, workshop, bundle/secondary bay and materials.
- The full room reads as one integrated plant from at least the entry and reverse views; no camera can hide missing exchanger, route, or rear work volume.
- The permanent 2.2m main lane is visually continuous and free of installed obstructions. The 5m entry opening stays clear to 5m height.
- Pump front/coupling lanes, shared pump lane, alcove approach, exchanger side strip, rear withdrawal reserve, hoist work zone and restart operator space read as deliberate working volumes.
- Supply/return identities remain distinguishable along the visible route; capped mine-water and portable-battery connections look reachable and temporary rather than permanently cluttering the cart lane.
- Every support-dependent object passes objective contact validation. The visual review treats any visible gap, floating item, severe penetration, or detached shadow as a failure even if the validator misses it.
- Pixel comparisons use identical camera transforms, framing and render settings. Review defects are recorded as observed pixels; no coordinate or geometry recipes are issued by this reviewer.

## Current known hazards carried into the resumed run

These are objective blockers already evidenced in `production/technical/S03-validation.json` and must be resolved before slice or full-room acceptance:

1. D02 open leaf overlaps the KC-BENCH standing strip by approximately 20 mm.
2. CP-WORKBENCH exceeds its declared rear Y envelope by approximately 10 mm.
3. Both D02 hinge support anchors penetrate the jamb support plane by 64.64 mm each.
4. Removed blackened seal floats 20 mm above the wiping rag.

The prior independent S02 pixel review remains useful only as a hazard baseline: shape 80, hierarchy 82, materials 73, lighting 76, color 88, storytelling 68. It cannot be transferred to S03 or to a full-room build. S03 has three rendered slice cameras but no independent art score; no full-room score exists.

## Expected high-impact failure modes to watch

- Full-room expansion leaves the entry/route as an empty shell while the pump slice receives detail; this fails specification coverage and integration readiness.
- Pump and exchanger bodies become a repeated teal primitive language; this fails machinery, construction and reference fidelity even if silhouettes are tidy.
- Nearly black machine faces, blocked couplings, unreadable gauges, or shadowed service lanes prevent a player from understanding repair flow.
- The rear exchanger reserve is visually occupied by pipes, columns, bins, labels or props, making tube withdrawal a claim rather than a usable maintenance volume.
- Decorative signage or cyan lights substitute for causal evidence of supply, return, pressure loss, backup coolant, reserve power and manual valve intervention.
- Bench dressing, paperwork, rags and tools look staged or float; localized human maintenance evidence must support the work story and survive fixed-camera inspection.

## Decision rule for future concepts/renders

Any new image concept is eligible for independent consideration only when each relevant component is scored from its visible pixels at 90/100 or better against this calibration. No user-rating wait is required under the current instruction. A concept can inform direction, but it does not waive gameplay dimensions, route clearances, support-contact checks, fixed-camera evidence, or the four-cycle production protocol.
