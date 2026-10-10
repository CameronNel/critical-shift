# C84 pool inlet and through-wall service review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`

## Findings

### Pool inlet route and diffuser-to-liner interference

The authored inlet is an over-rim drop. In `scripts/rh_services.py`, the route starts at the manifold near `(-1.4, -4.9, 0.32)` and runs over the pool rim to `(-1.4, -3.0, -3.0)` before the submerged diffuser is built (lines 365–395). The source therefore does not call for a penetration through the cylindrical pool wall at the diffuser.

The saved C84 mesh nevertheless has an unmanaged nozzle/liner intersection. `LUNA_C84_POOL_PENETRATION_INTERSECTIONS.json` reports four diffuser-body versus liner face intersections and twenty black-slot versus liner intersections. The liner is a continuous 64-vertex, 32-quad cylinder at radius 3.4 m from z −0.55 to −6.55; the sampled faces have no opening at the diffuser. The body and slot bounds are respectively x −1.57…−1.23 m and x −1.572…−1.228 m around the centerline x −1.4, y −3.0. A separate iron flange in the same assembly has 4 reported liner intersection pairs.

The current centerline is at radial distance `sqrt(1.4² + 3.0²) = 3.31059 m`, leaving about 89.4 mm to the liner radius. The existing body radius is 170 mm, slot radius 172 mm, and separate iron flange radius 120 mm. Reducing only the body and slots to 70/72 mm would leave the flange crossing the liner. A repair should also reduce or reshape that flange to fit inside the measured 89.4 mm radial envelope with margin, or move the nozzle inward while preserving the pipe axis. Keep #85 open until the corrected saved meshes show clearance and a useful current-quality image shows the over-rim termination.

### Later in-memory fit probe (not a C84 repair)

The owner's `rh_pool_diffuser_fit.py` test applies the proposed size correction to the saved C84 scene in memory only. Its exact C84 input SHA remains unchanged, and the test changes only local vertices of the three nozzle parts: body radius 70 mm, black-slot radius 72 mm, and the separate iron flange radius 75 mm. The second application changes zero vertices, showing the edit is idempotent. The follow-up BVH probe reports zero nozzle/liner overlap pairs and minimum sampled clearances of 8.57 mm (body), 6.59 mm (slots), and 3.66 mm (flange). The 75 mm flange is now within the measured radial allowance, though its 3.66 mm minimum gap remains tight. This is a viable geometry correction, but it does not change or repair the saved C84 file and supplies no appearance evidence. Recheck the exact saved candidate and full-quality view before closing #85.

### Actual wall penetrations

The C84 `wall-bores.json` is exact-source evidence for eight active wall routes. It reports 65 rays per route, zero blocked rays, and `all_pass: true` for the EC vent, EC-A drain, EC-B drain, turbine steam, turbine exhaust, waste vent, bank A service, and bank B service. The source places annular sleeves at the matching wall faces; the over-rim pool inlet is not one of these wall crossings. I found no additional wall-crossing pipe in the reviewed service source that lacks a sleeve or bore entry.

This is a finite geometry result, not a visual acceptance of sleeve appearance. Keep the relevant appearance portion of #90 pending until the mapped full-quality view establishes that the fittings read as actual wall sleeves. Do not characterize the pool diffuser as a wall penetration; it is a separate liner-interface fit defect under #85.

## Evidence files

- `/workspace/scratch/reactor-refinement-cycle84/wall-bores.json` — exact C84 source SHA; eight routes, 65 rays each, zero hits.
- `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_POOL_PORT_LINER_AUDIT.json` — exact diffuser/flange bounds and radial sample points.
- `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_POOL_PENETRATION_INTERSECTIONS.json` — evaluated mesh pair-intersection counts.
- `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_POOL_PORT_LINER_AUDIT.py` — read-only probe source.
- `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_POOL_PENETRATION_INTERSECTIONS.py` — read-only probe source.

**Disposition:** #85 has a confirmed saved-geometry defect. #90 has a finite technical pass for the eight actual wall routes; final visual acceptance remains pending. No global score is assigned.
