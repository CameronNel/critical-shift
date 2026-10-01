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
| Render-visible geometry objects | 1,574 | 759 |
| Triangles | 352,462 | 352,462 |
| Draw-call estimate (objects x material slots, before any engine batching) | 1,918 | 762 |
| Materials in use | 249 | 31 (30 visible plus one untouched copy for animated labels; the 24-material spawn-room cap comes from the per-room budget in PR #59, branch `claude/eloquent-rubin-5y6lnu`, `design/MATERIAL_BUDGETS.md`, where the owner's approval of 2026-10-01 is recorded; that document is not on `main` yet) |
| Lights | 20 | 20 (the optimisation changes none, it only tags roles; the 20 are the 14 original lights, 4 baked locker strip lights and 2 baked doorway spill lights added by the hero and polish passes) |

Numbers reflect the module after the hero-suit pass (`../../blender/add_hero_suits.py`: the crew worker's own hazmat suit hung in each of the four PPE lockers) and the polish pass (`../../blender/polish_spawn.py`). The hero suit is **linked** into `module.blend` from `hero_suit.blend`; `optimise_spawn.py` first makes the linked instances local (`realize_instances.py`) so the derivative is self-contained (no library).

Every number below (objects, joins, conversions, draw calls, materials) comes from one run, recorded in
`optimise_report.json` next to this file.

## What it does (each step is meant to leave the look unchanged)

1. 315 curve/text objects become meshes (evaluated, with name, parent, collections, properties and children kept). Curve/text objects that are animated, driven, in NLA, constrained or have an animated data block or shape keys
   (for example the POD_state_* labels) are NOT converted, because a mesh copy would freeze them;
   modifiers are baked on 753 objects (the parts that get merged or touched).
2. Procedural patterns that depend on the object (Generated / Object coordinates, 40 materials) are frozen into per-vertex
   attributes `CS_GEN` / `CS_OBJ`, on every mesh including hidden ones, and those materials read the attributes, so joining
   parts cannot change a pattern. Curve/text objects that stay curves cannot carry attributes, so they keep an
   untouched copy of the material (`<name>__noattr`).
3. The 199 constant-colour Principled materials are folded into one `PAL_flat` material: three packed 16x16 float images
   (albedo, roughness+metal, emission), `Closest` sampling, a `CS_PAL` UV layer. Cell mapping is in text block `OPT_PALETTE`.
3b. **Material families** (the method of the reactor control room, PR #54; budgets in PR #59): materials with exactly the same node graph that differ only in
   constants become one `FAM ...` material. The constants (every differing socket value, and the two stop colours of each
   colour ramp) are written per polygon into colour attributes `FAM0..FAM3`; the family graph reads them. The graph is the
   same, so the shading is the same (the structural key includes the colour-ramp interpolation and colour mode, so ramps that differ never share a family): a 2-stop LINEAR/EASE ramp becomes a clamped Map Range (smoothstep for EASE) plus a Mix.
   Read-back of every attribute is checked at build time. 14 families replace 50 materials; members are listed in text block
   `OPT_FAMILIES`. Materials with different graphs are left alone.
4. Parts of the same asset that share material and object flags are joined (971 objects into 156); shell parts outside any
   asset are joined per collection, material and 5 m cell. Left exactly as they were: every object that is animated, has
   children, carries its own properties, is in a support-checked collection, is named by any `cs_support_target`,
   looks interactive (door, hinge, hatch, lever, button, handle, switch...) or belongs to an asset with
   moving-state properties. `OPT_MERGE_MANIFEST` lists which source objects went into each merged mesh.
5. Light roles written as custom properties only (`cs_rt_role`, `cs_rt_group`, `cs_rt_shadow`; 4 dynamic hall lights, 2 real-time
   shadow casters, the rest baked plus emissive); see `LIGHT_BUDGET.md`.

## Evidence

- `signature.py` / `compare_signatures.py` (per-member: every polygon of a family material is decoded back to the source material whose constants it carries, from text block `OPT_FAMILY_ROWS`; members with identical constants form one class; verified to fail when constants of one member are put on another member's faces): triangles identical; scene and per-asset bounding boxes within 0.1 mm; area per
  original material (palette cells decoded back) within 8e-6 relative; every world vertex of each file has a match in the
  other within about 2 mm; every object with properties, and every empty, keeps name, properties, transform and parent. PASS.
- Animation inventory, compared as a multiset: for every owner (objects, material node trees, meshes, curves, lights,
  cameras, worlds, shape keys) a digest of a generic deep dump of its whole animation data: owner settings and assigned
  slot, the action with all layers, slots, channelbags, F-curves (mute, keyframes, handles, easing), F-curve modifiers
  including collections such as envelope points, drivers (expression, variables, targets and their settings), and NLA
  tracks and strips (influence, timing, modifiers) with the content of each action they play. Verified to fail on a
  0.01 keyframe edit, muting an F-curve, an elastic-easing amplitude, a noise-modifier strength, an envelope point, NLA-only
  action edits, NLA influence, a driver target's rotation mode and a duplicated entry. A first version of this derivative
  lost the keyframes of
  `POD_state_READY` (an animated text object converted to a mesh); Codex's review of #60 caught this class of bug and the
  comparison now fails on it, and also fails if the derivative gains an action, driver or NLA entry the original did not have.
- `validate_contacts.py` on the derivative: PASS (208 tagged objects, 0 failures) on the post-polish module, same as the original (the count was 224 before the suit pass removed the belongings and added the hooks, docks and strip lights). (An earlier
  version of this script merged support targets and failed 48 of them; targets are now kept by name.)
- Render comparison (Cycles, 48 samples, denoised, fixed seed, 960x540) on six fixed validation cameras, original vs
  derivative; `renders/<camera>.png` shows before | after | difference amplified 6x:

  | Camera | mean abs diff | 99th percentile | pixels differing by more than 8% |
  |---|---:|---:|---:|
  | VALIDATE_Spawn | 0.0067 | 0.043 | 0.182% |
  | VALIDATE_LockerDoor | 0.0071 | 0.043 | 0.120% |
  | VALIDATE_BriefingDoor | 0.0087 | 0.051 | 0.297% |
  | VALIDATE_ExitReverse | 0.0060 | 0.039 | 0.096% |
  | VALIDATE_Hero_A | 0.0067 | 0.043 | 0.150% |
  | VALIDATE_Material_A | 0.0081 | 0.047 | 0.153% |

  The differences sit on edges (anti-aliasing and denoiser noise from a different object order); there are no
  colour or pattern shifts. Rendered again on the post-polish module (wear layer, doorway spill, reframed Material_A) and its regenerated derivative; I looked at the Hero_A montage (the linked suit, neck collar, dock and strip light match, differences on edges only); the other five were checked by the numbers only. This is a Cycles comparison, not engine rendering, and not art approval.

## Not done / not claimed

- No engine build or profiling: draw calls are a Blender estimate, not measured batches or frame time.
- 30 materials remain (visible; 31 in use counting the untouched copy for animated labels) against the room cap of 24 proposed in `design/MATERIAL_BUDGETS.md` on PR #59's branch (owner approval recorded there; not on `main` yet). The leftovers each have a one-off shader graph (locker steel,
  rubber, wood, bench timber, pressure metal, safety tread, glass, exposed plaster, V_ochre, the posters, TV screen,
  amber signal, the three floors and the suit visor glass `SUIT_glass`, a blended-alpha material taken as is from the player character, which is the one added by the hero pass), so merging them would change the look and needs owner approval. Texture memory (12 x 2K images, about 50 MP, including 4 displacement maps)
  is not reduced.
- Door, hatch and interaction assets, support-contact targets and anything with its own properties are intentionally
  left unmerged, which is why the count is 762 and not lower.
- The merged meshes are an export-oriented derivative: authoring edits belong in `module.blend`.
