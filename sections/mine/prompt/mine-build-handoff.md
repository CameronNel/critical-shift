# Gullet Mine — Agent Build / Review Handoff

Before doing anything else, read [`../AGENT_READ_FIRST.md`](../AGENT_READ_FIRST.md), then `../../design/ART_DIRECTION.md`, `../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`, and [`../scenery/mine.md`](../scenery/mine.md).

## Immediate objective

Take the committed deterministic Gullet source through the missing **real Blender validation loop**. Do not replace it with a primitive blockout. Do not declare completion based on scene-tree complexity, object count, successful script execution or a single flattering render.

## Build

From `sections/mine/blender/gullet/`:

```bash
python tools/prepare_assets.py
blender --background --python build_mine.py -- --output ./output --quality high --render all
```

The builder targets newest stable Blender, authored around Blender 5.2 APIs with 4.2+ fallbacks. Prefer HIP on Cameron's RX 9070 XT when Blender exposes it.

## Review loop

1. Inspect all ten fixed-camera renders listed in `../production/CAMERAS.md`.
2. Score the scene using `../production/RUBRIC.md`.
3. Identify the worst visible defects, not the easiest defects.
4. Fix the deterministic source under `blender/gullet/source_parts/`; do not hand-patch only the generated `.blend`.
5. Rebuild and rerender the same cameras.
6. Compare like-for-like pixels.
7. Repeat for at least four full correction cycles after first visual completion.
8. Maintain `../production/TASK_STATE.md` with evidence, regressions and the exact successful commands.
9. Reopen the saved `.blend` in a new Blender process and run:

```bash
blender --background ./output/CriticalShift_Gullet.blend --python tools/cold_start_check.py -- --render entry,main_route
```

10. Only after Blender acceptance, export variants and proceed to Unity integration.

## Non-negotiable creative target

Grounded stylized semi-realism. Believable industrial mine construction, strong readable silhouettes, tactile material separation, authored wear, restrained clutter and constrained practical light. It must not look like a Three.js demo, a generic low-poly cave, toy geometry, glossy sci-fi, or AAA photorealism.

## Gameplay / layout constraints

Preserve the covered preparation bay, fictional charge pickup/instruction area, blast gate, 2.5% downhill adit, cart haulage with no elevator, three independent work sectors, progressive shallow/extended/deep openings, oversized-event collapse requiring rubble removal, and the wet pumping/sump work area.

The numerical cut indices in the scene are deliberately fictional game-state values with no physical units. Do not replace them with real-world explosive engineering data.
