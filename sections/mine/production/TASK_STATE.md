# Gullet Mine: Task State

**Read first:** `../AGENT_READ_FIRST.md`  
**Current revision:** `1.1.0-cc0-cycles`  
**Phase:** Material/lighting repair executed; final art and Unity integration pending.  
**Actual Blender build:** PASS, Blender 5.2.1 LTS / Cycles.  
**Fresh-process validation:** PASS.  
**Production-final acceptance:** NOT YET EARNED.

## Completed

- Preserved deterministic mine geometry, 2.5% descending grade, no elevator, staging bay, facility handoff, blast gate, three progressive sectors and 22-piece collapse recovery.
- Downloaded six CC0 2K texture sets and verified all 24 map hashes.
- Applied differentiated rock, gravel, concrete, steel, paint and groundwater materials; limited teal to selected equipment/signage.
- Added bounded rock relief and corrected concrete value separation and structural colours.
- Executed the source in Blender, rather than treating Python compilation or VTK output as visual evidence.
- Completed a focused three-stage material review and inspected all ten fixed camera views locally.
- Independently rebuilt the committed source in the repository runner and rendered entry, main route and sump.
- Reopened the repository-generated .blend in a fresh process, tested actual bpy state/gate/rubble controls and scene data, and rendered entry again.
- Committed the packed Blender scene, original CC0 materials, real review renders, logs and validation reports in section-local paths.

## Evidence

- Scene: `../blender/gullet/Gullet_MaterialReview.blend`.
- Source entrypoint: `../blender/gullet/build_mine.py`.
- Material originals and hashes: `../assets/pbr/`.
- Actual repository renders: `renders/review/cc0-materials/`.
- Build and cold-start evidence: `checkpoints/cc0-materials/`.
- Pixel review and limitations: `MATERIAL_REVIEW.md`.

## Validation record

The repository cold-start report records PASS, 7,472 checks and no issues. Its scope is packed scene images, finite geometry, IDs, UVs, cameras, actual authoring-state controls and 61 standing-path clearance rays. It is not a complete physical controller sweep or Unity test.

## Remaining work

1. Continue the full global art-acceptance protocol, including the required complete correction cycles; do not count the focused material review as an automatic protocol pass.
2. Improve any remaining repetitive excavation-face/collapse silhouettes and verify exterior facility integration at gameplay scale.
3. Bake or recreate box-projected Blender materials in the engine, then compare actual gameplay-camera frames with the Blender evidence.
4. Implement/test Unity cart, pickup, detonation, rubble, networking, navigation, collision, audio and VFX systems.
5. Measure HIP rendering and runtime performance on the user's actual hardware.

## Reproduction

Follow the fresh-build and cold-start commands in `../AGENT_READ_FIRST.md`. The canonical builder now selects the textured revision. Do not use the preserved geometry source or earlier diagnostic exporter as the visual delivery.

## Supplied hardware

Radeon RX 9070 XT; Ryzen 7 5800X; 32 GB DDR4. Recorded validation used CPU, not this GPU. No target-hardware performance number is asserted.
