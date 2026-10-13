# Compact map assembly report (2026-10-13)

**Status: unreviewed, not accepted.** One agent session built, measured and reported this; no independent review, no owner approval of the result, no Unity run.
Task: `OPUS_ASSEMBLY_PROMPT.md` (take the compact map from "laid out" to "assembled"), widened by the owner during the session: *"you may shift around the entire map as you please and build as many things as needed ... One shot the most compact map possible without reinventing the individual rooms beyond recognition"*, then *"Ignore all previous specs and planning docs - build and decide what comes where on your own with the goal of the most compact and logical map possible. Do not ask me questions"*. After the first assembly pass the owner asked about the fuel run, asked for a grey-box test of a short fuel corridor (`GREYBOX_FUEL_TEST.md`) and then said *"yes do the rebuild to the same graphical fidelity as it was previously"*. This report describes the result: the **short fuel corridor layout**. The first pass's numbers are kept where they are compared.
Rooms are linked, never edited: every change below is a local copy made by `build_compact_map.py`, except the short fuel corridor, which is a new derived file (`sources/fuel-corridor/module_short_S1.blend`) built from F23ci by a script; F23ci itself is unchanged. "Done and dusted" rooms got no art pass; they got door cuts and closed leaves, which are layout work.

Contents: layout decision, door table, plates and dead ends, lighting, collision and walk test, performance, travel times, Unity, files, open decisions, what ran.

## 1. Layout decision

![plan](renders/assembly/19_assembly_plan.png)

*Plan cut at 1.1 m (condenser level at -5.0 m drawn light), green lines: the capsule lanes the walk test found, green dots: open doors, red bars: closed doors.*

What fixes what: the yard rail fixes the refinery; the refinery's fuel door fixes the fuel corridor's F01. In the first pass the corridor (F23ci, a fixed 38 m L) then fixed the reactor, so the reactor and the 34 m spine stayed put. The short corridor removes that constraint: its new east door F02E fixes the concourse, and the concourse fixes the reactor, which moves **18.7 m south**; every room that hangs off the reactor moves with it.

| Change | Why it is more compact or more logical |
|---|---|
| **Fuel corridor S1**: F23ci's north half (service bypass, plant header with S01, clean port S02, delivery leg, F02 adapter) removed and closed with a concrete wall and two shallow lined alcoves; the corridor's own waste-transfer door assembly moved to the east turn's east wall as the reactor door **F02E**; the entry leg one 1.47 m wall bay shorter. All visible parts are F23ci's own geometry, materials, lights and dressing (`sections/fuel-corridor/blender/build_short_corridor.py`). | The corridor's freight path drops from 38 m to about 26 m and it no longer pushes the reactor north. 1.65 M evaluated triangles instead of 3.10 M. |
| **Reactor cluster 18.7 m south** (reactor, turbine, electrical, condenser bay, condenser stair, cooling; their relative positions unchanged) | The north edge drops from y 39.7 to 21.0. Every trip through the spine is 18.7 m shorter. |
| **Concourse rebuilt** in front of the corridor (x -5.46..5.85, y -38.3..-33.5, 5.9 m high, same shell, materials and lamps as before): F02E on its west wall, the spine on its east side, the tunnel to the reactor south door on its north side | One junction joins the fuel run, the front end and the reactor. |
| **Spine shortened from 33.5 m to 14.8 m**: its end door, frame and last bay's rib, beam and lamp moved with the reactor, the five bays between left out, the walls, dado, floor, roof and route line clipped | The front end's spine is the one long hall left; it is now a short street with the dock on one side and the concourse at its end. |
| **Waste on the reactor's east wall**, through a new 2.84 x 3.2 m opening cut through the wall's 4 m patch panel (which stays as the jambs and head), with a threshold in the hall's own floor material | The reactor already had a panel there. Waste is one door from the reactor floor (22.6 m from the core) instead of 30 m through the spine. |
| Kept from the first pass: electrical on the turbine's east flank, the condenser stair from the turbine's west wall, the dock on the spine's east wall, cooling on the reactor west stub, the closed dead-end doors | |
| Dropped: the S03 transfer hall and the spine's waste door (the corridor and the waste position they served are gone); fuel S01 and S02 (removed with the corridor's north half) | |

