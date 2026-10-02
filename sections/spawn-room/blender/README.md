# Spawn Room Blender Source

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Store the authoritative editable Blender source for the Spawn Room here.

Primary filename when created:

- spawnroom.blend

Keep Blender Python helpers, Geometry Nodes notes, or generated-source scripts here if they are specific to this room.

Do not store exported runtime meshes here; those belong in ../assets/.


## Build policy

Spawn Room source is headless-first.

The final section must be reproducible through Blender CLI/scripts from a fresh process. MCP may orchestrate and inspect, but the .blend must not depend on MCP-only scene state.

See ../../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md.


## Support-contact validator

This section includes `validate_contacts.py`.

Run it headlessly after any dressing pass:

```bash
blender -b spawnroom.blend --python validate_contacts.py
```

It writes `../production/contact_validation.json` and fails the Blender job when required props are floating, over-penetrating, incorrectly oriented, or not registered.

### Required collections

- `CS_SUPPORT_REQUIRED` — every prop that depends on a wall/floor/ceiling support
- `CS_WALL_DRESSING` — papers, portraits, signs, boards, wall art and similar mounted props
- `CS_FLOOR_DRESSING` — floor-supported dressing that should be audited
- `CS_CEILING_DRESSING` — ceiling-supported dressing that should be audited

Any object in one of the three dressing collections that is missing from `CS_SUPPORT_REQUIRED` is an automatic failure.

### Required object properties

Every object in `CS_SUPPORT_REQUIRED` must define:

- `cs_support_target` — exact Blender object name of the support mesh
- `cs_support_direction` — one of `LOCAL_+X`, `LOCAL_-X`, `LOCAL_+Y`, `LOCAL_-Y`, `LOCAL_+Z`, `LOCAL_-Z`, `WORLD_+X`, `WORLD_-X`, `WORLD_+Y`, `WORLD_-Y`, `WORLD_+Z`, `WORLD_-Z`

Optional overrides:

- `cs_support_max_gap_m` — default 0.005
- `cs_support_max_penetration_m` — default 0.002
- `cs_support_max_angle_deg` — default 12.0

For irregular objects, add child Empty objects with `cs_support_anchor = true`. The validator checks those anchor positions instead of relying on a bounding-box face.


## Modeling guardrails

The current art reset changes what counts as a finished asset.

Required:
- object-specific geometry;
- believable wall and door thickness;
- believable furniture proportions;
- PPE with fabric volume;
- visible support contact;
- localized bevels only where construction warrants them;
- actual gameplay-camera renders during every major pass.

Forbidden as final art:
- cube + uniform bevel + flat colour;
- display-toy suit bays;
- giant scanner booths built from primitive frames;
- floating wall panels;
- repeating generic sci-fi control boxes.

Before rebuilding the full room, model only the approved style-validation slice.


## Pre-build reference requirement

Before starting or regenerating Spawn Blender art:

1. read `../art/SPAWN_REFERENCE_BIBLE.md`;
2. read `../art/SPAWN_ASSET_REFERENCE_MATRIX.md`;
3. inspect the numbered reference plates;
4. complete `../production/REFERENCE_REVIEW.md`.

Do not build from the scenery text alone. The reference library exists specifically to prevent the generic bevelled-box / flat-plastic failure mode.


## Cozy-modern restyle (user-directed palette + performance pass)

> **Status of `module.blend`:** the committed module is the output of this pipeline (regenerated headlessly and validated with `validate_contacts.py`). To reproduce it, run the three commands below against the original module (the version before this work) with Blender 5.2 `bpy` + Pillow.

The working module `../../facility-assembly/sources/spawn-room/module.blend` was restyled from the earlier teal/cream palette to a highly stylized, modern but cozy look. `accepted.blend` is untouched and remains the frozen baseline that `build_master.py` hashes.

**This deliberately departs from the written palette** in `art/SPAWN_MATERIAL_REFERENCE.md` and plate `20_spawn_colour_palette.svg` (warm plaster upper wall, painted industrial green dado). Those documents have not been rewritten and now disagree with the module; treat the direction below as the current owner decision until they are updated or the change is reverted.

