# Reactor room overhaul R1 (draft, needs review)

## Status at a glance

Rebuilt: architecture shell, doors, floor graphics, materials, fixture lighting, banks, control room interior, pool lining and rim glow, elevator with landing doors, station lamps, dressing, piping and cables (26 runs, connectivity-checked), one `REACTOR_STATE.stability` value driving the reactor light. Verified on the final file with `scripts/verify_scene.py` and `scripts/verify_piping.py`: 0 stair objects; elevator car, counterweight and landing doors keyed; both banks visible from the control room desk positions (75% of sample points each), 52-61% of the pool water and 41-44% of the hall floor.

Station remodel pass (scripts `v0b.py`, `v0c.py`, `v0d.py`, `st1.py` to `st4.py`, kit in `hs.py`): the legacy station housings were removed (interactive parts, gauges, legends and piping fittings kept in place) and replaced by new hard-surface builds: grid switchgear and demand console, bank-control console, generator set with silencer and alternator, reserve-power battery cabinets, tiered fuel rack with hoist and receiving table, fuel cart, waste cask, EC accumulators with manifold, coolant pump and starter, turbine casing with generator end, vent valve cage, sampling kiosk, work bench, plus floor props (barriers, drums, signs, drains, stools, lockers, carts) placed by an occupancy grid (`occ.py`), a bridge crane with animated bridge and trolley, and stability-driven wall boards. `st4.py` (crane and boards) has since been run.

Map connection fix (`ap1.py`, `ap2.py`): the map layout (`LAYOUT_A12.json`) expects the three reactor ports at 14.5 m (west `reactor.turbine`, local (-14.5, 0, 0); north `reactor.fuel`, (0, 14.5, 0); SE `reactor.cooling`, (11.016, -11.016, 0)). The earlier R1 build had moved the door planes to the hall wall and dropped the 3.7 m stubs behind them. The stubs and closed distant doors were re-imported from `module.blend` (recoloured to the R2 palette) at their original coordinates, and the hall-plane door leaves were removed so each doorway is open. Measured on the file: west door x -14.49..-14.39, y -3.00..3.00, z 0..5.50; north door y 14.39..14.49, x -2.50..2.50, z 0..5.00; SE door x 9.17..12.78, y -12.78..-9.17, z 0..5.00, all identical to `module.blend`. Rays from the hall along each door axis first hit the distant door, not a wall. The east control room, east stair and their two hinge empties are intentionally not carried over (elevator and interior control room replace them).

Verified on the current file: `verify_scene.py` (0 stair objects, elevator keyed, bank A/B 75% from the desk, pool 52-61%), `verify_piping.py` (26 runs, 0 dangling, 0 unconnected ports), `clearance.py` (0 clashes). A stray-vertex bug in the floor-prop placement (prop geometry outside the hall) was fixed by building each prop in its own buffer.

Not done: the draw-call merge; spec and art-direction documents still say clean and bright; no independent review; nothing measured in an engine; `module.blend`, `MASTER_MANIFEST.json` and the map files are untouched, so the map does not show this scene until it is reviewed and promoted.


Additive candidate: `sections/facility-assembly/sources/reactor-room/module_overhaul_R1.blend` (in LFS; contains the state described in `BUDGET.md`). It is rebuilt from `module.blend` with `scripts/`.
`module.blend` is untouched because `MASTER_MANIFEST.json` pins its SHA-256, and the assembled map still links it. The map shows none of this until the revision is reviewed and promoted (manifest hash, MAP.json and the derived preview regenerated).

## What changed in R1

| Area | Before | R1 |
|---|---|---|
| Control room | Outside the east wall at +10 m, window facing the east, so bank B hides behind bank A | Inside the hall on the -Y wall as a mezzanine (floor +5.4 m), 5.4 x 2.4 m window on the axis where both banks and the pool are side by side |
| Access | External stair core (about 700 objects) and a floor-level door to it | Traction elevator in the hall's south-west corner zone (x -8.0 to -5.6, y -8.0 to -5.6): glazed shaft, car, guide rails, counterweight, ropes, sheave and motor, with a railed upper landing and a door into the control room's west wall |
| East wall | Door and window openings | Patched panels; old "REACTOR CONTROL / 10" sign removed |
| Motion | Single 200-frame bank descent | 480-frame loop (16 s at 30 fps): banks A and B move out of phase between 7.0 and 8.5 m, pool glow pulses, elevator cycles ground and upper landing with ropes and counterweight following |
| Palette / mood | White, grey and orange with an amber pool | "Dead shift": dark and gloomy. Soot-iron, bruise-grey walls, mildew-olive lower walls, oxblood machines, rust-orange trim, wet dark floor; no teal, no cream. Dim violet-white practicals, some failing, some dead; thin haze; the reactor pool is the main light |
| Review cameras | `01_HERO` and `09_BANK_MECHANISMS` sat inside the new room | Moved to clear positions |