Footprint of the buildings (plan cut at 1.1 m, the mine's mountain excluded; box and convex hull computed by the same script for every row):

| | Extent | Box | Hull |
|---|---|---|---|
| before the assembly pass | x -53.6..54.1, y -93.1..56.6 | 16,130 m2 | 10,201 m2 |
| first assembly pass | x -53.6..37.3, y -93.1..39.7 | 12,080 m2 | 8,981 m2 |
| grey-box test | x -53.6..37.3, y -93.1..19.1 | 10,207 m2 | 7,508 m2 |
| **short fuel corridor layout (now)** | x -53.6..37.3, y -93.1..21.0 | **10,380 m2** (-14 % on the first pass, -36 % on the start) | **7,640 m2** (-15 %, -25 %) |

(The hull figures of the first pass and the grey-box test were reported as 8,969 and 7,494 m2 earlier; recomputed here with one script, they are 8,981 and 7,508.)
`check_footprints.py` (20 footprints): the only overlap >= 0.5 m is the corridor entry against the refinery's rough bounding box (the corridor starts at the refinery's recessed fuel-door sill), as before. `check_overlaps.py` on the plan cut at 8 heights (`validation/overlaps.txt`): no intrusion between rooms. The new hits it lists are the reactor's rectangle (its corner stubs reach x 12.8 and y -12.6) against waste and the corridor; direct checks on the cut found **no reactor geometry east of x 11.62** where waste starts and **none south of reactor-local y -11.62** west of the tunnel, where the corridor's north wall stands at -12.07 (0.47 m gap). The rest are the reactor south tunnel, the condenser's U04 receive into the turbine floor and the front end's L-shaped outline, as before.

Placements (plan metres, rotation about z):

| Room | Translation | Rot | Fixed by |
|---|---|---|---|
| fuel corridor S1 | (-22.2, -43.6, 0) | 0 | F01 on the refinery north fuel door (unchanged); F02E lands at (-5.46, -36.62) |
| reactor | (0, -18.7, 0) | 0 | concourse y RY-19.6..RY-14.8 holds F02E; south wall (RY-11.6) 0.47 m clear of the corridor's north wall (-30.77) |
| turbine / condenser bay | (0, -4.2, 0) / (1.6, 3.2, -6) | 0 | reactor north stub end (reactor-local y 14.5); condenser at turbine + (1.6, 7.4, -6) |
| electrical (R11) | (10.5, 14.3, 0) | -90 | D01 face on the turbine east wall outer face at turbine-local y 18.5 (bay between columns at 16 and 21) |
| cooling | (-14.5, -18.7, 0) | 90 | reactor west stub end |
| waste (AAA) | (11.94, -14.84, 0) | -90 | WS_RECEIVING exterior face (module y -0.32) on the reactor's east outer face x 11.62; opening centre reactor-local y 3.86, between the lockers (to y 2.42) and the column plinth (from y 5.29) |
| compliance dock (R1) | (12.15, -40.39, 0) | -90 | P1 corridor start on the spine east face (unchanged) |
| front end, spawn, mine, refinery, medical | unchanged | | COMPACT_MAP.md, COMBINED_MAP.md |

## 2. Doors (`validation/doors.json`, 32 doors, `DOOR_<id>` anchors in the scene)

Default state when the map opens: each door's contract default where it has one, otherwise open when it leads somewhere and closed when it leads outside. Every door has an anchor empty (door id, owner room, kind, default state, states `open,closed,locked`, where it leads, clear size, leaf) and, in COLLIDERS, a trigger threshold and a solid blocker that is enabled while the door is closed or locked. Visual leaves for the non-default state are the room module's own objects (named in the doors file); this pass does not animate them.

