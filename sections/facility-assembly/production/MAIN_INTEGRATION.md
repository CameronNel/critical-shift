# Main integration — 2026-09-14

Cameron explicitly authorized committing and integrating the existing approximately 75%-complete whole map so remote agents can continue it from main. This supersedes historical task-local "no main merge" instructions for this integration only.

Source authoring branch: codex/facility-assembly-20260912, checkpoint5936c2a. Its inherited accepted condenser R34 is included. All twelve selected portable room modules, exteriors, connections, floor/terrain/perimeter work, roof services, latest R17 full-map scene, scripts and review evidence are included. No unrelated room branches or removed runtime prototypes were merged.

Integration branch: codex/map-main-integration-20260914, based on origin/main57f15bc. Squashed source-tree integration prevents unpublishable historical raw >100MB Git blobs entering main; original task branch history is retained locally. Large new map assets use scoped Git LFS attributes. Reproducible older preview/intermediate copies remain in their original worktree; see LOCAL_REPLAY_COPIES.json. They are not current-map dependencies.

Independent /root/network_review inspected scope, dependencies, entrypoints and bundled-launcher changes; no remaining entrypoint/launcher blocker. Fresh MAIN_CHECKOUT_VALIDATION.json passes native and preview cold-load, 24 contained libraries per scene, source hashes and bundled controls. PORTABLE_MAP_RELINK.json records the path-only saves needed to remove private-worktree dependencies. Existing source/review imagery is retained; this integration does not claim a new art pass. R17 visuals remain below the >93 threshold. Unity and interactive FPS remain unverified.

Root MAP.md and MAP.json are authoritative entrypoints for remote agents. Root README and AGENTS route map work there. Use the editable native scene; regenerate the batched preview after geometry changes.
