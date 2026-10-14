# Cafeteria revamp

The full editable scene is [front_end_area_cafeteria_revamp.blend](../front_end_area_cafeteria_revamp.blend). It contains the cafeteria, hall and yard in the original module frame. Open with **Blender 5.2.2 LTS or newer**. The default render camera presents the games corner; the fixed inspection cameras remain available. Images and fonts are packed into the native files.

The cafeteria has a crafted games corner, tailored lounge furniture, a slatted media wall, detailed coffee and food service, an angled touchscreen kiosk, varied dining settings, original graphic artwork, ceiling services and manufactured door hardware. Original doorway interfaces and circulation lanes are retained. Geometry and object transforms in the hall, yard and shared shell are checked against the original. The cafeteria face of the north wall receives the new paint material.

The final R6 independent authoring review passes at **91.90/100**, with all 13 views passing and no material regression across R5/R6. [Final review](critics/review_r6.md). The final numerical report checks **799,874 module triangles**, six clear furniture lanes, seven unchanged interfaces and **850 support anchors** covering all 431 classified supported cafeteria objects. The missing-registration negative check is also verified. This is an authored-Blender result; owner/map/runtime acceptance is separate.

## Render gallery

[Presentation sheet](renders/final/presentation.jpg) · [Games](renders/final/R8_GAMES_HERO.png) · [Lounge](renders/final/R8_LOUNGE_HERO.png) · [Dining](renders/final/R8_DINING_HERO.png)

[Foosball detail](renders/final/R8_FOOSBALL_DETAIL.png) · [Dartboard detail](renders/final/R8_DARTBOARD_DETAIL.png) · [Basketball detail](renders/final/R8_BASKETBALL_DETAIL.png) · [Coffee station](renders/final/R8_COFFEE_DETAIL.png)

The portable download is generated with `python package_delivery.py --output /workspace/deliverables`. It includes the complete scene, all three standalone native assets, the presentation sheet, licensing and brief evidence. Archive integrity is checked with CRC and per-file SHA-256 hashes. Rebuild sources and the complete historical review trail remain in this repository.

## Standalone games and reimport

Each game is authored in its own empty Blender process and saved before the room imports its native ASSET collection. These are editable models with component separation and materials, rather than flattened presentation meshes.

| Native asset | Room instances | Evaluated triangles per asset | Components | Details |
|---|---:|---:|---:|---|
| [Foosball](assets/foosball.blend) | 2 | 32,830 | 26 | Eight independent rods, 22 molded players, goals, ball returns, bearings, bumpers, grips, bead counters and threaded feet |
| [Dartboard](assets/dartboard.blend) | 1 | 15,574 | 111 | Correct scoring sectors and numerals, red inner bull in a closed green annulus, metal spider, three darts, hinged cabinet, chalk scores and task lamp |
| [Basketball machine](assets/basketball.blend) | 2 | 14,592 | 18 | Ramp, wire containment, seamed balls, backboard, rim, diamond-knotted net, sensor, physical seven-segment displays and service hardware |

The dart bull is 1.73 m above the floor. The oche is 2.37 m from the scoring face. Asset roots retain floor-centre or bull/mounting-back origins; foosball rods have independent pivot parents. `reimport_report.json` records all five imports. Bounds must match within 10 micrometres, with exactly preserved component counts and evaluated triangles.

## Rebuild

Run from any directory using a Python environment with Pillow and the DejaVu Sans font family at its standard Linux font path. The authoring files themselves have no dependency on local fonts or unpacked texture folders after saving.

```bash
python /path/to/cafeteria-revamp/rebuild.py \
  --blender /path/to/blender-5.2.2-linux-x64/blender \
  --render-review
```

The entrypoint regenerates original graphics, independently builds and renders each game, opens the hydrated original front-end scene, reimports and places the games, applies the room pass, saves the additive candidate, and validates it in another fresh process. `--render-review` also renders all nine fixed views and four function/detail views. Failed numerical gates stop the command. Logs are written under `logs/`.

`--skip-asset-renders` rebuilds the native assets without refreshing their studio previews. Support coverage includes inherited cafeteria props as well as new assemblies: `support_coverage.py` registers actual mesh anchors, repairs small inherited mounting gaps, and connects suspended fixtures to the roof. The validator rejects independently supported props without a registration. `verify_support_gate.py` demonstrates this by removing the game-rules sign's registration in memory; the model is never saved during that negative check.

Hydrate only the necessary original scene if it is an LFS pointer:

```bash
git lfs pull --include='sections/facility-assembly/sources/front-end-area/front_end_area.blend'
```

Manual render entrypoint:

```bash
blender --background --disable-autoexec front_end_area_cafeteria_revamp.blend \
  --python-exit-code 1 --python render_views.py -- \
  cafeteria-revamp/renders/custom R8_GAMES_HERO 32 1920 1080 -0.5
```

## Evidence and scope

See [production state](TASK_STATE.md), [rubric](RUBRIC.md), [cameras](CAMERAS.md) and [delivery checks](CHECKLIST.md). Historical checkpoints and same-camera comparisons retain the review trail. `validation_final.json` is the cold-start numerical report; `renders/final/` contains presentation renders.

Presentation rendering uses `render_presentation.py`, which reuses the original renderer at 1600 × 900, up to 48 Cycles samples, adaptive threshold 0.035 and eight minimum samples. `renders/final/render_settings.json` records the actual settings. Native game studio previews are 1200 × 1000 with 32 samples. All rendering uses live geometry/materials/lights; no lighting is baked into the source textures. Embedded DejaVu font licensing is retained in `FONT_LICENSE.txt`.

This is a Blender authoring delivery. The original source scene and combined map remain separate from this additive candidate. Doors are presented closed with editable hinge roots; no gameplay or animation binding is claimed. No Unity import, colliders, LODs or FPS measurement were performed. The high-detail foosball and dartboard exceed the historical 15k hero-asset limit; they are authored masters for the user's requested detail level, while the whole-module 800k authoring budget is enforced.

Its remaining triangle reserve is 126; the separate per-view material-family limit has not been measured. The reviewer identifies coffee-machine clarity and more selective furniture-use variation as further polish opportunities.
