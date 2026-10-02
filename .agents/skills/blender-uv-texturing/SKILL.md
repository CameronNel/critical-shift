---
name: blender-uv-texturing
description: Use for Critical Shift Blender UV layouts, texture atlases, trim sheets, decals, PBR map wiring, baking and stretched or missing textures. Extends blender-headless; not for unrelated modeling, runtime code or documentation-only tasks.
---

# Critical Shift: UV and materials

Read [blender-headless](../blender-headless/SKILL.md) first. Existing art direction,
section material families, source ownership and acceptance gates remain authoritative.
This is a headless adaptation of a pinned upstream workflow, not its executable
recipes. See [source and adaptations](SOURCE.md) and [license](LICENSE).

## Establish the material contract

Inspect the affected objects, shared mesh/material/image users, UV layers, texture
files, color management, renderer and Blender version before changing anything.
Record the permitted material slots, UV names, physical texture scale and baseline
views. Preserve unrelated users of linked data. A local change to a shared image's
color-space setting can affect other materials; isolate only when necessary.

Choose the technique from the asset, not a universal recipe:
- Repeating surfaces: preserve the approved physical scale and seams.
- Atlas or trim sheet: map each part to its intended region with a padding policy.
- Projected decal: verify projection space, orientation, alpha and side coverage.
- Unique bake: retain the approved source and create a separate delivery derivative.

Do not hide weak geometry with texture noise. Preserve the project's grounded
stylized semi-realism and readability from its actual gameplay/validation cameras.

## Work and verify

1. Use existing builders and section tooling in a disposable working copy. Do not
   re-unwrap accepted assets or replace their material library without task scope.
2. Validate named UV layers, face coverage and intentional overlaps. Inspect a
   checker on all relevant sides, including caps and sidewalls, not only the hero.
3. Wire maps by meaning: color versus numeric data, tangent normal versus height,
   roughness versus smoothness. Use the installed-version API, not old UI recipes.
4. For baking, isolate source/target sets and configure all participating material
   slots and image targets. Save images explicitly; saving a blend alone is not
   proof that external baked files exist. Keep diagnostics out of the source file.
5. Inspect checker, neutral-light material and actual scene renders at useful
   gameplay distance. Compare before/after with the same camera and color setup.
6. Repair the identified defect, re-render and check that neighboring surfaces and
   other users of shared data have not regressed. Small edits need focused evidence;
   full-section acceptance still requires the existing complete protocol.

Read [map, bake and portability checks](references/surfacing.md) only as needed.
For export, also use [game-asset-pipeline](../game-asset-pipeline/SKILL.md).

## Completion and boundaries

Report source/output paths, changed slots/layers, map meanings, inspected views,
remaining defects and any downstream conversion still unverified. Missing image
inspection means visual QA is blocked. A technically valid UV layer is not art
approval; a Blender render is not Unity material equivalence.

Do not install texture services, download unlicensed assets, upgrade Blender,
change the renderer, edit runtime packages, create new shaders or overwrite frozen
sources merely to use this skill. No commands execute when this file is loaded.
