# Turbine Room requirements and design B

This is the 2026-09-11 takeover of checkpoint `4dcaad9`. The previous maintenance slice is retained in `production/checkpoints/slice-05/inherited-slice-05.blend`. The current section is built from empty Blender data with original geometry; no neighbouring room mesh is imported.

Authority: the facility BUILD_BRIEF, `briefs/turbine-room.md`, GAME_SPEC chapters12,18,19,23–25, ART_DIRECTION and ART_REFERENCE_INDEX. The latest user mandate supersedes the old slice-only/four-cycle workflow, Astra reviewer, deadline and intermediate approval gates. The builder is Astra; independent reviewer is Luna. Strict Valorant style and no teal override inherited palette choices.

## Explicit specification coverage

| Requirement | Scene representation | Engine responsibility |
|---|---|---|
| Turbine speed and load | Shaft train, separate THROTTLE and LOAD controls, SPEED readback | Host-owned speed/load simulation and animation |
| Electrical output and readable demand | Generator, supported outgoing bus, adjacent OUTPUT/DEMAND readbacks | Demand waves, actual output, overload consequences |
| Health, alarms and safety | HEALTH/SAFETY readbacks, guarded TRIP, bearing/inlet fault markers | State transitions, damage, warnings, automatic trips |
| Repair and maintenance | Bearing housings, oil-service cabinet, removable hatches, maintained bench, tools | Repair interaction, inventory and live-repair consequences |
| Emergency turbine disconnect | Trip control and output interface | Authoritative disconnect/shutdown protocol |
| Shared reserve and turbine-reserve recovery | RESERVE readback and HOOK_SHARED_RESERVE | Electrical reserve pool and recovery cost; no duplicate battery system |
| Navigation between reactor and electrical | D01/D02 clear through-route, crossovers and east maintenance loop | Reciprocal connector acceptance, collision/navmesh and whole-map travel |
| Readable diegetic information | Physical names, distinct control shapes, labelled readbacks | Dynamic values, localization and accessibility scaling |
| Audio/incident communication | Actual inlet, bearing and train markers | Idle/start/run/stress/warning/failure/shutdown/repair audio states |
| Modular integration | Local origin, exact interface IDs, collections, fixed cameras and saved checks | Engine import, optimization, networking, relevance/spawn boundaries |

No operating RPM, MW capacity, pressure, real electrical clearance or mechanical load rating is specified or certified by this scenic model. Readout words are authored neutral presentation states, not live telemetry.

## Dimensioned design decisions

Clear shell: x−4..10, y0..24, z0..7.2 metres. Fourteen metres wide, twenty-four long. Floor z0; no mezzanine, stairs or thresholds requiring a step. Wall thickness.25m. Train shaft x4.6/z2.0, along Y. Foundation x2.5..6.7/y5.5..20, top.45m. HP casing y6.02..8.35, expanding LP y8.94..12.35, coupling y13.04..13.98, generator y14.4..18.7. Bearings support the common shaft.

Main route x±1.2 gives2.4m width. West equipment apron x1.2..2.5 gives1.3m. East aisle x7.1..9.3 gives2.2m. South crossover y1.1..4.9, north crossover y20.4..23. Maintenance bench x−3.87..−2.62, y19.85..22.85, top1m; apron to main lane1.42m. Controls occupy west bay, away from the through-route. The .8×2.2m nominal cart turns at crossovers, not within the2.2m east aisle. Carrier bodies and animation sweeps remain untested engine work.

The LP downhood is a deliberate process decision: a large2.5×1.5m downward exhaust interface awaits an underfloor condenser. The.2m liquid return pipe is blind terminated, not portrayed as the turbine's entire exhaust. This limitation is visible in the contract and handoff. No basement room or neighbouring cooling machinery is silently built. The steam branch is lateral and removable; heavy upper-casing work stays in-room under the monorail. Full casing extraction through2.4m doors is not claimed.

The SVG/PNG floorplan is a design drawing; revision-specific evaluated geometry audits are the evidence for the actual saved scene. Existing ARCHITECTURE/MACHINE_DESIGN are inherited design history; this revision and interface.json supersede conflicting utility routes and unfinished-state statements.
