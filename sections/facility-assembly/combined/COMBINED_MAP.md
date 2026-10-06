# Combined map (new scene, built room by room)

Status: **work in progress, unreviewed, not accepted.** This is the scene that replaces the retiring `facility_environment.blend`
(see `AGENTS.md`, owner plan 2026-10-03). The old map file is not touched.

Spec followed: the layout proposal drafted with the owner on 2026-10-04, `design/facility-layout/README.md` (plan v7) and
`design/facility-layout/front-end-area/DESIGN.md`. Rooms are added **one at a time**; the next room is added only after the owner's OK.
Nothing is guessed: each placement cites the source that fixes it. Where the plan and the as-built front end disagree, the as-built
front end and DESIGN.md win, and the difference is recorded here.

Build: `blender --background --python build_combined_map.py -- --through <room-key>` writes `combined_map.blend`, which links the source
modules (they are never edited). Frame: plan metres, +x east, +y north, origin at the reactor centre.

## Rooms added so far

| # | Room | Source | Placement (plan) | Status |
|---|---|---|---|---|
| 0 | Front-end area (cafeteria, hall, yard) | `sources/front-end-area/front_end_area.blend`, `MODULE_front-end-area` | translation (8, -80), rotation 0. As built: local origin = spawn exit, plan = local + (8, -80) | built, unreviewed (see PR) |
| 1 | Spawn room | `sources/spawn-room/module.blend`, `MODULE_spawn-room` | translation (8, -92.38), rotation 0 | **added, awaiting owner OK** |

### Room 1: spawn room, what fixes the placement
- `DESIGN.md`: "Compared with plan v7 the 6 m connectors are gone ... That moves the spawn 12 m north", spawn exit on the reactor axis x = 8, exit
  2.6 m wide into the cafeteria. Plan v7 has the spawn at y -105.4 to -92; moved 12 m north is y -93.4 to -80.
- Measured in the module (headless Blender): outer 17.4 x 13.4 m, exit on +Y, airlock leaves at local (0, 9.3), the 3.4 m wide service stub ends
  at local y 12.38 to 12.46 (the old map's "spawn clean-route portal", `fix_spawn_transition.py`). Placing the stub end on the cafeteria south
  wall gives spawn y from -93.3 to -80.0, which is exactly the 12 m shift, so the stub end is the join.
- Doorways follow the old map's established method (`ENVIRONMENT_BACKUP.md`): the room is linked through a membership wrapper that omits the 22
  airlock exclusions of `connections/access/DOOR_BINDINGS.json` (row `spawn_airlock`) and the four `SERVICE_end*` closures. 26 objects omitted,
  1,916 kept. The source module is unchanged.
- The cafeteria already has the 2.6 m "ARRIVAL AIRLOCK" opening in its south wall (front-end build), so nothing in the front end was edited.
- Evidence (480p, Cycles, eye level): `renders/01_spawn_to_cafeteria.png`, `renders/01_cafeteria_to_spawn.png`, plan cutaway
  `renders/01_spawn_plan_cutaway.png`.
- Deviation from plan v7: spawn centre x. v7 draws the spawn door at x = 9; the as-built front end and DESIGN.md put the reactor axis and the exit at
  x = 8, so the spawn is at x = 8.
- Not checked: lighting balance between the two modules (each keeps its own lights), collision, door state animation, performance.

## Remaining rooms in plan order (not yet added)
Yard-side: mountain/mine (R39). Hall-side: refinery (left), spine to reactor (middle), east trunk to dock and waste (right). Then medical, reactor,
turbine, electrical, waste, cooling, fuel corridor, compliance dock, outer ring and gantry.
