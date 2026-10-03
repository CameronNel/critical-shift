# Refinery interior overhaul — R24 dark and neglected

Editable room: [module_overhaul_R1.blend](../module_overhaul_R1.blend), Blender 5.2 LTS. The owner requested a run down, dark, gloomy and hopeless treatment after rejecting R15's cheerful mood. R24 passes the current [independent GPT-6 Luna review](production/critics/R24_fresh_final.md): 99 in every art category, 100 technical, weighted 99.10, no veto. The [updated brief](scenery/REFINERY_OVERHAUL.md) governs this darker direction. The previous [R15 review](production/critics/R15_fresh.md) is historical and does not approve this direction. Promotion into the canonical module/map is separate under MAP.md.

R16–R24 use faded enamel, dirty cold concrete, localized water damage, oxidized metal and old service leaks. Six failed fixtures have zero source energy and zero lens emission; remaining fixtures create weak pools. Sharp construction, supported worker belongings and the clear route remain. World strength is zero; every AREA source belongs to an actual in-room lens.

Current [numerical validation](production/validation_R24.json) and [independent technical audit](production/critics/technical_R24.md) pass: all 29 protected room/port interfaces match the original; the sampled route is clear; 418610 evaluated triangles. Every raw/evaluated mesh and object pose matches R23. Both final paired review cycles are stable. The original-source cold rebuild matches all 3043 object, 77 material and scene fingerprints, with identical cameras/settings and all eleven images pixel-identical (maximum channel delta 0). [Cold proof](production/coldstart/pixel_comparison_R24.json) records the result. These are bounded Blender authoring checks; Unity import, collision and performance were not assessed.

Current views: [entry](production/renders/R24/CAM_ENTRY.png), [main route](production/renders/R24/CAM_MAIN_ROUTE.png), [work nook](production/renders/R24/CAM_WORK_NOOK.png). Active source and immutable R24 checkpoint SHA256: `37896096ba619770afdf2d3dfc4443b2223aadcc71a468b809a833803eb8701b`.

## Rebuild and verify

From repository root, set `REFINERY_BLENDER` to Blender 5.2 LTS:

```bash
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/build_overhaul.py -- 24
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module_overhaul_R1.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/validate_overhaul.py -- R24
"$REFINERY_BLENDER" -b --disable-autoexec sections/facility-assembly/sources/refinery/module_overhaul_R1.blend -t 8 --python-exit-code 1 --python sections/facility-assembly/sources/refinery/overhaul/blender/render_overhaul.py -- R24
```

Rebuild writes only the additive file and its generated reports. Named validated checkpoints retain each correction cycle. Source/image hashes and fixed-camera settings are in the render manifests. [Production state](production/TASK_STATE.md) records the complete review history and delivery status.

For the separate original-source rebuild, append `coldstart` to the build arguments. Fingerprint checkpoint and rebuild with `blender/fingerprint_overhaul.py -- R24_checkpoint` and `-- R24_rebuild`; validate/render the cold file as `R24_cold`. Run `python blender/compare_coldstart.py R24` from this directory after both 11-view batches finish (requires Pillow). Current PASS evidence is under `production/coldstart/`.

## Connected context

`blender/build_context_preview.py` loads the actual current map and a checkpoint, copies nearby geometry, places the candidate at LAYOUT_A12 and writes a separate review-only wrapper. Its lights are only the candidate's physical fixtures. `blender/validate_context_preview.py` compares visible candidate placements. The R23 wrapper and three context views document real connected geometry at the preceding finish version; its 3029 visible poses pass comparison. R24 retains that exact geometry and placement but changes some local finishes. Context evidence is review-only, not a promoted map cache; the underlying map has unrelated missing Spawn object IDs.

Original module, registry, assembled map, exterior and frozen provenance remain preserved. Repository review and later promotion are pending; no merge was performed.

Repository delivery: R24 and its evidence are saved on the local task branch. Remote publication is pending after the earlier Git LFS batch-service rejection (`Maximum number of login attempts exceeded. Please try again later.`). No remote branch/PR publication, merge or promotion is claimed. The upload was not retried during this mood revision. The local source and evidence are available.
