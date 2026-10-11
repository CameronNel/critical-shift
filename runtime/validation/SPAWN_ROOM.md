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

## Owner-agreed editing and gameplay workflow (11 October 2026)

The owner is satisfied with the shown room comparisons and wants gameplay work
continued while Claude assembles the facility. Suit appearance remains open.
This records that feedback for those captures; it does not declare the complete
map, character presentation or multiplayer accepted.

Blender is the visual source of truth. Room assets are edited in the relevant
Blender authoring task; assembly placement/connection patches belong to the
combined builder. The combined `.blend` remains generated output, not a file to
hand-edit. Unity owns gameplay and the engine-specific material/light conversion.
Procedural texture inputs are baked from Blender; game lightmaps, shadow masks
and reflection probes are generated in Unity from the authored lighting plus
tracked conversion settings. No second lighting bake into Blender albedo is
required.

When the owner asks for a small map correction, the task includes the Blender
change and the resulting Unity refresh. A full affected-room refresh is preferred
for geometry/layout changes: preserve logical IDs, regenerate collision and
interaction poses, rebake affected lighting/probes, compare source/runtime views
and run the relevant physical checks. Rebuild textures only where their source
inputs or delivery UVs require it. The updated room stays in the assembled map.
Any newly assembled room uses Claude's recorded placement and reviewed handoff;
unfinished assembly work must not be overwritten or silently followed.

Gameplay rules and reusable adapters stay in tracked code. Bindings are recreated
by the scene generator from stable source names/IDs and explicit manifests. Do
not implement a feature only through manual changes to a generated scene: those
changes would be lost at regeneration. A room edit must revalidate interaction
positions, collision and reach, not merely its render mesh.

Current automation limits are explicit: saving Blender alone is not a live Unity
sync. `prepare_spawn.py` defaults to the documented PR95 snapshot; newer source
work requires its explicit `--map-ref` revision. Full preparation exports the
assembly, while the scoped spawn pass refreshes materials/collision and requires
the existing object inventory to match. General geometry refresh for an arbitrary
changed room, automatic upstream revision detection and incremental lighting
invalidation are not yet implemented. Until those exist, use the full verified
preparation path when required and handle it within the requested edit task.
The other five rooms still have preview materials; this workflow does not imply
that their conversion or gameplay is complete.

## Assigned behavior

| Spawn object | Runtime binding |
| --- | --- |
| `SPAWN_1` | One local first-person worker. All four markers remain present; no remote players are created. |
| Four `PPE_nn_suit` roots | Stand in front of an open locker and face it. The original `SUIT_UP` clip follows the 15-second preparation clock; the hanging suit stays visible and the worker stays unsuited. At the final pose, the accepted equipment transaction shows the worn suit and hides the hanging suit together. E/Q cancels; returning equipment restores the hanging suit. Boots/dock/light props stay put. |
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

Each locker has a generated Unity standing pose derived from its current imported front;
the source room and its markers are unchanged. Starting requires a grounded, uncrouched worker
within 0.4m horizontally and 0.2m vertically of that pose, facing within 35 degrees of the locker.
Movement and turning are held during preparation; losing the pose or reach cancels it.
The clip is sampled from the canonical shift clock across all 15 seconds, so pause freezes both
its progress and the deadline. Its final pose is applied before the outfit changes, followed by
the usual idle/movement blend. There is no suit flying out of the locker or cloth simulation.

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

Prepare the visual scene with **SpawnVisualReview.BakeAndRender** (command below), then open it and Play.
**Critical Shift > Spawn > Create assembled map scene** recreates the bindings and discards baked lighting, so run the visual preparation again after using it. The generated
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

## Gameplay baseline verification (4c5f1bb)

