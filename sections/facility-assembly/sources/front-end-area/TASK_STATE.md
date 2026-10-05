# Front-end area (cafeteria, hall, yard): production state

**Status: second build, unreviewed. Not independently reviewed, not accepted, not promoted anywhere.** Built 2026-10-04 from the
design in `design/facility-layout/front-end-area/DESIGN.md` and revised with the owner's review notes the same day.
Art label: owner's brief is "run-down, half-abandoned, horror-adjacent". Warm concrete, machine grey, charcoal steel, rust,
ochre; no teal.

## Files
- `front_end_area.blend`: editable scene (LFS). Collection `MODULE_front-end-area` with YARD, CAFETERIA, HALL, SHARED, LIGHTS,
  CAMERAS, INTERFACES. Prototypes live in a `PROTOTYPES` collection that is excluded from the view layer.
- Procedural source (kept, re-runnable): `build_front_end.py` plus `fe_*.py`. Rebuild with
  `blender --background --factory-startup --python build_front_end.py -- --stages shell,yard,cafeteria,hall,dress --output front_end_area.blend`.
  Needs `../mine-r39/module_r39_aaa.blend` (LFS pulled) for the mine front.
- `render_views.py`: renders the fixed cameras (see `CAMERAS.md`). `validate_front_end.py`: numeric checks, output `validation.json`.
- `renders/`: the nine v3 whole-area images (not regenerated this pass) and the eight revision 4 cafeteria images `CAF_*` (1600 x 900, 32 samples), all opened and inspected.

## Frame and interfaces
Module-local frame: origin at the spawn airlock threshold, +Y into the building, +X east. Plan = local + (8, -80).
Seven `IF_PORTAL_*` empties with clear width, height and outward normal: spawn airlock 2.6 m, yard door 3.0 m, medical door 2.2 m,
cafeteria-to-hall opening 6.0 m, hall west door 2.4 m, hall east door 2.4 m, spine blast door 3.6 m. All sit at the planned
plan positions; none were moved.

## Revision 7 (2026-10-05): yard rebuilt as the mine surface depot
The owner asked for the yard next, with the same standard: everything must make sense, cliff, portal front and ground rebuilt as well. The old yard was a random scatter (mixed-colour containers, trees, shrubs, barrels, bales and tyres, a pickup, van and forklift with no reason to be where they were). It is replaced by the surface depot of the mine (see `design/facility-layout/front-end-area/DESIGN.md`, yard section):
- **Portal:** natural cliff (benches, jointing, no block pattern, flattened around the portal), concrete collar with piers and lintel, steel jamb liners, hazard soffit, three timber sets with lagging, baked entrance plate, lamps, rock bolts and safety mesh; ventilation fan beside it with a duct stub into the rock. The reused R39 front panel (`fe_minefront.py`) is gone.
- **Lamp room and rail:** site cabin with barred windows, glazed door, steps and AC unit; tag board; three numbered ore cars loaded with ore; flush track scale with a display post.
- **Ore bays:** three push-wall bays (grade A, grade B, waste rock) with ore piles and baked plates, skid loader in front, caged gas store.
- **Rail dock:** two loading docks either side of the freight gate under the canopy, parcels, drums, hand truck, forklift, amber beacons, hazard threshold, STOP TRAINS stencil.
- **Vehicles and fuel:** three marked bays with wheel stops and numbers (new utility pickup, new crew van, forklift), bunded diesel station with two tanks, pump and board.
- **Store and power:** three green containers with baked plates, marked muster area B, fenced generator, water tank. **Porch:** benches, PPE check and site rules boards, recycling, planters.
- **Ground:** concrete apron with light wear (four slabs slightly sunk, two cracked, none missing), painted lane edges, bay lines, hatching, three trench drains; 212 wear decals now cover the hall, the yard apron and the cafeteria's yard-facing wall.
- Removed: all trees, most shrubs, barrels, bales, tyres, cones, crates, cable drums, steel stock, pipe stacks, hose reels, planters except three, `fe_yard2.py`, the old props and `fe_minefront.py`. `fe_yard.py` is reduced to constants and `inst()`.
- New modules: `fe_yard3.py` (apron, cliff, portal, rail, fence and gates, canopies, drains), `fe_depot.py` (layout, signs, markings), `fe_depot_assets.py` (pickup, van, ore car, ore pile, cabin, track scale, skid loader, fuel station, ore bays, rock bolt, safety mesh, LED pole, wheel stop, dock, beacon, fan).
- Cameras: `YRD_01` to `YRD_07` plus `YRD_X1` portal close, `YRD_X2` freight gate, `YRD_X3` evacuation gate (see `CAMERAS.md`).
- Numbers (`validation.json`): total 570,374 triangles (yard 214,170, cafeteria 262,624, hall 90,584, shared 2,996); 129 interior and 114 yard floor objects, 0 gap and 0 penetration failures; clear lanes pass; no prop-prop intersections except piles inside their bays (checked with a bounding-box script).
- Not done: the whole-area `FE_*` renders are stale; vehicle bodies are simpler than the hall props; the refinery side beyond the freight gate is not modelled. Unreviewed, no independent review, not accepted.

