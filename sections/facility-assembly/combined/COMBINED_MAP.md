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
| 1 | Spawn room | `sources/spawn-room/module.blend`, `MODULE_spawn-room` | translation (8, -92.38), rotation 0 | added, awaiting owner OK |
| 2 | Mine (R39) | `sources/mine-r39/module_r39_aaa.blend`, `MODULE_mine-r39` | translation (-14.4, -41.0), rotation 0 | **added, awaiting owner OK** |

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

### Room 2: mine, what fixes the placement
- Source: the wooden `R39 | Old mine` set (not the concrete "Gullet Mine", which is DO NOT USE), AAA mood file, 4.08 M triangles, owner asked to keep the detail
  (`sources/mine-r39/AAA_FINISH.md`). Not independently reviewed.
- Join, both measured: the mine tunnel runs west, as does the yard portal, so no rotation. Tunnel centre line (module y -29.0) goes on the yard mine lane
  (plan y -70, DESIGN.md "mine axis"); the first timber set (module x -39.0) goes on the end of the yard portal mouth (front-end local x -61.4,
  plan -53.4). Translation = (-14.4, -41.0, 0). The tunnel then runs 41 m west to plan x about -95 and a far bulkhead at -107, inside v7's mountain (x -112 to -56).
- Front-end stand-ins removed, because the real mine replaces them (done in the combined scene only; source files unchanged):
  `portal_void` (dark box closing the mouth), `mountain_mass` (8-vertex rock box filling x -90 to -56, which sealed the tunnel) and the 420 faces
  of `cliff_face` that form the rock plate closing the portal stub (a local copy of `cliff_face` with those faces cut). Ray test along the mine lane at
  heights 0.6, 1.7 and 3.0 m: clear from the yard to the far bulkhead (open at eye height).
- **Owner requirement: the portal shed in front of the mine stays.** Kept: the `R39 | Portal shed` and `R39 | Shed floor` collections and every object inside the
  shed footprint (module x -39.6 to -21.9, y -37.6 to -20.0 = plan x -54.0 to -36.3, y -78.6 to -61.0), with the rail running through it. 17 shed objects kept whole.
- Mine surface still removed, because the front-end yard is the surface depot: apron mud, yard puddles, yard ground fog, and lamps and props outside the shed
  (175 objects omitted, including 13 asset-source templates parked at the module origin); 26 straddling meshes (rails, sleepers, tunnel floor and similar) trimmed by
  deleting faces east of the mouth and outside the shed; `R39 | Cobwebs` (not a plain mesh) kept whole. The mountain (R40) is kept whole. The mine's sun lamp is kept.
- **Conflict, not resolved: the shed overlaps the yard's own objects.** The shed footprint contains the yard's `lamp_room_cabin`, `ore_bay_0/1`, `ore_pile_0/1`, `ore_cart_0/1/2`,
  `pole_0`, `pole_3`, `vent_fan` and the portal collar (`portal_pier_L/R`, `portal_lintel`, `portal_cap`, `mouth_roof`); `boulder_11` and the site pickup clip its edges.
  Nothing was removed or moved yet. Options: drop the overlapping yard props, shift the shed east of the collar, or accept the overlap.
- Evidence (768x432, Cycles, 32 samples): `renders/02_mine_yard_to_portal.png`, `renders/02_mine_yard_overview.png`, `renders/02_mine_tunnel_to_yard.png`, `renders/02_mine_mountain_wide.png`.
- Open and not fixed: the mine's mountain (R40) runs plan y -123 to -20, wider than v7's -104 to -60. Its north end will meet the cooling plant (x -57 to -44,
  y -30 to -15), the yard-to-cooling link and the mine-water pipe when those are placed; trim it then. The mine rail and the yard rail overlap
  only at the mouth (mine rail trimmed there); no check that the rail heights match.
- Not checked: lighting balance (the tunnel is dark green-lit, the yard warm), collision, rail height match, performance. 4 M triangles on top of the front end.

## Remaining rooms in plan order (not yet added)
Hall-side: refinery (left), spine to reactor (middle), east trunk to dock and waste (right). Then medical, reactor,
turbine, electrical, waste, cooling, fuel corridor, compliance dock, outer ring and gantry.
