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
| 2 | Mine (R39) | `sources/mine-r39/module_r39_aaa.blend`, `MODULE_mine-r39` | translation (-14.4, -41.0), rotation 0 | added, awaiting owner OK |
| 3 | Refinery | `sources/refinery/module_overhaul_R1.blend` (17 root collections of the overhaul scene) | translation (-26.28, -52.2), rotation 90 | **added, awaiting owner OK** |

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
- Mine surface still removed, because the front-end yard is the surface depot: apron mud, yard puddles, yard ground fog and the 13 asset-source templates parked at
  the module origin (28 objects omitted); 26 straddling meshes (rails, sleepers, tunnel floor and similar) trimmed by deleting faces east of the mouth and outside the shed;
  `R39 | Cobwebs` (not a plain mesh) kept whole. 46 shed objects kept. The mountain (R40) is kept whole. The mine's sun lamp is kept.
- **Shed vs yard, resolved (owner chose option 1: the shed replaces the yard props under it).** In the combined scene the front end loses the objects centred inside the shed
  footprint: `lamp_room_cabin` and its sign, tag board, door light and stains; both `ore_bay` with piles, signs and stains; the three `ore_cart` and their signs; `pole_0`,
  `pole_3` and their lights; `vent_fan`; `floor_bay_no_0`; nine ballast stones (37 objects). The yard's `rail_rails` and `rail_sleepers` are clipped through the footprint
  (2,530 and 683 faces) so only the mine's rail runs through the shed. The portal collar, rock face, its signage, ground pads and the rest of the yard are untouched. The
  front end now has no lamp room, ore bays or ore carts at the portal; its design notes (DESIGN.md section 3) still list them, so the owner should say whether they move
  elsewhere in the yard or stay dropped.
