# Turbine Room architecture — design A

This is the metric design baseline for the canonical conversion hall between Reactor Hall and Electrical Room. It defines local construction and interfaces, not an accepted facility placement. All dimensions below are implementation choices. This package does not certify Blender geometry, runtime collision, lifting loads, engineering-code compliance, or art quality.

## Authority and scope

Read for this design:

- `C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md`, `README.md`, and `briefs/turbine-room.md`.
- Current reactor-worktree `design/GAME_SPEC.md`: relevant worker carrying (§4.5), machine interfaces (§11.3), turbine/load/output and power (§12), incidents and recovery (§17–19), room sequence/modularity (§23), information/audio (§24–25), host authority (§28), and machine state (§30.2, §31.1).
- Current reactor-worktree `design/ART_DIRECTION.md`, `ART_REFERENCE_INDEX.md`, and full `AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`.
- Approved reactor reference pixels `reference-a02-hall.png` and `reference-b01-controls.png`, used for material/construction principles only. Their reactor layout is not imported.
- Electrical-room design interface A at `C:/Users/Camer/.codex/worktrees/a81e/critical-shift/sections/electrical-room/interface.json`, read on 2026-09-08. That snapshot is reference evidence, not reciprocal acceptance.

The game specification defines turbine speed, turbine load, electrical output, grid demand, throttle, overload consequences, turbine disconnection, repair, incident warnings, and host authority. It does not prescribe this hall's dimensions, a named overspeed mechanism, or a bearing-oil subsystem. The overspeed trip and bearing-oil repair points are explicit implementation choices supporting those systems. The reactor's small local turbine service station is not being duplicated: this hall owns the aligned conversion train and route toward distribution.

## Coordinate frame and construction

The local main entry threshold centre is `(0,0,0)` at finished floor. `+Y` enters the room toward electrical distribution, `+X` is right/east on the drawing, and `+Z` is up. These are local directions, not geographic north. `facility_transform` remains `null`.

| Element | Local design bounds or dimension |
|---|---|
| Hall clear interior | `x −4..10`, `y 0..24`, `z 0..7.2` |
| Main hall floor area | 14 × 24 = 336 m² |
| Wall thickness | 0.25 m, visibly drawn to scale |
| Main external wall footprint | `x −4.25..10.25`, `y −0.25..24.25` |
| Floor datum / threshold step | `z 0` / 0 m |
| D01 reactor-side opening | Centre `(0,0,0)`, 2.4 m clear width × 2.7 m clear height |
| D02 electrical-side opening | Centre `(0,24,0)`, 2.4 m clear width × 2.7 m clear height |
| Detachable D02 reveal | External `x −1.45..1.45`, `y 24..25.2`; clear width 2.4 m and height 2.7 m; flush floor |
| Envelope including reveal | Bounding rectangle `x −4.25..10.25`, `y −0.25..25.2`; this is not a solid rectangular room extension |
| Mezzanine | None in baseline A; no stairs or raised thresholds on the main route |

The main floor extends through wall thickness. The short electrical reveal is section-owned and detachable. D02 remains the logical threshold at `y=24`; the reveal ends at `y=25.2`. Before facility binding, the connector owner must agree whether to retain that reveal or remove it to prevent overlapping connector architecture. Its free end is not silently treated as a second accepted portal.

The plan shows door parking on both sides of each opening. Each portal has two opposed sliding leaves. Parked leaf footprints are `x −2.57..−1.39` and `x 1.39..2.57`; entry leaves are centred on `y=.075` with depth .11 m, and exit leaves on `y=23.925` with depth .11 m. The reserved pockets are slightly larger and entirely within the hall. Neither open pocket enters `x −1.2..1.2`. Header underside must remain at least `z=2.7`. The dashed position is the closed opening; arrows show the two travel directions. No hinge sweep is required, but actual moving-door collision and closed leaf meeting remain engine checks.

## Equipment and human access

The train axis is `x=4.6`, `z=2.0`, parallel to `+Y`. Turbine casing occupies axial `y=6.0..12.6`; coupling guard `y=13.0..14.0`; generator `y=14.4..18.7`. The two 0.4 m intervening shaft zones are intentional. The foundation envelope is `x 2.5..6.7`, `y 5.5..20`; the drawing's maximum casing envelope is 4.2 m wide and top `z=3.8`. These are envelope limits, not a substitute for authored casing segments, bearings, fasteners, guard profiles, supports, or actual shaft geometry.

