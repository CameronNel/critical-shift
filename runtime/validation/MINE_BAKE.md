# Wooden R39 mine delivery

This task bakes the mine already placed in the combined map. It does not use the discarded concrete Gullet scene, edit Blender source rooms, change the assembly builder, or merge its own work. The mine's source art remains unreviewed.

The assembly snapshot is PR 95, bb6b4924849d38097ee629a6fa2c00dc1b56095f. Main was inspected at d9eb1c5642273722f2ecee7179e958f05d39fa61; its assembly builder and mine source have the same content. Claude's PR 102 branch is `claude/critical-shift-hall-fixes-khgd29`. The owner's handoff described local reactor assembly work; the latest read-only check found it pushed at 7fffd1ae7d5a9d4a520047a3ef9b93757a6c4460. That revision adds reactor/concourse geometry and trims the front-end spine, with no mine source or placement changes. This bake uses committed main's six-room snapshot. No files on Claude's branch are written by this task.

## Refresh and ownership

Blender remains the visual source. The runtime exporter reads the combined builder's already patched mine, then releases other Blender rooms before baking. The mine mesh, mine surface files and bindings change. A separate `MineContext.fbx` supplies UV/material overlays for existing front-end depot meshes visible around the mine; their original mesh assets, transforms and all collision files stay unchanged. Native overlay validation checks bounds and triangle counts before replacing mesh UVs, and does not create duplicate objects. All collision files and other room meshes are SHA-256 checked against the prepared map.

After preparing the existing map and rig with `prepare_player.py` and `prepare_spawn.py`, run from the repository root:

```sh
python runtime/tools/prepare_mine.py --map-ref <committed-assembly-ref> --batched
```

The tool verifies the assembly builder and every staged room/exterior source against the prepared snapshot. If any changed, refresh the assembled delivery with `prepare_spawn.py --map-ref <new-ref> --skip-rig` first, then run `prepare_mine.py` with the same ref. A source geometry change requires refreshing collision and lighting; this material-only operation never reuses collision from changed geometry. General automatic room-by-room geometry refresh is still separate work.

No existing asset metadata is reset. Mine PNG import specifies linear numeric maps, sRGB albedo, atlas padding/filtering and retained alpha. The original 4096-pixel, 16-bit baked PNGs remain unchanged. Native runtime copies use high-quality BC7 for colour/metallic/smoothness and BC5 for normals, retaining resolution while bounding loaded texture memory. Emission stays HDR. Unity imports only channels that the materials actually use. This includes spawn: constant emission and direct screen images do not load an unused emission atlas. Unused channels retain their full source files but use a 32-pixel Unity placeholder import. Spawn normal and metallic/smoothness runtime maps also use BC5/BC7 at their original resolution; spawn colour textures retain their existing format. Thin visor reflection-mask maps remain required even when metallic and roughness are constant. Reflection probes require specular convolution, mipmaps, trilinear filtering and clamp wrapping.

## Native scene and lighting

The same isolated `AssembledMap.unity` contains all assembled rooms and existing spawn gameplay. Room inventory follows the manifest, so later assembly additions are validated individually rather than rejected by a fixed six-room count. Spawn remains required, along with the other five existing rooms.

Use the pinned Unity 6000.4.3f1 editor with graphics enabled:

```sh
Unity -batchmode -force-glcore -quit -projectPath runtime/unity \
  -executeMethod CriticalShift.Player.Editor.SpawnVisualReview.BakeAndRender \
  -csCapturePath <absolute-spawn-capture-directory> -logFile <absolute-log>
Unity -batchmode -force-glcore -quit -projectPath runtime/unity \
  -executeMethod CriticalShift.Player.Editor.SpawnVisualReview.Render \
  -csRoom mine -csCameraFile <absolute-mine-cameras-json> \
  -csCapturePath <absolute-mine-capture-directory> -logFile <absolute-log>
```