Interior contents of the old control room (1,493 objects from desks, screens and mimic panel) were rotated -90 degrees about Z and translated (x0 = -1.4, y +5.0, z -4.6) onto the mezzanine. Nothing else in the hall was moved.

## Asset Kit 1 and cleanup (after the layout work)

- Removed about 1,760 leftover stair-finish objects and about 4,900 modeled fasteners/grating bars (see `BUDGET.md`).
- New low-poly equipment at the existing station footprints, with `PORT_*` empties (medium, nominal diameter) for the piping pass: emergency-cooling accumulators EC-1/EC-2, coolant pump P-10, waste cask W-04, turbine set T-06. Named gameplay controls (`COOLANT_VALVE`, `EMERGENCY_COOLING`, `TURBINE_THROTTLE`, ...) were kept untouched.
- Scripts: `c1.py`/`c2.py` (cleanup), `c3.py`/`c4.py` (assets), `c5.py` (smooth shading).
- Piping and cables are deliberately last, so old pipes still end at the old positions and do not yet connect to the `PORT_*` empties.

## Placement constraints found

- The -Y wall is fully occupied at floor level (coolant pumps x -5.3 to -2.5, coolant valve x -1.7 to 0.7, emergency cooling EC-1/EC-2 x 1.1 to 3.9, storage x 4.3 to 5.1). The elevator therefore stands in the free south-west zone; the mezzanine only covers the emergency-cooling and pump area overhead (underside at +4.9 m, tallest equipment 2.8 m, coolant header at 4.7 m).
- All eight walls carry a door or equipment. The two banks sit at x = -1.4 and +1.4 (same y), so a window on the east or west wall always sees one behind the other; the -Y and +Y walls see them side by side.
- The east wall panels around the old door and window were patched with plain panels. The wall-mounted "A / SECTOR" graphics remain.

## Not done in R1

- Pipe, conduit and cable logic audit (every run needs a source, a sink and supports). Only the elevator ropes and the elevator/control-room additions were built with logic.
- Cables from the control room to the pool console and the banks, and elevator power feed.
- Remaining dressing, new assets, equipment layout changes and per-room lighting balance.
- Floor colour and the pool tile still need tuning after review; old conduit saddles at the back of the mezzanine (y -10.1 to -9.9, z 6.8 to 7.2) may clip and need rerouting.
- Not promoted: `module.blend`, `MASTER_MANIFEST.json`, MAP.json and the R17 preview are unchanged. The spec (`scenery/reactorroom.md` section 8) still says +10 m for the control room.
- No independent review, no collision/navmesh, no measured performance, no Unity import.

## Reproduce

`scripts/` holds the Blender Python steps in order: `b1.py` (relocate/delete), `b2.py` (wall patches, mezzanine, elevator), `b3.py` (palette via `palette.py`, pool lights, animation), `b4.py` (cameras, cleanup), `b5.py` (moves the elevator to the free south-west zone, rebuilds the landing and the door, patches the rest of the old east window). `render_final.py` makes the PR renders. They read and write `w1..w5.blend` from a scratch directory and need `bpy` 5.2.x (`pip install bpy==5.2.2` on Python 3.13). Renders in `../renders/overhaul-R1/` were Cycles CPU, 24 samples, frame 180. Before images in `before/` are 960x540, 12 samples.


## Dead-shift theme (owner brief)

Players leave a suspiciously cozy spawn room, pass the haunted mine and a barely operating refinery, then reach the sketchiest reactor room: dark, gloomy, spooky, with an eerie light from the reactor that changes color with reactor stability (unscientifically).

