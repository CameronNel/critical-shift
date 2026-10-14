# Grey-box test: a short fuel corridor (2026-10-13)

**Outcome:** the owner said "yes do the rebuild to the same graphical fidelity as it was previously"; the real short corridor (S1, cut from F23ci) and the layout around it are now the map (`COMPACT_MAP.md`, "Short fuel corridor layout"; `ASSEMBLY_REPORT.md`). The numbers below are the grey-box test's and are kept as its record; `greybox_fuel_test.py` runs from commit c25d102.

**A test, not the map.** The owner asked whether to rebuild the fuel corridor, then said "yes do the greybox test". `combined_map.blend` is unchanged; this builds a separate scratch scene with `greybox_fuel_test.py` (it refuses to write `combined_map.blend`). Grey parts are plain boxes named `GREY_*`, not art. Unreviewed.

![grey-box plan](renders/greybox/18_greybox_plan.png)

## What the test changes (against the assembly pass)
* The fuel corridor room (F23ci, 38.2 m freight path, 3.1 M triangles) is left out. A **grey corridor** (5 m wide, 5 m high) runs from the refinery fuel door north 5.8 m, then east 11.4 m to the concourse: **17.2 m** of freight path.
* That lets the **reactor cluster move 20.6 m south** (reactor, turbine, electrical, condenser bay, stair, cooling): the concourse now sits 2.5 m off the refinery's north wall, which is what fixes the distance.
* The **spine shrinks from 33.5 m to 12.6 m** (grey box; the front end's own spine objects are left out). The dock stays on its east wall.
* **Waste moves to the reactor's east wall**, through the 4 m opening the reactor already has there (closed by `East wall patch door`, left out; the wall layers and the orange wall-base guard inside a 3 m opening are split out, a grey threshold fills the wall depth). The S03 transfer hall is dropped with the corridor it served.

## Results (all measured on the built grey-box scene)

| | Assembly pass (now) | Grey-box test | Change |
|---|---|---|---|
| building box, mine excluded (plan cut 1.1 m) | x -53.6..37.3, y -93.1..39.7, 12,080 m2 | x -53.6..37.3, y -93.1..19.1, **10,207 m2** | **-15.5 %** |
| convex hull | 8,969 m2 | **7,494 m2** | **-16 %** |
| north edge | y 39.7 | y 19.1 | -20.6 m |
| fuel run, refinery to the core, loaded cart 1.5 m/s | 62.9 m, 41.9 s | **42.1 m, 28.1 s** | meets the 30 s target |
| spawn to reactor floor (walk 4.5 m/s) | 90.2 m, 20.0 s | **69.5 m, 15.4 s** | -4.6 s |
| medical to reactor floor | 95.0 m, 21.1 s | 74.4 m, 16.5 s | -4.6 s |
| reactor floor to dock | 48.9 m, 10.9 s | 28.3 m, 6.3 s | -4.6 s |
| reactor floor to waste | 33.7 m, 7.5 s | 35.7 m, 7.9 s | +0.4 s |
| reactor to electrical / condenser / cooling | 45.0 / 54.6 / 15.0 m | 45.0 / 54.5 / 15.0 m | same (moved together) |
| spawn to electrical (farthest station) | 160.9 m, 35.8 s | 140.1 m, 31.1 s | -4.7 s |
| evaluated triangles | 12.50 M | 9.33 M with grey boxes | the real corridor's budget decides the final number |

Capsule walk test (`greybox_walk.py`, same capsule and method as `walk_test.py`): **9/9 routes pass** (`validation/greybox_walk_report.json`). `check_overlaps.py` on the grey-box plan cut: no intrusion between the moved rooms; the waste hits it lists are the reactor's rectangle (its corner stubs reach x 12.8), and a direct check found no reactor geometry beyond the east face x 11.6 where waste sits.
Renders (640 x 360, looked at): `renders/greybox/18_greybox_*.png` (aerial, grey fuel corridor, concourse junction, short spine, reactor to waste).

## What it would take to make it real
1. A **new fuel corridor room** in place of F23ci (reviewed 99): an L about 6 + 11 m, 5 m wide, with the refinery F01 boundary, a freight gate, the S01/S02 service ports if still wanted, and an art and review pass. F23ci becomes unused (not deleted).
2. **Layout rebuild** of `build_compact_map.py` around the new reactor position: concourse and spine (the front end's spine trimmed to 12.6 m as a local copy instead of left out), waste on the reactor's east opening, the stair and every collider and door anchor moved, the walk, lighting and performance checks re-run.
3. Not checked in this test: lighting, collision proxies, door anchors, exterior roofs and the spine's look (grey), the reactor's east-wall interior beyond the 3 m opening, whether the cooling plant's new neighbours (fuel corridor 12 m south of it) matter for gameplay.

## Verdict
The test supports the rebuild **if a tighter map is the goal**: -16 % area, the north edge 20 m closer, every trip through the spine about 4.6 s faster, and the fuel run meets its target end to end. It is not needed **just for the fuel time** (dropping fuel at the corridor's reactor end already gives 27.7 s on the current map). Cost: one new room to build and review, and a layout pass. Owner decision.
