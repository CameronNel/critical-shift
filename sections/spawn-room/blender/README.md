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

> **Status of `module.blend`:** this commit ships the *generator scripts only*. The restyled `module.blend` was not committed because the authoring environment could not reach the Git LFS host. `module.blend` here is still the original; run the pipeline below against it to reproduce the restyled module (Blender 5.2 `bpy` + Pillow), then commit the result through normal LFS.

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

- **Plants cut to two** (locker corner ficus, briefing tea-corner pothos). The spec (section 14) allows 0-2 across the section; the module had about eight (roughly 100k triangles).
- **Briefing bench seats are kept clear** and the seating zone, door path and locker route are keep-out zones for trinkets.
- **Suits are still missing.** The four suit bays have shelves, boots and hangers but no hero hazmat suits, which the spec requires. Not part of this pass.

### Budget

Scene total went from about 1,331,000 to about 284,000 triangles (tile floor 449k -> 2, jackets 170k -> 4k, plants ~100k -> ~38k, wall skins ~130k flattened, boots/bags/clock ~110k replaced). The remaining cost is mostly suit-bay hardware (about 15k per bay) and the integrity pod. Measured on the final file: 284,036 triangles, 1,369 mesh objects, 188 materials, 15 lights. The object and material counts are still high for draw calls and are unmeasured on target hardware.

Last validation: `validate_contacts.py` reported PASS with no failures. Not run: Unity export, in-engine frame time on a 3050, formal rubric scoring.
