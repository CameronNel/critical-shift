---
name: unity-validation
description: Use for Critical Shift runtime readiness, Unity import or build validation, existing editor-free tests, native test evidence and performance profiling. Routes to current project tools; does not create or install a Unity project, packages or CI.
---

# Critical Shift: runtime and Unity validation

Start with [AGENTS.md](../../../AGENTS.md), the
[architecture entrypoint](../../../design/code-architecture/README.md),
[agent checklist](../../../design/code-architecture/AGENT_CHECKLIST.md),
[validation plan](../../../design/code-architecture/VALIDATION_PLAN.md),
[engine decision](../../../design/ENGINE_DECISION.md) and
[current runtime README](../../../runtime/README.md).
Follow their first-entry and affected-contract reading requirements. This skill routes
to those authorities, not a competing architecture, CI system or official Unity plugin.

## Discover before running

Inspect the current checkout, task scope, actual project files, package pins, editor
availability/license, build support, runner source and latest evidence revision.
Resolve stale narrative against the source and dated evidence without silently changing
the selected engine, renderer, backend or acceptance requirements. A folder named
`unity` proves neither a complete project nor a successful native import.

The inspected installation baseline contains an editor-free .NET verifier and optional
native foundation runner. Re-read the runtime README and scripts to resolve current
commands; do not assume that baseline paths, test inventories or results remain current.
Do not copy canonical domain/application code into a second Unity implementation.

## Choose the evidence layer

- Documentation-only: validate paths, metadata, scope and authority consistency.
  Do not run asset hydration, native project preparation or a game build needlessly.
- Pure runtime rules: use the existing editor-free verification path and its negative
  controls. A passing offline NUnit run is not a Unity Test Runner or Player pass.
- Native import, serialization, bindings or engine behavior: use the existing authorized
  native runner in its disposable workspace with the pinned, already activated editor.
- Performance: profile a representative target build using the existing V05 procedure,
  approved budgets and recorded hardware/settings. Do not infer FPS from code review.

Read [execution and evidence](references/execution.md) for relevant checks. Use
[game-asset-pipeline](../game-asset-pipeline/SKILL.md) when imported assets change.

## Reject false success

Report exact revision, commands, test discovery/execution/skip/failure counts, logs and
artifacts. Validate expected tests and parse results, not just process exit status.
Preserve initial failures and distinguish retries from an uninterrupted pass. Missing
required tests, a license, an editor, build support or usable graphics capability is a
blocker for the affected native claim. Continue unrelated authorized checks only.

Use the validation plan's Planned, NotRun, Passed, Failed, Blocked and NotApplicable
labels precisely. No automatic gate advancement, fabricated independent review or
human playtest approval. Technical, visual and gameplay acceptance remain distinct.

## Boundaries

Do not install the official Unity plugin/CLI, MCP packages, renderer upgrades or any
SDK merely to make this skill usable. Do not alter workflows, secrets, credentials,
cloud settings, test filters or thresholds to make a failure green. Native preparation
and engine execution require an authorized task; this installation performs neither.