## Revision 6 (2026-10-05): hall rebuilt as an operations hub
The owner asked for the hall to be refined and for everything in it to make sense. The previous hall was a scatter of jersey barriers, sandbags, scaffold, cable drums and a cave-in with no purpose, plus a gantry that led nowhere. It was removed (`fe_hallsite.py` deleted) and the hall rebuilt around one idea: **the shift hub and junction of the facility**. Every item belongs to a zone with a job (plan frame, x east, y north; hall x -4..32, y -60..-48):
- **Locker room and PPE issue (south-west):** eight steel PPE lockers on the west wall (two ajar with a hard hat and hi-vis), two changing benches, a PPE dispenser, a safety briefing board, water cooler, cleaner's cart.
- **Shift desk (south wall, x 12..16):** staffed desk with three monitors, radio base, phone, chair behind it; schedule board; radio charging dock and key cabinet. It sits beside the cafeteria opening so arrivals check in first.
- **Dispatch / goods in (south-east):** three painted pallet bays A to C, palletised parcels, pallet jack, roll cage, hand truck and two shelving bays, beside the east door to the trunk road to the dock and waste.
- **Emergency and status (north-east):** safety station (eyewash, first aid, AED, extinguisher, spill kit), fire hose cabinet, facility status board, evacuation plan, and a marked green muster area at the east end.
- **Blast door (north, reactor axis):** 3.6 x 3.2 m door with beacons, a control post (key switch, e-stop, lamps, keypad), an interlock notice (hard hat, dosimeter, two-person rule), two bollards and a hazard hatch in front.
- **Maintenance bay (north-west):** workbench with vice, tool wall, tool chest, parts shelving, marked floor zone, directly under the stair to the plant gantry.
- **Plant gantry (rebuilt):** a 10 m grated deck at 4.2 m over the blast door, reached by a 21-tread stair with sloped stringers (the old stair used horizontal beams), serving a closed plant-room hatch in the north wall.
- **Wayfinding:** four hanging signs (refinery, dock/waste, reactor spine, cafeteria), floor stencils, yellow walkway lines along the two clear lanes, exit signs over both end doors, painted double leaves with vision panels on the end doors.
- **Overhead services:** supply duct and PA horns along the south wall, red sprinkler main with heads, cable tray with cables, two rows of light strips, smoke detectors, four CCTV domes. All clear of the gantry and signs.
- **Lettering:** every sign, board, label and floor stencil is baked in the sign atlas; no text objects remain in the hall. New icons: hard hat, wrench, bolt, box, warning, muster, lock.
- Also fixed: the cafeteria kitchen's extractor hood poked through the hall wall; it is now a three-box hood inside the block. Painted-steel props had ignored their colour (no vertex-colour material); a new `paint` material fixes the lockers, bench, tool chest and station.
- Wear: the decal pass now covers the hall (lanes, door scuffs, bays, blast door, dado scuffs, skirting dust, streaks).
- Cameras: `HAL_01` to `HAL_06` plus door checks `HAL_X1` blast, `HAL_X2` west, `HAL_X3` east (see `CAMERAS.md`).
- Numbers (`validation.json`): total 683,384 triangles (yard 327,180, cafeteria 262,624, hall 90,584, shared 2,996). 129 interior and 130 yard floor objects, 0 gap and 0 penetration failures; clear lanes pass; seven interface portals unchanged.
- Asset library: five new groups in `asset-workspace/` (hall_ops, hall_work, hall_safety, hall_shell, and the hall door leaf).
- Not done: yard art; the whole-area `FE_*` renders are stale; hall `FE_03` and `FE_07` no longer match. Unreviewed, no independent review, not accepted.

