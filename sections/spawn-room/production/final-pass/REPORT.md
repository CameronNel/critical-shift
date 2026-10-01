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
- `../../blender/add_hero_suits.py` (idempotent) places one suit per locker `PPE_01..04` without the wearer (skin, head and face left out), facing the open front, pack against the back panel, hung by a strap from the rescue handle to a hook over the hanger rail. Suit scale is the player's (about 1.7 m including the hood antenna).
- It removes the personal-belongings dressing the suit replaces (jacket, wooden hangers, mid shelf and contents, floor work boots) and the earlier hand-modelled suit, helmet and cradle. The locker `contents` property is updated.
- Contacts: hooks rest on the hanger rail; `validate_contacts.py` **PASS 208/208** (224 before; the difference is the removed belongings, minus the added hooks and strip lights). `check_layout.py` still 6 PASS; a missing or renamed named object or collection is now reported `MISSING` in the JSON instead of aborting the run.
- `module_optimised.blend` regenerated: 759 objects, 762 draw calls, 31 materials, 352,462 triangles (linked suit, after the polish pass) (about 28,000 more than the suit-less room, 7,000 per suit: the cost of using the player's own mesh); `compare_signatures.py` before/after PASS.
- Renders with suits: `renders_with_suits/` (Spawn, LockerDoor, LockerReverse, Hero_A, 480p, 16 spp).
- **Lighting and suit fixes (owner request):** each locker has a baked strip light under its upper shelf (visible fixture, 40 W area, tagged `baked_plus_emissive_fixture` / `locker_power`, not dynamic; light budget unchanged at 4 dynamic, 2 shadow casters), set behind the hood so the visor does not mirror it. The neck stub is cut and capped with a dark inner collar. Hall lighting and the other rooms were **not** changed.
- **Floating fix:** each suit now stands on a low steel boot dock (plate, rubber pad, two legs) on the locker floor, measured to the sole underside and registered against the floor shelf, in addition to the strap and hook. Render: `renders_with_suits/locker1_boot_dock.png`.
- **Equip:** the suit asset carries `cs_equip_station` and `cs_hide_on_equip`; the toggle itself is runtime logic and is not built or tested. See `SUIT_EQUIP.md`.
- **Not re-scored.** The critic scores above predate the suits. Open items from the list above remain: material wear, lighting falloff, LockerReverse white blob, Walk_C bench uprights, plants and signage.

## Update: polish pass (owner request) and critic rescore
`../../blender/polish_spawn.py` (idempotent, run after `add_hero_suits.py`) applied, to the canonical module:
- **Bench posts:** `BRIEFING_backrest_upright.*` moved behind the backrest boards and ending under the top board, ends capped (they poked through as spikes in Walk_C).
- **Wear:** a scuff layer (object-space noise mask: darker grime and scuffs, rougher) added over the original graphs of `V_locker_steel` (lockers), `pressure_metal` (airlock door face), `CS_tile_floor`, `CS_hall_floor` and `rubber`; the original graph still drives the base colour.
- **Doorway colour spill:** two baked area lights (warm in the briefing room, cool in the locker room) beside the hall doors; the module now has 20 lights (14 original, 4 locker strips, 2 spill), still 4 dynamic and 2 shadow casters.
- **Door frames:** the portal frames use a lifted graphite (`portal_frame`) instead of pure-black `darksteel`.
- **Material_A:** reframed (26 mm, from the locker-room door side) to hold wall, floor, painted locker, rubber, paper and glass.
- **LockerReverse "white blob":** not geometry. A ray through it hits only the chamber glass and the wall behind; it is the reflection of a ceiling strip in the curved glass, so it was left.
- **Equip contract updated** with the owner's decision: the suit reappears once removed and can only be removed at its own locker (`cs_show_on_unequip`, `cs_unequip_only_at_station`; `SUIT_EQUIP.md`). Runtime logic is still not built.

Checks that ran: `validate_contacts.py` PASS 208/208 on the canonical module and on the regenerated `module_optimised.blend`; `check_layout.py` 6 PASS; `compare_signatures.py` canonical vs optimised PASS.

**Critic rescore** (two fresh-context critics, 11 renders in `renders_polish/`, 1280x720, 64 spp): **85 and 82 of 100. Still below 90, the room is NOT accepted.** Before the suits and polish the scores were 85 and 72.
Common remaining findings:
1. The suits (the owner's chosen player-character suit) read as a toy or plush mannequin to the critics: no fabric folds or seams. This is the owner's design; any change is an owner decision.
2. Hall lighting still reads even (two ceiling strips, little falloff); materials wear is subtle; locker doors are large flat slabs in the foreground of LockerDoor and LockerReverse.
3. Low-poly plants and the amount of signage (bulletin board, slogan board) read as filler or heavy.
4. Camera framing: LockerDoor hides one suit per side behind open doors; one critic called the Spawn black door-frame slab at the far left a geometry error (it is the black frame of the briefing door).
5. The LockerReverse chamber glass reflection reads as an artefact to both critics.
Reaching 90 needs owner-level decisions (suit style and fabric detail, plants, signage, door sizes) rather than more material tweaks.

## Update: the locker suits are linked to the hero suit (owner request)
The owner asked that the placed suits link to the hero suit and that the original hero suit is kept. So:
- `hero_suit.blend` (built by `../../blender/build_hero_suit.py`, LFS) is the single source: the collection `HERO_SUIT` is the player character's own hazmat suit exactly as `character_worker` + `character_suit` build it (default colours, A-pose rest), minus the wearer.
- `module.blend` **links** that collection (library `//hero_suit.blend`) as four collection instances `PPE_0n_suit_model`; nothing is copied. Edit and re-save `hero_suit.blend` and the four placed suits change on the next open of the module (verified: changing the suit's colour in a scratch copy of the library changed all four placed suits).
- The earlier per-locker copies and every look change made to them (per-player accent colours, fabric folds, weave and grime, repair patches) are removed: the placed suits are the original hero suit, identical in all four lockers. A separate dark collar object around the neck stub hides it behind the empty visor; the suit itself is unmodified.
- The delivery derivative has to be self-contained, so `optimise_spawn.py` and `signature.py` first turn the linked instances into local objects (`../optimise/realize_instances.py`) and drop the library; `module_optimised.blend` has no library. The canonical module keeps the link.
- Checks that ran: `validate_contacts.py` PASS 208/208 on the canonical module and on the derivative; `check_layout.py` 6 PASS; `compare_signatures.py` PASS; six-camera Cycles comparison re-rendered (see the optimiser README).
- Not done: the player character's own scene still builds its suit with the same code rather than linking `hero_suit.blend`; moving it to the library is the step that makes "edit the hero suit" a single edit for both.
