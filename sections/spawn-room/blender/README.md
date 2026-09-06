# Spawn Room Blender Source

## Current Valorant reference iteration

The latest editable output is **`spawnroom_valorant_walk.blend`**. Work is paused at the user's request on 7 September 2026. The saved file contains pass-12 geometry plus a newer MCP material palette; the newer palette has not been rendered or scored. Resume from this saved file: the full builder currently reproduces pass 12 and would omit the final palette revision. Resume details and hashes: `../production/valorant-reference/PAUSED_20260907.md`.

The scene adds matte timber, small porcelain locker tiles, matching low-sheen metal lockers, a modern staff door, plants and detailed workplace props. The independent 90-per-category art review remains unmet; older delivery scores do not approve this revision. Status and recovery notes: `../production/VALORANT_REVISION_20260906.md`. Original corner captures, browser references, rendered passes and Luna reviews: `../production/valorant-reference/`.

## Current inhabited-room revision — 6 September 2026

Open **`spawnroom_inhabited_walk.blend`**. The four displayed suits have been removed. Their bays are personal lockers with hangers, shoes, folded clothing and belongings. Briefing now has staggered worn timber flooring, a faded woven rug and textured wooden benches. Six wall sockets, a whiteboard, clock, cleaning station, bags, towel/hamper, supply shelf and pod service details dress the rooms while preserving the open entrances and clear central routes.

F3 → **Walk Navigation**; WASD/mouse to move, Shift for speed, Esc to exit. Startup uses Material Preview with scene lights/world and the corrected filtered shadows. All texture maps are packed; no startup script execution is required.

```powershell
blender --background --factory-startup sections/spawn-room/blender/spawnroom_revised_walk.blend --python-exit-code 1 --python sections/spawn-room/blender/inhabit_spawn.py -- --review inhabited-rebuild
blender --background --factory-startup sections/spawn-room/blender/spawnroom_inhabited_walk.blend --python-exit-code 1 --python sections/spawn-room/blender/inhabit_spawn.py -- --validate-only --review inhabited-cold --cameras VALIDATE_Spawn,VALIDATE_HallForward,VALIDATE_LockerDoor,VALIDATE_LockerReverse,VALIDATE_BriefingDoor,VALIDATE_Material_A,VALIDATE_ExitReverse,VALIDATE_Walk_A,VALIDATE_Walk_B,VALIDATE_Walk_C,VALIDATE_Hero_A,USER_Floor,USER_BriefingFrame,USER_LockerEntry,DETAIL_LockerLife,DETAIL_BriefingFloor,DETAIL_HallLife,DETAIL_LockerSupplies
```

Direction and review history: `../production/INHABITED_REVISION_20260906.md`. Verification and unchanged render evidence: `../production/renders/final/inhabited/`. The previous corrected source remains preserved; this revision writes a separate output. Ambient sound, engine collisions and optimized exports remain integration work.

## Previous user corrections — 6 September 2026

Open **`spawnroom_revised_walk.blend`**. It is the editable EEVEE scene with the user-requested open room entrances, no observation windows or radiation meter, a 2.56m metal airlock, a large slim TV, two two-person briefing benches, forward PPE stations, changing benches and a rear-centered clear-glass metal pod. F3 → Walk Navigation; WASD/mouse, Shift for speed, Esc to exit. Materials and scene lighting are enabled at startup.

`revise_spawn.py` applies the latest direction to the tactile base. The former display housing, both personnel leaves and all their hardware are removed. Entrance wall ends are rebuilt behind the new reveals. The repeating floor/wall stripes were isolated to shadow maps; the correction retains surface relief and enables filtered jittered shadows in both viewport and final renders. The pod uses blended thin glazing to avoid dither speckling and preserve a clear interior.

```powershell
blender --background --factory-startup sections/spawn-room/blender/spawnroom_tactile_walk.blend --python-exit-code 1 --python sections/spawn-room/blender/revise_spawn.py -- --review user-rebuild
blender --background --factory-startup sections/spawn-room/blender/spawnroom_revised_walk.blend --python-exit-code 1 --python sections/spawn-room/blender/revise_spawn.py -- --validate-only --review user-cold --cameras VALIDATE_Spawn,VALIDATE_HallForward,VALIDATE_LockerDoor,VALIDATE_LockerReverse,VALIDATE_BriefingDoor,VALIDATE_Material_A,VALIDATE_ExitReverse,VALIDATE_Walk_A,VALIDATE_Walk_B,VALIDATE_Walk_C,VALIDATE_Hero_A,USER_Floor,USER_BriefingFrame,USER_LockerEntry
```

