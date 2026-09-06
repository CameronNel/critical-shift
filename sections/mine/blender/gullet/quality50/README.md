# Gullet: implemented fifty-camera quality pass

This directory contains executable Blender source, not an implementation prompt. It continues the preserved `../Gullet_MaterialReview.blend` checkpoint and produces `../Gullet_Quality50.blend` through the canonical `../build_mine.py` entrypoint. The initial checkpoint is intentionally retained for reproducibility.

## Open the result

Open `../Gullet_Quality50.blend` in Blender 5.2.1 LTS or a compatible newer version. Scene-used image textures are packed. Use Rendered shading or render a camera; Solid shading does not show the authored materials or lighting.

After reopening, run `../register_controls.py`, or run the embedded Blender text named `RUN_GULLET_CONTROLS.py`. This restores the Gullet sidebar without rebuilding or changing geometry. Script auto-execution is not required.

## Reproduce the scene

From `sections/mine/blender/gullet/`:

```bash
blender --background --factory-startup --python-exit-code 1 --python build_mine.py -- --output ./output/quality50
```

The source checkpoint and committed maps in `../../assets/pbr/quality50/` are required. The normal path is offline. The utility `quality50/download_weathering.py` restores the two selected CC0 packs when needed and verifies cached SHA-256 values.

To build and render the fifty declared camera/state pairs:

```bash
blender --background --factory-startup --python-exit-code 1 --python build_mine.py -- --output ./output/quality50 --render all
```

Use `--quality high` for higher-resolution renders, or `--render CAM_01,CAM_12,CAM_48` for selected views. The GUI entrypoint refuses to replace an unrelated open scene: open `Gullet_MaterialReview.blend` before executing it. Use a new output directory when preserving an earlier generated checkpoint.

Render an already-built scene without rebuilding:

```bash
blender --background Gullet_Quality50.blend --python-exit-code 1 --python quality50/render_quality.py -- --output ./output/review --width 1600 --samples 64
```

The renderer applies each camera's declared sector/gate state. Changing only the active camera manually does not change excavation state. The default saved scene is a mixed-state showcase; `--mode intact` in the canonical build saves all sectors sealed.

## Validate and inspect

```bash
blender --background Gullet_Quality50.blend --python-exit-code 1 --python quality50/check_quality.py -- --output ./output/cold_start_report.json
blender --background Gullet_Quality50.blend --python-exit-code 1 --python quality50/clearance_check.py -- --output ./output/route_gate_report.json
```

From this README, the review record is [../../../production/QUALITY50_REVIEW.md](../../../production/QUALITY50_REVIEW.md), the fifty PNGs are in [../../../production/renders/review/quality50/](../../../production/renders/review/quality50/), and machine-readable evidence belongs under `../../../production/checkpoints/quality50/`.

Camera names are exactly `CAM_01` through `CAM_50`. The HTML gallery and JPEG contact sheets index the original Cycles renders without replacing them. Automated checks are scoped tests, not a proof against every possible intersection or a substitute for Unity character-controller testing.

## Implemented changes

Two low wooden carts replace the metal hoppers. They have individually chipped planks, real grain textures, iron straps, bearings, brakes and flanged wheels. The rim is approximately 1.10 m above the floor, reduced from approximately 1.53 m. The body is approximately 1.67 m long; rail gauge remains 1.10 m.

Concrete has coarse aggregate, chips and dirt; iron and paint have pitting, corrosion and roughness variation; seven door/cabinet panels have physical surface dents. Ventilation fabric has wrinkles and a longitudinal seam. Local weathering includes rust bleed, mineral runoff, water-edge deposits and traffic wear.

Darker work-light pools, eight anchored web clusters, twenty discarded rotten boards and dirty sump edges establish an aged industrial atmosphere without removing navigation visibility. Additional physical task lamps make the newly exposed working pockets readable.

Each sector's 22 removable collapse fragments are settled using a 200-frame Blender rigid-body bake, then kept as separate stable meshes. Floor/rock seam holes, walkway geology incursions, the incomplete facility surround, regimented ore placement and obstructed review cameras were corrected. Rear gate lights are mounted to measured collar surfaces; rear reinforcement remains within the sliding envelope.

## Provenance and scope

The six earlier CC0 material sets remain in the source checkpoint. This revision adds ambientCG `Wood060` and `Metal026`, with source/license URLs and map hashes in `../../../assets/pbr/quality50/manifest.json`. No font files are bundled. No Three.js or VTK acceptance renderer is used.

The Blender environment and art-state controls are implemented. Unity still requires baked/recreated materials, cooked collision geometry, cart mass/capacity tuning for the smaller wooden body, gameplay/multiplayer integration, audio/VFX and target-hardware testing. Baked Blender rubble poses are not a claim that runtime physics is integrated.