| Area | Direction |
|---|---|
| Hall | dusty plum-grey upper wall, ink-navy dado, graphite floor, machine-grey airlock hatch |
| Briefing | dusty clay upper wall, navy dado, honey oak floor, navy/amber rug, wall TV, pendant lamps |
| Locker room | denim upper wall, ink dado, procedural slate tile, coral lockers, linear warm fixtures |
| Lighting | one ceiling fixture type per room (hall + locker: linear; briefing: pendants), warm 2700-3000K-style colour in briefing and locker |

### Pipeline (headless, Blender 5.2 `bpy`, Pillow for the TV still)

Run from the unmodified source, in order:

```bash
python restyle_cozy_modern.py -- <original module.blend> <stage1.blend>
python refine_spawn_assets.py -- <stage1.blend> <stage2.blend>
python add_cozy_trinkets.py  -- <stage2.blend> <module.blend>
```

- `restyle_cozy_modern.py` recolours through each material's "Reference palette balance" node (rugs and other graphs without one use a luminance-transfer path), flattens texture contrast toward a painted read, and sets neutral machine-grey metals.
- `refine_spawn_assets.py` is the structural pass: procedural tile floor, rebuilt jackets/towels, real wall TV + soundbar (screen still generated with Pillow and packed in the .blend), clean ceiling fixtures (emitter at the diffuser plane, no shadow wedge), removal of the fake fill/bounce lights, replacement of lumpy boots/bags/hamper/clock, pegboard holes as a shader, and baked Decimate passes.
- `add_cozy_trinkets.py` adds `COZY_*` props by raycast onto real supports, in keep-out-aware positions, registered for `validate_contacts.py`.
- `cozy_geo.py` (lathe / tube / pillow / ribbon kit) and `cozy_props.py` (recipes) are shared by both.

### Decisions worth reviewing

- **Plants are low-poly and back**: the originals (about eight, roughly 100k triangles, 135 leaf objects each) were replaced by cheap `f_ficus` / `f_snake` / `r_pothos` recipes (330-900 triangles each). Placed: briefing corner ficus + sideboard pothos; hall ficus, snake and shelf pothos; locker ficus, snake and two shelf pothos. **This is more than the spec's 0-2 (section 14)**; the owner asked for plants. Trim the placements in `add_cozy_trinkets.py` if the spec limit should win.
- **AI-generated images removed**: `commissioning_crew.png` and `human_contribution.png` (the crew photo and supervisor portrait) are replaced by generated flat poster art (`replace_ai_images`). The caption text objects under them are unchanged and may now mismatch the art.
- **Hall floor** is a single plane with a clay-tile shader and a whole-tile navy border along the walls (`rebuild_hall_floor`); the old 5.7k-triangle floor mesh is gone.
- **Briefing bench seats are kept clear** and the seating zone, door path and locker route are keep-out zones for trinkets.
- **Suits are still missing.** The four suit bays have shelves, boots and hangers but no hero hazmat suits, which the spec requires. Not part of this pass.

### Budget

Scene total went from about 1,331,000 to about 250,000 triangles (tile floor 449k -> 2, jackets 170k -> 4k, plants ~100k -> ~38k, wall skins ~130k flattened, boots/bags/clock ~110k replaced). The remaining cost is mostly suit-bay hardware (about 15k per bay) and the integrity pod. Measured on the final file: 249,708 triangles, 1,220 mesh objects, 188 materials, 14 lights. The object and material counts are still high for draw calls and are unmeasured on target hardware.

Last validation: `validate_contacts.py` reported PASS with no failures. Not run: Unity export, in-engine frame time on a 3050, formal rubric scoring.

## Crew character kit (concept stage)

`character_kit.py` builds a chunky, big-headed, mitten-handed worker from cheap primitives (about 4k triangles assembled, well under a 5k budget). `render_character_sheet.py` renders the turnaround, a four-player crew and an option sheet headlessly; `character_options.json` is the machine-readable option list for a future customisation UI.

