# Unity URP delivery: pilot (cooling plant)

Owner, 2026-10-15: *"Importing this into unity will look like shit"*. Asked, they chose to target **URP** (recorded in `design/ENGINE_DECISION.md`) and to **pilot one room first**. Unreviewed; no Unity editor was available.

## Why the map would import badly

`unity_audit` (2026-10-15, on `combined/combined_map.blend`) measured what an FBX import would carry:

| | Share of the map's 5.12 M base triangles |
|---|---|
| Procedural Cycles materials (noise, voronoi, AO and bevel nodes, object-coordinate masks): FBX drops all of it, Unity gets a flat colour | **83.7 %** |
| Constant colours (survive) | 8.5 % |
| Image textures (survive) | 7.8 % (almost all the turbine rebuild) |

Many meshes also have no UVs at all: the front end 99.8 % of its triangles, the spawn room 73.5 %, the electrical room 69.8 %, the refinery 66.4 %. The lighting does not transfer either: the map has 526 Blender lights, many of them area lights, which URP only supports baked.

## The method (`bake_room.py`)

The script runs on a room's source file, which it never saves. It works in stages so that each run fits a job limit:

1. **prep:** apply modifiers (bevels, weighted normals), turn curves and text into meshes, unwrap a `UVBake` layer per material, and size each atlas from the surface area. Saves `_work.blend`.
2. **bake:** one pass per run (`base`, `rough`, `normal`, plus `metal` and `emit` where a material has them). These bake the material only, not the scene lighting. Lightmaps are the last step, in Unity.
3. **finish:** write the URP Lit map set, swap in image-based materials, save `<room>_unity.blend`, export `<room>.fbx`, and write `materials.json`, `lights.json` and `bake_report.json`.

`render_compare.py` renders the room's own cameras on both files with the same lights and settings.

## Pilot result: cooling plant (`cooling-plant/`)

**Source and counts:** `sources/cooling-plant/module_aaa_A1.blend`, the AAA finish the map uses (unchanged). 1,570 meshes, 314,689 triangles after the modifiers, 23 materials: 18 procedural, baked; 5 constant, kept as values.

**Atlases:** 256 to 2048 px.

| Materials | Approximate density |
|---|---|
| Small equipment | 190 to 370 px/m |
| Mid-size surfaces (steel, cream paint, the floor) | 85 to 125 px/m |
| The largest surfaces: dark paint (577 m²), mineral walls (550 m²) | about 65 px/m |

**Bake settings and times:** 1 sample, AO and bevel node samples capped at 4. Base colour 31 min, roughness 29 min, normal 30 min, finish 18 s.

**Output** (54 maps in `textures/`):
- `_BaseMap` in sRGB;
- `_MetallicGlossMap`: metallic in R, smoothness (1 − roughness) in alpha;
- `_BumpMap`: tangent space, OpenGL +Y, as Unity expects.

**FBX re-import** in an empty Blender: same 1,570 meshes and 314,689 triangles, the same 23 materials, the same bounds to the millimetre. `UVBake` is the only UV layer, and all 54 textures are referenced.

**Comparison** (`compare/source_vs_baked.png`, five room cameras, Cycles, same lights): the baked room is nearly indistinguishable from the procedural one. The largest walls are slightly softer at close range.

**Not run:**
- An EEVEE real-time preview: there is no GPU or EGL in the container, so it could not start.
- A Unity import.

## Running it on the owner's PC (Ryzen 7 5800X, 32 GB, Radeon RX 9070 XT)

```powershell
powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_room.ps1 -Device GPU -Room cooling-plant `
    -Source sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend -Cameras C02_HERO,C06_EXCHANGER,C05_PUMP_A