- `REACTOR_STATE` empty, custom property `stability` (1 stable, 0.5 warning, 0 critical). Drivers on the pool materials, pool volume, pool lights and the state key light turn it into: sickly green (stable), amber (warning), red (critical), with a pulse that speeds up and strengthens as it drops. The game side should drive this one value.
- Equipment from Asset Kit 1 is now faceted (8-sided forms, flat shaded) for the angular Valorant-style silhouette; smooth shading was dropped.
- Renders: `renders/overhaul-R1/dead_shift_*.png` (same camera at all three states, plus control room and emergency-cooling views).
- Scripts: `palette2.py` (palette), `d3.py` (state drivers, lights, world), `r12.py` (renders).

### Known gaps in the theme

- **Spec conflict:** `scenery/reactorroom.md` section 1 still calls the room a clean, sterile, bright working environment, and the art-direction canon says the same. This theme contradicts it and needs an owner-approved update; not edited here.
- Stylization is only partly there: forms are angular, but textures are still the old ones under a tint, not hand-painted stylized textures, and lighting is not yet stylized (no authored rim/shadow color language).
- The critical state reads orange-red rather than deep red and the pool core clips toward white.
- The spawn room's warm terracotta/blue is deliberately not used; the reactor room is meant to be the dark twin of it.


## Lighting pass 1

`scripts/e1_lighting.py` (from the dead-shift file). Goal: readable but spooky, carried by light: pools of light with real dark between them, complementary hues (toxic reactor light against sodium amber and cold lavender).

- Reactor: state-coloured beam rising from the pool, low fill, stronger pool emission; all driven by `REACTOR_STATE.stability`.
- Hall: 34 practicals rebuilt (2/3 sodium amber, 1/3 cold lavender; a quarter with broken-tube flicker, some dead); 3 cold roof shafts; 3 rotating red emergency beacons that wake as stability drops.
- Rooms and stations: flickering control-room lamp and state-coloured screens seen through the window, flickering elevator lamps, small colour glows at emergency cooling, turbine exhaust, waste hatch, generator and fuel bay; two low violet rim lights.
- Look: a thin haze volume for the shafts, dark plum world, AgX Punchy at -0.4 EV.
- Renders: `lighting_pass1_*` (stable, low stability, control room view, and four frames three apart showing the flicker).

### Known gaps

- Walls still read flat grey; the palette needs more colour contrast against the lighting.
- Light shafts and the beacon sweep barely show in stills; they need a visual check in motion.
- Low stability (0.25) reads orange-amber; red only near 0.
- About 45 lights were added. That is fine for Cycles, but a real-time build cannot run that many dynamic lights: most must be baked or faked with emissives, and only a handful realtime. Not evaluated in an engine.


## Verification of the control room, stairs and elevator (measured on the file)

- **Stairs:** 0 objects or collections with "stair" in the name and 0 meshes using stair/tread materials after `f1_window_and_stair_cleanup.py`. 16 stair wall-finish panels had been carried onto the mezzanine when the room was relocated; they are deleted.
- **Elevator:** 42 objects; car and counterweight keyed; car floor 0.0 to 5.4 m while the counterweight goes 7.45 to 2.05 m.
- **Control room sight** (`verify_control_room_sight.py`, ray casts through the glass, haze volume ignored): the original 5.4 x 2.4 m window with a 0.7 m sill saw 0% of the pool and 6 to 16% of the hall floor. The window is now near-floor-to-ceiling (sill 0.25 m, 6.4 m wide, 2.85 m tall). From the centre desk: both drive columns 75% of sample points (the base below the pool rim is hidden), pool water 61%, hall floor 43%. Standing at the glass: pool 86%, floor 49%. The north half of the hall is mostly visible; the south half beside and under the mezzanine is not, and the left end of the room sees none of the pool.
- Renders: `control_room_eye_a_from_the_desk.png`, `control_room_eye_b_standing_at_the_glass.png`.


## Overhaul stage 1: stylised material look (`g1_stylise_stage1.py`)

Reference: the spawn room screenshots (bold colour blocking, crisp painted trim, clean edges, high-fidelity stylised finish), translated to the reactor room's dark theme. 58 existing materials got procedural nodes (no image textures): painted navy dado with a rust trim line on wall materials, worn bright edges from a bevel-normal mask (rust on iron, oxblood-orange on machines, violet on walls), and grime rising from the floor with noise. Render: `stage1_stylised_hero.png`.

Gaps: walls still read grey-olive rather than plum under the current light mix; these are Cycles procedural nodes and must be baked to textures for an engine build (bevel and world-position nodes do not exist there); no new modelled detail, decals or signage yet.