**Locked for every player:** body shape, head shape, proportions, art style.
**Choosable per player:** skin (7), outfit colour (8), glove colour (5), eyes (6), mouth (7), eyewear (7), hat (8) and hat colour (8), torso wear (5), pack (4), accessory (3). Every part is its own object under one root empty, with socket empties for head, hat, back and hands.

This **deliberately overrides** the "believable adult proportions, not chibi/mascot" rule in `design/ART_DIRECTION.md` section 13, by owner decision, for characters only. That document has not been updated. PEAK and R.E.P.O. are style references only: the designs here are original and nothing is copied.

Not done: rigging, animation, UVs/texture baking, any Unity export, or in-engine cost measurement.

### Scout character (from an owner-supplied concept image)

`character_scout.py` builds a taller, goofier take on the owner's concept. **The default is a nude, featureless base body** (a single blended mannequin-style skin surface: overlapping primitives are voxel-remeshed, Laplacian-smoothed and decimated into one mesh, so there are no ball joints or steps; no clothes, no anatomical detail, unisex shape; hands are oven-mitten style, with all fingers fused into one mitten and a distinct thumb, and feet are bean-shaped with a distinct big toe and the little toes fused; both are part of the same blended surface; primitives fed to the remesh must be closed solids; about 5.3k triangles with the head, slightly over the 5k target) with the neutral face: two round matching eyes, no eyebrows, a plain black-line smile, head straight. Everything else is opt-in: `clothes=True` adds a plain unisex tee and straight-leg jeans with shoes, `accessories=True` adds glasses and a hat, and `face="goofy"` restores the buck-toothed grin with mismatched eyes and brows. Parts are separate objects (body, jeans/shoes, tee, head, face, glasses, hat) under one root, with the head on a neck pivot. `render_scout.py` renders the turnaround. The concept image itself is **not** in the repo. It was produced by an image generator, and its originality has not been checked. Not done: outline shader, rig, poses, UVs, engine export, and porting the modular option lists to this body.

### Crew worker (the proposed player character)

`character_worker.py` shapes the Scout base into a character built for this game, chosen by design reasoning rather than copied from anything: a wide egg torso, short thick legs, a big round head with almost no neck, big oven-mitten hands and chunky feet, about 1.5 m tall so it fits the facility's rooms. The intent is a strong silhouette at distance for four players sharing a room, and a simple solid volume for the hazmat suit, gloves and boots to layer on. The body is one blended surface (overlapping closed primitives, voxel remesh, smooth, decimate); the head and neutral face reuse the Scout's parts on a scaled neck pivot, so faces, hats and accessories stay swappable. Refined pass: limbs follow smooth curved centre-lines with a soft calf, deltoid and defined wrist and ankle; the body surface is rebuilt with QuadriFlow (clean, evenly flowing quads with no decimation facets); the head and eyes are higher resolution. About 8.5k triangles, well above the 5k target; a lower-detail LOD is still to be made. `render_worker.py` renders the turnaround, a head close-up, a hand close-up and a Scout-versus-worker size comparison. The Scout is kept unchanged as a separate preset.

Not done: outline shader, rig, poses, UVs, suit/clothes layers for this body, engine export, and in-engine cost measurement.

## Crew worker face layers (2D decals)

The worker's eyes and mouth are flat transparent PNG decals on thin curved patches that follow the head
(`character_face.py`, textures in `character_faces/`). A custom eye or mouth is just another PNG: drop it in and call
`character_face.set_face_texture(obj, path)`, or pass `eyes=` / `mouth=` to `build_worker`. Sizes and the layout
contract are in the module docstring; the built-in library (`python character_face.py`) has eyes `round/dot/happy/
sleepy/wide` and mouths `smile/grin/o/flat/smirk`. `face="3d"` keeps the older modelled eyes. The decals are two
layers (eyes, mouth), about 560 triangles in total, and map onto a cutout/transparent material with one texture
slot per layer in Unity. Not yet tested in a Unity build.

