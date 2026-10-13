# Compact map assembly report (2026-10-13)

**Status: unreviewed, not accepted.** One agent session built, measured and reported this; no independent review, no owner approval of the result, no Unity run.
Task: `OPUS_ASSEMBLY_PROMPT.md` (take the compact map from "laid out" to "assembled"), widened by the owner during the session: *"you may shift around the entire map as you please and build as many things as needed ... One shot the most compact map possible without reinventing the individual rooms beyond recognition"*, then *"Ignore all previous specs and planning docs - build and decide what comes where on your own with the goal of the most compact and logical map possible. Do not ask me questions"*. Before that instruction the owner had answered the three open questions (dead ends, condenser access, default door state) with "do the best you can for map flow", "reason it out and choose" and "your choice".
Rooms are linked, never edited: every change below is a local copy made by `build_compact_map.py`. "Done and dusted" rooms got no art pass; they got door cuts and closed leaves, which are layout work.

Contents: layout decision, door table, plates and dead ends, lighting, collision and walk test, performance, travel times, Unity, open decisions, what ran.

## 1. Layout decision (the "street" layout)

![plan](renders/assembly/17_assembly_plan.png)

*Plan cut at 1.1 m (condenser level at -5.0 m drawn light), green lines: the capsule lanes the walk test found, green dots: open doors, red bars: closed doors.*

What fixes what (measured, not chosen): the yard rail fixes the refinery; the refinery's fuel door fixes the fuel corridor (its fixed 10 / 14.2 / 14 m L must face that door); the corridor's far port F02 fixes the reactor's south side. So the reactor, the 34 m spine and the front block stay where they were, and every other room was packed onto that chain. Moving the reactor south would have needed the refinery 25 m into the yard and the rail rebuilt; I judged that "reinventing beyond recognition" and did not do it.

| Change | Why it is more compact or more logical |
|---|---|
| **Electrical** to the turbine's **east flank** (new 2.4 x 2.7 m door between the turbine's wall columns), instead of past the turbine's far end | Removes the 17 m northern lobe: the map's north edge drops from y 56.6 to 39.7. Generator hall -> switchgear stays one door apart. |
| **Waste** and the **compliance dock** into the **empty pocket east of the spine**, each on a new opening in the spine's east wall | They sat in a diagonal annex with two halls (waste) and 20 m east of the hall (dock). Now the spine is a street: dock (arrivals) and waste both open off it, and the east edge drops from x 54.1 to 37.3. The dock's sealed arrival P2 faces east, to the outside, as its contract wants. |
| **Fuel corridor S03 opened** onto a new 11.3 m transfer hall into the spine's west wall, opposite waste | Refinery -> fuel corridor -> spine -> waste is one straight line (the corridor's own "waste transfer branch" port), and a second link between the fuel run and the spine. |
| **Condenser bay reachable**: a stair from a new door in the turbine's west wall down 6 m (34 risers, 30.5 degrees) and an 11.9 m corridor under the turbine end to its D01 stub | It was a sealed room under the turbine. Now it is a station 12 s from the reactor floor. |
| Dead ends closed with their own leaves | Every door either leads somewhere or reads as closed. |
| Removed: 7 m diagonal waste hall, 3.9 m waste-to-spine hall, three placeholder plates | |
| Wayfinding: signs over the new doors (spine, turbine, electrical, transfer hall) and a floor stencil REACTOR / WASTE / DOCK in front of the spine door; the hall's old floor stencil and hanging "to dock" sign, which pointed at the now closed east exit, left out | One way to every station from the hall: through the spine. |

