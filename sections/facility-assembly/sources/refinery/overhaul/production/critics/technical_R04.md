# R04 Blender technical audit

**Scope:** Read-only audit of `checkpoints/R04.blend`, `build_overhaul.py`, `revision_R04.py`, `validate_overhaul.py`, `build_R04.json` and `validation_R04.json`. Blender 5.2 opened the checkpoint in background with `--disable-autoexec`; no source, checkpoint or render was saved or changed. The checkpoint and additive candidate are byte-identical (11,881,465 bytes; SHA-256 `cebbc6255812dfc363f501e496fd066c064efa89cda38c316bb340586a669497`), matching the recorded build hash.

## Finding: unresolved inherited support contacts do not fail validation

`validation_R04.json` reports 156 legacy support screens as PASS and four as `UNRESOLVED`, but the top-level status remains PASS with an empty `issues` list. The four records are `CSM_Cart_wheel`, `.002`, `.003`, and `.004`, all marked `support_dependent`; each is an EMPTY parented to `AUTHENTIC_GULLET_CART`, with a nominated `Tip_cradle_rail` target and `LOCAL_-Z` direction. The legacy screen in `validate_overhaul.py` only maps `WORLD_*` directions, appends `UNRESOLVED` for unsupported/missing contracts, then continues without adding an issue (lines 49–56). These empty anchors have point bounds, so their support cannot be cleared by the current bounding-face sample either.

This does **not** establish that the cart is floating. The follow-up geometry check found the correct nested support anchors and verified contact; see the supplement below. The report still overstates what its own four `UNRESOLVED` entries mean, and unresolved contracts in general do not fail the summary. Use the nested anchor evidence for these four contacts and make any genuinely unresolved record fail overall validation.

## Measured checks that passed

- The recorded validation shows 29 protected shell/port interfaces unchanged, world strength `0.0`, no missing used images or linked libraries, 43/43 new explicit support anchors passing, and no obstruction in the 15 sampled primary-aisle ray checks. It reports 273,452 evaluated triangles across 2,382 visible mesh objects.
- Direct checkpoint inspection found 18 area lights, each linked to a named physical lens, all within the room bounds. The recorded light checks place all sources within 21 mm of their registered fixture lenses. The scene has no external image or library dependencies.
- R04's grouped crusher-console edit snapshots world matrices and applies the same transform in parent-depth order. The new selector/emergency decorations are parented to their corresponding interactive buttons, but their authored button-local offsets are lost; see the geometry supplement.
- No source builder or validator was replayed: the validator writes `validation_<revision>.json`, and the build script writes the candidate and build evidence. This audit therefore does not claim a fresh build or a fresh validation run.

## Scope limits

The validator explicitly says its anchors and inherited bounding-face screens are not exhaustive self-intersection, buried-volume or runtime-collision certification. Its aisle result samples five lateral positions at three heights over a 2.72 m ray distance; it is not a full swept-volume clearance test. The read-only audit did not run an exhaustive mesh-pair intersection or collision analysis. These limits are material to any technical score or acceptance claim.

**Disposition:** The four wheel-to-rail contacts are physically verified below, but the stored validator output still marks them unresolved and returns success. Update the validator to consume the matching child anchors and regenerate the evidence; make unresolved contracts fail closed. This report makes no visual score or art-acceptance claim.

## Geometry diagnostic supplement

These checks ran in separate Blender 5.2 background processes opening `checkpoints/R04.blend` with auto-execution disabled. They evaluated in memory and did not save the scene.

### Inverted ore-stone normals

I evaluated visible meshes tagged `authoring_owner=refinery-overhaul`, transformed their evaluated geometry into world space, and computed signed volume only for closed manifold meshes. Of **713** visible new mesh objects, **704** were closed and manifold; **45** had negative signed volume. All 45 are the ore-stone batches: 24 `RF1 | Receiving cart loaded ore*`, 15 `RF1 | Ore load upper layer*`, and 6 `RF1 | Moving ore batch*`. Their volumes range from **−0.00314 m³** to **−0.02733 m³** per object. Nine meshes were open or non-manifold and were excluded from signed-volume classification.

The winding is authored in `build_overhaul.py`'s `stone()` face construction; faces are flipped only when `REV>=5`. R04 runs at revision 4, so all 45 closed stones retain inward winding. Flip the stone faces for R04 as well, then rerun this diagnostic and check the rendered ore under the scene's practical lights. This is a measured normal defect, not an inference from object names.

### Selector and emergency-control decorations are centered on the button origins

I checked each generated selector grip, index, emergency cap and collar against its parent button's world matrix, transformed back to button-local coordinates. For all **24** decoration objects on the 18° tilted control heads, the actual local center is effectively `(0, 0, 0)`. The builder's authored offsets are 25 mm for selector grips, `(0, 14, 37) mm` for selector indices, 27 mm for emergency caps, and −23 mm for emergency collars. The measured offset error is **23.0–39.56 mm**; the maximum is the selector index. The decorations therefore sit at the button centers and overlap the underlying buttons instead of being seated on their intended faces.

In `revision_R04.py`, the new box/cylinder/ring objects are created with local offsets and their `matrix_world` values are read immediately to compose the button transform (lines 33–37 and 41–45). The resulting checkpoint confirms that the local offsets were lost before parenting. Update the view layer after creating the local geometry and before reading `matrix_world`, or construct each intended world matrix directly from the button matrix and its authored local offset. Recheck all 24 decoration centers in button-local space after rebuilding; visual confirmation alone may hide these overlaps at gameplay distance.

### The four wheel contacts pass through their nested support anchors

The four unresolved wheel objects are EMPTYs at `z=0.395 m`, with `LOCAL_-Z` and targets `Tip_cradle_rail` or `.001`. Their local down axis transforms to world `(0, 0, −1)`. A raycast from each wheel-center anchor using the validator's 120 mm search segment misses its nominated rail. The nearest point on each rail is **235.4 mm** away, with the rail surface normal aligned to the expected upward normal (0°); the wheel-center anchor is the wrong contact sample for this relationship.

Each wheel has a child `SUPPORT_CSM_Cart_wheel*_00` anchor at the actual contact point. Raycasting 60 mm above that child anchor downward to its nominated `Tip_cradle_rail*` hits the top face with a measured gap of **−0.000016 to −0.000009 mm** (floating-point tolerance) and **0°** normal deviation. The four child anchors map one-to-one to the four wheel/rail pairs. Teach the legacy support validator to resolve a wheel contract through this named child support anchor, or register the child anchor and target explicitly. This makes the contact evidence complete without treating a wheel-center-to-rail distance as a gap.

I also independently recomputed all **43** R04 explicit support records against evaluated target meshes. All passed: gap range **−0.000054 to 4.2834 mm**, maximum support-normal deviation **0°**. The 156 legacy records using existing `WORLD_*` directions all had sampled gaps within **−2 to +5 mm** and normal deviation no greater than **12°**; the four wheel-center records are the only unresolved legacy entries.

### Revised technical disposition

R04 has confirmed geometry defects in the ore stones and 24 button decorations. Repair these before technical acceptance. The four wheel contacts themselves are geometrically supported when measured at their existing child support anchors; the validator should use those anchors and still fail closed on contracts it cannot resolve. No exhaustive object-pair intersection or runtime collision analysis was run.