```

`-Device GPU` or `-Device CPU` is required: you choose, and the scripts never pick a device or fall back (`../blender_device.py`). With GPU, Blender uses the first backend it finds, which is HIP for the RX 9070 XT. If it finds none, the run stops instead of using the CPU. `--profile home` bakes at 4K atlases and 8 samples, with the shader AO and bevel nodes at full quality. The stages run one after another; after a crash, `-From <stage>` continues. Bake times on this PC are not measured yet; `bake_report.json` records them. URP settings for this PC are in `URP_SETTINGS.md`.

### Every room in one run (`bake_all.ps1`)

```powershell
powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_all.ps1 -Device GPU
```

**What it bakes:** the twelve rooms the compact map uses, smallest first, from the same sources and collections as `build_compact_map.py`. Each room gets three comparison cameras.

**Left out:** the condenser bay, whose finish is being reworked.

**Before the first bake** it checks:
- Blender is found;
- the chosen device is found (`check_device.py`, which renders nothing);
- every source file is pulled from LFS.

**Logs:** one per room, in `_logs/<room>.log`.

**Options:**
- `-Only a,b` bakes only those rooms; `-Skip a,b` leaves them out.
- `-From <stage>` resumes the first selected room at that stage.

The run stops at the first failure.

**Source checks (2026-10-16):** every room source is self-contained except the spawn room. Its four PPE hero suits are collection instances linked from `sources/spawn-room/hero_suit.blend`. Prep now makes collection instances real and linked meshes and materials local, so the suits are baked. The medical and dock sources reference `blender/facility_environment.blend` (only a linked scene that nothing uses). Blender warns that it is missing, and nothing needs it.

**Outputs stay local**, because the repository's LFS quota is small. The 2K pilot made 82 MB of maps, and 4K atlases can be up to four times that.

## Speed fix: merge for the bake (2026-10-17)

**The problem:** on the owner's PC the cooling plant's base pass ran for about 2.5 hours, busy on the CPU rather than the GPU. Blender bakes the selected objects one at a time, and each object pays for its whole atlas: a 4K atlas is 16.7 M pixels, copied and margin-filled again for each of the 1,570 objects.

**The fix:** the bake stage now joins the room into a few meshes first. This is in memory only; the bake stage never saves `_work.blend`. Before joining, it stores what the shaders read per object:
- object coordinates as `_cs_obj`;
- generated coordinates as `_cs_gen`, which are also the default vector of the procedural textures;
- each object's render UV as `_cs_render_uv`.

Bevel and local-AO shader nodes only see their own object. So an object that uses them never shares a mesh with an object whose bounds touch its own.

**Room survey (all twelve rooms):** no Object Info, object-space transform or object-attribute nodes, and no mirrored objects.

**Prep change:** prep no longer makes `UVBake` the render UV. That had made image textures with no UV named sample through the bake UV, which mattered for image-textured rooms.

**`--merge off`** keeps the old path.

**Test** (cooling plant, container CPU with the owner's OK, 512 px atlases, 1 sample): 1,570 objects became 10 meshes in 2 s, with the same 314,689 triangles.

| Pass | Old | Merged | Speed-up |
|---|---|---|---|
| Base colour | 1,178 s | 17 s | 70× |
| Normal | 459 s | 12 s | 38× |

**Same output:**
- Materials without AO or bevel nodes came out pixel-identical, for example floor and wood with generated-coordinate noise.
- Materials with AO and bevel nodes differ from the old bake by less than two merged runs differ from each other with only the noise seed changed: a mean of 0.018 against 0.031. That difference is the 1-sample noise of those nodes, not a change in the look.

## Fix after the pilot: base colour (2026-10-16)

The first pilot's baked renders were 8 to 19 % darker than the source, worst on the pump motor. The cause was the base colour, which came from Cycles' DIFFUSE colour pass. That pass is scaled by (1 − metallic), and Unity then applies metallic again. Base colour and roughness are now baked by routing their own node inputs into an emission shader. That gives the true albedo. Measured again on the same five cameras, the baked room is within 0.6 to 1.5 % of the source's brightness, with a mean pixel difference of 0.7 to 1.4 % (it had been 8 to 19 % darker). On this CPU the new base-colour pass took 48 min, against 31 min before.

## Important: rooms as they are in the map

The pilot bakes the **room module**. The combined map changes rooms locally: door cuts, the mine's triangle cut, the turbine's skin, the animated ore cart and the evacuation additions. Those changes are not in the modules. Before the whole map goes to Unity, each room should be taken from `combined_map.blend` with its local changes made real, and baked from there. That is the next pipeline step, and it is not built yet.

## Importing into Unity URP (not done here)

1. **Project:** Unity 6000.4.3 with the URP package and a URP pipeline asset. `runtime/unity` is still Built-in; switching it needs an editor run.
2. **Copy the room in:** copy `cooling-plant/` into `Assets/`. On the FBX, set scale 1, *Generate Lightmap UVs* on, and Materials *None*.
3. **Materials:** create one URP Lit material per entry in `materials.json`:
   - `_BaseMap`;
   - `_MetallicGlossMap` with *Smoothness Source: Metallic Alpha*, and sRGB off on that texture;
   - `_BumpMap`, with the texture type set to Normal map;
   - for constant materials, the listed colour, metallic and smoothness values.

   An editor script that does this from the manifest is the obvious next step. It is Unity code, so it needs its own task.
4. **Lights:** recreate them from `lights.json`. Area lights are *Baked*, points and spots *Mixed*. Blender watts are not URP intensities, so tune them against `compare/*_source.png`, then bake lightmaps.

## Next, if the owner agrees

- Roll the same staged bake out to the other rooms. The cost is roughly 1.5 hours of baking per room of this size on this container.
- For the largest walls and floors, use tiling texture sets instead of unique atlases, since about 65 px/m is soft up close.
- Add the Unity editor script for `materials.json`.
