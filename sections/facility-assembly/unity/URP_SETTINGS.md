# URP settings for the owner's PC (Radeon RX 9070 XT 16 GB, Ryzen 7 5800X, 32 GB)

**Status:** proposed, 2026-10-16. Nothing here has been tested in Unity; there is no editor in the agent environment.

**Who this is for:** the "High" quality tier, set for the owner's PC at 1440p. It is the PC the map is built and baked on. Players' minimum spec is a separate decision: `design/ENGINE_DECISION.md` asks for low defaults. So keep a "Low" tier as well, and treat this as the top one.

**Measure, then adjust.** These are starting values. Settle them with the Unity Profiler and Frame Debugger on the real map, aiming for 144 fps at 1440p in the busiest room (currently the reactor hall).

## Scale of the job

The map is:
- 8.7 M triangles;
- about 22,000 objects;
- 526 Blender lights;
- 13 rooms, each with roughly 80 MB of baked texture maps as PNG. In the GPU's compressed formats that is far less.

A 9070 XT can draw that much geometry comfortably. The real risks are draw calls (22k objects) and light count. Every choice below is aimed at those two.

## URP asset (High)

| Setting | Value | Why |
|---|---|---|
| Rendering Path | **Forward+** | Many lights per object (the rooms have 15 to 117 lights each); needed for the GPU Resident Drawer |
| GPU Resident Drawer | **Instanced Drawing** | Unity 6. Turns 22k static objects into a few GPU-driven draws, which is the biggest single win for this map |
| GPU Occlusion Culling | On | Rooms hide each other; walls are thick |
| SRP Batcher | On | |
| Static batching | Off (the GPU Resident Drawer replaces it) | |
| HDR | On, 32-bit (R11G11B10) | |
| Anti-aliasing | TAA, quality High; or MSAA 4x if TAA ghosting shows on moving carts | Forward+ supports both |
| Upscaling | Off at 1440p; STP at 4K | |
| Render scale | 1.0 | |
| Main light shadows | 4096, 4 cascades, distance 80 m | One sun for the yard; interiors use local lights |
| Additional light shadows | Atlas 4096, Soft Shadows **High**, up to 32 shadowed lights in view | Spot and point lamps |
| Light cookies | Atlas 2048 | |
| Reflection probes | Blending **on**, Box Projection **on** | Wet floors and steel need probes; URP has no screen-space reflections |
| Depth and Opaque textures | On | Needed for SSAO and the glass |

## Renderer features and post-processing

| Feature | Value |
|---|---|
| Screen Space Ambient Occlusion | On. Method Interleaved Gradient, intensity 0.6, radius 0.3, full resolution, After Opaque off |
| Decals | Off unless a room needs them |
| Tonemapping | **Neutral**, plus a colour-lookup LUT exported from Blender's AgX view. The LUT is still to do: it renders a colour strip through AgX, so Unity matches the look of the Blender renders. |
| Bloom | Threshold 1.0, intensity 0.3 (lamps and emissive signs) |
| Film grain, chromatic aberration | Off |

## Lighting

| Item | Setting |
|---|---|
| Lightmapper | Progressive **GPU** (runs on AMD) |
| Lightmap resolution | 20 texels per metre for rooms, 40 for hero areas (the reactor and the cafeteria) |
| Directional mode | Directional |
| Lightmap compression | High quality |
| Texture size | 4096 |
| Area lights | Baked. URP has no realtime area lights; `lights.json` marks them. |
| Spot and point lights | Mixed: realtime direct light and shadows for players, baked bounce |
| Light probes | **Adaptive Probe Volumes** (Unity 6), so players and carts get the baked light |
| Volumetric haze | Not in URP. Leave it out, or add a fog volume later (a separate decision). |

## Textures (import settings for the baked maps)

| Map | Compression | sRGB | Notes |
|---|---|---|---|
| `_BaseMap` | BC7 | On | |
| `_MetallicGlossMap` | BC7 | **Off** | Smoothness is in the alpha channel |
| `_BumpMap` | BC5 | Off | Texture type Normal map |
| `_EmissionMap` | BC7 | On | |

- **For all maps:** mipmaps on, max size 4096, Mipmap Streaming on with a 2 GB budget. That leaves room in 16 GB.

## FBX import

| Setting | Value |
|---|---|
| Scale | 1 |
| Convert Units | On |
| Read/Write | Off |
| Mesh Compression | Off |
| Generate Lightmap UVs | **On** (`UVBake` is uv0 and is not a lightmap layout) |
| Normals | Import |
| Tangents | Calculate Mikk |
| Materials | None (built from `materials.json`) |
| Static flags on room objects | Contribute GI, Occluder Static, Occludee Static, Reflection Probe Static |

## What the bake uses on this PC

`bake_room.ps1 -Device GPU` runs `bake_room.py --profile home --device GPU`. The device is always the one you name; nothing falls back. The profile adds:
- 4K atlases;
- 8 samples;
- the shader AO and bevel nodes at full quality.

The 4-core cloud container could not afford that last setting: there the AO and bevel nodes were capped at 4 samples and atlases at 2K. Bake times on this PC are not measured yet. `bake_report.json` records them per stage after the first run.
