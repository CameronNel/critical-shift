# Medical reanimation: material bake (derivative, unreviewed)

Separate derivative of `module_overhaul_R2.blend`. The room module is not modified and its
"done and dusted" status is unchanged. Nothing here is reviewed or accepted.

## What it produces
Eight 2K atlases (two for the room shells, six for props cut into slabs along the room), each with
three maps: albedo (sRGB), packed roughness (R) and metallic (G), tangent-space normal. 24 maps,
48 MB as PNG. 1,090 objects, 1,241 procedural material slots replaced by 8 baked materials.
Plain single-colour materials (glass, lenses, phosphor, solid enamels; 60 slots) are left alone.
No light, shadow or ambient occlusion is baked. UV0 is untouched; the bake uses a second UV layer `BAKE`.
The maps, a Unity-layout repack, the baked scene `module_baked_B1.blend` and a handoff note are committed (Git LFS) in `../baked/`; see `../baked/HANDOFF.md`.

## Commands (Blender 5.2.2 LTS, CPU)
1. `med_bake_prep.py -- --out PREP.blend --atlases 8` (about 45 s)
2. `med_bake_run.py -- --out MAPS --atlas K --maps albedo rm normal --samples 32 --seed 1 --prune 0.1` for K = 0..7
3. `med_bake_preview.py -- --maps MAPS --out RENDERS --cams CAM_ENTRY --samples 64 [--save BAKED.blend]`

## Why the bakes are not spotty (measured)
* Channels are baked deterministically through a temporary emission route; flat surfaces have zero noise.
* Only the edge-wear shaders are stochastic (Bevel and ambient-occlusion nodes). A 64-sample and a
  16-sample bake of one atlas with different seeds differ by RMS 2.64/255, which puts the 64-sample
  noise at about 1.2/255; the delivered bake uses 32 samples (estimated about 1.7/255).
* Islands are unique and non-overlapping with an 8 px gap, 4 px dilation, and unseen shell faces parked on a junk texel.
* Baked-only render versus the original, same camera (CAM_ENTRY, 854x480, 64 samples): mean difference
  1.4/255, 99% of pixels within 8 levels, 0.9% above 8 levels, and isolated outlier pixels no more common
  than in the original (0.85% vs 1.12%).

## Costs and limits
* Texel density: shells about 120 px/m, props 150 to 185 px/m. Soft in close-ups.
* Bake time on 4 CPU cores: about 3 hours for all 24 maps. Blender runs one bake job per object (about 2 s each);
  the occlusion nodes reach only 4.5 to 8 cm, so objects farther than 10 cm from an atlas are hidden during its bake.
* Prop normal maps are near flat because the source bumps are tiny (0.2 to 1 mm); the shells carry real normal detail.
* Floor clear-coat weight is not baked (engines differ); the preview does not reproduce it.
* The preview is a Blender render of baked-only materials with the room's authored lights and Cycles
  global illumination. It is a stand-in, not an engine screenshot: no engine lighting, post-processing or shader
  differences are modelled, and real Unity/Unreal output has not been run.
* CAM_HERO (the chamber) was not previewed from baked materials; only CAM_ENTRY was.
