# Compact map assembly report (2026-10-13)

**Status: unreviewed, not accepted.** One agent session built, measured and reported this; no independent review, no owner approval of the result, no Unity run.
Task: `OPUS_ASSEMBLY_PROMPT.md` (take the compact map from "laid out" to "assembled"), widened by the owner during the session: *"you may shift around the entire map as you please and build as many things as needed ... One shot the most compact map possible without reinventing the individual rooms beyond recognition"*, then *"Ignore all previous specs and planning docs - build and decide what comes where on your own with the goal of the most compact and logical map possible. Do not ask me questions"*. After the first assembly pass the owner asked about the fuel run, asked for a grey-box test of a short fuel corridor (`GREYBOX_FUEL_TEST.md`) and then said *"yes do the rebuild to the same graphical fidelity as it was previously"*. This report describes the result: the **short fuel corridor layout**. The first pass's numbers are kept where they are compared.
Rooms are linked, never edited: every change below is a local copy made by `build_compact_map.py`, except the short fuel corridor, which is a new derived file (`sources/fuel-corridor/module_short_S1.blend`) built from F23ci by a script; F23ci itself is unchanged. "Done and dusted" rooms got no art pass; they got door cuts and closed leaves, which are layout work.

Contents: layout decision, **turbine rebuild swap (1a)**, **condenser escape ladder (1b)**, door table, plates and dead ends, **meltdown flow (3a)**, **door-frame audit (3b)**, lighting, collision and walk test, performance, travel times, Unity, files, open decisions, what ran.

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
| turbine (v2 rebuild) / condenser bay | (0, -4.2, 0) / (1.6, 3.2, -6) | 0 | reactor north stub end (reactor-local y 14.5); condenser at turbine + (1.6, 7.4, -6) |
| electrical (R11) | (10.5, 8.3, 0) | -90 | D01 face on the turbine shell's outer face (x 10.25) at turbine-local y 12.5 (rebuild bay between the columns at 10 and 14); was (10.5, 14.3) with the original turbine |
| cooling | (-14.5, -18.7, 0) | 90 | reactor west stub end |
| waste (AAA) | (11.94, -14.84, 0) | -90 | WS_RECEIVING exterior face (module y -0.32) on the reactor's east outer face x 11.62; opening centre reactor-local y 3.86, between the lockers (to y 2.42) and the column plinth (from y 5.29) |
| compliance dock (R1) | (12.15, -40.39, 0) | -90 | P1 corridor start on the spine east face (unchanged) |
| front end, spawn, mine, refinery, medical | unchanged | | COMPACT_MAP.md, COMBINED_MAP.md |

## 1a. Turbine rebuild swap (latest)

Owner: "swap in the turbine rebuild". `turbine-room` now links the v2 rebuild (`sources/turbine-room/rebuild/turbine_room_v2_geo.blend`, collection `TURBINE_ROOM_V2`; merged in #63, declared done by the owner, its only review the builder's own at about 79/100) instead of the AAA finish of the original module. The rebuild has the original's envelope and door centres, so its placement is unchanged. Before cutting, its walls were inventoried loose part by loose part and its floor ray-scanned on a 0.25 m grid (east aisle x 7.05..8.05 clear from D01 to the east bays; the generator pedestal fills x 1.8..7.05 from y 2.6 to 23).

`patch_turbine` (local changes only; the room file is not edited):
* **D01**: the rebuild's 1.9 m vestibule, which ended in a closed-door panel inside the reactor stub, is clipped at y -0.3 part by part (`clip_parts`, closed parts capped). TO REACTOR over it stays.
* **D02 (emergency exit)**: the vestibule's end panel (windows, hinges, handle, seam, and the occluder's copy of it) is split out as the closed leaf (`take_parts`; the meltdown walk leaves it out by `leaf_regex`); the end wall behind it is opened 1.44 x 2.38 m (the band starts at y 25.68: the wall's inner face is 25.70, found when the first cut left it whole and the meltdown walk stuck there). The two TO ELECTRICAL signs (the lettered header board and a decal over the panel) are removed; a new EMERGENCY EXIT board, an EXIT label over the panel and the green EXIT box replace them. Outside, the vestibule is clad in the shell's concrete with a steel frame and the exit lamp; the north strip's apron is notched round it.
* **Electrical door**: 2.4 x 2.7 m at turbine-local y 12.5 (11.3..13.7) through the wall skin, panels, dado, skirting, the wall board DB-04 and the shell, in the bay between the columns at y 10 and 14. The bay at 18..22 (the original position) holds a wall cabinet and the condensate tank's end. **The electrical room moves 6.0 m south** to (10.5, 8.3); its D02 spur, lane, sign and lamp follow (`evacuation.py` now reads the placements from the build module).
* **Stair door**: 1.55 x 2.6 m at y 12.2..13.75 in the bay between the columns at 10 and 14 (its MIND YOUR HEAD poster and first-aid sign go with the cut). The stair's top landing starts at y 12.0, so the flight's goings shorten to 0.291 m (31.2 degrees).
* **Exterior**: the rebuild's walls are 0.05 m interior skins inside a black light-occluder shell of loose quads. Its 86 faces on the shell's five outer planes take the front end's `concrete_slab`; the cuts through the shell are lined with steel reveals and floor thresholds.
* Left out: the 16 cameras, the `MOON_EAST` sun lamp and the render-hidden haze box.

![D02 inside and outside](renders/assembly/21_turbine_D02_exit.png)

**Stacked slabs (found by the owner on the turbine render, fixed the same day).** The turbine's east aisle floor showed raw "ground": it was the condenser bay's roof (`Ceiling slab`, map z 0.0..0.3) standing 0.3 m proud of the turbine floor (top z 0) over the bay's whole footprint, under the turbine and the electrical room's west end. Each room was authored with its own full-thickness floor and roof; stacked (the bay sits 6 m under the turbine by its own CONNECTIONS.md), the bay's roof came up through the floor above. The plan cuts (0.4 m and up) and the walk test (0.35 m step) passed it. The same probe found the front end's ground slab (z -0.9..-0.15) running through the top of the bay: it was the bay's ceiling, 0.9 m low, with the light battens just under it. Both date from the first assembly pass, not the swap. Fixed with local copies: the roof slab squeezed to z -0.305..-0.015 under the turbine floor, a hole in the ground over the bay's roof footprint, the two gallery inspection lights (inside the turbine floor slab) dropped 0.12 m, and the turbine shell's underside faces (a black strip in the bay's ceiling) removed. Upward probes inside the bay now hit its own concrete ceiling; downward probes in the turbine hit the turbine floor first.

To catch this class of defect: the plan cut now also slices at z 0.15 and -0.6, and **`floor_audit.py`** (new, `validation/floor_audit.json`) casts a 0.5 m grid of rays down at the ground level and the condenser level and flags any upward-facing surface 0.02 to 0.5 m above the level that lies over another room's floor. Result on the final build (123,820 samples): in the reactor cluster one 0.5 m2 spot (a turbine pipe over a gap in the turbine floor, above the lowered bay roof; harmless); everything else is in the yard at the mine portal, all pre-existing surface dressing: the mine's mud apron, rails and sleepers laid 2 to 12 cm on the yard, and the front end's portal kerbs on the mine's shed planks. No room's roof or floor slab stands through another's floor any more.

