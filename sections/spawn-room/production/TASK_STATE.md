# Spawn Room — Task State

## Current Valorant reference iteration

**Paused at the user's request on 7 September 2026.** Active output: `../blender/spawnroom_valorant_walk.blend`, SHA256 `65c8a873da943e1936cd72d2a7b847938afc056adb9cfee87f5edf407b76d2b8`. It contains pass-12 geometry and a subsequent saved MCP material-palette revision. That palette revision has not been rendered or scored. Do not overwrite this checkpoint with the full builder, which currently reproduces pass 12 only.

Latest completed independent review: 12. Lighting/art/layout scores are Briefing 82/86/89, Hall 82/87/85 and Locker 79/85/84. The requested 90 in every category is not achieved. Pass-12 renders passed 17 inherited checks, 170 support contacts and 180 entrance/route rays; all nine direct user checks were last run on pass 07. Native Computer Use and Blender MCP verified pass 12 in the desktop viewport before the final palette edits. The edits were subsequently saved successfully through MCP and its claim released. No additional geometry, camera or light edits were performed after the palette save. Resume instructions and exact saved evidence: `valorant-reference/PAUSED_20260907.md`.

## Current inhabited-room delivery

Status: **Personal lockers and workplace dressing implemented and verified**, 2026-09-06. Current editable/walking file: `../blender/spawnroom_inhabited_walk.blend`, SHA256 `88d17ded84f51691628af1b9337f458dbe198834ee650a21b2f10858a0f3ac47`. This is a separate output from the preserved corrected base. Latest direct user direction is in `INHABITED_REVISION_20260906.md` and removes displayed suits in favour of hangers, shoes and personal belongings.

Implemented: four dressed personal lockers, twelve hangers, retained boots, short jackets, folded cotton, bags, thermoses and photograph; staggered timber briefing floor, bound/frayed woven rug, timber benches, six sockets, whiteboard/speaker/cables, remote and booklet; hall clock, notice, jacket, lunch bag, mop/bucket and dated repair; laundry/towel and supply-shelf clusters; pod inspection/service details; integrated airlock pressure gauge and guarded amber lamp.

All 17 objective checks pass in a fresh process, all 129 registered support contacts pass, 170 entrance rays and ten main-route rays are clear. All 18 review images were repeated after reopening; maximum pixel difference is one 8-bit level, greatest image mean difference 0.000738. Final unchanged evidence: `renders/final/inhabited/`. Four build/review iterations corrected contact gaps, stretched metal shading, fabric moire and inflated clothing forms. All used image dependencies remain packed. Prior corrected and user-edited worn sources retain their pre-task hashes.

The new source is open in the existing desktop Blender instance, PID 3036, and responded to API inspections and live viewport changes at Spawn, the briefing floor and personal lockers. Scene-lit Material Preview displays the timber, carpet and concrete without the old shadow stripes. The file load succeeded; the bridge reported a stale Camera RNA error after loading, then a fresh instance/session read confirmed the new file and responsive viewport. The file is saved; only review viewpoint changes are temporary.

The previous open entrance/airlock/TV/pod corrections remain. Clock and amber-lamp keyframes are Blender animation; ambient sound and engine gameplay are not implemented. This is editable art, not an optimized game export. No renewed human art acceptance or permanent crash-free guarantee is claimed.

## Previous screenshot-correction delivery

Status: **User screenshot corrections implemented and verified**, 2026-09-06. Current editable/walking file: `../blender/spawnroom_revised_walk.blend`. It has been opened in the existing desktop Blender window and remains responsive. The floor was inspected again in the live viewport after moving the viewpoint; no stripe artifact was visible with shadows enabled.

Latest requested direction is recorded in `USER_REVISION_20260906.md` and supersedes the older meter, observation-window, personnel-door, briefing-chair/console and central-room opaque chamber requirements below. Both room entrances now have clean open reveals. The locker doorway is widened to 2.2m to reduce occlusion of the forward suit bays. The operations airlock is 2.56m clear width. Briefing has one slim TV and exactly two two-person benches. Four suit stations move toward the entry; two changing benches flank the aisle; the glass/metal pod is centered at x=6.82, y=4 toward the back.

Review trail: `renders/review/user-corrections-01`, `-02`, `-03`, and `user-corrections-cold`. Pass 01 exposed dark pod glass and excessive entry occlusion; pass 02 exposed transparency dither and faceted ring highlights; pass 03 fixes those and adds targeted floor/frame views. Final evidence: `renders/final/user-corrections/`. All 19 objective checks pass, all 67 support contacts pass, and 170 doorway rays are clear. Floor top normals and duplicate-face checks pass. Six pod readout/door states pass. Fourteen cold renders differ by at most one 8-bit channel level, greatest per-image mean 0.000344. Source SHA256: `f4efd7d19f277edef8a2ff59e0457f000a46639c8b287bf8c036c5958dc7208d`.

The striped artifact was diagnosed by disabling shadow maps temporarily, then restoring them with jitter and filtering. Texture maps and bump relief were retained. Startup still uses Material Preview, scene lights/world, and a free perspective at spawn. The open file does not require startup Python. Its current source was saved by the background builder; live verification changed only the temporary viewport. The user's prior desktop states are preserved in two separate checkpoints. Original tactile sources and the pre-existing local `spawnroom_worn.blend` edit remain preserved. No global skill install or computer input automation was needed.

Remaining limits: the narrow fixed doorway camera does not contain all four forward suits simultaneously; side/reverse views and object checks cover both pairs. The pod's blended glass is deliberately simplified for realtime clarity. This task validates the requested corrections; prior holistic art scores are not renewed human acceptance. No engine gameplay implementation or permanent crash-free guarantee is claimed.

## Historical tactile delivery

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
