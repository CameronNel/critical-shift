# A06 connection pass — first rescue courtyard

Built from B06 blockout, then concept-R01, then geometry R04. This is the first connection area, not whole-map visual acceptance.

## Layout
Medical assembly instance moves +11m east and -6m south to (-18,31,0). Its source room remains untouched. R11 and R15 follow this placement; new R22 crosses the open courtyard. All remaining horizontal connections have explicit greybox floors. R19 still requires actual stairs/lift; doors, interlocks and engine collision remain integration work.

The planned mine-to-medical distance changes from 108.61m to 88.95m; refinery dispatch from 73.31m to 53.65m. These are graph centreline distances, not measured game timings. Both routes avoid the reactor and turbine. Spawn adds 3m; power-wing rescue routes save 17m.

## First built connection
Continuous pavement, clear 4m rescue lane, medical canopy, open shade pavilion, timber seating, olive planters, stored pipe rack, loose flanged pipe sections, crates, service cabinet, hose reel, drainage and wayfinding. Detail sits outside the route strips. The concept is a design target; current geometry is an initial implementation and does not claim identical fidelity.

## Evidence
- Actual whole-map top view: connections/rescue-courtyard/renders-R04/TOP.png
- Actual courtyard and eye views: renders-R04/COURT.png and EYE.png
- Generated design concept: art/concept-R01.png
- Clearance_R04: zero added obstacle candidates in the 0.08–2.25m route band (conservative AABB test).
- production/RESCUE_ROUTE_COMPARISON.json: connectivity, source occupancy and distance report.
- Context in courtyard review renders uses disposable room display meshes; master retains original linked render assets.

## Preservation and performance
A04/A05 masters and the previous walkthrough are preserved. New files: blender/facility_master_A06_connections.blend and blender/facility_walkthrough_A06_connections.blend. Walkthrough uses 26 mesh batches, including two new connection batches; source authoring collections remain accessible. Gravity stays disabled. No new FPS claim until measured on the new file.

## Remaining
Detailed structures for the remaining routes, all vertical access, terrain and boundary continuity, working doors, game collision/navmesh, whole-map travel playtests, and visual polish to concept standard.

Reopen verification: A06 live file reports 26 cache meshes, medical placement (-18,31,0), gravity disabled and courtyard authoring hidden in fast mode. Static redraw benchmark: 98.08 FPS over 30 redraws. This is not a gameplay FPS guarantee. MCP file-open returned a stale Camera-reference error after successful opening; fresh instance identity and readback confirmed the new file loaded correctly.