## Rebuild A: new architecture shell (`j3_rebuild_architecture.py`, `r2lib.py`, `k1_relight_for_new_architecture.py`)

Owner direction: the legacy scene looks archaic next to the spawn room, so this is a structural rebuild, not a tint. About 2,200 legacy architecture, wall-finish, services and floor-detail objects were deleted in this revision (`module.blend` still has them) and replaced by a generated shell of 176 objects: 24 structural columns and 8 corner piers, plinth/navy dado/rust rail/plum panel/lintel band/upper panel tiers with raised insets, cornice with trim stripe, clerestory windows, roof girders, a tiled floor, and three real blast doors (recessed reveal, closed leaves, slits, handles, status lamp, lit sign) at the fixed door positions: MAIN ACCESS (west), FUEL HANDLING (north), COOLING PLANT (south-east diagonal). Materials are new procedural stylised ones (mottled paint, bevel edge wear, floor-up grime). Lighting was rebuilt as modelled wall-washer fixtures on the cornice, alternating sodium amber and cold lavender, some failing.

Removed with the legacy layers, to be rebuilt in the piping pass: wall conduits, cable trays, coolant headers, junction boxes.

Not yet: floor inlays and stencils, wall graphics, dressing, ceiling detail, remaining equipment, pool lining, draw-call merge, piping/cables.


## Rebuild B: floor, graphics, dressing, station lighting

- `m1_floor_graphics_dressing.py`: floor inlays (orange safety ring round the pool; route lanes with chevrons from the three doors to the pool; drain grates), painted wall graphics (sector numerals, company and safety stencils), angular drums and crates.
- `n2_station_lamps_palette5.py`: task lamps (modelled hood plus spot) for the generator, reserve power, grid cabinets, turbine, fuel bay, fuel racks, waste cask and pool console; equipment materials lifted; edge-wear masks thinned.
- `n4_fixture_shadow_fix.py`: **bug fix.** Every fixture's light sat inside its own closed housing, so the housing blocked the light. This is why the cornice washers, beacons and (at first) the task lamps lit almost nothing. Housings no longer cast shadows.


## Rebuild C: banks and control room interior

- `o1_banks.py`, `o3_bank_lighting_labels.py`: both control banks rebuilt as angular octagonal housings with hazard bands, hydraulic cassettes (with `PORT_BANK_*_hyd_*` empties), state-glow rings, and moving drive columns with banded state-glow scale marks, parented to the original `BANK_A_MOVING` / `BANK_B_MOVING` empties so the animation is unchanged. Gameplay names `BANK_x_FIXED_HOUSING`, `BANK_x_CARRIAGE`, `BANK_x_DRIVE_COLUMN` are kept. Uplights and gantry lamps added.
- `p1_control_room_interior.py`: the legacy control-room dressing (297 objects) is replaced by a rebuilt interior: low console desk with five monitors (kept below eye height so the window sight line stays clear), mimic wall panel with state-coloured nodes, chairs, shelving with binders, cabinets, a cot in the corner, papers and mugs, ceiling panels and a desk lamp. The room shell (floor, back wall, roof) is regenerated as well.


## Rebuild D: elevator doors, pool glow, dressing (`q2_elevator_doors_pool_glow_dressing.py`)

Sliding landing doors at the ground and upper landing, keyed to the car (open while the car is at that level), indicator lamps, call panels, floor signs and a hazard stripe; a state-glow ring round the pool rim and eight glow slots on the pool wall; framed posters, exit signs over the three doors, caution-tape barriers, cones, a wet-floor sign and puddles.


## Piping and cables (`scripts/pipes_and_cables.py`, checked by `scripts/verify_piping.py`, runs in `piping_runs.json`)

Built last, from the `PORT_*` empties. 26 runs, 76 objects, plus a perimeter cable ring.

- **Coolant:** plant supply enters through the -Y wall (sleeved penetration, `PORT_WALL_COOLANT_SUPPLY`), runs along the wall header, tees down into EC-1 and EC-2, and its far end drops through the two isolation valves of the coolant-valve station and into the pump suction. Pump discharge rises, drops into a floor trench junction box, runs under cover plates to the pool inlet manifold, and a submerged riser ends in a diffuser in the pool. EC-1/EC-2 injection lines leave through the wall.
- **Steam:** lagged supply enters the east wall high, drops onto the turbine inlet; the exhaust leaves through the wall.
- **Waste vent:** cask vent rises and exits through the north-east wall.
- **Hydraulics:** a pressure unit and a return tank hang from the gantry; four lines connect the bank cassette ports to them.
- **Power:** a perimeter cable tray ring at z = 11.6 m, with conduit risers from the grid cabinets, turbine sensor, generator, bank control console, control room, elevator machine, waste-vent control, both reserve-power racks and the west bench socket; the pump starter feeds the trench junction box.
- About 36 old dangling pipe and feed curves were deleted because the layers they connected to no longer exist.

