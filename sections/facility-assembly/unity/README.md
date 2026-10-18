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
2. **bake:** one pass per run (`base`, `rough`, `normal`, plus `metal`, `emit` and `mask` where a material needs them). These bake the material only, not the scene lighting. Lightmaps are the last step, in Unity.
3. **finish:** write the URP Lit map set, swap in image-based materials, save `<room>_unity.blend`, export `<room>.fbx`, and write `materials.json`, `lights.json` and `bake_report.json`.
4. **check** (`bake_check.py`): stops the run if the room's output is wrong (see *Review and fixes, 2026-10-18* below).

`render_compare.py` renders the room's own cameras on both files with the same lights and settings.

## Review and fixes, 2026-10-18 (before any further bake)

The map bake of 2026-10-17/18 was stopped after the isolation bug (below). Before baking again, two independent reviews read every script, and the pipeline was fixed and rehearsed end to end. What was wrong in every bake made before this date:

| Problem | Effect in the old bakes | Fix |
|---|---|---|
| Only the first Principled BSDF was baked | Emission strips mixed into the turbine's architecture (M_ARCH, M_MACH, M_PROPS, M_SHAFT), the front-end screens and the connectors' emissive (Add shader) were lost; Mix-with-Transparent materials (refinery traffic paint, wall leak, condensate) came out as opaque sheets | The whole shader tree (Mix and Add of Principled, Emission, Transparent, Glossy, Glass, ...) is rebuilt per channel from Emission shaders and baked; a `mask` pass bakes alpha, reflective weight and coverage, and the finish divides them out |
| Emission baked into an 8-bit image | Clipped at 1 (lamps reach 45: the mine's lanterns, 35 reactor materials) and normalised in gamma space | Emission bakes to float EXR; the map is colour / linear peak, and the peak is the URP intensity |
| Baked materials never transparent | 47 decal, glass and film materials (the front end's 34 wear decals, reactor paint and puddle films) exported opaque | Alpha goes into the base map's alpha; the importer sets those materials Transparent |
| A Python error in Blender exited 0 | A failed stage looked like a pass; finish could use stale maps | Every Blender call passes `--python-exit-code 1`; finish stops when a planned map is missing; prep clears `_raw/`; plans carry a version |
| Nothing checked what rendered | The isolation bug ran 12 hours unseen | Prep, every bake pass and finish stop if anything outside the room renders; the `check` stage re-checks the output |
| Missing images bake magenta silently | The turbine's 23 textures are external LFS PNGs; a pull of the .blend files alone leaves them as pointers | Prep stops on any image without pixels; `bake_all.ps1` checks the PNGs before starting; the handover pulls them |
| `-Cameras ""` (map-connections) | Windows PowerShell 5.1 drops the empty argument: the 13th piece could not start | The argument is only passed when non-empty |
| Smaller | Hidden lights in `lights.json`; area-light size without object scale; pure-emission surfaces glossy; constant shader mixes flattened; `-From` case-sensitive; compare silently skipped a missing camera | All fixed |

Importer: transparency for baked materials (base map alpha kept on import), the map scene updated in place instead of recreated (lightmaps and hand edits survive), the renderer's post-processing data assigned, ellipse lights as same-area rectangles, unique material file names, and the FBX reimported only when a remap changed.

**Proof before the GPU run.**
- A synthetic scene with known values (a Principled/Emission strip, Transparent/Principled cutout, alpha-linked decal, an emission-45 lamp, Add shader, pure emission, a constant mix, an object-space-normal material, glass, a hidden light) is baked through the real runner; 32 numeric checks of the URP maps pass (base colour, smoothness, metallic, alpha, emission x intensity within 1 to 3 %).
- Failure paths stop the runner: a broken plan (uncaught Python error), a missing raw map, a deleted texture and an emptied `lights.json` each end the run with a non-zero exit.
- The rehearsal (below) runs all 13 map pieces through every stage.

**Found by the rehearsal and fixed (2026-10-18):**
- **Glass read as frosted.** Transmission glass became a 25 % white overlay (the dock's windows and hatch looked milky). Now clear glass bakes with no diffuse (transmission has none) at alpha 0.1 and imports with URP's *Preserve Specular* blend: the background shows through at 90 % and reflections stay whole. Decals and films keep the plain alpha blend.
- **The new check's own false alarms**, made precise: clear glass is black by design; a text object's own geometry is not an instance; Blender's FBX importer drops a trailing `.5` from a material name (the FBX keeps it, and the Unity importer now matches either way).
- **Not fixable by a bake, listed in the log:** view-dependent shading (Layer Weight, Fresnel, Light Path) bakes as seen head-on. The turbine's blue rim glow on M_ARCH, M_MACH, M_PROPS and M_SHAFT (Emission mixed in by Layer Weight *Facing*) is lost; URP Lit has no rim term, so bringing it back needs a small custom shader (owner's call).
- **Expected differences in the comparison renders:** Cycles does not trace light through glass by default, so in the source renders glass casts dark shadows (the dock's counter and speaker ring); URP's transparent glass casts none, like the baked renders. The 256 px rehearsal atlases also soften fine detail (sign text, wet-floor highlights).

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

## Map mode: rooms as they are in the map (2026-10-17)

**Why it exists.** The first whole run (below) baked each room from its own room file, so it lacks everything the combined map changes:
- the cut walls and patches that open the doorways (about 650 map-side objects);
- the slimmed mine;
- the turbine's skin;
- the ore cart;
- the connectors, stairs, signs and evacuation road, which exist only in the map.

**`bake_all.ps1 -Map`** bakes each room from `combined/combined_map.blend` instead. It bakes the `ROOM_<room>_members` collection, the map's own membership of that room with the edits applied, in the room's frame.

`bake_room.py --isolate` handles the map file:
- it links that collection into the scene;
- it excludes everything else, so neighbouring rooms neither bake nor shade it;
- linked objects, meshes, materials and node groups are made local.

**Output:**
- Each room goes to `unity/map/<room>`.
- One more piece, `map-connections`, holds the connector, stair, escape and sign collections and the evacuation road. It is baked in the map frame.
- Comparison renders: map mode compares the map room before baking (`_work.blend`) with the room after baking. Both share the map's world and render settings; the room file only lends its review cameras, which the map's room collections do not carry.
- End-to-end test, turbine, on the container CPU with the owner's OK, at 256 px and 1 sample: every stage ran (prep, five bake passes, finish, FBX of 9.7 MB, 28 materials, 59 lights) in 16.5 minutes. Before baking the map room measured a mean brightness of 14.9; after baking, 15.4 (mean pixel difference 6/255). The map lights the turbine darker than its own file does, so comparing against the room file would mislead.

**Placement.** `map_placement.py` reads the map's `ROOM_<room>` instancers, including the collections' instance offset, into `map/map_placement.json`. It is committed, and it needs re-running when the layout changes.

**Check:** every instanced object in the map, put through the importer's rule, lands where the map shows it. Across 20,620 objects in 13 rooms the error is under 1 cm. The rule is: the prefab goes at Blender `(x, y, z)` → Unity `(-x, z, -y)`, and a Z rotation r becomes a Y rotation of -r. The 32 hero-suit parts are instances inside instances, so the check measured them from the suit file's own origin; the bake makes them real objects.

**Isolation bug, found 2026-10-18 (PR #110).**
- **The bug:** `isolate()` set `exclude` through `LayerCollection` references it already held. Each exclude rebuilds the view layer, so the exclude on `COMBINED_MAP` was lost. Every map bake scene still held the map's 13 room instancers: 20,653 objects, 7.9 M triangles and 60 lights.
- **What it did:** passes ran about 10× slower (cooling plant base, 23 min instead of 2), and other rooms shaded each room through its AO nodes. In the turbine's case, 751 condenser objects sat inside its bake box.
- **Fix:** fresh lookups, a check afterwards, and stray objects hidden.
- **After the fix:**
  - turbine: 60 meshes, 0 instances, 416,510 triangles;
  - connections: 446 meshes, 0 instances, 30,490 triangles;
  - room mode: unchanged.
- **Re-bake needed:** the 8 map rooms baked before the fix must be baked again.

**Shakedown, 2026-10-17:** map-mode prep plus the merge step ran on all 13 pieces in the container. It renders nothing, so no device was used. Every piece passed:

| Piece | Objects | Triangles | Merged meshes |
|---|---|---|---|
| turbine-room | 60 | 416,510 | 6 |
| fuel-corridor | 255 | 1,120,559 | 1 |
| mine (the map's slim version) | 167 | 765,429 | 1 |
| cooling-plant | 1,572 | 314,699 | 10 |
| waste-storage | 2,111 | 352,300 | 11 |
| compliance-dock | 1,143 | 397,976 | 12 |
| medical-reanimation | 1,379 | 507,648 | 9 |
| spawn-room | 1,670 | 312,534 | 1 |
| electrical-room | 3,037 | 579,699 | 1 |
| front-end-area | 2,161 | 743,496 | 9 |
| refinery (with the ore cart) | 2,815 | 390,384 | 14 |
| reactor-room | 1,644 | 1,115,902 | 21 |
| map-connections | 446 | 30,490 | 3 |

Every merge kept every triangle. The reactor comes from `sections/reactor-room/blender/reactorroom.blend`, which is the newest version: the reviewed refined hall of PRs #96 and #100. No branch or open PR holds a newer one.

**Unity:** *Critical Shift > Rooms > Import Baked Map (all rooms in place)* imports `unity/map/*` into `Content/Rooms/map/` and saves the scene `Content/Rooms/map/CriticalShift_Map.unity`, with every piece placed.

**Left out:** the condenser bay, which is being reworked, so the space under the turbine is empty.

## Whole-map bake on the owner's PC, from the room files (2026-10-17)

**Setup:** commit `ac624fd`, Blender 5.2.2 LTS, on the GPU (HIP, RX 9070 XT), `--profile home`, run by `bake_all.ps1`. The local agent reported the run; these files are not in the repository.

**Result:** all twelve rooms finished, and all 36 comparison pairs were rendered.

| Room | Objects | Triangles | Lights | Bake passes (min) | Total (min) | Textures (MB) | 4K atlases |
|---|---|---|---|---|---|---|---|
| cooling-plant | 1,570 | 314,689 | 15 | 6.0 | 11.2 | 207 | 5 |
| waste-storage | 2,075 | 351,868 | 19 | 8.0 | 16.1 | 246 | 7 |
| turbine-room | 16 | 416,472 | 61 | 2.1 | 3.8 | 18 | 8 |
| fuel-corridor | 263 | 1,132,567 | 22 | 3.7 | 21* | 160 | 15 |
| electrical-room | 3,037 | 580,219 | 18 | 2.6 | 14.7 | 158 | 8 |
| compliance-dock | 1,145 | 398,352 | 26 | 10.7 | 23.6 | 211 | 6 |
| medical-reanimation | 1,261 | 491,012 | 19 | 7.2 | 15.8 | 204 | 5 |
| refinery | 2,690 | 376,036 | 21 | 15.0 | 35.3 | 378 | 12 |
| front-end-area | 2,229 | 799,874 | 75 | 36.2 | 50.3 | 687 | 32 |
| spawn-room | 1,574 | 352,462 | 6 | 3.0 | 16.2 | 368 | 10 |
| reactor-room | 1,763 | 1,174,433 | 105 | 50.8 | 59* | 809 | 34 |
| mine | 168 | 3,740,342 | 67 | 8.7 | 21.1 | 767 | 19 |
| **Total** | **17,791** | **10,128,326** | **454** | | **about 3.6 h** | **4,212** | **161** |

\* Runs resumed after a fix; the total is prep plus the resumed run.

**Where the time goes now:**
- **Prep:** UV unwrapping on the CPU takes 3 to 22 minutes per room, now usually the longest stage.
- **The rooms with the most 4K atlases** (front end 32, reactor 34) take 11 to 16 minutes per bake pass.

**What it means for Unity:**
- **Texture budget.** At full resolution the baked maps need about 13 GB of GPU memory: 161 materials × 3 maps at 4K, BC7/BC5 with mips, is about 11 GB, and the 2K atlases add about 2 GB. Mip streaming (a 2 GB budget in `URP_SETTINGS.md`) keeps what is resident within the 16 GB card. The build size and lower-end PCs will still need tiling texture sets for the largest walls and floors, or a lower density, before release.
- **The mine** comes from its room module at 3.74 M triangles and a 116 MB FBX. The map's decimation, cutting it to about 0.79 M, is applied only inside the map. It needs an LOD or decimation step before it goes into the game.
- **Fixes during the run:**
  - Windows-safe file names (`FC | bed`);
  - non-Principled materials become constants (the reactor's water is a transparent constant);
  - render-hidden collections are skipped (the mine's CC0 source meshes).

  Each fix applies to every room baked after it.

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

## Importing into Unity URP: `Critical Shift > Rooms`

The importer lives in `runtime/unity/Assets/CriticalShift/Content/Editor/`. It is editor-only and described in its `README.md`.

**Once per project:**
1. Open `runtime/unity` in Unity 6000.4.3.
2. Install URP: *Window > Package Manager > Unity Registry > Universal RP > Install*.
3. Run *Critical Shift > Rooms > Set Up URP*. It switches the project to Linear colour and creates and assigns a URP pipeline asset in `Assets/CriticalShift/Content/Rendering/`. If that automatic step fails, the message gives the two manual clicks.
4. Tune the pipeline asset per `URP_SETTINGS.md`.

**Each time rooms are baked:** run *Critical Shift > Rooms > Import All Baked Rooms*. It reads every baked room folder here (each has `materials.json`, `<room>.fbx` and `textures/`) and, for each room:
1. copies the FBX, the textures and the manifests into `Assets/CriticalShift/Content/Rooms/<room>/`. That folder is git-ignored and regenerated. Unchanged files are skipped.
2. applies the import settings:
   - textures: `_BaseMap` and `_EmissionMap` as sRGB BC7; `_MetallicGlossMap` as linear BC7 with alpha; `_BumpMap` as a normal map in BC5; all at 4096 with mip streaming;
   - FBX: scale 1, axis conversion baked, Generate Lightmap UVs, tangents calculated with MikkTSpace, no cameras, lights or animation.
3. builds one URP Lit material per `materials.json` entry:
   - smoothness from the metallic map's alpha, normal and emission keywords set;
   - constant materials from their values; transparent ones as alpha blend.

   It then remaps the FBX's `U_<name>` materials to them.
4. recreates the lights from `lights.json`:
   - area lights are Baked; points and spots are Mixed;
   - the Blender frame `(x, y, z)` becomes Unity `(-x, z, -y)`;
   - starting intensities are P/(4π²) for points and spots, P/(π²·area) for area lights, and S/π for a sun.
5. saves `Rooms/<room>/<room>.prefab`: the model, flagged static for GI, occlusion and reflection probes, plus its lights, at the room's own origin.

Batch mode, for a scripted run: `Unity -batchmode -projectPath runtime/unity -executeMethod CriticalShift.Content.Editor.BakedRoomImporter.ImportAllBatch -quit`.

**Not done by the importer:**
- placing rooms where the map puts them (each prefab sits at its module origin);
- colliders;
- lightmap baking;
- the AgX colour LUT.

**Light intensities are unit-matched, not calibrated.** Compare each room against `compare/*` and adjust the lights. Blender's AgX view transform and URP's tonemapper also differ.

## Next, if the owner agrees

- Roll the same staged bake out to the other rooms. The cost is roughly 1.5 hours of baking per room of this size on this container.
- For the largest walls and floors, use tiling texture sets instead of unique atlases, since about 65 px/m is soft up close.
