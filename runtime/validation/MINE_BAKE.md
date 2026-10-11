# Wooden R39 mine delivery

This task bakes the mine already placed in the combined map. It does not use the discarded concrete Gullet scene, edit Blender source rooms, change the assembly builder, or merge its own work. The mine's source art remains unreviewed.

The assembly snapshot is PR 95, bb6b4924849d38097ee629a6fa2c00dc1b56095f. Main was inspected at d9eb1c5642273722f2ecee7179e958f05d39fa61; its assembly builder and mine source have the same content. Claude's PR 102 branch is `claude/critical-shift-hall-fixes-khgd29`. The owner's handoff described local reactor assembly work; a later read-only check found it pushed at c1b1b81c95ff45f28fea394419103b192f532f95. That revision adds reactor/concourse geometry and trims the front-end spine, with no mine source or placement changes. This bake uses committed main's six-room snapshot. No files on Claude's branch are written by this task.

## Refresh and ownership

Blender remains the visual source. The runtime exporter reads the combined builder's already patched mine, then releases other Blender rooms before baking. Only `Room-mine.fbx`, mine surface files, and their explicit material bindings change. All collision files and other room meshes are SHA-256 checked against the prepared map.

After preparing the existing map and rig with `prepare_player.py` and `prepare_spawn.py`, run from the repository root:

```sh
python runtime/tools/prepare_mine.py --map-ref <committed-assembly-ref>
```

The tool verifies the assembly builder and every staged room/exterior source against the prepared snapshot. If any changed, refresh the assembled delivery with `prepare_spawn.py --map-ref <new-ref> --skip-rig` first, then run `prepare_mine.py` with the same ref. A source geometry change requires refreshing collision and lighting; this material-only operation never reuses collision from changed geometry. General automatic room-by-room geometry refresh is still separate work.

No existing asset metadata is reset. Mine PNG import specifies linear numeric maps, sRGB albedo, atlas padding/filtering and retained alpha. The original 4096-pixel, 16-bit baked PNGs remain unchanged. Native runtime copies use high-quality BC7 for colour/metallic/smoothness and BC5 for normals, retaining resolution while bounding loaded texture memory. Emission stays HDR. Unity imports only channels that the materials actually use. Reflection probes require specular convolution, mipmaps, trilinear filtering and clamp wrapping.

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

Unity owns its lightmaps, probes and engine lighting. Mine delivery maps contain source shader inputs, including authored shader AO, rather than baked scene illumination. The assembly's dusk lighting and display transform are read from Blender. The player retains spawn's display transform inside its collision bounds and uses the assembly transform outside them.

Blender's surface UVs and geometry stay untouched. Unity generates its own lightmap UV channel, and an import postprocessor checks its range and coverage. Larger surfaces receive the normal lightmap budget; props smaller than 0.5 m use baked probes and are excluded from lightmap contribution. Native validation rejects omitted lightmapped surfaces. Each room's display transform has its own Unity material, so the mine cannot overwrite spawn's colour profile.

## Evidence and limits

The task record and inspected images belong in `mine-bake-20261011/`. Technical import, native physical validation, visual comparison and independent art acceptance are separate claims. Do not infer target-hardware performance from this software-rendered container.

The source's two volume containers require engine-specific atmosphere; they are hidden rather than imported as opaque surface meshes. Crystal facing color and refractive water also need visual comparison. Neighboring rooms without explicit baked surface packages retain preview materials. Baking the mine does not approve or finish the rest of the facility.