## Crew worker body regions

`character_regions.py` cuts the worker body into nine skin regions (`TORSO`, `ARM_L/R`, `HAND_L/R`, `LEG_L/R`,
`FOOT_L/R`) with straight edge loops at the hips, ankles, wrists and shoulders; the head is its own object. Outfits
hide the regions they cover with `set_hidden(root, [...])` (render + viewport) so no skin pokes through a suit and
those triangles are not drawn. Shading matches the uncut body until a region is hidden. `render_regions.py` renders
a seam check and a hidden-regions test. The cuts add about 500 triangles (6,788 total with the face decals). Known
limits: the arm cut is a vertical plane at |x| = 0.24 m, so the outer flank of the chest belongs to the arm region;
not yet skinned to a skeleton or merged per outfit for Unity.

## Crew worker hazmat suit (outfit test)

**2026-10-01 owner-reference revision:** `build_hazmat` now defaults to the yellow
HZ-01 reference style. Open `crew_hazmat_reference.blend` for the wearable review
scene, or the linked `hero_suit.blend` library for the empty locker suit. See
[the source, commands and evidence](../production/hero-suit-reference/README.md).
The original design and triangle table below are retained for `style="legacy"`;
they do not describe the new hero authoring model or establish its runtime budget.

`character_suit.py` builds a cute hazmat suit as pieces that each list the skin regions they cover (`cs_covers`);
`equip(root)` hides those regions. Pieces: coverall (soft folds, waist gather, hem bunching), gloves, boots, hood with a
big open face and a clear glass visor so the face decals show through, plus belt, zipper, straps, pack and tank, hose,
rescue handle, dosimeter and ID patch. `build_hazmat(root, colors={...})` swaps the suit, gloves, boots, accent, pack
and visor tint (any `#RRGGBB`). `render_suit.py` renders the turnaround, close-ups and a colour-variant sheet.
Design test only: about 12.8k triangles of suit on top of the 6.8k skin (roughly 19.6k drawn with the skin regions
hidden), so it needs a lower-detail pass, and it is not yet skinned to a rig or tested in Unity. The wrist and ankle
hems and the shoulder straps are approximations that need a look under animation.

### Detail levels (`lod` on `build_worker` and `build_hazmat`)

Counted per mesh (faces split into triangles), suit on and skin regions hidden:

| lod | Use | Bare worker | Suit pieces | Drawn with suit |
|---|---|---|---|---|
| 0 | near / hero (default) | 6,788 | 12,826 | 14,666 |
| 1 | medium, keeps the smooth look | 6,106 | 10,500 | 12,340 |
| 2 | far only | 3,958 | 6,406 | 7,182 |

lod 2 (body remesh 3,300, coarse head/hood, fewer segments, no bevels on small parts) looks faceted up close, so it is
for distance only. lod 1 is nearly indistinguishable from lod 0 but saves only about 16 percent. Not yet measured on a
3050 or in Unity, and no LOD switching distances are set.

## Crew worker rig and animation clips

`character_rig.py` builds a Unity Humanoid-compatible skeleton (Root, Hips, Spine, Chest, Neck, Head, shoulders, arms,
hands, legs, feet; Unity naming so the Avatar auto-maps; A-pose rest; no Toes bone because the feet are toeless) plus
extra bones `Belly` (jiggle), `Pack` (backpack lag) and `Tool` (carries a hand tool rigidly). The worker faces +Y, so
its own left side, and the `Left*` bones, are at -X (`SIDES`); earlier revisions had the sides swapped, which put the
"right-hand" tool in the anatomical left hand and would have mirrored the Humanoid Avatar. Skin weights are a pure
function of position (bone heat on the welded body for torso and arms, same-side distance weights for the legs, the
glutes and crotch riding the pelvis), so region seams and outfit pieces deform together.

