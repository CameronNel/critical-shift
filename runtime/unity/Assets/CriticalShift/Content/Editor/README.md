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

**Evidence, 2026-10-17:**
- **Compile:** compiled with the .NET 8 SDK against the pinned 6000.4.3f1 editor's own UnityEngine and UnityEditor module DLLs and its .NET Standard 2.1 references, the same reference set as `runtime/tools/api_compile.py`. Result: 0 errors, 0 warnings. A deliberate bad API call failed as expected.
- **Light rotation:** checked against Blender's `mathutils` over 2,000 random rotations; the largest error was 2e-7.
- **Not run:** a Unity import, the URP set-up and any Unity test. There are no Unity tests for this assembly yet. The Blender-to-Unity axis rule `(-x, z, -y)` is derived, not measured: if the lights in a prefab sit mirrored relative to the room, the rule is wrong.
