# Spawn Room — Task State

Status: **Tactile material/lighting revision verified and packaged**, 2026-09-06. Current files are `../blender/spawnroom_tactile.blend` and `../blender/spawnroom_tactile_walk.blend`. The latter opens with scene-lit Material Preview at spawn eye height. User art acceptance remains pending; the earlier worn pass below was rejected as too flat.

Latest main `97bb68c` fetched and merged. New authoring still starts from an empty factory scene. Four CC0 Poly Haven sets (12 new maps) supply worn concrete, trowelled painted plaster, timber and threshold tread. Different material families now have distinct reflection/roughness response. Selected sheet panels have bounded 4mm deflection. Practical lights create pools, darker recesses and a clearer operational threshold. Current renders: `renders/final/tactile/`; the `walk/` subdirectory holds EEVEE evidence.

Verification: all 11 fixed Cycles views plus two details rendered from a fresh process; all 11 EEVEE walking views rendered and repeated after reopening. Contact checks: 83 PASS. Objective checks: 29 PASS. All 15 required texture hashes pass; ten saved viewport spaces retain Material Preview with scene lights/world. The walking cold comparison passes, maximum image mean difference 0.00316 on the 0–255 scale. Final source save and engine provenance are in the new gallery.

The prior `spawnroom_worn.blend` has local edits made before this turn; it was not overwritten or included in the new revision commit. No GUI automation or global skill installation was used. Online skill research, defects and corrections: `critics/tactile-lighting-review.md`. Current review score and specific limits are recorded in `RUBRIC.md`.

Known limit: EEVEE uses four baked room volumes plus a bounded floor-bounce approximation, so its lighting differs from Cycles. Materials remain authoring node graphs; engine baking/optimization and gameplay integration remain separate work. Initial Material Preview shader compilation can take about a minute on this machine.

## Historical maintained-wear delivery

The following records describe the prior pass, not the current accepted appearance.

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
