# Source and local adaptations

## Inspected upstream

Repository: [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill).
Pinned revision: `11016c9a5847897491dde935c346571bd7548e3d`.
Inspected module: [blender-uv-texturing/SKILL.md](https://github.com/RobLe3/cc-blender-skill/blob/11016c9a5847897491dde935c346571bd7548e3d/plugin/skills/blender-uv-texturing/SKILL.md).
Inspected module Git blob: `b125feda4e247c0739e11d5f29c1cef06d153284`.
The complete upstream [MIT license](LICENSE) is retained unchanged.

This is a local headless adaptation, not a verbatim upstream installation, a claim
of upstream endorsement, or evidence that it improves every model's output.
No upstream Python recipes, MCP tool allowlist, installer or auto-updater are included.

## Adaptations

- Preserve the existing headless workflow, section art authority and adaptive effort.
- Separate tangent-space normal maps from scalar height/bump inputs rather than using
  the upstream combined normal-or-bump recipe for both.
- Require installed-version transparency APIs instead of hard-coded legacy settings.
- Distinguish object-local projection from world/camera projection and validate
  sidewalls/caps without loading the upstream suite's additional skills.
- Inspect shared datablock users before edits; scope UV, material and bake mutations.
- Cover target material slots, source/target feedback, saved images and mip bleeding.
- Separate color encodings and shader channel conventions, including the receiving
  Unity shader, without installing a new renderer or importer.
- Require actual checker/material/scene image inspection and honest engine blockers.

The Blender Manual pages for normal maps and baking could not be fetched by the
research browser during this installation. No claim of fresh manual/API verification
is made for them. Consult the installed Blender version's documentation before coding;
this adaptation deliberately supplies workflow checks rather than untested API recipes.

## Other specialists in this change

`game-asset-pipeline` and `unity-validation` are project-authored routing/checklist
skills, not vendored Unity or third-party packages. They derive their acceptance from
Critical Shift's existing A08 and V00/V05 contracts and current runtime tooling.

[Unity's official skills README](https://github.com/Unity-Technologies/skills) was
inspected. It notes that many skills use the Unity CLI and an open editor. Its full
bundle is not installed: automatic tool/project/package setup does not fit this
bounded instruction-only integration. Official command-line/Test Framework references
are linked in the Unity specialist; they do not select or upgrade a package.

[Blender Game Skills](https://github.com/majidmanzarpour/blender-game-skills) was also
consulted for its measured reference/round-trip approach. Its scripts, default budgets,
per-phase gates and rigging pipeline are not copied or installed. Current Critical
Shift contracts remain the authority. No X/Reddit consensus or benchmark is claimed.