| Door | Owner | Plan (x, y, z) | Clear w x h | Kind | Default | Leads to |
|---|---|---|---|---|---|---|
| SPAWN_EXIT | front end | (8.00, -80.00, 0) | 2.58 x 2.60 | airlock | open | spawn |
| CAF_YARD | front end | (-7.27, -70.00, 0) | 3.00 x 2.51 | double sliding | open | yard |
| CAF_MEDICAL | medical | (26.00, -70.00, 0) | 2.20 x 2.50 | sliding pressure leaves | open | cafeteria |
| HALL_WEST | front end | (-3.97, -54.00, 0) | 2.32 x 2.60 | double leaf | open | refinery colonnade |
| HALL_SPINE | front end | (8.00, -48.50, 0) | 3.60 x 3.20 | blast door | open | spine |
| HALL_EAST | front end | (31.97, -54.00, 0) | 2.32 x 2.60 | double leaf | **closed** | outside |
| MINE_PORTAL | mine | (-53.40, -70.00, 0) | 7.20 x 3.90 | portal | open | yard |
| YARD_SERVICE | front end | (-46.00, -60.15, 0) | 2.40 x 2.35 | single leaf | **closed** | outside |
| YARD_FREIGHT_GATE | front end | (-22.20, -60.10, 0) | 3.10 x 3.10 | sliding gate | open | refinery freight door |
| REFINERY_FUEL | fuel corridor | (-22.20, -43.60, 0) | 2.60 x 3.00 | boundary double leaf | open | refinery (F01 leaves left out) |
| **FUEL_F02E** | fuel corridor | (-5.46, -36.62, 0) | 2.38 x 3.00 | double leaf (the S03 door, moved) | open | concourse (leaves left out) |
| REACTOR_S | reactor | (0.00, -30.90, 0) | 5.00 x 5.00 | wall cut | open | concourse |
| REACTOR_N | reactor | (0.00, -4.30, 0) | 5.00 x 5.00 | stub double door | open | turbine D01 |
| REACTOR_W | reactor | (-14.40, -18.70, 0) | 5.00 x 5.00 | stub double door | open | cooling P01 |
| REACTOR_SE | reactor | (11.00, -29.70, 0) | 5.00 x 5.00 | stub double door | **closed** | outside |
| **REACTOR_E_WASTE** | reactor | (11.20, -14.84, 0) | 2.84 x 3.20 | new opening through the patch panel | open | waste |
| TURBINE_D01 | turbine | (0.00, -4.20, 0) | 2.40 x 2.70 | opposed sliding | open | reactor N stub |
| TURBINE_D02 | turbine | (0.00, 19.80, 0) | 2.40 x 2.70 | opposed sliding | **closed** | outside (32 leaf objects moved shut) |
| TURBINE_E_ELECTRICAL | turbine | (10.12, 14.30, 0) | 2.40 x 2.70 | new opening | open | electrical D01 |
| ELECTRICAL_D01 | electrical | (10.50, 14.30, 0) | 2.40 x 2.70 | sliding pair | open | turbine |
| ELECTRICAL_D02 | electrical | (26.90, 14.30, 0) | 2.40 x 2.70 | sliding pair | **closed** | outside (74 leaf objects moved shut) |
| TURBINE_W_STAIR | turbine | (-4.12, 9.25, 0) | 2.00 x 2.60 | new opening | open | condenser stair |
| CONDENSER_D01 | condenser | (1.60, 3.20, -6) | 2.00 x 2.40 | opposed sliding | open | stair corridor |
| COOLING_P01 | cooling | (-14.50, -18.70, 0) | 5.00 x 5.00 | overhead folding shutter | open | reactor W stub |
| WASTE_RECEIVING | waste | (11.94, -14.84, 0) | 3.00 x 3.20 | rolling shutter | open | reactor (east opening) |
| WASTE_PERSONNEL | waste | (14.34, -21.00, 0) | 1.20 x 2.30 | hinged, outward | **closed** | outside (leaf turned into the frame) |
| WASTE_DISPATCH | waste | (29.94, -14.84, 0) | 2.40 x 2.80 | rolling shutter | **closed** | outside (new 36-slat curtain) |
| DOCK_P1 | dock | (11.15, -40.39, 0) | 2.40 x 2.60 | sliding (X) | open | spine |
| DOCK_P2 | dock | (27.95, -40.39, 0) | 4.60 x 3.50 | blast leaves | **closed** | outside (arrival, contract default sealed) |
| SPINE_NORTH_END | front end | (8.00, -33.25, 0) | 3.30 x 3.30 | single leaf | **closed** | outside (moved with the spine end) |
| **SPINE_W_CONCOURSE** | front end | (6.00, -35.90, 0) | 4.80 x 4.20 | opening (wall split out) | open | concourse |
| SPINE_E_DOCK | front end | (10.00, -40.39, 0) | 2.60 x 2.60 | new opening | open | dock |

