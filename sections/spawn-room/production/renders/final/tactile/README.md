# Tactile revision evidence

Root PNGs: all eleven fixed cameras plus two detail views, rendered in a fresh Blender 5.2.0 LTS process using Cycles HIP, 1440×900, 32 samples, denoising, AgX Medium High Contrast, exposure +0.3. `CONTACT_SHEET.png` collects the fixed views. Raw images are unaltered.

`walk/`: all eleven fixed EEVEE views from a fresh reopen of the final walking copy, plus the two inspected detail frames from the prior EEVEE pass. `slice/`: the corrected two-view validation slice. The walking source starts in Material Preview with scene lights/world enabled, because saved Rendered mode reverted to Solid at reload.

`render_provenance.json` records source and image hashes, render settings and the provenance of each image. Both engine sets pass 83 support-contact checks, 29 objective checks and all 15 required packed-texture hashes. `walk/cold_comparison.json` compares all eleven fixed walking views before and after reopening; max image mean change is 0.00316/255.

The Cycles and EEVEE sets are separately reviewed. EEVEE uses baked room probes and four unshadowed floor-bounce approximations; it is not intended to be pixel-identical to Cycles. First shader compilation can take about a minute. This is editable Blender art, not an optimized game build or human art approval.

Source: `../../../../blender/spawnroom_tactile.blend`. Walk: `../../../../blender/spawnroom_tactile_walk.blend`. Texture URLs/licenses: `../../../../assets/textures/TACTILE_SOURCES.md`. Detailed critique: `../../../critics/tactile-lighting-review.md`.
