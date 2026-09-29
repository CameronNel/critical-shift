# Reactor room overhaul R1 (draft, needs review)

## Status at a glance

Rebuilt: architecture shell, doors, floor graphics, materials, fixture lighting, banks, control room interior, pool lining and rim glow, elevator with landing doors, station lamps, dressing, piping and cables (26 runs, connectivity-checked), one `REACTOR_STATE.stability` value driving the reactor light. Verified on the final file with `scripts/verify_scene.py` and `scripts/verify_piping.py`: 0 stair objects; elevator car, counterweight and landing doors keyed; both banks visible from the control room desk positions (75% of sample points each), 52-61% of the pool water and 41-44% of the hall floor.

Not done: baking and UVs for an engine build; material consolidation (77 in use, target 40); the remaining draw-call merge (station objects kept separate on purpose); the generator, grid cabinets, fuel racks, sampling station and pool-side console are legacy models with new materials, lights and connections, not redesigned; collision-clearance check for the new pipes; spec and art-direction documents still say clean and bright; no independent review; nothing measured in an engine.


Additive candidate: `sections/facility-assembly/sources/reactor-room/module_overhaul_R1.blend` (**not in this commit**: the Git LFS upload was blocked by the session's network policy for `lfs.github.com`; it will be added once that host is allowed. Until then the file can be rebuilt from `module.blend` with `scripts/`).
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
