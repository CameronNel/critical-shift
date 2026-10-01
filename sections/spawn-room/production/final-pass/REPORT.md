# Spawn room final pass

Scope: the canonical `sections/facility-assembly/sources/spawn-room/module.blend`. **Edited in this PR by the hero-suit pass** (see Update below); the first-pass renders and critic scores describe the module before that edit. The optimised derivative is a runtime copy of the same scene (identical triangles; see `../optimise/README.md`).

**Owner decisions applied:** the Geiger/radiation check is a player-HUD element and is deliberately not built in the room (spec section 12 is superseded for this room).

## Evidence that ran
| Check | Result |
|---|---|
| `check_layout.py` (named objects, BVH route clearance) | 6 PASS, Geiger N/A by owner decision. `layout_check.json` |
| `validate_contacts.py` (canonical module) | PASS, 224/224. `contact_validation_rerun.json` |
| Fixed cameras, Cycles 1280x720, 64 spp | 11 renders in `renders/` (VALIDATE_Spawn, HallForward, LockerDoor, LockerReverse, BriefingDoor, Material_A, ExitReverse, Walk_A/B/C, Hero_A) |
| Two independent fresh-context critics scoring against `RUBRIC.md` | 85/100 and 72/100. **Neither clears the 90 overall bar or the category floors.** |

Not run: RUBRIC cycles 3+ (the rubric asks for at least 4 review cycles and a cold start), any Unity or in-engine check, and any user playtest. **The room is not accepted.**

## Critic findings (both critics, merged)
1. **No hero hazmat suits in the module.** The four `PPE_0x` stations are personal lockers ("BELONG_*": jacket, folded fabric, thermos, hangers). Spec sections 8.3-8.4 call for four visible hero suits, one per bay. One critic scored this as a critical failure. Needs an owner decision: model four suits, or the suit is the worn rig and the bays stay as lockers.
2. **Materials:** locker paint, airlock door, floor tile and rubber mats read uniformly clean satin, with little wear, edge scuffing or roughness variation. The airlock door is a flat grey slab with a pasted-on dial.
3. **Lighting:** the hall and locker room are evenly lit by tubes, with little falloff, bounce or contact shadow. Doorway voids are pure black. Hero_A is dark, red-saturated and muddy.
4. **Camera briefs:** Hero_A shows an empty locker interior rather than a hero object. Material_A shows only the airlock door and does not contain the paper/rubber/glass set its brief lists.
5. **LockerReverse:** a white curved blob inside the chamber glass at upper left (likely a reflected or hung item; not yet traced) and heavy glass smear.
6. **Walk_C:** bench back uprights poke through the top slat; pouf and rug edge look clipped.
7. **Dressing:** low-poly leaf plants read as filler; the bulletin board and signage are heavy in ExitReverse and Spawn.

## Recommended next steps (owner-approved before any look change)
- Decide on the suits (item 1).
- A single material and lighting polish pass on the canonical module (wear on locker/airlock, bounce light, doorway fill), then regenerate `module_optimised.blend` and compare renders.
- Reframe Hero_A and Material_A to match `CAMERAS.md`; trace the white blob and fix the bench uprights.

## Update: hero suits added (owner request)
The owner confirmed four lockers, one per player, and asked for the suits to be modelled and hung in them.
- `../../blender/add_hero_suits.py` (idempotent) adds, per locker `PPE_01..04`: one hanging hazmat suit on the hanger rail (broad folds, collar and hood roll, dosimeter, closure flap, belt, knee pads, gloves, boots, back pack with filters and rescue handle, hanger and hook), a wall-bolted helmet cradle with a helmet, and a per-player colour (blue, green, magenta, cream).
- It removes the personal-belongings dressing the suit replaces: jacket, wooden hangers, mid shelf and what sat on it, floor work boots. The locker `contents` property is updated.
- Contacts: hooks rest on the hanger rail, cradles bolt to the side panel, helmets rest on the cradle pad; `validate_contacts.py` **PASS 208/208** (224 before; the difference is the removed belongings). `check_layout.py` still 6 PASS.
- `module_optimised.blend` regenerated: 744 objects, 747 draw calls, 32 materials (+2 one-off: `SUIT_fabric`, `SUIT_visor`), 327,590 triangles (+4,868, all suits); `compare_signatures.py` before/after PASS.
- Renders with suits: `renders_with_suits/` (Spawn, LockerDoor, LockerReverse, Hero_A). Hero_A now frames a suit and the chamber as its brief asks.
- **Not re-scored.** The critic scores above predate the suits. Open items from the list above that remain: materials wear, lighting falloff, LockerReverse white blob, Walk_C bench uprights, plants and signage. The suits are a first modelling pass (stylised tubes and boxes); the visor is faceted and the knee pads are boxy, so they are likely to be marked down on silhouette quality.