These results predate the source-preserving visual conversion below. New native results are
recorded separately; historical gameplay passes do not establish visual acceptance.

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
| Native PlayMode | Passed: 15 discovered/executed/passed, zero failed/skipped/inconclusive. Nine graybox cases plus six actual-map cases cover complete collision/rig import, all four benches and live bone/animation changes, all four locker standing poses and rejection/cancellation, hanging/worn visibility throughout the full 15-second clip, pause/final-pose equip/return, airlock-to-cafeteria traversal, and curved chamber sealing/test/release. |
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
API/static evidence: `runtime/out/spawn-api-locker-end/player-api.json`, `runtime/out/spawn-source-locker-end.json`.
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
unity -batchmode -nographics -projectPath "$PWD/runtime/unity" -runTests -testPlatform PlayMode -assemblyNames CriticalShift.Player.Tests.PlayMode -testResults "$PWD/runtime/out/spawn-playmode.xml" -logFile "$PWD/runtime/out/spawn-playmode.log"
xvfb-run -a -s '-screen 0 1280x720x24' "$PWD/runtime/out/spawn-player/CriticalShift" -batchmode -force-glcore -screen-width 1280 -screen-height 720 -screen-fullscreen 0 --cs-player-smoke -logFile "$PWD/runtime/out/spawn-player-smoke.log"
```

`--cs-player-smoke` verifies a running world for 120 frames, then stops it and checks that the
stopped view has no connected workers, pending timers, claims or registered objects. Success
requires `CS_PLAYER_ROOM_SMOKE_OK` and exit 0. This checks lifecycle in the built Player; the
15 native Test Runner cases establish the physical and animation behavior listed above.
The display uses Mesa llvmpipe software rendering, which is not target GPU performance evidence.
The final native result is `runtime/out/spawn-playmode-locker-end.xml` with its matching `.log`.
Build/smoke logs are `runtime/out/spawn-build-locker-end.log` and
`runtime/out/spawn-player-smoke-locker-end.log`. The cloud audio device falls back to FMOD nosound;
audio behavior is not validated.

The native pass required real fixes: invalid input-package and duplicate Test Runner references;
default 16-bit/welded collision import; overwritten FBX axis correction; a disabled door query
probe; interaction rays hitting the acting worker; bench orientation/clearance; and a decorative
cafeteria dust plane blocking the exit. Earlier native runs recorded 10/14, 11/14, 12/14 and 13/14
passes before the prior 14/14 result. The locker timing/standing follow-up passes 15/15 on its
first native run. Original failures remain in ignored logs and XML files.
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

The spawn conversion explicitly delivers unlit base colour, tangent normals,
metallic/smoothness and HDR emission in two general 4096px atlases plus dedicated floor, lettering and wall atlases. The TV retains its original packed
image and UV coordinates. Solid source colours and inactive normal inputs retain their original values instead of relying on tiny atlas islands. The other five rooms still use preview materials. Native lighting and
image comparison are separate evidence from gameplay tests.
Prototype room collision totals 7,071,274 triangles (mine 3,287,462; fuel 2,059,090). The front end
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
animation or full physical clothing simulation. Suit-up stretches the existing short gesture over
the required 15-second preparation; its pacing/contact still needs human review. Both visible outfit
and equipment stay unworn until the animation/deadline completes; cancellation leaves the suit
on its hanger. Airlock pressure, upgrades, radiation protection,
scanner certification, room machines and networked characters are separate gameplay work.

The map pin is intentional. Future assembly changes require explicit source/binding review and
`--map-ref`; unknown layouts fail rather than silently loading the old retiring map. Nothing in
this task modifies Claude's next-room branch or advances a room's art acceptance status.

## Source-preserving visual conversion

The initial Unity views failed comparison with fresh Blender renders at the same three authored
cameras. They lost procedural tile/paint/wood inputs, screen images and the authored lighting.
The old exporter collected only eight light instances from the module collection, missing the
ceiling and briefing practicals outside it. The conversion now reads the complete authored spawn
scene (22 light instances including linked dependencies).

`export_spawn_materials.py` evaluates shader inputs on export copies, retains original UVs for
source sampling, and records each object's material slots in the existing manifest. A temporary
joined bake mesh explicitly preserves object/generated coordinates as attributes, so joining
does not change procedural recipes. The delivery UV is also the normal bake’s tangent basis, and implicit procedural coordinates are preserved explicitly. Solid input colours use small linear textures; unused normal inputs remain geometric normals. No lighting, shadows or AO are baked into albedo. Metallic
is stored in R and smoothness in A; numeric maps stay linear and use channel-packed alpha
when saved, so smoothness never premultiplies metallic. Each constant source input is bound
independently from its atlas channel. HDR emission uses
half-float ZIP EXR. UV0 is the atlas, UV1 is reserved for Unity lightmapping, and UV2 retains
the original screen coordinates. The TV image is copied from the packed source without resizing.

The partial exporter reads spawn and its PR95 exterior skin directly, validates the assembled
object inventory, and round-trips only its updated collision. Other room exports are preserved.
Full preparation exports assembly geometry first, then performs the scoped material pass. Two
4096px general atlases, dedicated 2048px locker-floor and lettering atlases, and a
4096px wall atlas fit the 16GiB container; the single 8192px experiments exceeded memory. The shared atlas undersampled the tiny grout lines and produced visible aliasing. The dedicated floor uses a full planar UV layout and preserves the authored shader recipe.
The lettering pass rebakes all 69 nonempty source text meshes at sufficient texel density.
Its delivery meshes retain source positions and triangle counts; only UVs and material bindings
change, with a 2mm bounds guard. This avoids thin glyphs sampling unrelated atlas padding.
The same derivative path delivers 52 wall/dado meshes with dedicated texture density,
retaining source recipes and geometry. Failure
logs remain under `runtime/out/spawn-surfaces-export-v2.log` through `v4.log`.

FBX can reorder material slots, so multi-slot surfaces bind by imported material name.
Single-slot text/line meshes use their explicit source binding even when Unity imports them
as Default-Material. `BlenderSurface.shader` uses StandardSpecular lighting with exported dielectric
IOR/specular reflectivity and preserved metallic-workflow diffuse energy, two-sided rendering
and reversed back-face shading normals, matching Cycles' treatment of opaque surfaces.
The whiteboard's inward-facing front otherwise exposes its dark metal backing. Its two-sided
surface receives probe lighting: a shared baked chart darkens the side that faces the room. Opaque
materials also enable two-sided GI. Six tiny socket faces likewise use probe
lighting instead of unreliable small baked charts. The three reflection volumes cover the complete rooms
and import their HDR captures as linear cubemaps. Custom probe textures persist across scene
reloads; assigning only a bakedTexture outside Unity’s lighting-data asset loses the reference.
Temporary reflection-only rectangles supply the authored fixture area-light radiance during
capture and are removed before the scene is saved. Invisible spill/fill lights do not add
rectangular fixture geometry to reflections. Glass uses two-sided Standard fade lighting with
the source constant coverage: 0.16 for the pod and 0.10 for the suit visor. Raster glass still
approximates Cycles transmission/refraction.

For a floor-only refresh on an existing export, without changing geometry hashes
(add `--lettering` for text, `--walls` for wall delivery, or `--inputs-only` for source constant values):

```sh
blender -b runtime/out/spawn-export-source/map/sections/facility-assembly/sources/spawn-room/module.blend --disable-autoexec --python-exit-code 1 --python runtime/tools/export_spawn_floor.py -- runtime/unity/Assets/CriticalShift/Generated/Spawn
```

After preparing assets, run the graphics-enabled visual generator:

```sh
xvfb-run -a -s '-screen 0 1440x810x24' unity -batchmode -force-glcore -quit -projectPath "$PWD/runtime/unity" -executeMethod CriticalShift.Player.Editor.SpawnVisualReview.BakeAndRender -csCapturePath "$PWD/runtime/out/spawn-unity-matched" -logFile "$PWD/runtime/out/spawn-lighting.log"
```

On a desktop omit `xvfb-run`. Do not use `-nographics` for captures. The manifest stores the
three authored camera poses and 16:9 lens conversions. The generator sets linear rendering,
imports maps explicitly, configures source practicals/shadows, bakes stationary geometry, and
creates lighting/reflection probes. Players and movable doors/suits are excluded from static
GI; the local worker is hidden during reflection capture. Source AgX/look/exposure/gamma are
exported through Blender into a display LUT and applied to the actual gameplay camera.

`SpawnMapBuild.Build` consumes this prepared scene instead of regenerating an unlit one.
Source/scene/binding hashes reject stale preparation and altered exported textures or meshes.
`SpawnVisualReview.Render` recaptures the saved scene without saving camera/worker visibility
changes. Rebuild lighting after geometry/material/light changes. Built-in rectangle lights are
baked; moving objects receive probe lighting. The inverse-square point bake uses the reference-calibrated scale
power/100; area emitters use power/(π×area). Legacy forward
point attenuation uses power/500 after baking. The two mixed pendant lights retain their finite-source baked shadow masks;
other practical points and area lights are baked. Shadowmask mode combines static
soft fixture shadows with moving-object caster shadows. The generator preserves
the mixed bake output when calibrating runtime direct intensity, and does not
switch the pendants to real-time-only lighting or discard their masks.
Regenerate with `BakeAndRender` after changing light/material settings; the prepared-scene
source fingerprint rejects builds from an earlier lighting configuration.
Embedded visible bulb faces are separated into a derived non-shadow-casting renderer; the
fixture body keeps its shadows. Blender’s finite point emitter extends beyond those bulbs,
whereas a built-in point bake starting at their centre otherwise self-occludes. The complete
visible triangle union and collision mesh are preserved.
Transparency, moving-object lighting, target performance and human acceptance need separate
review. This route does not guarantee pixel-identical Cycles lighting.


## Earlier visual derivative verification (5687ebe, 11 October 2026)

The [three matched-camera comparisons](spawn-visual-20261011/README.md) and
[compact evidence](spawn-visual-evidence.json) belong to this visual derivative,
not the older gameplay baseline above. The native bake/capture finished on the
saved gameplay scene with two lightmaps, 390 probe positions and three persisted
reflection cubemaps. All 51 pinned source inputs and all six geometry/collision
file hashes remain unchanged.

| Check | Actual result |
|---|---|
| Pinned API compile | Passed: four assemblies, 16 C# files, warnings as errors. |
| Python tooling | Passed: 40 tests. |
| Metadata/static source | Passed: 918 GUIDs, nine asmdefs, 22 C# assets including generated derivatives. |
| Native physical/animation PlayMode | Passed: 15 executed/passed, zero failed/skipped; all benches, lockers, full suit clip, airlock traversal and pod seal/test/release. |
| Linux Development Mono Player | Build passed; 120-frame running-world smoke and clean shutdown passed, exit 0. |
| Canonical rules | Unchanged from the 4c5f1bb baseline (718 tests and 12 scenarios run twice); those results are reused, not relabeled as a fresh run. |

The final native PlayMode run preceded only the last point-light bake-intensity
calibration; geometry, collisions, materials, animation and gameplay behavior were
identical. The final calibrated scene was then baked, reloaded, captured, built
and smoke-tested. Two large-collision-mesh warnings remain during build processing
(the mine and fuel corridor); Player startup does not repeat them. The container
has no audio device and uses FMOD nosound. Mesa llvmpipe is not target-GPU evidence.

Visual acceptance is **pending**. Briefing's pendant shadows and ceiling brightness
still differ visibly from Cycles; procedural grain and metallic/screen reflections
also differ. Glass remains an approximation. The other five rooms still use their
preview conversion. Windows Player execution, remote peers, full continuous
animation/contact review and target-GPU performance remain NotRun. Neither the
images nor passing physical tests declare a perfect Blender match.

## Wall correction follow-up (11 October 2026)

The owner's harsh-wall feedback prompted a controlled material/shadow comparison.
The [mistake and correction note](SPAWN_VISUAL_CORRECTION.md) records what was
wrong and the final conversion. See the [new comparison gallery](spawn-visual-correction-20261011/README.md)
and [current evidence](spawn-wall-correction-evidence.json). The earlier table
above is historical evidence, not the test record for this follow-up. Visual
acceptance remains pending; lighting near the sideboard and screen reflections
still differ from Blender.

| Current correction check | Actual result |
|---|---|
| Native bake and saved-scene capture | Passed: two lightmaps/two shadow masks, 390 probes and three persisted reflection cubemaps. |
| Native PlayMode | Passed: 15 executed/passed, zero failed/skipped on the final corrected scene. |
| Linux Development Mono Player | Build passed; 120-frame running-world check and clean shutdown passed, exit 0. |
| Pinned API and tooling | Four assemblies/16 C# files passed; 40 Python tests passed; static metadata checks passed (983 GUIDs). |
| Source and exported assets | All 51 inputs and six original room mesh/collision hashes unchanged; all five atlas packages and wall/lettering FBX hashes verified. |

The initial API/native compile failed on an incorrect enum namespace, then passed
after correction; its logs are retained in the evidence hashes. Disk pressure
during the Player build was resolved by relocating own generated data/backups to
tmpfs; that same build completed successfully. No new OOM events occurred. These
container checks do not establish target performance or Windows Player execution.


## Suit appearance and reflection imports (11 October 2026)

The worn suit exports its original shader inputs to a separate 4096px atlas.
The clear visor converts its active Transparent/Fresnel/Glossy graph rather than
the unused Principled node. Its authored reflection falloff remains separate
from colour; Fresnel is evaluated at runtime. The older hanging suit retains its
own materials and receives geometry-derived front/back hood occlusion through a
separate shader. No room texture, geometry or original Blender asset is edited.
[The suit gallery](spawn-suit-correction-20261011/README.md) records the source
comparisons, physical validation and remaining rendering differences.

Appearance refreshes retain the validated animation FBX separately from the
model/material FBX. Source-revision changes regenerate animations; the round trip
checks the same 23-bone bind pose. The current correction preserves all 30 mesh
geometries/skin weights and all 52 animation curves. Prepared-scene validation
includes both FBXs, the rig manifest, suit atlas hashes and hood derivative.

Refreshing exports creates Unity metadata only when missing. Reflection baking
explicitly imports the three snapshots as linear cubemaps with specular-filtered
mipmaps. Capture/build validation rejects unfiltered imports. This prevents the
severe wall speckles caused by the metadata reset during the suit refresh; the
[correction note](SPAWN_VISUAL_CORRECTION.md) retains that diagnosis and its controls.
The shared room surface shader stays at its approved version.

In this container, optional `-csCompressedBuild` development packaging uses LZ4HC
to reduce transient disk use. The default build behavior is retained. This is
packaging, not target-GPU performance evidence.