`verify_piping.py` result on this file: 26 runs, 0 dangling ends (every end is a port, a device, a tee on another run, the trench, the diffuser, the pressure unit or the cable ring), 0 unconnected `PORT_*` empties. It checks connectivity only, not clearance or collisions with walkways or equipment.

## Final pass: station kit, piping rebuild, engine hand-off

- `s1.py`: hazard-stripe stencils, bollards, wall sign plates with emissive text, waste ring and hood at stations.
- `pipes2.py`: piping rebuild with clashes fixed (26 runs). `clearance.py` ray-casts every run: 0 clashes. Run data in `piping_runs_generated.json`.
- `t1.py` / `t0.py`: material consolidation (48 in use), UVs on all meshes, gauge ticks removed, text/curves merged or converted to meshes.
- `t2.py`: bake and glTF export into `engine/`.
- `verify_scene.py` on the final file: 0 stair objects; elevator car, counterweight and 4 landing doors keyed; from the desk both banks 75% visible, pool water 52-61%, hall floor 41-44%. Standing exactly at the glass a mullion hides bank B.
- Not done: generator, grid cabinets, fuel racks, sampling station and pool console are restyled (kit, lights, signs, connections) but not remodeled; `sections/reactor-room/scenery/reactorroom.md` still describes the older clean/bright room and needs an owner decision; no independent review; `module.blend`, `MASTER_MANIFEST.json` and `MAP.json` are untouched.

## Verifier and export script usage (review fixes)

- `scripts/verify_piping.py -- <scene dir> <scene.blend> [runs.json]` and `scripts/clearance.py -- <scene dir> <scene.blend> [runs.json]` read the checked-in `piping_runs_generated.json` by default (pass a manifest path as the third argument to override) and exit with status 1 when there are dangling runs, unconnected ports or clashes, 0 otherwise.
- Run the verifiers headless through Blender with `--python-exit-code 1`, so a script that reports `FAIL` (or raises) makes Blender itself exit non-zero for shell or CI callers, for example: `blender --background --python-exit-code 1 --python scripts/verify_piping.py -- <scene dir> <scene.blend>` (same for `clearance.py`; `t2b.py` and `ap1.py` should be launched the same way).
- `scripts/ap1.py -- <scene dir> <src.blend> <dst.blend> [module.blend]` finds `module.blend` relative to the repository by default; the fourth argument overrides it, and a missing file stops with an error.
- `scripts/t2b.py` no longer swallows glTF export errors: a failed export raises (non-zero exit) and `ok` is only printed after the GLB exists.
- `verify_piping.py` tolerances were re-synced with the final layout (trench junction box and pool diffuser positions). The previous checked-in copy predated those layout changes and reported 2 false dangling runs on the shipped scene.

## Control room depth +50% (`scripts/cr2.py`)

The window-to-back-wall depth grew from 3.94 m to 5.92 m (glass at y -5.99, back wall inner face at y -11.91). The **back wall** moved back 1.97 m; the window, desks, chairs, west door, elevator landing and rails did not move. The hall's south wall is only about 0.5 m behind the old back wall, so an opening (x -5.0..2.2, z 5.16..9.0) was cut through the wall slab, panel bands, insets and pilasters, and the room's floor, soffit, roof, side walls and long beams were stretched out through it. The back wall, back furniture, shelves, east storage run, cot and back lamps, readouts and screens move as rigid pieces. One extra ceiling light covers the new rear area.

The new rear volume sits outside the octagon shell (to about y -12.1, x -5.0..2.2). In the assembled map the reactor room is placed at (14.2, 46.5) rotated 180 degrees, so this bay lies at about x 12..19, y 57.3..58.7; `LAYOUT_A12.json` lists no placement or reserved volume there, but the cooling-plant footprint (placed at (-2.5, 63.2)) was not measured.