The west control station is an open bay at `x −4..−1.5`, `y 8..13`. A separate control booth is unnecessary. Furniture is reserved west of `x −2.8` with a 1.3 m operator apron inside the bay. The throttle, load control, speed/output readouts, and trip must form a meaningful operating cluster with sight toward the train. No layout claim about the reactor's two control banks applies to this section.

The maintenance bay is `x −4..−1.5`, `y 18..24`. During architecture coordination, the deeper proposed bench was found to leave only 0.77 m to the main route. The builder corrected the top to `x −3.87..−2.62`, `y 19.85..22.85`: 1.25 m depth × 3.0 m length and 1.42 m clearance to the route edge at `x=−1.2`. The separate oil stand is `x −3.31..−2.59`, `y 18.425..19.075`. The corrected plan includes these bounds. The 1.42 m is a design clearance; actual stance, repair interaction, tools, and prop collision still require verification. The bench ends before the north door's pockets.

The west side of the foundation leaves a 1.3 m service apron at `x 1.2..2.5`. The east aisle is 2.2 m wide at `x 7.1..9.3`; there is a 0.4 m separation between the base edge and the marked aisle. Those margins are not permission to fill access space with pipes or dressing. Bearing-oil access is nominated at `(2.15,12.9,1.0)` near the west shaft region. Access to opposite generator faces comes from the east aisle.

## Circulation and removal evidence

The main keep-clear volume is `x −1.2..1.2`, `y 0..24`, `z 0..2.7`. It connects both portals continuously without steps. The south crossover spans `y 1.1..4.9` (3.8 m deep); the north crossover spans `y 20.4..23.0` (2.6 m deep). Both link the main route with the east aisle. Open door pockets remain outside the main route and outside these crossover rectangles.

The cart/stretcher test footprint is 0.8 × 2.2 m, with a nominal height of 1.6 m. This is an authored conservative placeholder, not a canonical player/carrying rig. Straight placement in the main 2.4 m route leaves 0.8 m to either side; straight placement centred in the 2.2 m service aisle leaves 0.7 m to either side. The complete in-place rotation sweep has diameter `sqrt(0.8² + 2.2²) = 2.34094 m`.

The four drawn turn discs are centred at `(0,3)`, `(8.1,3)`, `(0,21.7)`, and `(8.1,21.7)`. All fit the authored crossover bounds arithmetically. The 2.4 m main route has only 0.05906 m total clearance around the ideal rotation diameter; this is not enough evidence to claim a two-person rescue passes. The 2.2 m east aisle cannot hold that full in-place turn: rotate in the open crossovers. Carriers, protruding handles, ragdolls, physics tolerances, moving doors, and engine collision skins remain untested.

North staging is `x 2.5..6.7`, `y 20.4..23`. Small disassembled parts can be moved to a cart there, traverse west toward `(0,21.7)`, and follow the main route to a doorway. The drawing distinguishes this service plan from full equipment removal: a 4.2 m-wide foundation or assembled machine cannot pass a 2.4 m personnel opening. No whole-train removal opening is claimed. Component sizes, lifting points, split lines, guard motion, and disassembly sweeps must be verified before claiming a particular casing segment is removable.

The overhead reservation is `x 2.5..6.7`, `y 5.5..20`, `z 3.8..5.8`. It illustrates the room that a future hoist/disassembled-part lift must respect, below the 7.2 m shell. It is not a load rating, a certified rigging solution, or evidence of crane travel. Actual beams, lights, pipes, hooks, slings, and lifted parts must be checked against one another. The longitudinal section follows the train axis; the cross section at `y=10` demonstrates route headroom, human scale, base offset, and the floor return. Utility routes elsewhere are shown on the plan rather than falsely intersected into that section.

The game specifies adjacent-area travel targets of 10–20 seconds and a full-facility crossing under 60 seconds. No movement speed, complete facility route, or runtime travel test was available here. The 24 m local threshold separation is recorded without claiming those targets pass.

## Utilities and neighbor reconciliation

| ID | Local interface centre | Purpose and current state |
|---|---|---|
| U01 | `(8.4,0,4.9)` | Steam inlet; upstream reactor connection unbound; nominal drawn diameter 0.4 m |
| U02 | `(9.5,0,0.45)` | Condensate return; destination requires connector assignment; nominal drawn diameter 0.2 m |
| U03 | `(8.4,24,4.6)` | Generator output bus toward electrical; nominal section 0.4 × 0.3 m; adapter required |

