# Shared headless Blender skill

## Purpose and authority

Make Critical Shift's existing Blender production workflow discoverable in both
Codex and Claude cloud repository sessions, without replacing the working art
pipeline or constraining a capable model's modeling techniques.

The [shared skill](../../.agents/skills/blender-headless/SKILL.md) routes into
[AGENTS.md](../../AGENTS.md), [MAP.md](../../MAP.md),
[ART_DIRECTION.md](../ART_DIRECTION.md), [ART_REFERENCE_INDEX.md](../ART_REFERENCE_INDEX.md)
and [AUTONOMOUS_SECTION_BUILD_PROTOCOL.md](../AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).
Those documents and the affected section's current specification remain authoritative.
This directory is an integration guide, not another art or architecture canon.

## How it is loaded

- Codex: `.agents/skills/blender-headless/SKILL.md`, with an explicit routing link
  in root AGENTS.md. Invoke `$blender-headless` where the client supports skills,
  or explicitly ask it to read that file before the Blender task.
- Claude Code, including repository-backed cloud sessions:
  `.claude/skills/blender-headless/SKILL.md` is a small adapter to the same canonical
  file. `/blender-headless` is its explicit invocation. Root CLAUDE.md imports
  AGENTS.md so the existing shared project rules are not duplicated.

The two skill entrypoints use the same name and task-specific description. The
Claude adapter links to the canonical file rather than maintaining a second copy
or relying on symlinks. Its paths are relative to the file, not the current shell.
Supporting references are loaded only when needed.

Start a fresh cloud task from a branch containing these files. Existing sessions
or older branches may still have an earlier checkout. Ask the agent to identify
the loaded skill path and applicable project rules before the first Blender job.
Committed instructions do not install Blender, hydrate Git LFS, add GPUs or grant
vision tools. These capabilities still come from the session environment.
This integration is repository-scoped; it does not configure every project or a
plain chat session without repository access.

## Adaptive, not model-specific

Small changes use affected checks and image review. Complex or failing work gets
additional views, measurements and targeted diagnostics. New rooms, major passes
and formal acceptance retain the complete existing protocol and any stricter
section/map requirements. There is no weaker acceptance standard for a preferred
model and no compulsory extra modeling recipe for a capable one.

## Deliberately unchanged

This installation changes instructions only. It does not change `.blend` files,
room modules, the assembled map, MAP.json, provenance, source hashes, art direction,
runtime/Unity code, exporters, Blender scripts, existing workflows, packages,
cloud environment setup, permissions or standing review/merge policy.
It does not install any external skill, MCP service, hook or automatic renderer.
The existing section tools are the harness; these documents tell agents how to
find and use them. Additional executable diagnostics require their own bounded,
tested change rather than being slipped into this installation.

## Maintenance and verification

Keep the canonical workflow in `.agents/skills/blender-headless/`; leave the Claude
adapter thin. Put actual art decisions in the existing art/section authority, not
in this guide. Preserve explicit user scope and repository ownership constraints.

For an instruction update, check both frontmatter blocks, relative links, the
CLAUDE.md import, the AGENTS.md route, and the diff for accidental non-document
changes. No scene rebuild or LFS download is needed for those checks.

For a later live trial, use a separate branch and a bounded existing asset task.
Compare baseline/result at fixed settings, confirm the agent opened the images,
run the applicable section checks and inspect its handoff. Record the exact client,
model, Blender version and blockers. Structural documentation checks alone do not
prove model quality, cloud auto-discovery or Blender/runtime compatibility.

Rollback is a normal reviewed revert of the instruction-only change. Do not reset
main, delete scenes or rewrite history to disable a skill. Keep standing merge
rules intact; this installation grants no future self-merge permission.
