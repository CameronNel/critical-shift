# Surfacing checks

Use with [the skill](../SKILL.md). These are checks for the authorized objects,
not instructions to rebuild every material or impose a new texture budget.

## UVs and mapping

Record UV-layer names and the layer used by each texture, bake and export. A viewport
UV preview does not prove that shader nodes use that layer. Test finite coordinates,
coverage and degenerate islands. Overlap/out-of-range UVs may be deliberate for tiled
or mirrored surfaces; classify them rather than failing every asset identically.
A lightmap layout has different uniqueness and padding needs from repeating albedo.

For atlases, state the image origin convention and convert top-left pixel rectangles
to Blender UV coordinates explicitly. Keep padding appropriate to target resolution,
filtering and expected mip levels. Inspect distant views for bleeding. Do not apply
the whole atlas to every part. Projection must name its coordinate frame; object-local
X/Z coordinates are not world coordinates or a perspective-camera projection.

## Map semantics

Treat base color as color-managed data under the project's configuration. Treat
roughness, metallic, masks and normal/height maps as numeric data. Verify the installed
color-space names; do not assume all images, HDR inputs or lightmaps use one encoding.
Inspect shared image users before changing a datablock's color-space setting.

A tangent-space normal texture belongs through a Normal Map node with the matching
UV/tangent convention; a scalar height texture belongs through a Bump node. Do not
route an RGB normal map into Bump Height. Check handedness/green-channel conventions
against the receiving importer with a directional-light test, not a blind channel flip.

Blender roughness and a target shader's smoothness are not interchangeable. Determine
the receiving shader, channel packing, numeric encoding and inversion explicitly.
Do not assume a glTF metallic/roughness map can be assigned unchanged to Unity's
Built-in Standard shader, or that a procedural Blender graph survives FBX export.

For decals, connect the intended alpha, inspect edge fringes and depth artifacts,
and verify the installed renderer's transparency API. Avoid legacy hard-coded
`blend_method` recipes. Alpha in an image alone is not a verified material setup.

## Baking without collateral edits

Baking lighting (lightmaps, baked shadows or AO) is the final production step. Do not bake while authoring; finish geometry, UV0 materials and live lighting first, and bake only into a separate delivery derivative once those are accepted. Anything in this section applies only at that final step.

Use a disposable process/copy. Identify evaluated high/low meshes, scale, cage/ray
settings, named UVs, map type, resolution and margins before running the existing bake
path. Selection and active-object state are explicit; unrelated objects stay excluded.
For image baking, configure an active image target in every participating target
material. Prevent an active target image from also being read by the source shader.
Choose color-only albedo when lighting must remain separate; do not bake shadows into
albedo accidentally. Keep normal and AO outputs distinct from color maps.

Save each output image to a task-owned path. Reopen/reload saved images and inspect
seams, cage misses, black tiles, projection errors and compression artifacts. Record
source revision, output hashes and settings with the existing asset evidence, without
creating a second source-of-truth manifest. Pack or reference files only according to
the actual delivery contract. Never overwrite the original texture pack in place.

## Acceptance

A checker, material response under a useful light and gameplay-distance scene views
answer different questions. Record which were actually inspected. Neutral lighting
is diagnostic, not permission to alter the approved scene lighting. Keep technical,
visual and target-engine statuses separate and preserve stricter section gates.