Footprint of the buildings (plan cut at 1.1 m, the mine's mountain excluded): **before** x -53.6..54.1, y -93.1..56.6 = 16,130 m2 box, 10,184 m2 hull; **after** x -53.6..37.3, y -93.1..39.7 = **12,080 m2 box (-25 %), 8,969 m2 hull (-12 %)**. `check_footprints.py`: 19 footprints, extent x -52..38, y -105..39 (was -52..54, -105..57); the only overlap >= 0.5 m is the old fuel corridor / refinery sill overlap of rough boxes. `check_overlaps.py` on the plan cut (8 heights): no intrusion involving electrical, waste, dock, the stair or the transfer hall; the remaining hits are the reactor south tunnel, the condenser's U04 receive into the turbine floor and the front end's L-shaped outline (a rectangle test cannot model it), all as before (`validation/overlaps.txt`).

Placements (plan metres, rotation about z):

| Room | Translation | Rot | Fixed by |
|---|---|---|---|
| electrical (R11) | (10.5, 33.0, 0) | -90 | D01 exterior face (module y -0.25) on the turbine east wall outer face x 10.25 at turbine-local y 18.5 (bay between columns at 16 and 21, past the condensate return ending at 16.8) |
| waste (AAA) | (10.47, -25.48, 0) | -90 | WS_RECEIVING exterior face (module y -0.32) on the spine east face x 10.15 |
| compliance dock (R1) | (12.15, -40.39, 0) | -90 | P1 corridor start (module y -2.0, its back wall left out) on the spine east face; south edge 0.4 m clear of the hall's north wall |
| turbine, condenser, cooling, reactor, front block | unchanged | | COMPACT_MAP.md, COMBINED_MAP.md |

## 2. Doors (`validation/doors.json`, 35 doors, `DOOR_<id>` anchors in the scene)

Default state when the map opens: each door's contract default where it has one, otherwise open when it leads somewhere and closed when it leads outside. Every door has an anchor empty (door id, owner room, kind, default state, states `open,closed,locked`, where it leads, clear size, leaf) and, in COLLIDERS, a trigger threshold and a solid blocker that is enabled while the door is closed or locked. Visual leaves for the non-default state are the room module's own objects (named in the leaf column); this pass does not animate them.

| Door | Owner | Plan (x, y, z) | Clear w x h | Kind | Default | Leads to | Leaf / what the build did |
|---|---|---|---|---|---|---|---|
| SPAWN_EXIT | front end | (8.0, -80.0, 0) | 2.58 x 2.60 | airlock | open | spawn | front-end leaves parked; spawn AIRLOCK leaves left out (DOOR_BINDINGS), plus the leaf hardware that stood in the doorway (new) |
| CAF_YARD | front end | (-7.27, -70.0, 0) | 3.00 x 2.51 | double sliding | open | yard | parked |
| CAF_MEDICAL | medical | (26.0, -70.0, 0) | 2.20 x 2.50 | sliding pressure leaves | open | cafeteria | parked (contract: open traversal) |
| HALL_WEST | front end | (-3.97, -54.0, 0) | 2.32 x 2.60 | double leaf | open | refinery colonnade | leaves left out (were closed in the source) |
| HALL_SPINE | front end | (8.0, -48.5, 0) | 3.60 x 3.20 | blast door | open | spine | parked |
| HALL_EAST | front end | (31.97, -54.0, 0) | 2.32 x 2.60 | double leaf | **closed** | outside (trunk canopy) | source leaves kept |
| YARD_SERVICE | front end | (-46.0, -60.15, 0) | 2.40 x 2.35 | single leaf | **closed** | outside | source leaf kept |
| YARD_FREIGHT_GATE | front end | (-22.2, -60.1, 0) | 3.10 x 3.10 | sliding gate | open | refinery freight door | parked |
| MINE_PORTAL | mine | (-53.4, -70.0, 0) | 7.20 x 3.90 | portal | open | yard | no leaf |
| REFINERY_FUEL | fuel corridor | (-22.2, -43.6, 0) | 2.60 x 3.00 | boundary double leaf | open | refinery | F01 boundary leaves left out (they were closed in F23ci and blocked the fuel run) |
| FUEL_F02 | fuel corridor | (-8.0, -19.6, 0) | 5.00 x 5.00 | boundary double leaf | open | concourse | F02 boundary leaves left out (closed in F23ci) |
| FUEL_S01_PLANT | fuel corridor | (-27.6, -26.2, 0) | 2.00 x 2.50 | double leaf | **closed** | outside | source leaves |
| FUEL_S02_CLEAN | fuel corridor | (-15.6, -22.6, 0) | 2.00 x 2.50 | double leaf | **closed** | outside | source leaves |
| FUEL_S03_WASTE | fuel corridor | (-5.8, -27.6, 0) | 2.40 x 3.00 | double leaf | open | transfer hall | leaves left out |
| REACTOR_S | reactor | (0, -12.2, 0) | 5.00 x 5.00 | wall cut | open | concourse | cut (older pass) + trim bar split out (new) |
| REACTOR_N | reactor | (0, 14.4, 0) | 5.00 x 5.00 | stub double door | open | turbine D01 | door pieces and their hardware left out |
| REACTOR_W | reactor | (-14.4, 0, 0) | 5.00 x 5.00 | stub double door | open | cooling P01 | door pieces and their hardware left out |
| REACTOR_SE | reactor | (11.0, -11.0, 0) | 5.00 x 5.00 | stub double door | **closed** | outside | source door kept |
| TURBINE_D01 | turbine | (0, 14.5, 0) | 2.40 x 2.70 | opposed sliding | open | reactor N stub | parked |
| TURBINE_D02 | turbine | (0, 38.5, 0) | 2.40 x 2.70 | opposed sliding | **closed** | outside | 32 leaf objects moved 1.37 m shut (local copies) |
| TURBINE_E_ELECTRICAL | turbine | (10.12, 33.0, 0) | 2.40 x 2.70 | new opening | open | electrical D01 | wall, plinth, cap and two reveals split (bisect, capped jambs) |
| ELECTRICAL_D01 | electrical | (10.5, 33.0, 0) | 2.40 x 2.70 | sliding pair | open | turbine | parked |
| ELECTRICAL_D02 | electrical | (26.9, 33.0, 0) | 2.40 x 2.70 | sliding pair | **closed** | outside | 74 leaf objects moved 1.25 m shut |
| TURBINE_W_STAIR | turbine | (-4.12, 27.95, 0) | 2.00 x 2.60 | new opening | open | condenser stair | split like the east door |
| CONDENSER_D01 | condenser | (1.6, 21.9, -6) | 2.00 x 2.40 | opposed sliding | open | stair corridor | parked; stub end wall and blanking panel left out |
| COOLING_P01 | cooling | (-14.5, 0, 0) | 5.00 x 5.00 | overhead folding shutter | open | reactor W stub | raised (contract: fixed open) |
| WASTE_RECEIVING | waste | (10.47, -25.48, 0) | 3.00 x 3.20 | rolling shutter | open | spine | rolled up |
| WASTE_PERSONNEL | waste | (12.87, -31.64, 0) | 1.20 x 2.30 | hinged, outward | **closed** | outside (gap to the dock) | leaf turned 90 degrees into the frame (11 objects) |
| WASTE_DISPATCH | waste | (28.47, -25.48, 0) | 2.40 x 2.80 | rolling shutter | **closed** | outside | new 36-slat curtain (the module has only the rolled-up barrel) |
| DOCK_P1 | dock | (11.15, -40.39, 0) | 2.40 x 2.60 | sliding (X) | open | spine | P1 deep back wall and leaf left out |
| DOCK_P2 | dock | (27.95, -40.39, 0) | 4.60 x 3.50 | blast leaves | **closed** | outside (arrival) | contract default sealed |
| SPINE_NORTH_END | front end | (8.0, -14.55, 0) | 3.30 x 3.30 | single leaf | **closed** | dead end | source leaf kept (the concourse is entered through the spine's west wall) |
| SPINE_E_WASTE / SPINE_E_DOCK / SPINE_W_TRANSFER | front end | x 10.0 / 10.0 / 6.0 | 3.1 / 2.6 / 2.4 wide | new openings | open | waste / dock / transfer hall | spine wall, dado, ribs and decals split |

Doors that need an owner decision: none blocks play. Whether the hall's east exit and the yard service door are evacuation exits (a runtime rule, not geometry), and whether the spine's north-end door should go (it closes a 3 m dead end) are open items in section 10.

## 3. Plates and dead ends

All three `PLACEHOLDER_*` plates are gone. Electrical D02 and turbine D02 are closed with their own leaves (both face the outside now); waste dispatch gets a closed roller curtain; waste personnel's leaf is closed in its frame (it faces the dock's wall 0.29 m away). The condenser bay is no longer a dead end: stair door in the turbine's west wall at (-4.25, 27.95), landing, 34 risers of 0.176 m on 0.300 m goings (30.5 degrees, 2.1 m clear, handrails both sides), corridor 2.48 x 2.7 m at z -6 for 11.9 m, D01 stub opened. The front end's ground slab (`context_ground`, z -0.9..-0.15) was holed over the shaft. Remaining dead ends: none walkable (the spine's north end is a 3 m blind stub behind a closed door, as before).

## 4. Lighting (`validation/lighting.json`, `measure_lighting.py`)

Method: 18 views at 1.6 m eye height in every junction, Cycles CPU 640 x 360, 14 spp, denoised, the scene's own view transform (Khronos PBR Neutral, exposure 0.5) and lights; measured on the image as displayed. My bar (not an art-direction rule): median luma >= 0.15, near-black (< 0.04) <= 25 %, clipped (any channel > 0.98) <= 5 %.

| View | Median | P10 | Near-black | Clipped (any / white) | Result |
|---|---|---|---|---|---|
| reactor N stub (to turbine) | 0.802 | 0.519 | 0 % | 5.7 % / 0 % | marginal hot (reactor's own lighting) |
| turbine entry | 0.449 | 0.082 | 4 % | 1.3 % / 0 % | ok |
| turbine east aisle to electrical | 0.575 | 0.223 | 1 % | 0.4 % / 0 % | ok |
| electrical inside | 0.549 | 0.178 | 1 % | 2.8 % / 0 % | ok |
| reactor W stub to cooling | 0.596 | 0.228 | 2 % | 4.5 % / 0.1 % | ok |
| cooling inside | 0.580 | 0.189 | 1 % | 3.3 % / 0.8 % | ok |
| spine to waste | 0.279 | 0.011 | 11 % | 0.7 % / 0 % | ok |
| waste inside | 0.283 | 0.115 | 5 % | 1.4 % / 0 % | ok |
| spine to dock | 0.407 | 0.200 | 1 % | 0.3 % / 0 % | ok |
| dock inside | 0.248 | 0.063 | 5 % | 1.0 % / 0 % | ok |
| concourse | 0.589 | 0.313 | 0 % | 1.3 % / 0.7 % | ok |
| spine (mid) | 0.704 | 0.298 | 0 % | 2.3 % / 0 % | ok |
| reactor from the south door | 0.583 | 0.278 | 1 % | 5.4 % / 2.3 % | marginal hot (reactor's own lighting) |
| transfer hall | 0.533 | 0.193 | 0 % | 6.1 % / 0 % | marginal hot (warm ceiling highlights) |
| stair top | 0.736 | 0.543 | 0 % | 4.9 % / 0 % | ok |
| stair bottom | 0.769 | 0.625 | 0 % | 1.8 % / 0 % | ok |
| condenser D01 | 0.792 | 0.351 | 0 % | 2.1 % / 0 % | ok |
| condenser inside | 0.463 | 0.243 | 1 % | 1.1 % / 0 % | ok |

Findings: **nothing is too dark to read**; the AAA rooms are the darkest (waste 0.28, dock 0.25 median) and the bright halls next to them (spine 0.70) give a 2.5x step at their doors. The problems were my own additions: the transfer hall's accent strips and lights (17.8 % clipped at first) and the stair corridor, whose spawn dado and slab concrete (base colour 0.11) read as a black band (15 to 20 % near-black). Fixed locally (`EMISSION_OVERRIDES`, `HALL_LIGHT_SCALE`, a dimmer lamp-panel copy for that hall, a mid-grey stair concrete, corridor lights 110 -> 70 W). Not changed: the reactor's own lighting (two views 0.4 to 0.7 points over my clipping bar; it is the reviewed refined hall) and the AAA rooms (owner-accepted look). No junction fill lights were needed (`FILL_LIGHTS` is empty). Not measured: dynamic exposure in the engine, emissive screens animated, the exterior at night. The 18 lighting renders were made on the build before two later changes (the mine-portal door anchor and the hall's stencil and sign swap); neither touches a measured view.

## 5. Collision and navigation (`assembly_colliders.py`, `walk_test.py`)

Proxies (COLLIDERS collection, hidden; `validation/colliders.json`): 126 boxes and one sloped slab for the spine, concourse, reactor south tunnel and N/W stubs, the transfer hall, the three spine junctions and the dock P1 tube, the turbine/electrical junction, the condenser stair (landing, a 30.5-degree ramp, shaft, lower corridor), plus a trigger threshold and a solid blocker on each of the 35 doors (blockers enabled while closed). Roles: floor 13, wall 30, roof 12, ramp 1, door_threshold 35, door_blocker 35. Rooms keep their own collision; the proxies stop at each room's door plane.

Capsule walk test (radius 0.40 m, height 1.80 m, step offset 0.35 m; floor ray every 0.1 m, seven spheres from 0.75 to 1.40 m; sideways lane search up to 1.5 m with continuity):

| Run | Result |
|---|---|
| visual meshes, 18 routes (`validation/walk_report.json`) | **17 pass**. Fail: yard -> refinery freight door, blocked by the refinery's parked ore cart and tipper in the doorway (its own unload scene; a cart route, not a player route; players reach the refinery by the hall colonnade, which passes). |
| visual meshes, 9 closed doors | **9 block** (turbine D02, electrical D02, waste dispatch, waste personnel, reactor SE, hall east, dock P2, fuel S01, fuel S02) |
| collision proxies only, 10 hall / stub / junction / stair routes (`validation/walk_report_colliders.json`) | **10 pass**; the same 9 closed doors block |

The first runs failed on real defects, all fixed in this pass: the spine's east wall still closed over both new doors (two holes cut in one mesh by `cut_hall` were bridged across), the fuel corridor's F01 and F02 boundary leaves closed (the whole fuel run blocked), a 0.5 m trim bar across the reactor's south doorway, leaf hardware left floating in the reactor stubs and the spawn exit, skirt dust decals across five open front-end doorways, my stair's plaster skin across its own door, and the ground slab roofing the stair shaft.

## 6. Performance (`perf_report.py`, `validation/perf_report.json`)

No frame rate was measured: there is no runtime build. Static counts of the evaluated scene (Blender 5.2.2, viewport evaluation, instances counted):

| | Triangles | Objects | Submeshes (draw calls before batching) | Lights (shadowed) | Textures |
|---|---|---|---|---|---|
| whole map | 12,500,244 | 23,758 | 26,251 | 462 (424) | 110 images, 1,014 MB as RGBA8 with mips |
| before this pass | 12,518,153 | 23,609 | 26,148 | 453 | same |

Per room (400k is the repository's per-room flag, 800k the front end's design budget): mine 3.31 M, fuel corridor 3.10 M, reactor 1.22 M, electrical 0.77 M, medical 0.60 M, front end 0.56 M, refinery 0.46 M, spawn 0.43 M, condenser 0.42 M, turbine 0.42 M, dock 0.42 M, waste 0.37 M, cooling 0.35 M; halls, stair and signs 0.06 M. Eleven rooms are over the flag. The fuel corridor's F23ci file evaluates to 3.10 M with its bevels (AGENTS.md quotes 678,692 for the corridor; that figure is not reproduced by this file, which has no decimation modifiers).

Proposals (not built):
1. **Streaming by room**, using the portal graph from the door table. Worst-case visible sets through open doors: reactor 5.10 M (it sees the fuel corridor through the concourse), fuel corridor 4.79 M, refinery 4.12 M, mine 3.87 M, front end 2.86 M, turbine 2.40 M; every other room under 1.6 M. The fuel corridor and the mine are the two to split: corridor into its two legs (F01 leg / F02 leg, the freight gate between them is a natural portal), the mine into tunnel and surface.
2. **LODs** first where one mesh is heavy: mine `R39 | Gravel tunnel` 444k, `R40 | Mine cliff` 352k, boulders 66 to 98k each, placed four times each (they share mesh data already, so one LOD set serves all copies).
3. **Batching**: unique meshes nearly equal objects in the overhauled rooms (electrical 3,037 meshes for 3,124 objects), so instancing buys little; static batching by material per room would cut 26k submeshes to roughly the material count per room (22 to 206).
4. **Lights**: 424 shadow-casting lights; most rooms carry 15 to 45, the reactor 117 and the mine 64. Bake or limit shadows per room before any frame-rate test (baking is the last step and needs accepted lighting first).

## 7. Travel times (`validation/walk_report.json` lane lengths)

Walking 4.5 m/s, loaded cart 1.5 m/s (README assumptions). Distances are the continuous lanes the capsule actually walked, not straight lines.

| Route | Lane (m) | Walk (s) | Cart (s) |
|---|---|---|---|
| spawn -> reactor floor | 90.2 | 20.0 | |
| spawn -> mine portal | 83.3 | 18.5 | |
| medical -> reactor floor | 95.0 | 21.1 | |
| reactor floor -> electrical (through the turbine) | 45.0 | 10.0 | |
| reactor floor -> condenser bay (stair) | 54.6 | 12.1 | |
| reactor floor -> cooling | 15.0 | 3.3 | |
| reactor floor -> waste | 33.7 | 7.5 | |
| reactor floor -> dock | 48.9 | 10.9 | |
| refinery fuel door -> fuel corridor F02 (the reactor-side fuel boundary, measuring point of plan v7's "41 m, 27 s") | 41.6 | 9.2 | **27.7** |
| refinery fuel door -> reactor south door (FUEL HANDLING stub) | 56.8 | 12.6 | 37.9 |
| refinery fuel door -> reactor floor by the core (fuel run end to end) | 62.9 | 14.0 | 41.9 |
| fuel corridor -> waste (S03 transfer) | 24.4 | 5.4 | 16.2 |
| mine portal -> refinery freight door, along the rail (geometry, not walked) | 39.5 | | 26.3 |
| hall -> refinery (colonnade) | 31.6 | 7.0 | |
| cafeteria -> medical | 23.0 | 5.1 | |
| spawn -> electrical (farthest station) | 160.9 | 35.8 | |
| mine portal -> electrical (composed from walked lanes) | 208 | 46 | |

Against the README targets (adjacent 10 to 20 s, mine -> refinery 20 to 35 s, refinery -> reactor 15 to 30 s, full crossing under 60 s): the refinery -> reactor fuel run **depends on where the fuel is dropped**: to the fuel corridor's reactor port F02 it is 27.7 s by loaded cart (within 30, and the same measuring point as plan v7's 27 s); to the reactor's south door 37.9 s; all the way to the core 41.9 s (misses). The corridor's own 38.2 m freight path is 25.5 s of it, so the end-to-end run can only meet 30 s with a fuel drop at or near F02 (the concourse) or a faster cart. Recommendation: define the fuel drop at the concourse end of the corridor (F02); owner decision. Adjacent stations from the reactor are all under 13 s (cooling is 3.3 s, under the 10 s floor of the target, which a compact map will do). Full crossing 46 s: within 60.

## 8. Unity

`runtime/unity` is a source-only WP-01 foundation (Unity 6000.4.3f1, never opened for this map); there is no editor or licence in this environment and no approved map import route (`runtime/README.md`, game-asset-pipeline skill). So: **engine import, prefab binding, collision in engine and Player behaviour: Blocked (no editor); not claimed.**
What exists instead (`export/`):
* `compact_map_colliders_anchors.fbx` (362 KB): the 126 collision proxies, 35 door anchors and 13 room placement anchors with their custom properties. FBX because Unity imports it natively; no GLB importer is assumed. Settings in the manifest.
* Blender re-import check (an empty process): 174 objects exported, 174 re-imported, 0 missing, 0 extra, 0 bound mismatches over 1 mm (recorded in the manifest).
* `binding_manifest.json`: the A08 fields (source revision, export settings, scale/axes/origin, logical ids, room placements, collider roles, state variants, licensing). UNRESOLVED fields: per-room prefab mapping (no approved room export route), spawn/interaction point ownership, runtime owner of map collision and doors.

Readiness checklist for whoever opens the editor: 1. decide the room export route (FBX per room module, scale 1, -Z forward / Y up) and the runtime owner of doors (D-xx in DECISIONS_AND_RISKS); 2. import `export/compact_map_colliders_anchors.fbx` and confirm 126 proxies land on the room anchors; 3. bind `door_blocker` enable state to door state, `door_threshold` as triggers; 4. run the capsule routes of `walk_test.py` with the Unity CharacterController (radius 0.4, height 1.8, step 0.35, slope 45) and compare lane lengths; 5. profile against D-07 / D-09 once those budgets exist. No package was installed and no infrastructure was chosen.

## 9. What changed, files

* `build_compact_map.py` rewritten for the assembly pass (placements, door table and anchors, `split_openings`, `hole_in_slab`, closed leaves, the condenser stair, signs, local lighting overrides); `assembly_colliders.py` (new).
* Tools (new): `plan_cut.py`, `check_overlaps.py`, `walk_test.py`, `measure_lighting.py`, `perf_report.py`, `export_unity.py`, `draw_assembly_plan.py`; `check_footprints.py` updated to the new placements.
* Evidence: `validation/` doors, colliders, walk reports, lighting, performance, overlaps, hall audit; `renders/assembly/` plan and walking-height views; `export/`.
* `combined_map.blend` rebuilt from the final script. `build_combined_map.py`, `reactor_links.py` and every room source are unchanged.
* Deliberately not done: any art pass on a room; moving the reactor or refinery; the gantry (no attachment spec); the plan's dropped features (outer ring, yard passage, medical direct door, fuel-service hall), which this layout no longer needs; baking; LODs; Unity.

## 10. Open decisions for the owner

1. **Fuel run**: 27.7 s by loaded cart to the corridor's reactor port F02 (meets 30 s), 41.9 s to the core (misses). A grey-box test of a short replacement corridor (`GREYBOX_FUEL_TEST.md`) gives 28.1 s end to end and 16 % less map area, at the cost of a new fuel corridor room. Recommended: fuel drop at F02 / the concourse. Alternatives: accept 42 s, raise the cart speed above 1.5 m/s, or shorten the fuel corridor (a room change).
2. **Refinery freight door is blocked to players** by the refinery's parked ore cart: intended (carts only) or should the cart park inside?
3. Hall east exit, yard service door: are they evacuation exits (runtime rule)? The spine's north-end door closes a 3 m blind stub: keep or remove (removing it means trimming the front end's spine).
4. Fuel corridor S01 (plant service) and S02 (clean service) stay closed: they have no neighbour in this layout.
5. AAA finishes' own open items (condenser and waste reach checks in their `reach-check.json`) are untouched.
6. Performance: streaming split of the fuel corridor and the mine, LOD and shadow policy, once D-07 / D-09 budgets exist.
7. The reactor's two hot views (5.4 and 5.7 % clipped at the scene's exposure): leave or adjust in a reactor pass.

## 11. What ran (exact)

Blender 5.2.2 LTS (downloaded to `/opt/blender52` in the container), headless. Every check below ran on the final `combined_map.blend` unless noted.
* `blender -b --factory-startup --python build_compact_map.py` (about 40 s; log lines: 35 door anchors, 126 colliders, stair 34 risers 30.5 degrees).
* `plan_cut.py` (8 heights) + `check_overlaps.py`; `check_footprints.py`.
* `walk_test.py` (visual, 18 routes, about 6 minutes) and `walk_test.py --colliders` (10 routes).
* `measure_lighting.py` (18 views, about 14 minutes); the fix iterations used the same script on the affected views.
* `perf_report.py` on the final build and on the pre-pass compact build (baseline).
* `export_unity.py` (export + re-import in an empty Blender process).
* `validate_halls.py` (the older hall audit, now covering the one built hall): `PASS (geometry audit only)`, transfer hall 11.3 m, 0 blocked ray steps, 0 of 1,000 sphere rays escaping (`validation/compact_report.json`).
* Render reviews: every image in `renders/assembly/` was looked at (`17_assembly_plan.png`; `17_walk_*` = the lighting views of the junctions; `17_*_closed`, `17_reactor_south_door`, `17_hall_to_spine_sign`, `17_stair_house_outside`, `17_aerial_east`). A view of the closed reactor SE stub could not be framed (the camera lands inside the reactor's own corner equipment); that door is evidenced by the walk test's block check only. Scratch renders were deleted.
Not run: Unity anything, a frame-rate test, an independent review, the room validators, a human playtest.
