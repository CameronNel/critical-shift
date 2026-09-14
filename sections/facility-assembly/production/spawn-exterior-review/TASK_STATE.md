# Spawn and rescue courtyard exterior pass

User confirmed 2026-09-13: start with spawn and adjoining courtyard; exterior only; GPU and CPU rendering resources authorized; four concept angles comprising top-down and three exterior angles. Present concepts for explicit user approval before polishing toward them. No interior edits.

Baseline: facility_master_A14_exterior.blend, native source materials. Existing rough shell, stepped roofs, courtyard floor, access doors, drains, lighting and roof machinery retained. No new design geometry added before concept approval.

Independent critic: /root/luna_spawn_exterior, model gpt-5.6-luna. Every applicable rubric category must be strictly above 93. 93, lower, and unverified are rejection; no averaged pass. No acceptance has been achieved.

Camera setup trials retained in baseline-A14. South-west trial was blocked by mine rock. East trial cropped the subject. Trial renderer also reported shadow-pool exhaustion. Replacement views and enlarged shadow pool are in baseline-fixed-v1. FIXED_CAMERAS.json is the final reproducible camera definition once all four images are visually confirmed.

Next: inspect all four corrected scene renders; generate one cohesive four-view ChatGPT concept sheet using those renders as edit inputs; present for user approval. Then build approved exterior design and repeatedly obtain independent Luna reviews using unchanged cameras, plus detail evidence and technical checks as required by RUBRIC.md.

Concept 01 generated and saved in concepts/SPAWN_EXTERIOR_CONCEPT_01.png. Presented to Cameron for approval. STOP at approval gate. Luna's fresh baseline is REJECT: visible categories 58–78; remaining technical/reference categories unverified. No polish implementation is authorized until the concept approval reply. GPU render job completed and gate released.

Concept 01 rejected by Cameron: needs our Valorant art style. Concept 02 generated with built-in ChatGPT image_gen as an edit of the four-view screenshot-derived Concept 01. Stronger olive/orange/ivory blocks, painterly material simplification and sculpted rock/foliage forms. Saved concepts/SPAWN_EXTERIOR_CONCEPT_02.png. Awaiting approval; no geometry edits. Preserve actual doorway widths and neighbor signage during implementation despite generated illustration drift.

## 2026-09-13 — Concept 02 implementation authorized
Cameron approved Concept 02 with “Implement that”. Exterior implementation is active in this private assembly worktree. R02 independently rejected (visible scores 58–81); R04 is saved with new service cabinets, mounted hose/conduits, grounded spare-pipe rack, planted beds, ivory/olive/orange materials and retained source interiors. TECHNICAL_R04.json passes cold load, source hashes, placements, dependencies and targeted contacts. Route audit R04 has no findings. R04 four fixed renders complete; Luna reviewing. R05 lowers the crude backdrop; R06 adds broad directional daylight fill to the overly dark south façade. No >93 acceptance, no Unity readiness claim. Interior lights are retained in collection30 but disabled for exterior review; enable them when reviewing interiors. Next: render R06 at locked cameras, independent review, iterate.

## 2026-09-13 — R15 implementation checkpoint, REJECT
Current authored scene: blender/facility_spawn_concept02_R15.blend. Current batched inspection scene: blender/facility_spawn_material_preview_R15.blend. Four native locked views: renders-R15. Both files saved; preview cold-load validation PASS (32 merged groups, 105 packed images, no missing used images, EEVEE, ray tracing disabled). No interactive FPS or Unity acceptance claim.

Fresh technical/contact/source/dependency/reservation/route checks PASS. 67 ground/roof contacts checked. All 2,444 protected rock lower-interface/boundary vertices remain exactly unchanged after upper-surface simplification. Original source libraries and section placements preserved. Hose spool connection added. Full native four-frame render batch completed.

Independent Luna R15 decision: REJECT. Scoped category scores: circulation 95, construction/support 95, utility continuity 94, terrain/transitions 95, interfaces/reservations 95, offline assembly readiness 95. Visual categories remain below the strictly >93 requirement. Read SCORES_R15.json and REVIEW_R15.md for actual independent scores/deductions. No final acceptance and no new section authorized by this checkpoint.

Outstanding: professional visual finish of contextual rock, top-view material/value grouping, roof/wall/paving specificity, planting/bench rhythm, and south-entry readability within the locked camera and retained guard/door dimensions. Do not claim the entire map or this exterior pass has passed. No render jobs remain after this checkpoint; work is saved locally for continued iteration.
## 2026-09-13 — R16 non-RT render-quality upgrade
Native scene: blender/facility_spawn_concept02_R16.blend. Batched preview: blender/facility_spawn_material_preview_R16.blend. Launcher: blender/OPEN_SPAWN_PREVIEW_R16.ps1.

EEVEE ray tracing and Fast GI are disabled. A 20 x 24 x 8 volume probe completed its 512-sample bake; artificial broad sky-fill lamps are disabled. Render AA is 256 samples, viewport AA 64, shadow sampling 4 x 12 with jitter. The high-quality preview retains full shadow resolution instead of the former half-resolution override. Cold preview validation PASS: 32 groups, 105 packed images, no missing used images, baked probe present. Fresh route/contact/source/dependency checks PASS. Geometry and layout carried from R15.

Four locked-camera renders are being completed; an additional 1920 x 1080 eye-height view is queued. Independent Luna R16 review pending. R15 remains the latest scored REJECT. This is a Blender approximation of non-RT game rendering; Unity runtime and interactive FPS remain unverified.
## 2026-09-13 — R17 corrected non-RT quality checkpoint
R16 completed all four fixed renders plus a player-height 1080p render, but Luna rejected its dark shadow treatment (lighting70, materials84, professional finish74). Failed evidence retained.

R17 restores broad direct fill, softens sun shadows, retains the baked diffuse probe, 256 render AA samples, 64 viewport samples and full shadow resolution. Ray tracing and Fast GI remain disabled. Current native/preview files and launcher use R17. Four corrected fixed renders complete; cold preview/source/contact/reservation/route checks PASS in their documented scopes.

Independent Luna R17: REJECT. Reference90, silhouette90, layout92, circulation95, construction95, utilities94, materials88, lighting90, storytelling89, terrain95, roof91, consistency89, interfaces95, offline delivery95, professional finish82. No category scores have been self-assigned. Strictly >93 remains required. Remaining art: coarse background rock, roof/paving value separation and surface authorship, repetitive planting/furniture. Interactive FPS and Unity runtime remain unverified. Additional player render is the final pending render at this entry.
R17 completion: all five fresh images finished successfully, including 1920x1080 PLAYER_1080P. Worker exited; GPU gate released. Current art remains independently REJECT, as scored above.
