# Blender animation specialist

Critical Shift's headless adaptation of RobLe3's `blender-animation`, installed
beside the existing [headless workflow](../blender-headless/README.md).
The [canonical skill](../../.agents/skills/blender-animation/SKILL.md) covers
keyframes, F-curves, existing-rig posing, shape keys, drivers, Actions/NLA, loops,
camera motion and temporal validation. It is not an auto-rigger or a runtime system.
[Source pin, comparison, adaptation notes and license](../../.agents/skills/blender-animation/SOURCE.md).

## Discovery and use

- Codex: `.agents/skills/blender-animation/SKILL.md`; invoke `$blender-animation`
  where supported, or explicitly ask it to read the canonical file.
- Claude Code repository/cloud sessions: `.claude/skills/blender-animation/SKILL.md`
  is a thin adapter to the same canonical file; invoke `/blender-animation`.
- Root [AGENTS.md](../../AGENTS.md) routes animation work to the specialist.
  The existing [CLAUDE.md](../../CLAUDE.md) import continues to share those rules.

Start from a checkout containing these files. A PR branch is usable for a trial;
main receives the skill only after an authorized reviewed merge. Existing cloud
sessions on older commits do not inherit files added elsewhere automatically.
This is repository-scoped, not a global installation for every cloud project.
Skills do not install Blender, GPUs, Git LFS, image tools or video playback.

[Codex skill documentation](https://developers.openai.com/codex/skills) and
[Claude skill documentation](https://code.claude.com/docs/en/skills) describe the
client discovery mechanisms. Client support must still be checked in a live session.

## Scope and non-regression boundaries

The existing headless skill and its references remain unchanged. Static scene work
does not need this animation specialist. Small edits use focused review; complex
motion gets blocking and denser diagnostics only as warranted. All agents retain
modeling/animation judgment, with the same quality standards and honest QA status.

This instruction-only addition changes no map, scene, asset, rig, clip, Blender
script, runtime/Unity code, exporter, dependency, workflow, cloud setting or merge
policy. It installs no MCP server, hook, remote updater or executable toolkit.
Example Python inside reference Markdown is inert until an authorized future task
chooses to adapt and execute it. It is not a new production editing library.

## Validation and trial

For this package, validate canonical/adapter frontmatter, routing, relative links,
source pin and license, example Python syntax/isolated behavior, and the entire diff.
Preserve all pre-existing entry rules. Check the committed Git blobs against the
validated package. These checks do not establish live Blender compatibility.

A later trial should use a separate bounded asset task: save a baseline, identify
the actual rig/Action slots and FPS, animate one scoped property or clip, inspect
key and intermediate frame renders, review playback where supported, and run the
existing section checks. Record exact Blender/client versions and blockers.
Keep technical, temporal image, real-time playback and export/runtime validation
separate. Neither self-review nor a tool's clean exit is independent approval.

## Review, maintenance and rollback

Use the existing one-branch/one-author process and obtain independent review. This
installation grants no standing self-merge permission. Keep project art and engine
decisions in their existing authorities, not in this guide or upstream documents.
Future upstream updates must be pinned, audited and tested rather than auto-fetched.
Disable through a normal reviewed revert of this bounded change. Do not reset main,
rewrite history, delete source assets or alter unrelated skills to roll it back.