The suit body is one fused mesh: the legs touch from the knee to the crotch and each inner arm touches the flank below
the armpit. `_separate_limbs` cuts those creases open along a smoothed limb classification and closes each side with its
own wall (a strip of triangles between the front and back cut lines), and each side is then weighted to its own limb
only (the flank gets torso weights computed as if the arm were not there). Only faces within the sleeve's own radius
count as arm; the web that joined arm and flank stays on the flank, and what is left of it is tucked back, so neither a
claw on the raised arm nor a bulge on the flank remains. Fabric under the rigid hood never follows the arm. The two boot
shells are kept to their own foot the same way. Kit on the suit: pieces lying flat on the fabric follow it vertex by
vertex with long edges subdivided; bands round the legs and small raised items move as one piece; long hard parts
(belt, tank) are rigid to one bone; everything behind the back rides `Pack`. Head, hood, visor and face decals
are rigid to `Head` (tagged `cs_head_rigid`, hidden in the first-person view).

Fitting the HZ-01 reference suit (`style="reference"`, now the default): its pieces are narrowed in x (body 0.90,
gloves 0.91, boots at worker scale), so `skin_worker` widens each piece back to worker scale, weights it there and
narrows it again, keeping the sleeves on the arms. On top of the steps above:
- The trouser hems are pulled inside the boot shafts before the cut.
- The waist and belt rings are hugged onto the torso, so they do not stand off it as wings.
- The two trouser legs overlap at the midline in this suit, so faces near the midline are sorted to a leg by which
  way they face, not by where they sit.
- Each leg's cut is closed with a rounded cap following the leg's own radius, and the inner flaps are tucked in.
- Each boot shell is assigned to a foot by which side its piece sits on.
- The boot soles are rigid to `Foot`, and the composer lifts each foot just enough that no sole point goes under the
  floor at any pitch.

Legs are two-bone IK to planned foot paths (planted stance foot sliding back at treadmill speed, heel strike, toe roll,
swing), with the knees aimed slightly outward; arms are two-bone IK to where the mitten closes, the forearm following
the upper arm through a pure elbow hinge so the sleeve never twists at the elbow.

Stance (`STANCE`, `TOE_OUT`): the ankles stand 0.17 m either side of the centre line, 0.34 m apart where they were
0.22 m before, and each foot turns out 5 degrees. This keeps the HZ-01 trouser legs and boots apart in every standing
and stepping clip. The gait tracks are 0.135 m (walk and plain run) and 0.14 m (\o/ run) either side of the centre.
Hanging mittens sit 0.40 m out with the elbow turned out and a little forward (`POLE_HANG`), and the arms swing out
from the shoulder (30 to 38 degrees), so they clear the wider hips, the belt pouches and the back of the armpit.

### Clips

All clips are in place at 24 fps. Loops have their last frame equal to the first; one-shots (`act["cs_loop"]` false)
start and end on the pose the game blends from and to (standing, or the crate carry). Speeds are the floor speed of the
planted foot, so the game can match playback to the character's velocity.

Movement is deliberate:
- Strides are 25 % longer than the first pass (`restride`), and each step takes about 10 % longer, so floor speeds
  rose by 11 to 17 %.
- The hips sit lower so the legs reach.
- The arms swing wider.
- One-shots wind up before they act, hold a beat at the contact, and settle into the end pose. They are 15 to 25 %
  longer than before.

In `character_rig.py` (`ACTIONS`):
- `RUN` (18, one stride, 1.57 m/s): cartoon run, arms up beside the head like \o/, mittens waving.
- `HOLD_SHOVEL`, `HOLD_PICKAXE` (48): the tool in the right hand at chest height in front of the right shoulder, blade
  or pick head raised forward so it shows in the lower right of the first-person view (`TOOL_HOLD`); left arm hanging.
- `RUN_SHOVEL`, `RUN_PICKAXE` (20, 1.33 m/s): a plain run holding the tool the same way (`TOOL_RUN`), left arm pumping.

