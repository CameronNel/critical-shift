# Approved spawn exterior implementation — active review checkpoint

Cameron approved Concept02 with “Implement that”. This is an exterior implementation of that approved concept, not final art acceptance.

Current authored scene: `blender/facility_spawn_concept02_R17.blend`.
Current batched inspection scene: `blender/facility_spawn_material_preview_R17.blend`.
Interactive launcher: `blender/OPEN_SPAWN_PREVIEW_R17.ps1` (1920x1080 window; rendered EEVEE; no ray tracing; existing walk controls and no-gravity navigation). Current-revision interactive FPS is not verified. This file is not a Unity build.

Implemented: local ivory/olive/orange paint, service enclosures with wall anchors, mounted hose/conduits and pipe sleeves, supported spare-pipe rack, narrow planted beds, broader tree and ground foliage, roof membrane courses, restrained painted texture, exterior daylight and distant backdrop. The visible exterior rock faces use local material overrides and a simplified derived upper surface. All 2,444 protected boundary/lower-interface vertices were verified unchanged; original source-library geometry is unchanged. Section placements and original room libraries are retained. Original interior lights are enabled in the authored assembly and isolated temporarily only by the exterior review renderer; the batched preview copies them into its cullable light collection.

Four fixed review cameras are in `FIXED_CAMERAS.json`; native renders are in `renders-R17`. Do not substitute a concept image for a scene render or change camera crops to evade defects. Independent critic: /root/luna_spawn_exterior, Luna. Every applicable category must be strictly >93. Prior reviews remain REJECT. Current review status is in TASK_STATE.md and the latest SCORES file; this checkpoint is not a final handoff.

Replay in a disposable copy of the section, keeping historical artifacts intact:
1. From retained A14 baseline, run `build_spawn_concept02.py` with SPAWN_REV=R02.
2. Run `finish_spawn_lighting.py` to produce R03.
3. Run `refine_spawn_R04.py` through `refine_spawn_R15.py` in numerical order. R10 uses the packed/generated painted material in blender/textures.
4. Run `audit_spawn_all.py` with SPAWN_REV=R15. It cold-loads once, inventories dependencies/reservations, verifies source hashes and targeted contacts including roof courses, then records route floor/headroom/crossing samples over unchanged context caches plus the new live geometry. These checks do not certify Unity collision/navmesh.
5. Run `review_spawn_exterior_locked.py` with SPAWN_FILE=facility_spawn_concept02_R15.blend and SPAWN_OUTPUT=renders-R15 through gpu_gate.py, owner astra-facility-assembly.
6. Run `record_spawn_render_benchmark.py R15` after all four renders complete.
7. Build the inspection cache with build_material_preview.py, PREVIEW_SOURCE=facility_spawn_concept02_R15.blend, PREVIEW_DEST=facility_spawn_material_preview_R15.blend, PREVIEW_REPORT=spawn-exterior-review/MATERIAL_PREVIEW_R15.json.

The generated texture is packed and also retained at blender/textures/spawn_painted_mineral_01.png. Its generation source is exec-8f2452e3-9bc2-4229-bc66-85c0bb5221d3.png under Codex generated_images. It is a material texture, not a render or acceptance image. Geometry caches preserve material slots and UV layers; merged meshes can change implicit Generated/Object coordinate textures, as disclosed in the preview build report.


R16 quality replay: run upgrade_spawn_realtime_R16.py through the GPU gate after R15. This bakes a daylight volume probe, disables artificial sky fill, and sets EEVEE to 256 render samples / 64 viewport samples with jittered shadows and RT disabled. Render/audit with R16 environment paths. Build the R16 preview with PREVIEW_QUALITY=HIGH so full shadow resolution is retained. render_spawn_player_R16.py produces a supplementary 1920x1080 eye-height image; it does not replace the four locked review views.

R17 correction: after R16, run correct_spawn_daylight_R17.py, then render_spawn_R17.py through the GPU gate. The latter renders all four locked views and the additional player view from one cold load. Use R17 source/destination names and PREVIEW_QUALITY=HIGH for the preview builder; run R17 audits. This restores readable direct fill after Luna rejected R16 lighting. See RENDER_QUALITY_R17.md for settings and limitations.