Unity owns its lightmaps, probes and engine lighting. Mine delivery maps contain source shader inputs, including authored shader AO, rather than baked scene illumination. The default path bakes original objects directly. The optional `--batched` path joins only compatible attribute/UV schemas, captures original material coordinates, and hides the original meshes while their temporary replacements bake. This avoids evaluating duplicated geometry and retains per-object data. Materials that depend on Object Info fall back to direct baking. Constant channels use their exact per-material definitions; unused atlas channels skip scene evaluation. Completed object-preserving atlas passes can be reused only with a source-pinned, resolution-matched record and matching texture hashes. Blender persistent data bounds repeated scene compilation. The assembly's dusk lighting and display transform are read from Blender. The player retains spawn's display transform inside its collision bounds and uses the assembly transform outside them.

Blender's surface UVs and geometry stay untouched. The Blender exporter generates a dedicated per-mesh lightmap UV channel with padding, and a Unity import postprocessor checks its range and coverage. Unity's dense-mesh unwrap was superseded after a 38-minute import; the dedicated export avoids that repeated cost. Larger surfaces receive the normal lightmap budget; props smaller than 0.5 m use baked probes and are excluded from lightmap contribution. Split mine flame/bulb surfaces also use probes: their authored point lights provide illumination, rather than forcing tiny emissive faces into a lightmap. Native validation rejects omitted lightmapped surfaces and incorrect emitter contribution flags. The selected depot overlays participate in the same lighting bake; other front-end preview renderers are muted during the bake and restored afterwards. A native bake returning without lightmaps is rejected, including Unity failures that incorrectly return success. For the bake only, static collision instances are released to bound memory and then restored from their unchanged manifest assets before captures or scene saving.

Join validation exports nine ray expectations from Blender geometry. The centre rail is occupied by the authored ore cart at 0.6 m; both side walking lanes are clear at 0.6, 1.7 and 3.0 m. Unity must match the source contacts and all six clear walking rays. The initial all-clear centreline assumption failed and was corrected after tracing the actual cart; no collider faces or map objects were removed. Each room's display transform has its own Unity material, so the mine cannot overwrite spawn's colour profile.

## Evidence and limits

The task record and inspected images belong in `mine-bake-20261011/`. Technical import, native physical validation, visual comparison and independent art acceptance are separate claims. Do not infer target-hardware performance from this software-rendered container.

The source's two volume containers are hidden as opaque meshes. Blender samples their procedural density through its own shader evaluator into 128×16×16 grids. Unity uses these fields for a depth-aware local atmosphere pass, before the display transform, with illumination sampled from its baked probes. This is an approximation of volume scattering, rather than Cycles' full multiple scattering. Crystal facing color and refractive water also need visual comparison. Neighboring rooms without explicit baked surface packages retain preview materials. Baking the mine does not approve or finish the rest of the facility.

## Visual correction in progress

The first native bake passed binding, lightmap and collision checks, but its three mine captures failed visual review. Joined material baking produced coarse/triangular artifacts, and the front-end context ground and depot props retained white preview materials. The corrected object-preserving material bake, depot overlay and atmosphere must pass a fresh native bake, matched captures, gameplay tests and Player build before this delivery is treated as finished. Earlier native evidence applies only to the superseded first pass.

The subsequent three-lightmap bake completed, but the matched views still failed visual review: the cliff was green instead of grey, timber looked coarse, and the tunnel backing was white. A native diagnostic confirmed that Unity's JSON deserializer creates an empty `directEmission` record when that field is omitted. Checking only for a non-null record incorrectly skipped the authored emission atlas and left emission enabled with a white fallback. The importer now requires a non-empty direct file before skipping that atlas, and native mine validation rejects missing authored emission/colour textures. Diagnostic captures confirm the solid white backing is removed. They retain the previous lightmaps and are not final lighting evidence; a fresh lighting bake and remaining colour/texture corrections are still required.