Verified on the modified scene: sight lines unchanged from before (`verify_scene.py`: bank A and B 75% from the desk positions, pool water 52-61%), `clearance.py` 0 clashes, `verify_piping.py` 26 runs / 0 dangling / 0 unconnected ports, rays from inside the room pass through the opening to the new back wall, the hall wall above the room is intact (`cr2_chk.py`). The engine export (`engine/reactor_room_R1.glb`) has not been regenerated for this change.

## Control room redo (`scripts/cr_build.py` and the `cr_*.py` / `crk.py` / `crt.py` modules)

The first 1990s pass (uniform chamfers, purple plum palette, flat lighting, primitive props) was rejected and is **replaced entirely** by this one; its scripts (`co1.py`, `co_mat.py`, `co_views3.py`, `grid5.py`) and renders were removed. Everything inside the deeper 5.92 m room was rebuilt at spawn-room fidelity: only the floor slab, back-wall slab, ceiling slab, side walls, window glass and mullions and the door opening are reused as structure.

**Pipeline.** `cr2.py` (depth) then `python cr_build.py -- <src.blend> <dst.blend>`. `cr_build.py` is idempotent: it deletes a previous run (collection `31 CR CONTROL ROOM REDO`) and everything in `26 R2 CONTROL ROOM` except the structural slabs, so it can be run on the shipped `module_overhaul_R1.blend`. Set `CR_TEXT_CACHE=<dir>` to cache the rendered lettering between runs (first run renders about 150 strings and takes several minutes).

