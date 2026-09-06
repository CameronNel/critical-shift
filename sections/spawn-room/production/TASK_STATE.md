# Spawn Room — Task State

Status: **PASS — maintained-wear Blender art delivery**, 2026-09-06. This is the user-directed maintained-wear revision. Builder review is not user acceptance.

Direction: old, dirty and mildly damaged but maintained; rough stylized concrete/plaster; used equipment and PPE; restrained irregularity and actual depth. Six free CC0 Poly Haven maps are remapped in shaders. No paid or attribution-required assets were used. Provenance and original-download checksums: ../assets/textures/SOURCES.md and manifest.json.

The source starts in an empty factory scene. No previous blend is modeling input. Current branch: codex/spawn-reference-rebuild. Latest main d849d3d was fetched and merged during this revision; the Gullet additions do not overlap Spawn. Original worktree and earlier review evidence remain preserved.

Implemented: mineral wall/floor texture and roughness; softer painted dado; localized recessed plaster loss; real shallow grout and chipped tile corners over the original structural floor slab; subtle wall waviness; small furniture/equipment edge compression and dry paint loss; separate used responses for fabric, rubber, paint, wood, glass, paper and ceramic. All six texture maps plus both existing portraits are packed. SOLID startup remains enabled.

Review: three rendered slice iterations; two rejected full-room attempts (curved-seat paint contact and rotated-wall texture stretching); then all eleven fixed room views in renders/review/worn-room-03 inspected. Corrected room audit: 83 contacts, zero failures; 29 objective checks PASS. Camera transforms and lenses match room-06 exactly. The final source-only rebuild retains the original 170mm structural slab beneath the revised floor surface.

Chamber aisles remain 1.203m north/south and 1.295m rear. Hall clear: 3.296m. Briefing outer routes: 1.247m behind seats and 1.437m north. All six machine readout/door/scan states pass their existing objective checks.

Open the protected delivery copy: ../blender/spawnroom_worn.blend. It is byte-identical to the rebuilt canonical ../blender/spawnroom.blend. Small kit: ../blender/spawnroom_style_slice.blend. Reproduction: ../blender/README.md. Detailed correction trail: critics/worn-surface-review.md. Prior room-01..06, startup recovery, historic scores and state renders remain historical evidence; those scores do not automatically approve this new pass.

This remains editable Blender art. Runtime interactions, networking, collisions, rigging, LODs and optimized engine exports are separate integration work. No Computer Use or foreground window control was used for the wear revision.

Final verification: all eleven fixed cameras and two detail views rendered from the saved scene in fresh processes. The full cold set was visually inspected against worn-room-03 with no material regression; maximum per-image mean 8-bit change is 0.07731 after the hidden structural-slab rebuild. All 83 contacts, 29 objective checks, six packed-texture hashes and ten SOLID startup spaces pass. Current gallery: renders/final/. Earlier state pictures remain explicitly historical in renders/review/cold-start/.

A concurrent save of the older room-06 scene overwrote the canonical file at 16:05. The exact unexpected file was preserved in ignored logs, the unchanged deterministic builder regenerated the worn scene, and a separate spawnroom_worn.blend copy was verified from a fresh process. Its Spawn comparison differs by at most one 8-bit colour value (mean 0.00004784). See worn_recovery_comparison.json and renders/final/render_provenance.json. No scene edits were discarded from the unexpected save.

Current builder rubric: 92/100, with material separation improved and other category assessments stable; see RUBRIC.md. This is not human acceptance or a claim of perfection. Final build and verification jobs completed with exit 0 before delivery; rejected/cancelled earlier attempts remain documented in the review trail.