Removed against the first pass: FUEL_F02, FUEL_S01_PLANT, FUEL_S02_CLEAN, FUEL_S03_WASTE (the corridor's north half), SPINE_E_WASTE and SPINE_W_TRANSFER. Doors that need an owner decision: none blocks play; see section 10.

## 3. Plates and dead ends

All three `PLACEHOLDER_*` plates are gone (first pass). Turbine D02, electrical D02 and the waste personnel door are closed with their own leaves, waste dispatch with a new roller curtain; the reactor SE stub keeps its own door; the spine's end door is closed and now opens onto the 3 m gap between the spine end and the reactor's south wall. The short corridor's cut north wall carries two shallow alcoves (the bypass and delivery mouths), backed by copies of the corridor's own lined wall bay; they are dressing, not dead-end routes. The condenser bay is reached by the stair (34 risers of 0.176 m on 0.300 m goings, 30.5 degrees, 2.1 m clear, handrails both sides; corridor 2.48 x 2.7 m at z -6 for 11.9 m), moved with the turbine. Remaining walkable dead ends: none.

## 4. Lighting (`validation/lighting.json`, `measure_lighting.py`)

Method: 19 views at 1.6 m eye height in every junction, Cycles CPU 640 x 360, 14 spp, denoised, the scene's own view transform (Khronos PBR Neutral, exposure 0.5) and lights; measured on the image as displayed. My bar (not an art-direction rule): median luma >= 0.15, near-black (< 0.04) <= 25 %, clipped (any channel > 0.98) <= 5 %. Views that moved with the reactor keep their reactor-local positions; new: `reactor_to_waste`, `fuel_F02E_to_concourse`, `fuel_corridor_east`; gone: `spine_to_waste`, `transfer_hall`.

| View | Median | P10 | Near-black | Clipped (any / white) | Result |
|---|---|---|---|---|---|
| reactor N stub (to turbine) | 0.714 | 0.388 | 0 % | 2.5 % / 0.0 % | ok |
| turbine entry | 0.363 | 0.064 | 6 % | 1.3 % / 0.0 % | ok |
| turbine east aisle to electrical | 0.443 | 0.182 | 1 % | 0.4 % / 0.0 % | ok |
| electrical inside | 0.544 | 0.172 | 1 % | 2.7 % / 0.0 % | ok |
| reactor W stub to cooling | 0.538 | 0.196 | 3 % | 3.8 % / 0.1 % | ok |
| cooling inside | 0.574 | 0.177 | 0 % | 3.1 % / 0.8 % | ok |
| **reactor to waste (east opening)** | 0.319 | 0.146 | 4 % | 0.2 % / 0.0 % | ok |
| waste inside | 0.282 | 0.130 | 5 % | 1.0 % / 0.0 % | ok |
| spine to dock | 0.386 | 0.196 | 1 % | 0.2 % / 0.0 % | ok |
| dock inside | 0.246 | 0.057 | 5 % | 1.0 % / 0.0 % | ok |
| **concourse** | 0.617 | 0.314 | 0 % | 2.4 % / 0.7 % | ok |
| spine (mid, towards the end door) | 0.470 | 0.253 | 0 % | 5.8 % / 0.0 % | marginal hot (the spine end door's glowing panel, now 18.7 m closer) |
| reactor from the south door | 0.505 | 0.267 | 1 % | 3.6 % / 2.3 % | ok |
| **fuel corridor F02E to the concourse** | 0.390 | 0.046 | 8 % | 1.2 % / 0.0 % | ok |
| **fuel corridor, east turn** | 0.292 | 0.084 | 3 % | 0.1 % / 0.0 % | ok |
| stair top | 0.720 | 0.489 | 0 % | 2.9 % / 0.0 % | ok |
| stair bottom | 0.769 | 0.627 | 0 % | 1.8 % / 0.0 % | ok |
| condenser D01 | 0.792 | 0.347 | 0 % | 2.1 % / 0.0 % | ok |
| condenser inside | 0.466 | 0.227 | 1 % | 1.2 % / 0.0 % | ok |

Findings: **18 of 19 views pass; nothing is too dark to read.** The new junctions read well: the concourse 0.62 median, the corridor's east turn 0.29 and its F02E view 0.39 (F23ci's own lighting), the reactor's east opening into waste 0.32. The one miss is the spine looking at its end door, 5.8 % of pixels with one channel clipped (0 % white): the front end's own end-door panel glows (the source spine renders the same, checked on `front_end_area.blend`), and the shorter spine brings it closer. Both reactor views that were marginally hot in the first pass now pass (2.5 % and 3.6 %), most likely because the reactor's merged meshes are no longer stripped by the old splitter and the cut pieces have their materials (not isolated by a separate test). No light was added or changed for this layout (`FILL_LIGHTS`, `EMISSION_OVERRIDES` and `HALL_LIGHT_SCALE` are empty; the first pass's transfer-hall overrides went with the hall). Not measured: dynamic exposure in the engine, animated screens, the exterior at night.