## Revision 5 (2026-10-05): textures, panelling, wear, asset workspace (final pass)
The owner said the walls read as "90s doom graphics", some assets needed overhauls, and everything should look a bit worn. Only the cafeteria and the shared hall shell were touched.
- Textures (new `fe_textures.py`, numpy + Pillow, build time, tileable, deterministic): `plaster5` (painted lime plaster with orange-peel stipple, trowel swirls, roller streaks, hairline cracks, pits), `wood5` (sealed timber veneer), `metal5` (brushed steel), `cork5` and `wear_atlas.png`. They replace the blotchy CC0 plaster, wood and metal sets on the walls, ceiling, timber and charcoal steel; the old files stay in `textures/` for the yard. A new `steel_brushed` material (light stainless) replaces the dark charcoal on every light-coloured steel part.
- Wall panelling (real geometry, in `fe_shell.py`): wainscot stiles and top, middle and base rails over the navy dado, two-step cornice with a cove, pilaster bases and capitals. About 20k triangles.
- Wear (`fe_wear.py`): 107 single-quad decals sampled from `wear_atlas.png`: floor traffic paths along the airlock-to-hall, yard-to-medical and queue lines, skids at the doors, scuffs, blotches, dado scuffs, skirting dust, water streaks under the rail and the high windows, handprint smudges beside door frames, corner grime. They are named `stain_*` or `streak_*` and cast no shadow.
- Asset overhauls: booth (kick plinth, channel-quilted vinyl back with buttons, piping, edge-banded table), water cooler (tap recess, drip tray, cup tube, full bottle), microwave bench (cabinet doors, real microwave, kettle, toaster, splashback), cutlery station (tubs with cutlery), recycling station (lids, apertures, label strips, wheels), cork notice board, brushed-steel serving-counter doors with handles; chair back tubes now end in brackets behind the shell (they used to poke through); the order kiosk was rebuilt as a single slim pillar.
- Asset workspace: `asset-workspace/` (see its README) collects every prop into `asset_library.blend` and renders labelled contact sheets with triangle counts against caps.
- Numbers (`validation.json`): total 715,274 triangles (yard 327,180, cafeteria 262,100, hall 122,998, shared 2,996), within the 800k budget. 154 interior and 130 yard objects: 0 gap and 0 penetration failures. Clear lanes pass.
- Not done: yard and hall art are unchanged. Sofas, armchairs and the arcade machine were not remodelled. The earlier nine whole-area renders are stale.
- Status: unreviewed, no independent review, not accepted.

## Revision 4 (2026-10-05): cafeteria-only refinement pass, doors with baked signs
Per the owner's instruction to stop one-shotting every room, only the cafeteria (dining, serving/kitchen, lounge plus small game corner) was
refined this pass. Hall and yard art were not refined; their text now uses the baked sign pipeline but the layouts are unchanged from v3.
- Five inspection cameras (`CAF_01_ENTRY_NORTH`, `CAF_02_DINING`, `CAF_03_SERVING`, `CAF_04_LOUNGE`, `CAF_05_GAME_CORNER`) plus three door-check
  cameras (`CAF_X1_AIRLOCK_DOOR`, `CAF_X2_YARD_DOOR`, `CAF_X3_MEDICAL_DOOR`). Four inspect-and-fix rounds were run on them.
