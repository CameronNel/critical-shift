# Medical / Reanimation

Complete original Medical art rebuild around Grok's preserved R09 layout, authored by Astra and independently reviewed by Luna. Strict grounded Valorant direction, restrained off-white/graphite/ochre materials, neutral and warm practical light; no teal. The original source scene remains untouched.

Open [medical_integration.blend](blender/medical_integration.blend) in Blender5.2. The current saved revision is M11:1203 objects,23 materials and14 fixed player-height cameras. The room is8×9×3.6m with the inherited1.70×2.12m decon extension and one2.20×2.50m external entry. The whole shell, OCRU, transfer/cart mechanism, service hookups, controls, reserve power, supplies, recovery position and decon equipment are included.

Independent final result: **PASS**. Luna scored all sixteen relevant categories93–98 and all twenty designated views93–96, strictly above90 throughout. All fourteen fresh-process cold renders pass the documented1/255 rounding tolerance, and two cold scene fingerprints match an independent factory-empty rebuild exactly. These are saved-artifact results, not a claim of whole-map runtime completion.

The existing interactive Blender window was safely preserved on M10 after automatic approval rejected a reload following an add-on Camera bookkeeping error. Its lease is released. Open the saved M11 file linked above to inspect the delivery; the M11 cold evidence was produced independently in fresh Blender processes.

## Inspect and integrate

- [Actual-render gallery](gallery.html): ten formal fixed cameras, four additional approaches and six interaction demonstrations.
- [Dimensioned architectural plan](architecture/floorplan.png), [editable vector plan](architecture/floorplan.svg).
- [Exact interfaces and topology](architecture/INTEGRATION.md), machine-readable [interface.json](interface.json).
- [Required-equipment checklist](production/CHECKLIST.md) and [requirements/authority](architecture/REQUIREMENTS.md).
- [Independent final Luna review](production/critics/luna-scene-M11.md), [honest correction history](production/CORRECTIONS.md), [concept provenance](art/concepts/provenance.json).
- [Final evidence index](production/FINAL_EVIDENCE.json), [saved-artifact measurements](production/validation/M11/technical.json), [cold-open comparison](production/validation/cold-comparison.json).

Use `main_entry` and the five named utility markers exactly as documented. Append the section collection at its local origin; the clean-service junction and neighboring global transforms remain unbound. Do not reposition other rooms to absorb an invented offset. Actual evaluated equipment extrema in the technical report supersede simplified plan reservations. Preserve the constrained lateral extraction of the southwest cart and the separate decon cart apron.

The default scene is open and ready to inspect. Cart lift, bridge and cabinet/entry mechanisms have editable roots; demonstrated state poses are supplemental evidence, not changes to the saved inspection state. The adult proxy in transfer evidence is a neutral validation shape, not a character asset.

## Reproduce

The ten original modelling sources are hashed in the saved scene and build manifest. `blender/build_scene.py` runs factory-empty, constructs all geometry/materials, and saves the final artifact. Use a private section-local `BLENDER_USER_RESOURCES`. Pass `--revision M11-replay --output <section>/production/checkpoints/source-replay.blend` after Blender's argument separator for an isolated replay; do not overwrite the delivered file merely to inspect it.

`validate_scene.py`, `contact_audit.py`, `sign_audit.py` and `cold_audit.py` inspect the saved file. `interaction_evidence.py` checks specific carry, transfer and obstruction scenarios; `--render` creates six in-memory posed images without saving the file. Every GPU invocation must go through the shared facility-run `gpu_gate.py --owner medical-reanimation`. `production/final_render_batch.py` performs final, independent cold and state batches; `compare_evidence.py` compares their actual pixels and the independent source-replay fingerprints.

All materials are procedural or solid shader materials. There are no external texture files or linked libraries. Lettering uses Blender's built-in font; a structured dependency tool incorrectly treats `<builtin>` as a missing path, documented in the cold-open evidence.

## Remaining integration work

This deliverable is the owned art module. The host still implements power/inventory costs, identity/compliance state, restart/pause/recovery logic, occupancy/interlocks, ragdoll physics, networking, navmesh and neighboring connector placement. Specific geometric route checks and staged images do not claim exhaustive runtime or whole-map validation. The room has one external entrance, so host interactions must preserve recovery/repositioning of an entrance obstruction.