## 5. Collision and navigation (`assembly_colliders.py`, `walk_test.py`)

Proxies (COLLIDERS collection, hidden; `validation/colliders.json`): 117, for the spine (14.8 m, dock door east, concourse west), the concourse (its west wall with the F02E gap), the reactor south tunnel and N/W stubs, the reactor-waste, spine-dock and turbine-electrical junctions (floor plates, heads, jambs, the dock P1 tube), the condenser stair (landing, a 30.5-degree ramp, shaft, lower corridor), plus a trigger threshold and a solid blocker on each of the 32 doors (blockers enabled while closed). Roles: floor 12, wall 29, roof 11, ramp 1, door_threshold 32, door_blocker 32. Rooms keep their own collision; the proxies stop at each room's door plane.

Capsule walk test (radius 0.40 m, height 1.80 m, step offset 0.35 m; floor ray every 0.1 m, seven spheres from 0.75 to 1.40 m; sideways lane search up to 1.5 m with continuity):

| Run | Result |
|---|---|
| visual meshes, 18 routes (`validation/walk_report.json`) | **17 pass**. Fail (as in the first pass): yard -> refinery freight door, blocked by the refinery's parked ore cart and tipper in the doorway (a cart route; players reach the refinery through the hall colonnade, which passes). |
| visual meshes, 8 closed doors | **8 block** (turbine D02, electrical D02, waste dispatch, waste personnel, reactor SE, hall east, dock P2, spine north end) |
| collision proxies only, 9 hall / stub / junction / stair routes (`validation/walk_report_colliders.json`) | **9 pass**; the same 8 closed doors block |

