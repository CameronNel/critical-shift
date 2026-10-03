# Refinery interior overhaul — R15

Editable room: [module_overhaul_R1.blend](../module_overhaul_R1.blend), Blender 5.2 LTS. Fresh GPT-6 Luna [review](production/critics/R15_fresh.md):99 in every category, 99.0 weighted, no veto. This is the additive authoring delivery for PR1; promotion into the canonical module/map is separate under MAP.md.

The rework uses oxide enamel, desaturated green protection, cast steel, stainless worktops and warm concrete. One-segment construction chamfers and authored folds provide sharper edges; service records, PPE, sample handling and the radio/mug/food/shift-board nook give the room human use. World strength is zero. All21 AREA lights belong to actual in-room fixture lenses.

All 29 protected room/port interfaces match the original. [Independent technical audit](production/critics/technical_R15.md) and both numerical validations pass. A fresh rebuild from the untouched original matches every 2,989 object/45 material/scene fingerprint and all 11 fixed rendered images exactly. These are bounded Blender authoring checks; Unity import/collision/performance were not assessed.

## Rebuild and verify

From repository root, set `REFINERY_BLENDER` to Blender 5.2 LTS:

```bash
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/build_overhaul.py -- 15
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module_overhaul_R1.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/validate_overhaul.py -- R15
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module_overhaul_R1.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/render_overhaul.py -- R15
```

Rebuild writes only the additive file and its generated reports. Named validated checkpoints retain each correction cycle. Source/image hashes and fixed-camera settings are in the render manifests. [Production state](production/TASK_STATE.md) records the complete review history and delivery status.

For the separate original-source rebuild, append `coldstart` to the build arguments. Fingerprint checkpoint and rebuild with `blender/fingerprint_overhaul.py -- R15_checkpoint` and `-- R15_rebuild`; validate/render the cold file as `R15_cold`. Run `python blender/compare_coldstart.py R15` from this directory after both 11-view batches finish (requires Pillow). Current PASS evidence is under `production/coldstart/`.

## Connected context

`blender/build_context_preview.py` loads the actual current map and a checkpoint, copies nearby geometry, places the candidate at LAYOUT_A12 and writes a separate review-only wrapper. Its lights are only the candidate's physical fixtures. `blender/validate_context_preview.py` compares visible candidate placements. Earlier R08/R10 wrappers document real connected geometry; they are not the final authoring checkpoint or a promoted map cache.

Original module, registry, assembled map, exterior and frozen provenance remain preserved. Repository review and later promotion are pending; no merge was performed.

Repository delivery: local asset commit `7e57984` is complete. GitHub upload is blocked by the LFS batch service (`Maximum number of login attempts exceeded. Please try again later.`). No remote branch/PR publication, merge or promotion is claimed. The accepted local source and all evidence are available; retry authenticated LFS upload after the service restriction clears.