To rebuild the base from an empty scene, run the historical tactile commands below first, then apply this revision. For the delivered run, the actual desktop session was preserved as `../production/checkpoints/before_user_corrections_20260906.blend` and used as input. A second checkpoint preserves the desktop session immediately before reopening the corrected file. The older `.blend` sources remain unchanged.

Evidence: `../production/renders/final/user-corrections/`. All 19 objective checks and 67 registered support contacts pass, including 170 ray tests through both room entrances, floor face/normal checks, and six pod states. Fourteen final renders were repeated in a fresh process; the greatest image mean difference is 0.000344 on the 0–255 scale. Native `.blend` textures are packed. This is an editable art scene; game interaction and collision integration remain separate.

## Historical tactile revision — 6 September 2026

Open **`spawnroom_tactile_walk.blend`** for walking with materials and scene lighting. It uses EEVEE, four baked room light volumes and a bounded floor-bounce approximation. Material Preview uses the scene lights/world and starts at the spawn eye position. Hover over the viewport, press F3, choose **Walk Navigation**; WASD moves, mouse looks, Shift speeds up, Esc exits. Initial material compilation can take a minute. No automatic script execution is required.

**`spawnroom_tactile.blend`** is the editable Cycles authoring source with conservative Solid startup. Both are derived from an empty factory scene. This pass adds four CC0 material sets, separate surface finishes, localized sheet deflection and stronger practical-light falloff. The earlier locally edited `spawnroom_worn.blend` is preserved.

Reproduce from the repository root:

```powershell
blender --background --factory-startup --python-exit-code 1 --python sections/spawn-room/blender/build_grounded.py -- --scope room --tactile --output spawnroom_tactile.blend --review-id tactile-source --samples 32 --no-render
blender --background sections/spawn-room/blender/spawnroom_tactile.blend --python-exit-code 1 --python sections/spawn-room/blender/cold_start_grounded.py -- --review-id tactile-verify --device HIP
blender --background sections/spawn-room/blender/spawnroom_tactile.blend --python-exit-code 1 --python sections/spawn-room/blender/prepare_lit_walk.py -- --review-id tactile-walk
blender --background sections/spawn-room/blender/spawnroom_tactile_walk.blend --python-exit-code 1 --python sections/spawn-room/blender/cold_start_grounded.py -- --review-id tactile-walk-verify
```

Omit `--device HIP` to use CPU. The tested GPU is the Radeon RX 9070 XT, Blender 5.2.0 LTS. Review output is 1440×900, AgX Medium High Contrast, exposure +0.3, Cycles 32 samples/denoised; walking renders use EEVEE 64 samples with 16 viewport samples. All eleven fixed cameras remain unchanged. Material Preview is intentional: Blender restored the saved Rendered-mode viewport to Solid during the reopen check.

Current evidence: `../production/renders/final/tactile/`, with `walk/` holding EEVEE images. New online sources and licenses: `../assets/textures/TACTILE_SOURCES.md`. Rendering-skill research and rejected passes: `../production/critics/tactile-lighting-review.md`. The EEVEE copy approximates indirect light; it is not pixel-identical to Cycles or an optimized game-engine export.

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Store the authoritative editable Blender source for the Spawn Room here.

## Grounded rebuild implementation

`spawnroom.blend` is generated from an empty factory scene by `build_grounded.py`, `grounded_kit.py` and `grounded_room.py`. Existing blends are never read as build input. Reference base: `origin/main` commit `8603063`. Tested with Blender 5.2.0 LTS, Cycles CPU, eight threads. The build requires no MCP connection, addon, downloaded model or texture service.

From the repository root (replace `blender` with its installed executable path):

```powershell
blender -b -t 8 --python-exit-code 1 --python sections/spawn-room/blender/build_grounded.py -- --scope room --review-id rebuild --samples 20
blender -b -t 8 --python-exit-code 1 sections/spawn-room/blender/spawnroom.blend --python sections/spawn-room/blender/cold_start_grounded.py -- --review-id cold-start --states
```

The `--python-exit-code 1` flag is required: Blender otherwise can return process code zero after a Python exception. The build retains failed renders for diagnosis and raises if objective or support checks fail. Do not judge PASS from Blender's exit status alone without that flag.

