# Spawn bindings on the current assembled map

User-authorized implementation, 10 October 2026. Branch: `feat/spawn-room-runtime-bindings-20261010`.
Base: player slice `624879b6b50c3cee2ac753d78e033b5f53d43f9c` (PR #97).
Primary author: Codex. Independent review and maintainer merge are pending.

## Source and preservation

The map is PR #95, `bb6b4924849d38097ee629a6fa2c00dc1b56095f`, as confirmed by the map author.
Its six rooms are spawn, front end/cafeteria, mine, refinery, medical reanimation and fuel corridor.
The reactor is not placed. The preparation tool runs that exact assembly builder in ignored scratch
storage, preserving its omissions, local patches, exterior skins and placements. It never saves
to a tracked Blender file or edits the assembly builder. Spawn remains at plan `(8, -92.38, 0)`, yaw 0.

Spawn's source module supplies exact original names, four spawn markers, four hanging suit roots,
locker hinges, two briefing benches, TV, sideboard, two thermoses, integrity pod and door poses.
The viewing assembly removed its airlock leaves: only the runtime derivative restores those 22
leaf/gauge objects from the source. The four omitted service-end closures remain omitted for the
cafeteria join. No existing name or source contract is renamed.

The existing character builders/rig come from `claude/character-rig`, PR #55,
`90a42290df627330e4c4e445b6bfa7fba0464e3a`. The reference `.blend` itself is static, so the exporter
runs the existing procedural builders and all 49 registered clip builders from that revision.
It preserves their 23-bone skeleton, names, rest pose, 24fps, in-place motion and outfit regions.
No source animation is rewritten. Three simple room-only sitting derivatives fill the missing
inventory: `SPAWN_SIT_DOWN` / `SPAWN_STAND_UP` (frames 0–18), `SPAWN_SEATED_IDLE` (0–48, loop).
They use the same existing pose/IK machinery. Preview tools/props are excluded.

Geometry is exported as FBX using Unity's built-in importer, metre units, -Z forward/+Y up.
The Blender plan `(x,y,z)` becomes Unity `(x,z,y)` with negated yaw. Placement uses a separate
parent to retain the FBX root axis correction; door node-local poses reflect Blender Z. Meshes
are triangulated before export. Collision uses 32-bit indices without importer welding or
optimization, and scene creation checks each room’s complete triangle inventory and all spawn
anchor positions. Decorative `stain_` / `decal_` / `scuff_` surfaces are excluded from collision,
with omissions recorded in the manifest. Per-file hashes, source pins, anchors and roles accompany exports.
The rig uses Generic animation on its original skeleton, with root motion disabled. There is no
retargeting, external mocap, renderer/importer package, network transport or new third-party asset.
Original geometry, images and existing material licensing/provenance remain with their source files.

## Assigned behavior

| Spawn object | Runtime binding |
| --- | --- |
| `SPAWN_1` | One local first-person worker. All four markers remain present; no remote players are created. |
| Four `PPE_nn_suit` roots | Exclusive 15-second preparation at an open locker, original `SUIT_UP` gesture, cancel/return to that station, then equipment-slot custody and suit visibility. Boots/dock/light props stay put. |
| Two briefing benches | Two exclusive seats each, oriented toward the authored TV, sit/idle/stand clips, explicit clear exits and disabled seated locomotion. |
| `AIRLOCK_leaf_L/R` | Authored sliding translations, use on leaves or approach controls, closing obstruction checks/reopening, advisory PPE warning that permits exit. |
| Eight personal locker leaves | Original hinge pivots/open rotations, interactive open/close; preparation requires that locker to be open. |
| Integrity pod leaves/button/state variants | Original open/closed poses, sealing, a three-second test on the existing shift clock, pass/inspect/fail from current worker facts, automatic opening and E cancellation. It reports condition without repairing or certifying the suit. |
| `BRIEFING_TV_display` | E opens/closes the shift briefing. Authored screen geometry stays in place. |
| `BELONG_01_thermos`, `BELONG_03_thermos` | Physical carryables, exclusive claim, pickup/drop gestures and collision-safe carry projection. |
| Sideboard | One place/take slot and existing `PLACE`/`PICKUP` clips. |
| Worker | Existing idle, directional walk, sprint, jump/fall/land, carry and interaction animations; canonical gear/posture determines outfit and seated pose. |

Doors/scanner/briefing are local Unity presentation and physical motion. Equipment, holder, posture,
worker condition and shift time have their existing canonical writers. `PlayerOperations` owns only
a bounded pending intention per actor, tied to the live claim generation and shift deadline.
Early equip, full hands, contention, retries, cancellation, stale deadlines and legacy bypasses
are rejected without a second inventory. Claim loss, impact, attachment failure, disconnect and
stop reconcile the intention. Scanner state is not an authoritative gameplay certificate.

## Prepare and play

Prerequisites: Git LFS, .NET 8, Python 3.10+, Blender 5.2.2 LTS, activated Unity 6000.4.3f1
(revision `39d1a88d4dd1`). Use the pinned editor instead of changing the repository engine version.
Unity Personal is now activated in this container through official browser sign-in. A fresh
machine still needs activation. Passwords and license credentials do not belong in the repository.
The pinned editor resolves its bundled Test Framework 1.6.0 / NUnit 2.0.5; package/profile pins
now match those versions. Legacy input needs no `inputlegacy` package, and built-in animation
is enabled. The Linux SDK/toolchain 1.1.0 dependencies are registered by the editor.

From the repository root:

```sh
python runtime/tools/prepare_player.py
python runtime/tools/prepare_spawn.py --blender /path/to/blender
unity -projectPath "$PWD/runtime/unity"
```

The second command fetches missing pinned Git objects, hydrates only the exact source assets,
builds in `runtime/out/spawn-export-source/` and exports to
`runtime/unity/Assets/CriticalShift/Generated/Spawn/`. Both locations are ignored. It verifies input
hashes after export and creates deterministic asset metadata. Do not run a full LFS pull or copy
an old assembled map into this scene. Allow storage for the scoped sources and several hundred MB
of derivative geometry. `--rig-only` / `--skip-rig` permit separate preparation.

In Unity select **Critical Shift > Spawn > Create assembled map scene**, then Play. The generated
`Assets/CriticalShift/Generated/Spawn/AssembledMap.unity` is separate from the foundation catalogue
and graybox scene. Use the legacy Input Manager (Old), with default Mouse X/Y axes.

WASD/mouse move/look; Space jumps; Ctrl crouches; Shift sprints. E uses doors, suits, benches,
briefing, scanner and props. E or Q cancels preparation. Q drops a carried prop. E at the original
station or U in reach returns its suit. Escape pauses/resumes; F5 restarts with fresh world state.
The 15-second suit preparation is automatic on completion; R cannot bypass its deadline.

Desktop build entrypoint after activation:

```sh
unity -batchmode -nographics -quit -projectPath "$PWD/runtime/unity" -buildTarget Linux64 -executeMethod CriticalShift.Player.Editor.SpawnMapBuild.Build -csBuildPath "$PWD/runtime/out/spawn-player/CriticalShift" -logFile "$PWD/runtime/out/spawn-build.log"
```

For Windows use Win64 and an `.exe` output path with matching build support. The build selects
only the generated map scene, Built-in rendering, Mono, .NET Standard, Disabled stripping and
pre-baked collision meshes.
Scene generation does not add it to the foundation build catalogue.

## Actual verification

| Check | Result and scope |
| --- | --- |
| Canonical `python tools/verify.py` | Passed: 718 executed/passed, zero failed/skipped, including 30 player cases. All 12 scenarios passed twice; failing NUnit/scenario/report-safety controls behaved correctly. .NET 8.0.425. |
| `prepare_player.py` | Passed: eight canonical Release DLLs, source/destination fingerprints, zero build warnings/errors. |
| Pinned Unity API compilation | Passed: four assemblies / 13 source files, warnings as errors against actual 6000.4.3f1 APIs. The five editor-only map cases execute in the native runner; supplementary compilation does not validate them. |
| Python tooling suite | Passed: 40 tests. Native runner negative/control cases remain distinct from actual engine execution. |
| Blender exports and clean reimport | Passed: six room collision FBXs preserve local bounds within 2mm; rig preserves 23 bones and exactly 52 actions. All original 49 clip names are present. |
| Sampled exported pose review | 156 finite pose samples (first/mid/last of every clip); seated idle position seam is 0m. Twelve rendered samples of the three sitting clips and `SUIT_UP` were inspected. The visible seat contact motivated a measured 0.34m model support offset; this places the short character's feet above the floor on these benches. Still imagery does not establish rhythm at 24fps. |
| Source preservation | Passed: 51 scratch source inputs match their staged hashes after export. Tracked `sections/`, map builder/placement/docs, source rig and original checkout are unchanged. |
| Static source/metadata | Passed: 84 GUIDs, 9 asmdefs, 19 C# assets, including ignored generated outputs. No missing/orphan/duplicate metadata or new runtime assembly dependency edge. Native package corrections are recorded above. |
| Native map scene creation | Passed: exact editor imported and saved the separate six-room scene, checked all spawn anchors and bound all 52 animation states. The earlier license failure is retained. |
| Native PlayMode | Passed: 14 discovered/executed/passed, zero failed/skipped/inconclusive. Nine graybox cases plus five actual-map cases cover complete collision/rig import, all four benches and live bone/animation changes, locker cancellation/pause/full 15-second equip/return, airlock-to-cafeteria traversal, and curved chamber sealing/test/release. |
| Linux Player | Passed: Development Mono build, 120-frame running-world smoke and clean shutdown, exit 0. Pre-baking removes the two large-mesh warnings from Player startup; the build still emits them while processing mesh assets. Windows Player execution remains NotRun. |
| Animation/art/feel and remote peers | Native sit/suit playback assertions pass. Full continuous playback/contact review, visual acceptance, human feel, remote peers and target profiling remain NotRun. Independent review and merge remain pending; no roadmap/art acceptance is advanced. |

Reproducible checks from the repository root:

```sh
python runtime/tools/check_player_api.py --editor-root /path/to/unity-6000.4.3f1 --out runtime/out/spawn-api-final
python runtime/tools/check_source.py
python -m unittest discover -s runtime/tools/tests -v
blender -b --disable-autoexec --python-exit-code 1 --python runtime/tools/review_spawn_rig.py -- runtime/unity/Assets/CriticalShift/Generated/Spawn runtime/out/spawn-rig-review
```

Offline evidence: `runtime/dotnet/artifacts/summary.json` and `runtime/out/spawn-offline-final.log`.
API/static evidence: `runtime/out/spawn-api-validated/player-api.json`, `runtime/out/spawn-source-validated.json`.
Exports: `map-bindings.json`, `rig-bindings.json`, `map-roundtrip.json`, `rig-roundtrip.json` inside the
generated asset folder. Pose samples/images: `runtime/out/spawn-rig-review/pose-evidence.json` and
`poses.png`. Source integrity: `runtime/out/spawn-export-source/source-integrity-final.json`.
Initial activation failure: `runtime/out/spawn-native-create.log`. Final native scene/build/test logs
and compact evidence are listed below. These are actual local ignored outputs, not files that a
fresh checkout already contains. A compact record accompanies this note.

The first export attempt failed on a linked spawn collection absent from the saved viewing scene;
the exporter now reads it directly from the pinned source. Python exceptions now terminate Blender
with a nonzero exit code. A rule test caught stale preparation after impact and prompted reconciliation
in the existing worker workflow. Final checks passed after those fixes; no earlier failure is a pass.

## Native execution

Run the pinned editor after preparing both the canonical DLLs and map exports. Native test
execution must omit `-quit`; the Test Runner exits when its result file is complete.

```sh
unity -batchmode -nographics -quit -projectPath "$PWD/runtime/unity" -executeMethod CriticalShift.Player.Editor.SpawnMapBuild.Create -logFile "$PWD/runtime/out/spawn-native-create.log"
unity -batchmode -nographics -projectPath "$PWD/runtime/unity" -runTests -testPlatform PlayMode -assemblyNames CriticalShift.Player.Tests.PlayMode -testResults "$PWD/runtime/out/spawn-playmode.xml" -logFile "$PWD/runtime/out/spawn-playmode.log"
xvfb-run -a -s '-screen 0 1280x720x24' "$PWD/runtime/out/spawn-player/CriticalShift" -batchmode -force-glcore -screen-width 1280 -screen-height 720 -screen-fullscreen 0 --cs-player-smoke -logFile "$PWD/runtime/out/spawn-player-smoke.log"
```

`--cs-player-smoke` verifies a running world for 120 frames, then stops it and checks that the
stopped view has no connected workers, pending timers, claims or registered objects. Success
requires `CS_PLAYER_ROOM_SMOKE_OK` and exit 0. This checks lifecycle in the built Player; the
14 native Test Runner cases establish the physical and animation behavior listed above.
The display uses Mesa llvmpipe software rendering, which is not target GPU performance evidence.
The final native result is `runtime/out/spawn-playmode-validated.xml` with its matching `.log`.
Build/smoke logs are `runtime/out/spawn-build-prebaked.log` and
`runtime/out/spawn-player-smoke-prebaked.log`. The cloud audio device falls back to FMOD nosound;
audio behavior is not validated.

The native pass required real fixes: invalid input-package and duplicate Test Runner references;
default 16-bit/welded collision import; overwritten FBX axis correction; a disabled door query
probe; interaction rays hitting the acting worker; bench orientation/clearance; and a decorative
cafeteria dust plane blocking the exit. Earlier native runs recorded 10/14, 11/14, 12/14 and 13/14
passes before the final 14/14 result. Original failures remain in ignored logs and XML files.
A Player attempt without a display crashed in SDL mouse input; the supported cloud smoke
command above uses Xvfb. The initial smoke assertion also incorrectly expected the stopped
view to disappear; the corrected check verifies its stopped state and released resources.

The fixed 32GiB cloud disk filled during the first native import. Only this task's generated
`runtime/unity/Library` cache was moved to `/dev/shm/critical-shift-spawn-library` and symlinked.
It is disposable and ignored; a fresh machine can use a normal Library directory with enough
disk space. Source assets, installed editors and Claude's checkout were preserved.

The compact [spawn-export-evidence.json](spawn-export-evidence.json) records current source/export
hashes, exact test identities, build and smoke results, output hashes and remaining limitations.
Native raw logs and binaries live in ignored `runtime/out/`; they are available in this workspace
and must be regenerated on a fresh checkout.

## Remaining limits

Procedural Blender shaders and authored lighting do not transfer faithfully through FBX. Image
textures and geometry are retained, while Unity lighting/materials are previews requiring native
review. Prototype room collision totals 7,071,274 triangles (mine 3,287,462; fuel 2,059,090). The front end
omits 206 decorative surfaces / 412 triangles from collision. For rooms over two million triangles,
Fast Midphase is disabled to avoid Unity’s documented large-mesh collision limitation.
The final build retains two warnings while processing the mine/fuel mesh assets; native tests
verify those active colliders have Fast Midphase disabled, and the pre-baked Player starts with
zero such warnings.
No collision/performance budget or frame time has been accepted. These meshes need profiling and
likely purpose-built simplification before production. Spawn’s benches, scanner and cafeteria exit
have native coverage above. Traversal through all other rooms, actual thermos/sideboard use,
camera/outfit clipping, longer play sessions and full
animation continuity still need broader physical/visual review. API compilation cannot establish them.

Original clip contact defects documented on the rig branch remain, including `SUIT_UP` strap
contact and some tool/prop grips. The new sitting clips are simple poses, with no hand contacts,
breathing layer or polished sit approach. Suit removal reuses `SUIT_UP`; it has no bespoke doffing
animation or full physical clothing simulation. The outfit previews during preparation, which
holds its final gesture until the canonical deadline. Protection remains unequipped until that
deadline commits equipment; cancellation clears the preview. Airlock pressure, upgrades, radiation protection,
scanner certification, room machines and networked characters are separate gameplay work.

The map pin is intentional. Future assembly changes require explicit source/binding review and
`--map-ref`; unknown layouts fail rather than silently loading the old retiring map. Nothing in
this task modifies Claude's next-room branch or advances a room's art acceptance status.
