# Environment backup — 2026-09-29

This branch preserves the owner's approved saved environment from the separate
main-integration-20260914 worktree. It is a draft backup, not an art acceptance,
runtime integration, or a reproducible rebuild claim.

## Authority and provenance

- Current scene: `blender/facility_environment.blend`.
- SHA-256: `964d81807cd3cc6c43f86a1de5c5a33cba8c13aceb32c44fccc93372cc28d763`.
- Blender: 5.2.0 LTS, build `fbe6228777e7`.
- R18 is separately retained by cherry-picking b3cfbc31 and 008f20a2.
- All 24 linked libraries match the verified saved-scene baseline; retain the
  R17 material preview, exterior libraries, and twelve source modules.
- Room module files are unchanged from the fetched main baseline.
- SOURCES.json is intentionally unchanged from main, not copied from the dirty
  authoring worktree. No unrelated staged deletions are included.

## Scope

The scene includes the mine/refinery transition courtyard, refinery exterior
systems and finishes, grey/oxide palette, geometric panel/fitting gaps,
dimensional weathered paving, ground finish, and spawn/medical courtyard pass.
The new spawn/medical work is in `ART | Spawn and medical courtyard`.

Read `../../design/NON_FLAT_ENVIRONMENTS.md` for geometry-first finishing guidance.
Construction, correction, render and verification scripts are preserved as
historical migrations, not an idempotent rebuild pipeline. Many require prior
hash-guarded checkpoints and transient runtime/out inspection reports; these
local records and recovery .blend files are not included in this backup. Some
launchers contain original-machine absolute paths. Do not blindly rerun them.

The authoritative backup is the saved .blend and its retained linked libraries.
Prior cold-open evidence verified the saved scene, but no new render or Unity
validation was performed for this backup. Git LFS must be hydrated to open it.

MAP.json selects this scene for authoring and inspection. Older R18 instructions
elsewhere remain historical; do not regenerate R17 over the current dependency
or replace this scene with R18. Review launcher behavior before changing workflow.