For the small kit slice, use `--scope slice`. `--stage 1` produces the primary-form grey review. `--no-render` builds and audits without rendering; `--cameras VALIDATE_Spawn,VALIDATE_LockerDoor` selects a diagnostic subset. Full review omits `--cameras` and renders all eleven fixed views at 1440 × 900, AgX Medium High Contrast, exposure +0.3.

`validate_contacts.py` is the existing repository support audit. `validate_grounded.py` adds asset counts, metric clearances, actual furniture-foot bounds, packed dependencies, camera heights and machine-state checks. It is a source audit, not runtime collision simulation. `compare_reviews.py` uses Python 3 with Pillow to compare camera manifests and decoded pixels; it does not assign art scores.

Major source collections separate the hall, briefing room, locker room, PPE stations, integrity machine, gameplay hooks and review cameras. Overlapping `CS_*` collections hold support audit registrations. Interactive leaves and the scan carriage remain separate objects with editable origins. Procedural materials are reusable. Both original portrait PNGs are packed and retain project-relative paths; provenance is in `../assets/portraits/SOURCES.md`.

The six integrity preview keys are 1 ready, 31 occupied, 61 testing, 91 pass, 121 inspect, 151 fail. Readouts, indicator emission and inward-hinged doors change; the scanning carriage moves. Audio locations are named empties for the engine handoff. The pocket personnel door has a separate leaf and saved closed position; operations, rear-entry and briefing doors have hinge origins. Gameplay interaction, networking, collision meshes, character skinning/LODs, sound playback and engine lighting remain engine integration work.

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
blender -b --python-exit-code 1 spawnroom.blend --python validate_contacts.py
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

## Worn surface revision (2026-09-06)

The user's revised direction is old, dirty and mildly damaged, but maintained. `worn_surfaces.py` adds CC0 concrete/plaster maps with restrained colour remapping, metric projection and controlled relief. Cloth, rubber, wood, paint and glass have separate wear responses. Floors have actual recessed joints and occasional chipped corners; wall plaster has subtle mesh waviness and localized recessed loss. Selected equipment edges have small paint chips. The pass is deterministic and is included automatically in stage 3 fresh builds. Downloads, license URLs and checksums are in `../assets/textures/`; all six maps are packed, so opening the blend needs no network connection.

The lightweight SOLID startup remains enabled. Use the saved render gallery to see the complete materials without changing the viewport shading.

For this delivered wear pass, open **spawnroom_worn.blend**. It is a byte-identical verified copy of the rebuilt canonical `spawnroom.blend`, kept under a distinct name after an older open room-06 scene was resaved over the canonical path during validation. The unexpected resave was preserved in ignored production logs before recovery. Reopen the new file to load the new materials; a previously opened scene retains its old in-memory data.

Example from repository root:

```bash
blender -b --python-exit-code 1 --python sections/spawn-room/blender/build_grounded.py -- --scope room --review-id worn-room-03 --samples 24
blender -b sections/spawn-room/blender/spawnroom.blend --python-exit-code 1 --python sections/spawn-room/blender/cold_start_grounded.py -- --review-id worn-cold-start
```

Cold verification checks the SHA256 of each packed CC0 image against the original download, all saved viewport shading modes, support contacts and the existing layout/state audit. Omit `--cameras` for the complete eleven-camera cold render set; `--states` also renders all supplemental state previews.

## Desktop startup recovery (2026-09-06)

The saved room and future builds now open in SOLID shading with material colours. This avoids automatically compiling the full GPU material-preview workload while loading. All saved 3D workspaces in the delivered room use SOLID. Cycles render settings, geometry, material graphs and packed portraits are unchanged. Switch shading deliberately after loading if needed.

The reported disappearing window did not produce a crash note in Blender's own temporary directory, the user temporary directory or the blend directory, nor a recent Blender Windows Application error. The desktop process was still answering its MCP add-on. GPU material preview is a suspected loading-pressure path, not a proven crash cause. The lightweight startup is a mitigation, not a driver diagnosis.

After the change, a fresh headless open passed all 59 contacts and 29 objective checks. The desktop process was closed gracefully and relaunched minimized without Computer Use; the new process read the exact source in 5.829 seconds and remained MCP-ready. See ../production/renders/review/startup-fix/. Full rendered output was not rerendered for this viewport-only change. A local pre-change backup and launch stdout/stderr are kept in ignored ../production/logs/.