- Doors: real frames and leaves on every opening: spawn airlock (hazard-striped pressure leaves with porthole and wheel), yard door, medical
  door, kitchen staff door, hall opening (sliding panels parked hall-side, rail and sensor). Leaves are swung open against the jambs so the
  reactor-axis and door lanes stay clear (`lane_pass` true).
- Signs: all lettering and icons are baked into one atlas, `textures/sign_atlas.png`, painted by `fe_signs.py` (Pillow, build-time only). Every
  sign is a single plate mesh with UVs into the atlas, in the spawn-room style (dark plates, white lettering, icon, orange bar). There are
  no text objects or per-letter shapes anywhere in the cafeteria. Signs: door and exit signs, hanging zone signs, menu boards, directory board,
  allergen board, banners, recycling, game room rules, neon game room sign.
- More cafeteria detail: branded wall bands on all four walls, painted roof beams, food pans in the hot wells, patterned baked rugs, TV and
  poster art, directory board (the old blank totem screen), tray stacks, bread basket, cutlery bin, sanitiser stations, recycling bins, tray
  trolley, bean bags, stools, side tables, table lamps, detailed arcade basketball.
- Build needs Pillow: `blender-python -m pip install --target pylib pillow` (the build adds `pylib/` to its path; not committed).
- Numbers (validation.json): total 683,720 triangles (yard 327,180, cafeteria 239,582, hall 113,962, shared 2,996), within the 800k budget.
  Support contact: 154 interior and 130 yard objects, 0 gap and 0 penetration failures. Clear lanes: pass. Interfaces unchanged.
- Status: still unreviewed, no independent review, not accepted. The earlier Revision 3 numbers below are superseded.

## Revision 3 (2026-10-05): cafeteria restored, game room cut down, real textures, more props
The owner found v2 too sparse and too low in visual quality, and said the cafeteria had gone missing (v2 had shrunk the dining area to
four tables and let the game area take over the room). v3:
- Cafeteria restored as a real cafeteria: ten four-seat tables (east block, north-middle, beside the lane) and two booth banks, the serving
  counter and kitchen with hatch, ordering kiosk and queue stanchions, vending, drinks fridge, water cooler, microwave bench, coat rack,
  planter dividers, table settings (trays, mugs, bottles, napkin dispensers, salt and pepper, menu cards).
- Game room cut to a small north-west corner (about 7 x 6 m): foosball, arcade basketball and a dartboard. The air hockey table was dropped
  to make room. The **lounge stays on the left (west) side**, south of the west door and clear of the dining tables: 3-seat and 2-seat sofas, two armchairs, coffee table, bookcase, lamps, plants, a large rug and a TV on the slatted south wall.
