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
powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_room.ps1 -Room cooling-plant `
    -Source sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend -Cameras C02_HERO,C06_EXCHANGER,C05_PUMP_A
```

`--profile home` bakes on the GPU through HIP (the script picks the first backend Blender finds), at 4K atlases and 8 samples, with the shader AO and bevel nodes at full quality. The stages run one after another; after a crash, `-From <stage>` continues. Bake times on this PC are not measured yet; `bake_report.json` records them. URP settings for this PC are in `URP_SETTINGS.md`.

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
