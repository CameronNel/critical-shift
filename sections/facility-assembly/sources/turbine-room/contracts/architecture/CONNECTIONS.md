# Measured interfaces and proposed topology

Metres, right-handed coordinates. Turbine origin D01=(0,0,0), inward+Y, up+Z. All transforms below are proposals for the facility integrator; no neighbouring geometry is moved or changed. Detailed read-only saved-file bounds and SHA256 identities are in `reactor-saved-survey.json` and `electrical-saved-survey.json`.

## Existing neighbouring evidence

Reactor saved `reactor_scene.blend` has MAIN ACCESS at(−10.8,0,0), outward−X, width6m alongY, height5.5m. Its own stub extends to x−14.500001m, floorz0, clearY±3m. Its closed distant doors occupy x−14.490001..−14.389999 and currently block traversal. They belong to the reactor; this assignment leaves them untouched. There is no dedicated Turbine Room portal. Cooling Plant uses the separate southeast reactor connection and is preserved.

Electrical saved `electrical_slice.blend` has D01_Turbine=(0,0,0), outward−Y. Evaluated jamb inner faces are x±1.19999993m; header undersidez2.70000005m; threshold topz0. Therefore the opening is2.4×2.7m within float tolerance. The electrical contract revisionC places U01 incoming bus at(−4.32,0,3.88). Its saved file is a slice: incoming switchgear marker is measured, but a complete reciprocal utility endpoint is not proven by that scene. This distinction remains unresolved.

Fuel Corridor's S01_PLANT(−5.4,17.4,0), outward−X,2×2.5m is reserved/shared, not assigned to Turbine. No claim is made on it. No direct Cooling Plant doorway is created. Completed refinery and mine remain outside scope.

## Owned Turbine interface table

| ID / marker | Local centre | Outward | Clear section / ownership |
|---|---|---|---|
| D01 / IF_PORTAL_D01_REACTOR | (0,0,0) | −Y |2.4×2.7m, parked leaves and frame owned by Turbine |
| D02 / IF_PORTAL_D02_ELECTRICAL | (0,24,0) | +Y |2.4×2.7m logical threshold; Turbine reveal continues to y25.2 |
| U01 / IF_STEAM_IN_REACTOR | (8.4,0,4.9) | −Y |.4m nominal steam diameter; unbound remote source |
| U02 / IF_CONDENSATE_RETURN | (9.5,0,.45) | −Y |.2m liquid return; opposite end blind until condenser designed |
| U03 / IF_POWER_OUT_ELECTRICAL | (−4.32,25.2,3.88) | +Y |.4×.3m bus mating face; owned overhead cross-route and drop |
| U04 / IF_LP_EXHAUST_CONDENSER | (4.6,11.45,0) | −Z |2.5×1.5m actual hood/slab opening; underfloor condenser owner unassigned |

## Coherent proposed facility placement

Keep reactor in its current frame. Place Turbine local origin at reactor-world(−18.5,0,0), Rz=+90°. Turbine+Y then points west, away from reactor. A proposed4m connector extends from reactor stub outer edge(−14.5,0,0) to Turbine D01(−18.5,0,0). It narrows6×5.5m to2.4×2.7m without consuming either owner's wall. Reactor's closed door requires an integrator-approved operational opening state; it is not removed here. The connector is reserved topology, not constructed scenery in another section.

In Turbine's frame, place Electrical origin at(0,25.45,0), Rz=0. Its existing south wall reaches y25.20 because that wall occupies local−.25..0. Thus the Turbine reveal ends where Electrical's exterior wall begins. The two2.4m openings are collinear and level. A.25m bus bridge connects Turbine U03 at y25.20 to Electrical contract U01 at y25.45, with x−4.32/z3.88 unchanged. Existing Electrical optional scenic closure/stub must be reviewed by its owner, not silently deleted by Turbine.

This gives a clear reactor → reserved connector → Turbine → Electrical chain extending west, away from the southeast Cooling Plant. It is a local topology proposal, not whole-map collision proof: spawn/refinery/mine and every other facility transform must be assembled before final facility validation. Connector generation, reciprocal approval, steam source and condenser placement remain named integration work.
