# Fuel corridor overhaul

The editable deliverable is the existing
[`module.blend`](../facility-assembly/sources/fuel-corridor/module.blend), exported
through `MODULE_fuel-corridor` at its established metre-scale map placement.
Its original outer-wall bounds, floor footprints, 16 review cameras and 34
interface markers remain fixed. Visible architecture, portals, machinery,
furniture, practicals and props are rebuilt from the procedural source here.

Use Blender **5.2 LTS**. Open the updated corridor in the assembled authoring map
with the normal repository launcher:

```sh
blender --python open_map.py
```

The launcher hides the old fuel render cache and its lights, then instances the
verified live source. The canonical main map and immutable R17 preview stay
byte-exact; opening the main `.blend` directly still uses its historical cache.
The preview launcher continues to open the immutable whole-map preview.
Compatibility-only copies of the new materials retain the hidden fuel cache's
30 historical library names; live corridor meshes use the rebuilt materials.

For a headless proof from the actual assembled map:

```sh
blender -b --disable-autoexec --python-exit-code 1 \
  --python open_fuel_overhaul.py -- --render C03_HERO
```

Check the normal launcher, repeat-install idempotence, current native/build/cold
pair and the frozen main/preview/spawn hashes without saving any native scene:

```sh
blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
  --python sections/fuel-corridor/blender/validate_live_map.py
```

This writes `production/MAP_LAUNCHER_VALIDATION.json`; the actual map render
records its own source and image hashes in `production/MAIN_LINK_VALIDATION.json`.

Rebuild from the byte-guarded original module, then run the cold checks:

```sh
blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
  --python sections/fuel-corridor/blender/build_overhaul.py -- --stage full
blender -b sections/facility-assembly/sources/fuel-corridor/module.blend \
  --disable-autoexec --python-exit-code 1 \
  --python sections/fuel-corridor/blender/validate_overhaul.py
```

The build packs all used image/font resources. Asset provenance and font licensing
are in [`assets/PROVENANCE.md`](assets/PROVENANCE.md). The 20 construction ideas and
review bar are in [`scenery/OVERHAUL_BRIEF.md`](scenery/OVERHAUL_BRIEF.md).
Native checkpoints, hashes, render settings, numerical checks and independent
Luna reports are recorded under `production/`.

The selected F23ci module removes unmotivated ambient and map-helper fill from the corridor while keeping its real modeled fixtures and readable routes. It preserves the eerie, rundown atmosphere and ten modeled infrastructure detail families: sockets, retained lead, clipped conduit, gland/junction connections, motor bond, intercom, captive bleed cap, open recessed strainer, cloth hems and tied inspection tag. Local wear/fracture outlines and gauge scales are refined. See [all rendered areas and closeups](production/REVIEW_INDEX.md) and the [self-critique](production/SELF_CRITIQUE_DETAILS.md). Pessimistic Luna independently clears every category and area above 98 in the two stable final full cycles; [the rubric](production/RUBRIC.md) records actual grades.

The native light loop plays frames **1–240 at 24 fps**, with a closure key at
241, without drivers or auto-run. Watch the [10-second preview](production/renders/temporal/F23ci-entry-loop.mp4)
or inspect the [assembled-map render](production/renders/integration/F23ci_complete_main_C03_HERO.png).
Every-frame technical evaluation and encoded timing pass. Target-speed visual
playback could not be reviewed here; Unity/runtime behaviour is unverified.
Preview provenance and reproduction are in the [temporal report](production/TEMPORAL_VALIDATION.json).

Current acceptance is tracked in [`production/TASK_STATE.md`](production/TASK_STATE.md).
Development-gate approval does not accept the whole corridor. Final visual
acceptance requires every category and every area strictly above 98, at least
four complete review cycles, and two materially stable final cycles.
Closed exterior leaves, authoring-only gate state and sampled geometric
clearance do not certify Unity collision, controllers, adjacent-room passage or
runtime performance.
