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
- `renders/`: the nine fixed-camera images that were opened and inspected.

## Frame and interfaces
Module-local frame: origin at the spawn airlock threshold, +Y into the building, +X east. Plan = local + (8, -80).
Seven `IF_PORTAL_*` empties with clear width, height and outward normal: spawn airlock 2.6 m, yard door 3.0 m, medical door 2.2 m,
cafeteria-to-hall opening 6.0 m, hall west door 2.4 m, hall east door 2.4 m, spine blast door 3.6 m. All sit at the planned
plan positions; none were moved.

## Revision 2 (2026-10-04, overnight): look matched to the spawn room
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
- Triangles (evaluated, instances and text counted): yard 433,632; cafeteria 158,952; hall 133,384; shared 2,996; **total 728,964**
  against the 800,000 budget.
- Support contact: 101 interior floor-supported props at 5 mm gap / 2 mm penetration: 0 failures. Yard, 113 props at 0.12 m because
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
- Cliff face is a smoothed block heightfield: believable at yard distance, noisy and smooth up close; the rock shader shows speckle.
- Vehicles, containers and tanks are stylised, not photoreal; interior props follow the spawn room's rounded stylisation.
- Behind the portal frame the tunnel mouth ends in a flat black void; there is no tunnel.
- The spawn airlock opening shows an empty bright sky because the spawn room is not part of this module.
- The cafeteria still has a large open floor between the 2.4 m lanes; furniture sits in three zones around it.
- Concrete slabs read slightly blue under the sky light.
- Only FE_03, FE_07, FE_02 and FE_06 were re-rendered after the last small fixes (floor drains, bale colours); the other five images
  are from the build just before that change and match it except for those two items.