In `character_clips.py` (`CLIPS`, registered into `ACTIONS` on import), built as keyed poses (pelvis, spine, chest and
head angles, hips offset, mitten targets on the chest or fixed in the world or held on a prop, elbow poles, ankle
targets with pitch and yaw), interpolated with a monotone cubic so nothing overshoots and equal keys hold:
- Standing: `IDLE` (48 loop, breathing and a slow weight shift, keyed on the same `STAND` pose every one-shot starts
  and ends on; it replaces the rig's procedural idle).
- Locomotion:
  - `WALK_F` (26, 0.73 m/s) and `WALK_B` (26, the walk reversed so the toe lands first).
  - `WALK_L`/`WALK_R` (18, side-steps that never cross, 0.44 m/s).
  - `TURN_L`/`TURN_R` (22, stepping on the spot, 51 deg/s).
  - `SPRINT` (14, one stride, the \o/ run longer and quicker, 2.75 m/s).
  - `JUMP` (17: rise, deep crouch, spring; ends in the fall pose).
  - `FALL` (20 loop, arms up paddling).
  - `LAND` (19: a deep absorb held a beat, then back to standing).
- Carrying (preview crate 0.34 x 0.30 x 0.28 m, held near the rear edge of its sides so the cuffs stay out of it,
  carried 0.50 m out, its top edge in the first-person view):
  - `PICKUP` (36: look down, stoop so the arms come down in front of the knees, grip, brace, stand into the carry) and
    `PLACE` (36, the pickup reversed).
  - `CARRY_IDLE` (48), `CARRY_WALK` (26, 0.58 m/s), `CARRY_RUN` (20, 1.08 m/s).
  - `DROP` (22, a small heave first).
  - `THROW_UNDER` (33, a deep stooped wind-up held a beat, the crate swung out past the belly) and `THROW_OVER` (31, a
    chest heave with a long step, thrust from far enough out to clear the visor: the arms are too short to lift a
    crate over the hood).
  - `PUSH_IDLE` (32), `PUSH_WALK` (26, 0.69 m/s), `PULL_WALK` (26, walking backwards, 0.58 m/s); the cart is held at
    its outer rear corners.
  - `DRAG_BODY` (30, crouched, walking backwards with a body by its shoulder straps, 0.39 m/s).
- Interactions at the worker's chest height (its shoulders are at 1.06 m and its chin at 1.15 m):
  - `PRESS_BUTTON` (24: look, draw the hand up, press, hold).
  - `PULL_LEVER` (31: look up, grip, drop the weight into an 80 degree pull, hold).
  - `TURN_VALVE` (32 loop, hand over hand, 60 degrees per loop) and `HOLD_VALVE` (32 loop, straining).
  - `OPEN` (31, sit back, then push a door open stepping into it; the door is 30 degrees open before the body steps
    in, so the visor stays clear of it).
  - `INSERT` (31, line a cartridge up, then push it home).
  - `CONNECT_PORT` (36, plugging the service cable into a worker in the OCRU).
  - `POINT` (26, gather, point, hold).
  - `RADIO` (48 loop, radio held to the hood).
- Hits and recovery:
  - `STAGGER_F`/`B`/`L`/`R` (26, a bigger lurch and a longer catch step each way).
  - `GETUP_FRONT` (48, from face down: push up, all fours, kneel, stand).
  - `GETUP_BACK` (50, from the back: up onto the hands behind, feet in, push off with the arms swinging forward, rock
    onto the feet, stand; a hand on the floor beside an upright seated body is out of the arms' 0.45 m reach).
  - Lying bodies lie along +Y from the root and stand up on it.
- Suit and OCRU:
  - `SUIT_UP` (64, pull the suit up the outside of the legs and round the hip pockets, settle it, zip, seat the hood).
  - `LOCKER_EXIT` (28, two steps out of a locker 0.45 m behind the root).
  - `REANIM_IDLE` (48 loop, slumped in the upright OCRU cabinet), `REANIM_JOLT` (18, a shock) and `REANIM_EXIT` (28,
    wake and stumble out).
- Tool work: `SHOVEL_DIG` (40 loop, both hands, right on the D-handle: stab, lever, lift, toss to the right).

Props (crate, panels, lever, valve wheel, door, cartridge, radio, a body stand-in, cabinets) are preview-only stand-ins
for the renders (`character_clips.PROPS`); they are not exported. `SHOVEL_DIG` drives the real shovel on the `Tool`
bone.

### Arm clearance

The suit is puffy: the sleeves are about 0.13 m in radius and the coat about 0.26 m. An arm posed by its target alone
sinks into the coat, the thighs or the hood.

`_compose` therefore works in three passes:
1. It keys the torso.
2. It solves and keys the legs.
3. It solves the arms, then evaluates the body as it really deforms in that frame and moves each arm out of it.

The body here is the coat, trousers, boots, hood and the closed kit pieces, leaving out everything that follows an arm.
Moving an arm out of it (`_solve_clear`) works like this:
- The arm turns about the line from its shoulder to its mitten. The elbow swings round while the hand stays on its
  target.
- A hand that holds nothing (hanging, swinging or \o/) may also swing out from the shoulder.

Contact up to 8 mm is allowed as soft fabric touching. Upper-arm points that already touch the body in the bind pose
(the armpit fold, the hood's rim over the shoulder) and points within 0.20 m of the shoulder are left to the skinning.

Corrections are averaged over five frames and limited to 4 degrees of change per frame. In a one-shot they fade to
nothing over its first and last five frames, so the clip starts and ends exactly on the pose it blends with.

### Transitions

Clips are made to blend into each other:
- Every one-shot starts and ends on `STAND` (or the carry pose), and the keyed `IDLE` is built on `STAND`. The
  difference between them is the idle's breathing: at most 9 degrees on any bone, against 19 before.
- One-shot keys ease in and out.
- Loops close with no seam (the fastest loops change speed across it by under 8 degrees per frame, as they do
  anywhere else).
- Every gait loops over exactly one stride with the right foot striking at its first frame, so a blend between gaits,
  or a speed-synced blend tree, keeps the feet in step.

`chain.py` (in the review scratch area, not committed) renders a chain of clips with 6-frame cross-fades in the NLA as
an engine would blend them.

### Bones

No bones were added. The audit traced the arm clipping to arm paths and to the skinning at the shoulder, not to a
missing joint:
- Twist bones would not move a sleeve out of the coat.
- An `UpperChest` would not keep the elbow band off the hip.
- Toes would add nothing: the boots are stiff and toeless.

The skeleton stays the same 23 bones.

### First-person view

The game is first-person with the body visible. `render_rig.py` renders an `eye` view: a camera at the eyes (0, 0.20,
1.40 at rest) following the `Head` bone, 60 degree vertical field of view at 16:9, with the head-rigid meshes hidden.
The worker's eyes are 0.34 m above its shoulders and its arms are short, so in a 60 degree view the mittens show only
when they reach forward at chest height or above (pointing, buttons, levers, the valve wheel, throws); a hand at the hip
is 66 degrees below the eye line. The tool holds therefore keep the hand at chest height and raise the tool's working
end into the lower right of the view (measured: 56 % of the shovel's vertices and 73 % of the pickaxe's are on screen
when standing, 41 to 73 % while running), and the carried crate's top edge sits at the bottom of the view.

### Tools, export and rendering

`character_tools.py` builds the shovel and pickaxe (origin at the right grip, shaft along +Z). `add_tools` skins them
100% to the `Tool` bone and hides them; `show_tool` shows one. `export_fbx` exports the rigged worker and one action per
file, baked over that action's own frames, with the FBX take (Unity clip) named after the action and only the tool that
action holds. `render_rig.py` renders posed frames: `SUIT=1`, `ACTIONS=...`, `VIEWS=` (close, close_side, three_q,
front, side, side_r, back, wide, shoulders, sh_side, sh_back, legs, legs_b, flank_r, flank_l, feet, knees,
crotch_f, crotch_b, armpit_b, eye), `FRAMES=0,4,...` for a contact sheet, `VIDEO=1` for every frame plus an mp4 (loops
twice, one-shots once with a hold), `RES=WxH`, `SAMPLES=N`, `HIDE=<object>`, `EXPORT=<dir>` for the FBX clips.

Checked (headless bpy 5.0.1, Cycles CPU renders reviewed as contact sheets from a close three-quarter camera and the
first-person eye, plus numeric checks): every clip builds and loops close; no hand target is out of reach by more than 1
cm except in `PICKUP`/`PLACE` and the get-ups (below); no tool vertex enters the suit; the eye never ends up inside a
prop; apart from the mittens gripping things, no suit vertex is inside a prop except brief contacts (a few forearm or
knee vertices on the crate while it is lifted or carried); legs stay within reach (at most 99.8 % extended).

Suit clipping, checked on the evaluated HZ-01 suit at every frame by BVH face overlap:
- left against right trouser leg below 0.6 m;
- left against right boot;
- mittens against the coat and legs;
- the lowest boot vertex against the floor.

42 of the 49 clips have no overlaps, and their boots stay within 1 mm of the floor. They include `IDLE`, every walk,
turn and run (the tool runs included) and every carry, push, pull and drag walk.

The other seven have contacts:
- `PICKUP` / `PLACE`: the inner thighs touch in the stooped squat, and a forearm brushes a knee for a few frames on
  the way down.
- `SUIT_UP`: the hands grip the suit.
- `SHOVEL_DIG`: the left mitten touches the belly at the stab.
- `LOCKER_EXIT`: 6 faces.
- `GETUP_FRONT` / `GETUP_BACK`: see the known limits below.

Arm audit: the penetration depth of sleeves, cuffs and mittens into the torso, legs, boots and hood, measured at every
frame.
- After the arm clearance:
  - the \o/ forearms in the hood are down from 50 to 26 mm;
  - the tool runs' pumping arm is down from 42 to 16 mm;
  - the reaching forearms in the chest are down from 39–46 to 23–39 mm;
  - `PULL_WALK` is down from 41 to 30 mm, `SHOVEL_DIG` from 50 to 28 mm and the idle from 27 to 20 mm.
- The wider hanging pose keeps the elbow bands out of the belt pouches. It also presses the back of the right armpit
  up to 38 mm into the coat when the chest twists (turns, side-steps, staggers). That contact lies between the arm and
  the back, hidden under the sleeve in the renders.

Known limits: not imported into Unity (Humanoid Avatar mapping, clip import and the first-person camera are untested in
the engine). Clips are in place with no root motion, so planted feet slide back on the treadmill unless playback speed
is matched. The bare (unsuited) body was not reviewed. In the get-ups the mittens rest on the thighs and knees, and the
knees touch in `GETUP_BACK` (overlapping faces that read as contact in the renders); a hand trails its target by up to 4
cm while pushing up, and a lying or kneeling boot dips up to 5 mm under the floor. The raised shovel blade sits beside
the right of the visor in a front view, so that it shows in the first-person view. Face decals are rigid, so expressions
do not animate. In `PICKUP`/`PLACE` the hands trail their path for a few frames as the body bends (up to 11 cm short of
it). Props are stand-ins, so real handle, button and slot positions must be matched to the clips (or the clips
re-keyed). The FBX clips and renders are not committed.

Status: kept on the `claude/character-rig` branch, not merged. Open polish items:
- Clear the get-up hand and knee contacts.
- A corrective for the shoulder skinning: the fold behind the armpit and the inner sleeve near the shoulder, which
  the arm clearance deliberately leaves to the skinning.
- Re-key the reaches that still bring a forearm into the chest (`CONNECT_PORT`, `INSERT`, `TURN_VALVE`; 23 to 39 mm).
- Mittens higher in the \o/ run (they reach about the top of the hood).
- Round the flank wall that shows under a raised arm, and ease the armpit stretch (up to about 5.5x at the fold).
- Root motion or foot locking, so the planted foot does not slide on the treadmill.
- Import the FBX clips into Unity and check the Humanoid Avatar mapping, clip loop settings and the first-person camera.
- Review the bare (unsuited) body in these animations.
