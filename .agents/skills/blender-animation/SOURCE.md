# Provenance and adaptation record

Reviewed for Critical Shift on 2026-09-30.

## Selected upstream

- Repository: [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill).
- Pinned commit: `11016c9a5847897491dde935c346571bd7548e3d` (2026-05-01, v1.3.0).
- Selected [animation entrypoint](https://github.com/RobLe3/cc-blender-skill/blob/11016c9a5847897491dde935c346571bd7548e3d/plugin/skills/blender-animation/SKILL.md)
  and [animation overview](https://github.com/RobLe3/cc-blender-skill/blob/11016c9a5847897491dde935c346571bd7548e3d/plugin/skills/blender-animation/references/overview.md).
- Upstream copyright: Copyright (c) 2026 RobLe3. The complete upstream MIT notice
  is retained in [LICENSE](LICENSE).

This directory is a locally edited adaptation of those instructions, not an
unmodified vendor snapshot, upstream endorsement or installation of the full
30-skill plugin. Its keyframe/property, easing, rotation, shape-key, driver and
NLA topics come from the selected module. Critical Shift authority, headless
execution, ownership safety and temporal QA are local integration additions.

## Selection evidence and limits

The [skills.sh listing](https://www.skills.sh/roble3/cc-blender-skill/blender-animation)
reported 725 installs and 78 repository stars when inspected on 2026-09-30.
These are adoption signals, not user satisfaction, independent recommendations or
an animation-quality benchmark. Searches of X/Reddit and technical communities did
not establish a reliable consensus winner. Selection was based on visible adoption,
an inspectable focused module, MIT licensing and bounded adaptation cost.

Also inspected [Scenario's animation skill](https://github.com/scenario-labs/skills/blob/main/skills/dcc/blender/scenario-blender-animation/SKILL.md),
which routes into its own expert/toolkit siblings, and
[ra100's animation/rigging skill](https://github.com/ra100/blender-claude-plugin/blob/master/skills/blender-animation-rigging/SKILL.md),
which assumes MCP tooling. Neither was installed. This comparison is not a
benchmark or a claim that this module outperforms them.

## Deliberate changes from upstream

- Removed MCP-specific tool permissions, desktop edit steps and viewport-dependent
  preview instructions. No remote installer, hook, service or automatic updater.
- Kept lazy references and model-independent artistic freedom. Replaced blanket
  interpolation/style prescriptions with choices based on the requested motion.
- Replaced global scene/FPS assumptions with existing project timing and ownership.
- Required Action-slot/channel scoping rather than sweeping every Action curve.
- Clarified outgoing-key interpolation, multi-turn rotation, loop period/closure,
  real shape-key deformation, driver coordinate spaces and safe NLA transfer.
- Added evaluated temporal samples, contact/seam checks and separate playback status.
- Kept rig replacement, mocap pipelines, dependencies, baking/export-contract changes
  and runtime controller work outside the implied scope of animation authoring.
- Did not import upstream scripts, the quality-autoloop system or sibling plugins.

## Version maintenance

Before adopting another revision, compare the pinned source, review every changed
instruction/snippet and test in a disposable scene with the actual Blender version.
Consult the installed Blender API/manual for Action slots, F-curves, keyframe
interpolation and NLA behavior; do not infer API compatibility from this document.
Retain copyright attribution and describe modifications. Update only through a
bounded reviewed change, never by silently downloading moving upstream content.

See [integration guide](../../../design/blender-animation/README.md) for discovery,
validation limits and rollback. Static checks of Markdown/snippets do not prove
Blender execution, cloud auto-discovery, motion quality or runtime compatibility.