## 1b. Condenser bay escape ladder

Owner: "build the condenser ladder". The first idea (a ladder up through the bay's U04 opening into the turbine) does not work: U04 is the turbine exhaust neck over the condenser shell. A survey for a straight shaft found no column clear both in the bay and on the floor above it: the bay's north-west holds the ejector skid and two pump power feeds, the turbine's east aisle over the bay holds the condensate tank skid and its pumps, and under the electrical room the two interiors overlap by 0.66 m with a roof girder through it.

So the exit leaves sideways (`add_condenser_escape`, `ESC` in `build_compact_map.py`):
* a 1.0 x 2.3 m emergency door (green steel leaf, push bar, frames both faces) cut in the bay's west wall at its north-west corner (`patch_condenser`), reached along the bay's clear north wall;
* a 4.1 m tunnel at bay level (1.0 x 2.4 m, the stair's plaster, wainscot and lamps) under the turbine's west aisle;
* a shaft on the stair house's line north of it with a 6.0 m caged ladder (rails 0.5 m apart, rungs every 0.30 m, carried 1.1 m above the landing, hoops from 2.4 m up), a grade landing with kick plates and rails round the opening;
* a small concrete hatch house over the shaft with an emergency door north onto a new paved path to the north evacuation strip (one more yard pole lights it).
To walk to the door, pump B's power riser (a 32 mm cable rising from under the floor to the ceiling 0.76 m from the north dado, under the walk test's 0.8 m capsule) is moved against the north wall as a local copy (its under-floor run jogs north below the floor); the walk then has 1.19 m between it and the ejector exhaust riser.
Doors `CONDENSER_W_ESCAPE` and `ESCAPE_HOUSE_DOOR` (both emergency exits: closed in normal play, open in the evacuation state; both block the walker when closed). Checks: the meltdown walk walks the bay to the ladder foot (16.3 m) and the hatch house to the road (50.2 m); the ladder is a `ladder` collider volume and is not walked; the collider walk walks the tunnel; door audit 45 doors, 0 flagged; the door graph now gives the bay 2 independent routes out and no single door cuts it off.

![escape](renders/assembly/22_escape_ladder.png)

## 1c. Cafeteria revamp as the front end (2026-10-14)

Owner: "yes switch it on and run everything". The front end is now Codex's cafeteria revamp (PR 105, `sources/front-end-area/front_end_area_cafeteria_revamp.blend`: same `MODULE_front-end-area` collection and module frame; hall, yard and shell equal to the original; its own R6 authoring review 91.90/100; owner acceptance and runtime integration were open in its `TASK_STATE.md`). Unreviewed in the map. `FRONT_END_SOURCE=original` builds with the original front end.

Local changes (`build_compact_map.py`; the room file is not edited):
* The revamp's new airlock (spawn exit) and medical door leaves, `airlock_L/R` and `medical_N/S` `_door_leaf_body` / `_fittings_seals_hinges`, stand closed in two doorways the map keeps open (SPAWN_EXIT, CAF_MEDICAL). They are left out, as the original's parked leaves were open (6 routes stuck on them in the first compatibility walk).
* `evacuation.py` borrowed the yard's materials (wet apron concrete, lane paint, charcoal steel, lamp emissive) from the front-end library by file name, so with the revamp it silently fell back to its substitute colours. It now accepts either file; the evacuation paving uses the revamp's `apron_wet` again.

Every texture of the revamp is packed in its file (48 images, no library links), so the build needs only that one file.

Results on the rebuilt map (all run, one Blender process at a time):

| Check | Result |
|---|---|
| Build log | the same patch counts as before (front end 2,303 objects, 119 left out; condenser, turbine and spine patches unchanged) |
| Plan cut, 10 heights, + overlaps | the same overlap pairs as before; segment counts differ by a few |
| Walk, normal | 17/18 (only the refinery cart route, as before); every lane length within 5 cm of the previous build |
| Walk, collision proxies | 10/10 |
| Walk, meltdown | 20/20; `evac_report.py` unchanged |
| Closed doors | 13/13 block |
| `door_audit.py` | 45 doors, 0 flagged |
| `floor_audit.py` | the same 40 pre-existing owner pairs (mine yard dressing, one 0.5 m² turbine spot); nothing in the cafeteria |
| `perf_report.py` | front end 753,736 triangles (560,372 with the original; under its 800k budget), 57 area lights, 42 textures; map 11,223,611 |
| Export | 202 objects, re-import PASS |
| Lighting | 29/30. The five new cafeteria views pass (medians 0.69 to 0.76, no near-black). The game corner sits on the 5 % clip bar and dining is at 4.7 %. The spine view is the same marginal-hot miss as before. |

Renders from the map: `renders/assembly/22_cafeteria_*` (15 views: Codex's own cafeteria camera spots in plan coordinates, plus an overview and a view from the medical side).

## 1d. Ore cart, cart-only freight door, mine triangle cut (2026-10-15, latest)

Owner: "fix both" (the freight door and the mine's triangle count) and "Animate minecart wheel as well". Then, on the choices put to them: the freight door is a cart-only door, the cart rolls in, tips and rolls out, and the mine goes under 800k triangles. All map-side (`build_compact_map.py`); the refinery and mine files are not edited. Unreviewed.

**Freight door.** The walk test's former "cart route" stopped at the refinery's tipper, not just its parked cart: the side tipper sits in the doorway (lock at the cart's south end, trunnion bearings on the axis). The door is now a **cart door**. People reach the refinery through the hall's west door and the colonnade (`hall_to_refinery`, passes). The walk test drops the route, and `YARD_FREIGHT_GATE` in `validation/doors.json` says so. The new **`cart_check.py`** runs the cart through its whole cycle instead.

**Ore cart** (`patch_refinery_cart`). The receiving bay's gullet cart (its four wheels, the 40 ore pieces in its hopper) and the tipper's cradle, lock and trunnion bearings are copied locally with their hierarchy. One loop: 576 frames at 24 fps (24 s), Cycles modifiers, frame 1 = the authored pose (so every static check sees the room as built):

| Frames | Motion |
|---|---|
| 1 to 24 | parked, loaded, lock up |
| 24 to 72 | tipper swings 75 degrees west into the receiving hopper (cradle and cart together about the trunnion axis) |
| 78 to 96 | load empties (scaled down onto the hopper floor) |
| 100 to 148 | tipper back upright |
| 148 to 172 | tip lock folds flat toward the door; captive wheel guides drop 0.05 m and retaining clamps 0.48 m |
| 172 to 340 | cart rolls 7.0 m out through the freight door to the yard end of the straight rail |
| 346 to 382 | reloaded in the yard (load rises) |
| 388 to 556 | rolls back onto the tipper |
| 556 to 576 | lock up, guides and clamps raised |

The wheels turn by distance over tread radius (0.235 m: axle height over the rail head), keyed on the same frames as the cart, so they roll without slipping.

As authored, the cart could not leave the tipper. Both trunnion bearings stood 0.08 m into the west wheels' path, the lock stood in front of the axle, and the guides and clamps stood above the flanges. So in the copy, the bearings and the tip axis sit 0.12 m further outboard, and the lock, guides and clamps retract, as a working tipper's would.

`cart_check.py` checks the cart (cart, wheels, load) against everything near the rail, the tipper's own moving parts included, every 4 frames. Contacts already present at frame 1 (the clamps on the north axle) are allowed. Result: **145 frames, 0 new contacts, PASS**. Its tip sweep is clear up to 80 degrees; at 85 the hopper lip meets the receiving hopper's walls, so the loop uses 75.

Renders `renders/assembly/23_cart_*`, every one looked at: tipping into the hopper, upright, lock folded, rolling out through the door, empty and reloaded in the yard, rolling back.

Not done: an ore stream or sound; the load scales away rather than pouring. No runtime playback, real-time review or Unity Animator test was run.

**Mine** (`slim_mine`, `MINE_LOD`). The mine was 3.31 M triangles, eight times the 400k room flag, mostly scanned CC0 props and terrain: a 0.44 m lantern was 34k triangles, a 1 m boulder 66k to 98k, the gravel tunnel 444k and the cliff 352k. The 67 heaviest objects (25 meshes) are decimated once at build time into local meshes, so nothing runs on load. Each shared mesh is decimated once. Targets:

| Group | Target |
|---|---|
| Lanterns | 2,500 triangles each |
| Boulders | 2,000 to 2,500 each |
| Barrels | 2,000 each |
| Oil lamps | 1,200 each |
| Gravel tunnel, cliff | 6 % |
| Tunnel floor, talus | 40 % |
| Mid-weight timber, ironwork and rock meshes | 30 to 60 % |

Result: those objects went from 2,973,014 to 444,507 triangles, and the **mine from 3,313,648 to 785,141** (`perf_report.py`). `MINE_LOD=0` builds it at full detail. Lanterns were first cut to 1,500; a close-up render showed faceted caps, so they stay at 2,500.

Before/after renders: `renders/assembly/23_mine_before_after.png` (tunnel mouth, lantern close-up, deep tunnel, tunnel end, shed, cliff) and `23_mine_lantern_before_after.png`. They are indistinguishable at walking distance, with slight faceting on the lantern base at 1.3 m.

Results on the rebuilt map:

| Check | Result |
|---|---|
| Walk, normal | **17/17** (the freight door is no longer a walking route) |
| Walk, collision proxies | 10/10 |
| Walk, meltdown | 20/20 |
| Closed doors | 13/13 block |
| `door_audit.py` | 45 doors, 0 flagged |
| `floor_audit.py` | 39 owner pairs, all the existing mine-yard dressing ones (one fewer; one renamed `... lod`) |
| Export | 202 objects, re-import PASS |
| Lighting | 29/30 (spine_mid as before) |
| Whole map | **8,695,104** triangles (was 11,223,611) |

The plan cut adds two lines, `ROOM_mine <- EXTERIOR_evacuation` at 1.1 m and 1.8 m. These are the same 16 segments of the west evacuation path already flagged at 0.15 m and 0.4 m. With fewer mine triangles, the mine's measured outline (its percentile box) shifted, so the same segments now count as inside at two more heights. No geometry moved.

## 2. Doors (`validation/doors.json`, 37 doors since the escape ladder, `DOOR_<id>` anchors in the scene)

Default state when the map opens: each door's contract default where it has one, otherwise open when it leads somewhere and closed when it leads outside. Twelve doors are **emergency exits** (`emergency_exit`: closed in normal play, `evac_state` open; `leaf_regex` names their closed-leaf objects): HALL_EAST, YARD_SERVICE, YARD_EVAC_GATE, REACTOR_SE, TURBINE_D02, ELECTRICAL_D02, CONDENSER_W_ESCAPE, ESCAPE_HOUSE_DOOR, COOLING_W_EXIT, WASTE_PERSONNEL, WASTE_DISPATCH, SPINE_NORTH_END (section 3a; the two condenser escape doors in section 1b). Every door has an anchor empty (door id, owner room, kind, default state, states `open,closed,locked`, where it leads, clear size, leaf) and, in COLLIDERS, a trigger threshold and a solid blocker that is enabled while the door is closed or locked. Visual leaves for the non-default state are the room module's own objects (named in the doors file); this pass does not animate them.

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
| TURBINE_D01 | turbine | (0.00, -4.20, 0) | 2.40 x 2.70 | opening (rebuild vestibule, clipped) | open | reactor N stub |
| TURBINE_D02 | turbine | (0.00, 21.53, 0) | 1.44 x 2.38 | vestibule end panel | **closed** | outside (the rebuild's end panel kept shut; the wall behind it opened) |
| TURBINE_E_ELECTRICAL | turbine | (10.10, 8.30, 0) | 2.40 x 2.70 | new opening | open | electrical D01 |
| ELECTRICAL_D01 | electrical | (10.50, 8.30, 0) | 2.40 x 2.70 | sliding pair | open | turbine |
| ELECTRICAL_D02 | electrical | (26.90, 8.30, 0) | 2.40 x 2.70 | sliding pair | **closed** | outside (74 leaf objects moved shut) |
| TURBINE_W_STAIR | turbine | (-4.10, 8.78, 0) | 1.55 x 2.60 | new opening | open | condenser stair |
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
| **REACTOR_BLAST** | reactor (concourse side) | (0.00, -33.77, 0) | 5.00 x 4.96 | blast door, sliding pair (new) | open | concourse (seal chamber) |
| **COOLING_W_EXIT** | cooling | (-27.80, -17.00, 0) | 1.60 x 2.35 | single leaf (new) | **closed**, emergency | west evacuation path |
| **YARD_EVAC_GATE** | front end | (-28.00, -84.00, 0) | 5.80 x 2.30 | double gate | **closed**, emergency | outside: the evacuation point |
| **CONDENSER_W_ESCAPE** | condenser | (-0.34, 12.10, -6) | 1.00 x 2.28 | single steel leaf (new) | **closed**, emergency | escape tunnel and ladder shaft |
| **ESCAPE_HOUSE_DOOR** | connector (hatch house) | (-5.60, 13.10, 0) | 1.56 x 2.18 | single steel leaf (new, top of the ladder) | **closed**, emergency | north evacuation strip |

The emergency exits listed above lead to the evacuation routes now (REACTOR_SE and WASTE_PERSONNEL to the east yard, TURBINE_D02, ELECTRICAL_D02, WASTE_DISPATCH and HALL_EAST to the east road, SPINE_NORTH_END to the east alley, COOLING_W_EXIT and YARD_SERVICE to the west path, CONDENSER_W_ESCAPE and ESCAPE_HOUSE_DOOR up the escape ladder to the north strip); the "outside" in the table above is their old wording.
Removed against the first pass: FUEL_F02, FUEL_S01_PLANT, FUEL_S02_CLEAN, FUEL_S03_WASTE (the corridor's north half), SPINE_E_WASTE and SPINE_W_TRANSFER. Doors that need an owner decision: none blocks play; see section 10.

## 3. Plates and dead ends

All three `PLACEHOLDER_*` plates are gone (first pass). Every door that used to open onto nothing is now either a door between two places or an **emergency exit onto an evacuation route** (section 3a): turbine D02, electrical D02, waste personnel and dispatch, the reactor's SE stub, the spine's end door (now a real 3.3 m opening; its panel was solid), the hall's east door and the yard's service door. Closed in normal play, each with its own leaves (local copies moved shut where the source showed them open) or, for waste dispatch, a new roller curtain. The dock's P2 stays sealed (its contract's default). The short corridor's cut north wall carries two shallow alcoves (the bypass and delivery mouths), backed by copies of the corridor's own lined wall bay; they are dressing, not routes. The condenser bay is reached by the stair (34 risers of 0.176 m on 0.300 m goings, 30.5 degrees, 2.1 m clear, handrails both sides; corridor 2.48 x 2.7 m at z -6 for 11.9 m). Walkable dead ends: none; doorways onto walls: none (section 3b).

## 3a. Meltdown flow (`evacuation.py`, `evac_report.py`, `validation/evac_report.json`, `validation/walk_report_meltdown.json`)

![evacuation plan](renders/assembly/20_evac_plan.png)

*The 18 escape legs the capsule walked in the evacuation state (green); red bars are doors closed in normal play, most of them emergency exits that open for evacuation.*

![east evacuation road at night](renders/assembly/20_evac_road_south.png)

Why: `design/GAME_SPEC.md` section 18 makes the critical meltdown a multi-stage event whose stage 5 brings *door failures and route collapse* and the objectives *seal chamber, restore blast door, recover workers, escape*. On the layout as it stood, every station north of the front end (turbine, electrical, condenser, cooling, waste) could leave only **through the reactor hall itself**, and the hall had **one** way out (its south tunnel); the doors that faced nothing were closed dead ends. What was added (all new geometry or the front end's own yard assets; no room source edited):

| Part | What |
|---|---|
| **East evacuation road** | A paved (`apron_wet`, the yard's own wet concrete), edge-lined, arrow-marked route along the east side: north strip past the turbine's north end (with a notch for its D02 porch floor), a 4 m road from y 25 to y -50.5, an apron to the hall's east canopy, spurs to electrical D02 and waste dispatch, and the **east yard** between the reactor's SE stub, waste and the dock with a 1.4 m alley to the spine's end door. 10 of the yard's own LED poles (its mesh) with copies of its 2600 W pole spotlight. |
| **West evacuation path** | A new 1.6 x 2.35 m emergency door in the cooling plant's rear wall (wall split like the other doors, a green steel leaf mid-wall, frames on both faces, push bar, threshold), a paved path south past the refinery's west face to the yard's north service door, 4 more poles. |
| **Reactor blast door** | Two 2.75 x 4.96 x 0.3 m leaves (the reactor's own wall steel panel and structural steel, hazard edges and kick bands) parked open behind the concourse's north wall faces, a header track and a floor guide; closed they overlap the 5 m tunnel mouth. The chamber can be sealed (`REACTOR_BLAST`); the front end's spine blast door (`HALL_SPINE`) already seals the front block. |
| **Signs and lamps** | A lit green EXIT sign over each emergency exit inside (7), a bulkhead lamp over each exit outside (8), "EVACUATION ROUTE" floor text and 24 painted arrows pointing to safety, "HALL > YARD GATE" on a fascia under the hall canopy and "YARD > EVACUATION GATE" over the yard service door. |
| **Real doorways and labels** | The spine's end door was a leaf on a **solid** frame panel (no opening behind it, found by the meltdown walk): the panel now has the 3.3 x 3.3 m opening. A dust decal across the hall's east doorway (it was always closed before) is clipped. Two door labels from the old plan were wrong in this layout (turbine D02 "ELECTRICAL / D02", electrical D02 "WASTE / D02"); both read "EXIT / D02" now (local copies of their text objects, same font, size and material). |

Escape times (walked lanes, 4.5 m/s walking; a running speed is not defined in the repository). Primary: from the station's reactor-side door through the reactor, the tunnel, the concourse and the spine to the hall (behind the spine blast door). Backup: through the emergency exits and the exterior routes; legs that join the east road part-way are composed with the road leg.

| Station | Primary (m / s) | Backup (m / s) | Backup route |
|---|---|---|---|
| reactor (core) | 33.0 / 7.3 | 37.1 / 8.2 | SE stub exit, alley, spine end door, spine (or the east yard to the road: 38.5 m to the road) |
| turbine (D01) | 70.5 / 15.7 | 152.8 / 34.0 | D02, north strip, east road, hall east door (161.9 m with the original turbine) |
| electrical (D01) | 97.5 / 21.7 | 95.2 / 21.2 | D02, east road, hall east door (101.3 / 101.2 m with the original turbine) |
| condenser bay | 174.8 / 38.8 (stair, turbine D02, north strip, road, hall) | **154.6 / 34.4 + a 6.0 m ladder** | second exit (section 1b): west escape door, tunnel, caged ladder, hatch house, north strip, road. No climbing speed is set in the repository, so the ladder is not timed |
| waste (receiving) | 57.8 / 12.9 | 69.1 / 15.4 | dispatch shutter, east road (personnel door: 30.0 m to the road) |
| cooling (P01) | 91.8 / 20.4 | **69.9 / 15.5** | rear emergency door, west path, yard service door. The primary is long because the pool railing and the west stations close the reactor's west half between the W stub and the south door (walk-tested): the new exit is the faster way out. |
| dock (P1) | 15.6 / 3.5 | none | P1 is its only door; P2 is its sealed arrival (contract default) |
| fuel corridor (F02E) | via the concourse | 65.0 / 14.4 | F01, refinery, colonnade, hall west door |
| hall to the yard evacuation gate | 69.2 / 15.4 | | cafeteria, yard; from the west path's service door 37.8 m |

Redundancy on the door graph (evacuation state; `evac_report.py`): edge-disjoint routes from each station to the front block (hall, cafeteria, yard), and every single door whose failure cuts a station off.

| Station | Routes, normal play | Routes, evacuation | Single doors that cut it off | Route that avoids the reactor hall | Out with the chamber sealed | ... and the spine blast door closed |
|---|---|---|---|---|---|---|
| reactor | 1 | **4** | none | (it is the reactor) | yes | yes |
| turbine | 1 | **3** | none | yes | yes | yes |
| electrical | 1 | **2** | none | yes | yes | yes |
| condenser | 1 | **2** | none (was: its stair) | yes | yes | yes |
| cooling | 1 | **2** | none | yes | yes | yes |
| waste | 1 | **3** | none | yes | yes | yes |
| dock | 1 | 1 | its door (SPINE_E_DOCK / DOCK_P1) | yes | yes | yes |
| fuel corridor, concourse, spine | 2 | 2 to 3 | none | yes | yes | yes |

Meltdown walk test (`walk_test.py --meltdown`: the emergency exits' closed leaves left out, the same capsule): **18 of 18 legs pass** (primary routes, every backup leg, the hall and the service door to the yard gate). The first run found the solid spine-end panel and the hall doorway decal (both fixed) and that the reactor's west half is closed to the south door (recorded above).

## 3b. Door-frame audit (`door_audit.py`, `validation/door_audit.json`)

Every map door (35) and every portal in the placed rooms' own contracts (8 more after removing duplicates; the fuel corridor's contract is F23ci's and is skipped, S1's ports are map doors) was ray-tested on both sides at two heights and three points across its middle 1.8 m: an open door or internal portal needs 1.2 m of clear space on both sides; a closed or emergency exit needs 1.5 m outside. **43 doors, 0 flagged** (re-run after the turbine rebuild swap: its new D02 exit faces 8.35 m of open strip, the electrical door 2.71 m of aisle, the stair door 2.51 m of landing): no doorway opens onto a wall and no exit faces one. Two wide frames narrow onto a smaller passage (reported, not failed): the reactor's 5 m north stub ends on the turbine's 2.4 m D01 (the clipped vestibule frame), and the mine's 7.2 m portal mouth onto the timber-lined tunnel. Before this pass the audit would have passed the spine's end door too (its leaf faced 1.57 m of alley) although nothing was behind it; that one was found by the meltdown walk, which is why both tests are kept.

## 4. Lighting (`validation/lighting.json`, `measure_lighting.py`)

Method: 30 views (25 before the cafeteria revamp, 23 before the escape ladder) at 1.6 m eye height in every junction and on the evacuation routes, Cycles CPU 640 x 360, 14 spp, denoised, the scene's own view transform (Khronos PBR Neutral, exposure 0.5) and lights; measured on the image as displayed. My bar (not an art-direction rule): median luma >= 0.15, near-black (< 0.04) <= 25 %, clipped (any channel > 0.98) <= 5 %. Views that moved with the reactor keep their reactor-local positions; new: `reactor_to_waste`, `fuel_F02E_to_concourse`, `fuel_corridor_east`, `evac_east_road`, `evac_east_yard`, `evac_west_path`, `concourse_blast_door`; gone: `spine_to_waste`, `transfer_hall`.

| View | Median | P10 | Near-black | Clipped (any / white) | Result |
|---|---|---|---|---|---|
| reactor N stub (to turbine) | 0.719 | 0.400 | 0 % | 3.6 % / 0.0 % | ok (7.2 % before the stub-end face was darkened, section 1a) |
| turbine entry (v2 rebuild) | 0.202 | 0.046 | 10 % | 0.3 % / 0.0 % | ok (the rebuild is darker by design: was 0.364 with the original) |
| turbine east aisle to electrical | 0.291 | 0.032 | 10 % | 0.5 % / 0.0 % | ok |
| electrical inside | 0.547 | 0.184 | 1 % | 2.7 % / 0.0 % | ok |
| reactor W stub to cooling | 0.543 | 0.198 | 3 % | 3.8 % / 0.1 % | ok |
| cooling inside | 0.580 | 0.177 | 1 % | 3.1 % / 0.8 % | ok |
| reactor to waste (east opening) | 0.316 | 0.143 | 4 % | 0.2 % / 0.0 % | ok |
| waste inside | 0.286 | 0.133 | 5 % | 1.0 % / 0.0 % | ok |
| spine to dock | 0.389 | 0.190 | 1 % | 0.2 % / 0.0 % | ok |
| dock inside | 0.246 | 0.057 | 5 % | 1.1 % / 0.0 % | ok |
| concourse | 0.604 | 0.307 | 1 % | 1.8 % / 0.6 % | ok |
| spine (mid, towards the end door) | 0.470 | 0.257 | 0 % | 5.8 % / 0.0 % | marginal hot (the spine end door's glowing panel, the front end's own) |
| reactor from the south door | 0.503 | 0.265 | 0 % | 3.6 % / 2.2 % | ok |
| fuel corridor F02E to the concourse | 0.380 | 0.046 | 8 % | 0.9 % / 0.0 % | ok |
| fuel corridor, east turn | 0.291 | 0.089 | 3 % | 0.1 % / 0.0 % | ok |
| stair top | 0.719 | 0.493 | 0 % | 2.9 % / 0.0 % | ok |
| stair bottom | 0.769 | 0.626 | 0 % | 1.8 % / 0.0 % | ok |
| condenser D01 | 0.792 | 0.348 | 0 % | 2.1 % / 0.0 % | ok |
| condenser inside | 0.464 | 0.228 | 1 % | 1.2 % / 0.0 % | ok |
| **east evacuation road (night)** | 0.506 | 0.451 | 0 % | 0.1 % / 0.0 % | ok |
| **east yard behind the reactor (night)** | 0.568 | 0.428 | 0 % | 1.1 % / 0.0 % | ok |
| **west evacuation path (night)** | 0.506 | 0.366 | 0 % | 0.0 % / 0.0 % | ok |
| **concourse, blast door parked** | 0.547 | 0.233 | 4 % | 2.2 % / 0.9 % | ok |
| **condenser escape tunnel** | 0.526 | 0.306 | 4 % | 0.0 % / 0.0 % | ok |
| **escape hatch house (night)** | 0.677 | 0.316 | 0 % | 0.3 % / 0.0 % | ok |
| **cafeteria entry (revamp)** | 0.685 | 0.428 | 0 % | 2.0 % / 0.1 % | ok |
| **cafeteria dining** | 0.717 | 0.451 | 0 % | 4.7 % / 0.2 % | ok (near the clip bar: the white table tops under the pendants) |
| **cafeteria lounge** | 0.723 | 0.465 | 0 % | 2.6 % / 0.1 % | ok |
| **cafeteria game corner** | 0.759 | 0.496 | 0 % | 5.0 % / 0.0 % | ok, on the clip bar (any channel; no white clipping) |
| **cafeteria to the medical door** | 0.730 | 0.447 | 0 % | 2.8 % / 0.0 % | ok |

Findings: **22 of 23 views pass; nothing is too dark to read**, the evacuation routes at night included (medians 0.51 to 0.57, no near-black: the yard's own pole spotlights). The new junctions read well: the concourse 0.62 median, the corridor's east turn 0.29 and its F02E view 0.39 (F23ci's own lighting), the reactor's east opening into waste 0.32. The one miss is the spine looking at its end door, 5.8 % of pixels with one channel clipped (0 % white): the front end's own end-door panel glows (the source spine renders the same, checked on `front_end_area.blend`), and the shorter spine brings it closer. Both reactor views that were marginally hot in the first pass now pass (2.5 % and 3.6 %), most likely because the reactor's merged meshes are no longer stripped by the old splitter and the cut pieces have their materials (not isolated by a separate test). No light inside a room was added or changed (`FILL_LIGHTS`, `EMISSION_OVERRIDES` and `HALL_LIGHT_SCALE` are empty); the evacuation routes carry their own 14 pole spotlights and 8 bulkheads (section 3a). Not measured: dynamic exposure in the engine, animated screens, the exterior at night.

## 5. Collision and navigation (`assembly_colliders.py`, `walk_test.py`)

Proxies (COLLIDERS collection, hidden; `validation/colliders.json`): 152, for the spine (14.8 m, dock door east, concourse west), the concourse (its west wall with the F02E gap), the reactor south tunnel and N/W stubs, the reactor-waste, spine-dock and turbine-electrical junctions (floor plates, heads, jambs, the dock P1 tube), the condenser stair (landing, a 30.5-degree ramp, shaft, lower corridor), the condenser escape (tunnel, shaft, landing and a `ladder` trigger volume), the evacuation aprons, road and paths (11 floor prisms) and the cooling exit threshold, plus a trigger threshold and a solid blocker on each of the 37 doors (blockers enabled while closed; emergency exits carry `emergency_exit`). Roles: floor 28, wall 36, roof 12, ramp 1, ladder 1, door_threshold 37, door_blocker 37. Rooms keep their own collision; the proxies stop at each room's door plane.

Capsule walk test (radius 0.40 m, height 1.80 m, step offset 0.35 m; floor ray every 0.1 m, seven spheres from 0.75 to 1.40 m; sideways lane search up to 1.5 m with continuity):

| Run | Result |
|---|---|
| visual meshes, 17 routes (`validation/walk_report.json`) | **17 pass** (since 2026-10-15; before, the yard -> refinery freight door route failed at the tipper in the doorway. That door is now a cart door, checked by `cart_check.py`, section 1d) |
| visual meshes, 11 closed doors | **11 block** (turbine D02, electrical D02, waste dispatch, waste personnel, reactor SE, hall east, dock P2, spine north end, cooling exit, yard service door, yard evacuation gate) |
| collision proxies only, 9 hall / stub / junction / stair routes (`validation/walk_report_colliders.json`) | **9 pass**; the same 11 closed doors block |
| evacuation state, 18 escape legs (`validation/walk_report_meltdown.json`) | **18 pass** (section 3a) |

New routes: the fuel run through the short corridor (on the freight gate's centre, and on the shortest clear line), reactor -> waste through the east opening, spawn -> waste.

## 6. Performance (`perf_report.py`, `validation/perf_report.json`)

No frame rate was measured: there is no runtime build. Static counts of the evaluated scene (Blender 5.2.2, viewport evaluation, instances counted):

| | Triangles | Objects | Submeshes (draw calls before batching) | Lights (shadowed) | Textures |
|---|---|---|---|---|---|
| **whole map now** (mine cut, animated cart, cafeteria revamp, turbine v2 rebuild, condenser escape) | **8,695,104** | 22,313 | 24,521 | 526 (486) | 147 images, 1,394 MB as RGBA8 with mips |
| before the mine cut (2026-10-14) | 11,223,611 | 22,313 | 24,521 | 526 (486) | 147 images, 1,394 MB |
| with the original front end (before the revamp) | 11,030,247 | 22,114 | 24,204 | 499 (461) | 133 images, 1,350 MB |
| with the AAA finish of the original turbine (before the swap) | 11,026,519 | 23,562 | 25,641 | 456 (418) | 110 images, 1,014 MB |
| of which the evacuation routes (paving, poles, signs, blast door) | 7,825 | | | 22 (22) | |
| first assembly pass | 12,500,244 | 23,758 | 26,251 | 462 (424) | same |

Per room (400k is the repository's per-room flag, 800k the front end's design budget): mine 0.79 M (3.31 M before the cut, section 1d), **fuel corridor 1.64 M** (F23ci was 3.10 M), reactor 1.22 M, electrical 0.77 M, medical 0.60 M, front end 0.75 M (0.56 M with the original; under its 800k budget), refinery 0.46 M, spawn 0.43 M, condenser 0.42 M, turbine 0.42 M, dock 0.42 M, waste 0.37 M, cooling 0.35 M; concourse, stair and signs 0.04 M. Ten rooms are over the flag.

Proposals (not built):
1. **Streaming by room**, using the portal graph from the door table. Worst-case visible sets through open doors: front end 5.80 M (it sees the mine, refinery, medical and spawn), mine 3.87 M, the concourse 3.43 M (corridor, front end and reactor), refinery 2.66 M, turbine 2.40 M, reactor 2.38 M (it no longer sees the whole corridor: was 5.10 M), fuel corridor 2.11 M (was 4.79 M); every other room under 1.6 M. The mine (tunnel / surface) is the one left to split.
2. **LODs** first where one mesh is heavy: mine `R39 | Gravel tunnel` 444k, `R40 | Mine cliff` 352k, boulders 66 to 98k each (they share mesh data, so one LOD set serves all copies).
3. **Batching**: unique meshes nearly equal objects in the overhauled rooms, so instancing buys little; static batching by material per room would cut 25k submeshes to roughly the material count per room.
4. **Lights**: 456 shadow-casting lights (the turbine rebuild brings 60 of them) (22 of them on the evacuation routes); the reactor carries 117 and the mine 64. Bake or limit shadows per room before any frame-rate test (baking is the last step and needs accepted lighting first).

## 7. Travel times (`validation/walk_report.json` lane lengths)

Walking 4.5 m/s, loaded cart 1.5 m/s (README assumptions). Distances are the continuous lanes the capsule actually walked, not straight lines. The fuel-run routes start 2.9 m inside the refinery, as in the first pass.

| Route | Lane now (m) | Walk (s) | Cart (s) | First pass (m) |
|---|---|---|---|---|
| spawn -> reactor floor | 71.6 | 15.9 | | 90.2 |
| spawn -> mine portal | 83.3 | 18.5 | | 83.3 |
| medical -> reactor floor | 76.5 | 17.0 | | 95.0 |
| reactor floor -> electrical (through the turbine) | 42.0 | 9.3 | | 45.0 |
| reactor floor -> condenser bay (stair) | 54.1 | 12.0 | | 54.6 |
| reactor floor -> cooling | 15.0 | 3.3 | | 15.0 |
| reactor floor -> waste receiving door | 22.6 | 5.0 | | about 30 (33.7 to 3.9 m inside waste) |
| reactor floor -> dock (3.4 m past P1) | 30.4 | 6.8 | | 48.9 |
| refinery fuel door -> corridor F02E (reactor-side port) | 29.2 | 6.5 | **19.5** | 41.6 to F02 (27.7 s) |
| refinery fuel door -> reactor south door | 39.4 | 8.8 | 26.3 | 56.8 (37.9 s) |
| **refinery fuel door -> reactor floor by the core (fuel run end to end)**, cart on the freight gate's centre | **46.0** | 10.2 | **30.7** | 62.9 (41.9 s) |
| the same on the shortest clear line (inside the gate's south post, diagonal across the concourse) | 41.4 | 9.2 | 27.6 | |
| hall -> refinery (colonnade) | 31.6 | 7.0 | | 31.6 |
| cafeteria -> medical | 23.0 | 5.1 | | 23.0 |
| spawn -> electrical (farthest station) | 138.7 | 30.8 | | 160.9 |
| spawn -> waste (receiving door) | 93.9 | 20.9 | | |
| mine portal -> electrical (composed from walked lanes, as before) | about 189 | 42 | | 208 |

Against the README targets (adjacent 10 to 20 s, mine -> refinery 20 to 35 s, refinery -> reactor 15 to 30 s, full crossing under 60 s): the end-to-end fuel run is **30.7 s on the freight lane and 27.6 s on the shortest line** (the grey-box test predicted 28.1 s); to the reactor's south door it is 26.3 s and to F02E 19.5 s, all within 30 s except the freight-lane end-to-end figure, which is 0.7 s over. Adjacent stations from the reactor are all under 13 s; the full crossing is about 42 s.

## 8. Unity

`runtime/unity` is a source-only WP-01 foundation (Unity 6000.4.3f1, never opened for this map); there is no editor or licence in this environment and no approved map import route (`runtime/README.md`, game-asset-pipeline skill). So: **engine import, prefab binding, collision in engine and Player behaviour: Blocked (no editor); not claimed.**
What exists instead (`export/`):
* `compact_map_colliders_anchors.fbx` (437 KB): the 152 collision proxies, 37 door anchors and 13 room placement anchors with their custom properties. FBX because Unity imports it natively; no GLB importer is assumed. Settings in the manifest.
* Blender re-import check (an empty process): 202 objects exported, 202 re-imported, 0 missing, 0 extra, 0 bound mismatches over 1 mm (recorded in the manifest).
* `binding_manifest.json`: the A08 fields (source revision with a worktree-dirty flag and a SHA-256 over the scene and its build scripts, export settings, scale/axes/origin, logical ids, room placements, collider roles, state variants, licensing). UNRESOLVED fields: per-room prefab mapping (no approved room export route), spawn/interaction point ownership, runtime owner of map collision and doors.

Readiness checklist for whoever opens the editor: 1. decide the room export route (FBX per room module, scale 1, -Z forward / Y up) and the runtime owner of doors (D-xx in DECISIONS_AND_RISKS); 2. import `export/compact_map_colliders_anchors.fbx` and confirm 152 proxies land on the room anchors; 3. bind `door_blocker` enable state to door state, `door_threshold` as triggers; 4. run the capsule routes of `walk_test.py` with the Unity CharacterController (radius 0.4, height 1.8, step 0.35, slope 45) and compare lane lengths; 5. profile against D-07 / D-09 once those budgets exist. No package was installed and no infrastructure was chosen.

## 9. What changed, files

* `sections/fuel-corridor/blender/build_short_corridor.py` (new) and its output `sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend` (LFS) with `module_short_S1.blend.json` (counts, ports, source hash). F23ci is not modified.
* `build_compact_map.py`: `RY` and every placement derived from it, the short corridor, `fold_spine`, `add_concourse` (replaces `build_combined_map.add_reactor_concourse` for this map), the reactor east opening and threshold, the new door rows, signs (`WASTE` over the reactor's east opening; the spine's waste and transfer signs gone), `scene['reactor_y']`; the S03 transfer hall and its lighting overrides removed.
* **`split_openings` fixed** (two defects of the first pass): every cut piece now keeps its source mesh's materials (the first pass's 230 cut pieces, and the 4 ground pieces of `hole_in_slab`, had none and rendered in Blender's default grey; the spine read white instead of the front end's pink plaster), and only the loose parts that reach into an opening are cut, inside the wall band (the first pass clipped whole meshes, so room-wide merged meshes lost a strip across the room: the reactor's south door split removed everything of those meshes within x -2.5..2.5 below z 5 across the whole hall). The pieces also keep the source object's transform (the first pass baked it into the mesh, which shifted Object-coordinate textures on the 13 cut objects whose origin is not at the module origin, all in the turbine). New helpers `clip_mesh` and a vertex-based `bbox` for local meshes.
* Meltdown flow (section 3a): `evacuation.py` (new: evacuation road, paths, east yard, poles, signs, bulkheads, the cooling exit door, the reactor blast door), `patch_cooling` (the rear-wall cut), emergency-exit fields in the door table, the spine end door's opening, `evac_report.py` (new), `walk_test.py --meltdown`; `door_audit.py` (new, section 3b).
* `assembly_colliders.py`, `walk_test.py`, `measure_lighting.py`, `check_footprints.py`, `draw_assembly_plan.py`, `perf_report.py` updated to the new layout (the scripts that run on a built scene read `scene['reactor_y']`). `greybox_fuel_test.py` is superseded (it refuses to run; use commit c25d102).
* Evidence: `validation/` doors, colliders, walk reports, lighting, performance, overlaps, `compact_report.json` (the hall audit, now with no halls to audit); `renders/assembly/19_*` and `20_evac_*` (the first pass's `17_*` renders showed the old layout and were removed; they remain in the history); `export/`.
* **Turbine rebuild swap** (section 1a): `build_compact_map.py` links `turbine-room/rebuild/turbine_room_v2_geo.blend`; `patch_turbine` rewritten for it, with the new loose-part helpers `take_parts` and `clip_parts`; `ELEC_DOOR_Y` 12.5, `STAIR_DOOR_Y` 12.975 with `ELEC_HW` / `STAIR_HW`; the stair's top landing follows the door. `evacuation.py` reads the turbine and electrical placements from the build module (north strip notch, electrical spur, lanes, signs, lamps). `walk_test.py` (turbine and electrical lanes, the D02 escape by the west aisle), `assembly_colliders.py`, `measure_lighting.py`, `check_footprints.py`, `draw_assembly_plan.py`, `evac_report.py` follow. New renders `21_turbine_*`.
* `combined_map.blend` rebuilt from the final script. `build_combined_map.py`, `reactor_links.py` and every room source are unchanged.
* Deliberately not done: any art pass on a room (the short corridor's closures are plain closures from its own parts, not an art pass); a review of S1; the gantry (no attachment spec); baking; LODs; Unity.

## 10. Open decisions for the owner

1. **Meltdown runtime rules**: which doors fail, lock or open in each meltdown stage, whether players run, and whether the yard evacuation gate is the escape point (front end DESIGN.md asks the same). The map now gives every station except the condenser bay and the dock a second way out, and both blast doors exist; the rules that use them are runtime design.
2. **Condenser bay**: its place under the turbine is settled (owner, 2026-10-13, "Ok keep it under the turbine") and it now has a second way out (the escape ladder, section 1b; owner: "build the condenser ladder"). Open: a climbing speed for the meltdown timings, and a review of the reroute of pump B's power riser (a small change to the bay's own dressing). **Dock has one door**: P2 is its sealed arrival by contract; making P2 an evacuation exit is a compliance-design call.
3. **Short fuel corridor S1 needs a review** before it can be called anything but unreviewed: F23ci's 99 does not carry over. Its two north alcoves and the moved east-wall dressing are the parts to look at.
4. **Fuel run**: 30.7 s end to end on the freight lane (27.6 s on the shortest line, 26.3 s to the reactor's south door). Accept, or define the drop at the concourse.
5. ~~Refinery freight door blocked to players~~: decided 2026-10-15, a cart-only door (section 1d). Open: whether the cart loop should play all the time at runtime or on a trigger.
6. The reactor's west half is closed to the south door by the pool railing and the west stations (cooling's way through the reactor goes round the north of the pool): intended, or should the reactor's own layout open a lane there (a reactor-room change)?
7. AAA finishes' own open items (condenser and waste reach checks in their `reach-check.json`) are untouched.
8. Performance: the mine is now 0.79 M (section 1d). Still open: LOD and shadow policy and streaming, once D-07 / D-09 budgets exist; the fuel corridor (1.64 M) and reactor (1.22 M) are the next heaviest.
9. The spine end door's glowing panel (5.8 % clipped in the spine view): leave, or dim it locally.
10. **Turbine rebuild**: its own interior lighting is darker than the other rooms (turbine entry median 0.20, near-black 10 %; by the rebuild's design, not changed here). It has only its builder's review (about 79/100). The electrical room moved 6 m south to meet the rebuild's clear wall bay; the bay at the old position (y 18..22) could take the door only if its wall cabinet moved, a change to the done-and-dusted room.

## 11. What ran (exact)

Blender 5.2.2 LTS (downloaded to `/opt/blender52` in the container), headless. Every check below ran on the final `combined_map.blend` unless noted.
* `build_short_corridor.py` (once, output committed); the S1 triangle count was then recounted on the saved file (1,650,355; the script's own log said 1,132,567 from a stale depsgraph, fixed in the script and noted in the `.json`).
* `blender -b --factory-startup --python build_compact_map.py` (about 3 minutes; log: spine 6 moved, 20 left out, 7 clipped; reactor east opening 66 objects split; 32 door anchors; 117 colliders; stair 34 risers 30.5 degrees).
* `plan_cut.py` (10 heights since the stacked-slab fix: 0.15, 0.4, 1.1, 1.8, 2.8, 4.5, -0.6, -3.5, -5.0, -5.6) + `check_overlaps.py`; `floor_audit.py`; `check_footprints.py`; box and hull areas from the 1.1 m cut.
* `walk_test.py` (visual, 18 routes, 6 minutes), `walk_test.py --colliders` (9 routes) and `walk_test.py --meltdown` (18 escape legs); `evac_report.py`; `door_audit.py` (43 doors).
* `measure_lighting.py` (23 views).
* `perf_report.py`; `export_unity.py` (export + re-import in an empty Blender process).
* `validate_halls.py` (the older hall audit): `PASS (geometry audit only)` with **0 halls** (no `LINKS` hall is left in this layout; the concourse and spine are covered by the walk tests), written to `validation/compact_report.json`.
* `render_views.py` (24 evidence views: `19_*` and `20_evac_*`) plus 14 of the lighting views copied as `19_walk_*`. Every image in `renders/assembly/19_*` was looked at; a stair-house exterior view rendered too dark at night to show anything and was not kept. Scratch renders were deleted.
* Cafeteria revamp compatibility (2026-10-14, after merging main with PR 105): `FRONT_END_SOURCE=revamp` build, identical patch log apart from the cafeteria's extra objects. The first walk found the revamp's new airlock and medical door leaves standing closed in two open doorways (6 routes stuck); with those leaves left out (as the original's parked leaves were open), all 8 front-end routes and the 5 meltdown legs through the cafeteria and yard pass, door audit 45/0, floor audit unchanged. The map then still linked the original front end.
* Cafeteria revamp switched on (2026-10-14, latest; section 1c): build; `plan_cut.py` + `check_overlaps.py`; `walk_test.py` (three modes); `evac_report.py`; `door_audit.py`; `floor_audit.py`; `perf_report.py`; `export_unity.py`; `measure_lighting.py` (25 views, then the 5 new cafeteria views); `render_views.py` (15 cafeteria views from the map, each looked at).
* Ore cart, cart-only freight door and mine cut (2026-10-15, latest; section 1d): build (and `MINE_LOD=0` for the before renders); `perf_report.py`; `cart_check.py --step 4 --tip-sweep`; `plan_cut.py` + `check_overlaps.py`; `walk_test.py` (three modes); `evac_report.py`; `door_audit.py`; `floor_audit.py`; `export_unity.py`; `measure_lighting.py` (30 views); `render_views.py` (mine before/after, 6 views each; cart, 10 frames), every image looked at. The perf, overlap, walk, floor, cart, export and mine-render steps were rerun after the last mine trim; the evac report, door audit and lighting ran on the build just before it (mine meshes only changed, and no lighting view or door is in the mine).
* After the condenser escape ladder (latest): build; walks 17/18 (cart route, as before), 10/10 proxies, 20/20 meltdown, 13/13 closed doors block; `evac_report.py`; `door_audit.py` 45 doors, 0 flagged; plan cut and overlaps (new entries: the escape door's frame on the bay's wall face, the front end's box round the shaft); `floor_audit.py` (no new flag); `perf_report.py`; export re-import PASS; lighting 24/25 (the new tunnel and hatch-house views pass; spine_mid as before); 32 evidence renders, the five `22_*` looked at. Before that, a column survey of the bay and the floor above, a 0.1 m occupancy map of the bay's north-west corner and the cable paths (found the 0.76 m pinch).
* After the stacked-slab fix: the full chain again on the rebuilt map (walks 17/18, 9/9, 18/18, 11/11 block; door audit 43/0; export PASS; lighting 22/23, condenser inside median 0.47; plan cut now at 10 heights), plus `floor_audit.py` (above, section 1a) and up/down ray probes in the condenser bay and the turbine aisle.
* After the turbine rebuild swap (2026-10-13), on the rebuilt `combined_map.blend`: the full chain again (build; plan cut + `check_overlaps.py`: the old turbine-reactor intrusion is gone, the only new entry is the D02 EXIT sign on the vestibule face, placed there; the three walk modes: 17/18 (the cart route, as before), 9/9, 18/18, 11/11 closed doors block; `evac_report.py`; `door_audit.py` 43 doors, 0 flagged; `perf_report.py`; `export_unity.py` re-import PASS, 183 objects; `validate_halls.py`; `measure_lighting.py`; `render_views.py`, 27 views). Two fixes came out of it and were re-checked: the D02 cut band missed the vestibule's end wall (meltdown walk stuck; band moved, both turbine escape legs then pass), and the stub view clipped 7.2 % on the shell's south face (darkened; 3.6 %). The board text was shrunk off a wall conduit (renders re-made). Before cutting, the rebuild was inventoried part by part and ray-scanned for floor occupancy, and 12 single-view renders of its doors were looked at.
Not run: Unity anything, a frame-rate test, an independent review, the room validators (including any validator on S1), a human playtest.

## 12. Condenser A3 (2026-10-19/20)

Owner: *"Rework the room to your liking, build into the main map and then ensure the baking process will work"*, later *"One more pass,
then merge"*. The map links `sources/condenser-bay/module_aaa_A3.blend` (room notes and reviews: `sources/condenser-bay/FINISH_A3.md`).

* **Level:** `COND` z -6.3 (was -6.0): the bay's own roof slab no longer shares the turbine floor's volume, so the patch only trims it 5 mm
  (target absolute, module 5.995); gallery headroom 2.07 m. The stair drop is `-COND[2]` (34 risers of 185 mm, 32.5 degrees), the escape
  ladder follows `COND`, the U04 pit walls are stretched locally to map z 1.2 (at -6.3 they stopped 6 cm short of the turbine machinery),
  `scene['condenser_z']` is read by `walk_test.py`, `measure_lighting.py` and `floor_audit.py`, and `unity/map/map_placement.json` is
  regenerated (condenser at -6.3).
* **Checks on the final file** (`20df1300...`), rebuilt map: plan cut 77 pairs (the two new ones are the U04 pit meeting the turbine again,
  as it did at -6.0); floor audit 39 pairs (unchanged); walks 17/17 with 13/13 closed doors blocking; proxies 10/10; meltdown 20/20; door
  audit 45/0; export re-import PASS (202 objects); lighting 29/30 (`spine_mid` as before; condenser inside median 0.47, near-black 1 %,
  clipped 0.1 %). `ROOM_condenser-bay` is 442,318 triangles in the map count (over the 400k flag, as A1 was: 422,140; 394,676 in the room
  file's own count).
* **Art:** four independent reviews rejected the finish (final 87 to 92 against "above 90 in all ten"); merged on the owner's decision.
* **Bake:** `unity/bake_all.ps1` includes the condenser; its CPU rehearsal is in `unity/README.md`.
* **Pitfall:** build `combined_map.blend` in place, and rebuild it after changing a linked room file that removes objects: the map keeps
  links by name, and a removed object shows as "missing linked data-block" at the next open (seen with two spindle guides).
