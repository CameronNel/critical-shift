# Focused production skills

## Installed scope

These repository-scoped instructions extend the existing headless and animation
skills. They add no executable tools, runtime code, assets, packages, workflows,
cloud configuration, hooks or permission grants. Existing art/build/architecture
rules remain authoritative. Small tasks retain artistic and implementation autonomy.

| Skill | Purpose | Does not do |
| --- | --- | --- |
| [blender-uv-texturing](../../.agents/skills/blender-uv-texturing/SKILL.md) | UVs, atlases, decals, map semantics and final-step baking QA (baking comes last, after geometry, materials and live lighting are accepted) | Replace the art style or install a texture service |
| [game-asset-pipeline](../../.agents/skills/game-asset-pipeline/SKILL.md) | Scoped export, re-import, binding, collider and LOD checks | Promote the map, invent budgets or install importers |
| [unity-validation](../../.agents/skills/unity-validation/SKILL.md) | Current offline/native tooling and evidence-based profiling | Create Unity projects, upgrade packages or claim gate completion |

Material look-development is included with UV/texturing rather than a second competing
materials skill. Optimization checks are included at the delivery/runtime boundaries;
there is no universal polygon or FPS budget. New rigging, VFX, multiplayer infrastructure
and alternate modeling suites are deferred until a bounded task establishes the need.

## Existing entrypoints remain authoritative

- [Agent rules](../../AGENTS.md) and [Claude entrypoint](../../CLAUDE.md).
- [Headless Blender](../../.agents/skills/blender-headless/SKILL.md) and
  [animation](../../.agents/skills/blender-animation/SKILL.md), unchanged by this addition.
- [Art direction](../ART_DIRECTION.md), [map](../../MAP.md) and section-local gates.
- [Architecture](../code-architecture/README.md), A08's binding boundary and V00/V05's
  validation/performance evidence. No competing hidden architecture is introduced.
- [Current runtime status](../../runtime/README.md), including actual runner source
  and revision-specific evidence. Read it instead of relying on historical claims.

Inspected base: `eb3a2d1ef3acb0e6ea76e86dd4771c81004f373b`.
That checkout contains editor-free gameplay verification and a source-only native
foundation; native Unity readiness and a playable map must not be inferred from it.
This addition neither runs those suites nor changes their existing status.

## Shared discovery

Canonical files live in `.agents/skills/<name>/SKILL.md`. Thin adapters in
`.claude/skills/<name>/SKILL.md` load the same content. Root AGENTS routing is additive;
CLAUDE.md and both previously installed skills are untouched.

Use a checkout containing this change. In supported Codex sessions, invoke
`$blender-uv-texturing`, `$game-asset-pipeline` or `$unity-validation`; in Claude Code,
use the corresponding `/` skill name. Automatic selection depends on the client
loading repository skills; this installation does not claim a live cloud discovery test.
If discovery is unavailable, explicitly ask the agent to read the canonical file.
Do not load every specialist for unrelated tasks.

## Provenance and limitations

[Source and adaptations](../../.agents/skills/blender-uv-texturing/SOURCE.md) records
the pinned UV module and retained license, consulted sources and omitted integrations.
The Unity specialist is project-authored, not the official Unity plugin. There are
no newly installed API recipes to mistake for tested Blender or Unity compatibility.

Package checks should cover metadata, relative links, additive routing and exact scope.
They are not Blender rendering, cloud-agent trials, native Unity execution, export
compatibility, animation-quality comparisons or performance measurements. Report those
as unrun unless a separate execution actually supplies evidence.

## Maintenance and review

Update the canonical specialist, not its adapter, when workflow knowledge changes.
Keep version-sensitive API examples out unless tested against the relevant toolchain.
Review the complete diff, source/license record and instruction conflicts. Preserve
all existing map/assets, immutable caches, source hashes and runtime ownership.
Use the normal independent-review process. This installation grants no standing
agent self-merge permission and changes no repository policy. Roll back with a normal
reviewed revert, never by rewriting main history or deleting art sources.