New routes: the fuel run through the short corridor (on the freight gate's centre, and on the shortest clear line), reactor -> waste through the east opening, spawn -> waste.

## 6. Performance (`perf_report.py`, `validation/perf_report.json`)

No frame rate was measured: there is no runtime build. Static counts of the evaluated scene (Blender 5.2.2, viewport evaluation, instances counted):

| | Triangles | Objects | Submeshes (draw calls before batching) | Lights (shadowed) | Textures |
|---|---|---|---|---|---|
| **whole map now** | **11,015,587** | 23,416 | 25,495 | 434 (396) | 110 images, 1,014 MB as RGBA8 with mips |
| first assembly pass | 12,500,244 | 23,758 | 26,251 | 462 (424) | same |

Per room (400k is the repository's per-room flag, 800k the front end's design budget): mine 3.31 M, **fuel corridor 1.64 M** (F23ci was 3.10 M), reactor 1.22 M, electrical 0.77 M, medical 0.60 M, front end 0.56 M, refinery 0.46 M, spawn 0.43 M, condenser 0.42 M, turbine 0.42 M, dock 0.42 M, waste 0.37 M, cooling 0.35 M; concourse, stair and signs 0.04 M. Ten rooms are over the flag.

Proposals (not built):
1. **Streaming by room**, using the portal graph from the door table. Worst-case visible sets through open doors: front end 5.80 M (it sees the mine, refinery, medical and spawn), mine 3.87 M, the concourse 3.43 M (corridor, front end and reactor), refinery 2.66 M, turbine 2.41 M, reactor 2.38 M (it no longer sees the whole corridor: was 5.10 M), fuel corridor 2.11 M (was 4.79 M); every other room under 1.6 M. The mine (tunnel / surface) is the one left to split.
2. **LODs** first where one mesh is heavy: mine `R39 | Gravel tunnel` 444k, `R40 | Mine cliff` 352k, boulders 66 to 98k each (they share mesh data, so one LOD set serves all copies).
3. **Batching**: unique meshes nearly equal objects in the overhauled rooms, so instancing buys little; static batching by material per room would cut 25k submeshes to roughly the material count per room.
4. **Lights**: 396 shadow-casting lights; the reactor carries 117 and the mine 64. Bake or limit shadows per room before any frame-rate test (baking is the last step and needs accepted lighting first).

## 7. Travel times (`validation/walk_report.json` lane lengths)

Walking 4.5 m/s, loaded cart 1.5 m/s (README assumptions). Distances are the continuous lanes the capsule actually walked, not straight lines. The fuel-run routes start 2.9 m inside the refinery, as in the first pass.

| Route | Lane now (m) | Walk (s) | Cart (s) | First pass (m) |
|---|---|---|---|---|
| spawn -> reactor floor | 71.6 | 15.9 | | 90.2 |
| spawn -> mine portal | 83.3 | 18.5 | | 83.3 |
| medical -> reactor floor | 76.5 | 17.0 | | 95.0 |
| reactor floor -> electrical (through the turbine) | 45.0 | 10.0 | | 45.0 |
| reactor floor -> condenser bay (stair) | 54.6 | 12.1 | | 54.6 |
| reactor floor -> cooling | 15.0 | 3.3 | | 15.0 |
| reactor floor -> waste receiving door | 22.6 | 5.0 | | about 30 (33.7 to 3.9 m inside waste) |
| reactor floor -> dock (3.4 m past P1) | 30.4 | 6.8 | | 48.9 |
| refinery fuel door -> corridor F02E (reactor-side port) | 29.2 | 6.5 | **19.5** | 41.6 to F02 (27.7 s) |
| refinery fuel door -> reactor south door | 39.4 | 8.8 | 26.3 | 56.8 (37.9 s) |
| **refinery fuel door -> reactor floor by the core (fuel run end to end)**, cart on the freight gate's centre | **46.0** | 10.2 | **30.7** | 62.9 (41.9 s) |
| the same on the shortest clear line (inside the gate's south post, diagonal across the concourse) | 41.4 | 9.2 | 27.6 | |
| hall -> refinery (colonnade) | 31.6 | 7.0 | | 31.6 |
| cafeteria -> medical | 23.0 | 5.1 | | 23.0 |
| spawn -> electrical (farthest station) | 141.8 | 31.5 | | 160.9 |
| spawn -> waste (receiving door) | 93.9 | 20.9 | | |
| mine portal -> electrical (composed from walked lanes, as before) | about 189 | 42 | | 208 |

Against the README targets (adjacent 10 to 20 s, mine -> refinery 20 to 35 s, refinery -> reactor 15 to 30 s, full crossing under 60 s): the end-to-end fuel run is **30.7 s on the freight lane and 27.6 s on the shortest line** (the grey-box test predicted 28.1 s); to the reactor's south door it is 26.3 s and to F02E 19.5 s, all within 30 s except the freight-lane end-to-end figure, which is 0.7 s over. Adjacent stations from the reactor are all under 13 s; the full crossing is about 42 s.

## 8. Unity

`runtime/unity` is a source-only WP-01 foundation (Unity 6000.4.3f1, never opened for this map); there is no editor or licence in this environment and no approved map import route (`runtime/README.md`, game-asset-pipeline skill). So: **engine import, prefab binding, collision in engine and Player behaviour: Blocked (no editor); not claimed.**
What exists instead (`export/`):
* `compact_map_colliders_anchors.fbx` (338 KB): the 117 collision proxies, 32 door anchors and 13 room placement anchors with their custom properties. FBX because Unity imports it natively; no GLB importer is assumed. Settings in the manifest.
* Blender re-import check (an empty process): 162 objects exported, 162 re-imported, 0 missing, 0 extra, 0 bound mismatches over 1 mm (recorded in the manifest).
* `binding_manifest.json`: the A08 fields (source revision, export settings, scale/axes/origin, logical ids, room placements, collider roles, state variants, licensing). UNRESOLVED fields: per-room prefab mapping (no approved room export route), spawn/interaction point ownership, runtime owner of map collision and doors.

Readiness checklist for whoever opens the editor: 1. decide the room export route (FBX per room module, scale 1, -Z forward / Y up) and the runtime owner of doors (D-xx in DECISIONS_AND_RISKS); 2. import `export/compact_map_colliders_anchors.fbx` and confirm 117 proxies land on the room anchors; 3. bind `door_blocker` enable state to door state, `door_threshold` as triggers; 4. run the capsule routes of `walk_test.py` with the Unity CharacterController (radius 0.4, height 1.8, step 0.35, slope 45) and compare lane lengths; 5. profile against D-07 / D-09 once those budgets exist. No package was installed and no infrastructure was chosen.

## 9. What changed, files

* `sections/fuel-corridor/blender/build_short_corridor.py` (new) and its output `sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend` (LFS) with `module_short_S1.blend.json` (counts, ports, source hash). F23ci is not modified.
* `build_compact_map.py`: `RY` and every placement derived from it, the short corridor, `fold_spine`, `add_concourse` (replaces `build_combined_map.add_reactor_concourse` for this map), the reactor east opening and threshold, the new door rows, signs (`WASTE` over the reactor's east opening; the spine's waste and transfer signs gone), `scene['reactor_y']`; the S03 transfer hall and its lighting overrides removed.
* **`split_openings` fixed** (two defects of the first pass): every cut piece now keeps its source mesh's materials (the first pass's 230 cut pieces, and the 4 ground pieces of `hole_in_slab`, had none and rendered in Blender's default grey; the spine read white instead of the front end's pink plaster), and only the loose parts that reach into an opening are cut, inside the wall band (the first pass clipped whole meshes, so room-wide merged meshes lost a strip across the room: the reactor's south door split removed everything of those meshes within x -2.5..2.5 below z 5 across the whole hall). The pieces also keep the source object's transform (the first pass baked it into the mesh, which shifted Object-coordinate textures on the 13 cut objects whose origin is not at the module origin, all in the turbine). New helpers `clip_mesh` and a vertex-based `bbox` for local meshes.
* `assembly_colliders.py`, `walk_test.py`, `measure_lighting.py`, `check_footprints.py`, `draw_assembly_plan.py`, `perf_report.py` updated to the new layout (the scripts that run on a built scene read `scene['reactor_y']`). `greybox_fuel_test.py` is superseded (it refuses to run; use commit c25d102).
* Evidence: `validation/` doors, colliders, walk reports, lighting, performance, overlaps, `compact_report.json` (the hall audit, now with no halls to audit); `renders/assembly/19_*` (the first pass's `17_*` renders showed the old layout and were removed; they remain in the history); `export/`.
* `combined_map.blend` rebuilt from the final script. `build_combined_map.py`, `reactor_links.py` and every room source are unchanged.
* Deliberately not done: any art pass on a room (the short corridor's closures are plain closures from its own parts, not an art pass); a review of S1; the gantry (no attachment spec); baking; LODs; Unity.

## 10. Open decisions for the owner

1. **Short fuel corridor S1 needs a review** before it can be called anything but unreviewed: F23ci's 99 does not carry over. Its two north alcoves and the moved east-wall dressing are the parts to look at.
2. **Fuel run**: 30.7 s end to end on the freight lane (27.6 s on the shortest line, 26.3 s to the reactor's south door). Accept, or define the drop at the concourse.
3. **Refinery freight door is blocked to players** by the refinery's parked ore cart: intended (carts only) or should the cart park inside?
4. Hall east exit, yard service door: are they evacuation exits (runtime rule)? The spine's end door now closes onto a 3 m outdoor gap: keep it as an exit or wall it.
5. AAA finishes' own open items (condenser and waste reach checks in their `reach-check.json`) are untouched.
6. Performance: streaming split of the mine, LOD and shadow policy, once D-07 / D-09 budgets exist.
7. The spine end door's glowing panel (5.8 % clipped in the spine view): leave, or dim it locally.

## 11. What ran (exact)

Blender 5.2.2 LTS (downloaded to `/opt/blender52` in the container), headless. Every check below ran on the final `combined_map.blend` unless noted.
* `build_short_corridor.py` (once, output committed); the S1 triangle count was then recounted on the saved file (1,650,355; the script's own log said 1,132,567 from a stale depsgraph, fixed in the script and noted in the `.json`).
* `blender -b --factory-startup --python build_compact_map.py` (about 3 minutes; log: spine 6 moved, 20 left out, 7 clipped; reactor east opening 66 objects split; 32 door anchors; 117 colliders; stair 34 risers 30.5 degrees).
* `plan_cut.py` (8 heights: 0.4, 1.1, 1.8, 2.8, 4.5, -3.5, -5.0, -5.6) + `check_overlaps.py`; `check_footprints.py`; box and hull areas from the 1.1 m cut.
* `walk_test.py` (visual, 18 routes, 6 minutes) and `walk_test.py --colliders` (9 routes).
* `measure_lighting.py` (19 views).
* `perf_report.py`; `export_unity.py` (export + re-import in an empty Blender process).
* `validate_halls.py` (the older hall audit): `PASS (geometry audit only)` with **0 halls** (no `LINKS` hall is left in this layout; the concourse and spine are covered by the walk tests), written to `validation/compact_report.json`.
* `render_views.py` (12 evidence views) plus 14 of the lighting views copied as `19_walk_*`. Every image in `renders/assembly/19_*` was looked at; a stair-house exterior view rendered too dark at night to show anything and was not kept. Scratch renders were deleted.
Not run: Unity anything, a frame-rate test, an independent review, the room validators (including any validator on S1), a human playtest.
