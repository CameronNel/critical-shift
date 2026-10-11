# Medical reanimation baked materials: handoff for the engine import

Unreviewed derivative of `../module_overhaul_R2.blend` (the room is "done and dusted"; its status is
unchanged). The source module is not modified. Built with Blender 5.2.2 LTS using `../bake/`.
Nothing here has been imported into Unity or Unreal; no engine output has been seen.

## Pull only these files
```sh
git lfs install --local
git lfs pull --include="sections/facility-assembly/sources/medical-reanimation/baked/**"
```
Do not run a full LFS pull and do not use a broad sparse checkout (see `AGENTS.md`).

## Files
| Path | Contents |
|---|---|
| `module_baked_B1.blend` | The room with 1,090 objects bound to 8 baked materials `MED_BAKED_A0`..`A7`. Modifiers are applied on those objects. Maps are packed. Object custom property `bake_atlas` gives the atlas. Plain single-colour materials (glass, lenses, phosphor, solid enamels) keep their original material. |
| `bake_groups.json` | Object name to atlas index (0 to 7), plus per-atlas object counts and average px/m. |
| `maps/med_aK_albedo.png` | Base colour, sRGB, 2048 x 2048. |
| `maps/med_aK_rm.png` | Packed: R = roughness, G = metallic. Linear. |
| `maps/med_aK_normal.png` | Tangent-space normal, +Y up (OpenGL, same as Unity). Linear (Non-Color). |
| `unity/med_aK_metal_smooth.png` | Unity Standard layout: R = G = B = metallic, A = smoothness = 1 - roughness. Linear: import with sRGB off. |

Atlases 0 and 1 are the room shells (floor, ceiling, walls; about 120 px/m). Atlases 2 to 7 are props cut into slabs along the
room's long axis (150 to 185 px/m). Prop normal maps are almost flat because the source bumps are 0.2 to 1 mm; the shell normals carry detail.

## What the engine import must do
1. Use UV layer `BAKE` (not `UVMap` / `MED_Physical_1m`) as the texture UVs of every object that has a `bake_atlas`. UV0 is the original layout and is left untouched. In FBX, make `BAKE` the first UV set or map it explicitly.
2. Replace the procedural material on each such object with one engine material per atlas, using the three maps above. Materials with a single flat colour keep their own values.
3. Faces on the outer side of floor, ceiling and walls are parked on a junk texel at about (0.9985, 0.9985); they are not visible from inside the room.
4. Floor clear-coat is not baked; add a reflection or clear-coat setting in the engine if wanted.

## What was checked, and what was not
* Blender only: a baked-only render versus the original, same camera (`CAM_ENTRY`, 854x480, 64 samples): mean difference 1.4/255, 99% of pixels within 8 levels, no more isolated outlier pixels than the original. Method and noise measurements: `../bake/README.md`.
* Not checked: any engine import or render, `CAM_HERO` from baked materials, close-range seams, collision, performance, or engine lighting and post-processing.

## Suggested prompt for Codex
> Read `sections/facility-assembly/sources/medical-reanimation/baked/HANDOFF.md`. Pull only the baked folder. Extend the map export so the medical-reanimation room uses `module_baked_B1.blend` (UV layer `BAKE`, the eight `MED_BAKED_A*` materials) instead of its procedural materials, import the maps from `baked/unity/` and `baked/maps/` with the colour spaces given there, and compare the result with the Blender renders. Report what you ran and what you did not, including how it looks.
