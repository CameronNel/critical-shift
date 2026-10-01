# Spawn room delivery optimisation (look-preserving derivative)

`module_optimised.blend` (next to `module.blend` in `sections/facility-assembly/sources/spawn-room/`) is a **separate
delivery derivative**. The approved `module.blend`, `accepted.blend`, the assembled map and `SOURCES.json` are not touched.
Nothing here is promoted; swapping it into the map is a separate reviewed PR (see `MAP.md`).

Regenerate with Blender 5.2 (the module is a 5.2 file; the `bpy` wheel on PyPI is only 5.0.1):

    blender -b --factory-startup -P optimise_spawn.py -- <module.blend> <module_optimised.blend> [report.json]
    blender -b --factory-startup -P signature.py -- <module.blend> before.json       # then the same on the derivative
    python compare_signatures.py before.json after.json
    blender -b <module_optimised.blend> --python ../../blender/validate_contacts.py  # run a copy so it does not overwrite production/
    blender -b -P render_cams.py -- <module.blend> <dir>   # fixed VALIDATE_* cameras; same for the derivative; then diff_renders.py

## Measured (Blender evaluated meshes, same method before and after; not engine-measured)

| | module.blend | module_optimised.blend |
|---|---:|---:|
| Render-visible geometry objects | 1,572 | 788 |
| Triangles | 322,722 | 322,722 |
| Draw-call estimate (objects x material slots, before any engine batching) | 1,878 | 804 |
| Materials in use | 189 | 62 |
| Lights | 14 | 14 (unchanged; roles tagged) |

## What it does (each step is meant to leave the look unchanged)

1. 351 curve/text objects become meshes (evaluated, with name, parent, collections, properties and children kept). Curve/text objects that are animated, driven, in NLA, constrained or have an animated data block or shape keys
   (for example the POD_state_* labels) are NOT converted, because a mesh copy would freeze them;
   modifiers are baked on the parts that get merged or touched.
2. Procedural patterns that depend on the object (Generated / Object coordinates, 40 materials) are frozen into per-vertex
   attributes `CS_GEN` / `CS_OBJ`, on every mesh including hidden ones, and those materials read the attributes, so joining
   parts cannot change a pattern. Curve/text objects that stay curves cannot carry attributes, so they keep an
   untouched copy of the material (`<name>__noattr`).
3. The 129 constant-colour Principled materials are folded into one `PAL_flat` material: three packed 16x16 float images
   (albedo, roughness+metal, emission), `Closest` sampling, a `CS_PAL` UV layer. Cell mapping is in text block `OPT_PALETTE`.
4. Parts of the same asset that share material and object flags are joined (957 objects into 173); shell parts outside any
   asset are joined per collection, material and 5 m cell. Left exactly as they were: every object that is animated, has
   children, carries its own properties, is in a support-checked collection, is named by any `cs_support_target`,
   looks interactive (door, hinge, hatch, lever, button, handle, switch...) or belongs to an asset with
   moving-state properties. `OPT_MERGE_MANIFEST` lists which source objects went into each merged mesh.
5. Light roles written as custom properties only (`cs_rt_role`, `cs_rt_group`); see `LIGHT_BUDGET.md`.

## Evidence

- `signature.py` / `compare_signatures.py`: triangles identical; scene and per-asset bounding boxes within 0.1 mm; area per
  original material (palette cells decoded back) within 8e-6 relative; every world vertex of each file has a match in the
  other within about 2 mm; every object with properties, and every empty, keeps name, properties, transform and parent. PASS.
- Animation inventory, compared as a multiset of content digests (F-curves with every keyframe and handle, drivers with
  expressions and targets, NLA tracks and strips; verified to fail on a 0.01 keyframe edit and on a duplicated entry) (every object, material node tree, mesh, curve, light, camera, world and shape key with an action,
  drivers or NLA tracks) is identical in both files. A first version of this derivative lost the keyframes of
  `POD_state_READY` (an animated text object converted to a mesh); Codex's review of #60 caught this class of bug and the
  comparison now fails on it, and also fails if the derivative gains an action, driver or NLA entry the original did not have.
- `validate_contacts.py` on the derivative: PASS (224 tagged objects, 0 failures), same as the original. (An earlier
  version of this script merged support targets and failed 48 of them; targets are now kept by name.)
- Render comparison (Cycles, 48 samples, denoised, fixed seed, 960x540) on six fixed validation cameras, original vs
  derivative; `renders/<camera>.png` shows before | after | difference amplified 6x:

  | Camera | mean abs diff | 99th percentile | pixels differing by more than 8% |
  |---|---:|---:|---:|
  | VALIDATE_Spawn | 0.0057 | 0.039 | 0.081% |
  | VALIDATE_LockerDoor | 0.0060 | 0.035 | 0.077% |
  | VALIDATE_BriefingDoor | 0.0079 | 0.043 | 0.190% |
  | VALIDATE_ExitReverse | 0.0053 | 0.035 | 0.055% |
  | VALIDATE_Hero_A | 0.0056 | 0.035 | 0.084% |
  | VALIDATE_Material_A | 0.0039 | 0.024 | 0.003% |

  The differences sit on edges (anti-aliasing and denoiser noise from a different object order); there are no
  colour or pattern shifts. I looked at the montages for Spawn and BriefingDoor; the other four were checked by the
  numbers only. This is a Cycles comparison, not engine rendering, and not art approval.

## Not done / not claimed

- No engine build or profiling: draw calls are a Blender estimate, not measured batches or frame time.
- 60 textured/procedural materials remain. Getting to the 40-material target means baking those to shared texture sets,
  which changes the look and needs owner review. Texture memory (12 x 2K images, about 50 MP, including 4 displacement maps)
  is not reduced.
- Door, hatch and interaction assets, support-contact targets and anything with its own properties are intentionally
  left unmerged, which is why the count is 804 and not lower.
- The merged meshes are an export-oriented derivative: authoring edits belong in `module.blend`.
