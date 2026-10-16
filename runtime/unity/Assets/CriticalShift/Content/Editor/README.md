# Baked room importer (editor only)

**Responsibility:** imports the rooms baked by `sections/facility-assembly/unity/bake_room.py` as URP Lit content. For each room it:
- copies the FBX, textures and manifests into `Assets/CriticalShift/Content/Rooms/<room>/`;
- applies the texture and FBX import settings;
- builds one URP Lit material per `materials.json` entry and remaps the FBX's materials to them;
- recreates the lights from `lights.json`;
- saves `<room>.prefab`.

**Not its responsibility:** gameplay, collision, room placement in the map, lightmap baking or URP quality tuning (see `URP_SETTINGS.md`).

**Owner and lifetime:** editor-only, run on demand. It is the only writer of `Content/Rooms/`, which is generated, git-ignored and safe to delete and re-import. The bake sources stay in `sections/`.

**Dependencies:** UnityEditor and UnityEngine only. URP is reached by shader name and reflection, so the assembly compiles without the package. The menu stops with instructions if URP is missing.

**Use:**
- Menus: `Critical Shift > Rooms > Set Up URP`, `Import All Baked Rooms` and `Import One Baked Room...`.
- Batch mode: `-executeMethod CriticalShift.Content.Editor.BakedRoomImporter.ImportAllBatch [-bakedRooms <folder>]`. Exit code 0 means every room imported; 1 means a room failed; 2 means URP is not ready; 3 means no rooms were found.

**Conversions** (`BlenderToUnity.cs`):
- A Blender point `(x, y, z)` becomes Unity `(-x, z, -y)`.
- Light intensities are matched for a white diffuse surface: P/(4π²) for points and spots, P/(π²A) for area lights, S/π for a sun. These are starting values; retune them against the bake's `compare/` renders.
- Area lights are Baked; points and spots are Mixed.

**Tests:** none in the Unity test assemblies yet. The C# was compiled against the pinned editor's API DLLs, and the conversions were checked against Blender; see the PR. No Unity import has been run.
