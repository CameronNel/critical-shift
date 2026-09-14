# Non-RT render quality — R17

Saved native scene: blender/facility_spawn_concept02_R17.blend.
Saved batched inspection scene: blender/facility_spawn_material_preview_R17.blend.
Launch: blender/OPEN_SPAWN_PREVIEW_R17.ps1.

- EEVEE raster rendering; ray tracing and Fast GI disabled.
- 256 render AA samples, 64 viewport samples, full-resolution jittered shadow maps, 4 shadow samples and 12 shadow steps.
- Retained 20 x 24 x 8 baked diffuse probe, 512 bake samples; bake completed in R16. R17 restores direct broad fill for stylized shaded-facade readability and softens the sun to .12 radians. The added direct fill is not included in the bake.
- Four original 1600 x 1100 fixed camera views; supplementary 1920 x 1080 player-height image at 1.7 m. No depth-of-field or cinematic camera replacement.
- Cold preview validation PASS: no missing used images, 105 packed images, 32 merged groups, ray tracing false, full shadow resolution, baked probe object retained. Fresh targeted contact, source, dependency, reservation and route audits pass their documented scope.

This is a Blender preview of the current art with non-RT lighting, not a Unity screenshot or performance benchmark. Unity materials/lighting may differ. Interactive FPS is unverified. Exterior art acceptance requires every rubric category strictly above 93; see the independent SCORES_R17.json when complete.

R16 is retained as a failed lighting iteration: Luna scored lighting 70 due to crushed shadows. R17 addresses that regression with fresh images instead of changing cameras or scores.