- Build note: linked objects report an identity world matrix until they pass through a scene, so the patches use `wm()` (the object's own transforms). An earlier build used
  matrix_world and wrongly dropped many mine props and lamps; fixed.
- Evidence (768x432, Cycles, 32 samples): `renders/02_mine_yard_to_portal.png`, `renders/02_mine_yard_overview.png`, `renders/02_mine_tunnel_to_yard.png`.
- Open and not fixed: the mine's mountain (R40) runs plan y -123 to -20, wider than v7's -104 to -60. Its north end will meet the cooling plant (x -57 to -44,
  y -30 to -15), the yard-to-cooling link and the mine-water pipe when those are placed; trim it then. The mine rail and the yard rail overlap
  only at the mouth (mine rail trimmed there); the rails look continuous in the renders but the heights were not measured.
- Not checked: lighting balance (the tunnel is dim next to the warm yard), collision, rail height match, performance. 4 M triangles on top of the front end.

### Room 3: refinery, what fixes the placement
- Plan checked first: `design/facility-layout/README.md` (plan v7, drafted with the owner; its status line still says proposal, not reviewed or accepted) and `front-end-area/DESIGN.md`.
  v7 puts the refinery on the line yard (freight in) to refinery to fuel corridor (fuel out), x -33.7 to -18.9, with the hall colonnade arriving at its east wall.
- Source: `module_overhaul_R1.blend` (R24 reviewed 99.10, "done and dusted" by owner; the R25 finish #76 on top is unreviewed). It is the complete room (module plus overhaul), so
  every root collection of its scene is linked except the duplicate `MODULE_refinery` wrapper and the review cameras. Hidden state travels per object. The file is not edited.
- Rotation 90 degrees: the module's freight door (`Door_Mine`, west wall at module (-7.51, -4.08)) goes to the south wall, the fuel door (`Door_Reactor`, east wall) to the north wall,
  the personnel door (`Door_Entry`, south wall at module (-1.8, -6.43)) to the east wall. Same rotation as `LAYOUT_A12.json`.
- Position, each from a measurement: freight door x = yard freight gate centre, x -22.2 (posts -23.9 to -20.5; DESIGN.md "turns north at x = -22.2") gives x = -26.28; personnel door y =
  colonnade centre line y -54 (`colonnade_floor` y -55.5 to -52.5) gives y = -52.2. Cross-check, not used to fit: the east outer face lands at x -18.95 against the colonnade end at -18.9,
  and the x range -33.75 to -18.95 matches v7's -33.7 to -18.9.
- **Deviation from v7:** y range is -61.2 to -43.6 (outer, with door sills), v7 drew -57.6 to -40.4, so the refinery is 3.6 m further south. v7 assumed door positions; the as-built
  gate and colonnade fix them. Consequence for later: the fuel corridor's start (v7 (-22.2, -40.4)) is now at y -43.6, 3.2 m closer to the refinery.
- **Railway (owner preference: the mine's, not the courtyard's).** The yard's `rail_*` objects and all `ballast_*` stones are removed (55 yard objects with the earlier shed clearance).
  The mine's own track (kept whole, no longer trimmed at the shed) is extended: its last 4.92 m segment (rails, sleepers, ironwork; level) is copied end to end: 4.2 m straight, a 4 m radius
  quarter turn onto x -22.2 (rails sliced every 0.25 m and bent, sleepers and ironwork placed rigidly), then 6.0 m north to the freight door at y -60.0. 16.5 m, 12 new objects.
  The refinery's own rail picks up inside the door. The yard's track scale stays on the line.
- Yard changes needed to fit: the two loading dock platforms (`dock_west`, `dock_east`) ran past the refinery's south wall (plan y -60.1) by up to 1.5 m and are cut at the wall (local copies).
  The north fence line (y -60.1) coincides with the refinery's south wall face; fence panels were left in place.
- Evidence (768x432, Cycles, 32 samples): `renders/03_refinery_yard_to_gate.png`, `03_refinery_rail_turn.png`, `03_refinery_rail_overhead.png`, `03_refinery_colonnade_door.png`,
  `03_refinery_freight_door_in.png`.
- Not checked: refinery interior lighting against the dusk yard, rail height against the refinery's inner rail, the yard fence panels sitting against the wall, collision, performance;
  the fuel corridor, personnel interior route and refinery roof against the colonnade roof were not inspected beyond the renders. Unreviewed.

## Review pass (renders in `renders/review/`, 33 views of the scene through room 3)
Cycles, 28 to 36 samples, 768x432 or 960x540, night world. Cameras that landed inside geometry were discarded or re-shot; one interior angle (refinery NW) was dropped as unusable.
Prefixes: `join_` connected areas, `new_` areas not shown before, `overview_` whole-scene, `risk_` places that look wrong or unfinished.

What works: spawn airlock to hall sightline (`join_01`), cafeteria west door to yard and shed (`join_02`), shed to tunnel and the tunnel itself (`join_03`, `join_04`), the rail
from shed through the turn into the refinery (`join_09`, `join_10`), colonnade to the refinery personnel door (`join_05`, `join_06`), refinery interior (`join_07`, `join_08`).

Defects and open items found, none fixed yet:
1. **Shed blocks the yard's north-west service gate path** (`risk_12`). DESIGN.md keep-clear: x -47.4 to -44.8, y > -68.8 (to the cooling-plant door). The shed (plan x -54.0 to -36.3, y -78.6 to -61.0)
   covers that path from y -68.8 up to the fence. The owner requires the shed, so the path or the gate needs a decision (move the gate, route round the shed, or accept the gate leading into the shed).
2. **Brown yard cliff against the grey mine mountain** (`risk_02`, `risk_11`): different rock materials and a hard vertical seam where the yard's cliff face butts the mine's flat grey wall.
3. **Mine mountain is a flat, very large, repetitive wall** (`risk_02`, `risk_03`), running plan y -123 to -20; it will collide with the cooling plant area (see room 2 notes).
4. **Evacuation gate sign is a blank mint rectangle** (`risk_01`, `risk_10`) in the front-end build (`sign_evac_gate`); other signs in the same atlas render their text.
5. **Refinery fuel door opens onto nothing** (`risk_04`) until the fuel corridor is placed; refinery west wall and roof are plain and very dark at night (`risk_05`, `risk_06`).
6. **Doors to rooms not placed yet** open to black: medical (`risk_09`), hall spine and east trunk, colonnade-side ground (`risk_07`).
7. **Front-end `directory_totem` in the cafeteria has a blank back face** (seen in the cafeteria render from the hall opening), a plain lilac slab in the aisle sightline.
8. **Spawn room exterior is flat saturated colour boxes** against the cafeteria's south wall (`new_07`).
9. **Tunnel far end is a dark timber barricade** at x -107 (`risk_08`); fine as a dead end, very dark.
10. Night exterior is very dark overall; the world beyond the front end's ground plane is empty black.

## Remaining rooms in plan order (not yet added)
Hall-side: spine to reactor (middle), east trunk to dock and waste (right). Then medical, reactor,
turbine, electrical, waste, cooling, fuel corridor, compliance dock, outer ring and gantry.
