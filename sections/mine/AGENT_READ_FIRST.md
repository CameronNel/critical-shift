# Gullet Mine — AGENT READ FIRST

**This file is the entrypoint for any agent touching the mine. Read it before editing, generating, importing, rendering, or integrating anything in this section.**

## Authority order

1. `design/GAME_SPEC.md` — mine gameplay and systems requirements.
2. `design/ART_DIRECTION.md` — authoritative visual target.
3. `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md` — mandatory build/review loop.
4. `sections/mine/scenery/mine.md` — section-specific layout and interaction decisions.
5. This handoff and the source under `sections/mine/blender/gullet/`.

Critical Shift is grounded stylized semi-realism: believable industrial construction, medium-complexity object-specific geometry, tactile material separation, controlled colour blocking, restrained wear, localized practical lighting, and readable silhouettes. Do not regress into primitive-heavy Three.js-looking geometry, glossy sci-fi, toy low-poly, or AAA photorealism.

## User-approved mine decisions

- The mine is the **Gullet** uranium mine section.
- It enters the mountain on a shallow **2.5% descending grade** (about 1.43°). There is **no mine elevator/lift**.
- Players can push/ride the mine cart back toward the facility handoff.
- A covered preparation/staging bay sits before the mine portal and connects to the rest of the facility.
- The staging bay includes: dynamite/fictional charge pickup, cart staging, mining/blast instructions, tools, workbench/service hardware, blast controls, and a substantial blast door.
- Blast instructions use **fictional game indices/tokens only**, never real explosive engineering quantities or real-world charge formulas.
- The mine has multiple mineable sectors and **progressive excavation states**, not one flat mineable wall.
- Small blast -> shallow pocket.
- Medium blast -> larger/deeper accessible area.
- Large controlled blast -> full/deep excavation with additional shoulder/branch space.
- Oversized blast -> the deep excavation exists but is blocked by a collapse. Players must remove rubble before mining/access continues.
- Unlocks are monotonic: a later smaller blast must not magically close previously opened geometry.
- Re-blasting must not erase uncleared collapse rubble.
- Dry, wet and deep sectors are independent.
- Wet mining has a real drainage/pump/sump working area.
- Cart rails, supports, ventilation, cables, drainage and mining infrastructure must look functionally plausible and deliberately authored.

## Source layout

The primary Blender entrypoint is:

`sections/mine/blender/gullet/build_mine.py`

That file is a small launcher which reconstructs the exact generated builder source from `source_parts/` and executes it. The split exists only because this repo upload path is text-only; do **not** redesign the builder merely because its source is stored in parts.

Before first Blender execution, generate the deterministic local geology/textures:

```bash
cd sections/mine/blender/gullet
python tools/prepare_assets.py
```

`prepare_assets.py` requires Python with `numpy`, `Pillow`, and `scikit-image`. It creates only section-local `assets/` and `textures/` output. Do not download random art packs as a shortcut.

Then build with the newest stable Blender available. The authored API target is Blender 5.2.x, with compatibility fallbacks for 4.2+:

```bash
blender --background --python build_mine.py -- --output ./output --render entry
blender --background --python build_mine.py -- --quality high --render all
```

After a saved `.blend` exists, reopen it in a **fresh Blender process** and run the cold-start check. The repo protocol requires fixed-camera pixel review and correction cycles; a successful Python exit is not visual approval.

## Hardware profile supplied by Cameron

- GPU: AMD Radeon RX 9070 XT
- CPU: AMD Ryzen 7 5800X
- RAM: 32 GB DDR4

Prefer HIP rendering when Blender enumerates the GPU; fall back to CPU if the driver/backend is unavailable. Do not assume performance numbers without measuring them.

## What the generated scene contains

- covered preparation/charge/cart bay;
- facility transition/handoff;
- detailed independent blast-door leaves and operator controls;
- shallow sloped haulage route into the mountain;
- continuous original field-sculpted geological shell, not visible rock spheres;
- profiled rails, sleepers/chairs/fasteners and detailed carts;
- heavy structural arches and mining support hardware;
- ventilation, cable routing, water services and practical lighting;
- pump installation and recessed sump;
- dry, wet and deep mining sectors;
- sealed, shallow, extended, deep and collapsed state alternatives per sector;
- 22 individually identified removable rubble pieces per collapsed sector;
- collision/interface metadata for later Unity integration;
- ten fixed review cameras.

## Runtime boundary

The Blender package authors geometry, hierarchy, state variants, metadata, materials, cameras and review evidence. It does **not** magically implement Unity gameplay. Unity still needs authoritative pickup/placement, detonation, rigid-body cart behaviour, rubble physics, collision cooking, navigation, multiplayer/network authority, VFX, audio and damage/state logic.

## Validation status

The non-Blender geometry/state audits from the generation session passed. The original delivery environment did **not** have Blender installed and therefore could not truthfully claim Blender render approval. The next agent must execute the Blender adapter, render the fixed cameras, inspect the actual pixels, repair defects in source, rerender, and perform cold-start validation before calling this section production-ready.

Do not rename diagnostic geometry previews as Blender renders. Do not hand-edit only the generated `.blend` while leaving the deterministic source broken.
