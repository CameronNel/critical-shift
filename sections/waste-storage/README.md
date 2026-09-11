# Waste Storage

Complete original Waste Storage environment for Critical Shift, revision **W22**. Independent Luna approval: **93/92/93/92/92/91/92/92** across specification, layout, machinery, navigation, construction, materials, lighting and reference fidelity. All20 reviewed views pass the scoped local gate. Earlier failures and corrections remain in the review history. Cold-render procedural closure is recorded in `production/HANDOFF.md`.

Authoritative continuing scene: `blender/waste_storage_integration.blend`. The old `waste_storage.blend` filename was externally saved back to W02 during this run; that local file and a recovery copy are preserved and excluded from the deliverable. They are not the integration artifact.

- Architecture: `architecture/floorplan.svg` / `.png`, `architecture/EQUIPMENT_DIMENSIONS.md`, and `interface.json`.
- Measured neighbor topology: `architecture/CONNECTIONS.md` and saved-artifact survey receipts.
- Equipment/functions: `REQUIRED_EQUIPMENT.md`.
- Original concepts, prompts and approval scope: `art/PROVENANCE.md`.
- Honest review/correction history: `production/critics` and `production/CORRECTION_HISTORY.md`.
- Ten formal player-height cameras plus ten supplementary access views. Review images remain separate from generated concepts.

The scene supplies editable original geometry, procedural materials, native text, lighting, cameras and engine-host hook anchors. It does not implement gameplay runtime or assert whole-map assembly. Electrical owns the receiving threshold seam; the proposed placement and onward/utility uncertainties are explicit in the contract.

Factory-empty authoring source is `blender/build_scene.py`, which executes the retained construction/correction passes. Rendering is separate and every GPU invocation must use `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py --owner waste-storage`. Use the section-local Blender user-resource directory. Temporary caches and recovery/checkpoint `.blend` backups are not repository deliverables.

Rebuild with Blender5.2: `blender --background --factory-startup --python blender/build_scene.py -- --revision W22 --output <new-output.blend>`. Choose a new output path to preserve user edits. Source replay and cold-open evidence are documented in `production/REPRODUCIBILITY.md`; original rejected images remain as review history.