Steam runs overhead along `(8.4,0,4.9) → (8.4,7.2,4.9) → (4.6,7.2,4.9)`. Output bus runs from `(4.6,18.7,4.6) → (8.4,18.7,4.6) → (8.4,24,4.6)`. Neither crosses the main route. Supports, insulation, valves, and actual lowest surfaces require geometric validation. Where any element crosses occupied circulation, its underside must remain at least `z=2.7`.

The floor-level condensate return stays at `x=9.5`, `z=.45`, along `y=0..12.6`. A 0.2 m diameter places its west edge at `x=9.4`, 0.1 m beyond the marked east-aisle edge. The branch from turbine to this return is not yet geometrically specified; it must stay outside circulation or run beneath a flush floor cover. No exposed hose/pipe across the main route is authorized by this drawing. Process pressure, temperature, capacity, electrical ratings, and actual simulation equations are intentionally unset.

Electrical interface A has D01 at `(0,0,0)` with the same nominal 2.4 × 2.7 m opening. That is dimensional compatibility only. Electrical incoming bus U01 is `(-4.4,0,3.9)` in its own local frame. Its x coordinate lies west of this hall's clear western wall, while turbine U03 is on the opposite side and higher. A connector adapter is therefore necessary after the two transforms bind. Do not assume a straight bus continuation or move either completed/active room. No authoritative reactor `interface.json` was available to the parent builder. All reciprocal acceptance and global alignment fields remain unresolved.

## Runtime contract

Proposed interaction IDs in `interface.json` cover throttle, generator load matching, turbine speed/load/output/demand readback, overspeed trip/reset, bearing-oil service, and component repair. These are design contract names, not proof that Blender markers or engine behavior exist. Overspeed and oil mechanisms are identified as implementation choices.

The engine must own collision, navigation, actual interactable reach, door/guard animation, machine/power simulation, audio, incidents, spawn markers, relevance boundaries, and final runtime lighting/optimization. The host owns machine state, incidents, reactor/power consequences, and important interactive objects; clients send intentions. The host validates range, current state, and contention before publishing outcomes. Opening a guard or repairing a bearing must not let a client declare a successful result.

Incident candidates include turbine failure, facility blackout, overload trip, bearing-oil loss, sensor drift, steam leak, live repair, suppressed alarms, and overspeed warning. Use readable physical gauge states, increasing turbine pitch, and staged local/department alarms. Proposed recovery paths are throttle/load reduction, trip and isolation followed by repair, and coordination with electrical backup supply. The engine must preserve a cause → warning → action/failure → downstream-output record for the shift debrief. No random unavoidable failure behavior is specified by the architecture.

## Files, rebuild, and verification boundary

- `../interface.json`: machine-readable baseline and unresolved bindings.
- `generate_floorplan.py`: reproducible original SVG/PNG drawing source and design arithmetic.
- `floorplan.svg`: scalable measured drawing.
- `floorplan.png`: same drawing primitives rasterized with Pillow; inspected at actual pixels.
- `design_checks.json`: 20 arithmetic checks with exact observed values and limitations.

Rebuild from the repository root:

```powershell
python sections/turbine-room/architecture/generate_floorplan.py
```

SVG and JSON need only Python's standard library. PNG additionally needs Pillow, available in the inspected local runtime. Font lookup uses Windows Arial with a fallback. The generator is scoped to this directory and reads the section interface; diagram composition also contains authored baseline dimensions, so dimension revisions must update the interface and generator together.

Performed: parsed the interface, ran all 20 design arithmetic checks successfully, generated SVG and PNG, and inspected the PNG for legible dimensioning and layout. These checks cover nominal doors, route/headroom dimensions, cart straight allowance and ideal rotation, pocket containment, route separation, bay offset, pipe-to-aisle design margin, and zero threshold step.

Not performed by this architecture package: Blender mesh checks, support contact, camera/render art review, collision/navigation/carrier sweeps, actual guarded repair poses, crane/casing removal, animation/netcode, physical engineering validation, accepted neighbor transforms, or facility travel. The independent technical validator and builder must report those separately. No category score or section acceptance is awarded here.
