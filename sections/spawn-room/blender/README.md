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