- Visual quality: real PBR texture maps from the repo (CC0 sets in `sections/mine/assets/pbr`: Concrete046, rock_face_03, gravel_ground_01,
  Metal046B; plaster and worn-wood maps and the poster and TV artwork from the spawn room's module) at 1024 px in `textures/`, applied by
  box projection with colour tints; a glossier varied tile floor; plaster-textured ceilings; the spawn room's poster art in the frames.
  Final images are 1600 x 900 at 64 samples (v2 was 1280 x 720 at 40).
- More props: forklift, stripped car on blocks, gas cylinder racks, hand trucks, hose reels, traffic barriers, sign posts, more crates,
  pallets and drums in the yard; gas racks, hand trucks, a second wheelbarrow, toolbox and ladder in the hall; bookcases, wall shelves with
  plants, fridge, water cooler, microwave bench, coat rack, mop bucket and wet-floor sign in the cafeteria. To pay for them the
  vegetation, drums, fences and vending machines were slimmed.

## Revision 2 (2026-10-04, overnight): look matched to the spawn room (superseded where v3 differs)
The owner found v1 read as a PS2 horror game and its props low-effort. v2 replaces the look and the assets:
- Look: the spawn room's idiom. Dusty-lilac plaster over a navy dado with a white rail, terracotta tile with a blue border, white trim,
  rust-red and mustard accents, warm bright lighting from working fixtures, daylight outside with a blue sky and a warm sun. Wear is
  light (about two years of use): faint dust and scuffs near the floor, a few tilted or cracked slabs, wet patches. No dead lights,
  mould, stains, litter or horror dressing remain.
- Assets: every prop was rebuilt with rounded forms, turned legs, subdivided upholstery, real leaf geometry, wheels with hubs and lug
  nuts, corrugated container profiles, welded-mesh fences, rail with sleepers, fishplates and ballast. Source: `fe_kit.py` (geometry
  kit), `fe_assets_int.py`, `fe_assets_yard.py`, `fe_assets_site.py`, `fe_wallart.py`.
- Cafeteria: east dining area (four tables, booth) facing a kiosk / serving area (counter with hot wells and sneeze guard, kitchen
  behind a hatch, ordering kiosk, queue stanchions, vending); west living room (two sofas, armchair, coffee table, rug, TV, lamp,
  plants); north-west recreation corner (foosball, air hockey, arcade basketball, dartboard with oche); planter dividers; posters,
  bulletin boards, extinguishers, first-aid boxes, clocks and exit signs in the spawn room's style.
- Yard: blocky layered cliff with ledge planting and the R39 portal front, timbered tunnel mouth, rail curving from the portal to the
  refinery gate, tidy salvage yard (stacked containers, pickup, van, skips, steel stock, pipe stacks, bales, crates, pallets, drums,
  tyre stacks, tanks, generator), mesh fences, ragged but sound ground, trees and shrubs.
- Hall: mid-refit rather than collapsed: scaffold tower, plasterboard and cement stock, ladder, wheelbarrow, racking, jersey-barrier
  chicanes and sandbags, and one small cordoned ceiling collapse with rubble. Footprint unchanged; clear lanes kept.

## Numbers (from `validation.json`, final scene)
- Triangles (evaluated, instances and text counted): yard 336,796; cafeteria 196,342; hall 122,290; shared 2,996; **total 658,424**
  against the 800,000 budget.
- Support contact: 145 interior floor-supported props at 5 mm gap / 2 mm penetration: 0 failures. Yard, 130 props at 0.12 m because
  the yard floor is deliberately uneven: 0 failures. Heap, broken-floor, debris, hanging, stacked, table and wall-mounted items are
  exempt, not measured.
- Clear lanes (no prop above 0.25 m): reactor axis x 6.8 to 9.2 (cafeteria and hall), hall door line y -55.3 to -52.7, cafeteria west
  and east door lanes, mine lane y -71.3 to -68.7: no violations.

## Not run, not claimed
- No independent review and no score. No room validator from the repo's section tooling was run (this module has none yet).
- No Unity import, collider, LOD, lightmap, bake or runtime check. No performance measurement. No texture UVs: materials are
  procedural node materials.
- No physics or gameplay assumptions: furniture and junk are static scenery.
- The mine front is the reference mine's portal only; its tunnel interior, props and track are not used. The existing mine
  module was not edited.

## Known defects
- Cliff face is a smoothed block heightfield with a box-projected rock texture: believable at yard distance, soft up close.
- Vehicles, containers and tanks are stylised, not photoreal; interior props follow the spawn room's rounded stylisation.
- Behind the portal frame the tunnel mouth ends in a flat black void; there is no tunnel.
- The spawn airlock opening shows an empty bright sky because the spawn room is not part of this module.
- The cafeteria keeps wide open floor along the reactor axis and the two door lanes (they are the required clear lanes).
- Textures are 1024 px; walls and floors repeat visibly at a few metres. No UV unwrapping: materials use box projection.
- Concrete slabs read slightly blue under the sky light.
