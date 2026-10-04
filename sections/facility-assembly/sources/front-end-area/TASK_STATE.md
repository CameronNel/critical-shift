# Front-end area (cafeteria, hall, yard): production state

**Status: first build, unreviewed. Not independently reviewed, not accepted, not promoted anywhere.** Built 2026-10-04 from the
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
- `renders/`: the nine fixed-camera images that were opened and inspected.

## Frame and interfaces
Module-local frame: origin at the spawn airlock threshold, +Y into the building, +X east. Plan = local + (8, -80).
Seven `IF_PORTAL_*` empties with clear width, height and outward normal: spawn airlock 2.6 m, yard door 3.0 m, medical door 2.2 m,
cafeteria-to-hall opening 6.0 m, hall west door 2.4 m, hall east door 2.4 m, spine blast door 3.6 m. All sit at the planned
plan positions; none were moved.

## What was built (against the owner's review notes)
- Cafeteria: dining area smaller and on the east side with a kiosk / serving area; small living room on the west (couches,
  armchair, coffee table, TV showing static); recreation corner (foosball, air hockey, arcade basketball, dartboard).
- Grime: dirt, streak and mould layer in all shared materials; floor cracks, stains, puddles, wall streaks, fallen ceiling tiles,
  litter, dead plants, dead lights, overturned furniture. No gore.
- Yard: the rail starts at the centre of the mine entrance (y = -70). Only the open front portal of the R39 mine is reused (cut from
  `module_r39_aaa.blend`; the rest of that mine is not copied). Ragged ground (sunk, tilted, cracked, missing slabs, potholes,
  rubble). Heavy scrapyard junk: containers, vehicle hulks, skips, crushed cubes, pipes, tyre stacks, scrap heaps, crates.
- Hall: two cave-ins with rubble, fallen slabs and beams, jersey-barrier chicanes, sandbags, crate walls, toppled shelving,
  hanging cables. Free width is cut by obstacles; the hall footprint itself is unchanged (36 x 12 m).

## Numbers (from `validation.json`, final scene)
- Triangles (evaluated, instances and text counted): yard 299,876; cafeteria 58,608; hall 72,192; shared 4,316; **total 434,992**
  against the 800,000 budget. About 365k is unspent; detail was added only where renders showed a need.
- Support contact: interior floors, 108 floor-supported props checked at 5 mm gap / 2 mm penetration: 0 failures.
  Yard, 134 props checked at 0.12 m because the yard floor is deliberately ragged: 0 failures. Exempt from the floor test
  (not measured): heap, broken-floor, debris, hanging, stacked, table and wall-mounted items.
- Clear lanes (no prop above 0.25 m): reactor axis x 6.8 to 9.2 (cafeteria and hall), hall door line y -55.3 to -52.7,
  cafeteria west and east door lanes, mine lane y -71.3 to -68.7: no violations.
- Bounds: three zones stay inside their declared footprints except rail and tunnel mouth (west of the cliff line, intended),
  shared wall pieces and rubble, which was clipped back inside the hall.

## Commands that ran
- Build (above): succeeded, 434,992 triangles.
- `blender -b front_end_area.blend -P validate_front_end.py -- validation.json`: succeeded, results above.
- `render_views.py` for all nine cameras at 1280 x 720, 40 samples, Cycles CPU with OIDN: succeeded.

## Not run, not claimed
- No independent review and no score. No room validator from the repo's section tooling was run (this module has none yet).
- No Unity import, collider, LOD, lightmap, bake or runtime check. No performance measurement. No texture UVs: materials are
  procedural node materials.
- No physics or gameplay assumptions: furniture and junk are static scenery.
- The mine front is the reference mine's portal only; its tunnel interior, props and track are not used. The existing mine
  module was not edited.

## Known defects
- Hard-edged flat rectangle of the mountain mass is visible behind the cliff in FE_02. Cliff face is a heightfield without strata detail.
- Behind the portal frame the tunnel mouth ends in a flat grey wall instead of a black void (FE_09); not yet diagnosed.
- Spawn airlock opening shows an empty bright sky because the spawn room is not part of this module.
- Sandbags read brick-red, the kitchen hatch light reads white, and the TV static is hard to see from the lane cameras.
- Scrap heaps are made of box-like scrap prototypes and read as piles of boxes up close. Foliage is blobby.
- The cafeteria middle is still open floor between the 2.4 m lanes; only chairs, tiles and litter fill it.
