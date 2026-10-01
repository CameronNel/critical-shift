# Spawn room final pass

Scope: the canonical `sections/facility-assembly/sources/spawn-room/module.blend`. **Edited in this PR by the hero-suit pass** (see Update below); the first-pass renders and critic scores describe the module before that edit. The optimised derivative is a runtime copy of the same scene (identical triangles; see `../optimise/README.md`).

**Owner decisions applied:** the Geiger/radiation check is a player-HUD element and is deliberately not built in the room (spec section 12 is superseded for this room).

## Evidence that ran
| Check | Result |
|---|---|
| `check_layout.py` (named objects, BVH route clearance) | 6 PASS, Geiger N/A by owner decision. `layout_check.json` |
| `validate_contacts.py` (canonical module, post-suit) | PASS, 208/208 (224/224 before the suit pass, which removed belongings and added hooks, docks and strip lights). `contact_validation_rerun.json` |
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
The owner confirmed four lockers, one per player. A first hand-modelled suit was rejected and deleted; the suit now hung is the crew worker's own hazmat suit, built by the same code the player character wears (`character_worker.build_worker` + `character_suit.build_hazmat` + `equip`, A-pose rest, the version on `main` and unchanged on `claude/character-rig`, which only adds the rig).
- `../../blender/add_hero_suits.py` (idempotent) builds one suit per locker `PPE_01..04` without the wearer (skin, head and face removed), facing the open front, pack against the back panel, hung by a strap from the rescue handle to a hook over the hanger rail. Per-player accent colour: blue, green, magenta, cream. Suit scale is the player's (about 1.7 m including the hood antenna).
- It removes the personal-belongings dressing the suit replaces (jacket, wooden hangers, mid shelf and contents, floor work boots) and the earlier hand-modelled suit, helmet and cradle. The locker `contents` property is updated.
- Contacts: hooks rest on the hanger rail; `validate_contacts.py` **PASS 208/208** (224 before; the difference is the removed belongings, minus the added hooks and strip lights). `check_layout.py` still 6 PASS; a missing or renamed named object or collection is now reported `MISSING` in the JSON instead of aborting the run.
- `module_optimised.blend` regenerated: 759 objects, 762 draw calls, 31 materials, 351,478 triangles (about 28,000 more than the suit-less room, 7,000 per suit: the cost of using the player's own mesh); `compare_signatures.py` before/after PASS.
- Renders with suits: `renders_with_suits/` (Spawn, LockerDoor, LockerReverse, Hero_A, 480p, 16 spp).
- **Lighting and suit fixes (owner request):** each locker has a baked strip light under its upper shelf (visible fixture, 40 W area, tagged `baked_plus_emissive_fixture` / `locker_power`, not dynamic; light budget unchanged at 4 dynamic, 2 shadow casters), set behind the hood so the visor does not mirror it. The neck stub is cut and capped with a dark inner collar. Hall lighting and the other rooms were **not** changed.
- **Floating fix:** each suit now stands on a low steel boot dock (plate, rubber pad, two legs) on the locker floor, measured to the sole underside and registered against the floor shelf, in addition to the strap and hook. Render: `renders_with_suits/locker1_boot_dock.png`.
- **Equip:** the suit asset carries `cs_equip_station` and `cs_hide_on_equip`; the toggle itself is runtime logic and is not built or tested. See `SUIT_EQUIP.md`.
- **Not re-scored.** The critic scores above predate the suits. Open items from the list above remain: material wear, lighting falloff, LockerReverse white blob, Walk_C bench uprights, plants and signage.