- `crk.py`: kit. Every element is a box/hull/cylinder with its **own** bevel (2-12 mm, 2 segments), bevel facets smooth and big faces flat (crisp planes, soft edge highlights), plus the spawn recipe material (Principled BSDF, low-frequency noise albedo variation, fine bump on non-metals, painted edge highlight), emissive/driver helpers, text and light helpers.
- `crt.py`: hand-painted style textures generated with numpy (no scans, no photo textures): six propaganda posters, six forms and notices, floor tile, CRT phosphor screens, TV telemetry / broadcast / NO SIGNAL images. `text_mask()` renders any string to an anti-aliased mask so the lettering is real.
- `cr_mats.py`: palette of charcoal, graphite steel, olive-grey paint, mineral plaster, beige early-90s plastic, laminate, with hazard orange and yellow accents. `cr_shell.py`: wall cladding (olive dado panels with screws, plaster modules with reveal joints, dado rail, rubber cove base), door frame with hinge plates, corner guards, floor markings, suspended ceiling (T-bar grid, tiles, missing tiles with duct and cable tray behind them, three troffers, one with a dying tube).
- `cr_desk.py`: three desk bays with real kneeholes (end panels, modesty panels, cable trays, grommets, glides), three 14-inch CRT terminals (dome glass, badge, knobs, vents; two green and one amber; one with a tower case), keyboards as **one flat plane with a painted QWERTY colour map plus the same layout as a height map driving a bump** (about 40 triangles each instead of about 11,000; the usual game-art trick for small dense detail), ball mice, five-star task chairs with gas lift, casters and armrests **tucked straight** under the desk (`cr_verify.py` checks that no chair vertex touches the desk-top slab).
- `cr_props1.py`, `cr_props2.py`: 19-inch server rack (UPS, patch panel with cords, two servers, tape drive, fan panel, about 60 LEDs on flickering materials), copier and dot-matrix printer corner, tall shelving with binders and boxes, cot, lockers, break corner (fridge, microwave, kettle, mugs, tins, clock), work table with plans and lamp, TV credenza with VCR and tapes, dead plant, six posters, pinboard with forms, coat hooks, extinguisher, aircon, PA horn, CCTV dome, outlets, raceway, smoke detectors, sprinkler heads, blind cassette. Fictional brands only (KESTREL, AXON, RIVEN, MERIDIAN, VOLTEX, TAKAMI, CIRRUS).
- `cr_light.py`: warm tungsten key zones over the desk row (three troffers), the rack (batten) and the work table (pendant, work lamp), a dim warm fill so far corners stay readable but darker, cool window and door spill, and coloured accents (CRT glows, rack LED glows, TV).
- `cr_tv.py`: the wall TV. A 20-second cycle (600 frames at the scene's 30 fps; the keys are rescaled from `fps`/`fps_base`) of reactor telemetry (tinted by `REACTOR_STATE.stability`), static burst, propaganda broadcast, static, NO SIGNAL bars, static. The empty `CR_TV` carries animated weights (`w_tel w_bro w_sta w_bar w_clip`) and the clip colour/intensity track (`clip_r clip_g clip_b clip_e`); the screen shader and the area light both read them, so the light colour and strength always match the picture.
- `cr_tv_clip.py -- <in.blend> <clip> <out.blend>`: **custom clip slot.** Loads the clip (movie file or a PNG/JPG frame sequence, first file given) into image node `TV CLIP`, switches the TV to clip mode, samples every frame at 32x18 and keyframes `clip_*` so the TV light follows the clip; also writes `tv_light_track.json`. Tested here with a generated 48-frame PNG sequence only (red to blue track came out monotonic and complete); **movie files (mp4, mov, webm) were not tested because the headless Blender used here has no FFmpeg** - run it once in a normal Blender build and check `tv_light_track.json`.
- `cr_tv_slides.py -- <in.blend> <image folder> <out.blend> [--hold FRAMES]`: **TV slideshow** (simpler than a video). Every image in the folder (sorted by name) is scaled to 640x360 and packed into one atlas texture; the TV shows slide `floor(((frame-1) mod (N*hold)) / hold)` (default hold = 20 s x scene fps / N frames, so the show loops in 20 s), and the `CR_TV` props `clip_*` get one constant key per slide (mean colour and brightness of the slide) so the light in front of the TV changes with each slide. Tested with three generated slides (picture and light checked at three frames); the atlas is a static texture, only the slide index is a driver.
- `cr_pal.py`: **purple is removed from the entire scene**, not only the room. Every unlinked colour in every material, node group, light and the world with hue 225-345 degrees is remapped at preserved luminance (blue-violet to steel blue-grey, plum to olive-khaki for surfaces, cool neutral for lights, haze and emission); the hall's plum walls, tiles, fabric, haze and violet lights change accordingly. The view transform is now AgX with `AgX - Medium High Contrast`.
- `cr_verify.py`: envelope, intersections with other collections (vertex level), walkability (2D occupancy dilated by a 0.28 m player radius, flood fill from the doorway, 15 zones), chair tuck, purple audit (materials incl. emission, lights, world, images), triangle counts. `cr_final_shots.py`: the final camera set incl. the four TV states.

**Second pass (after the darker-mood review).**
- *Fixes:* TV light narrowed to a downward-tilted spot cone (the ceiling no longer goes green); the pendant lamp over the work table sparkled because its spot light overlapped the diffuser, it is now a disc light at the diffuser with a matte shade; chair backs are now shaped (7-degree tilt, lumbar bulge, tapering pad, headrest, side bolsters, shell) and the chairs sit 4 cm further back so the shape clears the desk edge (`cr_verify.py` checks this); a real steel door leaf (vision panel, lever, closer, number plate, hinge barrels, badge reader) stands open against the north jamb; grime (water stain streaking down the back wall and on two ceiling tiles, floor scuffing, coffee spills), a ribbed rubber mat under the operator chairs, and a black/yellow floor cable cover with cables, tape and ramps.
- *Mood and story:* the troffers and the TV follow `REACTOR_STATE.stability` (steady tubes dim and stutter as it falls, the dying tube gets worse) and two red emergency beacons (door wall, back wall) stay dark above stability 0.5 and pulse harder as it falls; the QUESTIONS poster is defaced in marker; personal desk items (family photo, sticky notes on the CRTs, thermos, cup rings, a spill, cold tea and an untouched sandwich); the hall-side glass is dirty with streaks and has four taped notices facing the pool; a worn `SHIFT 04 - CONTROL` stencil above the TV, a floor `EXIT` arrow and `OPERATOR` markings; rack variety (second server slid out on rails with board and fan, coloured cord tags, cable loom with ties); a faint neutral haze volume (`CR haze volume`, render only).
- *Engine side:* 25 axis-aligned collision proxy boxes in collection `32 CR COLLISION` (wire, not rendered) and `control_room_collision.json` (desks filled under the kneeholes, furniture, door leaf, thin walls with the west door opening free). `cr_verify.py` check 7: proxies cover 99% of the detailed occupied floor area (excluding a 0.25 m wall strip) and every zone is reachable using the proxies alone.
- *Verifier changes:* `verify_scene.py` now skips the haze volume and the collision proxies and allows up to 16 pass-throughs per ray (the first run after these additions reported 0% because the new volume and proxies consumed the old 6-hit limit); `cr_verify.py` exempts the intentionally out-of-room hall-side notices.

**Third pass (after reading the new Blender skills; look first, speed second).**
- *Fixes:* the hall-side glass is mostly clear again (sparse streaks only, neutral tint) so the reactor stays readable from the desks; the TV cycle is now really 20 s (the scene runs at 30 fps, so the old 480-frame cycle was 16 s; verified numerically: weights sum to 1 at every frame, seam at frame 601 equals frame 1); the haze is thinner, forward-scattering and stops about 1.2 m short of the window; the plaster bump and mottling are reduced (it read as mould under grazing light); the rack's blank plates are replaced by switches, a modem bank, keyboard drawers and vented blanks; a work jacket hangs on the bay-3 chair, a jacket and boots lie by the cot.
- *UVs (blender-uv-texturing):* before this pass 97% of the mesh corners of the room had UV (0,0), so nothing could be baked or exported. `crk.Kit.build` now writes a **world-scaled box projection** (1 UV unit = 1 m, dominant-axis per face) for every face without an authored UV; 0.2% of corners (545 of 304,084) remain at the origin; I did not analyse which faces they are. Posters, forms, screens and the keyboard top keep their authored UVs.
- *Delivery derivative and round trip (game-asset-pipeline), `scripts/cr_delivery.py`:* on copies only, 42 procedural materials are baked to 256 px albedo tiles (single-location bake, not seamless, roughness/metal constants, no normal or AO), 19 emissive materials are frozen at frame 1, the floor keeps its seamless image through the UV, 25 materials already used the UV map. Exported to GLB (about 15.3 MB, not committed; regenerate with the script), re-imported into an empty scene: 294 objects in and out, 154,474 triangles in and out, bounds difference 0.0 m, 87 materials, 73 images (10.8 MPix), 0.1% of UV corners at the origin. The neutrally lit re-import render (`renders/overhaul-R1/control_room_delivery_roundtrip.png`) was opened: floor tile, posters, keyboard, TV, stain and stencil survive; colours are approximate, and drivers, stability reactions, the TV cycle and flicker do not export. Report: `control_room_delivery_report.json`.
- *Statuses, kept separate (V00 labels):* technical authoring checks Passed (`cr_verify.py`, piping, clearance, sight lines); Blender round trip Passed (numbers above); visual QA of the renders done by the author only (no independent review); engine import, materials, colliders and Player behaviour **Blocked** (no asset-specific validator and no working Unity target; the stock foundation runner does not import the map); formal room acceptance **not run** (style slice, review cycles and cold start from the production protocol were not executed, so this is an authoring pass, not an accepted room).
- *Not done:* no LODs or instancing (inventory only: 154k triangles, 87 materials, 73 images / 10.8 MPix in the delivery derivative, no ratified budget), no seamless tile bakes, no normal/AO bakes, no Unity run.

Verified on the shipped file: `cr_verify.py` PASS (0 envelope violations, 0 intruding objects, all zones reachable, 0 chair/desk overlaps, 0 purple-band colours, 0 purple images); `verify_piping.py` 26 runs / 0 dangling / 0 unconnected ports; `clearance.py` 0 clashes; `verify_scene.py` sight lines identical to before the redo (bank A and B 75%, pool water 52-61%, hall floor 40-48%). The redo collection has about 154k triangles in 312 merged objects (about 168k before the keyboard trick) (budget deliberately deferred: hero props are several thousand triangles each). **Not done / not measured:** the engine export (`engine/reactor_room_R1.glb`) was not regenerated and drivers do not survive glTF (the TV, LEDs and screens would export as one static state); no engine measurement, no draw-call or texture-memory measurement; no instancing or LODs yet (candidates: the four chairs, the terminal kits, the shelf binders and boxes, the rack plates); the stability-driven lights, beacons, TV and LED flicker are Blender drivers that the engine has to re-implement from the same inputs (`stability`, frame); no independent review; `module.blend`, `MASTER_MANIFEST.json` and `MAP.json` are untouched; `reactorroom.md` still describes the older bright room. Renders are `sections/reactor-room/production/renders/overhaul-R1/control_room_redo_*.png` (six main views at 1280x720, a TV cycle sheet at frames 1/205/300/480, a reactor-stability sweep at 1.0/0.6/0.3/0.1, stencil, defaced poster, cot corner, keyboard close-up, delivery round trip); composed with `scripts/cr_contact.py`.
